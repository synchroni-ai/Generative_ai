# app/api/routes/documents.py

import uuid
import datetime
from typing import List, Optional, Any, Dict
from werkzeug.utils import secure_filename
from app.models import Document, User, DocumentStatusEnum
from app.api.deps import get_current_user, get_db

# Import Form for non-file form data fields, and Path for clarity
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Form,
    Path,
    Body,
    Query,
)
from beanie import PydanticObjectId

# Import BaseModel from pydantic
from pydantic import BaseModel
from motor.core import AgnosticDatabase  # Import AgnosticDatabase for type hint

# Import necessary models (including User)
from app.models import (
    Document,
    Dataspace,
    ConfigModel,
    DocumentStatusEnum,
    User,
)  # <--- Ensure User is imported

# Import dependencies (get_db, get_dataspace_by_id, get_current_user)
# AuthenticatedUser is not used anymore, use deps.get_current_user directly
from app.api import deps  # <--- Import the whole deps module

# Import the timezone helper
from app.core.config import get_ist_now  # Import the timezone helper

# Import S3 service functions
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3

# Import response models from the separate responses file
from app.api.models.responses import (
    DocumentDetailResponse,  # Make sure these models match your requirements
    DocumentTimestampsResponse,
    BatchDeleteResponse,
    DeletedDocumentSummary,
    BatchUploadResponse,
    UploadedDocumentResponse,
    UploadErrorResponse,
)


router = APIRouter()


class BatchDeleteRequest(BaseModel):
    document_ids: List[PydanticObjectId]


def map_status_to_int(status_enum: DocumentStatusEnum) -> int:
    """Maps the internal DocumentStatusEnum to the required integer API status code."""
    status_map = {
        DocumentStatusEnum.PROCESSED: 1,
        DocumentStatusEnum.UPLOADED: -1,
        DocumentStatusEnum.PROCESSING: 0,
        DocumentStatusEnum.ERROR: -2,
    }
    # Use .get() with a default value for robustness against unexpected enum values
    # Ensure the value passed is the Enum member, not its string value, or update the map
    return status_map.get(status_enum, -99)


# Helper dependency to get a document by ID (defined locally if not in deps)
async def get_document_by_id(
    document_id: PydanticObjectId, db: AgnosticDatabase = Depends(deps.get_db)
) -> Document:
    """Dependency to fetch a document by ID or raise 404."""
    document = await Document.get(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )
    return document


# --- CREATE (Upload Single Document) ---
@router.post(
    "/dataspaces/{dataspace_id}/documents",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    dataspace_id: PydanticObjectId,  # Dataspace ID from the path
    file: UploadFile = File(..., description="The file to upload"),  # The uploaded file
    current_user: User = Depends(deps.get_current_user),  # <-- ADD AUTH DEPENDENCY
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Uploads a single document to a specific dataspace. Requires authentication.
    """
    # Validate if the dataspace exists using the dependency
    try:
        # Use the dependency directly; it handles the DB query and raises 404 if not found
        dataspace = await deps.get_dataspace_by_id(
            dataspace_id, db
        )  # Use the dependency from deps
        # Optional: Add dataspace-level permission check here if needed
        # e.g., if dataspace.created_by != current_user.id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission for this dataspace.")

    except HTTPException as e:
        # Re-raise the 404 or 403 from the dependency
        raise e
    except Exception as e:
        # Catch any other unexpected DB errors during dataspace validation
        print(f"Error validating dataspace {dataspace_id} for single upload: {e}")
        # In a real app, avoid leaking exception details in production errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file name provided."
        )

    original_filename = secure_filename(file.filename)
    if not original_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename provided after sanitization.",
        )

    # Generate a unique key for S3 upload
    # Structure: dataspaces/<dataspace_id>/documents/<uuid>_<original_filename>
    s3_key = f"dataspaces/{dataspace_id}/documents/{uuid.uuid4()}_{original_filename}"

    try:
        # Upload file to S3 using the service function
        # This service function handles S3 errors and closing the file stream on success/fail
        s3_url = await upload_file_to_s3(file, s3_key)

        # Create document entry in MongoDB
        new_document = Document(
            dataspace_id=dataspace_id,
            file_name=original_filename,
            s3_url=s3_url,
            uploaded_at=get_ist_now(),  # Set upload timestamp
            uploaded_by=current_user.id,  # <--- Assign the authenticated user's ID
            status=DocumentStatusEnum.UPLOADED,  # Set initial status using the Enum member
        )

        # Insert the document into the database
        await new_document.insert()
        # Return the newly created document object, which includes the generated _id
        return new_document

    except HTTPException as http_e:
        # Re-raise HTTP exceptions raised by the S3 service (e.g., 503 S3 not configured, 500 S3 upload failed)
        raise http_e
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"Error during single document upload for {original_filename}: {e}")
        # IMPORTANT: If DB save fails but S3 upload succeeded, the S3 file is orphaned.
        # Consider adding S3 cleanup logic here or marking for cleanup.
        # For now, we just raise a generic 500.
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {e}",
        )


# --- CREATE (Upload Multiple Documents - Batch Upload) ---
@router.post(
    "/documents/batch-upload",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def batch_upload_documents(
    dataspace_id: PydanticObjectId = Form(..., description="The ID of the dataspace"),
    files: List[UploadFile] = File(..., description="List of files to upload"),
    current_user: User = Depends(deps.get_current_user),  # Authentication dependency
    db: AgnosticDatabase = Depends(deps.get_db),  # DB connection
):
    """
    Upload multiple documents to a specific dataspace in a single request. Requires authentication.
    """
    # Validate if the dataspace exists first
    try:
        dataspace = await deps.get_dataspace_by_id(dataspace_id, db)
        # Optional: Add dataspace-level permission check here if needed
        # e.g., if dataspace.created_by != current_user.id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission for this dataspace.")

    except HTTPException as e:
        raise e  # Re-raise the 404 or 403 from the dependency
    except Exception as e:
        print(f"Error validating dataspace {dataspace_id} for batch upload: {e}")
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )

    # Initialize lists for successful uploads and errors
    uploaded_successfully: List[UploadedDocumentResponse] = []
    upload_errors: List[UploadErrorResponse] = []

    # Process each file in the list
    for file in files:
        original_filename = secure_filename(file.filename) if file.filename else None
        file_context_name = (
            original_filename
            if original_filename
            else f"Unknown File (Content Type: {file.content_type})"
        )

        # Validate file and filename early
        if not original_filename or not original_filename.strip():
            upload_errors.append(
                UploadErrorResponse(
                    file_name=file_context_name,
                    error="No file name provided or invalid name",
                )
            )
            try:
                await file.close()
            except Exception as e:
                print(f"Error closing file stream for {file_context_name}: {e}")
            continue

        # Generate unique key for S3 upload
        s3_key = (
            f"dataspaces/{dataspace_id}/documents/{uuid.uuid4()}_{original_filename}"
        )

        try:
            # Upload file to S3 using the service function
            s3_url = await upload_file_to_s3(file, s3_key)

            # Create document entry in MongoDB
            new_document = Document(
                dataspace_id=dataspace_id,
                file_name=original_filename,
                s3_url=s3_url,
                uploaded_at=get_ist_now(),  # Set upload timestamp
                uploaded_by=current_user.id,  # <--- Assign the authenticated user's ID
                status=DocumentStatusEnum.UPLOADED.value,  # Set initial status using the Enum member
            )

            try:
                # Insert the document into the database
                await new_document.insert()

                # --- Populate the uploaded_by field in the response model ---
                uploaded_successfully.append(
                    UploadedDocumentResponse(
                        _id=str(new_document.id),
                        file_name=new_document.file_name,
                        status=new_document.status,
                        uploaded_by=(
                            str(new_document.uploaded_by)
                            if new_document.uploaded_by
                            else None
                        ),
                        s3_url=new_document.s3_url,  # <--- Include this
                    )
                )

                # ------------------------------------------------------------

            except Exception as db_e:
                print(
                    f"Error saving document info for {original_filename} to DB: {db_e}"
                )
                upload_errors.append(
                    UploadErrorResponse(
                        file_name=original_filename,
                        error=f"Failed to save document info: {db_e}",
                    )
                )

                try:
                    await delete_file_from_s3(s3_key)
                    print(
                        f"Attempted S3 cleanup for {original_filename} ({s3_key}) after DB error."
                    )
                except Exception as cleanup_e:
                    print(
                        f"Failed to clean up S3 file {s3_key} after DB error: {cleanup_e}"
                    )

        except HTTPException as http_e:
            upload_errors.append(
                UploadErrorResponse(
                    file_name=file_context_name, error=f"Upload failed: {http_e.detail}"
                )
            )

        except Exception as other_e:
            print(
                f"An unexpected error occurred processing file {file_context_name}: {other_e}"
            )
            upload_errors.append(
                UploadErrorResponse(
                    file_name=file_context_name,
                    error=f"An unexpected error occurred: {other_e}",
                )
            )
            try:
                await file.close()
            except Exception as e:
                print(
                    f"Error closing file stream for {file_context_name} after unexpected error: {e}"
                )

    return BatchUploadResponse(
        dataspace_id=str(dataspace_id),
        uploaded=uploaded_successfully,
        errors=upload_errors,
    )


# --- READ (List Documents in a Dataspace) ---
@router.get("/dataspaces/{dataspace_id}/documents", response_model=List[Document])
async def list_dataspace_documents(
    dataspace_id: PydanticObjectId,  # Gets the dataspace ID from the path
    current_user: User = Depends(deps.get_current_user),  # <-- ADD AUTH DEPENDENCY
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Lists all documents belonging to a specific dataspace. Requires authentication.
    (Optional: Add authorization check for dataspace access)
    """
    # Validate if the dataspace exists using the dependency
    try:
        dataspace = await deps.get_dataspace_by_id(
            dataspace_id, db
        )  # Use the dependency from deps
        # Optional: Add dataspace-level permission check here if needed
        # e.g., if dataspace.created_by != current_user.id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission for this dataspace.")

    except HTTPException:
        raise  # Re-raise the 404 or 403 from the dependency
    except Exception as e:
        # Catch any other unexpected DB errors during dataspace validation
        print(f"Error validating dataspace {dataspace_id} for listing documents: {e}")
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )

    try:
        # Find all documents where the dataspace_id matches the path parameter
        documents = await Document.find(Document.dataspace_id == dataspace_id).to_list()
        # Returns a list of Document objects. Pydantic handles serialization.
        return documents

    except Exception as e:
        print(f"Error listing documents for dataspace {dataspace_id}: {e}")
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {e}",
        )


# --- READ (Get One Document) ---
# Add a route to get a single document by its ID
@router.get("/documents/{document_id}", response_model=Document)
async def get_document(
    document: Document = Depends(
        get_document_by_id
    ),  # Use the local document dependency
    current_user: User = Depends(deps.get_current_user),  # <-- ADD AUTH DEPENDENCY
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Gets details of a specific document by ID. Requires authentication.
    (Optional: Add authorization check: e.g., check if user owns the parent dataspace)
    """

    return document  # The document object is already returned by the dependency


# --- UPDATE (e.g., update status, config) ---
# Assuming DocumentUpdate model is defined elsewhere (e.g., in models.py or here)
# Let's define a simple one here if it's not in app.models
class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatusEnum] = None  # Can update status using Enum
    config: Optional[ConfigModel] = None  # Can update embedded ConfigModel

    class Config:
        # This allows partial updates where fields are omitted
        extra = "ignore"  # Or 'allow' if you need to accept extra fields


# --- UPDATE (Replace Document File) ---
# This endpoint now accepts a file upload as part of the body (multipart/form-data)
@router.put("/documents/{document_id}", response_model=Document)
async def replace_document_file(
    document_id: PydanticObjectId,
    new_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document: Document = Depends(get_document_by_id),
    db: AgnosticDatabase = Depends(get_db),
):
    from app.api.deps import get_dataspace_by_id  # Import inside if circular

    try:
        parent_dataspace = await get_dataspace_by_id(document.dataspace_id, db)
        if parent_dataspace.created_by != current_user.id:
            await new_file.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to replace documents in this dataspace.",
            )
    except HTTPException as http_e:
        await new_file.close()
        raise http_e
    except Exception as e:
        await new_file.close()
        print(f"Error checking dataspace permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking permissions for dataspace.",
        )

    new_original_filename = secure_filename(new_file.filename)
    if not new_original_filename:
        await new_file.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename.",
        )

    new_s3_key = f"dataspaces/{document.dataspace_id}/documents/{document_id}_{new_original_filename}"
    old_s3_url = document.s3_url

    try:
        new_s3_url = await upload_file_to_s3(new_file, new_s3_key)

        # ✅ Update document fields
        document.file_name = new_original_filename
        document.s3_url = new_s3_url
        document.uploaded_at = get_ist_now()
        document.uploaded_by = current_user.id
        document.status = DocumentStatusEnum.UPLOADED
        document.updated_at = get_ist_now()  # ✅ Set updated timestamp

        await document.save()

        if old_s3_url:
            try:
                await delete_file_from_s3(old_s3_url)
            except Exception as s3_e:
                print(f"Warning: failed to delete old S3 file: {s3_e}")

        return document

    except HTTPException as http_e:
        print(f"S3 upload error: {http_e.detail}")
        raise http_e
    except Exception as e:
        await new_file.close()
        print(f"Error replacing file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to replace document file: {e}",
        )


# --- DELETE (Single Document) ---
# Add a route to delete a single document by its ID
@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document: Document = Depends(
        get_document_by_id
    ),  # Get the document via local dependency
    current_user: User = Depends(deps.get_current_user),  # <-- ADD AUTH DEPENDENCY
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Deletes a document by ID and its S3 file. Requires authentication.
    (Optional: Add authorization check: e.g., check if user owns the parent dataspace)
    """

    try:
        # Delete the document entry from the database FIRST
        await document.delete()
        print(f"Document {document.id} deleted from DB by user {current_user.id}.")

        # Then attempt to delete the associated S3 file
        try:
            await delete_file_from_s3(document.s3_url)
            print(f"S3 file for document {document.id} deleted.")
        except HTTPException as s3_http_e:
            print(
                f"Warning: Failed to delete S3 file for document {document.id}: {s3_http_e.detail} (DB entry was deleted)."
            )
            # You might want to log this or report it differently, but don't raise 500 if DB delete succeeded
        except Exception as s3_e:
            print(
                f"Warning: An unexpected error during S3 deletion for document {document.id}: {s3_e} (DB entry was deleted)."
            )
            # Again, log the error but don't fail the API request if DB delete succeeded

        # No content is returned for 204
        return  # FastAPI automatically returns 204 if no response body is provided

    except Exception as e:
        print(f"Error deleting document {document.id}: {e}")
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {e}",
        )


# --- DELETE (Batch Delete Documents) ---
@router.delete(
    "/dataspaces/{dataspace_id}/documents/batch-delete",
    response_model=BatchDeleteResponse,
    status_code=status.HTTP_200_OK,
)
async def batch_delete_documents_in_dataspace(
    dataspace_id: PydanticObjectId,  # Get dataspace ID from the path
    delete_request: BatchDeleteRequest = Body(
        ..., description="List of document IDs to delete"
    ),
    current_user: User = Depends(deps.get_current_user),  # Authentication dependency
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Deletes multiple document entries from the database AND their corresponding files from S3,
    scoped to a specific dataspace. Requires Authentication.
    Only the creator of the dataspace can perform batch deletion.
    """
    total_requested = len(delete_request.document_ids)
    successfully_deleted_count = 0
    failed_deletions: List[DeletedDocumentSummary] = []

    # 1. Check if the dataspace exists AND the user has permission for the dataspace
    try:
        dataspace = await deps.get_dataspace_by_id(
            dataspace_id, db
        )  # Use the dependency from deps

        # --- AUTHORIZATION CHECK: ONLY DATASPACE CREATOR CAN BATCH DELETE ---
        # Check if the current user's ID matches the dataspace creator's ID
        if dataspace.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to batch delete documents in this dataspace.",
            )
        # --- END AUTHORIZATION CHECK ---

    except HTTPException as e:
        # Re-raise the 404 from get_dataspace_by_id or the 403 from our check
        raise e
    except Exception as e:
        print(f"Error validating dataspace {dataspace_id} for batch delete: {e}")
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )

    # 2. Iterate through each document ID provided in the request body
    # This loop now only runs IF the initial dataspace authorization passed.
    for doc_id in delete_request.document_ids:
        doc_id_str = str(doc_id)
        try:
            # Attempt to get the document by ID
            # We still check document.dataspace_id != dataspace_id below
            # to ensure the requested doc ID actually belongs to the dataspace in the URL.
            document = await Document.get(doc_id)

            if not document:
                failed_deletions.append(
                    DeletedDocumentSummary(
                        document_id=doc_id_str,
                        status="failed",
                        error="Document not found",
                    )
                )
                print(f"Batch Delete: Document with ID {doc_id_str} not found.")
                continue  # Skip to the next ID

            # 3. Ensure the document belongs to the specified dataspace (still needed as a safety check)
            if document.dataspace_id != dataspace_id:
                failed_deletions.append(
                    DeletedDocumentSummary(
                        document_id=doc_id_str,
                        status="failed",
                        error="Document does not belong to this dataspace",
                    )
                )
                print(
                    f"Batch Delete: Document {doc_id_str} does not belong to dataspace {dataspace_id}."
                )
                continue  # Skip to the next ID
#jhqb3djbhed
            # Optional: Check if the user who uploaded the document is the current user
            # This is different from dataspace creator permission - you decide if you need both layers.
            # if document.uploaded_by != current_user.id:
            #      failed_deletions.append(DeletedDocumentSummary(document_id=doc_id_str, status="failed", error="Permission denied to delete this specific document"))
            #      print(f"Batch Delete: Permission denied for document {doc_id_str} in dataspace {dataspace_id}.")
            #      continue # Skip to the next ID

            # 4. Get the S3 URL before deleting the DB record
            s3_url_to_delete = document.s3_url

            # 5. Delete the document entry from the database FIRST
            await document.delete()
            print(
                f"Batch Delete: Successfully deleted document from DB: {doc_id_str} in dataspace {dataspace_id}"
            )
            successfully_deleted_count += (
                1  # Increment count after successful DB delete
            )

            # 6. Now attempt to delete the file from S3 (do this AFTER successful DB delete)
            try:
                await delete_file_from_s3(s3_url_to_delete)
                print(f"Batch Delete: Attempted S3 deletion for {s3_url_to_delete}.")

            except HTTPException as s3_http_e:
                failed_deletions.append(
                    DeletedDocumentSummary(
                        document_id=doc_id_str,
                        status="s3_delete_failed_db_deleted",
                        error=f"S3 deletion failed: {s3_http_e.detail}",
                    )
                )
                print(
                    f"Batch Delete: S3 deletion failed for {doc_id_str}: {s3_http_e.detail} (DB entry was deleted)."
                )

            except Exception as s3_e:
                failed_deletions.append(
                    DeletedDocumentSummary(
                        document_id=doc_id_str,
                        status="s3_delete_failed_db_deleted",
                        error=f"S3 deletion failed: {s3_e}",
                    )
                )
                print(
                    f"Batch Delete: An unexpected error during S3 deletion for {doc_id_str}: {s3_e} (DB entry was deleted)."
                )

        except HTTPException as http_e:
            # This catches errors from operations *inside* the loop, like get_document (though less likely with Get(id))
            failed_deletions.append(
                DeletedDocumentSummary(
                    document_id=doc_id_str,
                    status="failed",
                    error=f"Error processing document: {http_e.detail}",
                )
            )
            print(
                f"Batch Delete: Error processing document {doc_id_str}: {http_e.detail}"
            )

        except Exception as e:
            # Catch any other unexpected errors during processing of a single document ID within the loop
            failed_deletions.append(
                DeletedDocumentSummary(
                    document_id=doc_id_str,
                    status="failed",
                    error=f"An unexpected error occurred: {e}",
                )
            )
            print(f"Batch Delete: An unexpected error occurred for {doc_id_str}: {e}")

    return BatchDeleteResponse(
        total_requested=total_requested,
        successfully_deleted=successfully_deleted_count,
        failed_deletions=failed_deletions,
    )

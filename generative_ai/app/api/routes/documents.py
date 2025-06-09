# app/api/routes/documents.py

import uuid
import datetime
from typing import List, Optional, Any, Dict
from werkzeug.utils import secure_filename
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_db
from bson import ObjectId
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
    # ConfigModel, # This is the model from app.models, no need to re-import from responses
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
    try:
        dataspace = await deps.get_dataspace_by_id(dataspace_id, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error validating dataspace {dataspace_id} for batch upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )
    uploaded_successfully: List[UploadedDocumentResponse] = []
    upload_errors: List[UploadErrorResponse] = []
    for file in files:
        original_filename = file.filename if file.filename else None
        file_context_name = (
            original_filename
            if original_filename
            else f"Unknown File (Content Type: {file.content_type})"
        )
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
        existing_doc= await db["documents"].find_one({
            "dataspace_id": dataspace_id,
            "file_name": original_filename
        })
        if existing_doc:
            upload_errors.append(
                UploadErrorResponse(
                    file_name=original_filename,
                    error="Document with the same name already exists in the dataspace. Please change your document name"
                )
            )
            try:
                await file.close()
            except Exception as e:
                print(f"Error closing file stream for duplicate file {file_context_name}: {e}")
            continue
        s3_key = (
            f"dataspaces/{dataspace_id}/documents/{uuid.uuid4()}_{original_filename}" # This will now include spaces if the filename had them
        )
 
        try:
            s3_url = await upload_file_to_s3(file, s3_key)
            new_document = Document(
                dataspace_id=dataspace_id,
                file_name=original_filename,
                s3_url=s3_url,
                uploaded_at=get_ist_now(),
                uploaded_by=current_user.id,
                status=DocumentStatusEnum.UPLOADED.value,
            )
            try:
                await new_document.insert()
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
                        s3_url=new_document.s3_url,
                    )
                )
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
import logging

logging.basicConfig(level=logging.DEBUG)

# --- READ (List Documents in a Dataspace) ---
@router.get("/dataspaces/{dataspace_id}/documents", response_model=List[Document])
async def list_and_update_dataspace_documents(
    dataspace_id: PydanticObjectId,
    new_status: Optional[DocumentStatusEnum] = Query(None, description="Optional: Update status of documents to this value"),
    current_user: User = Depends(deps.get_current_user),
    db: AgnosticDatabase = Depends(deps.get_db),
):
    """
    Lists all documents belonging to a specific dataspace.
    Optionally updates the status of all documents to a provided value.
    Requires authentication.
    """
    logging.debug(f"Received request to list/update documents in dataspace: {dataspace_id}, new_status: {new_status}")

    try:
        dataspace = await deps.get_dataspace_by_id(dataspace_id, db)
        logging.debug(f"Successfully validated dataspace: {dataspace_id}")
    except HTTPException as e:
        logging.warning(f"HTTPException while validating dataspace: {e}")
        raise  # Re-raise the HTTPException
    except Exception as e:
        logging.error(f"Error validating dataspace {dataspace_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )

    try:
        documents = await Document.find(Document.dataspace_id == dataspace_id).to_list()
        logging.debug(f"Found {len(documents)} documents")

        if new_status is not None:
            logging.debug(f"Updating status of all documents to {new_status}")
            for document in documents:
                logging.debug(f"Updating document: {document.id}, current status: {document.status}")

                document.status = new_status
                logging.debug(f"New status after assignment: {document.status}")

                try:
                    await document.save()
                    logging.debug(f"Document {document.id} saved successfully")
                except Exception as save_err:
                    logging.error(f"Error saving document {document.id}: {save_err}") # Log save errors
                    raise # Re-raise so it can be handled by overall error handling

        return documents

    except HTTPException as http_exc:
        logging.warning(f"HTTPException: {http_exc}")
        raise http_exc  # Re-raise without modification
    except Exception as e:
        logging.exception(f"Error listing/updating documents for dataspace {dataspace_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list/update documents: {e}",
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
async def replace_document_file(  # Renamed function for clarity
    document_id: PydanticObjectId,  # Get the document ID from the path
    new_file: UploadFile = File(
        ..., description="The new file to replace the existing document"
    ),  # <-- ACCEPT FILE UPLOAD
    # If you wanted to update other simple fields too, you could add them here with Form(...)
    # e.g., new_description: Optional[str] = Form(None, description="Optional new description")
    current_user: User = Depends(deps.get_current_user),  # Authentication dependency
    document: Document = Depends(
        get_document_by_id
    ),  # Get the existing document via local dependency
    db: AgnosticDatabase = Depends(deps.get_db),  # DB connection
):
    """
    Replaces the file content of an existing document and updates its metadata. Requires authentication.
    """

    # --- AUTHORIZATION CHECK: ONLY DATASPACE CREATOR CAN REPLACE DOCUMENT ---
    try:
        # Fetch the parent dataspace using the document's dataspace_id
        parent_dataspace = await deps.get_dataspace_by_id(document.dataspace_id, db)

#modified
    except HTTPException as http_e:
        # Re-raise 404 if parent dataspace not found (implies invalid document state)
        # Ensure the file stream is closed
        try:
            await new_file.close()
        except Exception:
            pass
        raise http_e
    except Exception as e:
        print(f"Error checking dataspace permissions for document {document.id}: {e}")
        try:
            await new_file.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking permissions for dataspace.",
        )
    # --- END AUTHORIZATION CHECK ---

    # --- PROCESS NEW FILE UPLOAD AND UPDATE DOCUMENT RECORD ---
    if not new_file.filename:
        try:
            await new_file.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No new file name provided."
        )

    new_original_filename = secure_filename(new_file.filename)
    if not new_original_filename:
        try:
            await new_file.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid new filename provided after sanitization.",
        )

    # Generate a NEW unique key for the new S3 upload
    # Use the document_id in the key to link the S3 object to the document record consistently
    # This is just one strategy; you could also use a new UUID if preferred.
    new_s3_key = f"dataspaces/{document.dataspace_id}/documents/{document_id}_{new_original_filename}"

    old_s3_url = (
        document.s3_url
    )  # Store the old URL before updating the document object

    try:
        # 1. Upload the new file to S3
        # The service function handles S3 errors and closing the file stream on success/fail
        new_s3_url = await upload_file_to_s3(new_file, new_s3_key)
        print(
            f"Successfully uploaded new S3 file for document {document_id} to {new_s3_url}"
        )

        # 2. Update the existing document object's fields in memory
        document.file_name = new_original_filename  # Update filename to match new file
        document.s3_url = new_s3_url  # Update S3 URL to the new file
        document.uploaded_at = get_ist_now()  # Update timestamp
        document.uploaded_by = current_user.id  # Update uploader to the current user
        document.status = DocumentStatusEnum.UPLOADED  # Reset status as content is new

        # Optional: If you wanted to update other form fields like description:
        # if new_description is not None:
        #     document.description = new_description

        # 3. Save the modified document object to the database
        # Beanie's save() performs the update operation
        await document.save()
        print(f"Successfully updated document record {document_id} in DB.")

        # 4. Attempt to delete the old file from S3 (do this AFTER the new one is uploaded and DB is updated)
        if old_s3_url:  # Only try to delete if there was an old URL
            try:
                await delete_file_from_s3(old_s3_url)
                print(
                    f"Successfully deleted old S3 file for document {document_id}: {old_s3_url}"
                )
            except HTTPException as s3_http_e:
                print(
                    f"Warning: Failed to delete OLD S3 file for document {document.id}: {s3_http_e.detail} (DB and new file updated)."
                )
                # Log the warning, but don't fail the request if the new file is up and DB is updated.
            except Exception as s3_e:
                print(
                    f"Warning: An unexpected error during OLD S3 deletion for document {document.id}: {s3_e} (DB and new file updated)."
                )
                # Log the warning

        return document  # Return the updated document object

    except HTTPException as http_e:
        # Re-raise HTTP exceptions raised by the S3 service during new file upload
        print(f"Error during NEW S3 upload for document {document_id}: {http_e.detail}")
        # The S3 service should have already closed the file stream in its finally block
        raise http_e  # Re-raise the S3 error to the client

    except Exception as e:
        # Catch any other unexpected errors during the replacement process (e.g., DB save failure)
        print(f"Error replacing document file for document {document.id}: {e}")
        # IMPORTANT: If DB save fails but S3 upload succeeded, the new S3 file is orphaned.
        # Consider adding S3 cleanup logic for the NEW file here or marking for cleanup.
        # For now, we just raise a generic 500.
        # Ensure the file stream is closed
        try:
            await new_file.close()
        except Exception:
            pass
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
    """
    total_requested = len(delete_request.document_ids)
    successfully_deleted_count = 0
    failed_deletions: List[DeletedDocumentSummary] = []

    # 1. Check if the dataspace exists AND the user has permission for the dataspace
    try:
        dataspace = await deps.get_dataspace_by_id(
            dataspace_id, db
        )  # Use the dependency from deps


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


from fastapi import Depends

# @router.get("/testcases/by-dataspace/{dataspace_id}")
# async def get_testcases_by_dataspace(
#     dataspace_id: str,
#     db: AsyncIOMotorDatabase = Depends(get_db)  # ✅ FIXED
# ):

#     try:
#         dataspace_obj_id = ObjectId(dataspace_id)

#         # 1. Find all documents in the dataspace
#         document_cursor = db["documents"].find(
#             {"dataspace_id": dataspace_obj_id},
#             {"_id": 1, "file_name": 1}
#         )
#         documents = await document_cursor.to_list(length=None)
#         document_ids = [str(doc["_id"]) for doc in documents]

#         if not document_ids:
#             return {"message": "No documents found in this dataspace.", "results": []}

#         # 2. Fetch test case results for any of the document_ids
#         test_case_cursor = db.test_case_grouped_results.find({
#             "$or": [
#                 {f"results.documents.{doc_id}": {"$exists": True}}
#                 for doc_id in document_ids
#             ]
#         })

#         test_case_results = await test_case_cursor.to_list(length=None)

#         # 3. Group test cases by document
#         response = []
#         for doc in documents:
#             doc_id = str(doc["_id"])
#             matching_cases = []

#             for tc in test_case_results:
#                 if doc_id in tc["results"]["documents"]:
#                     matching_cases.append({
#                         "config_id": tc["config_id"],
#                         "llm_model": tc.get("llm_model"),
#                         "generated_at": tc.get("generated_at"),
#                         "test_cases": tc["results"]["documents"][doc_id]
#                     })

#             response.append({
#                 "document_id": doc_id,
#                 "file_name": doc["file_name"],
#                 "test_case_versions": matching_cases
#             })

#         return {"dataspace_id": dataspace_id, "results": response}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@router.get("/testcases/by-dataspace/{dataspace_id}")
async def get_testcases_by_dataspace(
    dataspace_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        dataspace_obj_id = ObjectId(dataspace_id)

        # 1. Find all documents in the dataspace
        document_cursor = db["documents"].find(
            {"dataspace_id": dataspace_obj_id},
            {"_id": 1, "file_name": 1}
        )
        documents = await document_cursor.to_list(length=None)
        document_ids = [str(doc["_id"]) for doc in documents]
        document_name_map = {str(doc["_id"]): doc["file_name"] for doc in documents}

        if not document_ids:
            return {"message": "No documents found in this dataspace.", "results": []}

        # 2. Fetch test case results.  Crucially filtering at the DB level.
        test_case_cursor = db.test_case_grouped_results.find({
            "$or": [
                {f"results.documents.{doc_id}": {"$exists": True}}
                for doc_id in document_ids
            ]
        })

        test_case_results = await test_case_cursor.to_list(length=None)

        # 3. Structure the response as required.  This is the complex part.
        response_list = []
        for tc in test_case_results:
            config_id = tc["config_id"]
            llm_model = tc.get("llm_model")
            generated_at = tc.get("generated_at")
            use_case = tc.get("use_case", [])  # Handle missing use_case gracefully
            temperature = tc.get("temperature", None)  # Handle missing temperature gracefully

            results = tc["results"]
            documents_data = results["documents"]
            
            document_results = {}
            all_subtypes_content = {}
            final_subtypes_content = {}

            # Iterate through the documents associated with this test case
            for doc_id, subtypes in documents_data.items():
                if doc_id not in document_name_map:
                    print(f"Warning: doc_id {doc_id} not found in document list.")
                    continue

                document_name = document_name_map[doc_id]

                # Structure document results
                document_results[doc_id] = {
                    subtype: subtypes[subtype] for subtype in subtypes
                    if subtype not in ["all_subtypes"]
                }
                document_results[doc_id]["document_name"] = document_name
                
                # All subtypes combined
                all_subtypes_content[doc_id] = {
                    "content": "\n".join(subtypes.get("all_subtypes", [])),  #Join all subtypes content
                    "document_name": document_name
                }

                # Final subtypes (list of subtypes)
                final_subtypes_content[doc_id] = {
                    "content": subtypes.get("all_subtypes", []),
                    "document_name": document_name
                }

            # Structure all_documents
            all_documents = {}
            for subtype in set(st for doc_id, subtypes in documents_data.items() for st in subtypes if st not in ["all_subtypes"]):
                all_documents[subtype] = {
                    doc_id: {
                        "content": documents_data[doc_id].get(subtype, ""),
                        "document_name": document_name_map.get(doc_id, "Unknown Document")
                    }
                    for doc_id in documents_data if subtype in documents_data[doc_id] and doc_id in document_name_map
                }

            # Create the Final_subtypes structure
            final_subtypes = {}
            final_subtypes = {
                doc_id: {
                    "content": documents_data[doc_id].get("all_subtypes", []),
                    "document_name": document_name_map.get(doc_id, "Unknown Document")
                }
                for doc_id in documents_data if "all_subtypes" in documents_data[doc_id] and doc_id in document_name_map
            }

            response_item = {
                "config_id": config_id,
                "llm_model": llm_model,
                "temperature": temperature,
                "use_case": use_case,
                "generated_at": generated_at,
                "results": {
                    "documents": document_results,
                    "all_documents": all_documents,
                    "Final_subtypes": final_subtypes
                },
                "status": "completed",  # You might want to derive this from the data
                "summary": {  # You might need to compute a meaningful summary
                    "documents": list(document_results.keys()),
                    "subtypes": list(all_documents.keys()) if all_documents else []
                }
            }
            response_list.append(response_item)

        return response_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# app/api/routes/documents.py
 
import uuid
import datetime
from typing import List, Optional, Any, Dict
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
from pydantic import BaseModel
from motor.core import AgnosticDatabase
from app.models import (
    Document,
    Dataspace,
    ConfigModel,
    DocumentStatusEnum,
    User,
)
from app.api import deps
from app.core.config import get_ist_now
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3
from app.api.models.responses import (
    DocumentDetailResponse,
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
    return status_map.get(status_enum, -99)
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
 
# --- READ (List Documents in a Dataspace) ---
@router.get("/dataspaces/{dataspace_id}/documents", response_model=List[Document])
async def list_dataspace_documents(
    dataspace_id: PydanticObjectId,
    current_user: User = Depends(deps.get_current_user),
    db: AgnosticDatabase = Depends(deps.get_db),
):
    """
    Lists all documents belonging to a specific dataspace. Requires authentication.
    """
    try:
        dataspace = await deps.get_dataspace_by_id(dataspace_id, db)
    except HTTPException:
        raise  
    except Exception as e:
       
        print(f"Error validating dataspace {dataspace_id} for listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )
 
    try:
        documents = await Document.find(Document.dataspace_id == dataspace_id).to_list()
        return documents
 
    except Exception as e:
        print(f"Error listing documents for dataspace {dataspace_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {e}",
        )
class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatusEnum] = None
    config: Optional[ConfigModel] = None
 
    class Config:
        extra = "ignore"
 
# --- UPDATE (Replace Document File) ---
# This endpoint now accepts a file upload as part of the body (multipart/form-data)
@router.put("/documents/{document_id}", response_model=Document)
async def replace_document_file(
    document_id: PydanticObjectId,
    new_file: UploadFile = File(
        ..., description="The new file to replace the existing document"
    ),
    current_user: User = Depends(deps.get_current_user),
    document: Document = Depends(
        get_document_by_id
    ),
    db: AgnosticDatabase = Depends(deps.get_db),
):
    """
    Replaces the file content of an existing document and updates its metadata. Requires authentication.
    """
    try:
        parent_dataspace = await deps.get_dataspace_by_id(document.dataspace_id, db)
 
    except HTTPException as http_e:
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
    if not new_file.filename:
        try:
            await new_file.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No new file name provided."
        )
 
    new_original_filename = new_file.filename
    if not new_original_filename:
        try:
            await new_file.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid new filename provided after sanitization.",
        )
    new_s3_key = f"dataspaces/{document.dataspace_id}/documents/{document_id}_{new_original_filename}"
 
    old_s3_url = (
        document.s3_url
    )  
 
    try:
        new_s3_url = await upload_file_to_s3(new_file, new_s3_key)
        print(
            f"Successfully uploaded new S3 file for document {document_id} to {new_s3_url}"
        )
 
        document.file_name = new_original_filename
        document.s3_url = new_s3_url  
        document.uploaded_at = get_ist_now()
        document.uploaded_by = current_user.id
        document.status = DocumentStatusEnum.UPLOADED
        await document.save()
        print(f"Successfully updated document record {document_id} in DB.")
        if old_s3_url:
            try:
                await delete_file_from_s3(old_s3_url)
                print(
                    f"Successfully deleted old S3 file for document {document_id}: {old_s3_url}"
                )
            except HTTPException as s3_http_e:
                print(
                    f"Warning: Failed to delete OLD S3 file for document {document.id}: {s3_http_e.detail} (DB and new file updated)."
                )
            except Exception as s3_e:
                print(
                    f"Warning: An unexpected error during OLD S3 deletion for document {document.id}: {s3_e} (DB and new file updated)."
                )
               
        return document  
 
    except HTTPException as http_e:
        # Re-raise HTTP exceptions raised by the S3 service during new file upload
        print(f"Error during NEW S3 upload for document {document_id}: {http_e.detail}")
        # The S3 service should have already closed the file stream in its finally block
        raise http_e  # Re-raise the S3 error to the client
 
    except Exception as e:
        print(f"Error replacing document file for document {document.id}: {e}")
        try:
            await new_file.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to replace document file: {e}",
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
 
    try:
        dataspace = await deps.get_dataspace_by_id(
            dataspace_id, db
        )
 
 
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error validating dataspace {dataspace_id} for batch delete: {e}")
        # In a real app, avoid leaking exception details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error validating dataspace.",
        )
    for doc_id in delete_request.document_ids:
        doc_id_str = str(doc_id)
        try:
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
                continue
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
                continue  
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
 
 
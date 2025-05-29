# app/api/routes/documents.py

import uuid
import datetime
from typing import List, Optional, Any, Dict
from werkzeug.utils import secure_filename
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from beanie import PydanticObjectId
# import httpx # No need

# Import models and response models
from app.models import Document, Dataspace, DocumentStatusEnum
from app.api import deps
from app.core.config import get_ist_now
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3

# Import response models
from app.api.models.responses import DocumentDetailResponse, DocumentTimestampsResponse
router = APIRouter()

# Function to map internal status enum to required integer code
def map_status_to_int(status_enum: DocumentStatusEnum) -> int:
    status_map = {
        DocumentStatusEnum.PROCESSED: 1,
        DocumentStatusEnum.UPLOADED: -1,
        DocumentStatusEnum.PROCESSING: 0,
        DocumentStatusEnum.ERROR: -2 # Map error to -2
        # Add other mappings if you introduce more statuses
    }
    return status_map.get(status_enum, -99) 
# The path parameter is on the router itself
@router.post("/dataspaces/{dataspace_id}/documents", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    dataspace_id: PydanticObjectId, # Still need dataspace_id from the path
    file: UploadFile = File(...),
    db=Depends(deps.get_db) # Check DB connection
    # We could also use Depends(deps.get_dataspace_by_id) here if we needed the dataspace object itself later in the function
):
    """
    Uploads a document to a specific dataspace and stores it in S3.
    Expects file data in 'file' field of multipart/form-data.
    """
    try:
        # Perform the dataspace existence check explicitly if not using the dependency in the signature
        from app.models import Dataspace # Local import to avoid circular dependency
        dataspace = await Dataspace.get(dataspace_id)
        if not dataspace:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataspace with ID {dataspace_id} not found")
    except Exception as e:
         # Handle potential DB errors during the dataspace lookup
         print(f"Error checking for dataspace {dataspace_id} during upload: {e}")
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error checking dataspace.")


    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file name provided.")

    original_filename = secure_filename(file.filename)
    if not original_filename:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename provided.")

    # Generate a unique key for S3
    s3_key = f"dataspaces/{dataspace_id}/{uuid.uuid4()}_{original_filename}"

    s3_url = await upload_file_to_s3(file, s3_key)

    # Create document entry in MongoDB
    new_document = Document(
        dataspace_id=dataspace_id,
        file_name=original_filename,
        s3_url=s3_url,
        uploaded_at=get_ist_now(), # Use the helper
        status='uploaded'
    )

    try:
        await new_document.insert()
        return new_document
    except Exception as e:
        print(f"Error saving document info to database after S3 upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save document info to database: {e}")
    
@router.get("/documents/{document_id}", response_model=DocumentDetailResponse) 
async def get_document(
    document_id: PydanticObjectId,
    db=Depends(deps.get_db) # Check DB connection
):
    """
    Gets details of a specific document by ID, including embedded configuration and custom status/timestamps.
    """
    try:
        # 1. Find the document by its ID
        # Beanie will automatically fetch the embedded 'config' field
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with ID {document_id} not found")

        # 2. Map the internal status to the required integer format
        api_status = map_status_to_int(document.status)

        # 3. Create the nested timestamps object
        timestamps_data = DocumentTimestampsResponse(
            uploaded_at=document.uploaded_at,
            processed_at=document.processed_at
        )

        # 4. Structure the final response using the response model
        # Use the Document object's attributes and the mapped values
        response_data = DocumentDetailResponse(
            # Pydantic's populate_by_name=True and Field(alias=...) help map
            file_name=document.file_name, # Provide original field name for alias mapping
            status=api_status,
            timestamps=timestamps_data,
            # Pass the embedded config directly. It will be validated against DocumentConfigDetailsResponse
            # and will be None if document.config was None.
            config=document.config # This is already the correct Pydantic model or None
        )

        return response_data

    except HTTPException:
         # Re-raise HTTPExceptions (like 404 from document.get)
         raise
    except Exception as e:
         print(f"Error getting document {document_id}: {e}")
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=f"Failed to retrieve document details: {e}"
         )
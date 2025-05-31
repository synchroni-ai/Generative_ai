# app/api/models/responses.py

import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field  # Import Field for aliases
from beanie import PydanticObjectId  # Needed if you include _id
from app.models import ConfigModel


# Sub-model for timestamps in the response
class DocumentTimestampsResponse(BaseModel):
    uploaded_at: datetime.datetime
    processed_at: Optional[datetime.datetime] = None

    class Config:
        # Ensure datetimes are serialized correctly
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}


# Main response model for GET /documents/{document_id}
class DocumentDetailResponse(BaseModel):
    # Use Field(alias=...) to map internal model names to desired response names
    name: str = Field(
        alias="file_name"
    )  # Map file_name from Document model to 'name' in response
    status: int  # The integer status code
    config: Optional[ConfigModel] = None  # Embed the config sub-model
    timestamps: DocumentTimestampsResponse  # Embed the timestamps sub-model

    class Config:
        # Need to configure Pydantic to accept attributes (fields from Beanie model)
        populate_by_name = True  # Use field names for mapping (e.g., 'name')
        json_encoders = {
            PydanticObjectId: str,  # Still useful if you decide to add _id later
        }
        arbitrary_types_allowed = True  # Allow PydanticObjectId if used
        # orm_mode = True # For compatibility with ORMs/Beanie


class DeletedDocumentSummary(BaseModel):  # <--- DeletedDocumentSummary
    document_id: str  # The ID of the document
    status: str  # "success" or "failed"
    error: Optional[str] = None  # Reason for failure


class BatchDeleteResponse(BaseModel):  # <--- BatchDeleteResponse
    total_requested: int
    successfully_deleted: int
    failed_deletions: List[DeletedDocumentSummary] = []


# --- Models for Batch Upload Response ---


# Status in the batch upload response is a string ("uploaded", "queued")
class UploadedDocumentResponse(BaseModel):
    file_name: str
    document_id: str = Field(alias="_id")  # Map Beanie's _id to document_id in response
    status: str  # e.g., "uploaded", "queued" - comes from Enum value
    uploaded_by: Optional[str] = None
    s3_url: str  # <--- Add this line


class UploadErrorResponse(BaseModel):
    file_name: str
    error: str


class BatchUploadResponse(BaseModel):  # <--- BatchUploadResponse
    dataspace_id: str
    uploaded: List[UploadedDocumentResponse] = (
        []
    )  # List of successfully uploaded document info
    errors: List[UploadErrorResponse] = (
        []
    )  # List of files that failed upload/initial processing
    # Optional: Add job_id if you enqueue background tasks here
    # job_id: Optional[str] = None

    class Config:
        # Allow mapping from Document model attributes and handle ObjectId
        populate_by_name = True
        json_encoders = {PydanticObjectId: str}
        arbitrary_types_allowed = True


# Sub-model for the config details in the GET /documents/{document_id} response
# This matches the structure embedded in the Document model (DocumentConfigDetails)
class DocumentConfigDetailsResponse(
    BaseModel
):  # <--- This is likely the model you need for config responses
    llm_model: str
    temperature: float
    # subtype could be a string or Literal here, depending on desired validation
    subtype: str  # Use str if you just want to pass the string value through
    use_case: str
    # Include timestamps for the config itself if needed in the response
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    # Add other config fields here


# Sub-model for timestamps in the GET /documents/{document_id} response
class DocumentTimestampsResponse(BaseModel):
    uploaded_at: datetime.datetime
    processed_at: Optional[datetime.datetime] = None
    # Optionally include last_configured here if needed in the response
    # last_configured: Optional[datetime.datetime] = None

    class Config:
        # Ensure datetimes are serialized correctly
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}
        # Allow mapping from Document model attributes if needed
        # populate_by_name = True


# Main response model for GET /documents/{document_id}
class DocumentDetailResponse(BaseModel):
    # Use Field(alias=...) to map internal model names to desired response names
    name: str = Field(
        alias="file_name"
    )  # Map file_name from Document model to 'name' in response
    status: int  # The integer status code as required
    # Reference the config response model. It will be None if document.config was None
    config: Optional[DocumentConfigDetailsResponse] = (
        None  # Use the response model for config
    )
    timestamps: DocumentTimestampsResponse  # Embed the timestamps sub-model

    class Config:
        # Need to configure Pydantic to accept attributes (fields from Beanie model)
        populate_by_name = True  # Use field names for mapping (e.g., 'name')
        json_encoders = {
            PydanticObjectId: str,  # Encode ObjectId as string
            datetime.datetime: lambda dt: dt.isoformat(),  # Ensure datetimes are ISO formatted at the top level too
        }
        arbitrary_types_allowed = True  # Allow PydanticObjectId
        # orm_mode = True # For compatibility with ORMs/Beanie

# app/models.py

import datetime
from typing import Optional, List
from beanie import Document, PydanticObjectId
from enum import Enum # Import Enum 
from pydantic import BaseModel
from app.core.config import get_ist_now # Import the timezone helper

class Dataspace(Document):
    """Represents a Dataspace (Workspace)"""
    name: str
    description: Optional[str] = None
    created_by: Optional[PydanticObjectId] = None
    created_at: datetime.datetime = get_ist_now()
    category: Optional[str] = None
    sub_category: Optional[str] = None

    class Settings:
        name = "dataspaces"


class DocumentStatusEnum(str, Enum):
    UPLOADED = "uploaded"      # Corresponds to API status -1
    PROCESSING = "processing"  # Corresponds to API status 0
    PROCESSED = "processed"    # Corresponds to API status 1
    ERROR = "error"            # Corresponds to API status -2

# Sub-model for the config details (embedded)
class DocumentConfigDetails(BaseModel):
    llm_model: str
    temperature: float
    subtype: str
    use_case: str
    # Add other config fields here

class Document(Document):
    """Represents a BRD document uploaded to a Dataspace"""
    file_name: str
    dataspace_id: PydanticObjectId # References Dataspace._id
    uploaded_by: Optional[PydanticObjectId] = None
    uploaded_at: datetime.datetime = get_ist_now()
    processed_at: Optional[datetime.datetime] = None # <--- Add this field for processed timestamp
    last_configured: Optional[datetime.datetime] = None # Timestamp for when config was last saved/run
    s3_url: str
    # Use the Enum for status in the model
    status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED # <--- Use Enum with default

    # Embedded config details
    config: Optional[DocumentConfigDetails] = None

    class Settings:
        name = "documents"
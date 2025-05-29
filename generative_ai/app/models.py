# app/models.py

import datetime
from beanie import Document, PydanticObjectId
from enum import Enum # Import Enum 
from pydantic import BaseModel,Field
from app.core.config import get_ist_now # Import the timezone helper
from typing import Optional, List, Literal

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
class ConfigModel(BaseModel):
    llm_model: str
    temperature: float
    subtype: Literal["functional", "non-functional"]
    use_case: str
    created_at: Optional[datetime.datetime] = Field(default_factory=get_ist_now)
    updated_at: Optional[datetime.datetime] = Field(default_factory=get_ist_now)
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
    config: Optional[ConfigModel] = None

    class Settings:
        name = "documents"
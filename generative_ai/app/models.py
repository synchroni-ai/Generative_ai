# app/models.py

from typing import Optional, Literal, List
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.config import get_ist_now  # Your timezone helper
from uuid import uuid4
from enum import Enum


# Add User model for authentication
class User(Document):
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=get_ist_now)

    class Settings:
        name = "users"  # MongoDB collection name


class ConfigModel(BaseModel):
    llm_model: Literal["Mistral", "GPT-4"]
    temperature: float

    use_case: List[Literal["test case generation", "functional design", "wireframes"]]
    subtypes: List[
        Literal[
            "functional",
            "non-functional",
            "performance",
            "security",
            "boundary",
            "compliance",
        ]
    ]

    created_at: Optional[datetime] = Field(default_factory=get_ist_now)
    updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


class MultiDocumentConfigModel(BaseModel):
    documents: List[str]  # list of document IDs
    config: ConfigModel  # your existing config model
    created_by: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=get_ist_now)


class Dataspace(Document):
    name: str
    description: Optional[str] = None
    # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
    # created_by: Optional[User] = Link(...) # Example with linking
    # For now, keep it as PydanticObjectId referencing the user _id
    created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
    created_at: datetime = Field(default_factory=get_ist_now)
    category: Optional[str] = None
    sub_category: Optional[str] = None

    class Settings:
        name = "dataspaces"


class Document(Document):
    file_name: str
    dataspace_id: PydanticObjectId
    # Use the User model type hint for uploaded_by if you want Beanie relations (optional)
    # uploaded_by: Optional[User] = Link(...) # Example with linking
    # For now, keep it as PydasticObjectId referencing the user _id
    uploaded_by: Optional[PydanticObjectId] = None  # This will store the user's _id
    uploaded_at: datetime = Field(default_factory=get_ist_now)
    s3_url: str
    status: str = "uploaded"
    config: Optional[ConfigModel] = None  # Embedded ConfigModel here

    class Settings:
        name = "documents"


class DocumentStatusEnum(str, Enum):
    """Enum for internal document status representation."""

    UPLOADED = "uploaded"  # Corresponds to API status -1
    PROCESSING = "processing"  # Corresponds to API status 0
    PROCESSED = "processed"  # Corresponds to API status 1
    ERROR = "error"  # Corresponds to API status -2

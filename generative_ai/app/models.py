# app/models.py

from typing import Optional, Literal, List, Dict, Any
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.core.config import get_ist_now
from enum import Enum, IntEnum

# --- Base Models ---

class VersionInfo(BaseModel):
    version: int
    test_case_count: int
    generation_timestamp: datetime

class User(Document):
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=get_ist_now)

    class Settings:
        name = "users"

class ConfigModel(BaseModel):
    llm_model: Literal["Mistral", "Openai"]
    llm_version: Optional[str] = None
    temperature: float
    use_case: List[Literal["test case generation", "functional design", "wireframes"]]
    subtypes: List[
        Literal[
            "functional", "non_functional", "performance",
            "security", "boundary", "compliance",
        ]
    ]
    created_at: Optional[datetime] = Field(default_factory=get_ist_now)
    updated_at: Optional[datetime] = Field(default_factory=get_ist_now)

    @validator("llm_version", always=True)
    def check_llm_version(cls, value, values):
        llm_model = values.get("llm_model")
        if llm_model == "Openai":
            if not value:
                raise ValueError("llm_version is required for OpenAI models")
            # Use a lowercase list for case-insensitive comparison
            valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o"]
            if value.lower() not in valid_models:
                raise ValueError(
                    f"Invalid llm_version for OpenAI: {value}. Must be one of: {valid_models}"
                )
        return value

class MultiDocumentConfigModel(BaseModel):
    documents: List[str]
    config: ConfigModel
    created_by: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=get_ist_now)

class Dataspace(Document):
    name: str
    description: Optional[str] = None
    created_by: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=get_ist_now)
    category: Optional[str] = None
    sub_category: Optional[str] = None

    class Settings:
        name = "dataspaces"

class DocumentStatusEnum(IntEnum):
    UPLOADED = 0
    PROCESSING = 1
    PROCESSED = 2
    COMPLETE = 3
    ERROR = -1

class Document(Document):
    file_name: str
    dataspace_id: PydanticObjectId
    uploaded_by: PydanticObjectId
    uploaded_at: datetime
    s3_url: str
    status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
    config: Optional[dict] = None

    class Settings:
        name = "documents"

# --- Test Case and Subtype Models ---

class SubtypeStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"

class SubtypeDetail(BaseModel):
    content: str
    status: SubtypeStatusEnum = Field(default=SubtypeStatusEnum.PENDING)

class TestCaseResults(BaseModel):
    # Dict key is the document_id as a string
    documents: Dict[str, Dict[str, SubtypeDetail]]

class TestCaseGroupResult(Document):
    config_id: str
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    use_case: Optional[List[str]] = []
    generated_at: Optional[datetime] = None
    results: TestCaseResults
    summary: Dict[str, Any]

    class Settings:
        # Name of the MongoDB collection, consistent with documents.py
        name = "test_case_group_results"

# --- API Request/Response Models ---

class DocumentSubtypesResponse(BaseModel):
    document_id: str
    document_name: str
    subtypes: Dict[str, SubtypeDetail]

class UpdateSubtypeStatusRequest(BaseModel):
    document_id: str
    subtype_key: str  # e.g., "functional", "security"
    new_status: SubtypeStatusEnum

class TestResult(BaseModel):
    config_id: str
    llm_model: Optional[str]
    temperature: Optional[float]
    use_case: Optional[list]
    generated_at: Optional[datetime]
    results: Dict[str, Any]
    status: str
    summary: Optional[dict] = {}

class CSVTestResult(BaseModel):
    document_name: Optional[str] = None
    TCID: Optional[str] = None
    Test_type: Optional[str] = None
    Title: Optional[str] = None
    Description: Optional[str] = None
    Precondition: Optional[str] = None
    Steps: Optional[str] = None
    Action: Optional[str] = None
    Data: Optional[str] = None
    Result: Optional[str] = None
    Test_Nature: Optional[str] = None
    Test_priority: Optional[str] = None
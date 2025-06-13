# # # # # # # # app/models.py

# # # # # # # from typing import Optional, Literal, List, Dict, Any,Union
# # # # # # # from beanie import Document, PydanticObjectId
# # # # # # # from pydantic import BaseModel, Field
# # # # # # # from datetime import datetime
# # # # # # # from app.core.config import get_ist_now  # Your timezone helper
# # # # # # # from uuid import uuid4
# # # # # # # from enum import IntEnum

# # # # # # # class VersionInfo(BaseModel):
# # # # # # #     version: int
# # # # # # #     test_case_count: int
# # # # # # #     generation_timestamp: datetime
# # # # # # # # Add User model for authentication
# # # # # # # class User(Document):
# # # # # # #     username: str = Field(unique=True, index=True)
# # # # # # #     hashed_password: str
# # # # # # #     created_at: datetime = Field(default_factory=get_ist_now)

# # # # # # #     class Settings:
# # # # # # #         name = "users"  # MongoDB collection name


# # # # # # # class ConfigModel(BaseModel):
# # # # # # #     llm_model: Literal["Mistral", "GPT-4"]
# # # # # # #     temperature: float

# # # # # # #     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
# # # # # # #     subtypes: List[
# # # # # # #         Literal[
# # # # # # #             "functional",
# # # # # # #             "non_functional",
# # # # # # #             "performance",
# # # # # # #             "security",
# # # # # # #             "boundary",
# # # # # # #             "compliance",
# # # # # # #         ]
# # # # # # #     ]

# # # # # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
# # # # # # #     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # # # # class MultiDocumentConfigModel(BaseModel):
# # # # # # #     documents: List[str]  # list of document IDs
# # # # # # #     config: ConfigModel  # your existing config model
# # # # # # #     created_by: Optional[str] = None
# # # # # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # # # # class Dataspace(Document):
# # # # # # #     name: str
# # # # # # #     description: Optional[str] = None
# # # # # # #     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
# # # # # # #     # created_by: Optional[User] = Link(...) # Example with linking
# # # # # # #     # For now, keep it as PydanticObjectId referencing the user _id
# # # # # # #     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
# # # # # # #     created_at: datetime = Field(default_factory=get_ist_now)
# # # # # # #     category: Optional[str] = None
# # # # # # #     sub_category: Optional[str] = None

# # # # # # #     class Settings:
# # # # # # #         name = "dataspaces"
# # # # # # # class DocumentStatusEnum(IntEnum):
# # # # # # #     """Enum for internal document status representation."""
# # # # # # #     UPLOADED = 0         # Initial state
# # # # # # #     PROCESSING = 1       # Generation in progress
# # # # # # #     PROCESSED = 2        # Generation complete
# # # # # # #     ERROR = -1

# # # # # # # class Document(Document):
# # # # # # #     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
# # # # # # #     file_name: str
# # # # # # #     dataspace_id: PydanticObjectId
# # # # # # #     uploaded_by: PydanticObjectId
# # # # # # #     uploaded_at: datetime
# # # # # # #     s3_url: str
# # # # # # #     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
# # # # # # #     config: Optional[dict] = None

# # # # # # #     class Settings:
# # # # # # #         name = "documents"



# # # # # # # class DocumentStatusEnum(IntEnum):
# # # # # # #     """Enum for internal document status representation."""
# # # # # # #     UPLOADED = 0         # Initial state
# # # # # # #     PROCESSING = 1       # Generation in progress
# # # # # # #     PROCESSED = 2        # Generation complete
# # # # # # #     ERROR = -1   

# # # # # # # # class TestResult(BaseModel):
# # # # # # # #     config_id: str
# # # # # # # #     llm_model: Optional[str]
# # # # # # # #     temperature: Optional[float]
# # # # # # # #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# # # # # # # #     generated_at: Optional[datetime]
# # # # # # # #     results: Dict[str, Any]
# # # # # # # #     status: str
# # # # # # # #     summary: Dict[str, Any]
# # # # # # # class TestResult(BaseModel):
# # # # # # #     config_id: str
# # # # # # #     llm_model: Optional[str]
# # # # # # #     temperature: Optional[float]
# # # # # # #     use_case: Optional[list]
# # # # # # #     generated_at: Optional[datetime]
# # # # # # #     results: Dict[str, Any]  # flexible structure, or create a model for documents
# # # # # # #     status: str
# # # # # # #     summary: Optional[dict] = {}
# # # # # # # class CSVTestResult(BaseModel):
# # # # # # #     document_name: Optional[str] = None
# # # # # # #     TCID: Optional[str] = None
# # # # # # #     Test_type: Optional[str] = None
# # # # # # #     Title: Optional[str] = None
# # # # # # #     Description: Optional[str] = None
# # # # # # #     Precondition: Optional[str] = None
# # # # # # #     Steps: Optional[str] = None
# # # # # # #     Action: Optional[str] = None
# # # # # # #     Data: Optional[str] = None
# # # # # # #     Result: Optional[str] = None
# # # # # # #     Test_Nature: Optional[str] = None
# # # # # # #     Test_priority: Optional[str] = None
# # # # # # from typing import Optional, Literal, List, Dict, Any, Union
# # # # # # from beanie import Document, PydanticObjectId
# # # # # # from pydantic import BaseModel, Field
# # # # # # from datetime import datetime
# # # # # # from app.core.config import get_ist_now  # Your timezone helper
# # # # # # from uuid import uuid4
# # # # # # from enum import IntEnum


# # # # # # class VersionInfo(BaseModel):
# # # # # #     version: int
# # # # # #     test_case_count: int
# # # # # #     generation_timestamp: datetime


# # # # # # # Add User model for authentication
# # # # # # class User(Document):
# # # # # #     username: str = Field(unique=True, index=True)
# # # # # #     hashed_password: str
# # # # # #     created_at: datetime = Field(default_factory=get_ist_now)

# # # # # #     class Settings:
# # # # # #         name = "users"  # MongoDB collection name


# # # # # # class ConfigModel(BaseModel):
# # # # # #     llm_model: Literal["Mistral", "GPT-4"]
# # # # # #     temperature: float

# # # # # #     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
# # # # # #     subtypes: List[
# # # # # #         Literal[
# # # # # #             "functional",
# # # # # #             "non_functional",
# # # # # #             "performance",
# # # # # #             "security",
# # # # # #             "boundary",
# # # # # #             "compliance",
# # # # # #         ]
# # # # # #     ]

# # # # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
# # # # # #     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # # # class MultiDocumentConfigModel(BaseModel):
# # # # # #     documents: List[str]  # list of document IDs
# # # # # #     config: ConfigModel  # your existing config model
# # # # # #     created_by: Optional[str] = None
# # # # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # # # class Dataspace(Document):
# # # # # #     name: str
# # # # # #     description: Optional[str] = None
# # # # # #     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
# # # # # #     # created_by: Optional[User] = Link(...) # Example with linking
# # # # # #     # For now, keep it as PydanticObjectId referencing the user _id
# # # # # #     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
# # # # # #     created_at: datetime = Field(default_factory=get_ist_now)
# # # # # #     category: Optional[str] = None
# # # # # #     sub_category: Optional[str] = None

# # # # # #     class Settings:
# # # # # #         name = "dataspaces"


# # # # # # class DocumentStatusEnum(IntEnum):
# # # # # #     """Enum for internal document status representation."""
# # # # # #     UPLOADED = 0         # Initial state
# # # # # #     PROCESSING = 1       # Generation in progress
# # # # # #     PROCESSED = 2        # Generation complete
# # # # # #     ERROR = -1
# # # # # #     COMPLETE = 3


# # # # # # class Document(Document):
# # # # # #     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
# # # # # #     file_name: str
# # # # # #     dataspace_id: PydanticObjectId
# # # # # #     uploaded_by: PydanticObjectId
# # # # # #     uploaded_at: datetime
# # # # # #     s3_url: str
# # # # # #     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
# # # # # #     config: Optional[dict] = None

# # # # # #     class Settings:
# # # # # #         name = "documents"


# # # # # # # class TestResult(BaseModel):
# # # # # # #     config_id: str
# # # # # # #     llm_model: Optional[str]
# # # # # # #     temperature: Optional[float]
# # # # # # #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# # # # # # #     generated_at: Optional[datetime]
# # # # # # #     results: Dict[str, Any]
# # # # # # #     status: str
# # # # # # #     summary: Dict[str, Any]
# # # # # # class TestResult(BaseModel):
# # # # # #     config_id: str
# # # # # #     llm_model: Optional[str]
# # # # # #     temperature: Optional[float]
# # # # # #     use_case: Optional[list]
# # # # # #     generated_at: Optional[datetime]
# # # # # #     results: Dict[str, Any]  # flexible structure, or create a model for documents
# # # # # #     status: str
# # # # # #     summary: Optional[dict] = {}


# # # # # # class CSVTestResult(BaseModel):
# # # # # #     document_name: Optional[str] = None
# # # # # #     TCID: Optional[str] = None
# # # # # #     Test_type: Optional[str] = None
# # # # # #     Title: Optional[str] = None
# # # # # #     Description: Optional[str] = None
# # # # # #     Precondition: Optional[str] = None
# # # # # #     Steps: Optional[str] = None
# # # # # #     Action: Optional[str] = None
# # # # # #     Data: Optional[str] = None
# # # # # #     Result: Optional[str] = None
# # # # # #     Test_Nature: Optional[str] = None
# # # # # #     Test_priority: Optional[str] = None
# # # # # from typing import Optional, Literal, List, Dict, Any, Union
# # # # # from beanie import Document, PydanticObjectId
# # # # # from pydantic import BaseModel, Field
# # # # # from datetime import datetime
# # # # # from app.core.config import get_ist_now  # Your timezone helper
# # # # # from uuid import uuid4
# # # # # from enum import IntEnum


# # # # # class VersionInfo(BaseModel):
# # # # #     version: int
# # # # #     test_case_count: int
# # # # #     generation_timestamp: datetime


# # # # # # Add User model for authentication
# # # # # class User(Document):
# # # # #     username: str = Field(unique=True, index=True)
# # # # #     hashed_password: str
# # # # #     created_at: datetime = Field(default_factory=get_ist_now)

# # # # #     class Settings:
# # # # #         name = "users"  # MongoDB collection name


# # # # # class ConfigModel(BaseModel):
# # # # #     llm_model: Literal["Mistral", "GPT-4", "GPT-3.5-turbo", "GPT-4o"]  # Add new models
# # # # #     temperature: float

# # # # #     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
# # # # #     subtypes: List[
# # # # #         Literal[
# # # # #             "functional",
# # # # #             "non_functional",
# # # # #             "performance",
# # # # #             "security",
# # # # #             "boundary",
# # # # #             "compliance",
# # # # #         ]
# # # # #     ]

# # # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
# # # # #     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # # class MultiDocumentConfigModel(BaseModel):
# # # # #     documents: List[str]  # list of document IDs
# # # # #     config: ConfigModel  # your existing config model
# # # # #     created_by: Optional[str] = None
# # # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # # class Dataspace(Document):
# # # # #     name: str
# # # # #     description: Optional[str] = None
# # # # #     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
# # # # #     # created_by: Optional[User] = Link(...) # Example with linking
# # # # #     # For now, keep it as PydanticObjectId referencing the user _id
# # # # #     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
# # # # #     created_at: datetime = Field(default_factory=get_ist_now)
# # # # #     category: Optional[str] = None
# # # # #     sub_category: Optional[str] = None

# # # # #     class Settings:
# # # # #         name = "dataspaces"


# # # # # class DocumentStatusEnum(IntEnum):
# # # # #     """Enum for internal document status representation."""
# # # # #     UPLOADED = 0         # Initial state
# # # # #     PROCESSING = 1       # Generation in progress
# # # # #     PROCESSED = 2        # Generation complete
# # # # #     ERROR = -1
# # # # #     COMPLETE = 3


# # # # # class Document(Document):
# # # # #     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
# # # # #     file_name: str
# # # # #     dataspace_id: PydanticObjectId
# # # # #     uploaded_by: PydanticObjectId
# # # # #     uploaded_at: datetime
# # # # #     s3_url: str
# # # # #     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
# # # # #     config: Optional[dict] = None

# # # # #     class Settings:
# # # # #         name = "documents"


# # # # # # class TestResult(BaseModel):
# # # # # #     config_id: str
# # # # # #     llm_model: Optional[str]
# # # # # #     temperature: Optional[float]
# # # # # #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# # # # # #     generated_at: Optional[datetime]
# # # # # #     results: Dict[str, Any]
# # # # # #     status: str
# # # # # #     summary: Dict[str, Any]
# # # # # class TestResult(BaseModel):
# # # # #     config_id: str
# # # # #     llm_model: Optional[str]
# # # # #     temperature: Optional[float]
# # # # #     use_case: Optional[list]
# # # # #     generated_at: Optional[datetime]
# # # # #     results: Dict[str, Any]  # flexible structure, or create a model for documents
# # # # #     status: str
# # # # #     summary: Optional[dict] = {}


# # # # # class CSVTestResult(BaseModel):
# # # # #     document_name: Optional[str] = None
# # # # #     TCID: Optional[str] = None
# # # # #     Test_type: Optional[str] = None
# # # # #     Title: Optional[str] = None
# # # # #     Description: Optional[str] = None
# # # # #     Precondition: Optional[str] = None
# # # # #     Steps: Optional[str] = None
# # # # #     Action: Optional[str] = None
# # # # #     Data: Optional[str] = None
# # # # #     Result: Optional[str] = None
# # # # #     Test_Nature: Optional[str] = None
# # # # #     Test_priority: Optional[str] = None

# # # # from typing import Optional, Literal, List, Dict, Any, Union
# # # # from beanie import Document, PydanticObjectId
# # # # from pydantic import BaseModel, Field
# # # # from datetime import datetime
# # # # from app.core.config import get_ist_now  # Your timezone helper
# # # # from uuid import uuid4
# # # # from enum import IntEnum


# # # # class VersionInfo(BaseModel):
# # # #     version: int
# # # #     test_case_count: int
# # # #     generation_timestamp: datetime


# # # # # Add User model for authentication
# # # # class User(Document):
# # # #     username: str = Field(unique=True, index=True)
# # # #     hashed_password: str
# # # #     created_at: datetime = Field(default_factory=get_ist_now)

# # # #     class Settings:
# # # #         name = "users"  # MongoDB collection name


# # # # class ConfigModel(BaseModel):
# # # #     llm_model: Literal["Mistral", "Openai"]  # Modified to accept "Openai"
# # # #     llm_version: Literal["GPT-4", "GPT-3.5-turbo", "GPT-4o"] # added llm_version
# # # #     temperature: float

# # # #     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
# # # #     subtypes: List[
# # # #         Literal[
# # # #             "functional",
# # # #             "non_functional",
# # # #             "performance",
# # # #             "security",
# # # #             "boundary",
# # # #             "compliance",
# # # #         ]
# # # #     ]

# # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
# # # #     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # class MultiDocumentConfigModel(BaseModel):
# # # #     documents: List[str]  # list of document IDs
# # # #     config: ConfigModel  # your existing config model
# # # #     created_by: Optional[str] = None
# # # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # # class Dataspace(Document):
# # # #     name: str
# # # #     description: Optional[str] = None
# # # #     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
# # # #     # created_by: Optional[User] = Link(...) # Example with linking
# # # #     # For now, keep it as PydanticObjectId referencing the user _id
# # # #     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
# # # #     created_at: datetime = Field(default_factory=get_ist_now)
# # # #     category: Optional[str] = None
# # # #     sub_category: Optional[str] = None

# # # #     class Settings:
# # # #         name = "dataspaces"


# # # # class DocumentStatusEnum(IntEnum):
# # # #     """Enum for internal document status representation."""
# # # #     UPLOADED = 0         # Initial state
# # # #     PROCESSING = 1       # Generation in progress
# # # #     PROCESSED = 2        # Generation complete
# # # #     ERROR = -1
# # # #     COMPLETE = 3


# # # # class Document(Document):
# # # #     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
# # # #     file_name: str
# # # #     dataspace_id: PydanticObjectId
# # # #     uploaded_by: PydanticObjectId
# # # #     uploaded_at: datetime
# # # #     s3_url: str
# # # #     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
# # # #     config: Optional[dict] = None

# # # #     class Settings:
# # # #         name = "documents"


# # # # # class TestResult(BaseModel):
# # # # #     config_id: str
# # # # #     llm_model: Optional[str]
# # # # #     temperature: Optional[float]
# # # # #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# # # # #     generated_at: Optional[datetime]
# # # # #     results: Dict[str, Any]
# # # # #     status: str
# # # # #     summary: Dict[str, Any]
# # # # class TestResult(BaseModel):
# # # #     config_id: str
# # # #     llm_model: Optional[str]
# # # #     temperature: Optional[float]
# # # #     use_case: Optional[list]
# # # #     generated_at: Optional[datetime]
# # # #     results: Dict[str, Any]  # flexible structure, or create a model for documents
# # # #     status: str
# # # #     summary: Optional[dict] = {}


# # # # class CSVTestResult(BaseModel):
# # # #     document_name: Optional[str] = None
# # # #     TCID: Optional[str] = None
# # # #     Test_type: Optional[str] = None
# # # #     Title: Optional[str] = None
# # # #     Description: Optional[str] = None
# # # #     Precondition: Optional[str] = None
# # # #     Steps: Optional[str] = None
# # # #     Action: Optional[str] = None
# # # #     Data: Optional[str] = None
# # # #     Result: Optional[str] = None
# # # #     Test_Nature: Optional[str] = None
# # # #     Test_priority: Optional[str] = None
# # # from typing import Optional, Literal, List, Dict, Any, Union
# # # from beanie import Document, PydanticObjectId
# # # from pydantic import BaseModel, Field
# # # from datetime import datetime
# # # from app.core.config import get_ist_now  # Your timezone helper
# # # from uuid import uuid4
# # # from enum import IntEnum


# # # class VersionInfo(BaseModel):
# # #     version: int
# # #     test_case_count: int
# # #     generation_timestamp: datetime


# # # # Add User model for authentication
# # # class User(Document):
# # #     username: str = Field(unique=True, index=True)
# # #     hashed_password: str
# # #     created_at: datetime = Field(default_factory=get_ist_now)

# # #     class Settings:
# # #         name = "users"  # MongoDB collection name


# # # class ConfigModel(BaseModel):
# # #     llm_model: Literal["Mistral", "Openai"]  # Modified to accept "Openai"
# # #     llm_version: str # change to str
# # #     temperature: float

# # #     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
# # #     subtypes: List[
# # #         Literal[
# # #             "functional",
# # #             "non_functional",
# # #             "performance",
# # #             "security",
# # #             "boundary",
# # #             "compliance",
# # #         ]
# # #     ]

# # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
# # #     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # class MultiDocumentConfigModel(BaseModel):
# # #     documents: List[str]  # list of document IDs
# # #     config: ConfigModel  # your existing config model
# # #     created_by: Optional[str] = None
# # #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # # class Dataspace(Document):
# # #     name: str
# # #     description: Optional[str] = None
# # #     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
# # #     # created_by: Optional[User] = Link(...) # Example with linking
# # #     # For now, keep it as PydanticObjectId referencing the user _id
# # #     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
# # #     created_at: datetime = Field(default_factory=get_ist_now)
# # #     category: Optional[str] = None
# # #     sub_category: Optional[str] = None

# # #     class Settings:
# # #         name = "dataspaces"


# # # class DocumentStatusEnum(IntEnum):
# # #     """Enum for internal document status representation."""
# # #     UPLOADED = 0         # Initial state
# # #     PROCESSING = 1       # Generation in progress
# # #     PROCESSED = 2        # Generation complete
# # #     ERROR = -1
# # #     COMPLETE = 3


# # # class Document(Document):
# # #     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
# # #     file_name: str
# # #     dataspace_id: PydanticObjectId
# # #     uploaded_by: PydanticObjectId
# # #     uploaded_at: datetime
# # #     s3_url: str
# # #     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
# # #     config: Optional[dict] = None

# # #     class Settings:
# # #         name = "documents"


# # # # class TestResult(BaseModel):
# # # #     config_id: str
# # # #     llm_model: Optional[str]
# # # #     temperature: Optional[float]
# # # #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# # # #     generated_at: Optional[datetime]
# # # #     results: Dict[str, Any]
# # # #     status: str
# # # #     summary: Dict[str, Any]
# # # class TestResult(BaseModel):
# # #     config_id: str
# # #     llm_model: Optional[str]
# # #     temperature: Optional[float]
# # #     use_case: Optional[list]
# # #     generated_at: Optional[datetime]
# # #     results: Dict[str, Any]  # flexible structure, or create a model for documents
# # #     status: str
# # #     summary: Optional[dict] = {}


# # # class CSVTestResult(BaseModel):
# # #     document_name: Optional[str] = None
# # #     TCID: Optional[str] = None
# # #     Test_type: Optional[str] = None
# # #     Title: Optional[str] = None
# # #     Description: Optional[str] = None
# # #     Precondition: Optional[str] = None
# # #     Steps: Optional[str] = None
# # #     Action: Optional[str] = None
# # #     Data: Optional[str] = None
# # #     Result: Optional[str] = None
# # #     Test_Nature: Optional[str] = None
# # #     Test_priority: Optional[str] = None
# # from typing import Optional, Literal, List, Dict, Any, Union
# # from beanie import Document, PydanticObjectId
# # from pydantic import BaseModel, Field
# # from datetime import datetime
# # from app.core.config import get_ist_now  # Your timezone helper
# # from uuid import uuid4
# # from enum import IntEnum


# # class VersionInfo(BaseModel):
# #     version: int
# #     test_case_count: int
# #     generation_timestamp: datetime


# # # Add User model for authentication
# # class User(Document):
# #     username: str = Field(unique=True, index=True)
# #     hashed_password: str
# #     created_at: datetime = Field(default_factory=get_ist_now)

# #     class Settings:
# #         name = "users"  # MongoDB collection name


# # class ConfigModel(BaseModel):
# #     llm_model: Literal["Mistral", "Openai"]  # Modified to accept "Openai"
# #     llm_version: Optional[str] = None # change to Optional[str]
# #     temperature: float

# #     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
# #     subtypes: List[
# #         Literal[
# #             "functional",
# #             "non_functional",
# #             "performance",
# #             "security",
# #             "boundary",
# #             "compliance",
# #         ]
# #     ]

# #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
# #     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # class MultiDocumentConfigModel(BaseModel):
# #     documents: List[str]  # list of document IDs
# #     config: ConfigModel  # your existing config model
# #     created_by: Optional[str] = None
# #     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# # class Dataspace(Document):
# #     name: str
# #     description: Optional[str] = None
# #     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
# #     # created_by: Optional[User] = Link(...) # Example with linking
# #     # For now, keep it as PydanticObjectId referencing the user _id
# #     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
# #     created_at: datetime = Field(default_factory=get_ist_now)
# #     category: Optional[str] = None
# #     sub_category: Optional[str] = None

# #     class Settings:
# #         name = "dataspaces"


# # class DocumentStatusEnum(IntEnum):
# #     """Enum for internal document status representation."""
# #     UPLOADED = 0         # Initial state
# #     PROCESSING = 1       # Generation in progress
# #     PROCESSED = 2        # Generation complete
# #     ERROR = -1
# #     COMPLETE = 3


# # class Document(Document):
# #     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
# #     file_name: str
# #     dataspace_id: PydanticObjectId
# #     uploaded_by: PydanticObjectId
# #     uploaded_at: datetime
# #     s3_url: str
# #     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
# #     config: Optional[dict] = None

# #     class Settings:
# #         name = "documents"


# # # class TestResult(BaseModel):
# # #     config_id: str
# # #     llm_model: Optional[str]
# # #     temperature: Optional[float]
# # #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# # #     generated_at: Optional[datetime]
# # #     results: Dict[str, Any]
# # #     status: str
# # #     summary: Dict[str, Any]
# # class TestResult(BaseModel):
# #     config_id: str
# #     llm_model: Optional[str]
# #     temperature: Optional[float]
# #     use_case: Optional[list]
# #     generated_at: Optional[datetime]
# #     results: Dict[str, Any]  # flexible structure, or create a model for documents
# #     status: str
# #     summary: Optional[dict] = {}


# # class CSVTestResult(BaseModel):
# #     document_name: Optional[str] = None
# #     TCID: Optional[str] = None
# #     Test_type: Optional[str] = None
# #     Title: Optional[str] = None
# #     Description: Optional[str] = None
# #     Precondition: Optional[str] = None
# #     Steps: Optional[str] = None
# #     Action: Optional[str] = None
# #     Data: Optional[str] = None
# #     Result: Optional[str] = None
# #     Test_Nature: Optional[str] = None
# #     Test_priority: Optional[str] = None

# from typing import Optional, Literal, List, Dict, Any, Union
# from beanie import Document, PydanticObjectId
# from pydantic import BaseModel, Field, validator
# from datetime import datetime
# from app.core.config import get_ist_now  # Your timezone helper
# from uuid import uuid4
# from enum import IntEnum

# class VersionInfo(BaseModel):
#     version: int
#     test_case_count: int
#     generation_timestamp: datetime


# # Add User model for authentication
# class User(Document):
#     username: str = Field(unique=True, index=True)
#     hashed_password: str
#     created_at: datetime = Field(default_factory=get_ist_now)

#     class Settings:
#         name = "users"  # MongoDB collection name


# class ConfigModel(BaseModel):
#     llm_model: Literal["Mistral", "Openai"]  # Modified to accept "Openai"
#     llm_version: Optional[str] = None # change to Optional[str]
#     temperature: float

#     use_case: List[Literal["test case generation", "functional design", "wireframes"]]
#     subtypes: List[
#         Literal[
#             "functional",
#             "non_functional",
#             "performance",
#             "security",
#             "boundary",
#             "compliance",
#         ]
#     ]

#     created_at: Optional[datetime] = Field(default_factory=get_ist_now)
#     updated_at: Optional[datetime] = Field(default_factory=get_ist_now)

#     @validator("llm_version", always=True)
#     def check_llm_version(cls, value, values):
#         llm_model = values.get("llm_model")
#         if llm_model == "Openai":
#             if not value:
#                 raise ValueError("llm_version is required for OpenAI models")
#             valid_models = ["GPT-4", "GPT-3.5-turbo", "GPT-4o"]  # Add more as needed
#             if value not in valid_models:
#                 raise ValueError(f"Invalid llm_version for OpenAI: {value}.  Must be one of: {valid_models}")
#         return value


# class MultiDocumentConfigModel(BaseModel):
#     documents: List[str]  # list of document IDs
#     config: ConfigModel  # your existing config model
#     created_by: Optional[str] = None
#     created_at: Optional[datetime] = Field(default_factory=get_ist_now)


# class Dataspace(Document):
#     name: str
#     description: Optional[str] = None
#     # Use the User model type hint for created_by if you want Beanie relations (optional for basic auth)
#     # created_by: Optional[User] = Link(...) # Example with linking
#     # For now, keep it as PydanticObjectId referencing the user _id
#     created_by: Optional[PydanticObjectId] = None  # This will store the user's _id
#     created_at: datetime = Field(default_factory=get_ist_now)
#     category: Optional[str] = None
#     sub_category: Optional[str] = None

#     class Settings:
#         name = "dataspaces"


# class DocumentStatusEnum(IntEnum):
#     """Enum for internal document status representation."""
#     UPLOADED = 0         # Initial state
#     PROCESSING = 1       # Generation in progress
#     PROCESSED = 2        # Generation complete
#     ERROR = -1
#     COMPLETE = 3


# class Document(Document):
#     id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
#     file_name: str
#     dataspace_id: PydanticObjectId
#     uploaded_by: PydanticObjectId
#     uploaded_at: datetime
#     s3_url: str
#     status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
#     config: Optional[dict] = None

#     class Settings:
#         name = "documents"


# # class TestResult(BaseModel):
# #     config_id: str
# #     llm_model: Optional[str]
# #     temperature: Optional[float]
# #     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
# #     generated_at: Optional[datetime]
# #     results: Dict[str, Any]
# #     status: str
# #     summary: Dict[str, Any]
# class TestResult(BaseModel):
#     config_id: str
#     llm_model: Optional[str]
#     temperature: Optional[float]
#     use_case: Optional[list]
#     generated_at: Optional[datetime]
#     results: Dict[str, Any]  # flexible structure, or create a model for documents
#     status: str
#     summary: Optional[dict] = {}


# class CSVTestResult(BaseModel):
#     document_name: Optional[str] = None
#     TCID: Optional[str] = None
#     Test_type: Optional[str] = None
#     Title: Optional[str] = None
#     Description: Optional[str] = None
#     Precondition: Optional[str] = None
#     Steps: Optional[str] = None
#     Action: Optional[str] = None
#     Data: Optional[str] = None
#     Result: Optional[str] = None
#     Test_Nature: Optional[str] = None
#     Test_priority: Optional[str] = None
from typing import Optional, Literal, List, Dict, Any, Union
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.core.config import get_ist_now  # Your timezone helper
from uuid import uuid4
from enum import IntEnum

class VersionInfo(BaseModel):
    version: int
    test_case_count: int
    generation_timestamp: datetime


# Add User model for authentication
class User(Document):
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=get_ist_now)

    class Settings:
        name = "users"  # MongoDB collection name


class ConfigModel(BaseModel):
    llm_model: Literal["Mistral", "Openai"]  # Modified to accept "Openai"
    llm_version: Optional[str] = None # change to Optional[str]
    temperature: float

    use_case: List[Literal["test case generation", "functional design", "wireframes"]]
    subtypes: List[
        Literal[
            "functional",
            "non_functional",
            "performance",
            "security",
            "boundary",
            "compliance",
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

            valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o"]  # All lowercase
            if value.lower() not in valid_models:  # Convert input to lowercase
                raise ValueError(f"Invalid llm_version for OpenAI: {value}.  Must be one of: {valid_models}")
        return value


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


class DocumentStatusEnum(IntEnum):
    """Enum for internal document status representation."""
    UPLOADED = 0         # Initial state
    PROCESSING = 1       # Generation in progress
    PROCESSED = 2        # Generation complete
    ERROR = -1
    COMPLETE = 3


class Document(Document):
    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
    file_name: str
    dataspace_id: PydanticObjectId
    uploaded_by: PydanticObjectId
    uploaded_at: datetime
    s3_url: str
    status: DocumentStatusEnum = DocumentStatusEnum.UPLOADED
    config: Optional[dict] = None

    class Settings:
        name = "documents"


# class TestResult(BaseModel):
#     config_id: str
#     llm_model: Optional[str]
#     temperature: Optional[float]
#     use_case: Optional[Union[str, List[str]]]  # Allow either string or list
#     generated_at: Optional[datetime]
#     results: Dict[str, Any]
#     status: str
#     summary: Dict[str, Any]
class TestResult(BaseModel):
    config_id: str
    llm_model: Optional[str]
    temperature: Optional[float]
    use_case: Optional[list]
    generated_at: Optional[datetime]
    results: Dict[str, Any]  # flexible structure, or create a model for documents
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
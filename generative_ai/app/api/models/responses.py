# app/api/models/responses.py

import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field # Import Field for aliases
from beanie import PydanticObjectId # Needed if you include _id

# Sub-model for the config details in the response
# This should match the structure embedded in the Document model
class DocumentConfigDetailsResponse(BaseModel):
    llm_model: Optional[str] = None # Make Optional for response if config can be null
    temperature: Optional[float] = None
    subtype: Optional[str] = None
    use_case: Optional[str] = None
    # Add other config fields here, make them Optional

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
    name: str = Field(alias="file_name") # Map file_name from Document model to 'name' in response
    status: int # The integer status code
    config: Optional[DocumentConfigDetailsResponse] = None # Embed the config sub-model
    timestamps: DocumentTimestampsResponse # Embed the timestamps sub-model

    class Config:
        # Need to configure Pydantic to accept attributes (fields from Beanie model)
        populate_by_name = True # Use field names for mapping (e.g., 'name')
        json_encoders = {
            PydanticObjectId: str, # Still useful if you decide to add _id later
        }
        arbitrary_types_allowed = True # Allow PydanticObjectId if used
        # orm_mode = True # For compatibility with ORMs/Beanie
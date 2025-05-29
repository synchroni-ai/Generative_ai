# app/api/deps.py

from fastapi import Depends, HTTPException, status
from beanie import PydanticObjectId

from app.db.mongodb import get_db 
get_db = get_db # Re-export the DB dependency

async def get_dataspace_by_id(dataspace_id: PydanticObjectId, db=Depends(get_db)):
    from app.models import Dataspace # Import model locally to avoid circular dependency
    dataspace = await Dataspace.get(dataspace_id)
    if not dataspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataspace with ID {dataspace_id} not found")
    return dataspace
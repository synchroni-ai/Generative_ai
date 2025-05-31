from fastapi import APIRouter, HTTPException, Depends
from app.models import ConfigModel
from app.services.config_service import save_config, get_config_by_document_id
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


@router.post("/documents/{document_id}/config")
async def save_document_config(
    document_id: str, config: ConfigModel, db: AsyncIOMotorDatabase = Depends(get_db)
):
    success = await save_config(document_id, config, db)
    if not success:
        raise HTTPException(
            status_code=404, detail="Document not found or update failed"
        )
    return {"message": "Config saved successfully"}


@router.get("/documents/{document_id}/config")
async def get_document_config(
    document_id: str, db: AsyncIOMotorDatabase = Depends(get_db)
):
    config = await get_config_by_document_id(document_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"config": config}

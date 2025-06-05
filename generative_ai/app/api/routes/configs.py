from fastapi import APIRouter, HTTPException, Depends
from app.models import ConfigModel, MultiDocumentConfigModel,User
from app.services.config_service import save_config, get_config_by_document_id
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.api import deps
router = APIRouter()


@router.post("/documents/{document_id}/config")
async def save_document_config(
    document_id: str, config: ConfigModel, db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user)
):
    success = await save_config(document_id, config, db)
    if not success:
        raise HTTPException(
            status_code=404, detail="Document not found or update failed"
        )
    return {"message": "Config saved successfully"}


@router.get("/documents/{document_id}/config")
async def get_document_config(
    document_id: str, db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user)
):
    config = await get_config_by_document_id(document_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"config": config}


@router.post("/configs")
async def save_multi_document_config(
    config_data: MultiDocumentConfigModel, db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user),
):
    config_doc = {
        "documents": [ObjectId(doc_id) for doc_id in config_data.documents],
        "config": config_data.config.dict(),
        "created_by": config_data.created_by,
        "created_at": config_data.created_at,
    }
    result = await db["configurations"].insert_one(config_doc)

    return {
        "message": "Configuration saved",
        "config_id": str(result.inserted_id),
        "created_at": config_data.created_at,
    }



@router.get("/configs")
async def list_all_configs(
    db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user),
):
    """
    Returns a list of all configurations with minimal metadata: config_id and created_at.
    """
    configs_cursor = db["configurations"].find({})
    configs = []
    async for config in configs_cursor:
        configs.append({
            "config_id": str(config["_id"]),
            "created_at": config.get("created_at")
        })

    return {"configs": configs}


@router.get("/configs/{config_id}")
async def get_config_by_id(
    config_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Gets a configuration by its ID. Requires authentication.
    """
    config = await db["configurations"].find_one({"_id": ObjectId(config_id)})
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    # Remove fields you don't want to expose
    config.pop("created_by", None)
    config.pop("created_at", None)

    # Convert ObjectId fields to strings
    config["_id"] = str(config["_id"])
    config["documents"] = [str(doc_id) for doc_id in config.get("documents", [])]

    print(f"User {current_user.username} (ID: {current_user.id}) retrieved config by ID: {config_id}")
    return {"config": config}
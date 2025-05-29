from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import ConfigModel
 
async def save_config(id: str, config: ConfigModel, db: AsyncIOMotorDatabase):
    result = await db.documents.update_one(
        {
            "_id": ObjectId(id)
            },
        {"$set": {"config": config.dict()}}
    )
    return result.modified_count == 1
 
async def get_config_by_document_id(id: str, db: AsyncIOMotorDatabase):
    document = await db.documents.find_one({"_id": ObjectId(id)}, {"config": 1})
    return document.get("config") if document else None
 
 
# app/db/mongodb.py

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient
from pymongo.errors import ConnectionFailure, ConfigurationError, OperationFailure
from beanie import init_beanie

from app.core.config import MONGO_URI, MONGO_DB_NAME
from app.models import Dataspace, Document # Import your models

# Add other models here as you create them (e.g., User, Config, Job, Result)
document_models = [Dataspace, Document]

db_client: Optional[AgnosticClient] = None

async def connect_db():
    """Initializes MongoDB connection and Beanie ODM."""
    global db_client
    print("Attempting to connect to MongoDB...")
    print(f"MONGO_URI: {MONGO_URI}")
    print(f"MONGO_DB_NAME: {MONGO_DB_NAME}")


    if not MONGO_URI or not MONGO_DB_NAME:
         print("\n!!! WARNING: MongoDB connection not fully configured. Set MONGO_URI and MONGO_DB_NAME env vars. !!!\n")
         return

    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        await client.admin.command('ismaster')

        db_client = client

        print("MongoDB connection successful. Initializing Beanie...")
        await init_beanie(
            database=db_client[MONGO_DB_NAME],
            document_models=document_models
        )
        print("Beanie initialized.")
        print("DB connection function complete.")

    except (ConnectionFailure, ConfigurationError, OperationFailure) as e:
        print(f"\n!!! ERROR: Failed to connect to MongoDB: {e} !!!\n")
        db_client = None
    except Exception as e:
        print(f"\n!!! An unexpected error occurred during DB connection: {e} !!!\n")
        db_client = None

async def close_db():
    """Closes MongoDB connection."""
    global db_client
    print("Closing MongoDB connection.")
    if db_client:
        db_client.close()
        print("MongoDB connection closed.")
    else:
        print("No MongoDB connection to close.")

# This dependency will be used in your routes
async def get_db():
    """Dependency to get the MongoDB database connection status."""
    if db_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not established."
        )
   
    return True # Or just pass if you don't need to return anything
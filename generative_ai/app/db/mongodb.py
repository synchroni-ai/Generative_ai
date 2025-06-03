# app/db/mongodb.py

from typing import Optional
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)  # <-- Import AsyncIOMotorDatabase
from motor.core import AgnosticClient
from pymongo.errors import ConnectionFailure, ConfigurationError, OperationFailure
from beanie import init_beanie
from fastapi import HTTPException, status  # <-- Import HTTPException and status

from app.core.config import MONGO_URI, MONGO_DB_NAME

from app.models import Dataspace, Document, User

document_models = [Dataspace, Document, User]


db_client: Optional[AgnosticClient] = None


async def connect_db():
    """Initializes MongoDB connection and Beanie ODM."""
    global db_client
    print("Attempting to connect to MongoDB...")
    print(f"MONGO_URI: {MONGO_URI}")
    print(f"MONGO_DB_NAME: {MONGO_DB_NAME}")

    if not MONGO_URI or not MONGO_DB_NAME:
        print(
            "\n!!! WARNING: MongoDB connection not fully configured. Set MONGO_URI and MONGO_DB_NAME env vars. !!!\n"
        )
        return

    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        await client.admin.command("ismaster")  # Check connection

        db_client = client

        print("MongoDB connection successful. Initializing Beanie...")
        await init_beanie(
            database=db_client[MONGO_DB_NAME], document_models=document_models
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


# This dependency will be used in your routes and services
# CHANGE: Return the actual database object
async def get_db() -> AsyncIOMotorDatabase:  # Add type hint for clarity
    """Dependency to get the MongoDB database object."""
    global db_client
    if db_client is None:
        # Add print for debugging if this case is hit
        print("ERROR: Database client is None in get_db dependency.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not established.",
        )
    try:
        # Return the actual Motor database object
        database: AsyncIOMotorDatabase = db_client[MONGO_DB_NAME]
        return database
    except Exception as e:
        # Add print for debugging if accessing the database fails
        print(f"ERROR: Failed to get database object from client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database object: {e}",
        )

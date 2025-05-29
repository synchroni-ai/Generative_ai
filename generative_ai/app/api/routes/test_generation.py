from typing import List, Optional
from fastapi import APIRouter, HTTPException, Form, Query
from fastapi import Depends
from bson import ObjectId
from pathlib import Path
import os

from app.db.mongodb import get_db  # Assuming this is how you get your MongoDB connection
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.celery_app import celery_app
from app.tasks.task_with_api_key import process_and_generate_task_multiple
# Assuming data_ingestion, test_case_utils, VALID_TEST_CASE_TYPES, collection are available
from utils import data_ingestion, test_case_utils
# Constants
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
VALID_TEST_CASE_TYPES = [
    "functional",
    "non-functional",
    "security",
    "performance",
    "boundary",
    "compliance",
]

router = APIRouter()


@router.post("/api/generate_test_cases_multiple")
async def generate_test_cases_multiple(
    file_ids: List[str] = Form(...),  # List of file IDs
    model_name: Optional[str] = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form("all"),
    db: AsyncIOMotorDatabase = Depends(get_db), # injects mongodb
):
    """
    Generates test cases for multiple files, processing all test case types for one file before moving to the next.
    """

    # collection access through db injection
    collection = db["test_case_generation"]

    # Validate file_ids
    documents_data = []
    for file_id in file_ids:
        try:
            document = await collection.find_one({"_id": ObjectId(file_id)})  # Await the coroutine
        except Exception:
            raise HTTPException(
                status_code=400, detail=f"Invalid file_id format: {file_id}"
            )

        if not document:
            raise HTTPException(
                status_code=404, detail=f"Document not found in the database: {file_id}"
            )

        file_path = Path(document.get("file_path"))
        if not file_path.exists():
            raise HTTPException(
                status_code=404, detail=f"File not found on disk: {file_id}"
            )

        documents_data.append(
            {
                "file_id": file_id,
                "file_path": str(file_path),
                "file_name": file_path.name,  # Add file name for tracking
            }
        )

    # Parse and validate test_case_types (same as before)
    test_case_types_list = [t.strip().lower() for t in test_case_types.split(",")]
    if "all" in test_case_types_list:
        test_case_types_list = VALID_TEST_CASE_TYPES
    else:
        for test_case_type in test_case_types_list:
            if test_case_type not in VALID_TEST_CASE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid test_case_type: {test_case_type}. Must be one of {VALID_TEST_CASE_TYPES} or 'all'.",
                )

    # API key fallback logic (same as before)
    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
    warning = (
        "Using default API key. Consider providing your own to avoid shared limits."
        if not api_key
        else None
    )

    # Create a single document ID for tracking the multiple files job
    multiple_files_document_id = str(ObjectId())

    # ✅ Set initial status = 0 (processing) for multiple files document ID
    await collection.insert_one(
        {
            "_id": ObjectId(multiple_files_document_id),  # Store ID as ObjectId
            "status": 0,
            "selected_model": model_name,
            "api_key_used": f"...{api_key_to_use[-5:]}",
            "file_ids": file_ids,  # Store the file_ids being processed
            "file_names": [
                doc["file_name"] for doc in documents_data
            ],  # store the file names being proccessed
            "test_case_types": test_case_types_list,
            "type": "multiple",
        }
    )

    # Trigger Celery task FOR MULTIPLE DOCUMENTS. This now loops through the documents
    task = process_and_generate_task_multiple.delay(
        file_ids=documents_data,  # Changed this to pass a list of file data
        model_name=model_name,
        chunk_size=chunk_size,
        api_key=api_key_to_use,
        test_case_types=test_case_types_list,
        document_id=multiple_files_document_id,  # this is used as document_id inside celery
    )

    await collection.update_one(
        {"_id": ObjectId(multiple_files_document_id)},
        {"$set": {"last_task_id": task.id}},
    )

    return {
        "message": "✅ Test case generation task started for multiple files.",
        "task_id": task.id,
        "file_ids": file_ids,
        "document_id": multiple_files_document_id,
        "test_case_types": test_case_types_list,
        "api_key_being_used": f"...{api_key_to_use[-5:]}",
        "warning": warning,
    }
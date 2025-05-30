from typing import List, Optional
from fastapi import APIRouter, HTTPException, Form, Query
from fastapi import Depends
from bson import ObjectId
from pathlib import PurePosixPath
import os
from urllib.parse import urlparse

from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_db
from app.core.celery_app import celery_app
from app.tasks.task_with_api_key import process_and_generate_task_multiple
from ...utils.data_ingestion import download_file_from_s3  # Import the S3 download helper

# Constants
VALID_TEST_CASE_TYPES = [
    "functional",
    "non-functional",
    "security",
    "performance",
    "boundary",
    "compliance",
]

router = APIRouter()


@router.post("/generate_test_cases_multiple")
async def generate_test_cases_multiple(
    file_ids: List[str] = Form(...),  # List of file IDs
    model_name: Optional[str] = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form("all"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Generates test cases for multiple files, processing all test case types for one file before moving to the next.
    """

    collection = db["documents"]

    # Validate file_ids and prepare documents_data
    documents_data = []
    for file_id in file_ids:
        try:
            object_id = ObjectId(file_id)
            document = await collection.find_one({"_id": object_id})
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid file_id format: {file_id}. Error: {e}"
            )

        if not document:
            raise HTTPException(
                status_code=404, detail=f"Document not found in the database: {file_id}"
            )

        # Get S3 URL and download file
        s3_url = document.get("s3_url")
        if not s3_url:
            raise HTTPException(
                status_code=400, detail=f"No S3 URL found for document {file_id}"
            )

        try:
            file_path = download_file_from_s3(s3_url)  # Download and get local file path
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to download file from S3: {e}"
            )

        # Extract file name
        file_name = PurePosixPath(urlparse(s3_url).path).name

        documents_data.append(
            {
                "file_id": str(file_id),
                "file_path": file_path,  # Local temp file path
                "file_name": file_name,
            }
        )

    # Parse and validate test_case_types
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

    # API key fallback logic
    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
    warning = (
        "Using default API key. Consider providing your own to avoid shared limits."
        if not api_key
        else None
    )

    # Create a single document ID for tracking the multiple files job
    multiple_files_document_id = str(ObjectId())

    # Insert initial document in MongoDB
    await collection.insert_one(
        {
            "_id": ObjectId(multiple_files_document_id),
            "status": 0,
            "selected_model": model_name,
            "api_key_used": f"...{api_key_to_use[-5:]}",
            "file_ids": file_ids,
            "file_names": [doc["file_name"] for doc in documents_data],
            "test_case_types": test_case_types_list,
            "type": "multiple",
        }
    )

    # Trigger Celery task
    task = process_and_generate_task_multiple.delay(
        file_ids=documents_data,
        model_name=model_name,
        chunk_size=chunk_size,
        api_key=api_key_to_use,
        test_case_types=test_case_types_list,
        document_id=multiple_files_document_id,
    )

    # Update MongoDB with the Celery task ID
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

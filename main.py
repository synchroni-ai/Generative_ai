from fastapi import BackgroundTasks, HTTPException
from tasks import process_and_generate_task
from celery.result import AsyncResult
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Form,
    Query,
    status,
    WebSocket,
)
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from pathlib import Path
import os
import re
import time
import uuid
import pandas as pd
from openpyxl import load_workbook

# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
from core.websocket import websocket_endpoint


mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]


def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# ----------------- Directories Setup -----------------
TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_USER_STORY_PROMPT_FILE_PATH")
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process_and_generate/")
async def process_and_generate(
    file: UploadFile = File(...),
    model_name: str = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
):
    file_name = file.filename
    file_path = Path(INPUT_DIR) / file_name

    # Save the uploaded file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    finally:
        await file.close()

    # Start the Celery task
    task = process_and_generate_task.delay(
        str(file_path), model_name, chunk_size, cache_key
    )

    return {
        "message": "File uploaded successfully. Processing started.",
        "task_id": task.id,
    }


@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    if task.state == "SUCCESS":
        return {"status": "Completed", "result": task.result}
    elif task.state == "FAILURE":
        return {"status": "Failed", "error": str(task.info)}
    else:
        return {"status": task.state}


# ----------------- MongoDB Fetch Endpoints -----------------
@app.get("/documents/")
def get_all_documents():
    documents = list(collection.find())
    return [serialize_document(doc) for doc in documents]


@app.get("/documents/{document_id}")
def get_document_by_id(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return serialize_document(doc)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")


# ----------------- Delete Documents Endpoint -----------------
@app.delete("/delete-documents")
def delete_documents(document_ids: List[str]):
    try:
        for document_id in document_ids:
            doc = collection.find_one({"_id": ObjectId(document_id)})
            if not doc:
                raise HTTPException(
                    status_code=404, detail=f"Document {document_id} not found"
                )

            file_path = doc.get("doc_path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            collection.delete_one({"_id": ObjectId(document_id)})

        return JSONResponse(
            content={"success": f"{len(document_ids)} documents deleted successfully."},
            status_code=status.HTTP_200_OK,
        )
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- Download Excel Endpoints -----------------
@app.get("/download/testcases/{document_id}")
def download_test_cases_excel(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc or "test_case_excel_path" not in doc:
            raise HTTPException(
                status_code=404, detail="Excel file not found for test cases"
            )
        return FileResponse(
            doc["test_case_excel_path"],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=Path(doc["test_case_excel_path"]).name,
        )
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")


@app.get("/download/userstories/{document_id}")
def download_user_stories_excel(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc or "user_story_excel_path" not in doc:
            raise HTTPException(
                status_code=404, detail="Excel file not found for user stories"
            )
        return FileResponse(
            doc["user_story_excel_path"],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=Path(doc["user_story_excel_path"]).name,
        )
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")


@app.websocket("/ws/task_status")
async def websocket_task_status(websocket: WebSocket, task_id: str = Query(...)):
    await websocket_endpoint(websocket, task_id)

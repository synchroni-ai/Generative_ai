


from fastapi import BackgroundTasks, HTTPException, Body # <-- Moved Body here
from task_with_api_key import process_and_generate_task # Ensure this path is correct
from celery.result import AsyncResult
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    # HTTPException, # Already imported
    Form,
    Query,
    status,
    WebSocket,
    APIRouter,
    WebSocketDisconnect,
    Depends
)
from fastapi.responses import JSONResponse, FileResponse
from utils.jwt_auth import (
    create_jwt_token,
)
from pydantic import BaseModel, Field
from pymongo.collection import Collection

from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from pathlib import Path
import os
import re
import asyncio
from starlette.websockets import WebSocketState
from collections import Counter

from fastapi import APIRouter, Query, HTTPException
from bson import ObjectId
from typing import List, Dict, Any

from fastapi.responses import FileResponse
from bson import ObjectId
import os
from pathlib import Path
import csv
import tempfile
# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
from utils.data_ingestion import extract_text_from_file
from task_with_api_key import celery_app, process_and_generate_task
from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

load_dotenv()

# --- Environment Variables ---
ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "guest_user")
ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "Welcome@123")
SECRET_KEY_ENV = os.getenv("SECRET_KEY")
ALGORITHM_ENV = "HS256"
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

# --- Pydantic Models (Defined BEFORE app instance and routers) ---
class DataSpaceCreate(BaseModel): # Used by the old /data-spaces/ endpoint if you keep it
    name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    # category: Optional[str] = Field(None, max_length=50) # If adding here too
    # sub_category: Optional[str] = Field(None, max_length=50)

class DataSpaceResponse(BaseModel):
    data_space_id: str
    name: str
    description: Optional[str]
    category: Optional[str] = None # Add if you want to return it
    sub_category: Optional[str] = None # Add if you want to return it
    created_at: datetime
    document_count: int = 0
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class DocumentMetadataResponse(BaseModel):
    file_id: str
    file_name: str  # This field is required
    status: Optional[int]
    timestamp: datetime
    content_type: Optional[str] = None
    size: Optional[int] = None
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True # Changed from orm_mode = True for Pydantic v2

class UploadedFileDetail(BaseModel):
    file_id: Optional[str] = None
    file_name: str
    status: str
    error: Optional[str] = None
    message: Optional[str] = None

class BatchUploadResponse(BaseModel):
    data_space_id: str
    data_space_name: str
    description: str
    category:str
    sub_category:str
    message:str
    uploaded_files: Dict[str, str] # {original_filename: new_file_id or error_string}
    errors: Optional[List[Dict[str, str]]] = None
    generation_id: Optional[str] = None

class TokenRequest(BaseModel):
    username: str
    password: str

class GenerateTaskResponseItem(BaseModel):
    file_id: str
    document_id:Optional[str] = None
    task_id:Optional[str] = None
    batch_id:str
    message: str
    error: Optional[str] = None

class BatchGenerateTestCasesResponse(BaseModel):
    generation_id:str
    overall_message: str
    tasks_initiated: List[GenerateTaskResponseItem]
    warning: Optional[str] = None

# MOVED Pydantic models for /test-case-batch/results
class TestCaseBatchRequest(BaseModel):
    generation_id: str
    file_ids: List[str]
    types: Optional[List[str]] = None
    download_csv: Optional[bool] = False 

class TestCaseFileResult(BaseModel):
    file_id: str
    file_name: str
    status: Optional[int]
    progress: Optional[List[str]]
    error_info: Optional[str]
    test_cases: Optional[Dict[str, Any]]  # type: Dict[test_case_type, test_case_object]

class TestCaseBatchResultResponse(BaseModel):
    generation_id: str
    requested_file_ids: List[str]
    requested_types: Optional[List[str]]
    results: List[TestCaseFileResult]

# --- MongoDB Setup ---
mongo_client = MongoClient(MONGODB_URL)
db = mongo_client[MONGO_DB_NAME]
documents_collection: Collection = db["test_case_generation"]
data_spaces_collection: Collection = db["data_spaces"]
cost_collection: Collection = db["cost_tracking"]

# --- Serialization, Constants, Directory Setup ---
IST = ZoneInfo("Asia/Kolkata")
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
    Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

VALID_TEST_CASE_TYPES_FROM_USER = [
    "functional", "non-functional", "security", "performance",
    "boundary", "compliance", "all"
]
INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES_FROM_USER if t != "all"]

# --- FastAPI App Instance ---
app = FastAPI(title="GenAI API with Data Spaces (Full Integration - Corrected)")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body

from pymongo import MongoClient

from keybert import KeyBERT

import fitz  # PyMuPDF

import uuid

import base64
 
# app = FastAPI()
 
# MongoDB setup

client = MongoClient("mongodb://localhost:27017")

db = client.document_tags_db

tags_collection = db.tags
 
# 🔁 Endpoint 1: Original multipart/form-data upload
# --- API Routers ---
api_v1_router = APIRouter(prefix="/api/v1")

# --- Data Space Endpoints ---
@api_v1_router.post("/process-document")

async def process_document(file: UploadFile = File(...), filename: str = Form(...)):

    try:

        file_bytes = await file.read()
 
        doc_id = str(uuid.uuid4())

        tags = generate_tags(file_bytes)
 
        document_data = {

            "_id": doc_id,

            "filename": filename,

            "tags": tags

        }

        tags_collection.insert_one(document_data)
 
        return {"document_id": doc_id, "tags": tags}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
 
 
# 🆕 Endpoint 2: Base64 + JSON (Power Automate-friendly)

@api_v1_router.post("/process-document-base64")

async def process_document_base64(payload: dict = Body(...)):

    try:

        file_base64 = payload.get("file_base64")

        filename = payload.get("filename")
 
        if not file_base64 or not filename:

            raise ValueError("Missing 'file_base64' or 'filename' in request body")
 
        file_bytes = base64.b64decode(file_base64)
 
        doc_id = str(uuid.uuid4())

        tags = generate_tags(file_bytes)
 
        document_data = {

            "_id": doc_id,

            "filename": filename,

            "tags": tags

        }

        tags_collection.insert_one(document_data)
 
        return {"document_id": doc_id, "tags": tags}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
 
 
# 📄 Endpoint 3: Retrieve tags by document ID

@api_v1_router.get("/get-tags/{doc_id}")

def get_tags(doc_id: str):

    document = tags_collection.find_one({"_id": doc_id})

    if document:

        return {"filename": document["filename"], "tags": document["tags"]}

    raise HTTPException(status_code=404, detail="Document not found")
 
 
# 🔍 Utility: Extract text from PDF bytes

def extract_text(file_bytes: bytes) -> str:

    doc = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""

    for page in doc:

        text += page.get_text()

    return text
 
 
# 🧠 Utility: Generate tags using KeyBERT

def generate_tags(file_bytes):

    text = extract_text(file_bytes)

    kw_model = KeyBERT()

    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')

    return [kw[0] for kw in keywords[:5]]

@api_v1_router.post(
    "/data-spaces/create-and-upload/",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Data Spaces & Documents"],
    summary="Create Data Space with category/sub-category & Upload Documents"
)
async def create_dataspace_and_upload_documents(
    data_space_name: str = Form(..., min_length=3, max_length=100, description="Name for the new Data Space."),
    data_space_description: Optional[str] = Form(None, max_length=500, description="Optional description for the Data Space."),
    category: str = Form(..., min_length=1, max_length=50, description="Category for the Data Space."),
    sub_category: Optional[str] = Form(None, max_length=50, description="Sub-category for the Data Space."),
    files: List[UploadFile] = File(..., description="Documents to upload to the new Data Space."),
    # Using Depends to simulate how your global collections might be accessed
    # In your full app, you might access global `data_spaces_collection` directly
    # or have a more sophisticated dependency injection system.
    current_data_spaces_collection: Collection = Depends(lambda: data_spaces_collection),
    current_documents_collection: Collection = Depends(lambda: documents_collection)
):
    if current_data_spaces_collection.find_one({"name": data_space_name}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space with name '{data_space_name}' already exists.")

    now = datetime.now(IST)
    ds_doc_data = {
        "name": data_space_name,
        "description": data_space_description,
        "category": category,
        "sub_category": sub_category,
        "created_at": now,
        "updated_at": now,
        "document_ids": [],
        "generation_id": None  # <-- RENAMED AND INITIALIZED TO NULL
    }
    insert_ds_result = current_data_spaces_collection.insert_one(ds_doc_data)
    new_data_space_id_obj = insert_ds_result.inserted_id
    new_data_space_id_str = str(new_data_space_id_obj)

    if not files:
        return BatchUploadResponse(
            data_space_id=new_data_space_id_str,
            data_space_name=data_space_name,
            description=data_space_description,
            category=category,
            sub_category=sub_category,
            message="Data Space created. No files provided for upload.",
            uploaded_files={},
            errors=None,
            generation_id=None  # <-- RENAMED & INCLUDE IN RESPONSE
        )

    uploaded_files_map: Dict[str, str] = {}
    successfully_uploaded_doc_object_ids: List[ObjectId] = []
    individual_file_errors: List[Dict[str,str]] = []

    for file in files:
        original_filename = file.filename
        base, ext = os.path.splitext(original_filename)
        sanitized_base = re.sub(r'[^\w\s\.-]', '_', base).replace(" ", "_")
        unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
        file_path_on_disk = Path(INPUT_DIR) / unique_filename_on_disk
        try:
            with open(file_path_on_disk, "wb") as f:
                f.write(await file.read())
            file_size = file_path_on_disk.stat().st_size
            doc_meta = {
                "data_space_id": new_data_space_id_obj,
                "file_name": original_filename,
                "file_path": str(file_path_on_disk),
                "content_type": file.content_type,
                "size": file_size,
                "status": -1,
                "timestamp": now,
                "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
                "last_task_id": None, "requested_test_case_types": []
            }
            insert_doc_res = current_documents_collection.insert_one(doc_meta)
            new_doc_obj_id = insert_doc_res.inserted_id
            uploaded_files_map[original_filename] = str(new_doc_obj_id)
            successfully_uploaded_doc_object_ids.append(new_doc_obj_id)
        except Exception as e:
            print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
            individual_file_errors.append({"filename": original_filename, "error": str(e)})
            uploaded_files_map[original_filename] = f"ERROR: {str(e)}"
            if os.path.exists(file_path_on_disk) and original_filename not in [
                k for k,v in uploaded_files_map.items() if "ERROR" not in v
            ]:
                 try: os.remove(file_path_on_disk)
                 except Exception as e_del: print(f"Cleanup err for {file_path_on_disk}: {e_del}")
        finally:
            await file.close()

    if successfully_uploaded_doc_object_ids:
        current_data_spaces_collection.update_one(
            {"_id": new_data_space_id_obj},
            {"$set": {"document_ids": successfully_uploaded_doc_object_ids, "updated_at": datetime.now(IST)}}
        )
    elif files:
         current_data_spaces_collection.update_one(
             {"_id": new_data_space_id_obj},
             {"$set": {"updated_at": datetime.now(IST)}}
         )

    msg = f"Data Space '{data_space_name}' (Category: {category}, Sub-Category: {sub_category or 'N/A'}) created. "
    msg += f"{len(successfully_uploaded_doc_object_ids)} of {len(files)} files successfully uploaded and linked."
    if individual_file_errors:
        msg += " Some files encountered errors."

    return BatchUploadResponse(
        data_space_id=new_data_space_id_str,
        data_space_name=data_space_name,
        description=data_space_description,
        category=category,
        sub_category=sub_category,
        message=msg,
        uploaded_files=uploaded_files_map,
        errors=individual_file_errors if individual_file_errors else None,
        generation_id=None  # <-- RENAMED & INCLUDE IN RESPONSE
    )



@api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
async def list_data_spaces(skip: int = 0, limit: int = 20):
    spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
    data_spaces_list = [] # Renamed for clarity to avoid conflict with global data_spaces_collection
    for ds_doc in spaces_cursor:
        ds_id_obj = ds_doc["_id"] # This is an ObjectId

        # --- MODIFIED COUNTING LOGIC ---
        # Count only actual documents, excluding batch generation meta-documents.
        # Actual documents have a "file_name" and are NOT marked as "is_test_case_generation_batch".
        # Or, more simply, exclude those marked as batch generation documents.
        query_for_doc_count = {
            "data_space_id": ds_id_obj, # Match by ObjectId primarily
            "is_test_case_generation_batch": {"$ne": True} # Exclude documents that are batch markers
            # Optionally, you could also add: "file_name": {"$exists": True}
            # if all true documents are guaranteed to have a file_name.
        }
        
        # Your original query also checked for string version of ds_id.
        # If data_space_id in documents_collection could *sometimes* be a string (though upload uses ObjectId),
        # then the $in query was safer. But if it's always ObjectId, the simpler query is fine.
        # Let's use a robust query that handles both ObjectId and string, and excludes batch docs.
        robust_query_for_doc_count = {
            "$or": [
                {"data_space_id": ds_id_obj},
                {"data_space_id": str(ds_id_obj)} # If some legacy data might have string IDs
            ],
            "is_test_case_generation_batch": {"$ne": True}
        }
        # However, since your current create_dataspace_and_upload_documents stores ds_id_obj (ObjectId)
        # in the "data_space_id" field of document_meta, matching directly by ds_id_obj should be sufficient
        # for documents created by that endpoint. The batch generation also uses ds_obj_id.
        # So, the simpler query_for_doc_count should be fine if data is consistent.
        # Let's stick to the simpler one assuming consistent ObjectId storage for data_space_id in documents_collection.

        doc_count = documents_collection.count_documents(query_for_doc_count)
        # --- END MODIFIED COUNTING LOGIC ---

        data_spaces_list.append(
            DataSpaceResponse(
                data_space_id=str(ds_id_obj), # Use ds_id_obj here
                name=ds_doc.get("name"),
                description=ds_doc.get("description"),
                category=ds_doc.get("category"),
                sub_category=ds_doc.get("sub_category"),
                created_at=ds_doc.get("created_at"),
                document_count=doc_count
            )
        )
    return data_spaces_list




@api_v1_router.get("/documents/generation-status/", tags=["Document Test Cases"])
async def get_test_case_generation_status(
    data_space_id: str = Query(..., description="Data Space ID")
):
    # Step 1: Validate and convert data_space_id
    try:
        ds_obj_id = ObjectId(data_space_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid data_space_id.")

    # Step 2: Fetch the data space
    data_space = data_spaces_collection.find_one({"_id": ds_obj_id})
    if not data_space:
        raise HTTPException(status_code=404, detail="Data space not found.")

    generation_id = data_space.get("generation_id")
    if not generation_id:
        return {
            "status": -1,
            "message": "No test case generation initiated for this data space."
        }

    # Step 3: Ensure generation_id is an ObjectId
    try:
        gen_obj_id = ObjectId(generation_id) if isinstance(generation_id, str) else generation_id
    except Exception:
        raise HTTPException(status_code=500, detail="Stored generation_id is invalid.")

    # Step 4: Fetch the generation document
    generation_doc = documents_collection.find_one({
        "_id": gen_obj_id,
        "is_test_case_generation_batch": True
    })
    if not generation_doc:
        raise HTTPException(status_code=404, detail="Generation document not found.")

    # Step 5: Safely serialize the files list
    serialized_files = []
    for file in generation_doc.get("files", []):
        serialized_files.append({
            "batch_id": str(file.get("batch_id")),
            "file_id": str(file.get("file_id")),
            "file_name": file.get("file_name"),
            "status": file.get("status"),
            "error_info": file.get("error_info"),
            "last_task_id": file.get("last_task_id"),
            "test_cases": file.get("test_cases", {})
        })

    # Step 6: Return the response
    return {
        "generation_id": str(generation_doc["_id"]),
        "status": generation_doc.get("status", -1),
        "progress": generation_doc.get("progress", []),
        "files": serialized_files
    }


@api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
    try:
        ds_obj_id = ObjectId(data_space_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")

    if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")

    # Modify the query to exclude batch generation documents
    # We assume actual documents do NOT have 'is_test_case_generation_batch: True'
    # or that they have a 'file_name' field.
    # A more robust way is to ensure batch documents are distinguished.
    # Option 1: Filter out documents that are marked as batch generations
    query_filter = {
        "data_space_id": ds_obj_id,
        "is_test_case_generation_batch": {"$ne": True} # Exclude if this field is True
        # Alternatively, or in addition, ensure 'file_name' exists for actual documents:
        # "file_name": {"$exists": True}
    }

    docs_cursor = documents_collection.find(query_filter).sort("timestamp", -1).skip(skip).limit(limit)

    response_list = []
    for doc in docs_cursor:
        # Double-check if file_name is present, just in case, though the query should handle it.
        if "file_name" in doc:
            try:
                # Construct the Pydantic model.
                # If you use `from_attributes = True` (Pydantic v2) or `orm_mode = True` (Pydantic v1)
                # and your Pydantic model fields match the DB fields, you can often do:
                # response_list.append(DocumentMetadataResponse.model_validate(doc)) # For Pydantic v2
                # response_list.append(DocumentMetadataResponse.from_orm(doc)) # For Pydantic v1
                # However, your current explicit construction is fine too if file_id needs casting.

                # Your current way:
                response_list.append(DocumentMetadataResponse(
                    file_id=str(doc["_id"]),
                    file_name=doc["file_name"], # Explicitly pass required fields
                    status=doc.get("status"),
                    timestamp=doc["timestamp"], # Ensure timestamp is always present or handle None
                    content_type=doc.get("content_type"),
                    size=doc.get("size")
                ))
            except KeyError as e:
                print(f"Warning: Document {doc['_id']} is missing a required field for DocumentMetadataResponse: {e}")
                # Optionally skip this document or handle the error
            except Exception as e_pydantic:
                print(f"Pydantic validation error for document {doc['_id']}: {e_pydantic}")
                # Optionally skip or handle
        else:
            # This case should ideally be caught by the query filter
            print(f"Warning: Document {doc['_id']} was fetched but is missing 'file_name'. Skipping.")

    return response_list


@api_v1_router.delete("/data-spaces/{data_space_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Data Spaces"])
async def delete_data_space(data_space_id: str, delete_contained_documents: bool = Query(False)):
    try: ds_obj_id = ObjectId(data_space_id)
    except InvalidId: raise HTTPException(status_code=400, detail="Invalid Data Space ID.")
    if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
        raise HTTPException(status_code=404, detail="Data Space not found.")
    if delete_contained_documents:
        docs_to_del_cursor = documents_collection.find({"data_space_id": ds_obj_id}, {"_id": 1, "file_path": 1})
        for doc in docs_to_del_cursor:
            if doc.get("file_path") and os.path.exists(doc["file_path"]):
                try: os.remove(doc["file_path"])
                except Exception as e: print(f"ERR DEL FILE {doc['file_path']}: {e}")
            if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'): # Ensure CSV_OUTPUT_DIR is defined in utils
                csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{str(doc['_id'])}_test_cases.csv")
                if os.path.exists(csv_p):
                    try: os.remove(csv_p)
                    except Exception as e: print(f"ERR DEL CSV {csv_p}: {e}")
        documents_collection.delete_many({"data_space_id": ds_obj_id})
    result = data_spaces_collection.delete_one({"_id": ds_obj_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Data Space found but failed to delete.")

# --- Document Test Case Operations ---
@api_v1_router.post("/documents/batch-generate-test-cases/", response_model=BatchGenerateTestCasesResponse, tags=["Document Test Cases"])
async def batch_generate_test_cases_for_documents(
    data_space_id: str = Form(..., description="Data Space ID"),
    model_name: Optional[str] = Form("Openai"),
    chunk_size: Optional[int] = Form(None),
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form(None)
    # Assuming data_spaces_collection and documents_collection are accessible
    # (e.g., global or injected). For this snippet, let's make it explicit if needed,
    # or assume they are globally available as in your full main3.py.
    # If they are global, you don't need these Depends here.
    # current_data_spaces_collection: Collection = Depends(lambda: data_spaces_collection),
    # current_documents_collection: Collection = Depends(lambda: documents_collection)
):
    from bson import ObjectId
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from pathlib import Path

    # These would ideally be initialized once globally or passed via Depends
    # For the snippet, ensure they are in scope.
    # IST = ZoneInfo("Asia/Kolkata")
    # data_spaces_collection = ...
    # documents_collection = ...


    now = datetime.now(IST) # Ensure IST is defined

    VALID_TYPES = ["functional", "non-functional", "security", "performance", "boundary", "compliance"]
    types_for_resp = VALID_TYPES if (not test_case_types or test_case_types.lower() == "all") else [
        t.strip().lower() for t in test_case_types.split(",") if t.strip().lower() in VALID_TYPES
    ]
    if not types_for_resp:
        raise HTTPException(status_code=400, detail=f"No valid test_case_types provided. Valid types are: {', '.join(VALID_TYPES)} or 'all'.")

    try:
        ds_obj_id = ObjectId(data_space_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid data_space_id.")

    # Use the collection directly if it's global, or the injected one
    # For this snippet, let's assume global `data_spaces_collection` and `documents_collection`
    # are in scope from your main3.py.
    data_space = data_spaces_collection.find_one({"_id": ds_obj_id})
    if not data_space:
        raise HTTPException(status_code=404, detail="Data space not found.")

    document_ids_from_ds = data_space.get("document_ids", [])
    if not document_ids_from_ds:
        raise HTTPException(status_code=400, detail="No documents in data space to process.")

    files_embedded = []
    file_objs = []
    for doc_id_obj in document_ids_from_ds:
        doc = documents_collection.find_one({"_id": doc_id_obj})
        if doc and doc.get("file_path") and Path(doc.get("file_path", "")).exists():
            batch_file_specific_id = ObjectId()
            files_embedded.append({
                "batch_id": batch_file_specific_id,
                "file_id": doc["_id"],
                "file_name": doc.get("file_name"),
                "status": 0,
                "test_cases": {},
                "progress": ["Task initiated for batch generation."],
                "error_info": None,
                "last_task_id": None
            })
            file_objs.append({"doc": doc, "batch_file_specific_id": batch_file_specific_id})
        elif doc:
             print(f"Skipping document {str(doc_id_obj)}: file_path '{doc.get('file_path')}' missing or invalid.")
        else:
             print(f"Skipping document ID {str(doc_id_obj)}: document not found in documents_collection.")

    if not files_embedded:
        raise HTTPException(status_code=400, detail="No valid and accessible files found in the data space to process.")

    batch_doc_payload = {
        "data_space_id": ds_obj_id, # Link back to the data space
        "timestamp": now,
        "model_used": model_name,
        "requested_test_case_types": types_for_resp,
        "status": 0,
        "progress": ["Test case batch generation process initiated."],
        "files": files_embedded,
        "is_test_case_generation_batch": True
    }
    insert_result = documents_collection.insert_one(batch_doc_payload)
    generation_id_obj = insert_result.inserted_id  # This is the ObjectId
    generation_id_str = str(generation_id_obj)     # This is the string for the response

    # --- MODIFICATION: Update Data Space with this generation_id ---
    data_spaces_collection.update_one(
        {"_id": ds_obj_id},  # ds_obj_id is the ObjectId of the data space
        {"$set": {
            "generation_id": generation_id_obj, # Store the ObjectId in the 'generation_id' field
            "updated_at": datetime.now(IST)     # Also update the timestamp of the data space
            }
        }
    )
    # --- END MODIFICATION ---

    from task_with_api_key import process_and_generate_task # Ensure this import is correct
    initiated_tasks_info: List[GenerateTaskResponseItem] = []

    for item in file_objs:
        doc = item["doc"]
        batch_file_specific_id = item["batch_file_specific_id"]
        actual_file_id_str = str(doc["_id"])
        try:
            task = process_and_generate_task.apply_async(args=[
                doc["file_path"],
                model_name,
                chunk_size,
                api_key or os.getenv("TOGETHER_API_KEY"),
                ",".join(types_for_resp),
                generation_id_str, # Pass string ID to Celery task
                actual_file_id_str,
                str(batch_file_specific_id)
            ])
            documents_collection.update_one(
                {"_id": generation_id_obj, "files.batch_id": batch_file_specific_id}, # Query with ObjectId
                {"$set": {"files.$.last_task_id": task.id, "files.$.status": 0}}
            )
            initiated_tasks_info.append(GenerateTaskResponseItem(
                file_id=actual_file_id_str,
                document_id=actual_file_id_str,
                batch_id=str(batch_file_specific_id),
                task_id=task.id,
                message="✅ TC gen task started.",
                error=None
            ))
        except Exception as e:
            print(f"Error initiating Celery task for file {actual_file_id_str}: {e}")
            documents_collection.update_one(
                {"_id": generation_id_obj, "files.batch_id": batch_file_specific_id}, # Query with ObjectId
                {"$set": {"files.$.status": 2, "files.$.error_info": f"Failed to start Celery task: {str(e)}"}}
            )
            initiated_tasks_info.append(GenerateTaskResponseItem(
                file_id=actual_file_id_str,
                document_id=actual_file_id_str,
                batch_id=str(batch_file_specific_id),
                task_id=None,
                message="Failed to start Celery task.",
                error=str(e)
            ))

    success_count = sum(1 for item in initiated_tasks_info if item.task_id)
    # overall_batch_status = 0 # This variable is not used after this point, can be removed
    if success_count == 0 and len(file_objs) > 0:
        documents_collection.update_one(
            {"_id": generation_id_obj}, # Query with ObjectId
            {"$set": {"status": 2, "progress": batch_doc_payload["progress"] + ["All tasks failed to initiate."] }}
        )
    elif success_count < len(file_objs):
         documents_collection.update_one(
            {"_id": generation_id_obj}, # Query with ObjectId
            {"$push": {"progress": f"{success_count}/{len(file_objs)} tasks initiated. Some failed."}}
        )
    else: # All tasks initiated successfully
        documents_collection.update_one(
            {"_id": generation_id_obj}, # Query with ObjectId
            {"$push": {"progress": f"All {success_count}/{len(file_objs)} tasks successfully initiated."}}
        )

    return BatchGenerateTestCasesResponse(
        generation_id=generation_id_str, # Return string representation of the ID
        overall_message=f"Batch process initiation done. {success_count}/{len(file_objs)} tasks started.",
        tasks_initiated=initiated_tasks_info,
        warning=None if api_key or not os.getenv("TOGETHER_API_KEY") else "Using default API key."
    )
@api_v1_router.get("/documents/{file_id}/get-test-cases/", tags=["Document Test Cases"])
async def get_test_cases_as_json_filtered_and_counted(
    file_id: str, 
    types: Optional[str] = Query(None, description="Comma-separated types (e.g., functional,security) or 'all'. Omit for all types.")
):
    # ... (ObjectId conversion, doc fetching, base_res, empty_tc_res, status checks ... all same as before)
    try: doc_obj_id = ObjectId(file_id)
    except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
    doc = documents_collection.find_one({"_id": doc_obj_id})
    if not doc: raise HTTPException(status_code=404, detail="Document not found.")
    status_val = doc.get("status")
    base_res = {
        "file_id": file_id,
        "data_space_id": str(doc.get("data_space_id")) if doc.get("data_space_id") else None,
        "file_name": doc.get("file_name"),
        "req_gen_types": doc.get("requested_test_case_types", [])
    }
    empty_tc_res = {"test_cases": [], "counts_by_type": {}, "total_test_cases": 0}

    if status_val == -1: return {**base_res, **empty_tc_res, "status_code": -1, "status_message": "pending_gen", "detail": "Generation not started."}
    if status_val == 0:
        prog = doc.get("progress", [])
        return {**base_res, **empty_tc_res, "status_code": 0, "status_message": "processing", "detail": prog[-1] if prog else "Processing...", "progress_log": prog}
    if status_val == 2: return {**base_res, **empty_tc_res, "status_code": 2, "status_message": "error", "detail": f"Failed: {doc.get('error_info', 'Unknown error')}"}
    
    if status_val == 1: # Completed
        db_test_cases_structured = doc.get("test_cases")
        if not db_test_cases_structured or not isinstance(db_test_cases_structured, dict) or not any(val.get("content") for val in db_test_cases_structured.values() if isinstance(val, dict)):
            return {**base_res, **empty_tc_res, "status_code": 1, "status_message": "completed_no_data_on_record", "detail": "TCs field on doc record empty/not structured or content missing."}

        all_parsed_tcs = []
        for tc_type, type_data in db_test_cases_structured.items():
            if isinstance(type_data, dict) and "content" in type_data and type_data["content"]:
                parsed_from_content_str = parse_test_cases_from_content_string(type_data["content"])
                for case_item_dict in parsed_from_content_str:
                    case_item_dict["Test type"] = tc_type
                    all_parsed_tcs.append(case_item_dict)
        
        if not all_parsed_tcs:
            return {**base_res, **empty_tc_res, "status_code": 1, "status_message": "completed_parsing_yielded_empty", "detail": "Structured TCs found, but parsing content strings yielded no valid TCs."}

        final_list_to_return = all_parsed_tcs
        applied_filter_names_display = "All" # Default if no specific types filter
        
        # MODIFICATION FOR EXPLICIT 'types' PARAMETER HANDLING
        apply_type_filter = False
        req_filter_types_lower = []

        if types and types.strip().lower() != "all":
            apply_type_filter = True
            req_filter_types_lower = [t.strip().lower() for t in types.split(',') if t.strip()]
            applied_filter_names_display = ", ".join(sorted(list(set(req_filter_types_lower)))) # Show what was actually filtered
            if not req_filter_types_lower: # e.g. types was just "," or empty after strip
                apply_type_filter = False 
                applied_filter_names_display = "All (invalid type filter provided)"


        if apply_type_filter:
            final_list_to_return = [tc for tc in all_parsed_tcs if tc.get("Test type", "").lower() in req_filter_types_lower]
        
        counts_by_type_final = Counter(tc.get("Test type", "Not Specified") for tc in final_list_to_return)
        total_tcs_final = len(final_list_to_return)
        
        detail_msg_final = "Test cases retrieved."
        if apply_type_filter and not final_list_to_return: 
            detail_msg_final = f"No TCs matching filters: {applied_filter_names_display}"
        elif apply_type_filter: 
            detail_msg_final = f"Filtered by types: {applied_filter_names_display}"

        return {
            **base_res, "status_code": 1, 
            "status_message": "completed_ok" if total_tcs_final > 0 else ("completed_no_match_after_filter" if apply_type_filter else "completed_ok_empty_result"),
            "detail": detail_msg_final, 
            "filter_applied_types_str": types if types else "all (default)", # Show original types string
            "test_cases": final_list_to_return, 
            "counts_by_type": dict(counts_by_type_final), 
            "total_test_cases": total_tcs_final
        }
    return {**base_res, **empty_tc_res, "status_code": status_val or "unknown", "status_message": "unknown_status", "detail": f"Unexpected status: {status_val}"}

@api_v1_router.get("/documents/{file_id}/test-case-summary/", tags=["Document Test Cases"])

async def get_batch_test_case_summary(file_id: str):
    try:
        obj_file_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id.")

    # Find the batch doc that contains this file
    batch = documents_collection.find_one({
        "is_test_case_generation_batch": True,
        "files.file_id": obj_file_id
    })

    if not batch:
        raise HTTPException(status_code=404, detail="No batch found for this file.")

    # Find the specific file entry inside the batch
    file_entry = None
    for f in batch["files"]:
        # f["file_id"] could be ObjectId or string, so convert both to string
        if str(f["file_id"]) == file_id:
            file_entry = f
            break

    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found in batch.")

    if file_entry.get("status") != 1:
        raise HTTPException(status_code=409, detail=f"Summary not available. Status: {file_entry.get('status')}")

    tc_dict = file_entry.get("test_cases", {})
    counts_by_type = {}
    total = 0

    # Each value in tc_dict should be a dict with a "content" field (multiline string).
    for tc_type, tc_obj in tc_dict.items():
        content = tc_obj.get("content", "")
        # Split by "---\n" to count test cases; you may need to adjust this based on your formatting
        cases = [x for x in content.split("---") if x.strip()]
        counts_by_type[tc_type] = len(cases)
        total += len(cases)

    return {
        "file_id": file_id,
        "file_name": file_entry.get("file_name"),
        "counts_by_type": counts_by_type,
        "total_test_cases": total
    }
@api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
async def download_test_cases_csv_for_document(file_id: str):
    try:
        doc_obj_id = ObjectId(file_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid file_id.")

    doc = documents_collection.find_one({"_id": doc_obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Doc not found.")
    if doc.get("status") != 1:
        raise HTTPException(status_code=409, detail="CSV not ready. Document processing not complete or failed.")

    fname = doc.get("file_name", "doc.pdf")

    try:
        # This function should create the CSV if not exists or outdated, and return path
        csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
    except Exception as e_parse_csv:
        print(f"Error generating CSV for {file_id}: {e_parse_csv}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV file: {str(e_parse_csv)}")

    if not os.path.exists(csv_p):
        raise HTTPException(status_code=404, detail="CSV file missing post-parse attempt. Generation might have failed.")

    return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")


def split_test_cases(content):
    """
    Split a big test cases content block into individual cases.
    Splits on --- or the start of a new TCID.
    """
    # Normalize line endings and strip
    content = content.replace('\r\n', '\n').strip()
    # Remove initial "Test Cases:" label if present
    content = re.sub(r"^#+\s*Test Cases:\s*", "", content, flags=re.IGNORECASE)
    # Split on --- or lines starting with (**)TCID
    split_regex = r'(?:^|\n)(?:-{3,}|(?:\*\*)?TCID\s*[:：])'
    parts = re.split(split_regex, content)
    # Each part may be a header, drop if too short or not a real test case
    cases = []
    for p in parts:
        chunk = p.strip()
        if not chunk:
            continue
        # Add back the TCID line for parsing
        if not chunk.startswith("TCID"):
            chunk = "TCID: " + chunk
        cases.append(chunk)
    return cases

def parse_test_case_block(case_str):
    """
    Parse a single test case string into a dictionary of fields.
    Supports both "**Field:**" and "Field:" style, both with and without bold, and flexible order.
    """
    fields = [
        'TCID', 'Test type', 'Title', 'Description', 'Precondition', 'Steps',
        'Action', 'Data', 'Result', 'Test Nature', 'Test priority'
    ]
    result = {f: '' for f in fields}
    for f in fields:
        # Match **Field:** value OR Field: value (with optional bold)
        # Uses lookahead to stop at the next field or end of string
        pattern = rf'(?:\*\*)?{re.escape(f)}(?:\*\*)?\s*[:：]\s*(.*?)(?=(?:\n(?:\*\*)?[A-Za-z ]+(?:\*\*)?\s*[:：])|\Z)'
        match = re.search(pattern, case_str, flags=re.DOTALL | re.IGNORECASE)
        if match:
            value = match.group(1).strip().replace('\n', ' ')
            result[f] = value
    return result

@api_v1_router.get("/download-csv/{file_id}", tags=["Document Test Cases"])
async def download_test_cases_csv_for_document(file_id: str):
    try:
        doc_obj_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id.")

    doc = documents_collection.find_one({"_id": doc_obj_id})

    # Batch document
    if not doc or doc.get("status", -1) != 1 or not doc.get("test_cases"):
        batch = documents_collection.find_one({
            "is_test_case_generation_batch": True,
            "files.file_id": doc_obj_id
        })
        if not batch:
            raise HTTPException(status_code=404, detail="No test case results found for this document.")

        file_entry = None
        for f in batch["files"]:
            if str(f["file_id"]) == file_id or str(f["file_id"]) == str(doc_obj_id):
                file_entry = f
                break
        if not file_entry:
            raise HTTPException(status_code=404, detail="File not found in batch.")
        if file_entry.get("status", -1) != 1:
            raise HTTPException(status_code=409, detail="CSV not ready. Document processing not complete or failed (batch mode).")

        tc_dict = file_entry.get("test_cases", {})
        all_rows = []
        for tc_type, tc_obj in tc_dict.items():
            content = tc_obj.get("content", "")
            cases = split_test_cases(content)
            for case in cases:
                case_fields = parse_test_case_block(case)
                case_fields["Test type"] = tc_type  # Always override to guarantee
                all_rows.append(case_fields)
        if not all_rows:
            raise HTTPException(status_code=404, detail="No test cases found to export.")

        headers = [
            'Test type', 'TCID', 'Title', 'Description', 'Precondition', 'Steps',
            'Action', 'Data', 'Result', 'Test Nature', 'Test priority'
        ]
        with tempfile.NamedTemporaryFile("w+", newline='', delete=False, suffix=".csv") as tmp_csv:
            writer = csv.DictWriter(tmp_csv, fieldnames=headers)
            writer.writeheader()
            for row in all_rows:
                writer.writerow(row)
            tmp_csv_path = tmp_csv.name

        filename = file_entry.get("file_name", "testcases") + "_test_cases.csv"
        return FileResponse(tmp_csv_path, media_type="text/csv", filename=filename)

    # === OLD DIRECT DOCUMENT MODE ===
    if doc.get("status") != 1:
        raise HTTPException(status_code=409, detail="CSV not ready. Document processing not complete or failed.")

    fname = doc.get("file_name", "doc.pdf")
    db_test_cases = doc.get("test_cases")
    all_rows = []
    if isinstance(db_test_cases, dict):
        for tc_type, cases in db_test_cases.items():
            if isinstance(cases, list):
                for c in cases:
                    c['Test type'] = tc_type
                    all_rows.append(c)
            elif isinstance(cases, dict):
                content = cases.get("content", "")
                for case in split_test_cases(content):
                    case_fields = parse_test_case_block(case)
                    case_fields["Test type"] = tc_type
                    all_rows.append(case_fields)
    elif isinstance(db_test_cases, list):
        for c in db_test_cases:
            all_rows.append(c)

    if not all_rows:
        raise HTTPException(status_code=404, detail="No test cases found to export.")

    headers = [
        'Test type', 'TCID', 'Title', 'Description', 'Precondition', 'Steps',
        'Action', 'Data', 'Result', 'Test Nature', 'Test priority'
    ]
    with tempfile.NamedTemporaryFile("w+", newline='', delete=False, suffix=".csv") as tmp_csv:
        writer = csv.DictWriter(tmp_csv, fieldnames=headers)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
        tmp_csv_path = tmp_csv.name

    return FileResponse(tmp_csv_path, media_type="text/csv", filename=f"{fname.rsplit('.', 1)[0]}_test_cases.csv")




from fastapi import APIRouter, Query, HTTPException, status # Added status
from fastapi.responses import StreamingResponse # FileResponse might not be needed if always streaming
from typing import List, Optional # Already in your main file likely
from io import StringIO, BytesIO
import csv
import zipfile
from bson import ObjectId # Already in your main file likely
import io # Already imported, but good to note
import re

def parse_test_cases_from_content_string(content: str):
    if not content or not content.strip():
        return []

    content = content.replace('\r\n', '\n').strip()
    individual_case_blocks = re.split(r'\n\s*-{3,}\s*\n|(?=\n(?:[\n\s]*)(?:\*\*)?TCID\s*[:：])', content)

    parsed_cases = []
    expected_fields = [
        'TCID', 'Test type', 'Title', 'Description', 'Precondition', 'Steps',
        'Action', 'Data', 'Result', 'Test Nature', 'Test priority'
    ]
    next_field_lookahead_pattern = r"|".join([rf"(?:\*\*)?{re.escape(f)}(?:\*\*)?\s*[:：]" for f in expected_fields])

    for block_idx, block in enumerate(individual_case_blocks):
        block = block.strip()
        if not block:
            continue

        case_data = {field: '' for field in expected_fields}
        current_text_to_parse = block 

        for field_name in expected_fields:
            pattern = rf'(?:\*\*)?{re.escape(field_name)}(?:\*\*)?\s*[:：]\s*(.*?)(?=(?:\n\s*(?:{next_field_lookahead_pattern}))|\Z)'
            match = re.search(pattern, current_text_to_parse, re.DOTALL | re.IGNORECASE)
            
            if match:
                value = match.group(1).strip()
                cleaned_value = value

                # General stripping (from previous attempt)
                while True:
                    original_len = len(cleaned_value)
                    if cleaned_value.startswith("**") and cleaned_value.endswith("**") and len(cleaned_value) >= 4:
                        cleaned_value = cleaned_value[2:-2].strip()
                    elif cleaned_value.startswith("*") and cleaned_value.endswith("*") and len(cleaned_value) >= 2:
                        cleaned_value = cleaned_value[1:-1].strip()
                    if len(cleaned_value) == original_len:
                        break
                
                cleaned_value = re.sub(r"^\s*(\*\*|\*)\s+", "", cleaned_value).strip()
                cleaned_value = re.sub(r"\s+(\*\*|\*)\s*$", "", cleaned_value).strip()

                # ---- NEW SPECIFIC FIX for "CODE** TEXT" pattern ----
                if field_name in ['TCID', 'Title', 'Description']: # Apply to relevant fields
                    # Look for pattern like "ANYTHING_WITHOUT_SPACE_OR_ASTERISK" followed by "**" and then text
                    # This is very specific to the FTC_001** User Registration pattern
                    specific_pattern_match = re.match(r'^([A-Za-z0-9_/-]+)\s*\*\*(.*)$', cleaned_value)
                    if specific_pattern_match:
                        # If it matches, take the first group (code) and the second group (text after **)
                        # and join them with a space, effectively removing the "** "
                        cleaned_value = f"{specific_pattern_match.group(1)} {specific_pattern_match.group(2).strip()}"
                    
                    # Additional check if the value *itself* still starts with **, remove it from the beginning of the text part
                    # (e.g. if the original was FTC_001**** Text -> FTC_001 ** Text -> FTC_001 Text)
                    if cleaned_value.startswith("**"): # If after the above, it *still* starts with **
                        cleaned_value = cleaned_value[2:].strip()

                # ---- END NEW SPECIFIC FIX ----

                case_data[field_name] = cleaned_value.replace('\n', ' ')
            
        if case_data['TCID'] or case_data['Title']:
            parsed_cases.append(case_data)
            
    return parsed_cases

def get_case_insensitive_from_dict(data_dict: Dict, target_key: str):
    """
    Searches a dictionary for a key case-insensitively.
    Returns the original key (with its casing) and its value if found, else (None, None).
    """
    target_key_lower = target_key.lower()
    for original_key, value in data_dict.items():
        if original_key.lower() == target_key_lower:
            return original_key, value
    return None, None


@api_v1_router.get("/documents/download-testcases", tags=["Document Test Cases"], summary="Download test cases for multiple files and types as CSV or ZIP")
async def download_testcases(
    file_ids: str = Query(..., description="Comma-separated string of original document file_ids."),
    types: str = Query(..., description="Comma-separated test case types (e.g., functional,security). Case-insensitive."),
    mode: str = Query("zip", enum=["zip", "csv"], description="'zip' for multiple files/types, 'csv' for single file output (if only one file_id requested).")
):
    # --- Input Validation and Preparation ---
    file_id_str_list = [f_id.strip() for f_id in file_ids.split(',') if f_id.strip()]
    if not file_id_str_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")

    requested_types_lower = [t.strip().lower() for t in types.split(',') if t.strip()]
    if not requested_types_lower:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No test case types provided.")

    try:
        object_id_list = [ObjectId(f_id) for f_id in file_id_str_list]
    except Exception: # InvalidId can also be raised here
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more file_ids are invalid.")

    # --- Data Fetching ---
    # Find the batch document(s) that contain these files.
    # A single file_id might exist in multiple batch runs, but usually, we'd target a specific batch.
    # For simplicity, let's assume we find the latest batch or any batch containing these.
    # This query finds any batch doc that has at least one of the requested file_ids in its 'files' array.
    # It might be better to require a generation_id if files can be in multiple batches.
    batch_cursor = documents_collection.find({
        "is_test_case_generation_batch": True,
        "files.file_id": {"$in": object_id_list}
    }).sort("timestamp", -1) # Get the most recent batch first if multiple exist

    # We need to aggregate data from potentially multiple batch documents if files are spread out,
    # or assume all requested files are in ONE batch document.
    # For now, let's process the first batch found that contains relevant files.
    
    processed_file_entries = {} # Store as {file_id_str: file_entry_from_batch} to avoid duplicates

    for batch_doc in batch_cursor:
        batch_files_array = batch_doc.get("files", [])
        for file_entry_in_batch in batch_files_array:
            file_id_in_entry_obj = file_entry_in_batch.get("file_id")
            if not file_id_in_entry_obj: continue # Malformed entry

            file_id_in_entry_str = str(file_id_in_entry_obj)

            # If this file is one we requested and we haven't processed it yet from another (older) batch
            if file_id_in_entry_str in file_id_str_list and file_id_in_entry_str not in processed_file_entries:
                 if file_entry_in_batch.get("status") == 1: # Only consider successfully processed files
                    processed_file_entries[file_id_in_entry_str] = file_entry_in_batch
                 else:
                    print(f"File {file_id_in_entry_str} found in batch {batch_doc['_id']} but its status is not 1 (completed). Status: {file_entry_in_batch.get('status')}")


    if not processed_file_entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No successfully processed test case data found for the provided file_ids in any batch.")

    # --- CSV Header ---
    csv_header_fields = [
        "TCID", "Test type","Title", "Description", "Precondition",
        "Steps", "Action", "Data", "Result", "Test Nature", "Test priority"
    ] # Ensure your parse_test_cases_from_content_string returns dicts with these keys

    # --- Mode Handling ---
    if mode == "csv":
        if len(processed_file_entries) > 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="CSV mode is only supported for a single file_id. Multiple file_ids were found processed. Use mode='zip'.")
        if not processed_file_entries: # Should be caught above, but defensive
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No processed file found for CSV mode.")

        # Get the single file entry
        # Since processed_file_entries is a dict, get its first (and only) value
        single_file_id_str = list(processed_file_entries.keys())[0]
        file_entry_data = processed_file_entries[single_file_id_str]

        csv_output_stream = io.StringIO()
        csv_writer = csv.DictWriter(csv_output_stream, fieldnames=csv_header_fields, extrasaction='ignore')
        csv_writer.writeheader()

        file_had_matching_types = False
        test_cases_dict_in_file_entry = file_entry_data.get("test_cases", {})
        for requested_type_lower in requested_types_lower:
            # Find the test case content for the current requested_type_lower
            original_tc_type_key, tc_type_data_obj = get_case_insensitive_from_dict(test_cases_dict_in_file_entry, requested_type_lower)

            if tc_type_data_obj and isinstance(tc_type_data_obj, dict) and tc_type_data_obj.get("content"):
                content_string = tc_type_data_obj["content"]
                parsed_tc_rows = parse_test_cases_from_content_string(content_string)
                for row_dict in parsed_tc_rows:
                    row_dict["Test type"] = original_tc_type_key or requested_type_lower # Set the actual type found or requested
                    csv_writer.writerow(row_dict)
                if parsed_tc_rows:
                    file_had_matching_types = True
        
        if not file_had_matching_types:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No test cases found for the file '{file_entry_data.get('file_name', single_file_id_str)}' matching the requested types: {', '.join(requested_types_lower)}.")

        csv_output_stream.seek(0)
        csv_filename = f"{file_entry_data.get('file_name', 'testcases').rsplit('.',1)[0]}_test_cases.csv"
        return StreamingResponse(
            io.BytesIO(csv_output_stream.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=\"{csv_filename}\""}
        )

    elif mode == "zip":
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive_file:
            any_file_had_data = False
            for file_id_str, file_entry_data in processed_file_entries.items():
                csv_output_stream_for_zip = io.StringIO()
                csv_writer_for_zip = csv.DictWriter(csv_output_stream_for_zip, fieldnames=csv_header_fields, extrasaction='ignore')
                csv_writer_for_zip.writeheader()

                file_in_zip_had_matching_types = False
                test_cases_dict_in_file_entry = file_entry_data.get("test_cases", {})
                for requested_type_lower in requested_types_lower:
                    original_tc_type_key, tc_type_data_obj = get_case_insensitive_from_dict(test_cases_dict_in_file_entry, requested_type_lower)

                    if tc_type_data_obj and isinstance(tc_type_data_obj, dict) and tc_type_data_obj.get("content"):
                        content_string = tc_type_data_obj["content"]
                        parsed_tc_rows = parse_test_cases_from_content_string(content_string)
                        for row_dict in parsed_tc_rows:
                            row_dict["Test type"] = original_tc_type_key or requested_type_lower
                            csv_writer_for_zip.writerow(row_dict)
                        if parsed_tc_rows:
                            file_in_zip_had_matching_types = True
                            any_file_had_data = True
                
                if file_in_zip_had_matching_types:
                    csv_output_stream_for_zip.seek(0)
                    csv_bytes_for_zip = csv_output_stream_for_zip.getvalue().encode('utf-8')
                    csv_filename_in_zip = f"{file_entry_data.get('file_name', file_id_str).rsplit('.',1)[0]}_test_cases.csv"
                    zip_archive_file.writestr(csv_filename_in_zip, csv_bytes_for_zip)
            
            if not any_file_had_data:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No test cases found for any of the files matching the requested types: {', '.join(requested_types_lower)}.")

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": "attachment; filename=\"test_cases_batch.zip\""}
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mode specified. Choose 'zip' or 'csv'.")



# MOVED ENDPOINT DEFINITION for /test-case-batch/results
@api_v1_router.post(
    "/test-case-batch/results",
    response_model=TestCaseBatchResultResponse,
    tags=["Document Test Cases"]
)
async def get_test_case_batch_results(body: TestCaseBatchRequest = Body(...)):
    from bson import ObjectId # Local import for ObjectId

    try:
        batch_generation_obj_id = ObjectId(body.generation_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid generation_id format.")

    batch_doc = documents_collection.find_one({
        "_id": batch_generation_obj_id,
        "is_test_case_generation_batch": True
    })
    if not batch_doc:
        raise HTTPException(status_code=404, detail=f"Test case generation batch with ID '{body.generation_id}' not found.")

    requested_file_ids_set = set(body.file_ids)
    if not requested_file_ids_set:
         raise HTTPException(status_code=400, detail="No file_ids provided in the request.")

    types_list_lower = [t.strip().lower() for t in (body.types or []) if t.strip()] if body.types else None

    results: List[TestCaseFileResult] = []
    files_in_batch = batch_doc.get("files", [])

    found_any_requested_file_in_batch = False
    for file_sub_doc in files_in_batch:
        file_id_obj = file_sub_doc.get("file_id") # This should be an ObjectId
        if not file_id_obj:
            continue # Skip malformed entries

        file_id_str = str(file_id_obj)

        if file_id_str in requested_file_ids_set:
            found_any_requested_file_in_batch = True
            all_cases_for_file = file_sub_doc.get("test_cases") # Expected: {"functional": [...], "security": [...]}
            
            if not isinstance(all_cases_for_file, dict): # If test_cases is not a dict, treat as no cases
                all_cases_for_file = {}

            filtered_cases_for_file: Dict[str, Any] = {}
            if types_list_lower:
                for tc_type, tc_list in all_cases_for_file.items():
                    if tc_type.lower() in types_list_lower:
                        filtered_cases_for_file[tc_type] = tc_list
            else: # No type filter, return all test cases for this file
                filtered_cases_for_file = all_cases_for_file

            # Only add to results if there are test cases after filtering (or if no filter was applied and cases exist)
            # If types_list_lower is present, filtered_cases_for_file must not be empty.
            # If types_list_lower is None (no filter), all_cases_for_file is used, add if it's not empty.
            if (types_list_lower and filtered_cases_for_file) or (not types_list_lower and all_cases_for_file):
                results.append(TestCaseFileResult(
                    file_id=file_id_str,
                    file_name=file_sub_doc.get("file_name", "Unknown Filename"),
                    status=file_sub_doc.get("status"),
                    progress=file_sub_doc.get("progress"),
                    error_info=file_sub_doc.get("error_info"),
                    test_cases=filtered_cases_for_file
                ))
            elif types_list_lower and not filtered_cases_for_file:
                 # File was matched by ID, types were requested, but no test cases matched the types.
                 # Still, include the file status.
                 results.append(TestCaseFileResult(
                    file_id=file_id_str,
                    file_name=file_sub_doc.get("file_name", "Unknown Filename"),
                    status=file_sub_doc.get("status"),
                    progress=file_sub_doc.get("progress"),
                    error_info=file_sub_doc.get("error_info"),
                    test_cases={} # Empty dict as no types matched
                ))
            # else: if no types requested and all_cases_for_file is empty, don't add.
            # This part handles if a file_id is matched but has no test cases AT ALL.
            # We might still want to return its status.
            elif not types_list_lower and not all_cases_for_file:
                 results.append(TestCaseFileResult(
                    file_id=file_id_str,
                    file_name=file_sub_doc.get("file_name", "Unknown Filename"),
                    status=file_sub_doc.get("status"),
                    progress=file_sub_doc.get("progress"),
                    error_info=file_sub_doc.get("error_info"),
                    test_cases={} # Empty dict as no test cases
                ))


    if not found_any_requested_file_in_batch:
        raise HTTPException(status_code=404, detail=f"None of the requested file_ids were found in batch '{body.generation_id}'.")

    
    all_results_have_empty_cases = True
    if results: # only if we have some results to check
        for res_item in results:
            if res_item.test_cases and len(res_item.test_cases) > 0:
                all_results_have_empty_cases = False
                break
    
    if not results or (results and all_results_have_empty_cases and types_list_lower):
        
        if results and all_results_have_empty_cases and types_list_lower:
             
             raise HTTPException(status_code=404, detail="No data to return. Either requested file_ids were not in the batch, or they had no processable information.")


    return TestCaseBatchResultResponse(
        generation_id=body.generation_id,
        requested_file_ids=body.file_ids, # Echo back what was requested
        requested_types=body.types,     # Echo back what was requested
        results=results
    )


# --- Auth & Utility Endpoints ---
@api_v1_router.post("/auth/token", response_model=Dict[str, str], tags=["Authentication"])
async def login_for_access_token(request: TokenRequest):
    if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
    if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
        token = create_jwt_token(data={"sub": request.username, "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

@api_v1_router.get("/utilities/api-key-usage/{api_key_suffix}", tags=["Utilities"])
async def get_api_key_usage_stats(api_key_suffix: str):
    if len(api_key_suffix) < 5 : raise HTTPException(status_code=400, detail="Suffix too short (min 5 chars).")
    # Try finding by exact suffix first, then by full key if suffix match fails (for older records)
    rec = cost_collection.find_one({"api_key_suffix": api_key_suffix})
    if not rec: rec = cost_collection.find_one({"api_key": api_key_suffix})
    if not rec: return {"id":api_key_suffix, "tokens_used":0, "cost_usd":0.0, "message":"No usage data found for this API key suffix."}
    return {
        "api_key_suffix_queried":api_key_suffix,
        "api_key_suffix_in_db": rec.get("api_key_suffix", "N/A - Likely full key stored"),
        "tokens_used":rec.get("tokens_used",0),
        "cost_usd":round(rec.get("cost_usd",0.0),6),
        "last_updated":rec.get("last_updated","N/A"),
        "first_recorded": rec.get("first_recorded", "N/A")
        }

# THIS LINE MUST COME AFTER ALL @api_v1_router DEFINITIONS
app.include_router(api_v1_router)

# --- WebSocket Endpoint ---
@app.websocket("/ws/v1/task_status_by_doc/{doc_id}")
async def websocket_task_status_by_doc(websocket: WebSocket, doc_id: str):
    token = websocket.query_params.get("token")
    if not SECRET_KEY_ENV:
        await websocket.accept()
        await websocket.send_json({"s": "err", "m": "JWT secret missing on server."})
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return
    if not token:
        await websocket.accept()
        await websocket.send_json({"s": "err", "m": "Authentication token missing in query parameters."})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    username = "ws_user_anonymous" # Default username
    try:
        from jose import jwt, JWTError # Keep local for WebSocket specific auth
        payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
        username = payload.get("sub", "ws_user_no_sub_in_token")
       
    except JWTError as e_auth_ws:
        await websocket.accept()
        await websocket.send_json({"s": "err", "m": f"Authentication failed: {str(e_auth_ws)}"})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except Exception as e_jwt_other: # Catch other potential errors from jwt.decode
        await websocket.accept()
        await websocket.send_json({"s": "err", "m": f"Authentication error: {str(e_jwt_other)}"})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    print(f"WS Connection accepted: doc_id '{doc_id}', user '{username}'")
    await websocket.send_json({"status": "connected", "message": f"Monitoring document '{doc_id}' for test case generation status."})

    try:
        from bson import ObjectId # Local import for ObjectId
        doc_obj_id = ObjectId(doc_id)
    except InvalidId:
        await websocket.send_json({"status": "error", "message": f"Invalid document ID format: '{doc_id}'."})
        await websocket.close(code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA) # Or 1003 for unsupported
        return
    except Exception as e_oid_other: # Catch other ObjectId errors
        await websocket.send_json({"status": "error", "message": f"Error processing document ID: {str(e_oid_other)}"})
        await websocket.close(code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA)
        return

    # Celery specific imports, keep local to this endpoint if not used widely
    from celery.result import AsyncResult
    from starlette.websockets import WebSocketState
    import asyncio

    last_known_task_id = None
    task_mon: Optional[AsyncResult] = None
    initial_check = True

    try:
        while True:
            if websocket.client_state != WebSocketState.CONNECTED:
                print(f"WS Client '{username}' (doc '{doc_id}') disconnected by client state.")
                break

            # Fetch only necessary fields
            doc_info_ws = documents_collection.find_one(
                {"_id": doc_obj_id},
                {
                    "status": 1, 
                    "progress": 1, 
                    "error_info": 1, 
                    "last_task_id": 1, 
                    "test_cases": 1, # Make sure to fetch this field
                    "file_name": 1, 
                    "requested_test_case_types": 1
                }
            )

            if not doc_info_ws:
                await websocket.send_json({"status": "error", "message": f"Document '{doc_id}' not found."})
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                break

            current_task_id = doc_info_ws.get("last_task_id")
            db_status_code = doc_info_ws.get("status")
            progress_log = doc_info_ws.get("progress", [])
            error_message_db = doc_info_ws.get("error_info")
            
            # --- ROBUST HANDLING OF test_cases ---
            retrieved_test_cases = doc_info_ws.get("test_cases") # Get the field value
            generated_types_ws = [] # Default to empty list

            if isinstance(retrieved_test_cases, dict):
                # If it's a dictionary (even empty), get its keys
                generated_types_ws = list(retrieved_test_cases.keys())
            elif retrieved_test_cases is None:
                # If it's explicitly None in the DB, or not present and get() returned None (though default should prevent this unless default changes)
                print(f"WS Info (doc '{doc_id}'): 'test_cases' field is None or not present in DB. Treating as no generated types.")
                # generated_types_ws remains an empty list
            else:
                # Some other unexpected type, log it and treat as no generated types
                print(f"WS Warning (doc '{doc_id}'): 'test_cases' field is of unexpected type: {type(retrieved_test_cases)}. Treating as no generated types.")
                # generated_types_ws remains an empty list
            # --- END ROBUST HANDLING ---

            celery_state_str = "N/A"
            celery_task_info = None
            # ... (rest of your Celery task monitoring logic) ...

            if current_task_id:
                if current_task_id != last_known_task_id:
                    task_mon = AsyncResult(current_task_id)
                    last_known_task_id = current_task_id
                    print(f"WS (doc '{doc_id}'): Monitoring new Celery task_id: {current_task_id}")
                    await websocket.send_json({"status": "info", "message": f"Now monitoring Celery task ID: {current_task_id}"})

                if task_mon:
                    celery_state_str = task_mon.state
                    if celery_state_str == "PROGRESS":
                        celery_task_info = task_mon.info
                    # ... (other celery states)
            # ...


            response_payload = {
                "document_id": doc_id,
                "file_name": doc_info_ws.get("file_name", "N/A"),
                "database_status_code": db_status_code,
                "database_status_message": {-1: "Pending Generation", 0: "Processing", 1: "Completed Successfully", 2: "Error"}.get(db_status_code, "Unknown"),
                "progress_log": progress_log,
                "database_error_info": error_message_db,
                "celery_task_id": current_task_id,
                "celery_task_state": celery_state_str,
                "celery_task_progress_info": celery_task_info, # This might be large if not careful
                "requested_test_case_types": doc_info_ws.get("requested_test_case_types", []),
                "generated_test_case_types": generated_types_ws # Use the safely processed list
            }

            await websocket.send_json(response_payload)
            initial_check = False

            # ... (rest of your WebSocket loop: break conditions, sleep) ...
            if db_status_code == 1: # Completed successfully
                await websocket.send_json({"status": "final", "message": "Test case generation completed successfully."})
                break
            if db_status_code == 2: # Error in DB
                await websocket.send_json({"status": "final", "message": f"Test case generation failed. DB Error: {error_message_db}"})
                break
            
            await asyncio.sleep(3) # Poll interval

    except WebSocketDisconnect:
        print(f"WS Client '{username}' (doc '{doc_id}') disconnected.")
    except Exception as e_ws_main:
        error_type_name = type(e_ws_main).__name__
        print(f"WS Unhandled Error for doc '{doc_id}' (user '{username}'): {error_type_name} - {e_ws_main}")
        # ... (rest of your finally block and error sending)
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json({"status": "error", "message": f"A server-side WebSocket error occurred: {error_type_name}."})
            except Exception as e_send_err:
                print(f"WS: Failed to send error to client after main error: {e_send_err}")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                print(f"WS for doc '{doc_id}' (user '{username}'): Attempting to close connection.")
                await websocket.close(code=status.WS_1001_GOING_AWAY)
            except RuntimeError as e_close_runtime: # Can happen if already closing
                print(f"WS for doc '{doc_id}' (user '{username}'): Runtime error during close: {e_close_runtime}")
            except Exception as e_close:
                print(f"WS for doc '{doc_id}' (user '{username}'): Generic error during close: {e_close}")
        print(f"WS for doc '{doc_id}' (user '{username}') definitively closed.")


# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn
    print(f"--- GenAI API (Full Integration with DataSpaces) Starting ---")
    print(f"MongoDB URL: {MONGODB_URL}, DB: {MONGO_DB_NAME}")
    print(f"Input DIR: {INPUT_DIR}, Output DIR: {OUTPUT_DIR}")
    if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
        csv_output_dir_path = Path(test_case_utils.CSV_OUTPUT_DIR)
        csv_output_dir_path.mkdir(parents=True, exist_ok=True) # Ensure it exists
        print(f"CSV Output DIR (utils): {csv_output_dir_path.resolve()}")
    else:
        print("Warning: test_case_utils.CSV_OUTPUT_DIR not defined. CSVs might not be saved to a specific directory.")

    # Check if INPUT_DIR and OUTPUT_DIR exist, create if not
    Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Ensured Input DIR exists: {Path(INPUT_DIR).resolve()}")
    print(f"Ensured Output DIR exists: {Path(OUTPUT_DIR).resolve()}")


    uvicorn.run(
        "main3:app", # Important: "filename:app_instance_name"
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True # Add reload for development
        )

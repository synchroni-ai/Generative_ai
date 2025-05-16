from fastapi import BackgroundTasks, HTTPException
from task_with_api_key import process_and_generate_task # Assuming this is your Celery task
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
    WebSocketDisconnect, # Added for WebSocket handler
)
from fastapi.responses import JSONResponse, FileResponse
from utils.jwt_auth import create_jwt_token # Assuming this function is defined correctly

from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
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
import csv
import asyncio # For WebSocket polling sleep
from starlette.websockets import WebSocketState # For checking WebSocket state

# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
# from core.websocket import websocket_endpoint # This was for the old ws, can be removed if not used elsewhere

load_dotenv() # Ensure .env variables are loaded

mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]
cost_collection = db["cost_tracking"]


def serialize_document(doc):
    if doc and "_id" in doc: # Ensure doc is not None
        doc["_id"] = str(doc["_id"])
    return doc


# ----------------- Directories Setup -----------------
TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH") # Note: Same as test case path?
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

# Ensure directories exist
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)


VALID_TEST_CASE_TYPES = [
    "functional",
    "non-functional",
    "security",
    "performance",
    "boundary",
    "compliance",
]

# @app.post("/process_and_generate/")
# async def process_and_generate(
#     file: UploadFile = File(...),
#     model_name: str = Form("Mistral"),
#     chunk_size: Optional[int] = Query(default=None),
#     cache_key: Optional[str] = Query(default=None),
#     api_key: Optional[str] = Form(None),
#     test_case_types: str = Form("all"),  # Default is 'all'
# ):
#     # Convert comma-separated test_case_types to a list
#     test_case_types_list = [t.strip().lower() for t in test_case_types.split(",")]

#     # Handle 'all' case
#     if "all" in test_case_types_list:
#         test_case_types_list = VALID_TEST_CASE_TYPES
#     else:
#         for test_case_type in test_case_types_list:
#             if test_case_type not in VALID_TEST_CASE_TYPES:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Invalid test_case_type: {test_case_type}. Must be one of {VALID_TEST_CASE_TYPES} or 'all'",
#                 )

#     # Use default if user key not provided
#     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
#     warning = (
#         "Using default API key. Consider providing your own to avoid shared limits."
#         if not api_key else None
#     )

#     file_name = file.filename
#     file_path = Path(INPUT_DIR) / file_name

#     # Save the uploaded file
#     try:
#         contents = await file.read()
#         with open(file_path, "wb") as f:
#             f.write(contents)
#     finally:
#         await file.close()

#     task_results: Dict[str, AsyncResult] = {}
#     all_task_ids = {}

#     # Launch Celery tasks
#     for test_case_type in test_case_types_list:
#         task = process_and_generate_task.delay(
#             str(file_path),
#             model_name,
#             chunk_size,
#             api_key_to_use,
#             test_case_type,
#         )
#         task_results[test_case_type] = task
#         all_task_ids[test_case_type] = task.id

#     # Wait for all tasks to complete
#     results = {}
#     all_test_cases = {}
#     all_excel_paths = {}
#     for test_case_type, task in task_results.items():
#         results[test_case_type] = task.get()  # Blocking wait
#         all_test_cases[test_case_type] = results[test_case_type]["test_cases"]
#         all_excel_paths[test_case_type] = results[test_case_type]["excel_path"]

#     # Combine test case strings
#     combined_test_cases = "\n".join(
#         [f"--- {k} ---\n{v}" for k, v in all_test_cases.items()]
#     )

#     # Use the Excel path from the first test case type
#     excel_test_case_path = all_excel_paths[test_case_types_list[0]]

#     # MongoDB document
#     document = {
#         "doc_name": os.path.basename(file_path),
#         "doc_path": str(file_path),
#         "test_case_excel_path": excel_test_case_path,
#         "selected_model": model_name,
#         "all_llm_responses_testcases": all_test_cases,
#         "llm_response_testcases": combined_test_cases,
#         "api_key_used": f"...{api_key_to_use[-5:]}",
#         "test_case_types": test_case_types_list,
#     }

#     try:
#         collection.insert_one(document)
#     except Exception as e:
#         print("MongoDB Insertion Error:", str(e))

#     return {
#         "message": "File uploaded successfully. Processing started.",
#         "task_ids": all_task_ids,
#         "api_key_being_used": f"...{api_key_to_use[-5:]}",
#         "warning": warning,
#         "test_case_types": test_case_types_list,
#     }

@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    file_name = file.filename
    file_path = Path(INPUT_DIR) / file_name

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        await file.close()


    document_data = {
        "file_name": file_name,
        "file_path": str(file_path),
        "status": "uploaded",
        "created_at": time.time() # Optional: add a timestamp
    }
    try:
        result = collection.insert_one(document_data)
        file_id = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving document to DB: {str(e)}")


    return {
        "message": "File uploaded successfully",
        "file_name": file_name,
        "file_path": str(file_path),
        "file_id": file_id
    }

@app.post("/generate_test_cases/")
async def generate_test_cases(
    file_id: str = Form(...),
    model_name: Optional[str] = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    # cache_key: Optional[str] = Query(default=None), # cache_key is not used in process_and_generate_task shown
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form("all")
):
    try:
        doc_object_id = ObjectId(file_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid file_id format.")

    document = collection.find_one({"_id": doc_object_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found in the database.")

    file_path_str = document.get("file_path")
    if not file_path_str:
        raise HTTPException(status_code=404, detail="File path not found in document record.")
    
    file_path = Path(file_path_str)
    if not file_path.exists():
        # Potentially try to re-create if missing but this is usually a sign of a bigger issue
        raise HTTPException(status_code=404, detail=f"File not found on disk at path: {file_path_str}")

    test_case_types_list = [t.strip().lower() for t in test_case_types.split(",")]
    if "all" in test_case_types_list:
        test_case_types_list = VALID_TEST_CASE_TYPES
    else:
        for test_case_type in test_case_types_list:
            if test_case_type not in VALID_TEST_CASE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid test_case_type: {test_case_type}. Must be one of {VALID_TEST_CASE_TYPES} or 'all'",
                )

    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
    if not api_key_to_use:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="API key not provided and default TOGETHER_API_KEY is not set.")

    warning = (
        "Using default API key. Consider providing your own to avoid shared limits."
        if not api_key else None
    )

    # Pass file_id to the Celery task
    task = process_and_generate_task.delay(
        file_id, # The MongoDB document _id as a string
        str(file_path),
        model_name,
        chunk_size,
        api_key_to_use,
        test_case_types_list,
    )

    collection.update_one(
        {"_id": doc_object_id},
        {
            "$set": {
                "status": "processing",
                "last_task_id": task.id,
                "model_name_requested": model_name,
                "test_case_types_requested": test_case_types_list,
                "updated_at": time.time()
            }
        }
    )

    return {
        "message": "Test case generation started.",
        "file_id": file_id,
        "task_id": task.id,
        "api_key_being_used": f"...{api_key_to_use[-5:]}" if api_key_to_use and len(api_key_to_use) > 5 else "default",
        "warning": warning,
        "test_case_types": test_case_types_list
    }

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    response_data = {"task_id": task_id, "status": task.state}
    if task.state == "SUCCESS":
        response_data["result"] = task.result
    elif task.state == "FAILURE":
        response_data["error"] = str(task.info) # task.info contains the exception
    elif task.state == "PROGRESS":
        response_data["progress"] = task.info # task.info contains progress metadata
    return response_data


# ----------------- MongoDB Fetch Endpoints -----------------
@app.get("/documents/")
def get_all_documents():
    documents = list(collection.find().sort("created_at", -1)) # Sort by newest first
    return [serialize_document(doc) for doc in documents]


@app.get("/documents/{document_id}")
def get_document_by_id(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")
    
    doc = collection.find_one({"_id": doc_object_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return serialize_document(doc)


# ----------------- Delete Documents Endpoint -----------------
@app.delete("/delete-documents")
def delete_documents(document_ids: List[str] = Query(...)): # Taking list from query params
    deleted_count = 0
    errors = []
    for document_id in document_ids:
        try:
            doc_object_id = ObjectId(document_id)
            doc = collection.find_one({"_id": doc_object_id})
            if not doc:
                errors.append(f"Document {document_id} not found")
                continue

            # Delete associated files (doc_path, excel paths etc.)
            # Be careful with this in production - ensure paths are sanitized
            file_path_str = doc.get("doc_path")
            if file_path_str and os.path.exists(file_path_str):
                try:
                    os.remove(file_path_str)
                except OSError as e:
                    errors.append(f"Error deleting file {file_path_str} for doc {document_id}: {e}")
            
            excel_path_str = doc.get("test_case_excel_path")
            if excel_path_str and os.path.exists(excel_path_str):
                try:
                    os.remove(excel_path_str)
                except OSError as e:
                    errors.append(f"Error deleting Excel file {excel_path_str} for doc {document_id}: {e}")

            user_story_excel_path_str = doc.get("user_story_excel_path")
            if user_story_excel_path_str and os.path.exists(user_story_excel_path_str):
                try:
                    os.remove(user_story_excel_path_str)
                except OSError as e:
                    errors.append(f"Error deleting user story Excel file {user_story_excel_path_str} for doc {document_id}: {e}")


            result = collection.delete_one({"_id": doc_object_id})
            if result.deleted_count > 0:
                deleted_count += 1

        except InvalidId:
            errors.append(f"Invalid document ID format: {document_id}")
        except Exception as e:
            errors.append(f"Error processing document {document_id}: {str(e)}")

    response_message = f"{deleted_count} document(s) deleted successfully."
    if errors:
        response_message += " Errors encountered: " + "; ".join(errors)
        return JSONResponse(
            content={"message": response_message, "deleted_count": deleted_count, "errors": errors},
            status_code=status.HTTP_207_MULTI_STATUS if deleted_count > 0 else status.HTTP_500_INTERNAL_SERVER_ERROR ,
        )

    return JSONResponse(
        content={"message": response_message, "deleted_count": deleted_count},
        status_code=status.HTTP_200_OK,
    )


# ----------------- Download Excel Endpoints -----------------

@app.get("/download-csv/{document_id}")
def download_test_cases_csv(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    doc = collection.find_one({"_id": doc_object_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    all_test_cases_str = doc.get("all_test_cases_text") # <--- CHANGE THE FIELD NAME HERE # This field should be populated by the Celery task
    if not all_test_cases_str:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No test cases string (all_test_cases) found in document. Has the generation task completed and updated the document?")

    # Ensure EXCEL_OUTPUT_DIR exists (though it should be created at startup)
    Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    csv_output_path = Path(EXCEL_OUTPUT_DIR) / f"{document_id}_test_cases.csv"

    csv_headers = [
        "TCID", "Test type", "Title", "Description", "Precondition",
        "Steps", "Action", "Data", "Result", "Type (P / N / in)",
        "Test priority"
    ]

    try:
        with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers, quoting=csv.QUOTE_ALL)
            writer.writeheader()

            content_str = str(all_test_cases_str).strip()
            # ... (rest of your complex CSV parsing logic remains unchanged) ...
            # This logic is highly dependent on the LLM output format.
            if content_str:
                current_content_lines = content_str.splitlines()
                if current_content_lines and current_content_lines[0].strip().startswith("---"):
                    current_content_lines.pop(0)
                while current_content_lines and not current_content_lines[0].strip():
                    current_content_lines.pop(0)
                if current_content_lines and current_content_lines[0].strip().lower() == "test cases:":
                    current_content_lines.pop(0)
                while current_content_lines and not current_content_lines[0].strip():
                    current_content_lines.pop(0)
                content_to_split = "\n".join(current_content_lines).strip()

                individual_tc_blocks = []
                if content_to_split:
                    split_pattern = r'(?=^(?:\*\*(?:TC|PTC)_\d+\*\*|TCID:|Test Case ID:)\s*)'
                    potential_blocks = re.split(split_pattern, content_to_split, flags=re.MULTILINE)
                    processed_blocks = [b.strip() for b in potential_blocks if b.strip()]

                    if processed_blocks:
                        first_block_content = processed_blocks[0]
                        is_first_block_a_tc = re.match(r'^(?:\*\*(?:TC|PTC)_\d+\*\*|TCID:|Test Case ID:)', first_block_content.lstrip(), re.IGNORECASE)
                        if not is_first_block_a_tc and len(processed_blocks) > 1:
                            # Assuming the first block might be some preamble if it doesn't start like a TC
                            individual_tc_blocks = processed_blocks[1:]
                        else:
                            individual_tc_blocks = processed_blocks
                
                # Fallback if the above complex split yields nothing but there's content
                if not individual_tc_blocks and content_to_split: 
                    # Check if the entire content itself could be a single TC block
                    if re.match(r'^(?:\*\*(?:TC|PTC)_\d+\*\*|TCID:|Test Case ID:)', content_to_split.lstrip(), re.IGNORECASE):
                        individual_tc_blocks.append(content_to_split)
                    # else: consider logging that no TC blocks were identified

                for block_index, block in enumerate(individual_tc_blocks):
                    fields = {header: "N/A" for header in csv_headers} # Default to N/A
                    collecting_steps = False
                    current_steps_list = []
                    lines_in_block = block.splitlines()

                    first_line_processed_for_tcid = False
                    if lines_in_block:
                        first_line_stripped = lines_in_block[0].strip()
                        # Attempt to extract TCID if it's standalone on the first line like **TC_001**
                        tcid_standalone_match = re.match(r'^\*\*((?:TC|PTC)_\d+)\*\*\s*$', first_line_stripped)
                        if tcid_standalone_match:
                            fields["TCID"] = tcid_standalone_match.group(1)
                            first_line_processed_for_tcid = True
                    
                    for line_idx, line_content in enumerate(lines_in_block):
                        if first_line_processed_for_tcid and line_idx == 0:
                            continue # Already processed this line for TCID

                        line = line_content.strip()
                        if not line: # Skip empty lines
                            continue

                        key_value_match = re.match(r'^\**([^:]+):\**\s*(.*)', line)
                        if key_value_match:
                            key = key_value_match.group(1).strip().lower()
                            value = key_value_match.group(2).strip()
                            collecting_steps = False # Stop collecting steps if a new key-value is found

                            if key in ["tcid", "test case id"] and fields["TCID"] == "N/A": fields["TCID"] = value # Prioritize standalone if found
                            elif key in ["test type", "test case type"]: fields["Test type"] = value
                            elif key == "title": fields["Title"] = value
                            elif key == "description": fields["Description"] = value
                            elif key == "precondition": fields["Precondition"] = value
                            elif key == "action": fields["Action"] = value
                            elif key == "data": fields["Data"] = value
                            # MODIFICATION 1 comment was about "Expected Result". Current header is "Result".
                            # Assuming "Result" here means "Expected Result" or general result.
                            elif key == "result": fields["Result"] = value 
                            elif key == "type (p / n / in)": fields["Type (P / N / in)"] = value
                            elif key == "test priority": fields["Test priority"] = value
                            elif key == "steps":
                                collecting_steps = True
                                if value: current_steps_list.append(value) # Capture value on the same line as "Steps:"
                        elif collecting_steps:
                            current_steps_list.append(line) # Append subsequent lines as part of steps
                    
                    fields["Steps"] = " ".join(current_steps_list).strip() if current_steps_list else "N/A"
                    
                    # Ensure no field is empty, default to "N/A"
                    for f_key in fields:
                        if fields[f_key] == "": fields[f_key] = "N/A"
                    
                    writer.writerow(fields)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating CSV file: {str(e)}")

    return FileResponse(str(csv_output_path), media_type="text/csv", filename=csv_output_path.name)
    
@app.get("/download/testcases/{document_id}")
def download_test_cases_excel(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")
    
    doc = collection.find_one({"_id": doc_object_id})
    if not doc or "test_case_excel_path" not in doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Excel file not found for test cases. Check if generation task completed and updated the document."
        )
    
    excel_path_str = doc["test_case_excel_path"]
    if not os.path.exists(excel_path_str):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Excel file path found in DB but file does not exist on disk: {excel_path_str}")

    return FileResponse(
        excel_path_str,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=Path(excel_path_str).name,
    )


@app.get("/download/userstories/{document_id}")
def download_user_stories_excel(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format")

    doc = collection.find_one({"_id": doc_object_id})
    if not doc or "user_story_excel_path" not in doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Excel file not found for user stories. Check if generation task completed and updated the document."
        )

    excel_path_str = doc["user_story_excel_path"]
    if not os.path.exists(excel_path_str):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User story Excel file path found in DB but file does not exist on disk: {excel_path_str}")

    return FileResponse(
        excel_path_str,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=Path(excel_path_str).name,
    )


@app.get("/api_key_usage/{api_key}")
def get_api_key_cost(api_key: str):
    # Basic security: avoid logging full api_key unless necessary for debugging in a secure env
    # For this example, we assume api_key is stored as is.
    # Consider storing hashed API keys or partial keys if security is a major concern for this lookup.
    record = cost_collection.find_one({"api_key": api_key})
    if not record:
        return {"api_key_identifier": f"...{api_key[-5:]}" if len(api_key) > 5 else api_key, "tokens_used": 0, "cost_usd": 0.0}
    return {
        "api_key_identifier": f"...{api_key[-5:]}" if len(api_key) > 5 else api_key,
        "tokens_used": record.get("tokens_used", 0),
        "cost_usd": round(record.get("cost_usd", 0.0), 4),
    }


# JWT Configuration (should match what create_jwt_token uses)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256" # Ensure this matches the algorithm in create_jwt_token

if not SECRET_KEY:
    print("WARNING: SECRET_KEY environment variable is not set. JWT authentication for WebSockets will fail.")
    # raise ValueError("SECRET_KEY environment variable is required for JWT.") # Or handle more gracefully

@app.websocket("/ws/task_status/{task_id}")
async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
    token = websocket.query_params.get("token")
    
    if not SECRET_KEY: # Should be checked at startup, but good to have a runtime check for WS
        await websocket.accept() # Accept to send an error, then close
        await websocket.send_json({"status": "error", "message": "Server configuration error: JWT secret not set."})
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    if not token:
        # Optionally, accept and send an error message before closing
        await websocket.accept()
        await websocket.send_json({"status": "error", "message": "Authentication token missing."})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        from jose import jwt, JWTError # Moved import here to ensure SECRET_KEY check happens first
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if not username:
            await websocket.accept()
            await websocket.send_json({"status": "error", "message": "Invalid token: Subject missing."})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError as e:
        await websocket.accept()
        await websocket.send_json({"status": "error", "message": f"Authentication failed: {str(e)}"})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    await websocket.send_json({"status": "connected", "message": f"Authenticated as {username}. Monitoring task {task_id}."})

    task_monitor = AsyncResult(task_id)
    try:
        while True:
            task_state = task_monitor.state
            response_data = {"task_id": task_id, "status": task_state}

            if task_state == "PENDING":
                response_data["info"] = "Task is waiting to be processed."
            elif task_state == "STARTED":
                response_data["info"] = "Task has started."
            elif task_state == "PROGRESS":
                response_data["progress"] = task_monitor.info  # Celery task must use self.update_state(meta=...)
            elif task_state == "SUCCESS":
                response_data["result"] = task_monitor.result
                await websocket.send_json(response_data)
                break  # Task finished
            elif task_state == "FAILURE":
                response_data["error"] = str(task_monitor.info) # Exception info
                await websocket.send_json(response_data)
                break  # Task finished
            elif task_state == "RETRY":
                response_data["info"] = "Task is being retried."
                response_data["error"] = str(task_monitor.info)
            
            await websocket.send_json(response_data)

            if task_monitor.ready(): # Final check if task is completed (SUCCESS, FAILURE)
                # Ensure final state is sent if loop condition missed it
                if task_state not in ["SUCCESS", "FAILURE"]: # e.g. if it became ready between state check and send
                    final_state = task_monitor.state
                    final_response = {"task_id": task_id, "status": final_state}
                    if final_state == "SUCCESS": final_response["result"] = task_monitor.result
                    elif final_state == "FAILURE": final_response["error"] = str(task_monitor.info)
                    await websocket.send_json(final_response)
                break 

            await asyncio.sleep(2)  # Poll Celery every 2 seconds

    except WebSocketDisconnect:
        print(f"Client {username} (task: {task_id}) disconnected.")
    except Exception as e:
        # Log the error for server-side debugging
        print(f"Unexpected error in WebSocket for task {task_id} (User: {username}): {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        # Try to inform the client if the WebSocket is still open
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json({"status": "error", "message": "An unexpected error occurred on the server."})
            except Exception: # Catch error if send fails (e.g. socket already closed)
                pass
    finally:
        # Ensure WebSocket is closed if it hasn't been already
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close(code=status.WS_1001_GOING_AWAY)
            except RuntimeError: # Handles cases like "WebSocket is already closed"
                pass
        print(f"WebSocket connection for task {task_id} (User: {username}) definitively closed.")


# --- JWT Token Generation Endpoints ---
# It's good practice to have POST for actions that might create/retrieve sensitive data like tokens
class TokenRequest(BaseModel):
    username: str

@app.post("/get_token", tags=["Authentication"])
async def get_token_post(request: TokenRequest):
    if not request.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")
    
    if not SECRET_KEY: # Crucial for token generation
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cannot generate token: JWT Secret not configured on server.")

    # Assuming create_jwt_token is correctly implemented using jose.jwt and same SECRET_KEY/ALGORITHM
    # Example payload, customize as needed
    token_data = {"sub": request.username, "custom_claim": "example_value"} 
    try:
        token = create_jwt_token(token_data)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        # Log actual error server-side
        print(f"Error generating token: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate token.")


# @app.get("/get_tokens", tags=["Authentication"], deprecated=True, description="Use POST /get_token instead.") # Marked as deprecated
# async def get_token_get(username: str = Query(..., description="Username for which to generate the token.")):
#     if not username: # Query(...) makes it required, but good practice
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username query parameter is required")

#     if not SECRET_KEY:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cannot generate token: JWT Secret not configured on server.")
        
#     token_data = {"sub": username}
#     try:
#         token = create_jwt_token(token_data)
#         return {"access_token": token, "token_type": "bearer"}
#     except Exception as e:
#         print(f"Error generating token: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate token.")

# Pydantic model for JWT token endpoint, for clarity (already defined above TokenRequest)
# from pydantic import BaseModel
# class TokenRequest(BaseModel):
#     username: str
# @app.post("/get_token")
# def get_token(request: TokenRequest):
#     if not request.username:
#         raise HTTPException(status_code=400, detail="Username is required")
#     token = create_jwt_token({"sub": request.username})
#     return {"token": token}

if __name__ == "__main__":
    import uvicorn
    # This is for local development. In production, use a proper ASGI server like Uvicorn managed by a process manager.
    uvicorn.run(app, host="0.0.0.0", port=8000)
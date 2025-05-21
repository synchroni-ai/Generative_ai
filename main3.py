from fastapi import BackgroundTasks, HTTPException
from task_with_api_key import process_and_generate_task
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
    APIRouter,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse, FileResponse
from utils.jwt_auth import (
    create_jwt_token,
)
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
import asyncio  # For WebSocket polling sleep
from starlette.websockets import WebSocketState  # For checking WebSocket state
from collections import Counter # <<<<<<<<<<<<<<<<<<<<<<<<<<<< ADDED IMPORT


# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
# from utils import test_case_utils # Already imported above
from core.websocket import websocket_endpoint # Assuming this exists and is correct
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

# Load environment variables from .env file
load_dotenv() # Ensure .env is loaded if you haven't elsewhere

mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]
cost_collection = db["cost_tracking"]


def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return {
        # "_id": str(doc["_id"]),
        "file_id": str(doc["_id"]),
        "file_name": doc.get("file_name"),
        "file_path": doc.get("file_path"),
        "status": doc.get("status"),
        "selected_model": doc.get("selected_model", None),
        "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None, # Added timestamp serialization
        "last_task_id": doc.get("last_task_id") # Added last_task_id
    }
IST = ZoneInfo("Asia/Kolkata")

# ----------------- Directories Setup -----------------
TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH") # This seems to be the same as above, check if intended
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

# Create directories if they don't exist
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VALID_TEST_CASE_TYPES = [
    "functional",
    "non-functional",
    "security",
    "performance",
    "boundary",
    "compliance",
    "all" # Added 'all' here as it's a valid input, though handled specially
]


@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    file_name = file.filename
    file_path = Path(INPUT_DIR) / file_name

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    finally:
        await file.close()
    upload_time = datetime.now(IST)


    # Insert file metadata into MongoDB
    document_data = {
        "file_name": file_name,
        "file_path": str(file_path),
        "status": -1,  # Document uploaded but not processed
        "timestamp": upload_time
    }

    result = collection.insert_one(document_data)
    file_id = str(result.inserted_id)

    return {
        "message": "File uploaded successfully",
        "file_name": file_name,
        "file_path": str(file_path),
        "file_id": file_id,
        "timestamp": upload_time.isoformat()
    }


@app.post("/generate_test_cases/")
async def generate_test_cases(
    file_id: str = Form(...),
    model_name: Optional[str] = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form("all"),  # ✅ Accepts 'all' or comma-separated string like "functional,security"
):
    # ✅ Step 1: Fetch the document from MongoDB
    try:
        document = collection.find_one({"_id": ObjectId(file_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id format.")
 
    if not document:
        raise HTTPException(status_code=404, detail="Document not found in the database.")
 
    # ✅ Step 2: Ensure file path exists
    file_path = Path(document.get("file_path"))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")
 
    # ✅ Step 3: Parse and validate `test_case_types`
    if test_case_types.strip().lower() == "all":
        # If user requested all test cases, set full list
        test_case_types_to_send = "all"
        test_case_types_list = VALID_TEST_CASE_TYPES
    else:
        # ✅ Split and validate comma-separated input
        test_case_types_list = [t.strip().lower() for t in test_case_types.split(",")]
 
        # ✅ Check for any invalid test case types
        invalid_types = [t for t in test_case_types_list if t not in VALID_TEST_CASE_TYPES]
        if invalid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid test_case_type(s): {invalid_types}. Must be one of {VALID_TEST_CASE_TYPES} or 'all'.",
            )
 
        # ✅ Convert back to comma-separated string for Celery compatibility
        test_case_types_to_send = ",".join(test_case_types_list)
 
    # ✅ Step 4: Fallback to default API key if user hasn't supplied one
    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
    warning = (
        "Using default API key. Consider providing your own to avoid shared limits."
        if not api_key else None
    )
 
    # ✅ Step 5: Set status = 0 (processing) in MongoDB
    collection.update_one(
        {"_id": ObjectId(file_id)},
        {
            "$set": {
                "status": 0,
                "selected_model": model_name,
                "api_key_used": f"...{api_key_to_use[-5:]}",  # Mask key
            }
        },
    )
 
    # ✅ Step 6: Trigger Celery task (passes either "all" or comma-separated string)
    task = process_and_generate_task.apply_async(args=[
        str(file_path),             # file_path
        model_name,                 # model_name
        chunk_size,                 # chunk_size
        api_key_to_use,             # api_key
        test_case_types_to_send,    # "all" or "functional,security"
        file_id,                    # document_id
    ])
 
    # ✅ Save task ID to DB for tracking
    collection.update_one(
        {"_id": ObjectId(file_id)}, {"$set": {"last_task_id": task.id}}
    )
 
    # ✅ Step 7: Return response
    return {
        "message": "✅ Test case generation task started.",
        "task_id": task.id,
        "file_id": file_id,
        "test_case_types": test_case_types_list,  # Return list even if user passed 'all'
        "api_key_being_used": f"...{api_key_to_use[-5:]}",
        "warning": warning,
    }
 
 


@app.get("/documents/")
def get_all_documents():
    # Sort by timestamp descending to get newest first
    documents = list(collection.find().sort("timestamp", -1))
    return [serialize_document(doc) for doc in documents]


@app.get("/documents/{document_id}")
def get_document_by_id(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
        )

    doc = collection.find_one({"_id": doc_object_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return serialize_document(doc)


@app.delete("/delete-documents")
async def delete_documents(document_ids: List[str] = Query(...)): # Changed to Query for GET-like delete or use Body for proper DELETE
    deleted_ids = []
    errors = []
    for document_id in document_ids:
        try:
            doc_object_id = ObjectId(document_id)
            doc = collection.find_one({"_id": doc_object_id})
            if not doc:
                errors.append({"id": document_id, "error": "Document not found"})
                continue

            # Delete associated files (input PDF, output CSV)
            input_file_path = doc.get("file_path")
            if input_file_path and os.path.exists(input_file_path):
                try:
                    os.remove(input_file_path)
                except Exception as e:
                    errors.append({"id": document_id, "error": f"Could not delete input file {input_file_path}: {e}"})
            
            # Construct potential CSV output path based on your test_case_utils.CSV_OUTPUT_DIR
            # This assumes test_case_utils.CSV_OUTPUT_DIR is accessible or defined here
            # For robustness, this path should ideally be stored in the document metadata upon CSV creation
            csv_output_path = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{document_id}_test_cases.csv")
            if os.path.exists(csv_output_path):
                try:
                    os.remove(csv_output_path)
                except Exception as e:
                     errors.append({"id": document_id, "error": f"Could not delete output CSV file {csv_output_path}: {e}"})


            result = collection.delete_one({"_id": doc_object_id})
            if result.deleted_count > 0:
                deleted_ids.append(document_id)
            else: # Should not happen if find_one found it, but as a safeguard
                errors.append({"id": document_id, "error": "Document found but failed to delete from DB"})
        except InvalidId:
            errors.append({"id": document_id, "error": "Invalid document ID format"})
        except Exception as e:
            errors.append({"id": document_id, "error": str(e)})

    response_message = ""
    if deleted_ids:
        response_message += f"{len(deleted_ids)} document(s) deleted successfully: {', '.join(deleted_ids)}. "
    if errors:
        response_message += f"Errors occurred for some documents."
        return JSONResponse(
            content={"message": response_message, "deleted": deleted_ids, "errors": errors},
            status_code=status.HTTP_207_MULTI_STATUS if deleted_ids else status.HTTP_400_BAD_REQUEST ,
        )
    
    if not deleted_ids and not errors: # Should not happen if document_ids is not empty
        return JSONResponse(content={"message": "No documents specified for deletion."}, status_code=status.HTTP_400_BAD_REQUEST)

    return JSONResponse(
        content={"message": response_message, "deleted": deleted_ids},
        status_code=status.HTTP_200_OK,
    )


router = APIRouter()


@router.get("/get-test-cases/{document_id}")
def get_test_cases_as_json(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
        
    doc = collection.find_one({"_id": doc_object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_status = doc.get("status")
    if doc_status == 0: # Processing
        progress = doc.get("progress", []) # Assuming 'progress' is updated by Celery task
        last_progress = progress[-1] if progress else "Processing test cases..."
        return {
            "status_code": doc_status,
            "status_message": "processing",
            "detail": last_progress,
            "progress_log": progress,
        }
    elif doc_status == -1: # Not processed yet
        return {
            "status_code": doc_status,
            "status_message": "pending_generation",
            "detail": "Test case generation has not been initiated for this document."
        }
    elif doc_status == 1: # Completed
        try:
            # This will parse the test cases from the document's 'test_cases' field
            _, rows = test_case_utils.parse_test_cases_to_csv(
                document_id, collection
            )
            return {"status_code": doc_status, "status_message": "ready", "document_id": document_id, "test_cases": rows}
        except HTTPException as e: # Catch specific HTTPExceptions from parse_test_cases_to_csv
            raise e
        except Exception as e:
            print(f"Error parsing test cases in get_test_cases_as_json for doc {document_id}: {e}")
            # Check if 'test_cases' field even exists or is empty
            if not doc.get("test_cases"):
                raise HTTPException(status_code=404, detail=f"No 'test_cases' data found in completed document {document_id}. Generation might have failed to save results.")
            raise HTTPException(status_code=500, detail=f"Failed to parse test cases from document: {str(e)}")

    elif doc_status == 2: # Error state
        error_info = doc.get("error_info", "An unspecified error occurred during processing.")
        return {
            "status_code": doc_status,
            "status_message": "error",
            "detail": f"Test case generation failed for this document. Error: {error_info}"
        }
    else: # Unknown status
        return {
            "status_code": doc_status,
            "status_message": "unknown",
            "detail": f"Document is in an unknown state (status: {doc_status})."
        }


# >>>>>>>>>>>>>>>>>>>>> NEW ENDPOINT START <<<<<<<<<<<<<<<<<<<<<<<
@router.get("/test-case-summary/{document_id}")
async def get_test_case_summary(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
        )

    doc = collection.find_one({"_id": doc_object_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    doc_status = doc.get("status")
    if doc_status == -1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test case generation has not been initiated for this document. Summary not available."
        )
    if doc_status == 0:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Test case generation is still in progress. Summary will be available once completed."
        )
    if doc_status == 2: # Error state
        error_info = doc.get("error_info", "Processing failed.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Test case generation failed for this document: {error_info}. Summary not available."
        )
    if doc_status != 1: # Any other non-completed status
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document status is '{doc_status}'. Summary is only available for completed generations."
        )

    # If status is 1 (completed), proceed to parse and summarize
    try:
        # We don't need the csv_path here, only the rows (parsed test cases)
        _, parsed_test_cases = test_case_utils.parse_test_cases_to_csv(document_id, collection)
    except HTTPException as e:
        # If parse_test_cases_to_csv itself raises an HTTPException (e.g., no test cases found in doc)
        raise e
    except Exception as e:
        # Log this unexpected error during parsing for summary
        print(f"Error parsing test cases for summary (doc_id: {document_id}): {e}")
        raise HTTPException(status_code=500, detail="Error processing test cases for summary.")

    if not parsed_test_cases:
        return {
            "document_id": document_id,
            "counts_by_type": {},
            "total_test_cases": 0,
            "message": "No test cases were parsed from this document, although it's marked as completed."
        }

    test_type_counts = Counter()
    for tc in parsed_test_cases:
        # The key "Test type" comes from your CSV_HEADERS in test_case_utils.py
        test_type = tc.get("Test type", "Unknown")  # Default to "Unknown" if key is missing
        if test_type == "N/A" or not test_type.strip(): # Handle "N/A" or empty strings
            test_type = "Not Specified"
        test_type_counts[test_type] += 1
    
    total_test_cases = len(parsed_test_cases)
        
    return {
        "document_id": document_id,
        "counts_by_type": dict(test_type_counts), # Convert Counter to dict for JSON response
        "total_test_cases": total_test_cases
    }
# >>>>>>>>>>>>>>>>>>>>> NEW ENDPOINT END <<<<<<<<<<<<<<<<<<<<<<<<<


app.include_router(router)


@app.get("/download-csv/{document_id}")
def download_test_cases_csv(document_id: str):
    try:
        doc_object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    doc = collection.find_one({"_id": doc_object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_status = doc.get("status")
    if doc_status != 1:
        status_message = "not completed"
        if doc_status == 0: status_message = "still processing"
        elif doc_status == -1: status_message = "generation not started"
        elif doc_status == 2: status_message = f"failed ({doc.get('error_info', 'unknown error')})"
        raise HTTPException(status_code=409, detail=f"Cannot download CSV. Test case generation is {status_message}.")


    original_file_name = doc.get("file_name", "document.pdf")

    try:
        csv_path, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
    except HTTPException as e: # Catch specific errors from parsing, e.g. no test cases
        raise e
    except Exception as e:
        print(f"Error generating CSV for download (doc_id: {document_id}): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV file: {str(e)}")

    if not os.path.exists(csv_path):
        # This case should ideally be caught by parse_test_cases_to_csv if no TCs found
        raise HTTPException(status_code=404, detail=f"CSV file not found at {csv_path}. Parsing might have failed or produced no data.")

    csv_file_name = f"{Path(original_file_name).stem}_test_cases.csv"

    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename=csv_file_name,
    )


@app.get("/api_key_usage/{api_key}") # Consider making this POST if API key is sensitive
def get_api_key_cost(api_key: str):
    # For security, avoid exposing full API keys in GET requests if possible.
    # If this is for admin use, ensure proper auth.
    # A hashed version or an internal ID for the key might be safer if user-facing.
    record = cost_collection.find_one({"api_key_suffix": api_key[-5:]}) # Example: query by suffix
    if not record:
         # If querying by full key:
        record = cost_collection.find_one({"api_key": api_key})
        if not record:
            return {"api_key_identifier": api_key[-5:], "tokens_used": 0, "cost_usd": 0.0, "message": "No usage data found for this API key identifier."}
    
    return {
        "api_key_identifier": record.get("api_key_suffix", api_key[-5:]),
        "tokens_used": record.get("tokens_used", 0),
        "cost_usd": round(record.get("cost_usd", 0.0), 6), # Increased precision
        "last_updated": record.get("last_updated", "N/A") # Added last_updated
    }

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

if not SECRET_KEY:
    print(
        "WARNING: SECRET_KEY environment variable is not set. JWT authentication for WebSockets will fail."
    )

@app.websocket("/ws/task_status/{task_id}")
async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
    token = websocket.query_params.get("token")

    if not SECRET_KEY:
        await websocket.accept()
        await websocket.send_json(
            {"status": "error", "message": "Server configuration error: JWT secret not set."}
        )
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    if not token:
        await websocket.accept()
        await websocket.send_json(
            {"status": "error", "message": "Authentication token missing."}
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    username = None # Initialize username
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            await websocket.accept()
            await websocket.send_json(
                {"status": "error", "message": "Invalid token: Subject missing."}
            )
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError as e:
        await websocket.accept()
        await websocket.send_json(
            {"status": "error", "message": f"Authentication failed: {str(e)}"}
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except ImportError:
        await websocket.accept()
        await websocket.send_json(
            {"status": "error", "message": "Server configuration error: JWT library not available."}
        )
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return


    await websocket.accept()
    # Log WebSocket connection
    print(f"WebSocket connected for task {task_id}, user: {username}")
    await websocket.send_json(
        {
            "status": "connected",
            "message": f"Authenticated as {username}. Monitoring task {task_id}.",
        }
    )

    task_monitor = AsyncResult(task_id)
    try:
        while True:
            if websocket.client_state != WebSocketState.CONNECTED:
                print(f"WebSocket for task {task_id} (User: {username}) disconnected by client.")
                break

            task_state = task_monitor.state
            # Fetch the latest document status from DB for more context
            doc_db_info = collection.find_one({"last_task_id": task_id}, {"status": 1, "progress": 1, "error_info": 1})
            db_status = doc_db_info.get("status") if doc_db_info else None
            
            response_data = {"task_id": task_id, "celery_status": task_state, "db_doc_status": db_status}

            if task_state == "PENDING":
                response_data["info"] = "Task is waiting to be processed by a worker."
            elif task_state == "STARTED":
                response_data["info"] = "Task has been picked up by a worker and started."
            elif task_state == "PROGRESS":
                response_data["info"] = "Task is in progress."
                # Celery task must use self.update_state(state='PROGRESS', meta={'current': i, 'total': n, 'status': 'details'})
                response_data["progress_details"] = task_monitor.info 
                if doc_db_info and "progress" in doc_db_info:
                     response_data["db_progress_log"] = doc_db_info["progress"]
            elif task_state == "SUCCESS":
                response_data["info"] = "Task completed successfully."
                response_data["result"] = task_monitor.result # Result from Celery task return
                await websocket.send_json(response_data)
                break 
            elif task_state == "FAILURE":
                response_data["info"] = "Task failed."
                response_data["error_details"] = str(task_monitor.info) # Exception info from Celery
                if doc_db_info and "error_info" in doc_db_info:
                    response_data["db_error_info"] = doc_db_info["error_info"]
                await websocket.send_json(response_data)
                break
            elif task_state == "RETRY":
                response_data["info"] = "Task is being retried."
                response_data["retry_reason"] = str(task_monitor.info)

            await websocket.send_json(response_data)

            if task_monitor.ready(): # Task is definitively finished (SUCCESS, FAILURE)
                # Ensure final state is sent if loop condition missed it for some reason
                if task_state not in ["SUCCESS", "FAILURE"]:
                    final_state = task_monitor.state
                    final_response = {"task_id": task_id, "celery_status": final_state, "info": "Task reached final state."}
                    if final_state == "SUCCESS": final_response["result"] = task_monitor.result
                    elif final_state == "FAILURE": final_response["error_details"] = str(task_monitor.info)
                    await websocket.send_json(final_response)
                break
            
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print(f"Client {username} (task: {task_id}) disconnected gracefully.")
    except Exception as e:
        print(
            f"Unexpected error in WebSocket for task {task_id} (User: {username}): {type(e).__name__} - {e}"
        )
        import traceback
        traceback.print_exc()
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(
                    {"status": "error", "message": "An unexpected server error occurred while monitoring the task."}
                )
            except Exception as send_err:
                 print(f"Error sending WebSocket error message: {send_err}")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close(code=status.WS_1001_GOING_AWAY)
            except RuntimeError: # Already closed
                pass
        print(f"WebSocket connection for task {task_id} (User: {username}) definitively closed.")


class TokenRequest(BaseModel):
    username: str
    password: str # In a real app, never log passwords or send them around more than necessary


@app.post("/get_token", tags=["Authentication"])
async def get_token_post(request: TokenRequest):
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required",
        )

    # IMPORTANT: Replace with real DB/user authentication and password hashing
    # DO NOT use plain text password comparison in production. Use something like passlib.
    if request.username == os.getenv("ADMIN_USERNAME", "admin") and \
       request.password == os.getenv("ADMIN_PASSWORD", "admin123"): # Load credentials from env
        
        token_data = {"sub": request.username, "role": "admin"} # Add role or other claims
        try:
            if not SECRET_KEY:
                 raise ValueError("JWT_SECRET_KEY is not configured on the server.")
            token = create_jwt_token(token_data) # Assuming create_jwt_token uses SECRET_KEY and ALGORITHM
            return {"access_token": token, "token_type": "bearer"}
        except Exception as e:
            print(f"Error generating token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate token due to server error.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
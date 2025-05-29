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


# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
from utils import test_case_utils
from core.websocket import websocket_endpoint


mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]
cost_collection = db["cost_tracking"]


def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return {
        # "_id": str(doc["_id"]),
        "file_name": doc.get("file_name"),
        "status": doc.get("status"),
    }


# ----------------- Directories Setup -----------------
TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
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


VALID_TEST_CASE_TYPES = [
    "functional",
    "non-functional",
    "security",
    "performance",
    "boundary",
    "compliance",
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

    # Insert file metadata into MongoDB
    document_data = {
        "file_name": file_name,
        "file_path": str(file_path),
        "status": -1,  # Document uploaded but not processed
    }

    result = collection.insert_one(document_data)
    file_id = str(result.inserted_id)

    return {
        "message": "File uploaded successfully",
        "file_name": file_name,
        "file_path": str(file_path),
        "file_id": file_id,
    }


@app.post("/generate_test_cases/")
async def generate_test_cases(
    file_id: str = Form(...),
    model_name: Optional[str] = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form("all"),
):
    # Fetch document from MongoDB
    try:
        document = collection.find_one({"_id": ObjectId(file_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id format.")

    if not document:
        raise HTTPException(
            status_code=404, detail="Document not found in the database."
        )

    file_path = Path(document.get("file_path"))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")

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

    # ✅ Set initial status = 0 (processing)
    collection.update_one(
        {"_id": ObjectId(file_id)},
        {
            "$set": {
                "status": 0,
                "selected_model": model_name,
                "api_key_used": f"...{api_key_to_use[-5:]}",
            }
        },
    )

    # Trigger Celery task with document_id
    task = process_and_generate_task.delay(
        str(file_path),
        model_name,
        chunk_size,
        api_key_to_use,
        test_case_types_list,
        file_id,  # this is used as document_id inside celery
    )

    collection.update_one(
        {"_id": ObjectId(file_id)}, {"$set": {"last_task_id": task.id}}
    )

    return {
        "message": "✅ Test case generation task started.",
        "task_id": task.id,
        "file_id": file_id,
        "test_case_types": test_case_types_list,
        "api_key_being_used": f"...{api_key_to_use[-5:]}",
        "warning": warning,
    }


# ----------------- MongoDB Fetch Endpoints -----------------
@app.get("/documents/")
def get_all_documents():
    documents = list(collection.find())
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


# ----------------- Show Test Cases-----------------
router = APIRouter()


@router.get("/get-test-cases/{document_id}")
def get_test_cases_as_json(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("status") == 0:
            # Still processing: return progress so far
            progress = doc.get("progress", [])
            last_progress = progress[-1] if progress else "Processing test cases..."
            return {
                "status": "processing",
                "message": last_progress,
                "progress": progress,
            }

        # status == 1 means done, return final test cases
        csv_path, rows = test_case_utils.parse_test_cases_to_csv(
            document_id, collection
        )
        return {"status": "ready", "document_id": document_id, "test_cases": rows}

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        print(f"Error in get_test_cases_as_json: {e}")
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)


@app.get("/download-csv/{document_id}")
def download_test_cases_csv(document_id: str):
    try:
        # Fetch the original document from DB to get the original file name
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        original_file_name = doc.get("file_name", "document.pdf")  # fallback name

        # Generate CSV path and parse test cases (your existing logic)
        csv_path, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)

        # Create a user-friendly CSV filename based on original PDF name
        csv_file_name = f"{Path(original_file_name).stem}_test_cases.csv"

        return FileResponse(
            csv_path,
            media_type="text/csv",
            filename=csv_file_name,
        )
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api_key_usage/{api_key}")
def get_api_key_cost(api_key: str):
    record = cost_collection.find_one({"api_key": api_key})
    if not record:
        return {"tokens_used": 0, "cost_usd": 0.0}
    return {
        "tokens_used": record.get("tokens_used", 0),
        "cost_usd": round(record.get("cost_usd", 0.0), 4),
    }


# @app.websocket("/ws/task_status")
# async def websocket_task_status(websocket: WebSocket, task_id: str = Query(...)):
#     await websocket_endpoint(websocket, task_id)


# JWT Configuration (should match what create_jwt_token uses)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"  # Ensure this matches the algorithm in create_jwt_token

if not SECRET_KEY:
    print(
        "WARNING: SECRET_KEY environment variable is not set. JWT authentication for WebSockets will fail."
    )
    # raise ValueError("SECRET_KEY environment variable is required for JWT.") # Or handle more gracefully


@app.websocket("/ws/task_status/{task_id}")
async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
    token = websocket.query_params.get("token")

    if (
        not SECRET_KEY
    ):  # Should be checked at startup, but good to have a runtime check for WS
        await websocket.accept()  # Accept to send an error, then close
        await websocket.send_json(
            {
                "status": "error",
                "message": "Server configuration error: JWT secret not set.",
            }
        )
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    if not token:
        # Optionally, accept and send an error message before closing
        await websocket.accept()
        await websocket.send_json(
            {"status": "error", "message": "Authentication token missing."}
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        from jose import jwt, JWTError

        # Moved import here to ensure SECRET_KEY check happens first

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
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

    await websocket.accept()
    await websocket.send_json(
        {
            "status": "connected",
            "message": f"Authenticated as {username}. Monitoring task {task_id}.",
        }
    )

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
                response_data["progress"] = (
                    task_monitor.info
                )  # Celery task must use self.update_state(meta=...)
            elif task_state == "SUCCESS":
                response_data["result"] = task_monitor.result
                await websocket.send_json(response_data)
                break  # Task finished
            elif task_state == "FAILURE":
                response_data["error"] = str(task_monitor.info)  # Exception info
                await websocket.send_json(response_data)
                break  # Task finished
            elif task_state == "RETRY":
                response_data["info"] = "Task is being retried."
                response_data["error"] = str(task_monitor.info)

            await websocket.send_json(response_data)

            if (
                task_monitor.ready()
            ):  # Final check if task is completed (SUCCESS, FAILURE)
                # Ensure final state is sent if loop condition missed it
                if task_state not in [
                    "SUCCESS",
                    "FAILURE",
                ]:  # e.g. if it became ready between state check and send
                    final_state = task_monitor.state
                    final_response = {"task_id": task_id, "status": final_state}
                    if final_state == "SUCCESS":
                        final_response["result"] = task_monitor.result
                    elif final_state == "FAILURE":
                        final_response["error"] = str(task_monitor.info)
                    await websocket.send_json(final_response)
                break

            await asyncio.sleep(2)  # Poll Celery every 2 seconds

    except WebSocketDisconnect:
        print(f"Client {username} (task: {task_id}) disconnected.")
    except Exception as e:
        print(
            f"Unexpected error in WebSocket for task {task_id} (User: {username}): {type(e).__name__} - {e}"
        )
        import traceback

        traceback.print_exc()

        # Only attempt to send error if the socket is still connected
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(
                    {
                        "status": "error",
                        "message": "An unexpected error occurred on the server.",
                    }
                )
            except Exception:
                pass  # Avoid crashing if socket is already closed

    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close(code=status.WS_1001_GOING_AWAY)
            except RuntimeError:
                pass  # WebSocket is already closed
        print(
            f"WebSocket connection for task {task_id} (User: {username}) definitively closed."
        )


# --- JWT Token Generation Endpoints ---
# It's good practice to have POST for actions that might create/retrieve sensitive data like tokens
class TokenRequest(BaseModel):
    username: str
    password: str


@app.post("/get_token", tags=["Authentication"])
async def get_token_post(request: TokenRequest):
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required",
        )

    # Simulated credential check - replace with real DB/user auth
    if request.username != "admin" or request.password != "admin123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token_data = {"sub": request.username}
    try:
        token = create_jwt_token(token_data)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error generating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate token.",
        )

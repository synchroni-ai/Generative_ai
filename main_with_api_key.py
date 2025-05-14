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
)
from fastapi.responses import JSONResponse, FileResponse
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
import csv
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
cost_collection = db["cost_tracking"]


def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc


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


@app.post("/process_and_generate/")
async def process_and_generate(
    file: UploadFile = File(...),
    model_name: str = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
    api_key: Optional[str] = Form(None),
    test_case_types: List[str] = Query(["functional"]),  # Changed to Query
):
    # Validate test_case_type
    valid_test_case_types = [
        "functional",
        "non-functional",
        "security",
        "performance",
        "boundary",
        "compliance",
    ]
    for test_case_type in test_case_types:
        if test_case_type not in valid_test_case_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid test_case_type: {test_case_type}. Must be one of {valid_test_case_types}",
            )

    # Use default if user key not provided
    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")

    if not api_key:
        warning = (
            "Using default API key. Consider providing your own to avoid shared limits."
        )
    else:
        warning = None

    file_name = file.filename
    file_path = Path(INPUT_DIR) / file_name

    # Save the uploaded file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    finally:
        await file.close()

    task_results: Dict[str, AsyncResult] = {}  # Store task result objects
    all_task_ids = {}

    # Store the MongoDB Document to store all the objects
    document = {
        "doc_name": os.path.basename(file_path),
        "doc_path": str(file_path),
        "selected_model": model_name,
        "all_llm_responses_testcases": {},
        "llm_response_testcases": "",
        "api_key_used": f"...{api_key_to_use[-5:]}",
        "test_case_types": test_case_types,
    }
    # Insert the document into MongoDB
    try:
        result = collection.insert_one(document)
        document_id = result.inserted_id  # Get the inserted document's _id
    except Exception as e:
        print("MongoDB Insertion Error:", str(e))
        raise HTTPException(status_code=500, detail=f"MongoDB Insertion Error: {e}")

    # Launch all tasks
    for test_case_type in test_case_types:
        task = process_and_generate_task.delay(
            str(file_path),
            model_name,
            chunk_size,
            api_key_to_use,
            test_case_type,
        )
        task_results[test_case_type] = task
        all_task_ids[test_case_type] = task.id

    # Wait for all tasks to complete
    results = {}
    all_test_cases = {}

    for test_case_type, task in task_results.items():
        results[test_case_type] = task.get()  # This will block until task is complete
        all_test_cases[test_case_type] = results[test_case_type]["test_cases"]

    # Construct the combined document
    combined_test_cases = "\n".join(
        [f"--- {k} ---\n{v}" for k, v in all_test_cases.items()]
    )

    # Update MongoDB with results using the ObjectId
    try:
        collection.update_one(
            {"_id": document_id},  # Use the ObjectId to identify the document
            {
                "$set": {
                    "all_llm_responses_testcases": all_test_cases,
                    "llm_response_testcases": combined_test_cases,
                }
            },
        )
    except Exception as e:
        print("MongoDB Update Error:", str(e))
        raise HTTPException(status_code=500, detail=f"MongoDB Update Error: {e}")

    # --------------- Generate CSV files -----------------
    # Find document in MongoDB
    document = collection.find_one({"_id": document_id})  # Find document in mongo db
    if not document:
        raise HTTPException(
            status_code=404, detail=f"Document with ID {document_id} not found"
        )
    # # Generate CSV files from direct LLM output
    # csv_files = {}  # Add all paths to csv files
    # all_llm_responses_testcases = document.get("all_llm_responses_testcases")
    # for (
    #     test_case_type,
    #     llm_response_testcases,
    # ) in (
    #     all_llm_responses_testcases.items()
    # ):  # Add to the CSV files based on each object
    #     csv_file_path = os.path.join(OUTPUT_DIR, f"{test_case_type}_test_cases.csv")
    #     # format_test_cases_csv
    #     # Generate CSV files from direct LLM output
    #     test_case_utils.text_to_csv(llm_response_testcases, csv_file_path)
    #     csv_files[test_case_type] = csv_file_path

    return {
        "message": "File uploaded successfully. Processing started.",
        "task_ids": all_task_ids,
        "api_key_being_used": f"...{api_key_to_use[-5:]}",
        "warning": warning,
        "test_case_types": test_case_types,
        # "csv_files": csv_files,  # Return CSV file paths
    }


@app.get("/download-csv/{document_id}")
def download_test_cases_csv(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        test_cases_dict = doc.get("all_llm_responses_testcases")
        if not test_cases_dict:
            raise HTTPException(
                status_code=404, detail="No test cases found in document"
            )

        # Define the CSV output path
        csv_output_path = os.path.join(
            EXCEL_OUTPUT_DIR, f"{document_id}_test_cases.csv"
        )

        # ✅ START replacement here
        csv_headers = [
            "Test Case ID",
            "Test Type",
            "Title",
            "Description",
            "Precondition",
            "Steps",
            "Action",
            "Data",
            "Result",
            "Type (P / N / in)",
            "Test Priority",
        ]

        with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()

            for test_case_type, test_case_content in test_cases_dict.items():
                for block in test_case_content.split("---"):
                    block = block.strip()
                    if not block:
                        continue

                    tc_id = title = desc = steps = expected = ""
                    precondition = ""
                    action = ""
                    data = ""
                    result = ""
                    type = ""
                    test_priority = ""
                    collecting_steps = False
                    collecting_steps = False

                    for line in block.splitlines():
                        line = line.strip()
                        if line.startswith("TCID:"):
                            tc_id = line.replace("TCID:", "").strip()
                        elif line.startswith("Test Type:"):
                            test_case_type = line.replace("Test Type:", "").strip()
                        elif line.startswith("Title:"):
                            title = line.replace("Title:", "").strip()
                        elif line.startswith("Description:"):
                            desc = line.replace("Description:", "").strip()
                        elif line.startswith("Precondition:"):
                            precondition = line.replace("Precondition:", "").strip()
                        elif line.startswith("Steps:"):
                            collecting_steps = True
                        elif line.startswith("Action:"):
                            action = True
                        elif line.startswith("Data:"):
                            data = True
                        elif line.startswith("Result:"):
                            result = line.replace("Result:", "").strip()
                        elif line.startswith("Type (P /N /in):"):
                            type = line.replace("Type (P /N /in)", "").strip()
                        elif line.startswith("Test Priority:"):
                            test_priority = line.replace("Test Priority:", "").strip()
                            collecting_steps = False
                        elif collecting_steps and line:
                            steps += line + "\n"

                    writer.writerow(
                        {
                            "Test Case ID": tc_id,
                            "Test Type": test_case_type,
                            "Title": title,
                            "Description": desc,
                            "Precondition": precondition,
                            "Steps": steps.strip(),
                            "Action": action,
                            "Data": data,
                            "Result": result,
                            "Type (P / N / in)": type,
                            "Test Priority": test_priority,
                        }
                    )
        # ✅ END replacement here

        return FileResponse(
            csv_output_path,
            media_type="text/csv",
            filename=f"{document_id}_test_cases.csv",
        )

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    if task.state == "SUCCESS":
        return {"status": "Completed", "result": task.result}
    elif task.state == "FAILURE":
        return {"status": "Failed", "error": str(task.info)}


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


# ----------------- New Endpoint for CSV Download -----------------
@app.get("/download/csv/{document_id}/{test_case_type}")
async def download_test_cases_csv(document_id: str, test_case_type: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        csv_files = doc.get("csv_files", {})  # Get all files
        csv_path = csv_files.get(test_case_type)  # get the correct path

        if not csv_path or not os.path.exists(csv_path):
            raise HTTPException(
                status_code=404, detail="CSV file not found for this test case type"
            )

        return FileResponse(
            csv_path,
            media_type="text/csv",
            filename=f"{test_case_type}_test_cases.csv",  # Desired name
        )
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
# @app.get("/download/testcases/{document_id}")
# def download_test_cases_excel(document_id: str):
#     try:
#         doc = collection.find_one({"_id": ObjectId(document_id)})
#         if not doc or "test_case_excel_path" not in doc:
#             raise HTTPException(
#                 status_code=404, detail="Excel file not found for test cases"
#             )
#         return FileResponse(
#             doc["test_case_excel_path"],
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             filename=Path(doc["test_case_excel_path"]).name,
#         )
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid document ID format")


# @app.get("/download/userstories/{document_id}")
# def download_user_stories_excel(document_id: str):
#     try:
#         doc = collection.find_one({"_id": ObjectId(document_id)})
#         if not doc or "user_story_excel_path" not in doc:
#             raise HTTPException(
#                 status_code=404, detail="Excel file not found for user stories"
#             )
#         return FileResponse(
#             doc["user_story_excel_path"],
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             filename=Path(doc["user_story_excel_path"]).name,
#         )
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid document ID format")


@app.get("/api_key_usage/{api_key}")
def get_api_key_cost(api_key: str):
    record = cost_collection.find_one({"api_key": api_key})
    if not record:
        return {"tokens_used": 0, "cost_usd": 0.0}
    return {
        "tokens_used": record.get("tokens_used", 0),
        "cost_usd": round(record.get("cost_usd", 0.0), 4),
    }


@app.websocket("/ws/task_status")
async def websocket_task_status(websocket: WebSocket, task_id: str = Query(...)):
    await websocket_endpoint(websocket, task_id)

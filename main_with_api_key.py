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
import uuid
import pandas as pd
from openpyxl import load_workbook
import csv

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
    test_case_types: str = Form("functional"),  # Accept comma-separated string
):
    # Convert comma-separated test_case_types to a list
    test_case_types_list = [t.strip() for t in test_case_types.split(",")]
 
    # Validate test_case_types
    valid_test_case_types = [
        "functional",
        "non-functional",
        "security",
        "performance",
        "boundary",
        "compliance",
    ]
    for test_case_type in test_case_types_list:
        if test_case_type not in valid_test_case_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid test_case_type: {test_case_type}. Must be one of {valid_test_case_types}",
            )
 
    # Use default if user key not provided
    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
    warning = (
        "Using default API key. Consider providing your own to avoid shared limits."
        if not api_key
        else None
    )
 
    file_name = file.filename
    file_path = Path(INPUT_DIR) / file_name
 
    # Save the uploaded file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    finally:
        await file.close()
 
    task_results: Dict[str, AsyncResult] = {}
    all_task_ids = {}
 
    # Launch Celery tasks
    for test_case_type in test_case_types_list:
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
    all_excel_paths = {}
    for test_case_type, task in task_results.items():
        results[test_case_type] = task.get()  # Blocking wait
        all_test_cases[test_case_type] = results[test_case_type]["test_cases"]
        all_excel_paths[test_case_type] = results[test_case_type]["excel_path"]
 
    # Combine test case strings
    combined_test_cases = "\n".join(
        [f"--- {k} ---\n{v}" for k, v in all_test_cases.items()]
    )
 
    # Use the Excel path from the first test case type
    excel_test_case_path = all_excel_paths[test_case_types_list[0]]
 
    # MongoDB document
    document = {
        "doc_name": os.path.basename(file_path),
        "doc_path": str(file_path),
        "test_case_excel_path": excel_test_case_path,
        "selected_model": model_name,
        "all_llm_responses_testcases": all_test_cases,
        "llm_response_testcases": combined_test_cases,
        "api_key_used": f"...{api_key_to_use[-5:]}",
        "test_case_types": test_case_types_list,
    }
 
    try:
        collection.insert_one(document)
    except Exception as e:
        print("MongoDB Insertion Error:", str(e))
 
    return {
        "message": "File uploaded successfully. Processing started.",
        "task_ids": all_task_ids,
        "api_key_being_used": f"...{api_key_to_use[-5:]}",
        "warning": warning,
        "test_case_types": test_case_types_list,
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

@app.get("/download-csv/{document_id}")
def download_test_cases_csv(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        test_cases_dict = doc.get("all_llm_responses_testcases")
        if not test_cases_dict:
            raise HTTPException(status_code=404, detail="No test cases found in document")

        csv_output_path = os.path.join(EXCEL_OUTPUT_DIR, f"{document_id}_test_cases.csv")
        
        # MODIFICATION 1: Remove "Expected Result" from headers
        csv_headers = [
            "TCID", "Test type", "Title", "Description", "Precondition",
            "Steps", "Action", "Data", "Result", "Type (P / N / in)",
            "Test priority" # "Expected Result" removed
        ]

        with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers, quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for test_case_type_key, test_case_content_for_type in test_cases_dict.items():
                content_str = str(test_case_content_for_type).strip()
                if not content_str:
                    continue

                current_content_lines = content_str.splitlines()
                if current_content_lines and \
                   current_content_lines[0].strip().startswith("---") and \
                   current_content_lines[0].strip().endswith("---"):
                    current_content_lines.pop(0)
                while current_content_lines and not current_content_lines[0].strip():
                    current_content_lines.pop(0)
                if current_content_lines and \
                   current_content_lines[0].strip().lower() == "test cases:":
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
                            individual_tc_blocks = processed_blocks[1:]
                        else:
                            individual_tc_blocks = processed_blocks
                
                if not individual_tc_blocks and content_to_split:
                    if re.match(r'^(?:\*\*(?:TC|PTC)_\d+\*\*|TCID:|Test Case ID:)', content_to_split.lstrip(), re.IGNORECASE):
                        individual_tc_blocks.append(content_to_split)
                    else:
                        continue

                for block_index, block in enumerate(individual_tc_blocks):
                    # Initialize fields only with current headers
                    fields = {header: "N/A" for header in csv_headers}
                    fields["Test type"] = test_case_type_key 

                    collecting_steps = False
                    current_steps_list = []
                    lines_in_block = block.splitlines()
                    
                    first_line_processed_for_tcid = False
                    if lines_in_block:
                        first_line_stripped = lines_in_block[0].strip()
                        tcid_standalone_match = re.match(r'^\*\*((?:TC|PTC)_\d+)\*\*\s*$', first_line_stripped)
                        if tcid_standalone_match:
                            fields["TCID"] = tcid_standalone_match.group(1)
                            first_line_processed_for_tcid = True

                    for line_idx, line_content in enumerate(lines_in_block):
                        if first_line_processed_for_tcid and line_idx == 0:
                            continue
                        line = line_content.strip()
                        if not line: continue

                        key_value_match = re.match(r'^\**([^:]+):\**\s*(.*)', line)
                        
                        if key_value_match:
                            key = key_value_match.group(1).strip().lower()
                            value = key_value_match.group(2).strip()
                            collecting_steps = False 

                            if key == "tcid" or key == "test case id": fields["TCID"] = value
                            elif key == "test type" or key == "test case type": fields["Test type"] = value
                            elif key == "title": fields["Title"] = value
                            elif key == "description": fields["Description"] = value
                            elif key == "precondition": fields["Precondition"] = value
                            elif key == "action": fields["Action"] = value
                            elif key == "data": fields["Data"] = value
                            elif key == "result": fields["Result"] = value
                            elif key == "type (p / n / in)": fields["Type (P / N / in)"] = value
                            elif key == "test priority": fields["Test priority"] = value
                            # MODIFICATION 2: "expected result" parsing removed
                            # elif key == "expected result":
                            #     fields["Expected Result"] = value if value else "N/A" 
                            elif key == "steps":
                                collecting_steps = True
                                if value: current_steps_list.append(value)
                        elif collecting_steps:
                            current_steps_list.append(line) 
                    
                    fields["Steps"] = " ".join(current_steps_list).strip()
                    
                    for f_key in fields: 
                        if fields[f_key] == "": fields[f_key] = "N/A"
                    
                    writer.writerow(fields)

        return FileResponse(csv_output_path, media_type="text/csv", filename=f"{document_id}_test_cases.csv")

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        import traceback
        print(f"An error occurred: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
    
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

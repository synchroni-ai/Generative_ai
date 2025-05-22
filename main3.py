# from fastapi import BackgroundTasks, HTTPException
# from task_with_api_key import process_and_generate_task
# from celery.result import AsyncResult
# from fastapi import (
#     FastAPI,
#     UploadFile,
#     File,
#     HTTPException,
#     Form,
#     Query,
#     status,
#     WebSocket,
#     APIRouter,
#     WebSocketDisconnect,
# )
# from fastapi.responses import JSONResponse, FileResponse
# from utils.jwt_auth import (
#     create_jwt_token,
# )
# from pydantic import BaseModel

# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, List, Dict
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from bson import ObjectId
# from bson.errors import InvalidId
# from pathlib import Path
# import os
# import re
# import time
# import uuid
# import pandas as pd
# from openpyxl import load_workbook
# import csv
# import asyncio  # For WebSocket polling sleep
# from starlette.websockets import WebSocketState  # For checking WebSocket state
# from collections import Counter # <<<<<<<<<<<<<<<<<<<<<<<<<<<< ADDED IMPORT


# # Import your custom modules
# from utils import data_ingestion, test_case_utils, user_story_utils
# from utils.llms import Mistral, openai, llama
# # from utils import test_case_utils # Already imported above
# from core.websocket import websocket_endpoint # Assuming this exists and is correct
# from datetime import datetime,timezone
# from zoneinfo import ZoneInfo

# # Load environment variables from .env file
# load_dotenv() # Ensure .env is loaded if you haven't elsewhere

# mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# db = mongo_client["Gen_AI"]
# collection = db["test_case_generation"]
# cost_collection = db["cost_tracking"]


# def serialize_document(doc):
#     doc["_id"] = str(doc["_id"])
#     return {
#         # "_id": str(doc["_id"]),
#         "file_id": str(doc["_id"]),
#         "file_name": doc.get("file_name"),
#         "file_path": doc.get("file_path"),
#         "status": doc.get("status"),
#         "selected_model": doc.get("selected_model", None),
#         "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None, # Added timestamp serialization
#         "last_task_id": doc.get("last_task_id") # Added last_task_id
#     }
# IST = ZoneInfo("Asia/Kolkata")

# # ----------------- Directories Setup -----------------
# TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
# USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH") # This seems to be the same as above, check if intended
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

# # Create directories if they don't exist
# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# VALID_TEST_CASE_TYPES = [
#     "functional",
#     "non-functional",
#     "security",
#     "performance",
#     "boundary",
#     "compliance",
#     "all" # Added 'all' here as it's a valid input, though handled specially
# ]
# class DataSpaceCreate(BaseModel):
#     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
#     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# class DataSpaceResponse(BaseModel):
#     data_space_id: str
#     name: str
#     description: Optional[str]
#     created_at: datetime
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True # For Pydantic v2
# # --- New Router for Data Space Creation ---
# data_space_creation_router = APIRouter(prefix="/api/v1", tags=["Data Spaces"])

# @data_space_creation_router.post("/data-spaces/", response_model=DataSpaceResponse, status_code=status.HTTP_201_CREATED)
# async def create_new_data_space(data_space_input: DataSpaceCreate):
#     existing_space = data_spaces_collection.find_one({"name": data_space_input.name})
#     if existing_space:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_input.name}' already exists.")
#     current_time = datetime.now(IST)
#     ds_doc_data = data_space_input.dict()
#     ds_doc_data["created_at"] = current_time
#     insert_result = data_spaces_collection.insert_one(ds_doc_data)
#     created_doc = data_spaces_collection.find_one({"_id": insert_result.inserted_id})
#     if not created_doc:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data space post-creation.")
#     return DataSpaceResponse(data_space_id=str(created_doc["_id"]), **created_doc)

# app.include_router(data_space_creation_router)
# @app.post("/upload_document/")
# async def upload_document(file: UploadFile = File(...)):
#     file_name = file.filename
#     file_path = Path(INPUT_DIR) / file_name

#     try:
#         contents = await file.read()
#         with open(file_path, "wb") as f:
#             f.write(contents)
#     finally:
#         await file.close()
#     upload_time = datetime.now(IST)


#     # Insert file metadata into MongoDB
#     document_data = {
#         "file_name": file_name,
#         "file_path": str(file_path),
#         "status": -1,  # Document uploaded but not processed
#         "timestamp": upload_time
#     }

#     result = collection.insert_one(document_data)
#     file_id = str(result.inserted_id)

#     return {
#         "message": "File uploaded successfully",
#         "file_name": file_name,
#         "file_path": str(file_path),
#         "file_id": file_id,
#         "timestamp": upload_time.isoformat()
#     }


# @app.post("/generate_test_cases/")
# async def generate_test_cases(
#     file_id: str = Form(...),
#     model_name: Optional[str] = Form("Mistral"),
#     chunk_size: Optional[int] = Query(default=None),
#     cache_key: Optional[str] = Query(default=None),
#     api_key: Optional[str] = Form(None),
#     test_case_types: Optional[str] = Form("all"),  # ✅ Accepts 'all' or comma-separated string like "functional,security"
# ):
#     # ✅ Step 1: Fetch the document from MongoDB
#     try:
#         document = collection.find_one({"_id": ObjectId(file_id)})
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid file_id format.")
 
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found in the database.")
 
#     # ✅ Step 2: Ensure file path exists
#     file_path = Path(document.get("file_path"))
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found on disk.")
 
#     # ✅ Step 3: Parse and validate `test_case_types`
#     if test_case_types.strip().lower() == "all":
#         # If user requested all test cases, set full list
#         test_case_types_to_send = "all"
#         test_case_types_list = VALID_TEST_CASE_TYPES
#     else:
#         # ✅ Split and validate comma-separated input
#         test_case_types_list = [t.strip().lower() for t in test_case_types.split(",")]
 
#         # ✅ Check for any invalid test case types
#         invalid_types = [t for t in test_case_types_list if t not in VALID_TEST_CASE_TYPES]
#         if invalid_types:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid test_case_type(s): {invalid_types}. Must be one of {VALID_TEST_CASE_TYPES} or 'all'.",
#             )
 
#         # ✅ Convert back to comma-separated string for Celery compatibility
#         test_case_types_to_send = ",".join(test_case_types_list)
 
#     # ✅ Step 4: Fallback to default API key if user hasn't supplied one
#     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
#     warning = (
#         "Using default API key. Consider providing your own to avoid shared limits."
#         if not api_key else None
#     )
 
#     # ✅ Step 5: Set status = 0 (processing) in MongoDB
#     collection.update_one(
#         {"_id": ObjectId(file_id)},
#         {
#             "$set": {
#                 "status": 0,
#                 "selected_model": model_name,
#                 "api_key_used": f"...{api_key_to_use[-5:]}",  # Mask key
#             }
#         },
#     )
 
#     # ✅ Step 6: Trigger Celery task (passes either "all" or comma-separated string)
#     task = process_and_generate_task.apply_async(args=[
#         str(file_path),             # file_path
#         model_name,                 # model_name
#         chunk_size,                 # chunk_size
#         api_key_to_use,             # api_key
#         test_case_types_to_send,    # "all" or "functional,security"
#         file_id,                    # document_id
#     ])
 
#     # ✅ Save task ID to DB for tracking
#     collection.update_one(
#         {"_id": ObjectId(file_id)}, {"$set": {"last_task_id": task.id}}
#     )
 
#     # ✅ Step 7: Return response
#     return {
#         "message": "✅ Test case generation task started.",
#         "task_id": task.id,
#         "file_id": file_id,
#         "test_case_types": test_case_types_list,  # Return list even if user passed 'all'
#         "api_key_being_used": f"...{api_key_to_use[-5:]}",
#         "warning": warning,
#     }
 
 


# @app.get("/documents/")
# def get_all_documents():
#     # Sort by timestamp descending to get newest first
#     documents = list(collection.find().sort("timestamp", -1))
#     return [serialize_document(doc) for doc in documents]


# @app.get("/documents/{document_id}")
# def get_document_by_id(document_id: str):
#     try:
#         doc_object_id = ObjectId(document_id)
#     except InvalidId:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
#         )

#     doc = collection.find_one({"_id": doc_object_id})
#     if not doc:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
#         )
#     return serialize_document(doc)


# @app.delete("/delete-documents")
# async def delete_documents(document_ids: List[str] = Query(...)): # Changed to Query for GET-like delete or use Body for proper DELETE
#     deleted_ids = []
#     errors = []
#     for document_id in document_ids:
#         try:
#             doc_object_id = ObjectId(document_id)
#             doc = collection.find_one({"_id": doc_object_id})
#             if not doc:
#                 errors.append({"id": document_id, "error": "Document not found"})
#                 continue

#             # Delete associated files (input PDF, output CSV)
#             input_file_path = doc.get("file_path")
#             if input_file_path and os.path.exists(input_file_path):
#                 try:
#                     os.remove(input_file_path)
#                 except Exception as e:
#                     errors.append({"id": document_id, "error": f"Could not delete input file {input_file_path}: {e}"})
            
#             # Construct potential CSV output path based on your test_case_utils.CSV_OUTPUT_DIR
#             # This assumes test_case_utils.CSV_OUTPUT_DIR is accessible or defined here
#             # For robustness, this path should ideally be stored in the document metadata upon CSV creation
#             csv_output_path = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{document_id}_test_cases.csv")
#             if os.path.exists(csv_output_path):
#                 try:
#                     os.remove(csv_output_path)
#                 except Exception as e:
#                      errors.append({"id": document_id, "error": f"Could not delete output CSV file {csv_output_path}: {e}"})


#             result = collection.delete_one({"_id": doc_object_id})
#             if result.deleted_count > 0:
#                 deleted_ids.append(document_id)
#             else: # Should not happen if find_one found it, but as a safeguard
#                 errors.append({"id": document_id, "error": "Document found but failed to delete from DB"})
#         except InvalidId:
#             errors.append({"id": document_id, "error": "Invalid document ID format"})
#         except Exception as e:
#             errors.append({"id": document_id, "error": str(e)})

#     response_message = ""
#     if deleted_ids:
#         response_message += f"{len(deleted_ids)} document(s) deleted successfully: {', '.join(deleted_ids)}. "
#     if errors:
#         response_message += f"Errors occurred for some documents."
#         return JSONResponse(
#             content={"message": response_message, "deleted": deleted_ids, "errors": errors},
#             status_code=status.HTTP_207_MULTI_STATUS if deleted_ids else status.HTTP_400_BAD_REQUEST ,
#         )
    
#     if not deleted_ids and not errors: # Should not happen if document_ids is not empty
#         return JSONResponse(content={"message": "No documents specified for deletion."}, status_code=status.HTTP_400_BAD_REQUEST)

#     return JSONResponse(
#         content={"message": response_message, "deleted": deleted_ids},
#         status_code=status.HTTP_200_OK,
#     )


# router = APIRouter()


# @router.get("/get-test-cases/{document_id}", tags=["Test Cases"])
# async def get_test_cases_as_json_filtered_and_counted( # Renamed for clarity
#     document_id: str,
#     types: Optional[str] = Query(None, description="Filter test cases by a comma-separated list of types (e.g., 'functional,security')."),
#     # 'collection' should ideally be injected using FastAPI's Depends
# ):
#     """
#     Retrieves generated test cases for a document.
#     By default (no 'types' param), returns all available test cases.
#     Can be filtered by providing a 'types' query parameter.
#     The response includes counts for the returned (filtered) test cases.
#     e.g., /get-test-cases/some_id?types=functional,security
#     """
#     # Placeholder for DB collection access
#     from main3 import collection # Assuming collection is importable for this example

#     try:
#         doc_object_id = ObjectId(document_id)
#     except InvalidId:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format.")

#     doc = collection.find_one({"_id": doc_object_id})
#     if not doc:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

#     doc_status = doc.get("status")
#     requested_during_generation = doc.get("requested_test_case_types", [])
#     base_response = {
#         "document_id": document_id,
#         "requested_test_case_types_during_generation": requested_during_generation
#     }

#     # Handle non-completed statuses first
#     if doc_status == -1:
#         return {**base_response, "status_code": doc_status, "status_message": "pending_generation", "detail": "Test case generation has not been initiated."}
#     elif doc_status == 0:
#         progress = doc.get("progress", [])
#         last_progress = progress[-1] if progress else "Processing test cases..."
#         return {**base_response, "status_code": doc_status, "status_message": "processing", "detail": last_progress, "progress_log": progress}
#     elif doc_status == 2:
#         error_info = doc.get("error_info", "An unspecified error occurred.")
#         return {**base_response, "status_code": doc_status, "status_message": "error", "detail": f"Test case generation failed: {error_info}"}
#     elif doc_status != 1: # Any other unknown status
#         return {**base_response, "status_code": doc_status if doc_status is not None else "unknown", "status_message": "unknown_status", "detail": f"Document is in an unknown state (status: {doc_status})."}

#     # Proceed if doc_status is 1 (Completed)
#     try:
#         _, all_parsed_rows = test_case_utils.parse_test_cases_to_csv(document_id, collection)

#         if not all_parsed_rows:
#             return {
#                 **base_response,
#                 "status_code": doc_status,
#                 "status_message": "completed_no_data",
#                 "detail": "Generation completed, but no test cases were found or parsed from the document.",
#                 "test_cases": [],
#                 "counts_by_type": {},
#                 "total_test_cases": 0
#             }

#         # --- Filtering Logic for comma-separated 'types' string ---
#         final_rows_to_return = all_parsed_rows
#         applied_filter_types_list = []

#         if types:
#             filter_types_lower = [t.strip().lower() for t in types.split(',') if t.strip()]
#             applied_filter_types_list = [t.strip() for t in types.split(',') if t.strip()]

#             if filter_types_lower:
#                 final_rows_to_return = [
#                     tc for tc in all_parsed_rows
#                     if tc.get("Test type", "").lower() in filter_types_lower
#                 ]
        
#         # --- Counting Logic for the final_rows_to_return ---
#         test_type_counts = Counter()
#         if final_rows_to_return: # Only count if there are rows to count
#             for tc in final_rows_to_return:
#                 test_type_value = tc.get("Test type")
#                 if test_type_value is None or not str(test_type_value).strip() or str(test_type_value).strip().upper() == "N/A":
#                     normalized_test_type = "Not Specified"
#                 else:
#                     normalized_test_type = str(test_type_value).strip()
#                 test_type_counts[normalized_test_type] += 1
        
#         total_returned_test_cases = len(final_rows_to_return)
#         # --- End Counting Logic ---

#         status_message = "ready"
#         detail_message = "Test cases retrieved successfully."

#         if types and applied_filter_types_list and not final_rows_to_return:
#             status_message = "ready_no_match_for_filter"
#             detail_message = f"Generation completed. No test cases matched the filter types: {applied_filter_types_list}"
#         elif types and applied_filter_types_list:
#             detail_message = f"Test cases retrieved and filtered by: {applied_filter_types_list}"


#         return {
#             **base_response,
#             "status_code": doc_status,
#             "status_message": status_message,
#             "detail": detail_message,
#             "filter_applied_types": applied_filter_types_list if types else "None (all available shown)",
#             "test_cases": final_rows_to_return,
#             "counts_by_type": dict(test_type_counts), # Counts for the returned (filtered) TCs
#             "total_test_cases": total_returned_test_cases # Total for the returned (filtered) TCs
#         }

#     except HTTPException as he: # Catch specific errors from parse_test_cases_to_csv
#         if he.status_code == 404 and "No test cases found" in he.detail:
#             return {
#                 **base_response,
#                 "status_code": doc_status,
#                 "status_message": "completed_no_data", # Original error from parser
#                 "detail": he.detail,
#                 "test_cases": [],
#                 "counts_by_type": {},
#                 "total_test_cases": 0
#             }
#         raise he # Re-raise other HTTPExceptions
#     except Exception as e:
#         print(f"Error processing or counting test cases for doc {document_id}: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to process or count test cases: {str(e)}"
#         )

# # >>>>>>>>>>>>>>>>>>>>> NEW ENDPOINT START <<<<<<<<<<<<<<<<<<<<<<<
# @router.get("/test-case-summary/{document_id}")
# async def get_test_case_summary(document_id: str):
#     try:
#         doc_object_id = ObjectId(document_id)
#     except InvalidId:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
#         )

#     doc = collection.find_one({"_id": doc_object_id})
#     if not doc:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
#         )

#     doc_status = doc.get("status")
#     if doc_status == -1:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Test case generation has not been initiated for this document. Summary not available."
#         )
#     if doc_status == 0:
#         raise HTTPException(
#             status_code=status.HTTP_425_TOO_EARLY,
#             detail="Test case generation is still in progress. Summary will be available once completed."
#         )
#     if doc_status == 2: # Error state
#         error_info = doc.get("error_info", "Processing failed.")
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"Test case generation failed for this document: {error_info}. Summary not available."
#         )
#     if doc_status != 1: # Any other non-completed status
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"Document status is '{doc_status}'. Summary is only available for completed generations."
#         )

#     # If status is 1 (completed), proceed to parse and summarize
#     try:
#         # We don't need the csv_path here, only the rows (parsed test cases)
#         _, parsed_test_cases = test_case_utils.parse_test_cases_to_csv(document_id, collection)
#     except HTTPException as e:
#         # If parse_test_cases_to_csv itself raises an HTTPException (e.g., no test cases found in doc)
#         raise e
#     except Exception as e:
#         # Log this unexpected error during parsing for summary
#         print(f"Error parsing test cases for summary (doc_id: {document_id}): {e}")
#         raise HTTPException(status_code=500, detail="Error processing test cases for summary.")

#     if not parsed_test_cases:
#         return {
#             "document_id": document_id,
#             "counts_by_type": {},
#             "total_test_cases": 0,
#             "message": "No test cases were parsed from this document, although it's marked as completed."
#         }

#     test_type_counts = Counter()
#     for tc in parsed_test_cases:
#         # The key "Test type" comes from your CSV_HEADERS in test_case_utils.py
#         test_type = tc.get("Test type", "Unknown")  # Default to "Unknown" if key is missing
#         if test_type == "N/A" or not test_type.strip(): # Handle "N/A" or empty strings
#             test_type = "Not Specified"
#         test_type_counts[test_type] += 1
    
#     total_test_cases = len(parsed_test_cases)
        
#     return {
#         "document_id": document_id,
#         "counts_by_type": dict(test_type_counts), # Convert Counter to dict for JSON response
#         "total_test_cases": total_test_cases
#     }
# # >>>>>>>>>>>>>>>>>>>>> NEW ENDPOINT END <<<<<<<<<<<<<<<<<<<<<<<<<


# app.include_router(router)


# @app.get("/download-csv/{document_id}")
# def download_test_cases_csv(document_id: str):
#     try:
#         doc_object_id = ObjectId(document_id)
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid document ID format")

#     doc = collection.find_one({"_id": doc_object_id})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
    
#     doc_status = doc.get("status")
#     if doc_status != 1:
#         status_message = "not completed"
#         if doc_status == 0: status_message = "still processing"
#         elif doc_status == -1: status_message = "generation not started"
#         elif doc_status == 2: status_message = f"failed ({doc.get('error_info', 'unknown error')})"
#         raise HTTPException(status_code=409, detail=f"Cannot download CSV. Test case generation is {status_message}.")


#     original_file_name = doc.get("file_name", "document.pdf")

#     try:
#         csv_path, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
#     except HTTPException as e: # Catch specific errors from parsing, e.g. no test cases
#         raise e
#     except Exception as e:
#         print(f"Error generating CSV for download (doc_id: {document_id}): {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate CSV file: {str(e)}")

#     if not os.path.exists(csv_path):
#         # This case should ideally be caught by parse_test_cases_to_csv if no TCs found
#         raise HTTPException(status_code=404, detail=f"CSV file not found at {csv_path}. Parsing might have failed or produced no data.")

#     csv_file_name = f"{Path(original_file_name).stem}_test_cases.csv"

#     return FileResponse(
#         csv_path,
#         media_type="text/csv",
#         filename=csv_file_name,
#     )


# @app.get("/api_key_usage/{api_key}") # Consider making this POST if API key is sensitive
# def get_api_key_cost(api_key: str):
#     # For security, avoid exposing full API keys in GET requests if possible.
#     # If this is for admin use, ensure proper auth.
#     # A hashed version or an internal ID for the key might be safer if user-facing.
#     record = cost_collection.find_one({"api_key_suffix": api_key[-5:]}) # Example: query by suffix
#     if not record:
#          # If querying by full key:
#         record = cost_collection.find_one({"api_key": api_key})
#         if not record:
#             return {"api_key_identifier": api_key[-5:], "tokens_used": 0, "cost_usd": 0.0, "message": "No usage data found for this API key identifier."}
    
#     return {
#         "api_key_identifier": record.get("api_key_suffix", api_key[-5:]),
#         "tokens_used": record.get("tokens_used", 0),
#         "cost_usd": round(record.get("cost_usd", 0.0), 6), # Increased precision
#         "last_updated": record.get("last_updated", "N/A") # Added last_updated
#     }

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"

# if not SECRET_KEY:
#     print(
#         "WARNING: SECRET_KEY environment variable is not set. JWT authentication for WebSockets will fail."
#     )

# @app.websocket("/ws/task_status/{task_id}")
# async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
#     token = websocket.query_params.get("token")

#     if not SECRET_KEY:
#         await websocket.accept()
#         await websocket.send_json(
#             {"status": "error", "message": "Server configuration error: JWT secret not set."}
#         )
#         await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
#         return

#     if not token:
#         await websocket.accept()
#         await websocket.send_json(
#             {"status": "error", "message": "Authentication token missing."}
#         )
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return

#     username = None # Initialize username
#     try:
#         from jose import jwt, JWTError
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if not username:
#             await websocket.accept()
#             await websocket.send_json(
#                 {"status": "error", "message": "Invalid token: Subject missing."}
#             )
#             await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#             return
#     except JWTError as e:
#         await websocket.accept()
#         await websocket.send_json(
#             {"status": "error", "message": f"Authentication failed: {str(e)}"}
#         )
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
#     except ImportError:
#         await websocket.accept()
#         await websocket.send_json(
#             {"status": "error", "message": "Server configuration error: JWT library not available."}
#         )
#         await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
#         return


#     await websocket.accept()
#     # Log WebSocket connection
#     print(f"WebSocket connected for task {task_id}, user: {username}")
#     await websocket.send_json(
#         {
#             "status": "connected",
#             "message": f"Authenticated as {username}. Monitoring task {task_id}.",
#         }
#     )

#     task_monitor = AsyncResult(task_id)
#     try:
#         while True:
#             if websocket.client_state != WebSocketState.CONNECTED:
#                 print(f"WebSocket for task {task_id} (User: {username}) disconnected by client.")
#                 break

#             task_state = task_monitor.state
#             # Fetch the latest document status from DB for more context
#             doc_db_info = collection.find_one({"last_task_id": task_id}, {"status": 1, "progress": 1, "error_info": 1})
#             db_status = doc_db_info.get("status") if doc_db_info else None
            
#             response_data = {"task_id": task_id, "celery_status": task_state, "db_doc_status": db_status}

#             if task_state == "PENDING":
#                 response_data["info"] = "Task is waiting to be processed by a worker."
#             elif task_state == "STARTED":
#                 response_data["info"] = "Task has been picked up by a worker and started."
#             elif task_state == "PROGRESS":
#                 response_data["info"] = "Task is in progress."
#                 # Celery task must use self.update_state(state='PROGRESS', meta={'current': i, 'total': n, 'status': 'details'})
#                 response_data["progress_details"] = task_monitor.info 
#                 if doc_db_info and "progress" in doc_db_info:
#                      response_data["db_progress_log"] = doc_db_info["progress"]
#             elif task_state == "SUCCESS":
#                 response_data["info"] = "Task completed successfully."
#                 response_data["result"] = task_monitor.result # Result from Celery task return
#                 await websocket.send_json(response_data)
#                 break 
#             elif task_state == "FAILURE":
#                 response_data["info"] = "Task failed."
#                 response_data["error_details"] = str(task_monitor.info) # Exception info from Celery
#                 if doc_db_info and "error_info" in doc_db_info:
#                     response_data["db_error_info"] = doc_db_info["error_info"]
#                 await websocket.send_json(response_data)
#                 break
#             elif task_state == "RETRY":
#                 response_data["info"] = "Task is being retried."
#                 response_data["retry_reason"] = str(task_monitor.info)

#             await websocket.send_json(response_data)

#             if task_monitor.ready(): # Task is definitively finished (SUCCESS, FAILURE)
#                 # Ensure final state is sent if loop condition missed it for some reason
#                 if task_state not in ["SUCCESS", "FAILURE"]:
#                     final_state = task_monitor.state
#                     final_response = {"task_id": task_id, "celery_status": final_state, "info": "Task reached final state."}
#                     if final_state == "SUCCESS": final_response["result"] = task_monitor.result
#                     elif final_state == "FAILURE": final_response["error_details"] = str(task_monitor.info)
#                     await websocket.send_json(final_response)
#                 break
            
#             await asyncio.sleep(2)

#     except WebSocketDisconnect:
#         print(f"Client {username} (task: {task_id}) disconnected gracefully.")
#     except Exception as e:
#         print(
#             f"Unexpected error in WebSocket for task {task_id} (User: {username}): {type(e).__name__} - {e}"
#         )
#         import traceback
#         traceback.print_exc()
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try:
#                 await websocket.send_json(
#                     {"status": "error", "message": "An unexpected server error occurred while monitoring the task."}
#                 )
#             except Exception as send_err:
#                  print(f"Error sending WebSocket error message: {send_err}")
#     finally:
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try:
#                 await websocket.close(code=status.WS_1001_GOING_AWAY)
#             except RuntimeError: # Already closed
#                 pass
#         print(f"WebSocket connection for task {task_id} (User: {username}) definitively closed.")


# class TokenRequest(BaseModel):
#     username: str
#     password: str # In a real app, never log passwords or send them around more than necessary


# @app.post("/get_token", tags=["Authentication"])
# async def get_token_post(request: TokenRequest):
#     if not request.username or not request.password:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Username and password required",
#         )

#     # IMPORTANT: Replace with real DB/user authentication and password hashing
#     # DO NOT use plain text password comparison in production. Use something like passlib.
#     if request.username == os.getenv("ADMIN_USERNAME", "admin") and \
#        request.password == os.getenv("ADMIN_PASSWORD", "admin123"): # Load credentials from env
        
#         token_data = {"sub": request.username, "role": "admin"} # Add role or other claims
#         try:
#             if not SECRET_KEY:
#                  raise ValueError("JWT_SECRET_KEY is not configured on the server.")
#             token = create_jwt_token(token_data) # Assuming create_jwt_token uses SECRET_KEY and ALGORITHM
#             return {"access_token": token, "token_type": "bearer"}
#         except Exception as e:
#             print(f"Error generating token: {e}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Could not generate token due to server error.",
#             )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
#         )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastapi import BackgroundTasks, HTTPException
# from task_with_api_key import process_and_generate_task
# from celery.result import AsyncResult
# from fastapi import (
#     FastAPI,
#     UploadFile,
#     File,
#     HTTPException,
#     Form,
#     Query,
#     status,
#     WebSocket,
#     APIRouter,
#     WebSocketDisconnect,
# )
# from fastapi.responses import JSONResponse, FileResponse
# from utils.jwt_auth import (
#     create_jwt_token,
# )
# from pydantic import BaseModel, Field # Added Field
# from pymongo.collection import Collection # For type hinting

# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, List, Dict, Any # Added Any
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from bson import ObjectId
# from bson.errors import InvalidId
# from pathlib import Path
# import os
# import re
# # import time # Not used directly
# # import uuid # Not used directly
# # import pandas as pd
# # from openpyxl import load_workbook
# # import csv
# import asyncio
# from starlette.websockets import WebSocketState
# from collections import Counter


# # Import your custom modules
# from utils import data_ingestion, test_case_utils, user_story_utils
# from utils.llms import Mistral, openai, llama
# # from core.websocket import websocket_endpoint # Your WS is inline

# from datetime import datetime, timezone as dt_timezone
# from zoneinfo import ZoneInfo

# load_dotenv()

# # --- MongoDB Setup ---
# mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# db = mongo_client[os.getenv("MONGO_DB_NAME", "Gen_AI")]
# collection: Collection = db["test_case_generation"]
# data_spaces_collection: Collection = db["data_spaces"]
# cost_collection: Collection = db["cost_tracking"]

# # --- Pydantic Models ---
# class DataSpaceCreate(BaseModel):
#     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
#     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# class DataSpaceResponse(BaseModel):
#     data_space_id: str
#     name: str
#     description: Optional[str]
#     created_at: datetime
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True # For Pydantic v2

# class TokenRequest(BaseModel): # DEFINITION OF TokenRequest
#     username: str
#     password: str

# # --- Serialization Function (Your Existing One) ---
# def serialize_document(doc_data: dict): # Changed param name for clarity
#     return {
#         "file_id": str(doc_data["_id"]),
#         "file_name": doc_data.get("file_name"),
#         "file_path": doc_data.get("file_path"),
#         "status": doc_data.get("status"),
#         "selected_model": doc_data.get("selected_model", None),
#         "timestamp": doc_data.get("timestamp").isoformat() if isinstance(doc_data.get("timestamp"), datetime) else str(doc_data.get("timestamp")),
#         "last_task_id": doc_data.get("last_task_id")
#     }

# IST = ZoneInfo("Asia/Kolkata")

# # --- Directories Setup ---
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# # EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# app = FastAPI(title="GenAI API - Minimal Data Space Integration")
# app.add_middleware(
#     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"],
# )

# VALID_TEST_CASE_TYPES = [
#     "functional", "non-functional", "security", "performance",
#     "boundary", "compliance", "all"
# ]
# INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES if t != "all"]


# # --- New Router for Data Space Creation ---
# data_space_creation_router = APIRouter(prefix="/api/v1", tags=["Data Spaces"])

# @data_space_creation_router.post("/data-spaces/", response_model=DataSpaceResponse, status_code=status.HTTP_201_CREATED)
# async def create_new_data_space(data_space_input: DataSpaceCreate):
#     existing_space = data_spaces_collection.find_one({"name": data_space_input.name})
#     if existing_space:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_input.name}' already exists.")
#     current_time = datetime.now(IST)
#     ds_doc_data = data_space_input.dict()
#     ds_doc_data["created_at"] = current_time
#     insert_result = data_spaces_collection.insert_one(ds_doc_data)
#     created_doc = data_spaces_collection.find_one({"_id": insert_result.inserted_id})
#     if not created_doc:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data space post-creation.")
#     return DataSpaceResponse(data_space_id=str(created_doc["_id"]), **created_doc)

# app.include_router(data_space_creation_router)

# # --- Your Existing Endpoints ---
# @app.post("/upload_document/")
# async def upload_document_legacy(file: UploadFile = File(...)):
#     file_name = file.filename
#     base, ext = os.path.splitext(file.filename)
#     sanitized_base = re.sub(r'[^\w\.-]', '_', base)
#     unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
#     file_path = Path(INPUT_DIR) / unique_filename_on_disk
#     try:
#         with open(file_path, "wb") as f: f.write(await file.read())
#     except Exception as e: raise HTTPException(status_code=500, detail=f"Save err: {e}")
#     finally: await file.close()
#     upload_time = datetime.now(IST)
#     doc_data = {"file_name": file.filename, "file_path": str(file_path), "status": -1, "timestamp": upload_time, "data_space_id": None}
#     result = collection.insert_one(doc_data)
#     return {"message": "File uploaded (legacy, no Data Space link).", "file_name": file.filename, "file_path": str(file_path), "file_id": str(result.inserted_id), "timestamp": upload_time.isoformat()}

# @app.post("/generate_test_cases/")
# async def generate_test_cases(
#     file_id: str = Form(...), model_name: Optional[str] = Form("Mistral"),
#     chunk_size: Optional[int] = Query(default=None), #cache_key: Optional[str] = Query(default=None),
#     api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
# ):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     document = collection.find_one({"_id": doc_obj_id})
#     if not document: raise HTTPException(status_code=404, detail="Doc not found.")
#     f_path_str = document.get("file_path")
#     if not f_path_str or not Path(f_path_str).exists(): raise HTTPException(status_code=404, detail="Doc file missing.")
    
#     types_to_send, types_for_resp = "all", [t for t in VALID_TEST_CASE_TYPES if t != "all"]
#     req_types_str = test_case_types.strip().lower()
#     if req_types_str != "all":
#         parsed = [t.strip().lower() for t in test_case_types.split(",")]
#         validated = []
#         for t_type in parsed:
#             if t_type not in INDIVIDUAL_VALID_TEST_CASE_TYPES: # Use individual list for validation
#                 raise HTTPException(status_code=400, detail=f"Invalid type: '{t_type}'. Valid: {INDIVIDUAL_VALID_TEST_CASE_TYPES}")
#             if t_type not in validated: validated.append(t_type)
#         if not validated: raise HTTPException(status_code=400, detail="No valid specific types.")
#         types_to_send, types_for_resp = ",".join(validated), validated
    
#     key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
#     warn_msg = None
#     if not key_to_use: raise HTTPException(status_code=400, detail="API key required.")
#     if not api_key and os.getenv("TOGETHER_API_KEY"): warn_msg = "Using default API key."
    
#     collection.update_one({"_id": doc_obj_id}, {"$set": {
#         "status":0, "selected_model":model_name, "api_key_used":f"...{key_to_use[-5:]}" if key_to_use else "N/A",
#         "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST),
#         "progress":["Task init."], "error_info":None, "last_task_id":None }})
#     task = process_and_generate_task.apply_async(args=[
#         str(Path(f_path_str)), model_name, chunk_size, key_to_use, types_to_send, file_id])
#     collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
#     return {"message":"✅ TC gen task started.", "task_id":task.id, "file_id":file_id, "test_case_types_being_generated":types_for_resp, "api_key_being_used":f"...{key_to_use[-5:]}" if key_to_use else "N/A", "warning":warn_msg}

# @app.get("/documents/")
# def get_all_documents():
#     return [serialize_document(doc) for doc in collection.find().sort("timestamp", -1)]

# @app.get("/documents/{document_id}")
# def get_document_by_id(document_id: str):
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
#     doc = collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     return serialize_document(doc)

# @app.delete("/delete-documents")
# async def delete_documents(document_ids: List[str] = Query(...)):
#     deleted, errors = [], []
#     for doc_id in document_ids:
#         try:
#             obj_id = ObjectId(doc_id)
#             doc_data = collection.find_one_and_delete({"_id": obj_id})
#             if doc_data:
#                 deleted.append(doc_id)
#                 if doc_data.get("file_path") and os.path.exists(doc_data["file_path"]):
#                     try: os.remove(doc_data["file_path"])
#                     except Exception as e: errors.append({"id": doc_id, "file_error": str(e)})
#                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{doc_id}_test_cases.csv")
#                 if os.path.exists(csv_p):
#                     try: os.remove(csv_p)
#                     except Exception as e: errors.append({"id": doc_id, "csv_error": str(e)})
#             else: errors.append({"id": doc_id, "error": "Not found in DB"})
#         except InvalidId: errors.append({"id": doc_id, "error": "Invalid ID format"})
#         except Exception as e: errors.append({"id": doc_id, "error": str(e)})
    
#     msg = f"{len(deleted)} docs deleted." if deleted else "No docs deleted."
#     if errors: msg += f" Errors: {len(errors)}"
#     status_c = status.HTTP_200_OK
#     if errors and not deleted: status_c = status.HTTP_400_BAD_REQUEST
#     elif errors: status_c = status.HTTP_207_MULTI_STATUS
#     return JSONResponse(content={"message":msg, "deleted":deleted, "errors":errors}, status_code=status_c)


# router = APIRouter(prefix="/api/v1") # Your existing router

# @router.get("/get-test-cases/{document_id}", tags=["Test Cases"])
# async def get_test_cases_as_json_filtered_and_counted(
#     document_id: str, types: Optional[str] = Query(None),):
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid doc ID.")
#     doc = collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     doc_status = doc.get("status")
#     ds_id = doc.get("data_space_id") # Check if linked to a data space
#     base_res = {"document_id":document_id, "data_space_id": str(ds_id) if ds_id else None, "file_name": doc.get("file_name"), "requested_gen_types":doc.get("requested_test_case_types",[])}
#     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}

#     if doc_status == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
#     if doc_status == 0: prog=doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
#     if doc_status == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
#     if doc_status != 1: return {**base_res, **empty_tc_res, "status_code":doc_status or "unknown", "status_message":"unknown_status", "detail":f"Status: {doc_status}"}

#     try:
#         _, all_rows = test_case_utils.parse_test_cases_to_csv(document_id, collection)
#         if not all_rows: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
#         final_r, applied_f = all_rows, []
#         if types:
#             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
#             applied_f=[t.strip() for t in types.split(',') if t.strip()]
#             if f_lower: final_r=[tc for tc in all_rows if tc.get("Test type","").lower() in f_lower]
        
#         cts=Counter(); total_c=0
#         if final_r:
#             for tc_item in final_r:
#                 tt_val=tc_item.get("Test type")
#                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
#                 cts[norm_tt]+=1
#             total_c=len(final_r)
        
#         stat_msg,det_msg="ready","TCs retrieved."
#         if types and applied_f and not final_r: stat_msg,det_msg="ready_no_match",f"No TCs for filters: {applied_f}"
#         elif types and applied_f: det_msg=f"Filtered by: {applied_f}"
#         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
#     except HTTPException as he:
#         if he.status_code==404 and "No test cases found" in he.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":he.detail}
#         raise he
#     except Exception as e: print(f"ERR GET TC {document_id}: {e}"); raise HTTPException(status_code=500, detail=f"Err processing TCs: {e}")

# @router.get("/test-case-summary/{document_id}", tags=["Test Cases"])
# async def get_test_case_summary(document_id: str):
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
#     doc = collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     doc_status, ds_id = doc.get("status"), doc.get("data_space_id")
#     base_res = {"document_id":document_id, "data_space_id":str(ds_id) if ds_id else None, "file_name":doc.get("file_name")}
#     if doc_status != 1:
#         det = "Summ. not avail.";
#         if doc_status==-1: det+=" Gen not init."
#         elif doc_status==0: det+=" Gen in prog."
#         elif doc_status==2: det+=f" Gen failed: {doc.get('error_info','Unk')}"
#         else: det+=f" Doc status '{doc_status}'."
#         raise HTTPException(status_code=409, detail=det)
#     try:
#         _, parsed=test_case_utils.parse_test_cases_to_csv(document_id,collection)
#         if not parsed: return {**base_res, "counts_by_type":{},"total_test_cases":0,"message":"Completed, no TCs parsed."}
#         cts=Counter(tc.get("Test type","Not Specified") for tc in parsed)
#         return {**base_res, "counts_by_type":dict(cts),"total_test_cases":len(parsed)}
#     except Exception as e: print(f"ERR SUMM {document_id}: {e}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {e}")

# app.include_router(router) # Your existing router

# @app.get("/download-csv/{document_id}")
# def download_test_cases_csv(document_id: str):
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
#     doc = collection.find_one({"_id": doc_obj_id})
#     if not doc or doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready or doc not found.")
#     fname = doc.get("file_name", "doc.pdf")
#     csv_p, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
#     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV missing.")
#     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_tc.csv")

# @app.get("/api_key_usage/{api_key}", tags=["Utilities"])
# def get_api_key_cost(api_key: str):
#     key_sfx = api_key[-5:]
#     rec = cost_collection.find_one({"api_key_suffix": key_sfx}) or cost_collection.find_one({"api_key": api_key})
#     if not rec: return {"id":key_sfx, "tokens":0, "cost":0.0, "msg":"No data."}
#     return {"id":rec.get("api_key_suffix",key_sfx), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_updated":rec.get("last_updated","N/A")}

# SECRET_KEY_ENV = os.getenv("SECRET_KEY")
# ALGORITHM_ENV = "HS256"
# if not SECRET_KEY_ENV: print("WARNING: SECRET_KEY env var not set for JWT.")

# @app.websocket("/ws/task_status/{task_id}")
# async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
#     token = websocket.query_params.get("token")
#     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
#     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
#     username = "ws_user_anon"
#     try:
#         from jose import jwt, JWTError
#         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
#         username = payload.get("sub", "ws_user_no_sub")
#     except Exception as e: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e}"}); await websocket.close(1008); return
    
#     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
#     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}."})
#     task_mon = AsyncResult(task_id)
#     try:
#         while True:
#             if websocket.client_state != WebSocketState.CONNECTED: break
#             cel_stat = task_mon.state
#             doc_info = collection.find_one({"last_task_id":task_id}, {"status":1,"progress":1,"error_info":1,"_id":1})
#             db_stat, doc_id_ws = (doc_info.get("status"), str(doc_info["_id"])) if doc_info else (None, None)
#             resp = {"tid":task_id, "cs":cel_stat, "dbs":db_stat, "did":doc_id_ws}
#             if cel_stat=="PENDING": resp["i"]="Pending."
#             elif cel_stat=="STARTED": resp["i"]="Started."
#             elif cel_stat=="PROGRESS": resp["i"]="Progress."; resp["pd"]=task_mon.info;
#             elif cel_stat=="SUCCESS": resp["i"]="SUCCESS (Celery)"; resp["r"]=task_mon.result; await websocket.send_json(resp); break
#             elif cel_stat=="FAILURE": resp["i"]="FAILURE (Celery)"; resp["ed"]=str(task_mon.info); await websocket.send_json(resp); break
#             elif cel_stat=="RETRY": resp["i"]="RETRY"; resp["rr"]=str(task_mon.info)
#             else: resp["i"]=f"State: {cel_stat}"
#             await websocket.send_json(resp)
#             if task_mon.ready(): # Final check if missed above
#                 if cel_stat not in ["SUCCESS", "FAILURE"]:
#                     final_resp = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
#                     if task_mon.state == "SUCCESS": final_resp["r"] = task_mon.result
#                     elif task_mon.state == "FAILURE": final_resp["ed"] = str(task_mon.info)
#                     await websocket.send_json(final_resp)
#                 break
#             await asyncio.sleep(2)
#     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
#     except Exception as e: print(f"WS Unhandled Error {task_id} ({username}): {type(e).__name__} - {e}");
#     finally:
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
#             except RuntimeError: pass
#         print(f"WS for task {task_id} ({username}) closed.")

# @app.post("/get_token", tags=["Authentication"])
# async def get_token_post(request: TokenRequest): # TokenRequest definition IS HERE
#     ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
#     ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")
#     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
#     if request.username == ADMIN_USER and request.password == ADMIN_PASS:
#         token = create_jwt_token(data={"sub": request.username, "role":"admin"})
#         return {"access_token": token, "token_type": "bearer"}
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# if __name__ == "__main__":
#     import uvicorn
#     print(f"--- GenAI API (Minimal DataSpace Add) Starting ---")
#     print(f"MongoDB URL: {os.getenv('MONGODB_URL')}, DB: {os.getenv('MONGO_DB_NAME')}")
#     print(f"Input DIR: {INPUT_DIR}")
#     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
#         print(f"CSV Output DIR (from utils): {test_case_utils.CSV_OUTPUT_DIR}")
#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# from fastapi import BackgroundTasks, HTTPException
# from task_with_api_key import process_and_generate_task # Ensure this path is correct
# from celery.result import AsyncResult
# from fastapi import (
#     FastAPI,
#     UploadFile,
#     File,
#     HTTPException,
#     Form,
#     Query,
#     status,
#     WebSocket,
#     APIRouter,
#     WebSocketDisconnect,
# )
# from fastapi.responses import JSONResponse, FileResponse
# from utils.jwt_auth import ( # Assuming this exists and is correct
#     create_jwt_token,
# )
# from pydantic import BaseModel, Field # Added Field
# from pymongo.collection import Collection # For type hinting

# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, List, Dict, Any # Added Any
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from bson import ObjectId
# from bson.errors import InvalidId
# from pathlib import Path
# import os
# import re
# # import time # Not used directly
# # import uuid # Not used directly
# # import pandas as pd # Your original code has this
# # from openpyxl import load_workbook # Your original code has this
# # import csv # Your original code has this, test_case_utils also uses it
# import asyncio
# from starlette.websockets import WebSocketState
# from collections import Counter


# # Import your custom modules
# from utils import data_ingestion, test_case_utils, user_story_utils # Assuming these exist
# from utils.llms import Mistral, openai, llama # Assuming these exist
# # from core.websocket import websocket_endpoint # Your WS is inline in the provided code

# from datetime import datetime, timezone as dt_timezone # Renamed to avoid conflict
# from zoneinfo import ZoneInfo

# load_dotenv()

# # --- Environment Variables for Admin Credentials (used in /get_token) ---
# ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
# SECRET_KEY_ENV = os.getenv("SECRET_KEY") # For JWT
# ALGORITHM_ENV = "HS256" # For JWT


# # --- MongoDB Setup ---
# mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# db = mongo_client[os.getenv("MONGO_DB_NAME", "Gen_AI")] # Use MONGO_DB_NAME from .env
# collection: Collection = db["test_case_generation"] # Existing collection for documents/files
# data_spaces_collection: Collection = db["data_spaces"] # NEW collection for Data Spaces
# cost_collection: Collection = db["cost_tracking"] # Existing

# # Consider adding indexes in a separate script or manually:
# # db.data_spaces.createIndex({ "name": 1 }, { unique: true }) // If names should be unique

# # --- Pydantic Models ---
# class DataSpaceCreate(BaseModel):
#     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
#     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# class DataSpaceResponse(BaseModel):
#     data_space_id: str
#     name: str
#     description: Optional[str]
#     created_at: datetime
#     # document_count: int = 0 # Not calculated in this minimal version
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True # For Pydantic v2 (orm_mode=True for v1)

# class TokenRequest(BaseModel): # DEFINITION OF TokenRequest
#     username: str
#     password: str

# # --- Serialization Function (Your Existing One) ---
# def serialize_document(doc_data: dict): # Changed param name for clarity in this func
#     return {
#         "file_id": str(doc_data["_id"]),
#         "file_name": doc_data.get("file_name"),
#         "file_path": doc_data.get("file_path"),
#         "status": doc_data.get("status"),
#         "selected_model": doc_data.get("selected_model", None),
#         "timestamp": doc_data.get("timestamp").isoformat() if isinstance(doc_data.get("timestamp"), datetime) else str(doc_data.get("timestamp")),
#         "last_task_id": doc_data.get("last_task_id")
#     }

# IST = ZoneInfo("Asia/Kolkata")

# # --- Directories Setup ---
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files") # Used by test_case_utils for CSVs
# # EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files") # Your code has this

# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True) # Ensure base output dir exists
# # Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True) # Your code has this


# # --- FastAPI App Instance ---
# app = FastAPI(title="GenAI API - Minimal Data Space Integration")

# app.add_middleware(
#     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"],
# )

# # --- Constants from your original code ---
# VALID_TEST_CASE_TYPES = [ # This list is used by /generate_test_cases
#     "functional", "non-functional", "security", "performance",
#     "boundary", "compliance", "all"
# ]
# # This one is good for validating specific types if "all" is not allowed in a list
# INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES if t != "all"]


# # --- New Router for Data Space Creation ---
# data_space_creation_router = APIRouter(prefix="/api/v1", tags=["Data Spaces"]) # Added prefix

# @data_space_creation_router.post("/data-spaces/", response_model=DataSpaceResponse, status_code=status.HTTP_201_CREATED)
# async def create_new_data_space(data_space_input: DataSpaceCreate):
#     existing_space = data_spaces_collection.find_one({"name": data_space_input.name})
#     if existing_space:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_input.name}' already exists.")
    
#     current_time = datetime.now(IST)
#     # Convert Pydantic model to dict for MongoDB insertion
#     data_space_document_data = data_space_input.model_dump(exclude_unset=True) # For Pydantic v2
#     # For Pydantic v1: data_space_document_data = data_space_input.dict(exclude_unset=True)
    
#     data_space_document_data["created_at"] = current_time
#     # data_space_document_data["updated_at"] = current_time # If you track updates from start
#     # data_space_document_data["document_ids"] = [] # Not linking docs in this minimal step

#     insert_result = data_spaces_collection.insert_one(data_space_document_data)
    
#     created_document_from_db = data_spaces_collection.find_one({"_id": insert_result.inserted_id})
#     if not created_document_from_db:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data space after creation.")

#     # Manually construct the response from the DB document
#     return DataSpaceResponse(
#         data_space_id=str(created_document_from_db["_id"]),
#         name=created_document_from_db["name"],
#         description=created_document_from_db.get("description"),
#         created_at=created_document_from_db["created_at"]
#         # document_count is 0 by default in Pydantic model, which is correct for a new space
#     )

# app.include_router(data_space_creation_router)


# # --- Your Existing Endpoints (Unchanged for this minimal addition) ---

# @app.post("/upload_document/") # This is your original endpoint
# async def upload_document(file: UploadFile = File(...)): # Renamed from upload_document_legacy for direct replacement
#     file_name_original = file.filename # Store original filename
#     # Create a unique filename for storage to prevent overwrites
#     base, ext = os.path.splitext(file.filename)
#     sanitized_base = re.sub(r'[^\w\.-]', '_', base) # Basic sanitization
#     unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
#     file_path = Path(INPUT_DIR) / unique_filename_on_disk

#     try:
#         contents = await file.read()
#         with open(file_path, "wb") as f:
#             f.write(contents)
#     except Exception as e:
#         # It's good practice to log the error on the server
#         print(f"Error saving file {file_name_original}: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {str(e)}")
#     finally:
#         await file.close()
    
#     upload_time = datetime.now(IST)
#     document_data = {
#         "file_name": file_name_original, # Store original filename
#         "file_path": str(file_path), # Store path to uniquely named file
#         "status": -1,
#         "timestamp": upload_time,
#         "data_space_id": None # Explicitly mark as not belonging to a data space
#         # Add other default fields your application expects for a new document
#         # "test_cases": None, "progress": [], "error_info": None, 
#         # "selected_model": None, "last_task_id": None, "requested_test_case_types": []
#     }
#     result = collection.insert_one(document_data) # `collection` is `test_case_generation`
#     file_id = str(result.inserted_id)
#     return {
#         "message": "File uploaded successfully (not yet linked to a Data Space).",
#         "file_name": file_name_original,
#         "file_path": str(file_path), # You might not want to expose full server path
#         "file_id": file_id,
#         "timestamp": upload_time.isoformat()
#     }

# @app.post("/generate_test_cases/") # This is your existing endpoint
# async def generate_test_cases(
#     file_id: str = Form(...),
#     model_name: Optional[str] = Form("Mistral"),
#     chunk_size: Optional[int] = Query(default=None),
#     # cache_key: Optional[str] = Query(default=None), # Your code had this, uncomment if used by Celery
#     api_key: Optional[str] = Form(None),
#     test_case_types: Optional[str] = Form("all"),
# ):
#     try:
#         doc_obj_id = ObjectId(file_id)
#         document = collection.find_one({"_id": doc_obj_id}) # Uses existing `collection`
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid file_id format.")
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found in the database.")
    
#     file_path_str = document.get("file_path")
#     if not file_path_str or not Path(file_path_str).exists():
#         raise HTTPException(status_code=404, detail="Document file not found on disk.")
#     file_path_on_disk = Path(file_path_str) # Use this variable name

#     # Parse and validate `test_case_types`
#     types_to_send_to_celery: str
#     types_list_for_response: List[str] # For the API response and DB logging
    
#     processed_test_case_types_str = test_case_types.strip().lower()

#     if processed_test_case_types_str == "all":
#         types_to_send_to_celery = "all"
#         # For response and DB, list the actual types implied by "all"
#         types_list_for_response = INDIVIDUAL_VALID_TEST_CASE_TYPES[:] # Use the correct list
#     else:
#         parsed_list_from_input = [t.strip().lower() for t in test_case_types.split(",")]
#         validated_types_for_celery = []
#         for t_type in parsed_list_from_input:
#             if not t_type: continue # Skip empty strings from "type1,,type2"
#             if t_type not in INDIVIDUAL_VALID_TEST_CASE_TYPES: # Validate against individual types
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Invalid test_case_type: '{t_type}'. Must be one of {INDIVIDUAL_VALID_TEST_CASE_TYPES} or the string 'all'.")
#             if t_type not in validated_types_for_celery: # Avoid duplicates
#                 validated_types_for_celery.append(t_type)
        
#         if not validated_types_for_celery:
#              raise HTTPException(status_code=400, detail="No valid specific test case types provided.")
#         types_to_send_to_celery = ",".join(validated_types_for_celery)
#         types_list_for_response = validated_types_for_celery
 
#     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
#     warning_message = None
#     if not api_key_to_use:
#         # It's better to raise an error if API key is absolutely required by the LLM
#         raise HTTPException(status_code=400, detail="API key is required for generation.")
#     if not api_key and os.getenv("TOGETHER_API_KEY"): # Only show warning if default from env is used
#         warning_message = "Using default API key from environment. Consider providing your own."
 
#     # Update document in existing `collection`
#     collection.update_one(
#         {"_id": doc_obj_id},
#         {
#             "$set": {
#                 "status": 0, # Processing
#                 "selected_model": model_name,
#                 "api_key_used": f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", # Mask key
#                 "requested_test_case_types": types_list_for_response, # Store the list of actual types
#                 "processing_start_time": datetime.now(IST),
#                 "progress": ["Task initiated for test case generation"], # Initialize progress
#                 "error_info": None, # Clear any previous errors
#                 "last_task_id": None # Clear previous task ID before assigning new one
#             }
#         }
#     )
 
#     task = process_and_generate_task.apply_async(args=[
#         str(file_path_on_disk), model_name, chunk_size,
#         api_key_to_use, types_to_send_to_celery, file_id, # file_id is document_id string
#     ])
 
#     collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
 
#     return {
#         "message": "✅ Test case generation task started.",
#         "task_id": task.id,
#         "file_id": file_id,
#         "test_case_types_being_generated": types_list_for_response,
#         "api_key_being_used": f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A",
#         "warning": warning_message,
#     }


# @app.get("/documents/") # Your existing endpoint
# def get_all_documents():
#     documents = list(collection.find().sort("timestamp", -1)) # Uses existing `collection`
#     return [serialize_document(doc) for doc in documents]

# @app.get("/documents/{document_id}") # Your existing endpoint
# def get_document_by_id(document_id: str):
#     try: doc_object_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
#     doc = collection.find_one({"_id": doc_object_id}) # Uses existing `collection`
#     if not doc: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
#     return serialize_document(doc)


# @app.delete("/delete-documents") # Your existing endpoint
# async def delete_documents(document_ids: List[str] = Query(...)):
#     # This uses existing `collection` and `test_case_utils.CSV_OUTPUT_DIR`
#     deleted, errors = [], []
#     for doc_id_str in document_ids:
#         try:
#             obj_id = ObjectId(doc_id_str)
#             doc_data = collection.find_one_and_delete({"_id": obj_id}) # find_one_and_delete returns the doc
#             if doc_data:
#                 deleted.append(doc_id_str)
#                 # Delete associated files
#                 input_file = doc_data.get("file_path")
#                 if input_file and os.path.exists(input_file):
#                     try: os.remove(input_file)
#                     except Exception as e_f: errors.append({"id":doc_id_str, "file_error":str(e_f)})
                
#                 # Ensure CSV_OUTPUT_DIR is accessible, e.g., by importing test_case_utils if defined there
#                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#                     csv_path_to_del = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{doc_id_str}_test_cases.csv")
#                     if os.path.exists(csv_path_to_del):
#                         try: os.remove(csv_path_to_del)
#                         except Exception as e_c: errors.append({"id":doc_id_str, "csv_error":str(e_c)})
#             else: errors.append({"id": doc_id_str, "error": "Not found in DB"})
#         except InvalidId: errors.append({"id": doc_id_str, "error": "Invalid ID format"})
#         except Exception as e_main: errors.append({"id": doc_id_str, "error": str(e_main)})

#     response_msg = f"{len(deleted)} document(s) deleted." if deleted else "No documents deleted."
#     if errors: response_msg += f" Errors occurred for {len(errors)} IDs."
    
#     resp_status_code = status.HTTP_200_OK
#     if errors and not deleted: resp_status_code = status.HTTP_400_BAD_REQUEST
#     elif errors: resp_status_code = status.HTTP_207_MULTI_STATUS
    
#     return JSONResponse(content={"message":response_msg, "deleted":deleted, "errors":errors}, status_code=resp_status_code)


# # Your existing `router` for /get-test-cases and /test-case-summary
# # Ensure this router is defined before it's included in the app.
# # If it's already defined as `router = APIRouter()` in your code, that's fine.
# # If not, define it:
# router = APIRouter(prefix="/api/v1") # Added prefix for consistency, adjust if needed

# @router.get("/get-test-cases/{document_id}", tags=["Test Cases"])
# async def get_test_cases_as_json_filtered_and_counted(
#     document_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid doc ID.")
#     doc = collection.find_one({"_id": doc_obj_id}) # Uses existing `collection`
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    
#     doc_status = doc.get("status")
#     ds_id = doc.get("data_space_id")
#     base_res = {
#         "document_id":document_id,
#         "data_space_id": str(ds_id) if ds_id else None, # Show if doc is linked
#         "file_name": doc.get("file_name"),
#         "requested_test_case_types_during_generation":doc.get("requested_test_case_types",[])
#     }
#     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}

#     if doc_status == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_generation", "detail":"Gen. not started."}
#     if doc_status == 0: prog=doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
#     if doc_status == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
#     if doc_status != 1: return {**base_res, **empty_tc_res, "status_code":doc_status or "unknown", "status_message":"unknown_status", "detail":f"Status: {doc_status}"}

#     try:
#         # Ensure test_case_utils.parse_test_cases_to_csv uses `collection`
#         _, all_rows = test_case_utils.parse_test_cases_to_csv(document_id, collection)
#         if not all_rows: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
        
#         final_r, applied_f = all_rows, []
#         if types:
#             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
#             applied_f=[t.strip() for t in types.split(',') if t.strip()]
#             if f_lower: final_r=[tc for tc in all_rows if tc.get("Test type","").lower() in f_lower]
        
#         cts=Counter(); total_c=0
#         if final_r:
#             for tc_item in final_r:
#                 tt_val=tc_item.get("Test type") # This key comes from your CSV_HEADERS
#                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
#                 cts[norm_tt]+=1
#             total_c=len(final_r)
        
#         stat_msg,det_msg="ready","TCs retrieved."
#         if types and applied_f and not final_r: stat_msg,det_msg="ready_no_match_for_filter",f"No TCs for filters: {applied_f}"
#         elif types and applied_f: det_msg=f"Filtered by: {applied_f}"
#         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None (all available shown)", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
#     except HTTPException as he:
#         if he.status_code==404 and "No test cases found" in he.detail: # Error from parser
#              return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":he.detail}
#         raise he
#     except Exception as e: print(f"ERR GET TC {document_id}: {e}"); raise HTTPException(status_code=500, detail=f"Err processing TCs: {e}")

# @router.get("/test-case-summary/{document_id}", tags=["Test Cases"])
# async def get_test_case_summary(document_id: str):
#     # This uses existing `collection`
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
#     doc = collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    
#     doc_status, ds_id = doc.get("status"), doc.get("data_space_id")
#     base_res = {"document_id":document_id, "data_space_id":str(ds_id) if ds_id else None, "file_name":doc.get("file_name")}
    
#     if doc_status != 1:
#         det = "Summary not avail.";
#         if doc_status==-1: det+=" Gen not init."
#         elif doc_status==0: det+=" Gen in prog."
#         elif doc_status==2: det+=f" Gen failed: {doc.get('error_info','Unk')}"
#         else: det+=f" Doc status '{doc_status}'."
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=det)
#     try:
#         # Ensure test_case_utils.parse_test_cases_to_csv uses `collection`
#         _, parsed=test_case_utils.parse_test_cases_to_csv(document_id,collection)
#         if not parsed: return {**base_res, "counts_by_type":{},"total_test_cases":0,"message":"Completed, no TCs parsed."}
        
#         cts=Counter()
#         for tc_item in parsed: # Key "Test type" must match your CSV_HEADERS in utils
#             tt_val = tc_item.get("Test type")
#             norm_tt = str(tt_val).strip() if tt_val and str(tt_val).strip().upper() != "N/A" else "Not Specified"
#             cts[norm_tt]+=1
#         return {**base_res, "counts_by_type":dict(cts),"total_test_cases":len(parsed)}
#     except Exception as e: print(f"ERR SUMM {document_id}: {e}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {e}")

# app.include_router(router) # Include your existing router

# # Your existing /download-csv/{document_id}
# @app.get("/download-csv/{document_id}") # Keep at app level or move to the router
# def download_test_cases_csv(document_id: str):
#     try: doc_obj_id = ObjectId(document_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
#     doc = collection.find_one({"_id": doc_obj_id}) # Uses `collection`
#     if not doc or doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready or doc not found.")
    
#     fname = doc.get("file_name", "doc.pdf")
#     # Ensure test_case_utils.parse_test_cases_to_csv uses `collection`
#     # Also ensure test_case_utils.CSV_OUTPUT_DIR is correctly defined and accessible
#     csv_p, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
#     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV missing after parse attempt.")
#     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

# # Your existing /api_key_usage/
# @app.get("/api_key_usage/{api_key}", tags=["Utilities"]) # Keep at app level or move
# def get_api_key_cost(api_key: str):
#     # This uses `cost_collection`
#     key_sfx = api_key[-5:] # Be careful if key is < 5 chars
#     rec = cost_collection.find_one({"api_key_suffix": key_sfx})
#     if not rec: # Fallback if suffix matching isn't primary or if full key was passed
#         rec = cost_collection.find_one({"api_key": api_key})
#         if not rec: return {"api_key_identifier":key_sfx, "tokens_used":0, "cost_usd":0.0, "message":"No usage data."}
#     return {"api_key_identifier":rec.get("api_key_suffix",key_sfx), "tokens_used":rec.get("tokens_used",0), "cost_usd":round(rec.get("cost_usd",0.0),6), "last_updated":rec.get("last_updated","N/A")}


# # --- Your existing WebSocket and Auth Endpoints ---
# # (Copied from your provided code, ensure SECRET_KEY_ENV and ALGORITHM_ENV are used for JWT)
# if not SECRET_KEY_ENV:
#     print("WARNING: SECRET_KEY environment variable is not set. JWT auth will fail.")

# @app.websocket("/ws/task_status/{task_id}")
# async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
#     token = websocket.query_params.get("token")
#     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
#     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
#     username = "ws_user_anon"
#     try:
#         from jose import jwt, JWTError # Ensure 'python-jose[cryptography]' is installed
#         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
#         username = payload.get("sub", "ws_user_no_sub")
#     except ImportError: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT lib missing."}); await websocket.close(1011); return
#     except JWTError as e: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e}"}); await websocket.close(1008); return
    
#     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
#     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}."})
#     task_mon = AsyncResult(task_id)
#     try:
#         while True:
#             if websocket.client_state != WebSocketState.CONNECTED: break
#             cel_stat = task_mon.state
#             # Use `collection` (test_case_generation) for DB lookup
#             doc_info = collection.find_one({"last_task_id":task_id}, {"status":1,"progress":1,"error_info":1,"_id":1})
#             db_stat, doc_id_ws = (doc_info.get("status"), str(doc_info["_id"])) if doc_info else (None, None)
#             resp = {"tid":task_id, "cs":cel_stat, "dbs":db_stat, "did":doc_id_ws}

#             # Your existing state handling for WebSocket...
#             if cel_stat=="PENDING": resp["i"]="Pending."
#             elif cel_stat=="STARTED": resp["i"]="Started."
#             elif cel_stat=="PROGRESS": resp["i"]="Progress."; resp["pd"]=task_mon.info;
#             elif cel_stat=="SUCCESS": resp["i"]="SUCCESS (Celery)"; resp["r"]=task_mon.result; await websocket.send_json(resp); break
#             elif cel_stat=="FAILURE": resp["i"]="FAILURE (Celery)"; resp["ed"]=str(task_mon.info); await websocket.send_json(resp); break
#             elif cel_stat=="RETRY": resp["i"]="RETRY"; resp["rr"]=str(task_mon.info)
#             else: resp["i"]=f"State: {cel_stat}"
            
#             await websocket.send_json(resp)
#             if task_mon.ready(): # Final check
#                 if cel_stat not in ["SUCCESS", "FAILURE"]:
#                     final_resp = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
#                     if task_mon.state == "SUCCESS": final_resp["r"] = task_mon.result
#                     elif task_mon.state == "FAILURE": final_resp["ed"] = str(task_mon.info)
#                     await websocket.send_json(final_resp)
#                 break
#             await asyncio.sleep(2)
#     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
#     except Exception as e: print(f"WS Unhandled Error {task_id} ({username}): {type(e).__name__} - {e}");
#     finally:
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
#             except RuntimeError: pass
#         print(f"WS for task {task_id} ({username}) closed.")

# @app.post("/get_token", tags=["Authentication"]) # This is your existing endpoint
# async def get_token_post(request: TokenRequest): # Uses the TokenRequest model defined above
#     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set for token generation.")
#     # Use ADMIN_USERNAME_ENV and ADMIN_PASSWORD_ENV for credentials
#     if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
#         token_data = {"sub": request.username, "role":"admin"} # Example claims
#         token = create_jwt_token(data=token_data) # create_jwt_token needs SECRET_KEY_ENV and ALGORITHM_ENV
#         return {"access_token": token, "token_type": "bearer"}
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# # --- Main Execution ---
# if __name__ == "__main__":
#     import uvicorn
#     print(f"--- GenAI API (Minimal DataSpace Add) Starting ---")
#     print(f"MongoDB URL: {os.getenv('MONGODB_URL')}, DB: {os.getenv('MONGO_DB_NAME')}")
#     print(f"Input DIR: {INPUT_DIR}")
#     # Ensure CSV_OUTPUT_DIR from test_case_utils is created (if defined)
#     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
#         print(f"CSV Output DIR (from utils): {test_case_utils.CSV_OUTPUT_DIR}")
#     else:
#         print("Warning: test_case_utils.CSV_OUTPUT_DIR is not defined. CSV downloads might fail.")
        
#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# main3.py
# from fastapi import BackgroundTasks, HTTPException
# from task_with_api_key import process_and_generate_task # Ensure this path is correct
# from celery.result import AsyncResult
# from fastapi import (
#     FastAPI,
#     UploadFile,
#     File,
#     HTTPException,
#     Form,
#     Query,
#     status,
#     WebSocket,
#     APIRouter,
#     WebSocketDisconnect,
#     Depends 
# )
# from fastapi.responses import JSONResponse, FileResponse
# from utils.jwt_auth import ( 
#     create_jwt_token,
# )
# from pydantic import BaseModel, Field 
# from pymongo.collection import Collection 

# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, List, Dict, Any 
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from bson import ObjectId # Import ObjectId for Pydantic json_encoders
# from bson.errors import InvalidId
# from pathlib import Path
# import os
# import re
# import asyncio
# from starlette.websockets import WebSocketState
# from collections import Counter

# from utils import data_ingestion, test_case_utils, user_story_utils 
# from utils.llms import Mistral, openai, llama 

# from datetime import datetime, timezone as dt_timezone 
# from zoneinfo import ZoneInfo

# load_dotenv()

# # --- Environment Variables ---
# ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
# SECRET_KEY_ENV = os.getenv("SECRET_KEY")
# ALGORITHM_ENV = "HS256"
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

# # --- Pydantic Models (Defined BEFORE app instance and routers) ---
# class DataSpaceCreate(BaseModel):
#     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
#     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# class DataSpaceResponse(BaseModel):
#     data_space_id: str
#     name: str
#     description: Optional[str]
#     created_at: datetime
#     document_count: int = 0
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True # For Pydantic v2 (orm_mode = True for Pydantic v1)

# class DocumentMetadataResponse(BaseModel):
#     file_id: str
#     file_name: str
#     status: Optional[int]
#     timestamp: datetime
#     content_type: Optional[str] = None
#     size: Optional[int] = None
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True

# class UploadedFileDetail(BaseModel):
#     file_id: Optional[str] = None
#     file_name: str
#     status: str
#     error: Optional[str] = None
#     message: Optional[str] = None

# class BatchUploadResponse(BaseModel): # Used by single combined upload endpoint
#     data_space_id: str
#     data_space_name: str # Added for clarity in response
#     message: str
#     uploaded_files: Dict[str, str] # {original_filename: new_file_id}
#     errors: Optional[List[Dict[str, str]]] = None

# class TokenRequest(BaseModel):
#     username: str
#     password: str

# class GenerateTaskResponseItem(BaseModel): # For batch generate TC response
#     file_id: str
#     task_id: str
#     message: str
#     error: Optional[str] = None

# class BatchGenerateTestCasesResponse(BaseModel): # For batch generate TC response
#     overall_message: str
#     tasks_initiated: List[GenerateTaskResponseItem]
#     warning: Optional[str] = None


# # --- MongoDB Setup ---
# mongo_client = MongoClient(MONGODB_URL)
# db = mongo_client[MONGO_DB_NAME]
# documents_collection: Collection = db["test_case_generation"]
# data_spaces_collection: Collection = db["data_spaces"]
# cost_collection: Collection = db["cost_tracking"]

# # --- Serialization, Constants, Directory Setup ---
# IST = ZoneInfo("Asia/Kolkata")
# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'): # Ensure CSV output dir from utils is created
#     Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# VALID_TEST_CASE_TYPES_FROM_USER = [
#     "functional", "non-functional", "security", "performance",
#     "boundary", "compliance", "all"
# ]
# INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES_FROM_USER if t != "all"]

# # --- FastAPI App Instance ---
# app = FastAPI(title="GenAI API with Data Spaces (Corrected Model Order)")
# app.add_middleware(
#     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"],
# )

# # --- API Routers ---
# api_v1_router = APIRouter(prefix="/api/v1")


# # --- Data Space Endpoints ---
# @api_v1_router.post(
#     "/data-spaces/create-and-upload/",
#     response_model=BatchUploadResponse, # Changed to BatchUploadResponse
#     status_code=status.HTTP_201_CREATED,
#     tags=["Data Spaces & Documents"],
#     summary="Create a new Data Space and upload multiple documents to it."
# )
# async def create_dataspace_and_upload_documents(
#     data_space_name: str = Form(..., min_length=3, max_length=100),
#     data_space_description: Optional[str] = Form(None, max_length=500),
#     files: List[UploadFile] = File(...)
# ):
#     if data_spaces_collection.find_one({"name": data_space_name}):
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_name}' already exists.")
    
#     now = datetime.now(IST)
#     ds_doc_data = {"name": data_space_name, "description": data_space_description, "created_at": now, "updated_at": now}
#     insert_ds_result = data_spaces_collection.insert_one(ds_doc_data)
#     new_data_space_id = insert_ds_result.inserted_id
#     new_data_space_id_str = str(new_data_space_id)

#     if not files:
#         return BatchUploadResponse(
#             data_space_id=new_data_space_id_str, data_space_name=data_space_name,
#             message="Data Space created. No files provided.", uploaded_files={}, errors=[]
#         )
        
#     uploaded_files_map: Dict[str, str] = {}
#     file_upload_errors: List[Dict[str,str]] = []
#     successful_uploads_count = 0

#     for file in files:
#         original_filename = file.filename
#         base, ext = os.path.splitext(original_filename)
#         sanitized_base = re.sub(r'[^\w\s\.-]', '_', base).replace(" ", "_")
#         unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
#         file_path_on_disk = Path(INPUT_DIR) / unique_filename_on_disk
#         try:
#             with open(file_path_on_disk, "wb") as f: f.write(await file.read())
#             file_size = file_path_on_disk.stat().st_size
#             doc_meta = {
#                 "data_space_id": new_data_space_id, "file_name": original_filename, "file_path": str(file_path_on_disk),
#                 "content_type": file.content_type, "size": file_size, "status": -1, "timestamp": now,
#                 "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
#                 "last_task_id": None, "requested_test_case_types": []}
#             insert_doc_res = documents_collection.insert_one(doc_meta)
#             uploaded_files_map[original_filename] = str(insert_doc_res.inserted_id)
#             successful_uploads_count += 1
#         except Exception as e:
#             print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
#             file_upload_errors.append({"filename": original_filename, "error": str(e)})
#             if os.path.exists(file_path_on_disk) and original_filename not in uploaded_files_map:
#                  try: os.remove(file_path_on_disk)
#                  except Exception as e_del: print(f"Cleanup err {file_path_on_disk}: {e_del}")
#         finally: await file.close()

#     msg = f"Data Space '{data_space_name}' created. {successful_uploads_count} of {len(files)} files processed."
#     if file_upload_errors: msg += " Some files failed to upload."
    
#     return BatchUploadResponse(
#         data_space_id=new_data_space_id_str, data_space_name=data_space_name,
#         message=msg, uploaded_files=uploaded_files_map, errors=file_upload_errors if file_upload_errors else None
#     )

# @api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
# async def list_data_spaces(skip: int = 0, limit: int = 20):
#     # ... (Same as your previous list_data_spaces) ...
#     spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
#     return [DataSpaceResponse(data_space_id=str(ds_doc["_id"]), **ds_doc, document_count=documents_collection.count_documents({"data_space_id": ds_doc["_id"]})) for ds_doc in spaces_cursor]

# @api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
# async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
#     # ... (Same as your previous list_documents_in_data_space) ...
#     try: ds_obj_id = ObjectId(data_space_id)
#     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")
#     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
#     docs_cursor = documents_collection.find({"data_space_id": ds_obj_id}).sort("timestamp", -1).skip(skip).limit(limit)
#     return [DocumentMetadataResponse(file_id=str(doc["_id"]), **doc) for doc in docs_cursor]

# @api_v1_router.delete("/data-spaces/{data_space_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Data Spaces"])
# async def delete_data_space(data_space_id: str, delete_contained_documents: bool = Query(False)):
#     # ... (Same as your previous delete_data_space, ensure CSV_OUTPUT_DIR is accessible) ...
#     try: ds_obj_id = ObjectId(data_space_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid Data Space ID.")
#     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
#         raise HTTPException(status_code=404, detail="Data Space not found.")
#     if delete_contained_documents:
#         docs_to_del_cursor = documents_collection.find({"data_space_id": ds_obj_id}, {"_id": 1, "file_path": 1})
#         for doc in docs_to_del_cursor:
#             if doc.get("file_path") and os.path.exists(doc["file_path"]):
#                 try: os.remove(doc["file_path"])
#                 except Exception as e: print(f"ERR DEL FILE {doc['file_path']}: {e}")
#             if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{str(doc['_id'])}_test_cases.csv")
#                 if os.path.exists(csv_p):
#                     try: os.remove(csv_p)
#                     except Exception as e: print(f"ERR DEL CSV {csv_p}: {e}")
#         documents_collection.delete_many({"data_space_id": ds_obj_id})
#     result = data_spaces_collection.delete_one({"_id": ds_obj_id})
#     if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Data Space found but failed to delete.")


# # --- Document Test Case Operations ---
# @api_v1_router.post("/documents/batch-generate-test-cases/", response_model=BatchGenerateTestCasesResponse, tags=["Document Test Cases"])
# async def batch_generate_test_cases_for_documents(
#     file_ids_str: str = Form(..., alias="file_ids", description="Comma-separated file_ids."),
#     model_name: Optional[str] = Form("Mistral"), chunk_size: Optional[int] = Query(None),
#     api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
# ):
#     # ... (Your full logic for batch_generate_test_cases_for_documents from the previous response where it was working) ...
#     # This code should be the version that accepts a comma-separated string for file_ids.
#     actual_file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
#     if not actual_file_ids: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")
#     initiated_tasks_info: List[GenerateTaskResponseItem] = []
#     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
#     if not api_key_to_use: raise HTTPException(status_code=400, detail="API key required.")
#     warning_msg = "Using default API key." if not api_key and os.getenv("TOGETHER_API_KEY") else None
#     types_to_send, types_for_resp = "all", INDIVIDUAL_VALID_TEST_CASE_TYPES[:]
#     if test_case_types.strip().lower() != "all":
#         parsed = [t.strip().lower() for t in test_case_types.split(',') if t.strip()]
#         validated = list(dict.fromkeys(t for t in parsed if t in INDIVIDUAL_VALID_TEST_CASE_TYPES))
#         if not validated: raise HTTPException(status_code=400, detail="No valid types.")
#         types_to_send, types_for_resp = ",".join(validated), validated
#     for current_file_id in actual_file_ids:
#         try:
#             doc_obj_id = ObjectId(current_file_id)
#             document = documents_collection.find_one({"_id": doc_obj_id})
#             if not document: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc not found.", error="Doc not found")); continue
#             f_path_str = document.get("file_path")
#             if not f_path_str or not Path(f_path_str).exists(): initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc file missing.", error="File missing")); continue
#             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"status":0, "selected_model":model_name, "api_key_used":f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST), "progress":["Batch gen task init."], "error_info":None, "last_task_id":None}})
#             task = process_and_generate_task.apply_async(args=[str(Path(f_path_str)), model_name, chunk_size, api_key_to_use, types_to_send, current_file_id])
#             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
#             initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id=task.id, message="✅ TC gen task started."))
#         except InvalidId: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Invalid file_id.", error="Invalid file_id"))
#         except Exception as e: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message=f"Failed: {type(e).__name__}.", error=str(e)))
#     success_count = sum(1 for item in initiated_tasks_info if item.task_id != "N/A")
#     return BatchGenerateTestCasesResponse(overall_message=f"Batch process done. {success_count}/{len(actual_file_ids)} tasks started.", tasks_initiated=initiated_tasks_info, warning=warning_msg)


# # --- (All other Document Test Case endpoints: get, summary, download, delete - from previous full code) ---
# # These should all use `documents_collection` and refer to `file_id`.
# @api_v1_router.get("/documents/{file_id}/get-test-cases/", tags=["Document Test Cases"])
# async def get_test_cases_as_json_filtered_and_counted(
#     file_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
#     # ... (Your full logic from previous response)
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     status_val = doc.get("status")
#     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name"), "req_gen_types":doc.get("requested_test_case_types",[])}
#     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}
#     if status_val == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
#     if status_val == 0: prog = doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
#     if status_val == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
#     if status_val != 1: return {**base_res, **empty_tc_res, "status_code":status_val or "unknown", "status_message":"unknown_status", "detail":f"Status: {status_val}"}
#     try:
#         _, all_r = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#         if not all_r: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
#         final_r, applied_f = all_r, []
#         if types:
#             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
#             applied_f=[t.strip() for t in types.split(',') if t.strip()]
#             if f_lower: final_r=[tc for tc in all_r if tc.get("Test type","").lower() in f_lower]
#         cts = Counter(); total_c = 0
#         if final_r:
#             for tc_item in final_r:
#                 tt_val=tc_item.get("Test type")
#                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
#                 cts[norm_tt]+=1
#             total_c=len(final_r)
#         stat_msg, det_msg = "ready", "TCs retrieved."
#         if types and applied_f and not final_r: stat_msg, det_msg = "ready_no_match", f"No TCs for filters: {applied_f}"
#         elif types and applied_f: det_msg = f"Filtered by: {applied_f}"
#         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
#     except HTTPException as http_e:
#         if http_e.status_code==404 and "No test cases found" in http_e.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":http_e.detail}
#         raise http_e
#     except Exception as e_main: print(f"ERR GET TC {file_id}: {e_main}"); raise HTTPException(status_code=500, detail=f"Error processing TCs: {str(e_main)}")

# @api_v1_router.get("/documents/{file_id}/test-case-summary/", tags=["Document Test Cases"])
# async def get_document_test_case_summary(file_id: str):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     status_val = doc.get("status")
#     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name")}
#     if status_val != 1: raise HTTPException(status_code=409, detail=f"Summary not available. Status: {status_val}")
#     try:
#         _, parsed_list = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#         if not parsed_list: return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, no TCs parsed."}
#         cts = Counter(tc.get("Test type", "Not Specified") for tc in parsed_list)
#         return {**base_res, "counts_by_type":dict(cts), "total_test_cases":len(parsed_list)}
#     except Exception as e_sum: print(f"ERR SUMM {file_id}: {e_sum}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {str(e_sum)}")

# @api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
# async def download_test_cases_csv_for_document(file_id: str):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     if doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready.")
#     fname = doc.get("file_name", "doc.pdf")
#     csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV file missing post-parse.")
#     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

# @api_v1_router.delete("/documents/", tags=["Document Test Cases"])
# async def delete_multiple_documents(document_ids: List[str] = Query(...)):
#     del_c, errs = 0, []
#     for id_str in document_ids:
#         try:
#             obj_id = ObjectId(id_str)
#             doc = documents_collection.find_one_and_delete({"_id":obj_id})
#             if doc:
#                 del_c+=1
#                 if doc.get("file_path") and os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
#                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#                     csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{id_str}_test_cases.csv")
#                     if os.path.exists(csv_p): os.remove(csv_p)
#             else: errs.append({"id":id_str, "error":"Not found"})
#         except InvalidId: errs.append({"id":id_str, "error":"Invalid ID"})
#         except Exception as e_del: errs.append({"id":id_str, "error":str(e_del)})
#     return {"deleted_count":del_c, "errors":errs}


# # --- Auth & Utility Endpoints ---
# @api_v1_router.post("/auth/token", response_model=Dict[str, str], tags=["Authentication"])
# async def login_for_access_token(request: TokenRequest):
#     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
#     if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
#         token = create_jwt_token(data={"sub": request.username, "role": "admin"}) # Needs SECRET_KEY_ENV, ALGORITHM_ENV
#         return {"access_token": token, "token_type": "bearer"}
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

# @api_v1_router.get("/utilities/api-key-usage/{api_key_suffix}", tags=["Utilities"])
# async def get_api_key_usage_stats(api_key_suffix: str):
#     if len(api_key_suffix) < 5 : raise HTTPException(status_code=400, detail="Suffix too short.")
#     rec = cost_collection.find_one({"api_key_suffix": api_key_suffix})
#     if not rec: rec = cost_collection.find_one({"api_key": api_key_suffix}) 
#     if not rec: return {"id":api_key_suffix, "tokens":0, "cost":0.0, "msg":"No usage data."}
#     return {"id":rec.get("api_key_suffix",api_key_suffix), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_update":rec.get("last_updated","N/A")}


# app.include_router(api_v1_router) # Include the main v1 router

# # --- WebSocket Endpoint ---
# @app.websocket("/ws/v1/task_status/{task_id}")
# async def websocket_task_status_endpoint(websocket: WebSocket, task_id: str):
#     # ... (Your full WebSocket logic from the previous "full integration attempt" response,
#     #      making sure `documents_collection` is used for DB queries by `last_task_id`) ...
#     token = websocket.query_params.get("token")
#     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
#     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
#     username = "ws_user_anon"
#     try:
#         from jose import jwt, JWTError
#         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
#         username = payload.get("sub", "ws_user_no_sub")
#     except Exception as e_auth_ws: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e_auth_ws}"}); await websocket.close(1008); return
#     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
#     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}"})
#     task_mon = AsyncResult(task_id)
#     try:
#         while True:
#             if websocket.client_state != WebSocketState.CONNECTED: break
#             cel_stat = task_mon.state
#             doc_info_ws = documents_collection.find_one({"last_task_id":task_id}, {"status":1, "progress":1, "error_info":1, "_id":1})
#             db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None
#             doc_id_ws = str(doc_info_ws["_id"]) if doc_info_ws else None
#             resp_ws = {"tid":task_id, "cs":cel_stat, "dbs":db_stat_ws, "did":doc_id_ws}
#             if cel_stat == "PENDING": resp_ws["i"] = "Pending"
#             elif cel_stat == "STARTED": resp_ws["i"] = "Started"
#             elif cel_stat == "PROGRESS": resp_ws["i"] = "Progress"; resp_ws["pd"] = task_mon.info;
#             elif cel_stat == "SUCCESS":
#                 resp_ws["i"] = "SUCCESS (Celery)"; resp_ws["r"] = task_mon.result
#                 if doc_id_ws and db_stat_ws != 1: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":1, "error_info":None}, "$push":{"progress":"Celery SUCCESS via WS"}})
#                 await websocket.send_json(resp_ws); break
#             elif cel_stat == "FAILURE":
#                 resp_ws["i"] = "FAILURE (Celery)"; resp_ws["ed"] = str(task_mon.info)
#                 if doc_id_ws and db_stat_ws != 2: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":2, "error_info":str(task_mon.info)}, "$push":{"progress":"Celery FAILURE via WS"}})
#                 await websocket.send_json(resp_ws); break
#             elif cel_stat == "RETRY": resp_ws["i"] = "RETRY"; resp_ws["rr"] = str(task_mon.info)
#             else: resp_ws["i"] = f"State: {cel_stat}"
#             await websocket.send_json(resp_ws)
#             if task_mon.ready():
#                 if cel_stat not in ["SUCCESS", "FAILURE"]:
#                     final_resp_ws = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
#                     if task_mon.state == "SUCCESS": final_resp_ws["r"] = task_mon.result
#                     elif task_mon.state == "FAILURE": final_resp_ws["ed"] = str(task_mon.info)
#                     await websocket.send_json(final_resp_ws)
#                 break
#             await asyncio.sleep(2)
#     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
#     except Exception as e_ws_main:
#         print(f"WS Unhandled Error {task_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try: await websocket.send_json({"s":"error","m":"Server WS error."})
#             except: pass
#     finally:
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
#             except RuntimeError: pass
#         print(f"WS for task {task_id} ({username}) closed.")


# # --- Main Execution ---
# if __name__ == "__main__":
#     import uvicorn
#     print(f"--- GenAI API (Full Integration with DataSpaces) Starting ---")
#     print(f"MongoDB URL: {MONGODB_URL}, DB: {MONGO_DB_NAME}")
#     print(f"Input DIR: {INPUT_DIR}, Output DIR: {OUTPUT_DIR}")
#     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
#         print(f"CSV Output DIR (utils): {test_case_utils.CSV_OUTPUT_DIR}")
    
#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# main3.py
# from fastapi import BackgroundTasks, HTTPException
# from task_with_api_key import process_and_generate_task # Ensure this path is correct
# from celery.result import AsyncResult
# from fastapi import (
#     FastAPI,
#     UploadFile,
#     File,
#     HTTPException,
#     Form,
#     Query,
#     status,
#     WebSocket,
#     APIRouter,
#     WebSocketDisconnect,
#     Depends 
# )
# from fastapi.responses import JSONResponse, FileResponse
# from utils.jwt_auth import ( 
#     create_jwt_token,
# )
# from pydantic import BaseModel, Field 
# from pymongo.collection import Collection 

# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, List, Dict, Any 
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from bson import ObjectId # Import ObjectId for Pydantic json_encoders
# from bson.errors import InvalidId
# from pathlib import Path
# import os
# import re
# import asyncio
# from starlette.websockets import WebSocketState
# from collections import Counter


# # Import your custom modules
# from utils import data_ingestion, test_case_utils, user_story_utils 
# from utils.llms import Mistral, openai, llama 

# from datetime import datetime, timezone as dt_timezone 
# from zoneinfo import ZoneInfo

# load_dotenv()

# # --- Environment Variables ---
# ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
# SECRET_KEY_ENV = os.getenv("SECRET_KEY")
# ALGORITHM_ENV = "HS256"
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

# # --- Pydantic Models (Defined BEFORE app instance and routers) ---
# class DataSpaceCreate(BaseModel):
#     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
#     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# class DataSpaceResponse(BaseModel):
#     data_space_id: str
#     name: str
#     description: Optional[str]
#     created_at: datetime
#     document_count: int = 0
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True

# class DocumentMetadataResponse(BaseModel):
#     file_id: str
#     file_name: str
#     status: Optional[int]
#     timestamp: datetime
#     content_type: Optional[str] = None
#     size: Optional[int] = None
#     class Config:
#         json_encoders = {ObjectId: str}
#         from_attributes = True

# class UploadedFileDetail(BaseModel): # For individual file status in batch upload
#     file_id: Optional[str] = None
#     file_name: str
#     status: str # e.g., "uploaded", "failed_to_save", "db_insert_failed"
#     error: Optional[str] = None
#     message: Optional[str] = None # Optional success/info message per file

# class BatchUploadResponse(BaseModel): # For the combined create DataSpace and upload files
#     data_space_id: str
#     data_space_name: str
#     message: str # Overall message for the operation
#     uploaded_files: Dict[str, str] # {original_filename: new_file_id or error_string}
#     errors: Optional[List[Dict[str, str]]] = None # List of {"filename": ..., "error": ...}

# class TokenRequest(BaseModel):
#     username: str
#     password: str

# class GenerateTaskResponseItem(BaseModel):
#     file_id: str
#     task_id: str # Celery task ID
#     message: str
#     error: Optional[str] = None

# class BatchGenerateTestCasesResponse(BaseModel):
#     overall_message: str
#     tasks_initiated: List[GenerateTaskResponseItem]
#     warning: Optional[str] = None


# # --- MongoDB Setup ---
# mongo_client = MongoClient(MONGODB_URL)
# db = mongo_client[MONGO_DB_NAME]
# documents_collection: Collection = db["test_case_generation"]
# data_spaces_collection: Collection = db["data_spaces"]
# cost_collection: Collection = db["cost_tracking"]

# # --- Serialization, Constants, Directory Setup ---
# IST = ZoneInfo("Asia/Kolkata")
# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#     Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# VALID_TEST_CASE_TYPES_FROM_USER = [
#     "functional", "non-functional", "security", "performance",
#     "boundary", "compliance", "all"
# ]
# INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES_FROM_USER if t != "all"]

# # --- FastAPI App Instance ---
# app = FastAPI(title="GenAI API with Data Spaces (Full Integration - Corrected)")
# app.add_middleware(
#     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"],
# )

# # --- API Routers ---
# api_v1_router = APIRouter(prefix="/api/v1")

# # --- Data Space Endpoints ---
# @api_v1_router.post(
#     "/data-spaces/create-and-upload/",
#     response_model=BatchUploadResponse,
#     status_code=status.HTTP_201_CREATED,
#     tags=["Data Spaces & Documents"],
#     summary="Create Data Space & Upload Documents"
# )
# async def create_dataspace_and_upload_documents(
#     data_space_name: str = Form(..., min_length=3, max_length=100),
#     data_space_description: Optional[str] = Form(None, max_length=500),
#     files: List[UploadFile] = File(...)
# ):
#     if data_spaces_collection.find_one({"name": data_space_name}):
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_name}' already exists.")
#     now = datetime.now(IST)
#     ds_doc_data = {"name": data_space_name, "description": data_space_description, "created_at": now, "updated_at": now, "document_ids": []}
#     insert_ds_result = data_spaces_collection.insert_one(ds_doc_data)
#     new_data_space_id_obj = insert_ds_result.inserted_id
#     new_data_space_id_str = str(new_data_space_id_obj)

#     if not files:
#         return BatchUploadResponse(data_space_id=new_data_space_id_str, data_space_name=data_space_name, message="Data Space created. No files provided.", uploaded_files={}, errors=[])
        
#     uploaded_files_map: Dict[str, str] = {}
#     successfully_uploaded_doc_object_ids: List[ObjectId] = []
#     individual_file_errors: List[Dict[str,str]] = []
    
#     for file in files:
#         original_filename = file.filename
#         base, ext = os.path.splitext(original_filename); sanitized_base = re.sub(r'[^\w\s\.-]', '_', base).replace(" ", "_")
#         unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
#         file_path_on_disk = Path(INPUT_DIR) / unique_filename_on_disk
#         try:
#             with open(file_path_on_disk, "wb") as f: f.write(await file.read())
#             file_size = file_path_on_disk.stat().st_size
#             doc_meta = {
#                 "data_space_id": new_data_space_id_obj, "file_name": original_filename, "file_path": str(file_path_on_disk),
#                 "content_type": file.content_type, "size": file_size, "status": -1, "timestamp": now,
#                 "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
#                 "last_task_id": None, "requested_test_case_types": []}
#             insert_doc_res = documents_collection.insert_one(doc_meta)
#             new_doc_obj_id = insert_doc_res.inserted_id
#             uploaded_files_map[original_filename] = str(new_doc_obj_id)
#             successfully_uploaded_doc_object_ids.append(new_doc_obj_id)
#         except Exception as e:
#             print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
#             individual_file_errors.append({"filename": original_filename, "error": str(e)})
#             uploaded_files_map[original_filename] = f"ERROR: {str(e)}" # Indicate error in the map
#             if os.path.exists(file_path_on_disk):
#                  try: os.remove(file_path_on_disk)
#                  except Exception as e_del: print(f"Cleanup err {file_path_on_disk}: {e_del}")
#         finally: await file.close()

#     if successfully_uploaded_doc_object_ids:
#         data_spaces_collection.update_one({"_id": new_data_space_id_obj}, {"$set": {"document_ids": successfully_uploaded_doc_object_ids, "updated_at": datetime.now(IST)}})
#     elif files: # Files were provided but none were successful
#          data_spaces_collection.update_one({"_id": new_data_space_id_obj}, {"$set": {"updated_at": datetime.now(IST)}})


#     msg = f"Data Space '{data_space_name}' created. {len(successfully_uploaded_doc_object_ids)} of {len(files)} files successfully uploaded and linked."
#     if individual_file_errors: msg += " Some files encountered errors."
    
#     return BatchUploadResponse(
#         data_space_id=new_data_space_id_str, data_space_name=data_space_name, message=msg,
#         uploaded_files=uploaded_files_map, errors=individual_file_errors if individual_file_errors else None)

# @api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
# async def list_data_spaces(skip: int = 0, limit: int = 20):
#     spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
#     return [DataSpaceResponse(data_space_id=str(ds_doc["_id"]), **ds_doc, document_count=documents_collection.count_documents({"data_space_id": ds_doc["_id"]})) for ds_doc in spaces_cursor]

# @api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
# async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
#     try: ds_obj_id = ObjectId(data_space_id)
#     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")
#     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
#     docs_cursor = documents_collection.find({"data_space_id": ds_obj_id}).sort("timestamp", -1).skip(skip).limit(limit)
#     return [DocumentMetadataResponse(file_id=str(doc["_id"]), **doc) for doc in docs_cursor]

# @api_v1_router.delete("/data-spaces/{data_space_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Data Spaces"])
# async def delete_data_space(data_space_id: str, delete_contained_documents: bool = Query(False)):
#     try: ds_obj_id = ObjectId(data_space_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid Data Space ID.")
#     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
#     if delete_contained_documents:
#         docs_to_del_cursor = documents_collection.find({"data_space_id": ds_obj_id}, {"_id": 1, "file_path": 1})
#         for doc in docs_to_del_cursor:
#             if doc.get("file_path") and os.path.exists(doc["file_path"]):
#                 try: os.remove(doc["file_path"])
#                 except Exception as e: print(f"ERR DEL FILE {doc['file_path']}: {e}")
#             if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{str(doc['_id'])}_test_cases.csv")
#                 if os.path.exists(csv_p):
#                     try: os.remove(csv_p)
#                     except Exception as e: print(f"ERR DEL CSV {csv_p}: {e}")
#         documents_collection.delete_many({"data_space_id": ds_obj_id})
#     result = data_spaces_collection.delete_one({"_id": ds_obj_id})
#     if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Data Space found but failed to delete.")

# # --- Document Test Case Operations ---
# @api_v1_router.post("/documents/batch-generate-test-cases/", response_model=BatchGenerateTestCasesResponse, tags=["Document Test Cases"])
# async def batch_generate_test_cases_for_documents(
#     file_ids_str: str = Form(..., alias="file_ids", description="Comma-separated file_ids."),
#     model_name: Optional[str] = Form("Mistral"), chunk_size: Optional[int] = Query(None),
#     api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
# ):
#     actual_file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
#     if not actual_file_ids: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")
#     initiated_tasks_info: List[GenerateTaskResponseItem] = []
#     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
#     if not api_key_to_use: raise HTTPException(status_code=400, detail="API key required.")
#     warning_msg = "Using default API key." if not api_key and os.getenv("TOGETHER_API_KEY") else None
#     types_to_send, types_for_resp = "all", INDIVIDUAL_VALID_TEST_CASE_TYPES[:]
#     if test_case_types.strip().lower() != "all":
#         parsed = [t.strip().lower() for t in test_case_types.split(',') if t.strip()]
#         validated = list(dict.fromkeys(t for t in parsed if t in INDIVIDUAL_VALID_TEST_CASE_TYPES))
#         if not validated: raise HTTPException(status_code=400, detail="No valid types.")
#         types_to_send, types_for_resp = ",".join(validated), validated
#     for current_file_id in actual_file_ids:
#         try:
#             doc_obj_id = ObjectId(current_file_id)
#             document = documents_collection.find_one({"_id": doc_obj_id})
#             if not document: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc not found.", error="Doc not found")); continue
#             f_path_str = document.get("file_path")
#             if not f_path_str or not Path(f_path_str).exists(): initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc file missing.", error="File missing")); continue
#             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"status":0, "selected_model":model_name, "api_key_used":f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST), "progress":["Batch gen task init."], "error_info":None, "last_task_id":None}})
#             task = process_and_generate_task.apply_async(args=[str(Path(f_path_str)), model_name, chunk_size, api_key_to_use, types_to_send, current_file_id])
#             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}}) # This stores the task_id
#             initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id=task.id, message="✅ TC gen task started."))
#         except InvalidId: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Invalid file_id.", error="Invalid file_id"))
#         except Exception as e: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message=f"Failed: {type(e).__name__}.", error=str(e)))
#     success_count = sum(1 for item in initiated_tasks_info if item.task_id != "N/A")
#     return BatchGenerateTestCasesResponse(overall_message=f"Batch process done. {success_count}/{len(actual_file_ids)} tasks started.", tasks_initiated=initiated_tasks_info, warning=warning_msg)

# # ... (Your other endpoints: /documents/{file_id}/get-test-cases/, /documents/{file_id}/test-case-summary/, /documents/{file_id}/download-csv/, /documents/ (delete)
# #      will be here, exactly as in the previous full code response. I'm omitting them for brevity here but they should be included.
# #      Ensure they are on `api_v1_router`.)

# @api_v1_router.get("/documents/{file_id}/get-test-cases/", tags=["Document Test Cases"])
# async def get_test_cases_as_json_filtered_and_counted(
#     file_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     status_val = doc.get("status")
#     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name"), "req_gen_types":doc.get("requested_test_case_types",[])}
#     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}
#     if status_val == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
#     if status_val == 0: prog = doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
#     if status_val == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
#     if status_val != 1: return {**base_res, **empty_tc_res, "status_code":status_val or "unknown", "status_message":"unknown_status", "detail":f"Status: {status_val}"}
#     try:
#         _, all_r = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#         if not all_r: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
#         final_r, applied_f = all_r, []
#         if types:
#             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
#             applied_f=[t.strip() for t in types.split(',') if t.strip()]
#             if f_lower: final_r=[tc for tc in all_r if tc.get("Test type","").lower() in f_lower]
#         cts = Counter(); total_c = 0
#         if final_r:
#             for tc_item in final_r:
#                 tt_val=tc_item.get("Test type")
#                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
#                 cts[norm_tt]+=1
#             total_c=len(final_r)
#         stat_msg, det_msg = "ready", "TCs retrieved."
#         if types and applied_f and not final_r: stat_msg, det_msg = "ready_no_match", f"No TCs for filters: {applied_f}"
#         elif types and applied_f: det_msg = f"Filtered by: {applied_f}"
#         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
#     except HTTPException as http_e:
#         if http_e.status_code==404 and "No test cases found" in http_e.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":http_e.detail}
#         raise http_e
#     except Exception as e_main: print(f"ERR GET TC {file_id}: {e_main}"); raise HTTPException(status_code=500, detail=f"Error processing TCs: {str(e_main)}")

# @api_v1_router.get("/documents/{file_id}/test-case-summary/", tags=["Document Test Cases"])
# async def get_document_test_case_summary(file_id: str):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     status_val = doc.get("status")
#     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name")}
#     if status_val != 1: raise HTTPException(status_code=409, detail=f"Summary not available. Status: {status_val}")
#     try:
#         _, parsed_list = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#         if not parsed_list: return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, no TCs parsed."}
#         cts = Counter(tc.get("Test type", "Not Specified") for tc in parsed_list)
#         return {**base_res, "counts_by_type":dict(cts), "total_test_cases":len(parsed_list)}
#     except Exception as e_sum: print(f"ERR SUMM {file_id}: {e_sum}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {str(e_sum)}")

# @api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
# async def download_test_cases_csv_for_document(file_id: str):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     if doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready.")
#     fname = doc.get("file_name", "doc.pdf")
#     csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV file missing post-parse.")
#     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

# @api_v1_router.delete("/documents/", tags=["Document Test Cases"])
# async def delete_multiple_documents(document_ids: List[str] = Query(...)):
#     del_c, errs = 0, []
#     for id_str in document_ids:
#         try:
#             obj_id = ObjectId(id_str)
#             doc = documents_collection.find_one_and_delete({"_id":obj_id})
#             if doc:
#                 del_c+=1
#                 if doc.get("file_path") and os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
#                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#                     csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{id_str}_test_cases.csv")
#                     if os.path.exists(csv_p): os.remove(csv_p)
#             else: errs.append({"id":id_str, "error":"Not found"})
#         except InvalidId: errs.append({"id":id_str, "error":"Invalid ID"})
#         except Exception as e_del: errs.append({"id":id_str, "error":str(e_del)})
#     return {"deleted_count":del_c, "errors":errs}


# # --- Auth & Utility Endpoints ---
# @api_v1_router.post("/auth/token", response_model=Dict[str, str], tags=["Authentication"])
# async def login_for_access_token(request: TokenRequest):
#     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
#     if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
#         token = create_jwt_token(data={"sub": request.username, "role": "admin"}) # Needs SECRET_KEY_ENV, ALGORITHM_ENV
#         return {"access_token": token, "token_type": "bearer"}
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

# @api_v1_router.get("/utilities/api-key-usage/{api_key_suffix}", tags=["Utilities"])
# async def get_api_key_usage_stats(api_key_suffix: str):
#     if len(api_key_suffix) < 5 : raise HTTPException(status_code=400, detail="Suffix too short.")
#     rec = cost_collection.find_one({"api_key_suffix": api_key_suffix})
#     if not rec: rec = cost_collection.find_one({"api_key": api_key_suffix}) 
#     if not rec: return {"id":api_key_suffix, "tokens":0, "cost":0.0, "msg":"No usage data."}
#     return {"id":rec.get("api_key_suffix",api_key_suffix), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_update":rec.get("last_updated","N/A")}

# app.include_router(api_v1_router)

# # --- WebSocket Endpoint ---
# @app.websocket("/ws/v1/task_status/{task_id}")
# async def websocket_task_status_endpoint(websocket: WebSocket, task_id: str):
#     token = websocket.query_params.get("token")
#     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
#     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
#     username = "ws_user_anon"
#     try:
#         from jose import jwt, JWTError
#         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
#         username = payload.get("sub", "ws_user_no_sub")
#     except Exception as e_auth_ws: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e_auth_ws}"}); await websocket.close(1008); return
#     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
#     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}"})
#     task_mon = AsyncResult(task_id)
#     try:
#         while True:
#             if websocket.client_state != WebSocketState.CONNECTED: break
#             cel_stat = task_mon.state
#             doc_info_ws = documents_collection.find_one({"last_task_id":task_id}, {"status":1, "progress":1, "error_info":1, "_id":1})
#             db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None
#             doc_id_ws = str(doc_info_ws["_id"]) if doc_info_ws else None
#             resp_ws = {"tid":task_id, "cs":cel_stat, "dbs":db_stat_ws, "did":doc_id_ws}
#             if cel_stat == "PENDING": resp_ws["i"] = "Pending"
#             elif cel_stat == "STARTED": resp_ws["i"] = "Started"
#             elif cel_stat == "PROGRESS": resp_ws["i"] = "Progress"; resp_ws["pd"] = task_mon.info;
#             elif cel_stat == "SUCCESS":
#                 resp_ws["i"] = "SUCCESS (Celery)"; resp_ws["r"] = task_mon.result
#                 if doc_id_ws and db_stat_ws != 1: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":1, "error_info":None}, "$push":{"progress":"Celery SUCCESS via WS"}})
#                 await websocket.send_json(resp_ws); break
#             elif cel_stat == "FAILURE":
#                 resp_ws["i"] = "FAILURE (Celery)"; resp_ws["ed"] = str(task_mon.info)
#                 if doc_id_ws and db_stat_ws != 2: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":2, "error_info":str(task_mon.info)}, "$push":{"progress":"Celery FAILURE via WS"}})
#                 await websocket.send_json(resp_ws); break
#             elif cel_stat == "RETRY": resp_ws["i"] = "RETRY"; resp_ws["rr"] = str(task_mon.info)
#             else: resp_ws["i"] = f"State: {cel_stat}"
#             await websocket.send_json(resp_ws)
#             if task_mon.ready():
#                 if cel_stat not in ["SUCCESS", "FAILURE"]:
#                     final_resp_ws = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
#                     if task_mon.state == "SUCCESS": final_resp_ws["r"] = task_mon.result
#                     elif task_mon.state == "FAILURE": final_resp_ws["ed"] = str(task_mon.info)
#                     await websocket.send_json(final_resp_ws)
#                 break
#             await asyncio.sleep(2)
#     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
#     except Exception as e_ws_main:
#         print(f"WS Unhandled Error {task_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try: await websocket.send_json({"s":"error","m":"Server WS error."})
#             except: pass
#     finally:
#         if websocket.client_state == WebSocketState.CONNECTED:
#             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
#             except RuntimeError: pass
#         print(f"WS for task {task_id} ({username}) closed.")

# # --- Main Execution ---
# if __name__ == "__main__":
#     import uvicorn
#     print(f"--- GenAI API (Full Integration with DataSpaces) Starting ---")
#     print(f"MongoDB URL: {MONGODB_URL}, DB: {MONGO_DB_NAME}")
#     print(f"Input DIR: {INPUT_DIR}, Output DIR: {OUTPUT_DIR}")
#     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
#         print(f"CSV Output DIR (utils): {test_case_utils.CSV_OUTPUT_DIR}")
#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# main3.py
from fastapi import BackgroundTasks, HTTPException
from task_with_api_key import process_and_generate_task # Ensure this path is correct
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


# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils 
from utils.llms import Mistral, openai, llama 

from datetime import datetime, timezone as dt_timezone 
from zoneinfo import ZoneInfo

load_dotenv()

# --- Environment Variables ---
ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
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
    file_name: str
    status: Optional[int]
    timestamp: datetime
    content_type: Optional[str] = None
    size: Optional[int] = None
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

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

class TokenRequest(BaseModel):
    username: str
    password: str

class GenerateTaskResponseItem(BaseModel):
    file_id: str
    task_id: str
    message: str
    error: Optional[str] = None

class BatchGenerateTestCasesResponse(BaseModel):
    overall_message: str
    tasks_initiated: List[GenerateTaskResponseItem]
    warning: Optional[str] = None


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

# --- API Routers ---
api_v1_router = APIRouter(prefix="/api/v1")

# --- Data Space Endpoints ---
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
    files: List[UploadFile] = File(..., description="Documents to upload to the new Data Space.")
):
    # 1. Check for existing Data Space by name (if names should be globally unique)
    # You might want to make uniqueness dependent on category/sub-category as well.
    if data_spaces_collection.find_one({"name": data_space_name}): # Basic check
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space with name '{data_space_name}' already exists.")

    now = datetime.now(IST)
    ds_doc_data = {
        "name": data_space_name, "description": data_space_description,
        "category": category, "sub_category": sub_category, # Store new fields
        "created_at": now, "updated_at": now, "document_ids": []
    }
    insert_ds_result = data_spaces_collection.insert_one(ds_doc_data)
    new_data_space_id_obj = insert_ds_result.inserted_id
    new_data_space_id_str = str(new_data_space_id_obj)

    if not files:
        return BatchUploadResponse(
            data_space_id=new_data_space_id_str, data_space_name=data_space_name,
            message="Data Space created. No files provided for upload.", uploaded_files={}, errors=None
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
            with open(file_path_on_disk, "wb") as f: f.write(await file.read())
            file_size = file_path_on_disk.stat().st_size
            doc_meta = {
                "data_space_id": new_data_space_id_obj, "file_name": original_filename, "file_path": str(file_path_on_disk),
                "content_type": file.content_type, "size": file_size, "status": -1, "timestamp": now,
                "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
                "last_task_id": None, "requested_test_case_types": []
            }
            insert_doc_res = documents_collection.insert_one(doc_meta)
            new_doc_obj_id = insert_doc_res.inserted_id
            uploaded_files_map[original_filename] = str(new_doc_obj_id)
            successfully_uploaded_doc_object_ids.append(new_doc_obj_id)
        except Exception as e:
            print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
            individual_file_errors.append({"filename": original_filename, "error": str(e)})
            uploaded_files_map[original_filename] = f"ERROR: {str(e)}"
            if os.path.exists(file_path_on_disk) and original_filename not in [k for k,v in uploaded_files_map.items() if "ERROR" not in v]:
                 try: os.remove(file_path_on_disk)
                 except Exception as e_del: print(f"Cleanup err {file_path_on_disk}: {e_del}")
        finally: await file.close()

    if successfully_uploaded_doc_object_ids:
        data_spaces_collection.update_one(
            {"_id": new_data_space_id_obj},
            {"$set": {"document_ids": successfully_uploaded_doc_object_ids, "updated_at": datetime.now(IST)}}
        )
    elif files: # Files were provided but none successful, still update 'updated_at'
         data_spaces_collection.update_one({"_id": new_data_space_id_obj}, {"$set": {"updated_at": datetime.now(IST)}})

    msg = f"Data Space '{data_space_name}' (Category: {category}, Sub-Category: {sub_category or 'N/A'}) created. "
    msg += f"{len(successfully_uploaded_doc_object_ids)} of {len(files)} files successfully uploaded and linked."
    if individual_file_errors: msg += " Some files encountered errors."
    
    return BatchUploadResponse(
        data_space_id=new_data_space_id_str, data_space_name=data_space_name, description= data_space_description, category= category, sub_category=sub_category,message=msg,
        uploaded_files=uploaded_files_map, errors=individual_file_errors if individual_file_errors else None
    )

@api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
async def list_data_spaces(skip: int = 0, limit: int = 20):
    spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
    return [
        DataSpaceResponse(
            data_space_id=str(ds_doc["_id"]),
            name=ds_doc.get("name"),
            description=ds_doc.get("description"),
            category=ds_doc.get("category"), # Include category in response
            sub_category=ds_doc.get("sub_category"), # Include sub_category
            created_at=ds_doc.get("created_at"),
            document_count=documents_collection.count_documents({"data_space_id": ds_doc["_id"]})
        ) for ds_doc in spaces_cursor
    ]

@api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
    try: ds_obj_id = ObjectId(data_space_id)
    except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")
    if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
    docs_cursor = documents_collection.find({"data_space_id": ds_obj_id}).sort("timestamp", -1).skip(skip).limit(limit)
    return [DocumentMetadataResponse(file_id=str(doc["_id"]), **doc) for doc in docs_cursor] # **doc assumes fields match

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
    file_ids_str: str = Form(..., alias="file_ids", description="Comma-separated file_ids."),
    model_name: Optional[str] = Form("Mistral"), chunk_size: Optional[int] = Query(None),
    api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
):
    actual_file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
    if not actual_file_ids: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")
    initiated_tasks_info: List[GenerateTaskResponseItem] = []
    api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
    if not api_key_to_use: raise HTTPException(status_code=400, detail="API key required.")
    warning_msg = "Using default API key." if not api_key and os.getenv("TOGETHER_API_KEY") else None
    types_to_send, types_for_resp = "all", INDIVIDUAL_VALID_TEST_CASE_TYPES[:]
    if test_case_types.strip().lower() != "all":
        parsed = [t.strip().lower() for t in test_case_types.split(',') if t.strip()]
        validated = list(dict.fromkeys(t for t in parsed if t in INDIVIDUAL_VALID_TEST_CASE_TYPES))
        if not validated: raise HTTPException(status_code=400, detail="No valid types.")
        types_to_send, types_for_resp = ",".join(validated), validated
    for current_file_id in actual_file_ids:
        try:
            doc_obj_id = ObjectId(current_file_id)
            document = documents_collection.find_one({"_id": doc_obj_id})
            if not document: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc not found.", error="Doc not found")); continue
            f_path_str = document.get("file_path")
            if not f_path_str or not Path(f_path_str).exists(): initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc file missing.", error="File missing")); continue
            documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"status":0, "selected_model":model_name, "api_key_used":f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST), "progress":["Batch gen task init."], "error_info":None, "last_task_id":None}})
            task = process_and_generate_task.apply_async(args=[str(Path(f_path_str)), model_name, chunk_size, api_key_to_use, types_to_send, current_file_id])
            documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
            initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id=task.id, message="✅ TC gen task started."))
        except InvalidId: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Invalid file_id.", error="Invalid file_id"))
        except Exception as e: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message=f"Failed: {type(e).__name__}.", error=str(e)))
    success_count = sum(1 for item in initiated_tasks_info if item.task_id != "N/A")
    return BatchGenerateTestCasesResponse(overall_message=f"Batch process done. {success_count}/{len(actual_file_ids)} tasks started.", tasks_initiated=initiated_tasks_info, warning=warning_msg)

@api_v1_router.get("/documents/{file_id}/get-test-cases/", tags=["Document Test Cases"])
async def get_test_cases_as_json_filtered_and_counted(
    file_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
    try: doc_obj_id = ObjectId(file_id)
    except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
    doc = documents_collection.find_one({"_id": doc_obj_id})
    if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    status_val = doc.get("status")
    base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name"), "req_gen_types":doc.get("requested_test_case_types",[])}
    empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}
    if status_val == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
    if status_val == 0: prog = doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
    if status_val == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
    if status_val != 1: return {**base_res, **empty_tc_res, "status_code":status_val or "unknown", "status_message":"unknown_status", "detail":f"Status: {status_val}"}
    try:
        _, all_r = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
        if not all_r: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
        final_r, applied_f = all_r, []
        if types:
            f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
            applied_f=[t.strip() for t in types.split(',') if t.strip()]
            if f_lower: final_r=[tc for tc in all_r if tc.get("Test type","").lower() in f_lower]
        cts = Counter(); total_c = 0
        if final_r:
            for tc_item in final_r:
                tt_val=tc_item.get("Test type")
                norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
                cts[norm_tt]+=1
            total_c=len(final_r)
        stat_msg, det_msg = "ready", "TCs retrieved."
        if types and applied_f and not final_r: stat_msg, det_msg = "ready_no_match", f"No TCs for filters: {applied_f}"
        elif types and applied_f: det_msg = f"Filtered by: {applied_f}"
        return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
    except HTTPException as http_e:
        if http_e.status_code==404 and "No test cases found" in http_e.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":http_e.detail}
        raise http_e
    except Exception as e_main: print(f"ERR GET TC {file_id}: {e_main}"); raise HTTPException(status_code=500, detail=f"Error processing TCs: {str(e_main)}")

@api_v1_router.get("/documents/{file_id}/test-case-summary/", tags=["Document Test Cases"])
async def get_document_test_case_summary(file_id: str):
    try: doc_obj_id = ObjectId(file_id)
    except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
    doc = documents_collection.find_one({"_id": doc_obj_id})
    if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    status_val = doc.get("status")
    base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name")}
    if status_val != 1: raise HTTPException(status_code=409, detail=f"Summary not available. Status: {status_val}")
    try:
        _, parsed_list = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
        if not parsed_list: return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, no TCs parsed."}
        cts = Counter(tc.get("Test type", "Not Specified") for tc in parsed_list)
        return {**base_res, "counts_by_type":dict(cts), "total_test_cases":len(parsed_list)}
    except Exception as e_sum: print(f"ERR SUMM {file_id}: {e_sum}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {str(e_sum)}")

@api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
async def download_test_cases_csv_for_document(file_id: str):
    try: doc_obj_id = ObjectId(file_id)
    except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
    doc = documents_collection.find_one({"_id": doc_obj_id})
    if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    if doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready.")
    fname = doc.get("file_name", "doc.pdf")
    csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
    if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV file missing post-parse.")
    return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

@api_v1_router.delete("/documents/", tags=["Document Test Cases"]) # Note: Query param for list of IDs
async def delete_multiple_documents(document_ids: List[str] = Query(...)):
    del_c, errs = 0, []
    for id_str in document_ids:
        try:
            obj_id = ObjectId(id_str)
            doc = documents_collection.find_one_and_delete({"_id":obj_id})
            if doc:
                del_c+=1
                if doc.get("file_path") and os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
                if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
                    csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{id_str}_test_cases.csv")
                    if os.path.exists(csv_p): os.remove(csv_p)
            else: errs.append({"id":id_str, "error":"Not found"})
        except InvalidId: errs.append({"id":id_str, "error":"Invalid ID"})
        except Exception as e_del: errs.append({"id":id_str, "error":str(e_del)})
    return {"deleted_count":del_c, "errors":errs}


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
    if len(api_key_suffix) < 5 : raise HTTPException(status_code=400, detail="Suffix too short.")
    rec = cost_collection.find_one({"api_key_suffix": api_key_suffix})
    if not rec: rec = cost_collection.find_one({"api_key": api_key_suffix}) 
    if not rec: return {"id":api_key_suffix, "tokens":0, "cost":0.0, "msg":"No usage data."}
    return {"id":rec.get("api_key_suffix",api_key_suffix), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_update":rec.get("last_updated","N/A")}

app.include_router(api_v1_router)

# --- WebSocket Endpoint ---
@app.websocket("/ws/v1/task_status/{task_id}")
async def websocket_task_status_endpoint(websocket: WebSocket, task_id: str):
    token = websocket.query_params.get("token")
    if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
    if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
    username = "ws_user_anon"
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
        username = payload.get("sub", "ws_user_no_sub")
    except Exception as e_auth_ws: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e_auth_ws}"}); await websocket.close(1008); return
    await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
    await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}"})
    task_mon = AsyncResult(task_id)
    try:
        while True:
            if websocket.client_state != WebSocketState.CONNECTED: break
            cel_stat = task_mon.state
            doc_info_ws = documents_collection.find_one({"last_task_id":task_id}, {"status":1, "progress":1, "error_info":1, "_id":1})
            db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None
            doc_id_ws = str(doc_info_ws["_id"]) if doc_info_ws else None
            resp_ws = {"tid":task_id, "cs":cel_stat, "dbs":db_stat_ws, "did":doc_id_ws}
            if cel_stat == "PENDING": resp_ws["i"] = "Pending"
            elif cel_stat == "STARTED": resp_ws["i"] = "Started"
            elif cel_stat == "PROGRESS": resp_ws["i"] = "Progress"; resp_ws["pd"] = task_mon.info;
            elif cel_stat == "SUCCESS":
                resp_ws["i"] = "SUCCESS (Celery)"; resp_ws["r"] = task_mon.result
                if doc_id_ws and db_stat_ws != 1: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":1, "error_info":None}, "$push":{"progress":"Celery SUCCESS via WS"}})
                await websocket.send_json(resp_ws); break
            elif cel_stat == "FAILURE":
                resp_ws["i"] = "FAILURE (Celery)"; resp_ws["ed"] = str(task_mon.info)
                if doc_id_ws and db_stat_ws != 2: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":2, "error_info":str(task_mon.info)}, "$push":{"progress":"Celery FAILURE via WS"}})
                await websocket.send_json(resp_ws); break
            elif cel_stat == "RETRY": resp_ws["i"] = "RETRY"; resp_ws["rr"] = str(task_mon.info)
            else: resp_ws["i"] = f"State: {cel_stat}"
            await websocket.send_json(resp_ws)
            if task_mon.ready():
                if cel_stat not in ["SUCCESS", "FAILURE"]:
                    final_resp_ws = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
                    if task_mon.state == "SUCCESS": final_resp_ws["r"] = task_mon.result
                    elif task_mon.state == "FAILURE": final_resp_ws["ed"] = str(task_mon.info)
                    await websocket.send_json(final_resp_ws)
                break
            await asyncio.sleep(2)
    except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
    except Exception as e_ws_main:
        print(f"WS Unhandled Error {task_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")
        if websocket.client_state == WebSocketState.CONNECTED:
            try: await websocket.send_json({"s":"error","m":"Server WS error."})
            except: pass
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            try: await websocket.close(code=status.WS_1001_GOING_AWAY)
            except RuntimeError: pass
        print(f"WS for task {task_id} ({username}) closed.")

# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn
    print(f"--- GenAI API (Full Integration with DataSpaces) Starting ---")
    print(f"MongoDB URL: {MONGODB_URL}, DB: {MONGO_DB_NAME}")
    print(f"Input DIR: {INPUT_DIR}, Output DIR: {OUTPUT_DIR}")
    if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
        Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        print(f"CSV Output DIR (utils): {test_case_utils.CSV_OUTPUT_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
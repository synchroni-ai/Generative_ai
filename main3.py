# # from fastapi import BackgroundTasks, HTTPException
# # from task_with_api_key import process_and_generate_task
# # from celery.result import AsyncResult
# # from fastapi import (
# #     FastAPI,
# #     UploadFile,
# #     File,
# #     HTTPException,
# #     Form,
# #     Query,
# #     status,
# #     WebSocket,
# #     APIRouter,
# #     WebSocketDisconnect,
# # )
# # from fastapi.responses import JSONResponse, FileResponse
# # from utils.jwt_auth import (
# #     create_jwt_token,
# # )
# # from pydantic import BaseModel

# # from fastapi.middleware.cors import CORSMiddleware
# # from typing import Optional, List, Dict
# # from dotenv import load_dotenv
# # from pymongo import MongoClient
# # from bson import ObjectId
# # from bson.errors import InvalidId
# # from pathlib import Path
# # import os
# # import re
# # import time
# # import uuid
# # import pandas as pd
# # from openpyxl import load_workbook
# # import csv
# # import asyncio  # For WebSocket polling sleep
# # from starlette.websockets import WebSocketState  # For checking WebSocket state
# # from collections import Counter # <<<<<<<<<<<<<<<<<<<<<<<<<<<< ADDED IMPORT


# # # Import your custom modules
# # from utils import data_ingestion, test_case_utils, user_story_utils
# # from utils.llms import Mistral, openai, llama
# # # from utils import test_case_utils # Already imported above
# # from core.websocket import websocket_endpoint # Assuming this exists and is correct
# # from datetime import datetime,timezone
# # from zoneinfo import ZoneInfo

# # # Load environment variables from .env file
# # load_dotenv() # Ensure .env is loaded if you haven't elsewhere

# # mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# # db = mongo_client["Gen_AI"]
# # collection = db["test_case_generation"]
# # cost_collection = db["cost_tracking"]


# # def serialize_document(doc):
# #     doc["_id"] = str(doc["_id"])
# #     return {
# #         # "_id": str(doc["_id"]),
# #         "file_id": str(doc["_id"]),
# #         "file_name": doc.get("file_name"),
# #         "file_path": doc.get("file_path"),
# #         "status": doc.get("status"),
# #         "selected_model": doc.get("selected_model", None),
# #         "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None, # Added timestamp serialization
# #         "last_task_id": doc.get("last_task_id") # Added last_task_id
# #     }
# # IST = ZoneInfo("Asia/Kolkata")

# # # ----------------- Directories Setup -----------------
# # TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
# # USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH") # This seems to be the same as above, check if intended
# # INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# # OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# # EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

# # # Create directories if they don't exist
# # Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


# # app = FastAPI()

# # # Enable CORS
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )


# # VALID_TEST_CASE_TYPES = [
# #     "functional",
# #     "non-functional",
# #     "security",
# #     "performance",
# #     "boundary",
# #     "compliance",
# #     "all" # Added 'all' here as it's a valid input, though handled specially
# # ]
# # class DataSpaceCreate(BaseModel):
# #     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
# #     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# # class DataSpaceResponse(BaseModel):
# #     data_space_id: str
# #     name: str
# #     description: Optional[str]
# #     created_at: datetime
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True # For Pydantic v2
# # # --- New Router for Data Space Creation ---
# # data_space_creation_router = APIRouter(prefix="/api/v1", tags=["Data Spaces"])

# # @data_space_creation_router.post("/data-spaces/", response_model=DataSpaceResponse, status_code=status.HTTP_201_CREATED)
# # async def create_new_data_space(data_space_input: DataSpaceCreate):
# #     existing_space = data_spaces_collection.find_one({"name": data_space_input.name})
# #     if existing_space:
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_input.name}' already exists.")
# #     current_time = datetime.now(IST)
# #     ds_doc_data = data_space_input.dict()
# #     ds_doc_data["created_at"] = current_time
# #     insert_result = data_spaces_collection.insert_one(ds_doc_data)
# #     created_doc = data_spaces_collection.find_one({"_id": insert_result.inserted_id})
# #     if not created_doc:
# #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data space post-creation.")
# #     return DataSpaceResponse(data_space_id=str(created_doc["_id"]), **created_doc)

# # app.include_router(data_space_creation_router)
# # @app.post("/upload_document/")
# # async def upload_document(file: UploadFile = File(...)):
# #     file_name = file.filename
# #     file_path = Path(INPUT_DIR) / file_name

# #     try:
# #         contents = await file.read()
# #         with open(file_path, "wb") as f:
# #             f.write(contents)
# #     finally:
# #         await file.close()
# #     upload_time = datetime.now(IST)


# #     # Insert file metadata into MongoDB
# #     document_data = {
# #         "file_name": file_name,
# #         "file_path": str(file_path),
# #         "status": -1,  # Document uploaded but not processed
# #         "timestamp": upload_time
# #     }

# #     result = collection.insert_one(document_data)
# #     file_id = str(result.inserted_id)

# #     return {
# #         "message": "File uploaded successfully",
# #         "file_name": file_name,
# #         "file_path": str(file_path),
# #         "file_id": file_id,
# #         "timestamp": upload_time.isoformat()
# #     }


# # @app.post("/generate_test_cases/")
# # async def generate_test_cases(
# #     file_id: str = Form(...),
# #     model_name: Optional[str] = Form("Mistral"),
# #     chunk_size: Optional[int] = Query(default=None),
# #     cache_key: Optional[str] = Query(default=None),
# #     api_key: Optional[str] = Form(None),
# #     test_case_types: Optional[str] = Form("all"),  # ✅ Accepts 'all' or comma-separated string like "functional,security"
# # ):
# #     # ✅ Step 1: Fetch the document from MongoDB
# #     try:
# #         document = collection.find_one({"_id": ObjectId(file_id)})
# #     except Exception:
# #         raise HTTPException(status_code=400, detail="Invalid file_id format.")
 
# #     if not document:
# #         raise HTTPException(status_code=404, detail="Document not found in the database.")
 
# #     # ✅ Step 2: Ensure file path exists
# #     file_path = Path(document.get("file_path"))
# #     if not file_path.exists():
# #         raise HTTPException(status_code=404, detail="File not found on disk.")
 
# #     # ✅ Step 3: Parse and validate `test_case_types`
# #     if test_case_types.strip().lower() == "all":
# #         # If user requested all test cases, set full list
# #         test_case_types_to_send = "all"
# #         test_case_types_list = VALID_TEST_CASE_TYPES
# #     else:
# #         # ✅ Split and validate comma-separated input
# #         test_case_types_list = [t.strip().lower() for t in test_case_types.split(",")]
 
# #         # ✅ Check for any invalid test case types
# #         invalid_types = [t for t in test_case_types_list if t not in VALID_TEST_CASE_TYPES]
# #         if invalid_types:
# #             raise HTTPException(
# #                 status_code=400,
# #                 detail=f"Invalid test_case_type(s): {invalid_types}. Must be one of {VALID_TEST_CASE_TYPES} or 'all'.",
# #             )
 
# #         # ✅ Convert back to comma-separated string for Celery compatibility
# #         test_case_types_to_send = ",".join(test_case_types_list)
 
# #     # ✅ Step 4: Fallback to default API key if user hasn't supplied one
# #     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
# #     warning = (
# #         "Using default API key. Consider providing your own to avoid shared limits."
# #         if not api_key else None
# #     )
 
# #     # ✅ Step 5: Set status = 0 (processing) in MongoDB
# #     collection.update_one(
# #         {"_id": ObjectId(file_id)},
# #         {
# #             "$set": {
# #                 "status": 0,
# #                 "selected_model": model_name,
# #                 "api_key_used": f"...{api_key_to_use[-5:]}",  # Mask key
# #             }
# #         },
# #     )
 
# #     # ✅ Step 6: Trigger Celery task (passes either "all" or comma-separated string)
# #     task = process_and_generate_task.apply_async(args=[
# #         str(file_path),             # file_path
# #         model_name,                 # model_name
# #         chunk_size,                 # chunk_size
# #         api_key_to_use,             # api_key
# #         test_case_types_to_send,    # "all" or "functional,security"
# #         file_id,                    # document_id
# #     ])
 
# #     # ✅ Save task ID to DB for tracking
# #     collection.update_one(
# #         {"_id": ObjectId(file_id)}, {"$set": {"last_task_id": task.id}}
# #     )
 
# #     # ✅ Step 7: Return response
# #     return {
# #         "message": "✅ Test case generation task started.",
# #         "task_id": task.id,
# #         "file_id": file_id,
# #         "test_case_types": test_case_types_list,  # Return list even if user passed 'all'
# #         "api_key_being_used": f"...{api_key_to_use[-5:]}",
# #         "warning": warning,
# #     }
 
 


# # @app.get("/documents/")
# # def get_all_documents():
# #     # Sort by timestamp descending to get newest first
# #     documents = list(collection.find().sort("timestamp", -1))
# #     return [serialize_document(doc) for doc in documents]


# # @app.get("/documents/{document_id}")
# # def get_document_by_id(document_id: str):
# #     try:
# #         doc_object_id = ObjectId(document_id)
# #     except InvalidId:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
# #         )

# #     doc = collection.find_one({"_id": doc_object_id})
# #     if not doc:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
# #         )
# #     return serialize_document(doc)


# # @app.delete("/delete-documents")
# # async def delete_documents(document_ids: List[str] = Query(...)): # Changed to Query for GET-like delete or use Body for proper DELETE
# #     deleted_ids = []
# #     errors = []
# #     for document_id in document_ids:
# #         try:
# #             doc_object_id = ObjectId(document_id)
# #             doc = collection.find_one({"_id": doc_object_id})
# #             if not doc:
# #                 errors.append({"id": document_id, "error": "Document not found"})
# #                 continue

# #             # Delete associated files (input PDF, output CSV)
# #             input_file_path = doc.get("file_path")
# #             if input_file_path and os.path.exists(input_file_path):
# #                 try:
# #                     os.remove(input_file_path)
# #                 except Exception as e:
# #                     errors.append({"id": document_id, "error": f"Could not delete input file {input_file_path}: {e}"})
            
# #             # Construct potential CSV output path based on your test_case_utils.CSV_OUTPUT_DIR
# #             # This assumes test_case_utils.CSV_OUTPUT_DIR is accessible or defined here
# #             # For robustness, this path should ideally be stored in the document metadata upon CSV creation
# #             csv_output_path = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{document_id}_test_cases.csv")
# #             if os.path.exists(csv_output_path):
# #                 try:
# #                     os.remove(csv_output_path)
# #                 except Exception as e:
# #                      errors.append({"id": document_id, "error": f"Could not delete output CSV file {csv_output_path}: {e}"})


# #             result = collection.delete_one({"_id": doc_object_id})
# #             if result.deleted_count > 0:
# #                 deleted_ids.append(document_id)
# #             else: # Should not happen if find_one found it, but as a safeguard
# #                 errors.append({"id": document_id, "error": "Document found but failed to delete from DB"})
# #         except InvalidId:
# #             errors.append({"id": document_id, "error": "Invalid document ID format"})
# #         except Exception as e:
# #             errors.append({"id": document_id, "error": str(e)})

# #     response_message = ""
# #     if deleted_ids:
# #         response_message += f"{len(deleted_ids)} document(s) deleted successfully: {', '.join(deleted_ids)}. "
# #     if errors:
# #         response_message += f"Errors occurred for some documents."
# #         return JSONResponse(
# #             content={"message": response_message, "deleted": deleted_ids, "errors": errors},
# #             status_code=status.HTTP_207_MULTI_STATUS if deleted_ids else status.HTTP_400_BAD_REQUEST ,
# #         )
    
# #     if not deleted_ids and not errors: # Should not happen if document_ids is not empty
# #         return JSONResponse(content={"message": "No documents specified for deletion."}, status_code=status.HTTP_400_BAD_REQUEST)

# #     return JSONResponse(
# #         content={"message": response_message, "deleted": deleted_ids},
# #         status_code=status.HTTP_200_OK,
# #     )


# # router = APIRouter()


# # @router.get("/get-test-cases/{document_id}", tags=["Test Cases"])
# # async def get_test_cases_as_json_filtered_and_counted( # Renamed for clarity
# #     document_id: str,
# #     types: Optional[str] = Query(None, description="Filter test cases by a comma-separated list of types (e.g., 'functional,security')."),
# #     # 'collection' should ideally be injected using FastAPI's Depends
# # ):
# #     """
# #     Retrieves generated test cases for a document.
# #     By default (no 'types' param), returns all available test cases.
# #     Can be filtered by providing a 'types' query parameter.
# #     The response includes counts for the returned (filtered) test cases.
# #     e.g., /get-test-cases/some_id?types=functional,security
# #     """
# #     # Placeholder for DB collection access
# #     from main3 import collection # Assuming collection is importable for this example

# #     try:
# #         doc_object_id = ObjectId(document_id)
# #     except InvalidId:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format.")

# #     doc = collection.find_one({"_id": doc_object_id})
# #     if not doc:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

# #     doc_status = doc.get("status")
# #     requested_during_generation = doc.get("requested_test_case_types", [])
# #     base_response = {
# #         "document_id": document_id,
# #         "requested_test_case_types_during_generation": requested_during_generation
# #     }

# #     # Handle non-completed statuses first
# #     if doc_status == -1:
# #         return {**base_response, "status_code": doc_status, "status_message": "pending_generation", "detail": "Test case generation has not been initiated."}
# #     elif doc_status == 0:
# #         progress = doc.get("progress", [])
# #         last_progress = progress[-1] if progress else "Processing test cases..."
# #         return {**base_response, "status_code": doc_status, "status_message": "processing", "detail": last_progress, "progress_log": progress}
# #     elif doc_status == 2:
# #         error_info = doc.get("error_info", "An unspecified error occurred.")
# #         return {**base_response, "status_code": doc_status, "status_message": "error", "detail": f"Test case generation failed: {error_info}"}
# #     elif doc_status != 1: # Any other unknown status
# #         return {**base_response, "status_code": doc_status if doc_status is not None else "unknown", "status_message": "unknown_status", "detail": f"Document is in an unknown state (status: {doc_status})."}

# #     # Proceed if doc_status is 1 (Completed)
# #     try:
# #         _, all_parsed_rows = test_case_utils.parse_test_cases_to_csv(document_id, collection)

# #         if not all_parsed_rows:
# #             return {
# #                 **base_response,
# #                 "status_code": doc_status,
# #                 "status_message": "completed_no_data",
# #                 "detail": "Generation completed, but no test cases were found or parsed from the document.",
# #                 "test_cases": [],
# #                 "counts_by_type": {},
# #                 "total_test_cases": 0
# #             }

# #         # --- Filtering Logic for comma-separated 'types' string ---
# #         final_rows_to_return = all_parsed_rows
# #         applied_filter_types_list = []

# #         if types:
# #             filter_types_lower = [t.strip().lower() for t in types.split(',') if t.strip()]
# #             applied_filter_types_list = [t.strip() for t in types.split(',') if t.strip()]

# #             if filter_types_lower:
# #                 final_rows_to_return = [
# #                     tc for tc in all_parsed_rows
# #                     if tc.get("Test type", "").lower() in filter_types_lower
# #                 ]
        
# #         # --- Counting Logic for the final_rows_to_return ---
# #         test_type_counts = Counter()
# #         if final_rows_to_return: # Only count if there are rows to count
# #             for tc in final_rows_to_return:
# #                 test_type_value = tc.get("Test type")
# #                 if test_type_value is None or not str(test_type_value).strip() or str(test_type_value).strip().upper() == "N/A":
# #                     normalized_test_type = "Not Specified"
# #                 else:
# #                     normalized_test_type = str(test_type_value).strip()
# #                 test_type_counts[normalized_test_type] += 1
        
# #         total_returned_test_cases = len(final_rows_to_return)
# #         # --- End Counting Logic ---

# #         status_message = "ready"
# #         detail_message = "Test cases retrieved successfully."

# #         if types and applied_filter_types_list and not final_rows_to_return:
# #             status_message = "ready_no_match_for_filter"
# #             detail_message = f"Generation completed. No test cases matched the filter types: {applied_filter_types_list}"
# #         elif types and applied_filter_types_list:
# #             detail_message = f"Test cases retrieved and filtered by: {applied_filter_types_list}"


# #         return {
# #             **base_response,
# #             "status_code": doc_status,
# #             "status_message": status_message,
# #             "detail": detail_message,
# #             "filter_applied_types": applied_filter_types_list if types else "None (all available shown)",
# #             "test_cases": final_rows_to_return,
# #             "counts_by_type": dict(test_type_counts), # Counts for the returned (filtered) TCs
# #             "total_test_cases": total_returned_test_cases # Total for the returned (filtered) TCs
# #         }

# #     except HTTPException as he: # Catch specific errors from parse_test_cases_to_csv
# #         if he.status_code == 404 and "No test cases found" in he.detail:
# #             return {
# #                 **base_response,
# #                 "status_code": doc_status,
# #                 "status_message": "completed_no_data", # Original error from parser
# #                 "detail": he.detail,
# #                 "test_cases": [],
# #                 "counts_by_type": {},
# #                 "total_test_cases": 0
# #             }
# #         raise he # Re-raise other HTTPExceptions
# #     except Exception as e:
# #         print(f"Error processing or counting test cases for doc {document_id}: {e}")
# #         raise HTTPException(
# #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             detail=f"Failed to process or count test cases: {str(e)}"
# #         )

# # # >>>>>>>>>>>>>>>>>>>>> NEW ENDPOINT START <<<<<<<<<<<<<<<<<<<<<<<
# # @router.get("/test-case-summary/{document_id}")
# # async def get_test_case_summary(document_id: str):
# #     try:
# #         doc_object_id = ObjectId(document_id)
# #     except InvalidId:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
# #         )

# #     doc = collection.find_one({"_id": doc_object_id})
# #     if not doc:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
# #         )

# #     doc_status = doc.get("status")
# #     if doc_status == -1:
# #         raise HTTPException(
# #             status_code=status.HTTP_409_CONFLICT,
# #             detail="Test case generation has not been initiated for this document. Summary not available."
# #         )
# #     if doc_status == 0:
# #         raise HTTPException(
# #             status_code=status.HTTP_425_TOO_EARLY,
# #             detail="Test case generation is still in progress. Summary will be available once completed."
# #         )
# #     if doc_status == 2: # Error state
# #         error_info = doc.get("error_info", "Processing failed.")
# #         raise HTTPException(
# #             status_code=status.HTTP_409_CONFLICT,
# #             detail=f"Test case generation failed for this document: {error_info}. Summary not available."
# #         )
# #     if doc_status != 1: # Any other non-completed status
# #         raise HTTPException(
# #             status_code=status.HTTP_409_CONFLICT,
# #             detail=f"Document status is '{doc_status}'. Summary is only available for completed generations."
# #         )

# #     # If status is 1 (completed), proceed to parse and summarize
# #     try:
# #         # We don't need the csv_path here, only the rows (parsed test cases)
# #         _, parsed_test_cases = test_case_utils.parse_test_cases_to_csv(document_id, collection)
# #     except HTTPException as e:
# #         # If parse_test_cases_to_csv itself raises an HTTPException (e.g., no test cases found in doc)
# #         raise e
# #     except Exception as e:
# #         # Log this unexpected error during parsing for summary
# #         print(f"Error parsing test cases for summary (doc_id: {document_id}): {e}")
# #         raise HTTPException(status_code=500, detail="Error processing test cases for summary.")

# #     if not parsed_test_cases:
# #         return {
# #             "document_id": document_id,
# #             "counts_by_type": {},
# #             "total_test_cases": 0,
# #             "message": "No test cases were parsed from this document, although it's marked as completed."
# #         }

# #     test_type_counts = Counter()
# #     for tc in parsed_test_cases:
# #         # The key "Test type" comes from your CSV_HEADERS in test_case_utils.py
# #         test_type = tc.get("Test type", "Unknown")  # Default to "Unknown" if key is missing
# #         if test_type == "N/A" or not test_type.strip(): # Handle "N/A" or empty strings
# #             test_type = "Not Specified"
# #         test_type_counts[test_type] += 1
    
# #     total_test_cases = len(parsed_test_cases)
        
# #     return {
# #         "document_id": document_id,
# #         "counts_by_type": dict(test_type_counts), # Convert Counter to dict for JSON response
# #         "total_test_cases": total_test_cases
# #     }
# # # >>>>>>>>>>>>>>>>>>>>> NEW ENDPOINT END <<<<<<<<<<<<<<<<<<<<<<<<<


# # app.include_router(router)


# # @app.get("/download-csv/{document_id}")
# # def download_test_cases_csv(document_id: str):
# #     try:
# #         doc_object_id = ObjectId(document_id)
# #     except InvalidId:
# #         raise HTTPException(status_code=400, detail="Invalid document ID format")

# #     doc = collection.find_one({"_id": doc_object_id})
# #     if not doc:
# #         raise HTTPException(status_code=404, detail="Document not found")
    
# #     doc_status = doc.get("status")
# #     if doc_status != 1:
# #         status_message = "not completed"
# #         if doc_status == 0: status_message = "still processing"
# #         elif doc_status == -1: status_message = "generation not started"
# #         elif doc_status == 2: status_message = f"failed ({doc.get('error_info', 'unknown error')})"
# #         raise HTTPException(status_code=409, detail=f"Cannot download CSV. Test case generation is {status_message}.")


# #     original_file_name = doc.get("file_name", "document.pdf")

# #     try:
# #         csv_path, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
# #     except HTTPException as e: # Catch specific errors from parsing, e.g. no test cases
# #         raise e
# #     except Exception as e:
# #         print(f"Error generating CSV for download (doc_id: {document_id}): {e}")
# #         raise HTTPException(status_code=500, detail=f"Failed to generate CSV file: {str(e)}")

# #     if not os.path.exists(csv_path):
# #         # This case should ideally be caught by parse_test_cases_to_csv if no TCs found
# #         raise HTTPException(status_code=404, detail=f"CSV file not found at {csv_path}. Parsing might have failed or produced no data.")

# #     csv_file_name = f"{Path(original_file_name).stem}_test_cases.csv"

# #     return FileResponse(
# #         csv_path,
# #         media_type="text/csv",
# #         filename=csv_file_name,
# #     )


# # @app.get("/api_key_usage/{api_key}") # Consider making this POST if API key is sensitive
# # def get_api_key_cost(api_key: str):
# #     # For security, avoid exposing full API keys in GET requests if possible.
# #     # If this is for admin use, ensure proper auth.
# #     # A hashed version or an internal ID for the key might be safer if user-facing.
# #     record = cost_collection.find_one({"api_key_suffix": api_key[-5:]}) # Example: query by suffix
# #     if not record:
# #          # If querying by full key:
# #         record = cost_collection.find_one({"api_key": api_key})
# #         if not record:
# #             return {"api_key_identifier": api_key[-5:], "tokens_used": 0, "cost_usd": 0.0, "message": "No usage data found for this API key identifier."}
    
# #     return {
# #         "api_key_identifier": record.get("api_key_suffix", api_key[-5:]),
# #         "tokens_used": record.get("tokens_used", 0),
# #         "cost_usd": round(record.get("cost_usd", 0.0), 6), # Increased precision
# #         "last_updated": record.get("last_updated", "N/A") # Added last_updated
# #     }

# # SECRET_KEY = os.getenv("SECRET_KEY")
# # ALGORITHM = "HS256"

# # if not SECRET_KEY:
# #     print(
# #         "WARNING: SECRET_KEY environment variable is not set. JWT authentication for WebSockets will fail."
# #     )

# # @app.websocket("/ws/task_status/{task_id}")
# # async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
# #     token = websocket.query_params.get("token")

# #     if not SECRET_KEY:
# #         await websocket.accept()
# #         await websocket.send_json(
# #             {"status": "error", "message": "Server configuration error: JWT secret not set."}
# #         )
# #         await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
# #         return

# #     if not token:
# #         await websocket.accept()
# #         await websocket.send_json(
# #             {"status": "error", "message": "Authentication token missing."}
# #         )
# #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
# #         return

# #     username = None # Initialize username
# #     try:
# #         from jose import jwt, JWTError
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         username = payload.get("sub")
# #         if not username:
# #             await websocket.accept()
# #             await websocket.send_json(
# #                 {"status": "error", "message": "Invalid token: Subject missing."}
# #             )
# #             await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
# #             return
# #     except JWTError as e:
# #         await websocket.accept()
# #         await websocket.send_json(
# #             {"status": "error", "message": f"Authentication failed: {str(e)}"}
# #         )
# #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
# #         return
# #     except ImportError:
# #         await websocket.accept()
# #         await websocket.send_json(
# #             {"status": "error", "message": "Server configuration error: JWT library not available."}
# #         )
# #         await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
# #         return


# #     await websocket.accept()
# #     # Log WebSocket connection
# #     print(f"WebSocket connected for task {task_id}, user: {username}")
# #     await websocket.send_json(
# #         {
# #             "status": "connected",
# #             "message": f"Authenticated as {username}. Monitoring task {task_id}.",
# #         }
# #     )

# #     task_monitor = AsyncResult(task_id)
# #     try:
# #         while True:
# #             if websocket.client_state != WebSocketState.CONNECTED:
# #                 print(f"WebSocket for task {task_id} (User: {username}) disconnected by client.")
# #                 break

# #             task_state = task_monitor.state
# #             # Fetch the latest document status from DB for more context
# #             doc_db_info = collection.find_one({"last_task_id": task_id}, {"status": 1, "progress": 1, "error_info": 1})
# #             db_status = doc_db_info.get("status") if doc_db_info else None
            
# #             response_data = {"task_id": task_id, "celery_status": task_state, "db_doc_status": db_status}

# #             if task_state == "PENDING":
# #                 response_data["info"] = "Task is waiting to be processed by a worker."
# #             elif task_state == "STARTED":
# #                 response_data["info"] = "Task has been picked up by a worker and started."
# #             elif task_state == "PROGRESS":
# #                 response_data["info"] = "Task is in progress."
# #                 # Celery task must use self.update_state(state='PROGRESS', meta={'current': i, 'total': n, 'status': 'details'})
# #                 response_data["progress_details"] = task_monitor.info 
# #                 if doc_db_info and "progress" in doc_db_info:
# #                      response_data["db_progress_log"] = doc_db_info["progress"]
# #             elif task_state == "SUCCESS":
# #                 response_data["info"] = "Task completed successfully."
# #                 response_data["result"] = task_monitor.result # Result from Celery task return
# #                 await websocket.send_json(response_data)
# #                 break 
# #             elif task_state == "FAILURE":
# #                 response_data["info"] = "Task failed."
# #                 response_data["error_details"] = str(task_monitor.info) # Exception info from Celery
# #                 if doc_db_info and "error_info" in doc_db_info:
# #                     response_data["db_error_info"] = doc_db_info["error_info"]
# #                 await websocket.send_json(response_data)
# #                 break
# #             elif task_state == "RETRY":
# #                 response_data["info"] = "Task is being retried."
# #                 response_data["retry_reason"] = str(task_monitor.info)

# #             await websocket.send_json(response_data)

# #             if task_monitor.ready(): # Task is definitively finished (SUCCESS, FAILURE)
# #                 # Ensure final state is sent if loop condition missed it for some reason
# #                 if task_state not in ["SUCCESS", "FAILURE"]:
# #                     final_state = task_monitor.state
# #                     final_response = {"task_id": task_id, "celery_status": final_state, "info": "Task reached final state."}
# #                     if final_state == "SUCCESS": final_response["result"] = task_monitor.result
# #                     elif final_state == "FAILURE": final_response["error_details"] = str(task_monitor.info)
# #                     await websocket.send_json(final_response)
# #                 break
            
# #             await asyncio.sleep(2)

# #     except WebSocketDisconnect:
# #         print(f"Client {username} (task: {task_id}) disconnected gracefully.")
# #     except Exception as e:
# #         print(
# #             f"Unexpected error in WebSocket for task {task_id} (User: {username}): {type(e).__name__} - {e}"
# #         )
# #         import traceback
# #         traceback.print_exc()
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try:
# #                 await websocket.send_json(
# #                     {"status": "error", "message": "An unexpected server error occurred while monitoring the task."}
# #                 )
# #             except Exception as send_err:
# #                  print(f"Error sending WebSocket error message: {send_err}")
# #     finally:
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try:
# #                 await websocket.close(code=status.WS_1001_GOING_AWAY)
# #             except RuntimeError: # Already closed
# #                 pass
# #         print(f"WebSocket connection for task {task_id} (User: {username}) definitively closed.")


# # class TokenRequest(BaseModel):
# #     username: str
# #     password: str # In a real app, never log passwords or send them around more than necessary


# # @app.post("/get_token", tags=["Authentication"])
# # async def get_token_post(request: TokenRequest):
# #     if not request.username or not request.password:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Username and password required",
# #         )

# #     # IMPORTANT: Replace with real DB/user authentication and password hashing
# #     # DO NOT use plain text password comparison in production. Use something like passlib.
# #     if request.username == os.getenv("ADMIN_USERNAME", "admin") and \
# #        request.password == os.getenv("ADMIN_PASSWORD", "admin123"): # Load credentials from env
        
# #         token_data = {"sub": request.username, "role": "admin"} # Add role or other claims
# #         try:
# #             if not SECRET_KEY:
# #                  raise ValueError("JWT_SECRET_KEY is not configured on the server.")
# #             token = create_jwt_token(token_data) # Assuming create_jwt_token uses SECRET_KEY and ALGORITHM
# #             return {"access_token": token, "token_type": "bearer"}
# #         except Exception as e:
# #             print(f"Error generating token: {e}")
# #             raise HTTPException(
# #                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #                 detail="Could not generate token due to server error.",
# #             )
# #     else:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
# #         )

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)

# # from fastapi import BackgroundTasks, HTTPException
# # from task_with_api_key import process_and_generate_task
# # from celery.result import AsyncResult
# # from fastapi import (
# #     FastAPI,
# #     UploadFile,
# #     File,
# #     HTTPException,
# #     Form,
# #     Query,
# #     status,
# #     WebSocket,
# #     APIRouter,
# #     WebSocketDisconnect,
# # )
# # from fastapi.responses import JSONResponse, FileResponse
# # from utils.jwt_auth import (
# #     create_jwt_token,
# # )
# # from pydantic import BaseModel, Field # Added Field
# # from pymongo.collection import Collection # For type hinting

# # from fastapi.middleware.cors import CORSMiddleware
# # from typing import Optional, List, Dict, Any # Added Any
# # from dotenv import load_dotenv
# # from pymongo import MongoClient
# # from bson import ObjectId
# # from bson.errors import InvalidId
# # from pathlib import Path
# # import os
# # import re
# # # import time # Not used directly
# # # import uuid # Not used directly
# # # import pandas as pd
# # # from openpyxl import load_workbook
# # # import csv
# # import asyncio
# # from starlette.websockets import WebSocketState
# # from collections import Counter


# # # Import your custom modules
# # from utils import data_ingestion, test_case_utils, user_story_utils
# # from utils.llms import Mistral, openai, llama
# # # from core.websocket import websocket_endpoint # Your WS is inline

# # from datetime import datetime, timezone as dt_timezone
# # from zoneinfo import ZoneInfo

# # load_dotenv()

# # # --- MongoDB Setup ---
# # mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# # db = mongo_client[os.getenv("MONGO_DB_NAME", "Gen_AI")]
# # collection: Collection = db["test_case_generation"]
# # data_spaces_collection: Collection = db["data_spaces"]
# # cost_collection: Collection = db["cost_tracking"]

# # # --- Pydantic Models ---
# # class DataSpaceCreate(BaseModel):
# #     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
# #     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# # class DataSpaceResponse(BaseModel):
# #     data_space_id: str
# #     name: str
# #     description: Optional[str]
# #     created_at: datetime
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True # For Pydantic v2

# # class TokenRequest(BaseModel): # DEFINITION OF TokenRequest
# #     username: str
# #     password: str

# # # --- Serialization Function (Your Existing One) ---
# # def serialize_document(doc_data: dict): # Changed param name for clarity
# #     return {
# #         "file_id": str(doc_data["_id"]),
# #         "file_name": doc_data.get("file_name"),
# #         "file_path": doc_data.get("file_path"),
# #         "status": doc_data.get("status"),
# #         "selected_model": doc_data.get("selected_model", None),
# #         "timestamp": doc_data.get("timestamp").isoformat() if isinstance(doc_data.get("timestamp"), datetime) else str(doc_data.get("timestamp")),
# #         "last_task_id": doc_data.get("last_task_id")
# #     }

# # IST = ZoneInfo("Asia/Kolkata")

# # # --- Directories Setup ---
# # INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# # OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# # # EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

# # Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# # # Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# # app = FastAPI(title="GenAI API - Minimal Data Space Integration")
# # app.add_middleware(
# #     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
# #     allow_methods=["*"], allow_headers=["*"],
# # )

# # VALID_TEST_CASE_TYPES = [
# #     "functional", "non-functional", "security", "performance",
# #     "boundary", "compliance", "all"
# # ]
# # INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES if t != "all"]


# # # --- New Router for Data Space Creation ---
# # data_space_creation_router = APIRouter(prefix="/api/v1", tags=["Data Spaces"])

# # @data_space_creation_router.post("/data-spaces/", response_model=DataSpaceResponse, status_code=status.HTTP_201_CREATED)
# # async def create_new_data_space(data_space_input: DataSpaceCreate):
# #     existing_space = data_spaces_collection.find_one({"name": data_space_input.name})
# #     if existing_space:
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_input.name}' already exists.")
# #     current_time = datetime.now(IST)
# #     ds_doc_data = data_space_input.dict()
# #     ds_doc_data["created_at"] = current_time
# #     insert_result = data_spaces_collection.insert_one(ds_doc_data)
# #     created_doc = data_spaces_collection.find_one({"_id": insert_result.inserted_id})
# #     if not created_doc:
# #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data space post-creation.")
# #     return DataSpaceResponse(data_space_id=str(created_doc["_id"]), **created_doc)

# # app.include_router(data_space_creation_router)

# # # --- Your Existing Endpoints ---
# # @app.post("/upload_document/")
# # async def upload_document_legacy(file: UploadFile = File(...)):
# #     file_name = file.filename
# #     base, ext = os.path.splitext(file.filename)
# #     sanitized_base = re.sub(r'[^\w\.-]', '_', base)
# #     unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
# #     file_path = Path(INPUT_DIR) / unique_filename_on_disk
# #     try:
# #         with open(file_path, "wb") as f: f.write(await file.read())
# #     except Exception as e: raise HTTPException(status_code=500, detail=f"Save err: {e}")
# #     finally: await file.close()
# #     upload_time = datetime.now(IST)
# #     doc_data = {"file_name": file.filename, "file_path": str(file_path), "status": -1, "timestamp": upload_time, "data_space_id": None}
# #     result = collection.insert_one(doc_data)
# #     return {"message": "File uploaded (legacy, no Data Space link).", "file_name": file.filename, "file_path": str(file_path), "file_id": str(result.inserted_id), "timestamp": upload_time.isoformat()}

# # @app.post("/generate_test_cases/")
# # async def generate_test_cases(
# #     file_id: str = Form(...), model_name: Optional[str] = Form("Mistral"),
# #     chunk_size: Optional[int] = Query(default=None), #cache_key: Optional[str] = Query(default=None),
# #     api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
# # ):
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     document = collection.find_one({"_id": doc_obj_id})
# #     if not document: raise HTTPException(status_code=404, detail="Doc not found.")
# #     f_path_str = document.get("file_path")
# #     if not f_path_str or not Path(f_path_str).exists(): raise HTTPException(status_code=404, detail="Doc file missing.")
    
# #     types_to_send, types_for_resp = "all", [t for t in VALID_TEST_CASE_TYPES if t != "all"]
# #     req_types_str = test_case_types.strip().lower()
# #     if req_types_str != "all":
# #         parsed = [t.strip().lower() for t in test_case_types.split(",")]
# #         validated = []
# #         for t_type in parsed:
# #             if t_type not in INDIVIDUAL_VALID_TEST_CASE_TYPES: # Use individual list for validation
# #                 raise HTTPException(status_code=400, detail=f"Invalid type: '{t_type}'. Valid: {INDIVIDUAL_VALID_TEST_CASE_TYPES}")
# #             if t_type not in validated: validated.append(t_type)
# #         if not validated: raise HTTPException(status_code=400, detail="No valid specific types.")
# #         types_to_send, types_for_resp = ",".join(validated), validated
    
# #     key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
# #     warn_msg = None
# #     if not key_to_use: raise HTTPException(status_code=400, detail="API key required.")
# #     if not api_key and os.getenv("TOGETHER_API_KEY"): warn_msg = "Using default API key."
    
# #     collection.update_one({"_id": doc_obj_id}, {"$set": {
# #         "status":0, "selected_model":model_name, "api_key_used":f"...{key_to_use[-5:]}" if key_to_use else "N/A",
# #         "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST),
# #         "progress":["Task init."], "error_info":None, "last_task_id":None }})
# #     task = process_and_generate_task.apply_async(args=[
# #         str(Path(f_path_str)), model_name, chunk_size, key_to_use, types_to_send, file_id])
# #     collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
# #     return {"message":"✅ TC gen task started.", "task_id":task.id, "file_id":file_id, "test_case_types_being_generated":types_for_resp, "api_key_being_used":f"...{key_to_use[-5:]}" if key_to_use else "N/A", "warning":warn_msg}

# # @app.get("/documents/")
# # def get_all_documents():
# #     return [serialize_document(doc) for doc in collection.find().sort("timestamp", -1)]

# # @app.get("/documents/{document_id}")
# # def get_document_by_id(document_id: str):
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
# #     doc = collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     return serialize_document(doc)

# # @app.delete("/delete-documents")
# # async def delete_documents(document_ids: List[str] = Query(...)):
# #     deleted, errors = [], []
# #     for doc_id in document_ids:
# #         try:
# #             obj_id = ObjectId(doc_id)
# #             doc_data = collection.find_one_and_delete({"_id": obj_id})
# #             if doc_data:
# #                 deleted.append(doc_id)
# #                 if doc_data.get("file_path") and os.path.exists(doc_data["file_path"]):
# #                     try: os.remove(doc_data["file_path"])
# #                     except Exception as e: errors.append({"id": doc_id, "file_error": str(e)})
# #                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{doc_id}_test_cases.csv")
# #                 if os.path.exists(csv_p):
# #                     try: os.remove(csv_p)
# #                     except Exception as e: errors.append({"id": doc_id, "csv_error": str(e)})
# #             else: errors.append({"id": doc_id, "error": "Not found in DB"})
# #         except InvalidId: errors.append({"id": doc_id, "error": "Invalid ID format"})
# #         except Exception as e: errors.append({"id": doc_id, "error": str(e)})
    
# #     msg = f"{len(deleted)} docs deleted." if deleted else "No docs deleted."
# #     if errors: msg += f" Errors: {len(errors)}"
# #     status_c = status.HTTP_200_OK
# #     if errors and not deleted: status_c = status.HTTP_400_BAD_REQUEST
# #     elif errors: status_c = status.HTTP_207_MULTI_STATUS
# #     return JSONResponse(content={"message":msg, "deleted":deleted, "errors":errors}, status_code=status_c)


# # router = APIRouter(prefix="/api/v1") # Your existing router

# # @router.get("/get-test-cases/{document_id}", tags=["Test Cases"])
# # async def get_test_cases_as_json_filtered_and_counted(
# #     document_id: str, types: Optional[str] = Query(None),):
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid doc ID.")
# #     doc = collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     doc_status = doc.get("status")
# #     ds_id = doc.get("data_space_id") # Check if linked to a data space
# #     base_res = {"document_id":document_id, "data_space_id": str(ds_id) if ds_id else None, "file_name": doc.get("file_name"), "requested_gen_types":doc.get("requested_test_case_types",[])}
# #     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}

# #     if doc_status == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
# #     if doc_status == 0: prog=doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
# #     if doc_status == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
# #     if doc_status != 1: return {**base_res, **empty_tc_res, "status_code":doc_status or "unknown", "status_message":"unknown_status", "detail":f"Status: {doc_status}"}

# #     try:
# #         _, all_rows = test_case_utils.parse_test_cases_to_csv(document_id, collection)
# #         if not all_rows: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
# #         final_r, applied_f = all_rows, []
# #         if types:
# #             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
# #             applied_f=[t.strip() for t in types.split(',') if t.strip()]
# #             if f_lower: final_r=[tc for tc in all_rows if tc.get("Test type","").lower() in f_lower]
        
# #         cts=Counter(); total_c=0
# #         if final_r:
# #             for tc_item in final_r:
# #                 tt_val=tc_item.get("Test type")
# #                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
# #                 cts[norm_tt]+=1
# #             total_c=len(final_r)
        
# #         stat_msg,det_msg="ready","TCs retrieved."
# #         if types and applied_f and not final_r: stat_msg,det_msg="ready_no_match",f"No TCs for filters: {applied_f}"
# #         elif types and applied_f: det_msg=f"Filtered by: {applied_f}"
# #         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
# #     except HTTPException as he:
# #         if he.status_code==404 and "No test cases found" in he.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":he.detail}
# #         raise he
# #     except Exception as e: print(f"ERR GET TC {document_id}: {e}"); raise HTTPException(status_code=500, detail=f"Err processing TCs: {e}")

# # @router.get("/test-case-summary/{document_id}", tags=["Test Cases"])
# # async def get_test_case_summary(document_id: str):
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
# #     doc = collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     doc_status, ds_id = doc.get("status"), doc.get("data_space_id")
# #     base_res = {"document_id":document_id, "data_space_id":str(ds_id) if ds_id else None, "file_name":doc.get("file_name")}
# #     if doc_status != 1:
# #         det = "Summ. not avail.";
# #         if doc_status==-1: det+=" Gen not init."
# #         elif doc_status==0: det+=" Gen in prog."
# #         elif doc_status==2: det+=f" Gen failed: {doc.get('error_info','Unk')}"
# #         else: det+=f" Doc status '{doc_status}'."
# #         raise HTTPException(status_code=409, detail=det)
# #     try:
# #         _, parsed=test_case_utils.parse_test_cases_to_csv(document_id,collection)
# #         if not parsed: return {**base_res, "counts_by_type":{},"total_test_cases":0,"message":"Completed, no TCs parsed."}
# #         cts=Counter(tc.get("Test type","Not Specified") for tc in parsed)
# #         return {**base_res, "counts_by_type":dict(cts),"total_test_cases":len(parsed)}
# #     except Exception as e: print(f"ERR SUMM {document_id}: {e}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {e}")

# # app.include_router(router) # Your existing router

# # @app.get("/download-csv/{document_id}")
# # def download_test_cases_csv(document_id: str):
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
# #     doc = collection.find_one({"_id": doc_obj_id})
# #     if not doc or doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready or doc not found.")
# #     fname = doc.get("file_name", "doc.pdf")
# #     csv_p, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
# #     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV missing.")
# #     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_tc.csv")

# # @app.get("/api_key_usage/{api_key}", tags=["Utilities"])
# # def get_api_key_cost(api_key: str):
# #     key_sfx = api_key[-5:]
# #     rec = cost_collection.find_one({"api_key_suffix": key_sfx}) or cost_collection.find_one({"api_key": api_key})
# #     if not rec: return {"id":key_sfx, "tokens":0, "cost":0.0, "msg":"No data."}
# #     return {"id":rec.get("api_key_suffix",key_sfx), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_updated":rec.get("last_updated","N/A")}

# # SECRET_KEY_ENV = os.getenv("SECRET_KEY")
# # ALGORITHM_ENV = "HS256"
# # if not SECRET_KEY_ENV: print("WARNING: SECRET_KEY env var not set for JWT.")

# # @app.websocket("/ws/task_status/{task_id}")
# # async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
# #     token = websocket.query_params.get("token")
# #     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
# #     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
# #     username = "ws_user_anon"
# #     try:
# #         from jose import jwt, JWTError
# #         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
# #         username = payload.get("sub", "ws_user_no_sub")
# #     except Exception as e: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e}"}); await websocket.close(1008); return
    
# #     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
# #     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}."})
# #     task_mon = AsyncResult(task_id)
# #     try:
# #         while True:
# #             if websocket.client_state != WebSocketState.CONNECTED: break
# #             cel_stat = task_mon.state
# #             doc_info = collection.find_one({"last_task_id":task_id}, {"status":1,"progress":1,"error_info":1,"_id":1})
# #             db_stat, doc_id_ws = (doc_info.get("status"), str(doc_info["_id"])) if doc_info else (None, None)
# #             resp = {"tid":task_id, "cs":cel_stat, "dbs":db_stat, "did":doc_id_ws}
# #             if cel_stat=="PENDING": resp["i"]="Pending."
# #             elif cel_stat=="STARTED": resp["i"]="Started."
# #             elif cel_stat=="PROGRESS": resp["i"]="Progress."; resp["pd"]=task_mon.info;
# #             elif cel_stat=="SUCCESS": resp["i"]="SUCCESS (Celery)"; resp["r"]=task_mon.result; await websocket.send_json(resp); break
# #             elif cel_stat=="FAILURE": resp["i"]="FAILURE (Celery)"; resp["ed"]=str(task_mon.info); await websocket.send_json(resp); break
# #             elif cel_stat=="RETRY": resp["i"]="RETRY"; resp["rr"]=str(task_mon.info)
# #             else: resp["i"]=f"State: {cel_stat}"
# #             await websocket.send_json(resp)
# #             if task_mon.ready(): # Final check if missed above
# #                 if cel_stat not in ["SUCCESS", "FAILURE"]:
# #                     final_resp = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
# #                     if task_mon.state == "SUCCESS": final_resp["r"] = task_mon.result
# #                     elif task_mon.state == "FAILURE": final_resp["ed"] = str(task_mon.info)
# #                     await websocket.send_json(final_resp)
# #                 break
# #             await asyncio.sleep(2)
# #     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
# #     except Exception as e: print(f"WS Unhandled Error {task_id} ({username}): {type(e).__name__} - {e}");
# #     finally:
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
# #             except RuntimeError: pass
# #         print(f"WS for task {task_id} ({username}) closed.")

# # @app.post("/get_token", tags=["Authentication"])
# # async def get_token_post(request: TokenRequest): # TokenRequest definition IS HERE
# #     ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
# #     ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")
# #     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
# #     if request.username == ADMIN_USER and request.password == ADMIN_PASS:
# #         token = create_jwt_token(data={"sub": request.username, "role":"admin"})
# #         return {"access_token": token, "token_type": "bearer"}
# #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# # if __name__ == "__main__":
# #     import uvicorn
# #     print(f"--- GenAI API (Minimal DataSpace Add) Starting ---")
# #     print(f"MongoDB URL: {os.getenv('MONGODB_URL')}, DB: {os.getenv('MONGO_DB_NAME')}")
# #     print(f"Input DIR: {INPUT_DIR}")
# #     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# #         print(f"CSV Output DIR (from utils): {test_case_utils.CSV_OUTPUT_DIR}")
# #     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# # from fastapi import BackgroundTasks, HTTPException
# # from task_with_api_key import process_and_generate_task # Ensure this path is correct
# # from celery.result import AsyncResult
# # from fastapi import (
# #     FastAPI,
# #     UploadFile,
# #     File,
# #     HTTPException,
# #     Form,
# #     Query,
# #     status,
# #     WebSocket,
# #     APIRouter,
# #     WebSocketDisconnect,
# # )
# # from fastapi.responses import JSONResponse, FileResponse
# # from utils.jwt_auth import ( # Assuming this exists and is correct
# #     create_jwt_token,
# # )
# # from pydantic import BaseModel, Field # Added Field
# # from pymongo.collection import Collection # For type hinting

# # from fastapi.middleware.cors import CORSMiddleware
# # from typing import Optional, List, Dict, Any # Added Any
# # from dotenv import load_dotenv
# # from pymongo import MongoClient
# # from bson import ObjectId
# # from bson.errors import InvalidId
# # from pathlib import Path
# # import os
# # import re
# # # import time # Not used directly
# # # import uuid # Not used directly
# # # import pandas as pd # Your original code has this
# # # from openpyxl import load_workbook # Your original code has this
# # # import csv # Your original code has this, test_case_utils also uses it
# # import asyncio
# # from starlette.websockets import WebSocketState
# # from collections import Counter


# # # Import your custom modules
# # from utils import data_ingestion, test_case_utils, user_story_utils # Assuming these exist
# # from utils.llms import Mistral, openai, llama # Assuming these exist
# # # from core.websocket import websocket_endpoint # Your WS is inline in the provided code

# # from datetime import datetime, timezone as dt_timezone # Renamed to avoid conflict
# # from zoneinfo import ZoneInfo

# # load_dotenv()

# # # --- Environment Variables for Admin Credentials (used in /get_token) ---
# # ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
# # ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
# # SECRET_KEY_ENV = os.getenv("SECRET_KEY") # For JWT
# # ALGORITHM_ENV = "HS256" # For JWT


# # # --- MongoDB Setup ---
# # mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# # db = mongo_client[os.getenv("MONGO_DB_NAME", "Gen_AI")] # Use MONGO_DB_NAME from .env
# # collection: Collection = db["test_case_generation"] # Existing collection for documents/files
# # data_spaces_collection: Collection = db["data_spaces"] # NEW collection for Data Spaces
# # cost_collection: Collection = db["cost_tracking"] # Existing

# # # Consider adding indexes in a separate script or manually:
# # # db.data_spaces.createIndex({ "name": 1 }, { unique: true }) // If names should be unique

# # # --- Pydantic Models ---
# # class DataSpaceCreate(BaseModel):
# #     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
# #     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# # class DataSpaceResponse(BaseModel):
# #     data_space_id: str
# #     name: str
# #     description: Optional[str]
# #     created_at: datetime
# #     # document_count: int = 0 # Not calculated in this minimal version
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True # For Pydantic v2 (orm_mode=True for v1)

# # class TokenRequest(BaseModel): # DEFINITION OF TokenRequest
# #     username: str
# #     password: str

# # # --- Serialization Function (Your Existing One) ---
# # def serialize_document(doc_data: dict): # Changed param name for clarity in this func
# #     return {
# #         "file_id": str(doc_data["_id"]),
# #         "file_name": doc_data.get("file_name"),
# #         "file_path": doc_data.get("file_path"),
# #         "status": doc_data.get("status"),
# #         "selected_model": doc_data.get("selected_model", None),
# #         "timestamp": doc_data.get("timestamp").isoformat() if isinstance(doc_data.get("timestamp"), datetime) else str(doc_data.get("timestamp")),
# #         "last_task_id": doc_data.get("last_task_id")
# #     }

# # IST = ZoneInfo("Asia/Kolkata")

# # # --- Directories Setup ---
# # INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# # OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files") # Used by test_case_utils for CSVs
# # # EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files") # Your code has this

# # Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True) # Ensure base output dir exists
# # # Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True) # Your code has this


# # # --- FastAPI App Instance ---
# # app = FastAPI(title="GenAI API - Minimal Data Space Integration")

# # app.add_middleware(
# #     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
# #     allow_methods=["*"], allow_headers=["*"],
# # )

# # # --- Constants from your original code ---
# # VALID_TEST_CASE_TYPES = [ # This list is used by /generate_test_cases
# #     "functional", "non-functional", "security", "performance",
# #     "boundary", "compliance", "all"
# # ]
# # # This one is good for validating specific types if "all" is not allowed in a list
# # INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES if t != "all"]


# # # --- New Router for Data Space Creation ---
# # data_space_creation_router = APIRouter(prefix="/api/v1", tags=["Data Spaces"]) # Added prefix

# # @data_space_creation_router.post("/data-spaces/", response_model=DataSpaceResponse, status_code=status.HTTP_201_CREATED)
# # async def create_new_data_space(data_space_input: DataSpaceCreate):
# #     existing_space = data_spaces_collection.find_one({"name": data_space_input.name})
# #     if existing_space:
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_input.name}' already exists.")
    
# #     current_time = datetime.now(IST)
# #     # Convert Pydantic model to dict for MongoDB insertion
# #     data_space_document_data = data_space_input.model_dump(exclude_unset=True) # For Pydantic v2
# #     # For Pydantic v1: data_space_document_data = data_space_input.dict(exclude_unset=True)
    
# #     data_space_document_data["created_at"] = current_time
# #     # data_space_document_data["updated_at"] = current_time # If you track updates from start
# #     # data_space_document_data["document_ids"] = [] # Not linking docs in this minimal step

# #     insert_result = data_spaces_collection.insert_one(data_space_document_data)
    
# #     created_document_from_db = data_spaces_collection.find_one({"_id": insert_result.inserted_id})
# #     if not created_document_from_db:
# #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data space after creation.")

# #     # Manually construct the response from the DB document
# #     return DataSpaceResponse(
# #         data_space_id=str(created_document_from_db["_id"]),
# #         name=created_document_from_db["name"],
# #         description=created_document_from_db.get("description"),
# #         created_at=created_document_from_db["created_at"]
# #         # document_count is 0 by default in Pydantic model, which is correct for a new space
# #     )

# # app.include_router(data_space_creation_router)


# # # --- Your Existing Endpoints (Unchanged for this minimal addition) ---

# # @app.post("/upload_document/") # This is your original endpoint
# # async def upload_document(file: UploadFile = File(...)): # Renamed from upload_document_legacy for direct replacement
# #     file_name_original = file.filename # Store original filename
# #     # Create a unique filename for storage to prevent overwrites
# #     base, ext = os.path.splitext(file.filename)
# #     sanitized_base = re.sub(r'[^\w\.-]', '_', base) # Basic sanitization
# #     unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
# #     file_path = Path(INPUT_DIR) / unique_filename_on_disk

# #     try:
# #         contents = await file.read()
# #         with open(file_path, "wb") as f:
# #             f.write(contents)
# #     except Exception as e:
# #         # It's good practice to log the error on the server
# #         print(f"Error saving file {file_name_original}: {e}")
# #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {str(e)}")
# #     finally:
# #         await file.close()
    
# #     upload_time = datetime.now(IST)
# #     document_data = {
# #         "file_name": file_name_original, # Store original filename
# #         "file_path": str(file_path), # Store path to uniquely named file
# #         "status": -1,
# #         "timestamp": upload_time,
# #         "data_space_id": None # Explicitly mark as not belonging to a data space
# #         # Add other default fields your application expects for a new document
# #         # "test_cases": None, "progress": [], "error_info": None, 
# #         # "selected_model": None, "last_task_id": None, "requested_test_case_types": []
# #     }
# #     result = collection.insert_one(document_data) # `collection` is `test_case_generation`
# #     file_id = str(result.inserted_id)
# #     return {
# #         "message": "File uploaded successfully (not yet linked to a Data Space).",
# #         "file_name": file_name_original,
# #         "file_path": str(file_path), # You might not want to expose full server path
# #         "file_id": file_id,
# #         "timestamp": upload_time.isoformat()
# #     }

# # @app.post("/generate_test_cases/") # This is your existing endpoint
# # async def generate_test_cases(
# #     file_id: str = Form(...),
# #     model_name: Optional[str] = Form("Mistral"),
# #     chunk_size: Optional[int] = Query(default=None),
# #     # cache_key: Optional[str] = Query(default=None), # Your code had this, uncomment if used by Celery
# #     api_key: Optional[str] = Form(None),
# #     test_case_types: Optional[str] = Form("all"),
# # ):
# #     try:
# #         doc_obj_id = ObjectId(file_id)
# #         document = collection.find_one({"_id": doc_obj_id}) # Uses existing `collection`
# #     except InvalidId:
# #         raise HTTPException(status_code=400, detail="Invalid file_id format.")
# #     if not document:
# #         raise HTTPException(status_code=404, detail="Document not found in the database.")
    
# #     file_path_str = document.get("file_path")
# #     if not file_path_str or not Path(file_path_str).exists():
# #         raise HTTPException(status_code=404, detail="Document file not found on disk.")
# #     file_path_on_disk = Path(file_path_str) # Use this variable name

# #     # Parse and validate `test_case_types`
# #     types_to_send_to_celery: str
# #     types_list_for_response: List[str] # For the API response and DB logging
    
# #     processed_test_case_types_str = test_case_types.strip().lower()

# #     if processed_test_case_types_str == "all":
# #         types_to_send_to_celery = "all"
# #         # For response and DB, list the actual types implied by "all"
# #         types_list_for_response = INDIVIDUAL_VALID_TEST_CASE_TYPES[:] # Use the correct list
# #     else:
# #         parsed_list_from_input = [t.strip().lower() for t in test_case_types.split(",")]
# #         validated_types_for_celery = []
# #         for t_type in parsed_list_from_input:
# #             if not t_type: continue # Skip empty strings from "type1,,type2"
# #             if t_type not in INDIVIDUAL_VALID_TEST_CASE_TYPES: # Validate against individual types
# #                 raise HTTPException(
# #                     status_code=400,
# #                     detail=f"Invalid test_case_type: '{t_type}'. Must be one of {INDIVIDUAL_VALID_TEST_CASE_TYPES} or the string 'all'.")
# #             if t_type not in validated_types_for_celery: # Avoid duplicates
# #                 validated_types_for_celery.append(t_type)
        
# #         if not validated_types_for_celery:
# #              raise HTTPException(status_code=400, detail="No valid specific test case types provided.")
# #         types_to_send_to_celery = ",".join(validated_types_for_celery)
# #         types_list_for_response = validated_types_for_celery
 
# #     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
# #     warning_message = None
# #     if not api_key_to_use:
# #         # It's better to raise an error if API key is absolutely required by the LLM
# #         raise HTTPException(status_code=400, detail="API key is required for generation.")
# #     if not api_key and os.getenv("TOGETHER_API_KEY"): # Only show warning if default from env is used
# #         warning_message = "Using default API key from environment. Consider providing your own."
 
# #     # Update document in existing `collection`
# #     collection.update_one(
# #         {"_id": doc_obj_id},
# #         {
# #             "$set": {
# #                 "status": 0, # Processing
# #                 "selected_model": model_name,
# #                 "api_key_used": f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", # Mask key
# #                 "requested_test_case_types": types_list_for_response, # Store the list of actual types
# #                 "processing_start_time": datetime.now(IST),
# #                 "progress": ["Task initiated for test case generation"], # Initialize progress
# #                 "error_info": None, # Clear any previous errors
# #                 "last_task_id": None # Clear previous task ID before assigning new one
# #             }
# #         }
# #     )
 
# #     task = process_and_generate_task.apply_async(args=[
# #         str(file_path_on_disk), model_name, chunk_size,
# #         api_key_to_use, types_to_send_to_celery, file_id, # file_id is document_id string
# #     ])
 
# #     collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
 
# #     return {
# #         "message": "✅ Test case generation task started.",
# #         "task_id": task.id,
# #         "file_id": file_id,
# #         "test_case_types_being_generated": types_list_for_response,
# #         "api_key_being_used": f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A",
# #         "warning": warning_message,
# #     }


# # @app.get("/documents/") # Your existing endpoint
# # def get_all_documents():
# #     documents = list(collection.find().sort("timestamp", -1)) # Uses existing `collection`
# #     return [serialize_document(doc) for doc in documents]

# # @app.get("/documents/{document_id}") # Your existing endpoint
# # def get_document_by_id(document_id: str):
# #     try: doc_object_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
# #     doc = collection.find_one({"_id": doc_object_id}) # Uses existing `collection`
# #     if not doc: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
# #     return serialize_document(doc)


# # @app.delete("/delete-documents") # Your existing endpoint
# # async def delete_documents(document_ids: List[str] = Query(...)):
# #     # This uses existing `collection` and `test_case_utils.CSV_OUTPUT_DIR`
# #     deleted, errors = [], []
# #     for doc_id_str in document_ids:
# #         try:
# #             obj_id = ObjectId(doc_id_str)
# #             doc_data = collection.find_one_and_delete({"_id": obj_id}) # find_one_and_delete returns the doc
# #             if doc_data:
# #                 deleted.append(doc_id_str)
# #                 # Delete associated files
# #                 input_file = doc_data.get("file_path")
# #                 if input_file and os.path.exists(input_file):
# #                     try: os.remove(input_file)
# #                     except Exception as e_f: errors.append({"id":doc_id_str, "file_error":str(e_f)})
                
# #                 # Ensure CSV_OUTPUT_DIR is accessible, e.g., by importing test_case_utils if defined there
# #                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #                     csv_path_to_del = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{doc_id_str}_test_cases.csv")
# #                     if os.path.exists(csv_path_to_del):
# #                         try: os.remove(csv_path_to_del)
# #                         except Exception as e_c: errors.append({"id":doc_id_str, "csv_error":str(e_c)})
# #             else: errors.append({"id": doc_id_str, "error": "Not found in DB"})
# #         except InvalidId: errors.append({"id": doc_id_str, "error": "Invalid ID format"})
# #         except Exception as e_main: errors.append({"id": doc_id_str, "error": str(e_main)})

# #     response_msg = f"{len(deleted)} document(s) deleted." if deleted else "No documents deleted."
# #     if errors: response_msg += f" Errors occurred for {len(errors)} IDs."
    
# #     resp_status_code = status.HTTP_200_OK
# #     if errors and not deleted: resp_status_code = status.HTTP_400_BAD_REQUEST
# #     elif errors: resp_status_code = status.HTTP_207_MULTI_STATUS
    
# #     return JSONResponse(content={"message":response_msg, "deleted":deleted, "errors":errors}, status_code=resp_status_code)


# # # Your existing `router` for /get-test-cases and /test-case-summary
# # # Ensure this router is defined before it's included in the app.
# # # If it's already defined as `router = APIRouter()` in your code, that's fine.
# # # If not, define it:
# # router = APIRouter(prefix="/api/v1") # Added prefix for consistency, adjust if needed

# # @router.get("/get-test-cases/{document_id}", tags=["Test Cases"])
# # async def get_test_cases_as_json_filtered_and_counted(
# #     document_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid doc ID.")
# #     doc = collection.find_one({"_id": doc_obj_id}) # Uses existing `collection`
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    
# #     doc_status = doc.get("status")
# #     ds_id = doc.get("data_space_id")
# #     base_res = {
# #         "document_id":document_id,
# #         "data_space_id": str(ds_id) if ds_id else None, # Show if doc is linked
# #         "file_name": doc.get("file_name"),
# #         "requested_test_case_types_during_generation":doc.get("requested_test_case_types",[])
# #     }
# #     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}

# #     if doc_status == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_generation", "detail":"Gen. not started."}
# #     if doc_status == 0: prog=doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
# #     if doc_status == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
# #     if doc_status != 1: return {**base_res, **empty_tc_res, "status_code":doc_status or "unknown", "status_message":"unknown_status", "detail":f"Status: {doc_status}"}

# #     try:
# #         # Ensure test_case_utils.parse_test_cases_to_csv uses `collection`
# #         _, all_rows = test_case_utils.parse_test_cases_to_csv(document_id, collection)
# #         if not all_rows: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
        
# #         final_r, applied_f = all_rows, []
# #         if types:
# #             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
# #             applied_f=[t.strip() for t in types.split(',') if t.strip()]
# #             if f_lower: final_r=[tc for tc in all_rows if tc.get("Test type","").lower() in f_lower]
        
# #         cts=Counter(); total_c=0
# #         if final_r:
# #             for tc_item in final_r:
# #                 tt_val=tc_item.get("Test type") # This key comes from your CSV_HEADERS
# #                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
# #                 cts[norm_tt]+=1
# #             total_c=len(final_r)
        
# #         stat_msg,det_msg="ready","TCs retrieved."
# #         if types and applied_f and not final_r: stat_msg,det_msg="ready_no_match_for_filter",f"No TCs for filters: {applied_f}"
# #         elif types and applied_f: det_msg=f"Filtered by: {applied_f}"
# #         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None (all available shown)", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
# #     except HTTPException as he:
# #         if he.status_code==404 and "No test cases found" in he.detail: # Error from parser
# #              return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":he.detail}
# #         raise he
# #     except Exception as e: print(f"ERR GET TC {document_id}: {e}"); raise HTTPException(status_code=500, detail=f"Err processing TCs: {e}")

# # @router.get("/test-case-summary/{document_id}", tags=["Test Cases"])
# # async def get_test_case_summary(document_id: str):
# #     # This uses existing `collection`
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
# #     doc = collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
    
# #     doc_status, ds_id = doc.get("status"), doc.get("data_space_id")
# #     base_res = {"document_id":document_id, "data_space_id":str(ds_id) if ds_id else None, "file_name":doc.get("file_name")}
    
# #     if doc_status != 1:
# #         det = "Summary not avail.";
# #         if doc_status==-1: det+=" Gen not init."
# #         elif doc_status==0: det+=" Gen in prog."
# #         elif doc_status==2: det+=f" Gen failed: {doc.get('error_info','Unk')}"
# #         else: det+=f" Doc status '{doc_status}'."
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=det)
# #     try:
# #         # Ensure test_case_utils.parse_test_cases_to_csv uses `collection`
# #         _, parsed=test_case_utils.parse_test_cases_to_csv(document_id,collection)
# #         if not parsed: return {**base_res, "counts_by_type":{},"total_test_cases":0,"message":"Completed, no TCs parsed."}
        
# #         cts=Counter()
# #         for tc_item in parsed: # Key "Test type" must match your CSV_HEADERS in utils
# #             tt_val = tc_item.get("Test type")
# #             norm_tt = str(tt_val).strip() if tt_val and str(tt_val).strip().upper() != "N/A" else "Not Specified"
# #             cts[norm_tt]+=1
# #         return {**base_res, "counts_by_type":dict(cts),"total_test_cases":len(parsed)}
# #     except Exception as e: print(f"ERR SUMM {document_id}: {e}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {e}")

# # app.include_router(router) # Include your existing router

# # # Your existing /download-csv/{document_id}
# # @app.get("/download-csv/{document_id}") # Keep at app level or move to the router
# # def download_test_cases_csv(document_id: str):
# #     try: doc_obj_id = ObjectId(document_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid ID.")
# #     doc = collection.find_one({"_id": doc_obj_id}) # Uses `collection`
# #     if not doc or doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready or doc not found.")
    
# #     fname = doc.get("file_name", "doc.pdf")
# #     # Ensure test_case_utils.parse_test_cases_to_csv uses `collection`
# #     # Also ensure test_case_utils.CSV_OUTPUT_DIR is correctly defined and accessible
# #     csv_p, _ = test_case_utils.parse_test_cases_to_csv(document_id, collection)
# #     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV missing after parse attempt.")
# #     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

# # # Your existing /api_key_usage/
# # @app.get("/api_key_usage/{api_key}", tags=["Utilities"]) # Keep at app level or move
# # def get_api_key_cost(api_key: str):
# #     # This uses `cost_collection`
# #     key_sfx = api_key[-5:] # Be careful if key is < 5 chars
# #     rec = cost_collection.find_one({"api_key_suffix": key_sfx})
# #     if not rec: # Fallback if suffix matching isn't primary or if full key was passed
# #         rec = cost_collection.find_one({"api_key": api_key})
# #         if not rec: return {"api_key_identifier":key_sfx, "tokens_used":0, "cost_usd":0.0, "message":"No usage data."}
# #     return {"api_key_identifier":rec.get("api_key_suffix",key_sfx), "tokens_used":rec.get("tokens_used",0), "cost_usd":round(rec.get("cost_usd",0.0),6), "last_updated":rec.get("last_updated","N/A")}

#dvaedag
# # # --- Your existing WebSocket and Auth Endpoints ---
# # # (Copied from your provided code, ensure SECRET_KEY_ENV and ALGORITHM_ENV are used for JWT)
# # if not SECRET_KEY_ENV:
# #     print("WARNING: SECRET_KEY environment variable is not set. JWT auth will fail.")

# # @app.websocket("/ws/task_status/{task_id}")
# # async def ws_task_status_endpoint(websocket: WebSocket, task_id: str):
# #     token = websocket.query_params.get("token")
# #     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
# #     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
# #     username = "ws_user_anon"
# #     try:
# #         from jose import jwt, JWTError # Ensure 'python-jose[cryptography]' is installed
# #         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
# #         username = payload.get("sub", "ws_user_no_sub")
# #     except ImportError: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT lib missing."}); await websocket.close(1011); return
# #     except JWTError as e: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e}"}); await websocket.close(1008); return
    
# #     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
# #     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}."})
# #     task_mon = AsyncResult(task_id)
# #     try:
# #         while True:
# #             if websocket.client_state != WebSocketState.CONNECTED: break
# #             cel_stat = task_mon.state
# #             # Use `collection` (test_case_generation) for DB lookup
# #             doc_info = collection.find_one({"last_task_id":task_id}, {"status":1,"progress":1,"error_info":1,"_id":1})
# #             db_stat, doc_id_ws = (doc_info.get("status"), str(doc_info["_id"])) if doc_info else (None, None)
# #             resp = {"tid":task_id, "cs":cel_stat, "dbs":db_stat, "did":doc_id_ws}

# #             # Your existing state handling for WebSocket...
# #             if cel_stat=="PENDING": resp["i"]="Pending."
# #             elif cel_stat=="STARTED": resp["i"]="Started."
# #             elif cel_stat=="PROGRESS": resp["i"]="Progress."; resp["pd"]=task_mon.info;
# #             elif cel_stat=="SUCCESS": resp["i"]="SUCCESS (Celery)"; resp["r"]=task_mon.result; await websocket.send_json(resp); break
# #             elif cel_stat=="FAILURE": resp["i"]="FAILURE (Celery)"; resp["ed"]=str(task_mon.info); await websocket.send_json(resp); break
# #             elif cel_stat=="RETRY": resp["i"]="RETRY"; resp["rr"]=str(task_mon.info)
# #             else: resp["i"]=f"State: {cel_stat}"
            
# #             await websocket.send_json(resp)
# #             if task_mon.ready(): # Final check
# #                 if cel_stat not in ["SUCCESS", "FAILURE"]:
# #                     final_resp = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
# #                     if task_mon.state == "SUCCESS": final_resp["r"] = task_mon.result
# #                     elif task_mon.state == "FAILURE": final_resp["ed"] = str(task_mon.info)
# #                     await websocket.send_json(final_resp)
# #                 break
# #             await asyncio.sleep(2)
# #     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
# #     except Exception as e: print(f"WS Unhandled Error {task_id} ({username}): {type(e).__name__} - {e}");
# #     finally:
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
# #             except RuntimeError: pass
# #         print(f"WS for task {task_id} ({username}) closed.")

# # @app.post("/get_token", tags=["Authentication"]) # This is your existing endpoint
# # async def get_token_post(request: TokenRequest): # Uses the TokenRequest model defined above
# #     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set for token generation.")
# #     # Use ADMIN_USERNAME_ENV and ADMIN_PASSWORD_ENV for credentials
# #     if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
# #         token_data = {"sub": request.username, "role":"admin"} # Example claims
# #         token = create_jwt_token(data=token_data) # create_jwt_token needs SECRET_KEY_ENV and ALGORITHM_ENV
# #         return {"access_token": token, "token_type": "bearer"}
# #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# # # --- Main Execution ---
# # if __name__ == "__main__":
# #     import uvicorn
# #     print(f"--- GenAI API (Minimal DataSpace Add) Starting ---")
# #     print(f"MongoDB URL: {os.getenv('MONGODB_URL')}, DB: {os.getenv('MONGO_DB_NAME')}")
# #     print(f"Input DIR: {INPUT_DIR}")
# #     # Ensure CSV_OUTPUT_DIR from test_case_utils is created (if defined)
# #     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# #         print(f"CSV Output DIR (from utils): {test_case_utils.CSV_OUTPUT_DIR}")
# #     else:
# #         print("Warning: test_case_utils.CSV_OUTPUT_DIR is not defined. CSV downloads might fail.")
        
# #     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# # main3.py
# # from fastapi import BackgroundTasks, HTTPException
# # from task_with_api_key import process_and_generate_task # Ensure this path is correct
# # from celery.result import AsyncResult
# # from fastapi import (
# #     FastAPI,
# #     UploadFile,
# #     File,
# #     HTTPException,
# #     Form,
# #     Query,
# #     status,
# #     WebSocket,
# #     APIRouter,
# #     WebSocketDisconnect,
# #     Depends 
# # )
# # from fastapi.responses import JSONResponse, FileResponse
# # from utils.jwt_auth import ( 
# #     create_jwt_token,
# # )
# # from pydantic import BaseModel, Field 
# # from pymongo.collection import Collection 

# # from fastapi.middleware.cors import CORSMiddleware
# # from typing import Optional, List, Dict, Any 
# # from dotenv import load_dotenv
# # from pymongo import MongoClient
# # from bson import ObjectId # Import ObjectId for Pydantic json_encoders
# # from bson.errors import InvalidId
# # from pathlib import Path
# # import os
# # import re
# # import asyncio
# # from starlette.websockets import WebSocketState
# # from collections import Counter

# # from utils import data_ingestion, test_case_utils, user_story_utils 
# # from utils.llms import Mistral, openai, llama 

# # from datetime import datetime, timezone as dt_timezone 
# # from zoneinfo import ZoneInfo

# # load_dotenv()

# # # --- Environment Variables ---
# # ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
# # ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
# # SECRET_KEY_ENV = os.getenv("SECRET_KEY")
# # ALGORITHM_ENV = "HS256"
# # INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# # OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# # MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
# # MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

# # # --- Pydantic Models (Defined BEFORE app instance and routers) ---
# # class DataSpaceCreate(BaseModel):
# #     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
# #     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# # class DataSpaceResponse(BaseModel):
# #     data_space_id: str
# #     name: str
# #     description: Optional[str]
# #     created_at: datetime
# #     document_count: int = 0
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True # For Pydantic v2 (orm_mode = True for Pydantic v1)

# # class DocumentMetadataResponse(BaseModel):
# #     file_id: str
# #     file_name: str
# #     status: Optional[int]
# #     timestamp: datetime
# #     content_type: Optional[str] = None
# #     size: Optional[int] = None
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True

# # class UploadedFileDetail(BaseModel):
# #     file_id: Optional[str] = None
# #     file_name: str
# #     status: str
# #     error: Optional[str] = None
# #     message: Optional[str] = None

# # class BatchUploadResponse(BaseModel): # Used by single combined upload endpoint
# #     data_space_id: str
# #     data_space_name: str # Added for clarity in response
# #     message: str
# #     uploaded_files: Dict[str, str] # {original_filename: new_file_id}
# #     errors: Optional[List[Dict[str, str]]] = None

# # class TokenRequest(BaseModel):
# #     username: str
# #     password: str

# # class GenerateTaskResponseItem(BaseModel): # For batch generate TC response
# #     file_id: str
# #     task_id: str
# #     message: str
# #     error: Optional[str] = None

# # class BatchGenerateTestCasesResponse(BaseModel): # For batch generate TC response
# #     overall_message: str
# #     tasks_initiated: List[GenerateTaskResponseItem]
# #     warning: Optional[str] = None


# # # --- MongoDB Setup ---
# # mongo_client = MongoClient(MONGODB_URL)
# # db = mongo_client[MONGO_DB_NAME]
# # documents_collection: Collection = db["test_case_generation"]
# # data_spaces_collection: Collection = db["data_spaces"]
# # cost_collection: Collection = db["cost_tracking"]

# # # --- Serialization, Constants, Directory Setup ---
# # IST = ZoneInfo("Asia/Kolkata")
# # Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# # if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'): # Ensure CSV output dir from utils is created
# #     Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# # VALID_TEST_CASE_TYPES_FROM_USER = [
# #     "functional", "non-functional", "security", "performance",
# #     "boundary", "compliance", "all"
# # ]
# # INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES_FROM_USER if t != "all"]

# # # --- FastAPI App Instance ---
# # app = FastAPI(title="GenAI API with Data Spaces (Corrected Model Order)")
# # app.add_middleware(
# #     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
# #     allow_methods=["*"], allow_headers=["*"],
# # )

# # # --- API Routers ---
# # api_v1_router = APIRouter(prefix="/api/v1")


# # # --- Data Space Endpoints ---
# # @api_v1_router.post(
# #     "/data-spaces/create-and-upload/",
# #     response_model=BatchUploadResponse, # Changed to BatchUploadResponse
# #     status_code=status.HTTP_201_CREATED,
# #     tags=["Data Spaces & Documents"],
# #     summary="Create a new Data Space and upload multiple documents to it."
# # )
# # async def create_dataspace_and_upload_documents(
# #     data_space_name: str = Form(..., min_length=3, max_length=100),
# #     data_space_description: Optional[str] = Form(None, max_length=500),
# #     files: List[UploadFile] = File(...)
# # ):
# #     if data_spaces_collection.find_one({"name": data_space_name}):
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_name}' already exists.")
    
# #     now = datetime.now(IST)
# #     ds_doc_data = {"name": data_space_name, "description": data_space_description, "created_at": now, "updated_at": now}
# #     insert_ds_result = data_spaces_collection.insert_one(ds_doc_data)
# #     new_data_space_id = insert_ds_result.inserted_id
# #     new_data_space_id_str = str(new_data_space_id)

# #     if not files:
# #         return BatchUploadResponse(
# #             data_space_id=new_data_space_id_str, data_space_name=data_space_name,
# #             message="Data Space created. No files provided.", uploaded_files={}, errors=[]
# #         )
        
# #     uploaded_files_map: Dict[str, str] = {}
# #     file_upload_errors: List[Dict[str,str]] = []
# #     successful_uploads_count = 0

# #     for file in files:
# #         original_filename = file.filename
# #         base, ext = os.path.splitext(original_filename)
# #         sanitized_base = re.sub(r'[^\w\s\.-]', '_', base).replace(" ", "_")
# #         unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
# #         file_path_on_disk = Path(INPUT_DIR) / unique_filename_on_disk
# #         try:
# #             with open(file_path_on_disk, "wb") as f: f.write(await file.read())
# #             file_size = file_path_on_disk.stat().st_size
# #             doc_meta = {
# #                 "data_space_id": new_data_space_id, "file_name": original_filename, "file_path": str(file_path_on_disk),
# #                 "content_type": file.content_type, "size": file_size, "status": -1, "timestamp": now,
# #                 "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
# #                 "last_task_id": None, "requested_test_case_types": []}
# #             insert_doc_res = documents_collection.insert_one(doc_meta)
# #             uploaded_files_map[original_filename] = str(insert_doc_res.inserted_id)
# #             successful_uploads_count += 1
# #         except Exception as e:
# #             print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
# #             file_upload_errors.append({"filename": original_filename, "error": str(e)})
# #             if os.path.exists(file_path_on_disk) and original_filename not in uploaded_files_map:
# #                  try: os.remove(file_path_on_disk)
# #                  except Exception as e_del: print(f"Cleanup err {file_path_on_disk}: {e_del}")
# #         finally: await file.close()

# #     msg = f"Data Space '{data_space_name}' created. {successful_uploads_count} of {len(files)} files processed."
# #     if file_upload_errors: msg += " Some files failed to upload."
    
# #     return BatchUploadResponse(
# #         data_space_id=new_data_space_id_str, data_space_name=data_space_name,
# #         message=msg, uploaded_files=uploaded_files_map, errors=file_upload_errors if file_upload_errors else None
# #     )

# # @api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
# # async def list_data_spaces(skip: int = 0, limit: int = 20):
# #     # ... (Same as your previous list_data_spaces) ...
# #     spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
# #     return [DataSpaceResponse(data_space_id=str(ds_doc["_id"]), **ds_doc, document_count=documents_collection.count_documents({"data_space_id": ds_doc["_id"]})) for ds_doc in spaces_cursor]

# # @api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
# # async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
# #     # ... (Same as your previous list_documents_in_data_space) ...
# #     try: ds_obj_id = ObjectId(data_space_id)
# #     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")
# #     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
# #     docs_cursor = documents_collection.find({"data_space_id": ds_obj_id}).sort("timestamp", -1).skip(skip).limit(limit)
# #     return [DocumentMetadataResponse(file_id=str(doc["_id"]), **doc) for doc in docs_cursor]

# # @api_v1_router.delete("/data-spaces/{data_space_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Data Spaces"])
# # async def delete_data_space(data_space_id: str, delete_contained_documents: bool = Query(False)):
# #     # ... (Same as your previous delete_data_space, ensure CSV_OUTPUT_DIR is accessible) ...
# #     try: ds_obj_id = ObjectId(data_space_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid Data Space ID.")
# #     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
# #         raise HTTPException(status_code=404, detail="Data Space not found.")
# #     if delete_contained_documents:
# #         docs_to_del_cursor = documents_collection.find({"data_space_id": ds_obj_id}, {"_id": 1, "file_path": 1})
# #         for doc in docs_to_del_cursor:
# #             if doc.get("file_path") and os.path.exists(doc["file_path"]):
# #                 try: os.remove(doc["file_path"])
# #                 except Exception as e: print(f"ERR DEL FILE {doc['file_path']}: {e}")
# #             if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{str(doc['_id'])}_test_cases.csv")
# #                 if os.path.exists(csv_p):
# #                     try: os.remove(csv_p)
# #                     except Exception as e: print(f"ERR DEL CSV {csv_p}: {e}")
# #         documents_collection.delete_many({"data_space_id": ds_obj_id})
# #     result = data_spaces_collection.delete_one({"_id": ds_obj_id})
# #     if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Data Space found but failed to delete.")


# # # --- Document Test Case Operations ---
# # @api_v1_router.post("/documents/batch-generate-test-cases/", response_model=BatchGenerateTestCasesResponse, tags=["Document Test Cases"])
# # async def batch_generate_test_cases_for_documents(
# #     file_ids_str: str = Form(..., alias="file_ids", description="Comma-separated file_ids."),
# #     model_name: Optional[str] = Form("Mistral"), chunk_size: Optional[int] = Query(None),
# #     api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
# # ):
# #     # ... (Your full logic for batch_generate_test_cases_for_documents from the previous response where it was working) ...
# #     # This code should be the version that accepts a comma-separated string for file_ids.
# #     actual_file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
# #     if not actual_file_ids: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")
# #     initiated_tasks_info: List[GenerateTaskResponseItem] = []
# #     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
# #     if not api_key_to_use: raise HTTPException(status_code=400, detail="API key required.")
# #     warning_msg = "Using default API key." if not api_key and os.getenv("TOGETHER_API_KEY") else None
# #     types_to_send, types_for_resp = "all", INDIVIDUAL_VALID_TEST_CASE_TYPES[:]
# #     if test_case_types.strip().lower() != "all":
# #         parsed = [t.strip().lower() for t in test_case_types.split(',') if t.strip()]
# #         validated = list(dict.fromkeys(t for t in parsed if t in INDIVIDUAL_VALID_TEST_CASE_TYPES))
# #         if not validated: raise HTTPException(status_code=400, detail="No valid types.")
# #         types_to_send, types_for_resp = ",".join(validated), validated
# #     for current_file_id in actual_file_ids:
# #         try:
# #             doc_obj_id = ObjectId(current_file_id)
# #             document = documents_collection.find_one({"_id": doc_obj_id})
# #             if not document: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc not found.", error="Doc not found")); continue
# #             f_path_str = document.get("file_path")
# #             if not f_path_str or not Path(f_path_str).exists(): initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc file missing.", error="File missing")); continue
# #             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"status":0, "selected_model":model_name, "api_key_used":f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST), "progress":["Batch gen task init."], "error_info":None, "last_task_id":None}})
# #             task = process_and_generate_task.apply_async(args=[str(Path(f_path_str)), model_name, chunk_size, api_key_to_use, types_to_send, current_file_id])
# #             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}})
# #             initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id=task.id, message="✅ TC gen task started."))
# #         except InvalidId: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Invalid file_id.", error="Invalid file_id"))
# #         except Exception as e: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message=f"Failed: {type(e).__name__}.", error=str(e)))
# #     success_count = sum(1 for item in initiated_tasks_info if item.task_id != "N/A")
# #     return BatchGenerateTestCasesResponse(overall_message=f"Batch process done. {success_count}/{len(actual_file_ids)} tasks started.", tasks_initiated=initiated_tasks_info, warning=warning_msg)


# # # --- (All other Document Test Case endpoints: get, summary, download, delete - from previous full code) ---
# # # These should all use `documents_collection` and refer to `file_id`.
# # @api_v1_router.get("/documents/{file_id}/get-test-cases/", tags=["Document Test Cases"])
# # async def get_test_cases_as_json_filtered_and_counted(
# #     file_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
# #     # ... (Your full logic from previous response)
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     doc = documents_collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     status_val = doc.get("status")
# #     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name"), "req_gen_types":doc.get("requested_test_case_types",[])}
# #     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}
# #     if status_val == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
# #     if status_val == 0: prog = doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
# #     if status_val == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
# #     if status_val != 1: return {**base_res, **empty_tc_res, "status_code":status_val or "unknown", "status_message":"unknown_status", "detail":f"Status: {status_val}"}
# #     try:
# #         _, all_r = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
# #         if not all_r: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
# #         final_r, applied_f = all_r, []
# #         if types:
# #             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
# #             applied_f=[t.strip() for t in types.split(',') if t.strip()]
# #             if f_lower: final_r=[tc for tc in all_r if tc.get("Test type","").lower() in f_lower]
# #         cts = Counter(); total_c = 0
# #         if final_r:
# #             for tc_item in final_r:
# #                 tt_val=tc_item.get("Test type")
# #                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
# #                 cts[norm_tt]+=1
# #             total_c=len(final_r)
# #         stat_msg, det_msg = "ready", "TCs retrieved."
# #         if types and applied_f and not final_r: stat_msg, det_msg = "ready_no_match", f"No TCs for filters: {applied_f}"
# #         elif types and applied_f: det_msg = f"Filtered by: {applied_f}"
# #         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
# #     except HTTPException as http_e:
# #         if http_e.status_code==404 and "No test cases found" in http_e.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":http_e.detail}
# #         raise http_e
# #     except Exception as e_main: print(f"ERR GET TC {file_id}: {e_main}"); raise HTTPException(status_code=500, detail=f"Error processing TCs: {str(e_main)}")

# # @api_v1_router.get("/documents/{file_id}/test-case-summary/", tags=["Document Test Cases"])
# # async def get_document_test_case_summary(file_id: str):
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     doc = documents_collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     status_val = doc.get("status")
# #     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name")}
# #     if status_val != 1: raise HTTPException(status_code=409, detail=f"Summary not available. Status: {status_val}")
# #     try:
# #         _, parsed_list = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
# #         if not parsed_list: return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, no TCs parsed."}
# #         cts = Counter(tc.get("Test type", "Not Specified") for tc in parsed_list)
# #         return {**base_res, "counts_by_type":dict(cts), "total_test_cases":len(parsed_list)}
# #     except Exception as e_sum: print(f"ERR SUMM {file_id}: {e_sum}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {str(e_sum)}")

# # @api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
# # async def download_test_cases_csv_for_document(file_id: str):
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     doc = documents_collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     if doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready.")
# #     fname = doc.get("file_name", "doc.pdf")
# #     csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
# #     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV file missing post-parse.")
# #     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

# # @api_v1_router.delete("/documents/", tags=["Document Test Cases"])
# # async def delete_multiple_documents(document_ids: List[str] = Query(...)):
# #     del_c, errs = 0, []
# #     for id_str in document_ids:
# #         try:
# #             obj_id = ObjectId(id_str)
# #             doc = documents_collection.find_one_and_delete({"_id":obj_id})
# #             if doc:
# #                 del_c+=1
# #                 if doc.get("file_path") and os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
# #                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #                     csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{id_str}_test_cases.csv")
# #                     if os.path.exists(csv_p): os.remove(csv_p)
# #             else: errs.append({"id":id_str, "error":"Not found"})
# #         except InvalidId: errs.append({"id":id_str, "error":"Invalid ID"})
# #         except Exception as e_del: errs.append({"id":id_str, "error":str(e_del)})
# #     return {"deleted_count":del_c, "errors":errs}


# # # --- Auth & Utility Endpoints ---
# # @api_v1_router.post("/auth/token", response_model=Dict[str, str], tags=["Authentication"])
# # async def login_for_access_token(request: TokenRequest):
# #     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
# #     if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
# #         token = create_jwt_token(data={"sub": request.username, "role": "admin"}) # Needs SECRET_KEY_ENV, ALGORITHM_ENV
# #         return {"access_token": token, "token_type": "bearer"}
# #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

# # @api_v1_router.get("/utilities/api-key-usage/{api_key_suffix}", tags=["Utilities"])
# # async def get_api_key_usage_stats(api_key_suffix: str):
# #     if len(api_key_suffix) < 5 : raise HTTPException(status_code=400, detail="Suffix too short.")
# #     rec = cost_collection.find_one({"api_key_suffix": api_key_suffix})
# #     if not rec: rec = cost_collection.find_one({"api_key": api_key_suffix}) 
# #     if not rec: return {"id":api_key_suffix, "tokens":0, "cost":0.0, "msg":"No usage data."}
# #     return {"id":rec.get("api_key_suffix",api_key_suffix), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_update":rec.get("last_updated","N/A")}


# # app.include_router(api_v1_router) # Include the main v1 router

# # # --- WebSocket Endpoint ---
# # @app.websocket("/ws/v1/task_status/{task_id}")
# # async def websocket_task_status_endpoint(websocket: WebSocket, task_id: str):
# #     # ... (Your full WebSocket logic from the previous "full integration attempt" response,
# #     #      making sure `documents_collection` is used for DB queries by `last_task_id`) ...
# #     token = websocket.query_params.get("token")
# #     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
# #     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
# #     username = "ws_user_anon"
# #     try:
# #         from jose import jwt, JWTError
# #         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
# #         username = payload.get("sub", "ws_user_no_sub")
# #     except Exception as e_auth_ws: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e_auth_ws}"}); await websocket.close(1008); return
# #     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
# #     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}"})
# #     task_mon = AsyncResult(task_id)
# #     try:
# #         while True:
# #             if websocket.client_state != WebSocketState.CONNECTED: break
# #             cel_stat = task_mon.state
# #             doc_info_ws = documents_collection.find_one({"last_task_id":task_id}, {"status":1, "progress":1, "error_info":1, "_id":1})
# #             db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None
# #             doc_id_ws = str(doc_info_ws["_id"]) if doc_info_ws else None
# #             resp_ws = {"tid":task_id, "cs":cel_stat, "dbs":db_stat_ws, "did":doc_id_ws}
# #             if cel_stat == "PENDING": resp_ws["i"] = "Pending"
# #             elif cel_stat == "STARTED": resp_ws["i"] = "Started"
# #             elif cel_stat == "PROGRESS": resp_ws["i"] = "Progress"; resp_ws["pd"] = task_mon.info;
# #             elif cel_stat == "SUCCESS":
# #                 resp_ws["i"] = "SUCCESS (Celery)"; resp_ws["r"] = task_mon.result
# #                 if doc_id_ws and db_stat_ws != 1: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":1, "error_info":None}, "$push":{"progress":"Celery SUCCESS via WS"}})
# #                 await websocket.send_json(resp_ws); break
# #             elif cel_stat == "FAILURE":
# #                 resp_ws["i"] = "FAILURE (Celery)"; resp_ws["ed"] = str(task_mon.info)
# #                 if doc_id_ws and db_stat_ws != 2: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":2, "error_info":str(task_mon.info)}, "$push":{"progress":"Celery FAILURE via WS"}})
# #                 await websocket.send_json(resp_ws); break
# #             elif cel_stat == "RETRY": resp_ws["i"] = "RETRY"; resp_ws["rr"] = str(task_mon.info)
# #             else: resp_ws["i"] = f"State: {cel_stat}"
# #             await websocket.send_json(resp_ws)
# #             if task_mon.ready():
# #                 if cel_stat not in ["SUCCESS", "FAILURE"]:
# #                     final_resp_ws = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
# #                     if task_mon.state == "SUCCESS": final_resp_ws["r"] = task_mon.result
# #                     elif task_mon.state == "FAILURE": final_resp_ws["ed"] = str(task_mon.info)
# #                     await websocket.send_json(final_resp_ws)
# #                 break
# #             await asyncio.sleep(2)
# #     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
# #     except Exception as e_ws_main:
# #         print(f"WS Unhandled Error {task_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.send_json({"s":"error","m":"Server WS error."})
# #             except: pass
# #     finally:
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
# #             except RuntimeError: pass
# #         print(f"WS for task {task_id} ({username}) closed.")


# # # --- Main Execution ---
# # if __name__ == "__main__":
# #     import uvicorn
# #     print(f"--- GenAI API (Full Integration with DataSpaces) Starting ---")
# #     print(f"MongoDB URL: {MONGODB_URL}, DB: {MONGO_DB_NAME}")
# #     print(f"Input DIR: {INPUT_DIR}, Output DIR: {OUTPUT_DIR}")
# #     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# #         print(f"CSV Output DIR (utils): {test_case_utils.CSV_OUTPUT_DIR}")
    
# #     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# # main3.py
# # from fastapi import BackgroundTasks, HTTPException
# # from task_with_api_key import process_and_generate_task # Ensure this path is correct
# # from celery.result import AsyncResult
# # from fastapi import (
# #     FastAPI,
# #     UploadFile,
# #     File,
# #     HTTPException,
# #     Form,
# #     Query,
# #     status,
# #     WebSocket,
# #     APIRouter,
# #     WebSocketDisconnect,
# #     Depends 
# # )
# # from fastapi.responses import JSONResponse, FileResponse
# # from utils.jwt_auth import ( 
# #     create_jwt_token,
# # )
# # from pydantic import BaseModel, Field 
# # from pymongo.collection import Collection 

# # from fastapi.middleware.cors import CORSMiddleware
# # from typing import Optional, List, Dict, Any 
# # from dotenv import load_dotenv
# # from pymongo import MongoClient
# # from bson import ObjectId # Import ObjectId for Pydantic json_encoders
# # from bson.errors import InvalidId
# # from pathlib import Path
# # import os
# # import re
# # import asyncio
# # from starlette.websockets import WebSocketState
# # from collections import Counter


# # # Import your custom modules
# # from utils import data_ingestion, test_case_utils, user_story_utils 
# # from utils.llms import Mistral, openai, llama 

# # from datetime import datetime, timezone as dt_timezone 
# # from zoneinfo import ZoneInfo

# # load_dotenv()

# # # --- Environment Variables ---
# # ADMIN_USERNAME_ENV = os.getenv("ADMIN_USERNAME", "admin")
# # ADMIN_PASSWORD_ENV = os.getenv("ADMIN_PASSWORD", "admin123")
# # SECRET_KEY_ENV = os.getenv("SECRET_KEY")
# # ALGORITHM_ENV = "HS256"
# # INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# # OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# # MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
# # MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

# # # --- Pydantic Models (Defined BEFORE app instance and routers) ---
# # class DataSpaceCreate(BaseModel):
# #     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
# #     description: Optional[str] = Field(None, max_length=500, description="Optional description")

# # class DataSpaceResponse(BaseModel):
# #     data_space_id: str
# #     name: str
# #     description: Optional[str]
# #     created_at: datetime
# #     document_count: int = 0
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True

# # class DocumentMetadataResponse(BaseModel):
# #     file_id: str
# #     file_name: str
# #     status: Optional[int]
# #     timestamp: datetime
# #     content_type: Optional[str] = None
# #     size: Optional[int] = None
# #     class Config:
# #         json_encoders = {ObjectId: str}
# #         from_attributes = True

# # class UploadedFileDetail(BaseModel): # For individual file status in batch upload
# #     file_id: Optional[str] = None
# #     file_name: str
# #     status: str # e.g., "uploaded", "failed_to_save", "db_insert_failed"
# #     error: Optional[str] = None
# #     message: Optional[str] = None # Optional success/info message per file

# # class BatchUploadResponse(BaseModel): # For the combined create DataSpace and upload files
# #     data_space_id: str
# #     data_space_name: str
# #     message: str # Overall message for the operation
# #     uploaded_files: Dict[str, str] # {original_filename: new_file_id or error_string}
# #     errors: Optional[List[Dict[str, str]]] = None # List of {"filename": ..., "error": ...}

# # class TokenRequest(BaseModel):
# #     username: str
# #     password: str

# # class GenerateTaskResponseItem(BaseModel):
# #     file_id: str
# #     task_id: str # Celery task ID
# #     message: str
# #     error: Optional[str] = None

# # class BatchGenerateTestCasesResponse(BaseModel):
# #     overall_message: str
# #     tasks_initiated: List[GenerateTaskResponseItem]
# #     warning: Optional[str] = None


# # # --- MongoDB Setup ---
# # mongo_client = MongoClient(MONGODB_URL)
# # db = mongo_client[MONGO_DB_NAME]
# # documents_collection: Collection = db["test_case_generation"]
# # data_spaces_collection: Collection = db["data_spaces"]
# # cost_collection: Collection = db["cost_tracking"]

# # # --- Serialization, Constants, Directory Setup ---
# # IST = ZoneInfo("Asia/Kolkata")
# # Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# # Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# # if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #     Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# # VALID_TEST_CASE_TYPES_FROM_USER = [
# #     "functional", "non-functional", "security", "performance",
# #     "boundary", "compliance", "all"
# # ]
# # INDIVIDUAL_VALID_TEST_CASE_TYPES = [t for t in VALID_TEST_CASE_TYPES_FROM_USER if t != "all"]

# # # --- FastAPI App Instance ---
# # app = FastAPI(title="GenAI API with Data Spaces (Full Integration - Corrected)")
# # app.add_middleware(
# #     CORSMiddleware, allow_origins=["*"], allow_credentials=True,
# #     allow_methods=["*"], allow_headers=["*"],
# # )

# # # --- API Routers ---
# # api_v1_router = APIRouter(prefix="/api/v1")

# # # --- Data Space Endpoints ---
# # @api_v1_router.post(
# #     "/data-spaces/create-and-upload/",
# #     response_model=BatchUploadResponse,
# #     status_code=status.HTTP_201_CREATED,
# #     tags=["Data Spaces & Documents"],
# #     summary="Create Data Space & Upload Documents"
# # )
# # async def create_dataspace_and_upload_documents(
# #     data_space_name: str = Form(..., min_length=3, max_length=100),
# #     data_space_description: Optional[str] = Form(None, max_length=500),
# #     files: List[UploadFile] = File(...)
# # ):
# #     if data_spaces_collection.find_one({"name": data_space_name}):
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space '{data_space_name}' already exists.")
# #     now = datetime.now(IST)
# #     ds_doc_data = {"name": data_space_name, "description": data_space_description, "created_at": now, "updated_at": now, "document_ids": []}
# #     insert_ds_result = data_spaces_collection.insert_one(ds_doc_data)
# #     new_data_space_id_obj = insert_ds_result.inserted_id
# #     new_data_space_id_str = str(new_data_space_id_obj)

# #     if not files:
# #         return BatchUploadResponse(data_space_id=new_data_space_id_str, data_space_name=data_space_name, message="Data Space created. No files provided.", uploaded_files={}, errors=[])
        
# #     uploaded_files_map: Dict[str, str] = {}
# #     successfully_uploaded_doc_object_ids: List[ObjectId] = []
# #     individual_file_errors: List[Dict[str,str]] = []
    
# #     for file in files:
# #         original_filename = file.filename
# #         base, ext = os.path.splitext(original_filename); sanitized_base = re.sub(r'[^\w\s\.-]', '_', base).replace(" ", "_")
# #         unique_filename_on_disk = f"{sanitized_base}_{ObjectId()}{ext}"
# #         file_path_on_disk = Path(INPUT_DIR) / unique_filename_on_disk
# #         try:
# #             with open(file_path_on_disk, "wb") as f: f.write(await file.read())
# #             file_size = file_path_on_disk.stat().st_size
# #             doc_meta = {
# #                 "data_space_id": new_data_space_id_obj, "file_name": original_filename, "file_path": str(file_path_on_disk),
# #                 "content_type": file.content_type, "size": file_size, "status": -1, "timestamp": now,
# #                 "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
# #                 "last_task_id": None, "requested_test_case_types": []}
# #             insert_doc_res = documents_collection.insert_one(doc_meta)
# #             new_doc_obj_id = insert_doc_res.inserted_id
# #             uploaded_files_map[original_filename] = str(new_doc_obj_id)
# #             successfully_uploaded_doc_object_ids.append(new_doc_obj_id)
# #         except Exception as e:
# #             print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
# #             individual_file_errors.append({"filename": original_filename, "error": str(e)})
# #             uploaded_files_map[original_filename] = f"ERROR: {str(e)}" # Indicate error in the map
# #             if os.path.exists(file_path_on_disk):
# #                  try: os.remove(file_path_on_disk)
# #                  except Exception as e_del: print(f"Cleanup err {file_path_on_disk}: {e_del}")
# #         finally: await file.close()

# #     if successfully_uploaded_doc_object_ids:
# #         data_spaces_collection.update_one({"_id": new_data_space_id_obj}, {"$set": {"document_ids": successfully_uploaded_doc_object_ids, "updated_at": datetime.now(IST)}})
# #     elif files: # Files were provided but none were successful
# #          data_spaces_collection.update_one({"_id": new_data_space_id_obj}, {"$set": {"updated_at": datetime.now(IST)}})


# #     msg = f"Data Space '{data_space_name}' created. {len(successfully_uploaded_doc_object_ids)} of {len(files)} files successfully uploaded and linked."
# #     if individual_file_errors: msg += " Some files encountered errors."
    
# #     return BatchUploadResponse(
# #         data_space_id=new_data_space_id_str, data_space_name=data_space_name, message=msg,
# #         uploaded_files=uploaded_files_map, errors=individual_file_errors if individual_file_errors else None)

# # @api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
# # async def list_data_spaces(skip: int = 0, limit: int = 20):
# #     spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
# #     return [DataSpaceResponse(data_space_id=str(ds_doc["_id"]), **ds_doc, document_count=documents_collection.count_documents({"data_space_id": ds_doc["_id"]})) for ds_doc in spaces_cursor]

# # @api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
# # async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
# #     try: ds_obj_id = ObjectId(data_space_id)
# #     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")
# #     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
# #     docs_cursor = documents_collection.find({"data_space_id": ds_obj_id}).sort("timestamp", -1).skip(skip).limit(limit)
# #     return [DocumentMetadataResponse(file_id=str(doc["_id"]), **doc) for doc in docs_cursor]

# # @api_v1_router.delete("/data-spaces/{data_space_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Data Spaces"])
# # async def delete_data_space(data_space_id: str, delete_contained_documents: bool = Query(False)):
# #     try: ds_obj_id = ObjectId(data_space_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid Data Space ID.")
# #     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
# #     if delete_contained_documents:
# #         docs_to_del_cursor = documents_collection.find({"data_space_id": ds_obj_id}, {"_id": 1, "file_path": 1})
# #         for doc in docs_to_del_cursor:
# #             if doc.get("file_path") and os.path.exists(doc["file_path"]):
# #                 try: os.remove(doc["file_path"])
# #                 except Exception as e: print(f"ERR DEL FILE {doc['file_path']}: {e}")
# #             if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{str(doc['_id'])}_test_cases.csv")
# #                 if os.path.exists(csv_p):
# #                     try: os.remove(csv_p)
# #                     except Exception as e: print(f"ERR DEL CSV {csv_p}: {e}")
# #         documents_collection.delete_many({"data_space_id": ds_obj_id})
# #     result = data_spaces_collection.delete_one({"_id": ds_obj_id})
# #     if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Data Space found but failed to delete.")

# # # --- Document Test Case Operations ---
# # @api_v1_router.post("/documents/batch-generate-test-cases/", response_model=BatchGenerateTestCasesResponse, tags=["Document Test Cases"])
# # async def batch_generate_test_cases_for_documents(
# #     file_ids_str: str = Form(..., alias="file_ids", description="Comma-separated file_ids."),
# #     model_name: Optional[str] = Form("Mistral"), chunk_size: Optional[int] = Query(None),
# #     api_key: Optional[str] = Form(None), test_case_types: Optional[str] = Form("all"),
# # ):
# #     actual_file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
# #     if not actual_file_ids: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")
# #     initiated_tasks_info: List[GenerateTaskResponseItem] = []
# #     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
# #     if not api_key_to_use: raise HTTPException(status_code=400, detail="API key required.")
# #     warning_msg = "Using default API key." if not api_key and os.getenv("TOGETHER_API_KEY") else None
# #     types_to_send, types_for_resp = "all", INDIVIDUAL_VALID_TEST_CASE_TYPES[:]
# #     if test_case_types.strip().lower() != "all":
# #         parsed = [t.strip().lower() for t in test_case_types.split(',') if t.strip()]
# #         validated = list(dict.fromkeys(t for t in parsed if t in INDIVIDUAL_VALID_TEST_CASE_TYPES))
# #         if not validated: raise HTTPException(status_code=400, detail="No valid types.")
# #         types_to_send, types_for_resp = ",".join(validated), validated
# #     for current_file_id in actual_file_ids:
# #         try:
# #             doc_obj_id = ObjectId(current_file_id)
# #             document = documents_collection.find_one({"_id": doc_obj_id})
# #             if not document: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc not found.", error="Doc not found")); continue
# #             f_path_str = document.get("file_path")
# #             if not f_path_str or not Path(f_path_str).exists(): initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Doc file missing.", error="File missing")); continue
# #             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"status":0, "selected_model":model_name, "api_key_used":f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A", "requested_test_case_types":types_for_resp, "processing_start_time":datetime.now(IST), "progress":["Batch gen task init."], "error_info":None, "last_task_id":None}})
# #             task = process_and_generate_task.apply_async(args=[str(Path(f_path_str)), model_name, chunk_size, api_key_to_use, types_to_send, current_file_id])
# #             documents_collection.update_one({"_id": doc_obj_id}, {"$set": {"last_task_id": task.id}}) # This stores the task_id
# #             initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id=task.id, message="✅ TC gen task started."))
# #         except InvalidId: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message="Failed: Invalid file_id.", error="Invalid file_id"))
# #         except Exception as e: initiated_tasks_info.append(GenerateTaskResponseItem(file_id=current_file_id, task_id="N/A", message=f"Failed: {type(e).__name__}.", error=str(e)))
# #     success_count = sum(1 for item in initiated_tasks_info if item.task_id != "N/A")
# #     return BatchGenerateTestCasesResponse(overall_message=f"Batch process done. {success_count}/{len(actual_file_ids)} tasks started.", tasks_initiated=initiated_tasks_info, warning=warning_msg)

# # # ... (Your other endpoints: /documents/{file_id}/get-test-cases/, /documents/{file_id}/test-case-summary/, /documents/{file_id}/download-csv/, /documents/ (delete)
# # #      will be here, exactly as in the previous full code response. I'm omitting them for brevity here but they should be included.
# # #      Ensure they are on `api_v1_router`.)

# # @api_v1_router.get("/documents/{file_id}/get-test-cases/", tags=["Document Test Cases"])
# # async def get_test_cases_as_json_filtered_and_counted(
# #     file_id: str, types: Optional[str] = Query(None, description="Filter by comma-separated types"),):
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     doc = documents_collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     status_val = doc.get("status")
# #     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name"), "req_gen_types":doc.get("requested_test_case_types",[])}
# #     empty_tc_res = {"test_cases":[], "counts_by_type":{}, "total_test_cases":0}
# #     if status_val == -1: return {**base_res, **empty_tc_res, "status_code":-1, "status_message":"pending_gen", "detail":"Gen not started."}
# #     if status_val == 0: prog = doc.get("progress",[]); return {**base_res, **empty_tc_res, "status_code":0, "status_message":"processing", "detail":prog[-1] if prog else "Processing..", "progress_log":prog}
# #     if status_val == 2: return {**base_res, **empty_tc_res, "status_code":2, "status_message":"error", "detail":f"Failed: {doc.get('error_info','Unknown')}"}
# #     if status_val != 1: return {**base_res, **empty_tc_res, "status_code":status_val or "unknown", "status_message":"unknown_status", "detail":f"Status: {status_val}"}
# #     try:
# #         _, all_r = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
# #         if not all_r: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed."}
# #         final_r, applied_f = all_r, []
# #         if types:
# #             f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
# #             applied_f=[t.strip() for t in types.split(',') if t.strip()]
# #             if f_lower: final_r=[tc for tc in all_r if tc.get("Test type","").lower() in f_lower]
# #         cts = Counter(); total_c = 0
# #         if final_r:
# #             for tc_item in final_r:
# #                 tt_val=tc_item.get("Test type")
# #                 norm_tt=str(tt_val).strip() if tt_val and str(tt_val).strip().upper()!="N/A" else "Not Specified"
# #                 cts[norm_tt]+=1
# #             total_c=len(final_r)
# #         stat_msg, det_msg = "ready", "TCs retrieved."
# #         if types and applied_f and not final_r: stat_msg, det_msg = "ready_no_match", f"No TCs for filters: {applied_f}"
# #         elif types and applied_f: det_msg = f"Filtered by: {applied_f}"
# #         return {**base_res, "status_code":1, "status_message":stat_msg, "detail":det_msg, "filter_applied_types":applied_f if types else "None", "test_cases":final_r, "counts_by_type":dict(cts), "total_test_cases":total_c}
# #     except HTTPException as http_e:
# #         if http_e.status_code==404 and "No test cases found" in http_e.detail: return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data_in_doc", "detail":http_e.detail}
# #         raise http_e
# #     except Exception as e_main: print(f"ERR GET TC {file_id}: {e_main}"); raise HTTPException(status_code=500, detail=f"Error processing TCs: {str(e_main)}")

# # @api_v1_router.get("/documents/{file_id}/test-case-summary/", tags=["Document Test Cases"])
# # async def get_document_test_case_summary(file_id: str):
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     doc = documents_collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     status_val = doc.get("status")
# #     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name")}
# #     if status_val != 1: raise HTTPException(status_code=409, detail=f"Summary not available. Status: {status_val}")
# #     try:
# #         _, parsed_list = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
# #         if not parsed_list: return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, no TCs parsed."}
# #         cts = Counter(tc.get("Test type", "Not Specified") for tc in parsed_list)
# #         return {**base_res, "counts_by_type":dict(cts), "total_test_cases":len(parsed_list)}
# #     except Exception as e_sum: print(f"ERR SUMM {file_id}: {e_sum}"); raise HTTPException(status_code=500,detail=f"Err gen summ: {str(e_sum)}")

# # @api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
# # async def download_test_cases_csv_for_document(file_id: str):
# #     try: doc_obj_id = ObjectId(file_id)
# #     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
# #     doc = documents_collection.find_one({"_id": doc_obj_id})
# #     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
# #     if doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready.")
# #     fname = doc.get("file_name", "doc.pdf")
# #     csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
# #     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV file missing post-parse.")
# #     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

# # @api_v1_router.delete("/documents/", tags=["Document Test Cases"])
# # async def delete_multiple_documents(document_ids: List[str] = Query(...)):
# #     del_c, errs = 0, []
# #     for id_str in document_ids:
# #         try:
# #             obj_id = ObjectId(id_str)
# #             doc = documents_collection.find_one_and_delete({"_id":obj_id})
# #             if doc:
# #                 del_c+=1
# #                 if doc.get("file_path") and os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
# #                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #                     csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{id_str}_test_cases.csv")
# #                     if os.path.exists(csv_p): os.remove(csv_p)
# #             else: errs.append({"id":id_str, "error":"Not found"})
# #         except InvalidId: errs.append({"id":id_str, "error":"Invalid ID"})
# #         except Exception as e_del: errs.append({"id":id_str, "error":str(e_del)})
# #     return {"deleted_count":del_c, "errors":errs}


# # # --- Auth & Utility Endpoints ---
# # @api_v1_router.post("/auth/token", response_model=Dict[str, str], tags=["Authentication"])
# # async def login_for_access_token(request: TokenRequest):
# #     if not SECRET_KEY_ENV: raise HTTPException(status_code=500, detail="JWT Secret not set.")
# #     if request.username == ADMIN_USERNAME_ENV and request.password == ADMIN_PASSWORD_ENV:
# #         token = create_jwt_token(data={"sub": request.username, "role": "admin"}) # Needs SECRET_KEY_ENV, ALGORITHM_ENV
# #         return {"access_token": token, "token_type": "bearer"}
# #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

# # @api_v1_router.get("/utilities/api-key-usage/{api_key_suffix}", tags=["Utilities"])
# # async def get_api_key_usage_stats(api_key_suffix: str):
# #     if len(api_key_suffix) < 5 : raise HTTPException(status_code=400, detail="Suffix too short.")
# #     rec = cost_collection.find_one({"api_key_suffix": api_key_suffix})
# #     if not rec: rec = cost_collection.find_one({"api_key": api_key_suffix}) 
# #     if not rec: return {"id":api_key_suffix, "tokens":0, "cost":0.0, "msg":"No usage data."}
# #     return {"id":rec.get("api_key_suffix",api_key_suffix), "tokens":rec.get("tokens_used",0), "cost":round(rec.get("cost_usd",0.0),6), "last_update":rec.get("last_updated","N/A")}

# # app.include_router(api_v1_router)

# # # --- WebSocket Endpoint ---
# # @app.websocket("/ws/v1/task_status/{task_id}")
# # async def websocket_task_status_endpoint(websocket: WebSocket, task_id: str):
# #     token = websocket.query_params.get("token")
# #     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
# #     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
# #     username = "ws_user_anon"
# #     try:
# #         from jose import jwt, JWTError
# #         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
# #         username = payload.get("sub", "ws_user_no_sub")
# #     except Exception as e_auth_ws: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e_auth_ws}"}); await websocket.close(1008); return
# #     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
# #     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}"})
# #     task_mon = AsyncResult(task_id)
# #     try:
# #         while True:
# #             if websocket.client_state != WebSocketState.CONNECTED: break
# #             cel_stat = task_mon.state
# #             doc_info_ws = documents_collection.find_one({"last_task_id":task_id}, {"status":1, "progress":1, "error_info":1, "_id":1})
# #             db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None
# #             doc_id_ws = str(doc_info_ws["_id"]) if doc_info_ws else None
# #             resp_ws = {"tid":task_id, "cs":cel_stat, "dbs":db_stat_ws, "did":doc_id_ws}
# #             if cel_stat == "PENDING": resp_ws["i"] = "Pending"
# #             elif cel_stat == "STARTED": resp_ws["i"] = "Started"
# #             elif cel_stat == "PROGRESS": resp_ws["i"] = "Progress"; resp_ws["pd"] = task_mon.info;
# #             elif cel_stat == "SUCCESS":
# #                 resp_ws["i"] = "SUCCESS (Celery)"; resp_ws["r"] = task_mon.result
# #                 if doc_id_ws and db_stat_ws != 1: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":1, "error_info":None}, "$push":{"progress":"Celery SUCCESS via WS"}})
# #                 await websocket.send_json(resp_ws); break
# #             elif cel_stat == "FAILURE":
# #                 resp_ws["i"] = "FAILURE (Celery)"; resp_ws["ed"] = str(task_mon.info)
# #                 if doc_id_ws and db_stat_ws != 2: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":2, "error_info":str(task_mon.info)}, "$push":{"progress":"Celery FAILURE via WS"}})
# #                 await websocket.send_json(resp_ws); break
# #             elif cel_stat == "RETRY": resp_ws["i"] = "RETRY"; resp_ws["rr"] = str(task_mon.info)
# #             else: resp_ws["i"] = f"State: {cel_stat}"
# #             await websocket.send_json(resp_ws)
# #             if task_mon.ready():
# #                 if cel_stat not in ["SUCCESS", "FAILURE"]:
# #                     final_resp_ws = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
# #                     if task_mon.state == "SUCCESS": final_resp_ws["r"] = task_mon.result
# #                     elif task_mon.state == "FAILURE": final_resp_ws["ed"] = str(task_mon.info)
# #                     await websocket.send_json(final_resp_ws)
# #                 break
# #             await asyncio.sleep(2)
# #     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
# #     except Exception as e_ws_main:
# #         print(f"WS Unhandled Error {task_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.send_json({"s":"error","m":"Server WS error."})
# #             except: pass
# #     finally:
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
# #             except RuntimeError: pass
# #         print(f"WS for task {task_id} ({username}) closed.")

# # # --- Main Execution ---
# # if __name__ == "__main__":
# #     import uvicorn
# #     print(f"--- GenAI API (Full Integration with DataSpaces) Starting ---")
# #     print(f"MongoDB URL: {MONGODB_URL}, DB: {MONGO_DB_NAME}")
# #     print(f"Input DIR: {INPUT_DIR}, Output DIR: {OUTPUT_DIR}")
# #     if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
# #         Path(test_case_utils.CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# #         print(f"CSV Output DIR (utils): {test_case_utils.CSV_OUTPUT_DIR}")
# #     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# # main3.py
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
# from bson import ObjectId 
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
# from utils.data_ingestion import extract_text_from_file

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
# class DataSpaceCreate(BaseModel): # Used by the old /data-spaces/ endpoint if you keep it
#     name: str = Field(..., min_length=3, max_length=100, description="Name of the Data Space")
#     description: Optional[str] = Field(None, max_length=500, description="Optional description")
#     # category: Optional[str] = Field(None, max_length=50) # If adding here too
#     # sub_category: Optional[str] = Field(None, max_length=50)

# class DataSpaceResponse(BaseModel):
#     data_space_id: str
#     name: str
#     description: Optional[str]
#     category: Optional[str] = None # Add if you want to return it
#     sub_category: Optional[str] = None # Add if you want to return it
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

# class UploadedFileDetail(BaseModel):
#     file_id: Optional[str] = None
#     file_name: str
#     status: str
#     error: Optional[str] = None
#     message: Optional[str] = None

# class BatchUploadResponse(BaseModel):
#     data_space_id: str
#     data_space_name: str
#     description: str
#     category:str
#     sub_category:str
#     message:str
#     uploaded_files: Dict[str, str] # {original_filename: new_file_id or error_string}
#     errors: Optional[List[Dict[str, str]]] = None

# class TokenRequest(BaseModel):
#     username: str
#     password: str

# class GenerateTaskResponseItem(BaseModel):
#     file_id: str
#     document_id:Optional[str] = None
#     task_id:Optional[str] = None
#     batch_id:str
#     message: str
#     error: Optional[str] = None

# class BatchGenerateTestCasesResponse(BaseModel):
#     generation_id:str
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
#     summary="Create Data Space with category/sub-category & Upload Documents"
# )
# async def create_dataspace_and_upload_documents(
#     data_space_name: str = Form(..., min_length=3, max_length=100, description="Name for the new Data Space."),
#     data_space_description: Optional[str] = Form(None, max_length=500, description="Optional description for the Data Space."),
#     category: str = Form(..., min_length=1, max_length=50, description="Category for the Data Space."),
#     sub_category: Optional[str] = Form(None, max_length=50, description="Sub-category for the Data Space."),
#     files: List[UploadFile] = File(..., description="Documents to upload to the new Data Space.")
# ):
#     # 1. Check for existing Data Space by name (if names should be globally unique)
#     # You might want to make uniqueness dependent on category/sub-category as well.
#     if data_spaces_collection.find_one({"name": data_space_name}): # Basic check
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Data Space with name '{data_space_name}' already exists.")

#     now = datetime.now(IST)
#     ds_doc_data = {
#         "name": data_space_name, "description": data_space_description,
#         "category": category, "sub_category": sub_category, # Store new fields
#         "created_at": now, "updated_at": now, "document_ids": []
#     }
#     insert_ds_result = data_spaces_collection.insert_one(ds_doc_data)
#     new_data_space_id_obj = insert_ds_result.inserted_id
#     new_data_space_id_str = str(new_data_space_id_obj)

#     if not files:
#         return BatchUploadResponse(
#             data_space_id=new_data_space_id_str, data_space_name=data_space_name,
#             message="Data Space created. No files provided for upload.", uploaded_files={}, errors=None
#         )
        
#     uploaded_files_map: Dict[str, str] = {}
#     successfully_uploaded_doc_object_ids: List[ObjectId] = []
#     individual_file_errors: List[Dict[str,str]] = []
    
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
#                 "data_space_id": new_data_space_id_obj, "file_name": original_filename, "file_path": str(file_path_on_disk),
#                 "content_type": file.content_type, "size": file_size, "status": -1, "timestamp": now,
#                 "test_cases": None, "progress": [], "error_info": None, "selected_model": None,
#                 "last_task_id": None, "requested_test_case_types": []
#             }
#             insert_doc_res = documents_collection.insert_one(doc_meta)
#             new_doc_obj_id = insert_doc_res.inserted_id
#             uploaded_files_map[original_filename] = str(new_doc_obj_id)
#             successfully_uploaded_doc_object_ids.append(new_doc_obj_id)
#         except Exception as e:
#             print(f"ERR PROC FILE '{original_filename}' for DS '{data_space_name}': {e}")
#             individual_file_errors.append({"filename": original_filename, "error": str(e)})
#             uploaded_files_map[original_filename] = f"ERROR: {str(e)}"
#             if os.path.exists(file_path_on_disk) and original_filename not in [k for k,v in uploaded_files_map.items() if "ERROR" not in v]:
#                  try: os.remove(file_path_on_disk)
#                  except Exception as e_del: print(f"Cleanup err {file_path_on_disk}: {e_del}")
#         finally: await file.close()

#     if successfully_uploaded_doc_object_ids:
#         data_spaces_collection.update_one(
#             {"_id": new_data_space_id_obj},
#             {"$set": {"document_ids": successfully_uploaded_doc_object_ids, "updated_at": datetime.now(IST)}}
#         )
#     elif files: # Files were provided but none successful, still update 'updated_at'
#          data_spaces_collection.update_one({"_id": new_data_space_id_obj}, {"$set": {"updated_at": datetime.now(IST)}})

#     msg = f"Data Space '{data_space_name}' (Category: {category}, Sub-Category: {sub_category or 'N/A'}) created. "
#     msg += f"{len(successfully_uploaded_doc_object_ids)} of {len(files)} files successfully uploaded and linked."
#     if individual_file_errors: msg += " Some files encountered errors."
    
#     return BatchUploadResponse(
#         data_space_id=new_data_space_id_str, data_space_name=data_space_name, description= data_space_description, category= category, sub_category=sub_category,message=msg,
#         uploaded_files=uploaded_files_map, errors=individual_file_errors if individual_file_errors else None
#     )

# @api_v1_router.get("/data-spaces/", response_model=List[DataSpaceResponse], tags=["Data Spaces"])
# async def list_data_spaces(skip: int = 0, limit: int = 20):
#     spaces_cursor = data_spaces_collection.find().sort("created_at", -1).skip(skip).limit(limit)
#     return [
#         DataSpaceResponse(
#             data_space_id=str(ds_doc["_id"]),
#             name=ds_doc.get("name"),
#             description=ds_doc.get("description"),
#             category=ds_doc.get("category"), # Include category in response
#             sub_category=ds_doc.get("sub_category"), # Include sub_category
#             created_at=ds_doc.get("created_at"),
#             document_count=documents_collection.count_documents({"data_space_id": ds_doc["_id"]})
#         ) for ds_doc in spaces_cursor
#     ]

# @api_v1_router.get("/data-spaces/{data_space_id}/documents/", response_model=List[DocumentMetadataResponse], tags=["Data Spaces"])
# async def list_documents_in_data_space(data_space_id: str, skip: int = 0, limit: int = 20):
#     try: ds_obj_id = ObjectId(data_space_id)
#     except InvalidId: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Data Space ID.")
#     if not data_spaces_collection.count_documents({"_id": ds_obj_id}, limit=1):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Space not found.")
#     docs_cursor = documents_collection.find({"data_space_id": ds_obj_id}).sort("timestamp", -1).skip(skip).limit(limit)
#     return [DocumentMetadataResponse(file_id=str(doc["_id"]), **doc) for doc in docs_cursor] # **doc assumes fields match

# @api_v1_router.delete("/data-spaces/{data_space_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Data Spaces"])
# async def delete_data_space(data_space_id: str, delete_contained_documents: bool = Query(False)):
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
#             if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'): # Ensure CSV_OUTPUT_DIR is defined in utils
#                 csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{str(doc['_id'])}_test_cases.csv")
#                 if os.path.exists(csv_p):
#                     try: os.remove(csv_p)
#                     except Exception as e: print(f"ERR DEL CSV {csv_p}: {e}")
#         documents_collection.delete_many({"data_space_id": ds_obj_id})
#     result = data_spaces_collection.delete_one({"_id": ds_obj_id})
#     if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Data Space found but failed to delete.")

# # --- Document Test Case Operations ---
# @api_v1_router.post("/documents/batch-generate-test-cases/", response_model=BatchGenerateTestCasesResponse, tags=["Document Test Cases"])

# # async def batch_generate_test_cases_for_documents(
# #     file_ids_str: str = Form(..., alias="file_ids", description="Comma-separated file_ids."),
# #     model_name: Optional[str] = Form("Mistral"),
# #     chunk_size: Optional[int] = Query(None),
# #     api_key: Optional[str] = Form(None),
# #     test_case_types: Optional[str] = Form("all"),
# # ):
# #     actual_file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
# #     if not actual_file_ids:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file_ids provided.")
# #     initiated_tasks_info: List[GenerateTaskResponseItem] = []
# #     api_key_to_use = api_key or os.getenv("TOGETHER_API_KEY")
# #     if not api_key_to_use:
# #         raise HTTPException(status_code=400, detail="API key required.")
# #     warning_msg = "Using default API key." if not api_key and os.getenv("TOGETHER_API_KEY") else None
# #     types_to_send, types_for_resp = "all", INDIVIDUAL_VALID_TEST_CASE_TYPES[:]
# #     if test_case_types.strip().lower() != "all":
# #         parsed = [t.strip().lower() for t in test_case_types.split(',') if t.strip()]
# #         validated = list(dict.fromkeys(t for t in parsed if t in INDIVIDUAL_VALID_TEST_CASE_TYPES))
# #         if not validated:
# #             raise HTTPException(status_code=400, detail="No valid types.")
# #         types_to_send, types_for_resp = ",".join(validated), validated
# #     for current_file_id in actual_file_ids:
# #         try:
# #             doc_obj_id = ObjectId(current_file_id)
# #             document = documents_collection.find_one({"_id": doc_obj_id})
# #             doc_id_str = str(document["_id"]) if document else None
# #             if not document:
# #                 initiated_tasks_info.append(GenerateTaskResponseItem(
# #                     file_id=current_file_id,
# #                     document_id=None,
# #                     task_id="N/A",
# #                     message="Failed: Doc not found.",
# #                     error="Doc not found"
# #                 ))
# #                 continue
# #             f_path_str = document.get("file_path")
# #             if not f_path_str or not Path(f_path_str).exists():
# #                 initiated_tasks_info.append(GenerateTaskResponseItem(
# #                     file_id=current_file_id,
# #                     document_id=doc_id_str,
# #                     task_id="N/A",
# #                     message="Failed: Doc file missing.",
# #                     error="File missing"
# #                 ))
# #                 continue
# #             documents_collection.update_one(
# #                 {"_id": doc_obj_id},
# #                 {"$set": {
# #                     "status": 0,
# #                     "selected_model": model_name,
# #                     "api_key_used": f"...{api_key_to_use[-5:]}" if api_key_to_use else "N/A",
# #                     "requested_test_case_types": types_for_resp,
# #                     "processing_start_time": datetime.now(IST),
# #                     "progress": ["Batch gen task init."],
# #                     "error_info": None,
# #                     "last_task_id": None
# #                 }}
# #             )
# #             task = process_and_generate_task.apply_async(
# #                 args=[str(Path(f_path_str)), model_name, chunk_size, api_key_to_use, types_to_send, current_file_id]
# #             )
# #             documents_collection.update_one(
# #                 {"_id": doc_obj_id},
# #                 {"$set": {"last_task_id": task.id}}
# #             )
# #             initiated_tasks_info.append(GenerateTaskResponseItem(
# #                 file_id=current_file_id,
# #                 document_id=doc_id_str,
# #                 task_id=task.id,
# #                 message="✅ TC gen task started."
# #             ))
# #         except InvalidId:
# #             initiated_tasks_info.append(GenerateTaskResponseItem(
# #                 file_id=current_file_id,
# #                 document_id=None,
# #                 task_id="N/A",
# #                 message="Failed: Invalid file_id.",
# #                 error="Invalid file_id"
# #             ))
# #         except Exception as e:
# #             initiated_tasks_info.append(GenerateTaskResponseItem(
# #                 file_id=current_file_id,
# #                 document_id=None,
# #                 task_id="N/A",
# #                 message=f"Failed: {type(e).__name__}.",
# #                 error=str(e)
# #             ))
# #     success_count = sum(1 for item in initiated_tasks_info if item.task_id != "N/A")
# #     return BatchGenerateTestCasesResponse(
# #         overall_message=f"Batch process done. {success_count}/{len(actual_file_ids)} tasks started.",
# #         tasks_initiated=initiated_tasks_info,
# #         warning=warning_msg
# #     )
# async def batch_generate_test_cases_for_documents(

#     data_space_id: str = Form(..., description="Data Space ID"),

#     model_name: Optional[str] = Form("Mistral"),

#     chunk_size: Optional[int] = Form(None),

#     api_key: Optional[str] = Form(None),

#     test_case_types: Optional[str] = Form("all")

# ):

#     from bson import ObjectId

#     from datetime import datetime

#     from zoneinfo import ZoneInfo

#     from pathlib import Path
 
#     IST = ZoneInfo("Asia/Kolkata")

#     now = datetime.now(IST)

#     VALID_TYPES = ["functional", "non-functional", "security", "performance", "boundary", "compliance"]

#     types_for_resp = VALID_TYPES if (not test_case_types or test_case_types.lower() == "all") else [

#         t.strip().lower() for t in test_case_types.split(",") if t.strip().lower() in VALID_TYPES

#     ]
 
#     try:

#         ds_obj_id = ObjectId(data_space_id)

#     except Exception:

#         raise HTTPException(status_code=400, detail="Invalid data_space_id.")
 
#     data_space = data_spaces_collection.find_one({"_id": ds_obj_id})

#     if not data_space:

#         raise HTTPException(status_code=404, detail="Data space not found.")
 
#     document_ids = data_space.get("document_ids", [])

#     if not document_ids:

#         raise HTTPException(status_code=400, detail="No documents in data space.")
 
#     files_embedded = []

#     file_objs = []

#     for doc_id in document_ids:

#         doc = documents_collection.find_one({"_id": doc_id})

#         if doc and Path(doc.get("file_path", "")).exists():

#             batch_id = ObjectId()

#             files_embedded.append({

#                 "batch_id": batch_id,

#                 "file_id": doc["_id"],

#                 "file_name": doc.get("file_name"),

#                 "status": 0,  # 0=pending, 1=done, 2=error

#                 "test_cases": [],

#                 "progress": [],

#                 "error_info": None

#             })

#             file_objs.append({"doc": doc, "batch_id": batch_id})
 
#     if not files_embedded:

#         raise HTTPException(status_code=400, detail="No valid files found.")
 
#     # Store the batch generation document in `documents_collection` (NOT a new collection)

#     batch_doc = {

#         "data_space_id": ds_obj_id,

#         "timestamp": now,

#         "model_used": model_name,

#         "requested_test_case_types": types_for_resp,

#         "status": 0,

#         "progress": ["Test case batch generation started."],

#         "files": files_embedded,

#         "is_test_case_generation_batch": True   # Flag for easy filtering if needed

#     }

#     insert_result = documents_collection.insert_one(batch_doc)

#     generation_id = str(insert_result.inserted_id)
 
#     from task_with_api_key import process_and_generate_task

#     initiated_tasks_info: List[GenerateTaskResponseItem] = []

#     for item in file_objs:

#         doc = item["doc"]

#         batch_id = item["batch_id"]

#         try:

#             task = process_and_generate_task.apply_async([

#                 doc["file_path"],

#                 model_name,

#                 chunk_size,

#                 api_key or os.getenv("TOGETHER_API_KEY"),

#                 ",".join(types_for_resp),

#                 generation_id,

#                 str(doc["_id"]),

#                 str(batch_id)

#             ])

#             documents_collection.update_one(

#                 {"_id": insert_result.inserted_id, "files.batch_id": batch_id},

#                 {"$set": {"files.$.last_task_id": task.id}}

#             )

#             initiated_tasks_info.append(GenerateTaskResponseItem(

#                 file_id=str(doc["_id"]),

#                 document_id=str(doc["_id"]),

#                 batch_id=str(batch_id),

#                 task_id=task.id,

#                 message="✅ TC gen task started.",

#                 error=None

#             ))

#         except Exception as e:

#             initiated_tasks_info.append(GenerateTaskResponseItem(

#                 file_id=str(doc["_id"]),

#                 document_id=str(doc["_id"]),

#                 batch_id=str(batch_id),

#                 task_id=None,

#                 message="Failed to start task.",

#                 error=str(e)

#             ))
 
#     success_count = sum(1 for item in initiated_tasks_info if item.task_id)

#     return BatchGenerateTestCasesResponse(
#         generation_id=str(insert_result.inserted_id),
#         overall_message=f"Batch process done. {success_count}/{len(files_embedded)} tasks started.",

#         tasks_initiated=initiated_tasks_info,

#         warning=None

#     )
 
 

 

 
 

 
 
 
 
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

# @api_v1_router.delete("/documents/", tags=["Document Test Cases"]) # Note: Query param for list of IDs
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
#         token = create_jwt_token(data={"sub": request.username, "role": "admin"})
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

# # @app.websocket("/ws/v1/task_status/{task_id}")
# # async def websocket_task_status_endpoint(websocket: WebSocket, task_id: str):
# #     token = websocket.query_params.get("token")
# #     if not SECRET_KEY_ENV: await websocket.accept(); await websocket.send_json({"s":"err","m":"JWT secret missing."}); await websocket.close(1011); return
# #     if not token: await websocket.accept(); await websocket.send_json({"s":"err","m":"Token missing."}); await websocket.close(1008); return
# #     username = "ws_user_anon"
# #     try:
# #         from jose import jwt, JWTError
# #         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])
# #         username = payload.get("sub", "ws_user_no_sub")
# #     except Exception as e_auth_ws: await websocket.accept(); await websocket.send_json({"s":"err","m":f"Auth fail WS: {e_auth_ws}"}); await websocket.close(1008); return
# #     await websocket.accept(); print(f"WS Conn: task {task_id}, user {username}")
# #     await websocket.send_json({"s":"connected", "m":f"Monitoring {task_id}"})
# #     task_mon = AsyncResult(task_id)
# #     try:
# #         while True:
# #             if websocket.client_state != WebSocketState.CONNECTED: break
# #             cel_stat = task_mon.state
# #             doc_info_ws = documents_collection.find_one({"last_task_id":task_id}, {"status":1, "progress":1, "error_info":1, "_id":1})
# #             db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None
# #             doc_id_ws = str(doc_info_ws["_id"]) if doc_info_ws else None
# #             resp_ws = {"tid":task_id, "cs":cel_stat, "dbs":db_stat_ws, "did":doc_id_ws}
# #             if cel_stat == "PENDING": resp_ws["i"] = "Pending"
# #             elif cel_stat == "STARTED": resp_ws["i"] = "Started"
# #             elif cel_stat == "PROGRESS": resp_ws["i"] = "Progress"; resp_ws["pd"] = task_mon.info;
# #             elif cel_stat == "SUCCESS":
# #                 resp_ws["i"] = "SUCCESS (Celery)"; resp_ws["r"] = task_mon.result
# #                 if doc_id_ws and db_stat_ws != 1: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":1, "error_info":None}, "$push":{"progress":"Celery SUCCESS via WS"}})
# #                 await websocket.send_json(resp_ws); break
# #             elif cel_stat == "FAILURE":
# #                 resp_ws["i"] = "FAILURE (Celery)"; resp_ws["ed"] = str(task_mon.info)
# #                 if doc_id_ws and db_stat_ws != 2: documents_collection.update_one({"_id":doc_info_ws["_id"]}, {"$set":{"status":2, "error_info":str(task_mon.info)}, "$push":{"progress":"Celery FAILURE via WS"}})
# #                 await websocket.send_json(resp_ws); break
# #             elif cel_stat == "RETRY": resp_ws["i"] = "RETRY"; resp_ws["rr"] = str(task_mon.info)
# #             else: resp_ws["i"] = f"State: {cel_stat}"
# #             await websocket.send_json(resp_ws)
# #             if task_mon.ready():
# #                 if cel_stat not in ["SUCCESS", "FAILURE"]:
# #                     final_resp_ws = {"tid":task_id, "cs":task_mon.state, "i":"Final state."}
# #                     if task_mon.state == "SUCCESS": final_resp_ws["r"] = task_mon.result
# #                     elif task_mon.state == "FAILURE": final_resp_ws["ed"] = str(task_mon.info)
# #                     await websocket.send_json(final_resp_ws)
# #                 break
# #             await asyncio.sleep(2)
# #     except WebSocketDisconnect: print(f"WS Client {username} (task {task_id}) disconnected.")
# #     except Exception as e_ws_main:
# #         print(f"WS Unhandled Error {task_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.send_json({"s":"error","m":"Server WS error."})
# #             except: pass
# #     finally:
# #         if websocket.client_state == WebSocketState.CONNECTED:
# #             try: await websocket.close(code=status.WS_1001_GOING_AWAY)
# #             except RuntimeError: pass
# #         print(f"WS for task {task_id} ({username}) closed.")

# @app.websocket("/ws/v1/task_status_by_doc/{doc_id}")

# async def websocket_task_status_by_doc(websocket: WebSocket, doc_id: str):

#     token = websocket.query_params.get("token")

#     if not SECRET_KEY_ENV:

#         await websocket.accept()

#         await websocket.send_json({"s": "err", "m": "JWT secret missing."})

#         await websocket.close(1011)

#         return

#     if not token:

#         await websocket.accept()

#         await websocket.send_json({"s": "err", "m": "Token missing."})

#         await websocket.close(1008)

#         return

#     username = "ws_user_anon"

#     try:

#         from jose import jwt, JWTError

#         payload = jwt.decode(token, SECRET_KEY_ENV, algorithms=[ALGORITHM_ENV])

#         username = payload.get("sub", "ws_user_no_sub")

#     except Exception as e_auth_ws:

#         await websocket.accept()

#         await websocket.send_json({"s": "err", "m": f"Auth fail WS: {e_auth_ws}"})

#         await websocket.close(1008)

#         return

#     await websocket.accept()

#     print(f"WS Conn: doc_id {doc_id}, user {username}")

#     await websocket.send_json({"s": "connected", "m": f"Monitoring document {doc_id}"})

#     try:

#         from bson import ObjectId

#         doc_obj_id = ObjectId(doc_id)

#     except Exception as e_invalid:

#         await websocket.send_json({"s": "err", "m": f"Invalid document ID: {e_invalid}"})

#         await websocket.close(1008)

#         return
 
#     try:

#         doc_info_ws = documents_collection.find_one({"_id": doc_obj_id})

#         if not doc_info_ws:

#             await websocket.send_json({"s": "err", "m": "Document not found."})

#             await websocket.close(1008)

#             return

#         task_id = doc_info_ws.get("last_task_id")

#         if not task_id:

#             await websocket.send_json({"s": "err", "m": "No Celery task_id associated with this document yet."})

#             await websocket.close(1008)

#             return

#         from celery.result import AsyncResult

#         from starlette.websockets import WebSocketState

#         import asyncio
 
#         task_mon = AsyncResult(task_id)

#         while True:

#             if websocket.client_state != WebSocketState.CONNECTED:

#                 break

#             # Always fetch fresh doc status

#             doc_info_ws = documents_collection.find_one({"_id": doc_obj_id})

#             db_stat_ws = doc_info_ws.get("status") if doc_info_ws else None

#             progress = doc_info_ws.get("progress", []) if doc_info_ws else []

#             error_info = doc_info_ws.get("error_info") if doc_info_ws else None
 
#             cel_stat = task_mon.state

#             resp_ws = {

#                 "task_id": task_id,

#                 "celery_state": cel_stat,

#                 "db_status": db_stat_ws,

#                 "document_id": doc_id,

#                 "progress": progress,

#                 "error_info": error_info,

#             }

#             # Optional: Add user-friendly info

#             if cel_stat == "PENDING":

#                 resp_ws["info"] = "Pending"

#             elif cel_stat == "STARTED":

#                 resp_ws["info"] = "Started"

#             elif cel_stat == "PROGRESS":

#                 resp_ws["info"] = "Progress"

#                 resp_ws["task_info"] = task_mon.info

#             elif cel_stat == "SUCCESS":

#                 resp_ws["info"] = "SUCCESS (Celery)"

#                 resp_ws["result"] = task_mon.result

#                 await websocket.send_json(resp_ws)

#                 break

#             elif cel_stat == "FAILURE":

#                 resp_ws["info"] = "FAILURE (Celery)"

#                 resp_ws["error_detail"] = str(task_mon.info)

#                 await websocket.send_json(resp_ws)

#                 break

#             elif cel_stat == "RETRY":

#                 resp_ws["info"] = "RETRY"

#                 resp_ws["retry_info"] = str(task_mon.info)

#             else:

#                 resp_ws["info"] = f"State: {cel_stat}"
 
#             await websocket.send_json(resp_ws)
 
#             if task_mon.ready():

#                 if cel_stat not in ["SUCCESS", "FAILURE"]:

#                     final_resp_ws = {"task_id": task_id, "celery_state": task_mon.state, "info": "Final state."}

#                     if task_mon.state == "SUCCESS":

#                         final_resp_ws["result"] = task_mon.result

#                     elif task_mon.state == "FAILURE":

#                         final_resp_ws["error_detail"] = str(task_mon.info)

#                     await websocket.send_json(final_resp_ws)

#                 break
 
#             await asyncio.sleep(2)
 
#     except WebSocketDisconnect:

#         print(f"WS Client {username} (doc {doc_id}) disconnected.")

#     except Exception as e_ws_main:

#         print(f"WS Unhandled Error {doc_id} ({username}): {type(e_ws_main).__name__} - {e_ws_main}")

#         if websocket.client_state == WebSocketState.CONNECTED:

#             try:

#                 await websocket.send_json({"s": "error", "m": "Server WS error."})

#             except:

#                 pass

#     finally:

#         if websocket.client_state == WebSocketState.CONNECTED:

#             try:

#                 await websocket.close(code=status.WS_1001_GOING_AWAY)

#             except RuntimeError:
#                 pass
#         print(f"WS for doc {doc_id} ({username}) closed.")

 
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


# from fastapi import  Body

# class TestCaseBatchRequest(BaseModel):
#     generation_id: str
#     file_ids: List[str]
#     types: Optional[List[str]] = None

# class TestCaseFileResult(BaseModel):
#     file_id: str
#     file_name: str
#     status: Optional[int]
#     progress: Optional[List[str]]
#     error_info: Optional[str]
#     test_cases: Optional[Dict[str, Any]]  # type: Dict[test_case_type, test_case_object]

# class TestCaseBatchResultResponse(BaseModel):
#     generation_id: str
#     requested_file_ids: List[str]
#     requested_types: Optional[List[str]]
#     results: List[TestCaseFileResult]

# @api_v1_router.post(
#     "/test-case-batch/results",
#     response_model=TestCaseBatchResultResponse,
#     tags=["Document Test Cases"]
# )
# async def get_test_case_batch_results(body: TestCaseBatchRequest = Body(...)):
#     from bson import ObjectId

#     batch = documents_collection.find_one({
#         "_id": ObjectId(body.generation_id),
#         "is_test_case_generation_batch": True
#     })
#     if not batch:
#         raise HTTPException(status_code=404, detail="Test case generation batch not found.")

#     requested_file_ids = set(body.file_ids)
#     types_list = [t.strip().lower() for t in (body.types or [])] if body.types else None

#     results = []
#     for file_doc in batch.get("files", []):
#         file_id_str = str(file_doc.get("file_id"))
#         if file_id_str in requested_file_ids:
#             all_cases = file_doc.get("test_cases", {})
#             # Filter by type if requested, else return all types
#             if types_list:
#                 filtered_cases = {t: all_cases.get(t) for t in types_list if t in all_cases}
#             else:
#                 filtered_cases = all_cases
#             results.append(TestCaseFileResult(
#                 file_id=file_id_str,
#                 file_name=file_doc.get("file_name"),
#                 status=file_doc.get("status"),
#                 progress=file_doc.get("progress"),
#                 error_info=file_doc.get("error_info"),
#                 test_cases=filtered_cases
#             ))

#     if not results:
#         raise HTTPException(status_code=404, detail="No matching files or test case types found.")

#     return TestCaseBatchResultResponse(
#         generation_id=body.generation_id,
#         requested_file_ids=body.file_ids,
#         requested_types=body.types,
#         results=results
#     )

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

<<<<<<< HEAD
=======
# from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional
# from dotenv import load_dotenv
# from pymongo import MongoClient
# from bson import ObjectId
# from bson.errors import InvalidId
# from pathlib import Path
# import os
# import re
# import time
# import uuid

# # Import your custom modules
# from utils import data_ingestion, test_case_utils, user_story_utils
# from utils.llms import Mistral, openai, llama

# # ----------------- FastAPI App Setup -----------------
# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ----------------- MongoDB Setup -----------------
# load_dotenv()

# mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
# db = mongo_client["Gen_AI"]
# collection = db["test_case_generation"]

# # ----------------- Directories Setup -----------------
# PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH")
# USER_STORY_PROMPT_FILE_PATH = os.getenv("USER_STORY_PROMPT_FILE_PATH")
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")

# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# DEFAULT_CHUNK_SIZE = 7000
# TEST_CASES_CACHE = {}

# # ----------------- Model Dispatcher -----------------
# MODEL_DISPATCHER = {
#     "Mistral": Mistral.generate_with_mistral,
#     "Openai": openai.generate_with_openai,
#     "Llama": llama.generate_with_llama,
# }

# # ----------------- Helpers -----------------
# def split_text_into_chunks(text, chunk_size=7000):
#     chunks = []
#     current_chunk = ""
#     sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
#     for sentence in sentences:
#         if len(current_chunk) + len(sentence) + 1 <= chunk_size:
#             current_chunk += sentence + " "
#         else:
#             chunks.append(current_chunk.strip())
#             current_chunk = sentence + " "
#     if current_chunk:
#         chunks.append(current_chunk.strip())
#     return chunks

# def serialize_document(doc):
#     doc["_id"] = str(doc["_id"])
#     return doc

# # ----------------- Main Endpoint -----------------
# @app.post("/process_and_generate/")
# async def process_and_generate(
#     file: UploadFile = File(...),
#     model_name: str = Form("Mistral"),
#     chunk_size: Optional[int] = Query(default=None),
#     cache_key: Optional[str] = Query(default=None),
# ):
#     try:
#         # ------------- Handle Cache -------------
#         if cache_key and cache_key in TEST_CASES_CACHE:
#             return JSONResponse(content={
#                 "test_cases": TEST_CASES_CACHE[cache_key]["test_cases"],
#                 "user_stories": TEST_CASES_CACHE[cache_key]["user_stories"],
#                 "cache_key": cache_key,
#                 "model_used": model_name
#             })

#         # ------------- Validate Model -------------
#         if model_name not in MODEL_DISPATCHER:
#             raise HTTPException(status_code=400, detail=f"Unsupported model: {model_name}")
#         generation_function = MODEL_DISPATCHER[model_name]

#         # ------------- Save Uploaded File -------------
#         file_name = file.filename
#         file_path = Path(INPUT_DIR) / file_name

#         try:
#             contents = await file.read()
#             with open(file_path, "wb") as f:
#                 f.write(contents)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Error saving PDF: {str(e)}")
#         finally:
#             await file.close()

#         # ------------- Process PDF -------------
#         brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
#         if not brd_text:
#             raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

#         cleaned_text = data_ingestion.clean_text(brd_text)
#         chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE

#         if model_name == "Mistral":
#             chunks =[cleaned_text]
#         else:
#             chunks = split_text_into_chunks(cleaned_text, chunk)

#         # ------------- Generate Test Cases -------------
#         all_test_cases = []
#         all_user_stories = []
#         start_time = time.time()

#         for idx, chunk_text in enumerate(chunks):
#             print(f"Processing chunk {idx+1}/{len(chunks)} with model {model_name}")
#             test_case_text = test_case_utils.generate_test_cases(
#                 chunk_text, generation_function, PROMPT_FILE_PATH
#             )
#             user_stories_text = user_story_utils.generate_user_stories(chunk_text,
#                                                                        generation_function, 
#                                                                        USER_STORY_PROMPT_FILE_PATH)
#             if test_case_text:
#                 all_test_cases.append(test_case_text)
#             if user_stories_text:
#                 all_user_stories.append(user_stories_text)

#         combined_test_cases = "\n".join(all_test_cases)
#         combined_user_stories = "\n".join(all_user_stories)
#         end_time = time.time()
#         generation_latency = int(end_time - start_time)

#         # # ------------- Generate User Stories -------------
#         # user_stories_text = user_story_utils.generate_user_stories(
#         #     cleaned_text, generation_function, USER_STORY_PROMPT_FILE_PATH
#         # )

#         # ------------- Save Outputs -------------
#         base_stem = Path(file_name).stem

#         output_test_case_path = Path(OUTPUT_DIR) / f"{base_stem}_test_cases.txt"
#         with open(output_test_case_path, "w", encoding="utf-8") as f:
#             f.write(combined_test_cases)

#         output_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.txt"
#         with open(output_user_story_path, "w", encoding="utf-8") as f:
#             f.write(user_stories_text)

#         # ------------- Save to MongoDB and Cache -------------
#         if not cache_key:
#             cache_key = str(uuid.uuid4())

#         TEST_CASES_CACHE[cache_key] = {
#             "test_cases": combined_test_cases,
#             "user_stories": combined_user_stories
#         }

#         document = {
#             "doc_name": file.filename,
#             "doc_path": str(file_path),
#             "selected_model": model_name,
#             "llm_response_testcases": combined_test_cases,
#             "llm_response_user_stories": user_stories_text,
#             "llm_response_latency": generation_latency,
#         }
#         collection.insert_one(document)

#         return JSONResponse(content={
#             "test_cases": combined_test_cases,
#             "user_stories": combined_user_stories,
#             "cache_key": cache_key,
#             "model_used": model_name
#         })

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # ----------------- MongoDB Fetch Endpoints -----------------
# @app.get("/documents/")
# def get_all_documents():
#     documents = list(collection.find())
#     return [serialize_document(doc) for doc in documents]

# @app.get("/documents/{document_id}")
# def get_document_by_id(document_id: str):
#     try:
#         doc = collection.find_one({"_id": ObjectId(document_id)})
#         if not doc:
#             raise HTTPException(status_code=404, detail="Document not found")
#         return serialize_document(doc)
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid document ID format")



from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import JSONResponse
>>>>>>> cfb30743f31121e23fdb500f60820d7629b746ea
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

<<<<<<< HEAD
=======
# ----------------- FastAPI App Setup -----------------
app = FastAPI(root_path="/backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- MongoDB Setup -----------------
>>>>>>> cfb30743f31121e23fdb500f60820d7629b746ea
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
<<<<<<< HEAD
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
=======
            raise HTTPException(status_code=400, detail=f"Error saving PDF: {str(e)}")
        finally:
            await file.close()

        # ------------- Process PDF -------------
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
        if not brd_text:
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF.")
>>>>>>> cfb30743f31121e23fdb500f60820d7629b746ea

    msg = f"Data Space '{data_space_name}' (Category: {category}, Sub-Category: {sub_category or 'N/A'}) created. "
    msg += f"{len(successfully_uploaded_doc_object_ids)} of {len(files)} files successfully uploaded and linked."
    if individual_file_errors:
        msg += " Some files encountered errors."

<<<<<<< HEAD
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
    data_spaces = []
    for ds_doc in spaces_cursor:
        ds_id = ds_doc["_id"]
        # Count documents with either ObjectId or string representation
        doc_count = documents_collection.count_documents({
            "data_space_id": {"$in": [ds_id, str(ds_id)]}
        })
        data_spaces.append(
            DataSpaceResponse(
                data_space_id=str(ds_id),
                name=ds_doc.get("name"),
                description=ds_doc.get("description"),
                category=ds_doc.get("category"),
                sub_category=ds_doc.get("sub_category"),
                created_at=ds_doc.get("created_at"),
                document_count=doc_count
=======
        # ------------- Chunking Based on Model -------------
        if model_name == "Mistral":
            chunks = [cleaned_text]
        else:
            chunks = split_text_into_chunks(cleaned_text, chunk)
            if not chunks:
                chunks = [cleaned_text]

        # ------------- Generate Test Cases -------------
        all_test_cases = []
        start_time = time.time()    

        for idx, chunk_text in enumerate(chunks):
            print(f"Processing chunk {idx+1}/{len(chunks)} with model {model_name} for Test Cases")
            test_case_text = test_case_utils.generate_test_cases(
                chunk_text, generation_function, PROMPT_FILE_PATH
>>>>>>> cfb30743f31121e23fdb500f60820d7629b746ea
            )
        )
    return data_spaces


<<<<<<< HEAD
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
    model_name: Optional[str] = Form("Mistral"),
    chunk_size: Optional[int] = Form(None),
    api_key: Optional[str] = Form(None),
    test_case_types: Optional[str] = Form("all"),
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
=======
        # ------------- Generate User Stories -------------
        all_user_stories = []
        start_time_user_story = time.time()

        for idx, chunk_text in enumerate(chunks):
            print(f"Processing chunk {idx+1}/{len(chunks)} with model {model_name} for User Stories")
            user_story_text = user_story_utils.generate_user_stories(
                chunk_text, generation_function, USER_STORY_PROMPT_FILE_PATH
            )
            if user_story_text:
                all_user_stories.append(user_story_text)

        combined_user_stories = "\n".join(all_user_stories)
        end_time_user_story = time.time()
        user_story_generation_latency = int(end_time_user_story - start_time_user_story)
>>>>>>> cfb30743f31121e23fdb500f60820d7629b746ea

    return BatchGenerateTestCasesResponse(
        generation_id=generation_id_str, # Return string representation of the ID
        overall_message=f"Batch process initiation done. {success_count}/{len(file_objs)} tasks started.",
        tasks_initiated=initiated_tasks_info,
        warning=None if api_key or not os.getenv("TOGETHER_API_KEY") else "Using default API key."
    )

<<<<<<< HEAD
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
=======
        output_test_case_path = Path(OUTPUT_DIR) / f"{base_stem}_test_cases.txt"
        with open(output_test_case_path, "w", encoding="utf-8") as f:
            f.write(combined_test_cases)

        output_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.txt"
        with open(output_user_story_path, "w", encoding="utf-8") as f:
            f.write(combined_user_stories)

        # ------------- Save to MongoDB and Cache -------------
        if not cache_key:
            cache_key = str(uuid.uuid4())

        TEST_CASES_CACHE[cache_key] = {
            "test_cases": combined_test_cases,
            "user_stories": combined_user_stories
        }

        document = {
            "doc_name": file.filename,
            "doc_path": str(file_path),
            "selected_model": model_name,
            "llm_response_testcases": combined_test_cases,
            "llm_response_user_stories": combined_user_stories,
            "llm_response_latency": generation_latency,
        }
        collection.insert_one(document)

        return JSONResponse(content={
            "test_cases": combined_test_cases,
            "user_stories": combined_user_stories,
            "cache_key": cache_key,
            "model_used": model_name
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        # For server-side errors (like DB failures)
        raise HTTPException(status_code=500, detail="Server error. Please try again later.")

# ----------------- MongoDB Fetch Endpoints -----------------
@app.get("/documents/")
def get_all_documents():
    documents = list(collection.find())
    return [serialize_document(doc) for doc in documents]

@app.get("/documents/{document_id}")
def get_document_by_id(document_id: str):
>>>>>>> cfb30743f31121e23fdb500f60820d7629b746ea
    try:
        # Assuming parse_test_cases_to_csv returns (csv_path, list_of_test_case_dicts)
        # And that list_of_test_case_dicts is what we need here, not the content of the 'test_cases' field in DB directly
        # If 'test_cases' field in DB already holds the structured data, this call might be for CSV generation only.
        # For JSON output, we should ideally use the 'test_cases' field if it's structured.
        # The current implementation implies parse_test_cases_to_csv also structures it.
        # Let's assume doc.get("test_cases") is a dictionary like {"functional": [...], "security": [...]}
        all_tc_from_db = doc.get("test_cases") # This should be the primary source for JSON.
        if not all_tc_from_db or not isinstance(all_tc_from_db, dict):
             _, all_r_parsed_from_raw = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection, force_reparse_for_json=True) # You might need a flag
             if not all_r_parsed_from_raw : return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"No TCs parsed or found in DB."}
             # If parse_test_cases_to_csv returns a flat list of dicts, each with a "Test type" key:
             all_r = all_r_parsed_from_raw
        else: # test_cases field is structured: {"functional": [...], "security": [...]}
            # We need to flatten it into a list of dicts, each with a "Test type" for current filtering logic
            all_r_flat = []
            for tc_type, tc_list in all_tc_from_db.items():
                if isinstance(tc_list, list):
                    for tc_item_dict in tc_list:
                        if isinstance(tc_item_dict, dict):
                             all_r_flat.append({**tc_item_dict, "Test type": tc_type}) # Add/overwrite "Test type"
            all_r = all_r_flat
            if not all_r : return {**base_res, **empty_tc_res, "status_code":1, "status_message":"completed_no_data", "detail":"TCs field in DB is empty or not structured as expected."}

        final_r, applied_f = all_r, []
        if types:
            f_lower=[t.strip().lower() for t in types.split(',') if t.strip()]
            applied_f=[t.strip() for t in types.split(',') if t.strip()] # For display
            if f_lower: final_r=[tc for tc in all_r if tc.get("Test type","").lower() in f_lower]

        cts = Counter(); total_c = 0
        if final_r: # Count from the filtered list
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
# async def get_document_test_case_summary(file_id: str):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     status_val = doc.get("status")
#     base_res = {"file_id":file_id, "data_space_id":str(doc.get("data_space_id")) if doc.get("data_space_id") else None, "file_name":doc.get("file_name")}
#     if status_val != 1: raise HTTPException(status_code=409, detail=f"Summary not available. Status: {status_val}")

#     # Directly use the test_cases field from the document if it's structured
#     # e.g., test_cases: {"functional": [...], "performance": [...]}
#     db_test_cases = doc.get("test_cases")
#     if isinstance(db_test_cases, dict) and db_test_cases:
#         counts_by_type = {}
#         total_test_cases = 0
#         for tc_type, tc_list in db_test_cases.items():
#             if isinstance(tc_list, list):
#                 count = len(tc_list)
#                 counts_by_type[tc_type] = count
#                 total_test_cases += count
#         if not counts_by_type: # DB field was dict but empty, or values not lists
#              return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, but test cases structure in DB is empty or invalid for summary."}
#         return {**base_res, "counts_by_type":counts_by_type, "total_test_cases":total_test_cases}
#     else: # Fallback to parsing if not structured or not present
#         try:
#             _, parsed_list = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection, force_reparse_for_json=True) # Assuming this returns a flat list
#             if not parsed_list: return {**base_res, "counts_by_type":{}, "total_test_cases":0, "message":"Completed, no TCs parsed by utility."}
#             cts = Counter(tc.get("Test type", "Not Specified") for tc in parsed_list)
#             return {**base_res, "counts_by_type":dict(cts), "total_test_cases":len(parsed_list)}
#         except Exception as e_sum: print(f"ERR SUMM {file_id}: {e_sum}"); raise HTTPException(status_code=500,detail=f"Err gen summ via parsing: {str(e_sum)}")
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

# @api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
# async def download_test_cases_csv_for_document(file_id: str):
#     try: doc_obj_id = ObjectId(file_id)
#     except InvalidId: raise HTTPException(status_code=400, detail="Invalid file_id.")
#     doc = documents_collection.find_one({"_id": doc_obj_id})
#     if not doc: raise HTTPException(status_code=404, detail="Doc not found.")
#     if doc.get("status") != 1: raise HTTPException(status_code=409, detail="CSV not ready. Document processing not complete or failed.")
#     fname = doc.get("file_name", "doc.pdf")
#     try:
#         # This function should create the CSV if not exists or outdated, and return path
#         csv_p, _ = test_case_utils.parse_test_cases_to_csv(file_id, documents_collection)
#     except Exception as e_parse_csv:
#         print(f"Error generating CSV for {file_id}: {e_parse_csv}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate CSV file: {str(e_parse_csv)}")
#     if not os.path.exists(csv_p): raise HTTPException(status_code=404, detail="CSV file missing post-parse attempt. Generation might have failed.")
#     return FileResponse(csv_p, media_type="text/csv", filename=f"{Path(fname).stem}_test_cases.csv")

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

@api_v1_router.get("/documents/{file_id}/download-csv/", tags=["Document Test Cases"])
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


# from fastapi import APIRouter, Query, HTTPException
# from fastapi.responses import StreamingResponse, FileResponse
# from typing import List, Optional
# from io import StringIO, BytesIO
# import csv
# import tempfile
# import zipfile
# from bson import ObjectId
# import io


# def get_file_entry(documents_collection, file_id):
#     """Find a file entry in a test case generation batch document."""
#     batch = documents_collection.find_one({
#         "is_test_case_generation_batch": True,
#         "files.file_id": ObjectId(file_id)
#     })
#     if not batch:
#         return None, None
#     for f in batch["files"]:
#         if str(f["file_id"]) == str(file_id):
#             return batch, f
#     return None, None

# def parse_test_cases(content: str):
#     # Split by --- or double newline
#     blocks = re.split(r'---+|\n\s*\n(?=TCID:)', content)
#     cases = []
#     for block in blocks:
#         data = {
#             "Test type": "",
#             "TCID": "",
#             "Title": "",
#             "Description": "",
#             "Precondition": "",
#             "Steps": "",
#             "Action": "",
#             "Data": "",
#             "Result": "",
#             "Test Nature": "",
#             "Test priority": ""
#         }
#         lines = block.strip().split('\n')
#         for line in lines:
#             line = line.strip()
#             # Try all keys
#             for key in data.keys():
#                 pat = f"{key}:"
#                 if line.lower().startswith(pat.lower()):
#                     data[key] = line[len(pat):].strip()
#         # Only include if there is a TCID or Title
#         if data["TCID"] or data["Title"]:
#             cases.append(data)
#     return cases


# @api_v1_router.get("/documents/download-testcases", tags=["Document Test Cases"])
# async def download_testcases(
#     file_ids: str = Query(..., description="Comma-separated file_ids"),
#     types: str = Query(..., description="Comma-separated test case types"),
#     mode: str = Query("zip", description="'zip' for ZIP with CSVs, 'csv' for single CSV if one file")
# ):
#     file_id_list = [f.strip() for f in file_ids.split(",") if f.strip()]
#     type_list = [t.strip().lower() for t in types.split(",") if t.strip()]
#     if not file_id_list:
#         raise HTTPException(400, detail="No file_ids provided")
#     if not type_list:
#         raise HTTPException(400, detail="No test case types provided")
    
#     # Find the batch document containing any of these files
#     batch = documents_collection.find_one({
#         "is_test_case_generation_batch": True,
#         "files.file_id": {"$in": [ObjectId(fid) for fid in file_id_list]}
#     })
#     if not batch:
#         raise HTTPException(404, detail="Batch document not found for given file(s)")

#     file_entries = []
#     for f in batch["files"]:
#         fid = str(f["file_id"])
#         if fid in file_id_list:
#             file_entries.append(f)

#     if not file_entries:
#         raise HTTPException(404, detail="No files found with provided file_ids")

#     # Fieldnames for CSV
#     csv_fields = [
#         "Test type", "TCID", "Title", "Description", "Precondition",
#         "Steps", "Action", "Data", "Result", "Test Nature", "Test priority"
#     ]

#     # Helper to extract test cases case-insensitively
#     def get_case_insensitive(tc_dict, key):
#         """Returns the value in tc_dict matching key, ignoring case, or None."""
#         key = key.lower()
#         for k, v in tc_dict.items():
#             if k.lower() == key:
#                 return k, v
#         return None, None

#     # Single CSV for one file, else ZIP
#     if mode == "csv" and len(file_entries) == 1:
#         file_entry = file_entries[0]
#         output = io.StringIO()
#         writer = csv.DictWriter(output, fieldnames=csv_fields)
#         writer.writeheader()
#         for t in type_list:
#             tc_dict = file_entry.get("test_cases", {})
#             found_key, tc_obj = get_case_insensitive(tc_dict, t)
#             if tc_obj and tc_obj.get("content"):
#                 for row in parse_test_cases(tc_obj["content"]):
#                     row["Test type"] = found_key or t
#                     writer.writerow(row)
#         output.seek(0)
#         filename = f"{file_entry.get('file_name', 'testcases')}_test_cases.csv"
#         return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv", headers={
#             "Content-Disposition": f"attachment; filename={filename}"
#         })

#     # --- Multiple files: ZIP with CSVs ---
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#         for file_entry in file_entries:
#             rows = []
#             for t in type_list:
#                 tc_dict = file_entry.get("test_cases", {})
#                 found_key, tc_obj = get_case_insensitive(tc_dict, t)
#                 if tc_obj and tc_obj.get("content"):
#                     for row in parse_test_cases(tc_obj["content"]):
#                         row["Test type"] = found_key or t
#                         rows.append(row)
#             if not rows:
#                 continue
#             # Write this file's CSV into the zip
#             csv_stream = io.StringIO()
#             writer = csv.DictWriter(csv_stream, fieldnames=csv_fields)
#             writer.writeheader()
#             for row in rows:
#                 writer.writerow(row)
#             csv_bytes = csv_stream.getvalue().encode()
#             filename = f"{file_entry.get('file_name', 'testcases')}_test_cases.csv"
#             zipf.writestr(filename, csv_bytes)
#     zip_buffer.seek(0)
#     return StreamingResponse(zip_buffer, media_type="application/x-zip-compressed", headers={
#         "Content-Disposition": "attachment; filename=testcases.zip"
#     })

from fastapi import APIRouter, Query, HTTPException, status # Added status
from fastapi.responses import StreamingResponse # FileResponse might not be needed if always streaming
from typing import List, Optional # Already in your main file likely
from io import StringIO, BytesIO
import csv
# import tempfile # Not strictly needed if using BytesIO for zip
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
        "Test type", "TCID", "Title", "Description", "Precondition",
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


# @api_v1_router.delete("/documents/", tags=["Document Test Cases"]) # Note: Query param for list of IDs
# async def delete_multiple_documents(document_ids: List[str] = Query(...)):
#     del_c, errs = 0, []
#     if not document_ids:
#         raise HTTPException(status_code=400, detail="No document_ids provided for deletion.")
#     for id_str in document_ids:
#         try:
#             obj_id = ObjectId(id_str)
#             doc = documents_collection.find_one_and_delete({"_id":obj_id})
#             if doc:
#                 del_c+=1
#                 if doc.get("file_path") and os.path.exists(doc["file_path"]):
#                     try: os.remove(doc["file_path"])
#                     except Exception as e_fdel: print(f"Error deleting file {doc['file_path']}: {e_fdel}")
#                 if hasattr(test_case_utils, 'CSV_OUTPUT_DIR'):
#                     csv_p = os.path.join(test_case_utils.CSV_OUTPUT_DIR, f"{id_str}_test_cases.csv")
#                     if os.path.exists(csv_p):
#                         try: os.remove(csv_p)
#                         except Exception as e_csvdel: print(f"Error deleting CSV {csv_p}: {e_csvdel}")
#             else: errs.append({"id":id_str, "error":"Not found"})
#         except InvalidId: errs.append({"id":id_str, "error":"Invalid ID format"})
#         except Exception as e_del: errs.append({"id":id_str, "error":str(e_del)})
#     if del_c == 0 and not errs and document_ids: # If IDs were provided but none were found and no other errors
#         return {"deleted_count": 0, "errors": [{"id": "all_provided", "error": "None of the provided document IDs were found."}]}
#     return {"deleted_count":del_c, "errors":errs if errs else None}


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

    # If files were found, but after filtering, no actual test cases are returned in any result object
    # This condition needs care: do we 404 if results list contains objects but all have empty test_cases?
    # The current Postman response shows `{"detail": "Not Found"}` which suggests a 404.
    # Let's check if *all* results have empty test_cases.
    all_results_have_empty_cases = True
    if results: # only if we have some results to check
        for res_item in results:
            if res_item.test_cases and len(res_item.test_cases) > 0:
                all_results_have_empty_cases = False
                break
    
    if not results or (results and all_results_have_empty_cases and types_list_lower):
        # If 'results' is empty (no requested file_ids led to any result entry)
        # OR if 'results' has entries, but all of them have empty 'test_cases' AND a type filter was applied
        # this implies the types requested didn't match anything.
        # The original Postman error was a general "Not Found".
        # This could mean no matching files OR no matching test cases for the types.
        # The `if not found_any_requested_file_in_batch:` above handles "no matching files".
        # This handles "files matched, but no test cases for those types".
        # The original issue was a 404 for the entire endpoint, this is a 404 for the *content*.
        # The example 404 response was `{"detail":"Not Found"}`.
        # A more specific message for this case:
        if results and all_results_have_empty_cases and types_list_lower:
             # This means files were found, types were requested, but no test cases matched those types
             # We return the results list (which will contain file statuses but empty test_cases)
             # The API contract might decide if this should be a 200 with empty data or a 404.
             # For now, let's align with returning data if files are found, even if TCs are empty due to filter.
             # The initial 404 was likely due to the route not being found.
             # The prompt's 404 example `{"detail": "Not Found"}` could be from `if not batch:`
             # or from `if not results:` (the one commented out in the original user code).
             # The original code's `if not results:` before the return was:
             # `if not results: raise HTTPException(status_code=404, detail="No matching files or test case types found.")`
             # This is reasonable. If after all processing, `results` is empty, then 404.
             pass # Let it proceed to return if `results` has items, even with empty `test_cases`
        elif not results: # This means no file_id from the request was found in the batch that warranted an entry in `results`
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
        # Add role check if necessary:
        # if payload.get("role") != "admin":
        #     await websocket.accept()
        #     await websocket.send_json({"s": "err", "m": "Insufficient permissions."})
        #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        #     return
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

            doc_info_ws = documents_collection.find_one(
                {"_id": doc_obj_id},
                {"status": 1, "progress": 1, "error_info": 1, "last_task_id": 1, "test_cases": 1, "file_name": 1, "requested_test_case_types": 1}
            )

            if not doc_info_ws:
                await websocket.send_json({"status": "error", "message": f"Document '{doc_id}' not found."})
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE) # Or a specific error code
                break

            current_task_id = doc_info_ws.get("last_task_id")
            db_status_code = doc_info_ws.get("status")
            progress_log = doc_info_ws.get("progress", [])
            error_message_db = doc_info_ws.get("error_info")
            # test_cases_summary_ws = {k: len(v) if isinstance(v, list) else 0 for k,v in doc_info_ws.get("test_cases", {}).items()}
            generated_types_ws = list(doc_info_ws.get("test_cases", {}).keys())


            celery_state_str = "N/A"
            celery_task_info = None
            celery_result = None
            celery_error_detail = None

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
                    elif celery_state_str == "SUCCESS":
                        celery_result = task_mon.result # Be cautious with large results
                    elif celery_state_str == "FAILURE":
                        celery_error_detail = str(task_mon.info) # Celery error info
            elif initial_check:
                 await websocket.send_json({"status": "info", "message": "No Celery task ID yet associated with this document. Waiting for generation to start."})


            response_payload = {
                "document_id": doc_id,
                "file_name": doc_info_ws.get("file_name", "N/A"),
                "database_status_code": db_status_code,
                "database_status_message": {-1: "Pending Generation", 0: "Processing", 1: "Completed Successfully", 2: "Error"}.get(db_status_code, "Unknown"),
                "progress_log": progress_log,
                "database_error_info": error_message_db,
                "celery_task_id": current_task_id,
                "celery_task_state": celery_state_str,
                "celery_task_progress_info": celery_task_info,
                "requested_test_case_types": doc_info_ws.get("requested_test_case_types", []),
                "generated_test_case_types": generated_types_ws
            }

            await websocket.send_json(response_payload)
            initial_check = False # No longer the initial check

            # Conditions to break the loop from server-side (e.g., task completed or failed)
            if db_status_code == 1: # Completed successfully
                await websocket.send_json({"status": "final", "message": "Test case generation completed successfully."})
                break
            if db_status_code == 2: # Error in DB
                await websocket.send_json({"status": "final", "message": f"Test case generation failed. DB Error: {error_message_db}"})
                break
            if task_mon and task_mon.ready(): # Celery task is done (SUCCESS or FAILURE)
                # DB status might not be updated yet by Celery task, this provides faster Celery feedback
                if celery_state_str == "SUCCESS":
                     await websocket.send_json({"status": "info", "message": f"Celery task {current_task_id} reported SUCCESS. Waiting for DB update if any."})
                     # Don't break yet, wait for DB status 1 to confirm finalization
                elif celery_state_str == "FAILURE":
                     await websocket.send_json({"status": "info", "message": f"Celery task {current_task_id} reported FAILURE: {celery_error_detail}. Waiting for DB update."})
                     # Don't break yet, wait for DB status 2

            await asyncio.sleep(3) # Poll interval

    except WebSocketDisconnect:
        print(f"WS Client '{username}' (doc '{doc_id}') disconnected.")
    except Exception as e_ws_main:
        error_type_name = type(e_ws_main).__name__
        print(f"WS Unhandled Error for doc '{doc_id}' (user '{username}'): {error_type_name} - {e_ws_main}")
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

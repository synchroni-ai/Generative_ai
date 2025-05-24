
# from typing import Optional, Union, List, Tuple

# from celery_worker import celery_app
# from utils import data_ingestion, test_case_utils
# from utils.llms import Mistral, openai, llama
# from bson import ObjectId
# from bson.errors import InvalidId # Correct import for InvalidId
# import os
# import re
# from pathlib import Path
# from pymongo import MongoClient
# from datetime import datetime, timezone # For UTC timestamping

# # --- MongoDB Setup ---
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

# generation_batch_collection = None
# try:
#     mongo_client = MongoClient(MONGODB_URL)
#     db = mongo_client[MONGO_DB_NAME]
#     # This collection is used for:
#     # 1. Storing batch metadata documents (is_test_case_generation_batch: True)
#     # 2. Storing original uploaded document metadata (these are the ones WebSocket/get-test-cases queries)
#     generation_batch_collection = db["test_case_generation"]
#     print(f"TASK_WORKER: Successfully connected to MongoDB: {MONGODB_URL} - DB: {MONGO_DB_NAME}")
# except Exception as e:
#     print(f"TASK_WORKER_CRITICAL: Failed to connect to MongoDB: {e}")

# # --- Constants and Configuration ---
# INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
# OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
# Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# DEFAULT_CHUNK_SIZE = 7000
# MODEL_DISPATCHER = {
#     "Mistral": Mistral.generate_with_mistral,
#     "Openai": openai.generate_with_openai,
#     "Llama": llama.generate_with_llama,
# }
# VALID_TEST_CASE_TYPES = [
#     "functional", "non-functional", "security",
#     "performance", "boundary", "compliance",
# ]

# # --- Helper Functions ---
# def split_text_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
#     chunks = []
#     current_chunk = ""
#     sentences = re.split(r'(?<=[.?!])\s+', text.replace('\r\n', ' ').replace('\n', ' ').strip())
#     for sentence in sentences:
#         if not sentence.strip(): continue
#         if len(current_chunk) + len(sentence) + 1 <= chunk_size:
#             current_chunk += sentence + " "
#         else:
#             if current_chunk.strip(): chunks.append(current_chunk.strip())
#             current_chunk = sentence + " "
#     if current_chunk.strip(): chunks.append(current_chunk.strip())
#     if not chunks and text.strip(): chunks.append(text.strip())
#     return chunks

# def process_document_and_get_chunks(
#     file_path: str, model_name: str, chunk_size_param: Optional[int]
# ) -> Tuple[List[str], str]:
#     print(f"\n--- DBG_PDAGC: ENTER for: {Path(file_path).name} ---")
#     print(f"DBG_PDAGC: model_name='{model_name}', chunk_size_param={chunk_size_param}")
#     try:
#         brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
#     except Exception as e:
#         print(f"DBG_PDAGC: ERROR loading document {file_path}: {e}")
#         raise ValueError(f"Failed to load text: {file_path}") from e
#     if not brd_text or not brd_text.strip():
#         print(f"DBG_PDAGC: WARNING - No text extracted: {file_path}. Returning empty.")
#         return [], ""
#     cleaned_full_text = data_ingestion.clean_text(brd_text)
#     if not cleaned_full_text.strip():
#         print(f"DBG_PDAGC: WARNING - Cleaned text empty: {file_path}. Returning empty.")
#         return [], cleaned_full_text
#     MODELS_THAT_GET_ONE_CHUNK = ["Openai", "Mistral"]
#     final_chunks: List[str]
#     if model_name in MODELS_THAT_GET_ONE_CHUNK:
#         print(f"DBG_PDAGC: Model '{model_name}' IS IN one-chunk list. Using full text.")
#         final_chunks = [cleaned_full_text]
#     else:
#         eff_chunk_size = chunk_size_param if chunk_size_param and chunk_size_param > 0 else DEFAULT_CHUNK_SIZE
#         print(f"DBG_PDAGC: Model '{model_name}' NOT in one-chunk list. Splitting, target size ~{eff_chunk_size}.")
#         final_chunks = split_text_into_chunks(cleaned_full_text, eff_chunk_size)
#         if not final_chunks and cleaned_full_text:
#             print(f"DBG_PDAGC: WARNING - Splitting for '{model_name}' empty, using full text (fallback).")
#             final_chunks = [cleaned_full_text]
#     print(f"DBG_PDAGC: FINAL - Processed into {len(final_chunks)} chunk(s) for '{model_name}'.")
#     print(f"--- DBG_PDAGC: EXIT for: {Path(file_path).name} ---\n")
#     return final_chunks, cleaned_full_text

# # --- Celery Task ---
# @celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task")
# def process_and_generate_task(
#     self, file_path: str, model_name: str, chunk_size: Optional[int],
#     api_key: Optional[str], test_case_types: Union[str, List[str]],
#     generation_id: str, file_id: str, batch_id: str ): # file_id IS THE ORIGINAL DOCUMENT ID

#     print(f"\n--- CELERY TASK START (task_id: {self.request.id}) ---")
#     print(f"Processing file: {Path(file_path).name}, Original Doc ID (file_id): {file_id}")
#     print(f"Model: '{model_name}', Batch Gen ID: {generation_id}, DB Batch File ID: {batch_id}")
#     api_key_disp = f"'{api_key[:10]}...'" if api_key and len(api_key) > 10 else f"'{api_key}'"
#     print(f"Received 'api_key' param from FastAPI: {api_key_disp}")

#     if generation_batch_collection is None:
#         # ... (same error handling as before) ...
#         msg = "CRITICAL: MongoDB 'generation_batch_collection' is None. Task cannot proceed."
#         print(msg)
#         self.update_state(state="FAILURE", meta={"error": msg, "details": "DB connection issue in worker."})
#         raise ConnectionError(msg)


#     generation_function_callable = MODEL_DISPATCHER.get(model_name)
#     if not generation_function_callable:
#         # ... (same error handling) ...
#         msg = f"Unsupported model: '{model_name}'"
#         print(msg)
#         # Update batch document file entry
#         generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": msg}, "$push": {"files.$.progress": "Error: " + msg}} )
#         self.update_state(state="FAILURE", meta={"error": msg})
#         raise ValueError(msg)

#     # --- API Key Selection ---
#     key_to_be_used_by_llm = None
#     env_openai_key = os.getenv("OPENAI_API_KEY")
#     env_together_key = os.getenv("TOGETHER_API_KEY")
#     if model_name == "Openai":
#         if not env_openai_key:
#             msg = "CRITICAL FOR OPENAI: Env var OPENAI_API_KEY is NOT SET."
#             print(msg)
#             generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": msg},"$push": {"files.$.progress": "Error: " + msg}} )
#             self.update_state(state="FAILURE", meta={"error": msg})
#             raise ValueError(msg)
#         key_to_be_used_by_llm = env_openai_key
#         print(f"OpenAI: STRICTLY USING key from env OPENAI_API_KEY: '{key_to_be_used_by_llm[:10]}...'")
#     elif model_name in ["Mistral", "Llama"]:
#         key_to_be_used_by_llm = api_key if api_key else env_together_key
#         if not key_to_be_used_by_llm:
#             msg = f"CRITICAL FOR {model_name}: No API key (Postman 'api_key'='{api_key}', TOGETHER_API_KEY env empty)."
#             print(msg)
#             generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": msg},"$push": {"files.$.progress": "Error: " + msg}} )
#             self.update_state(state="FAILURE", meta={"error": msg})
#             raise ValueError(msg)
#         print(f"{model_name}: USING key from {'Postman' if api_key else 'env TOGETHER_API_KEY'}: '{key_to_be_used_by_llm[:10]}...'")
#     else: key_to_be_used_by_llm = api_key # Fallback
#     print("--- END CELERY TASK API KEY DEBUG ---\n")

#     try:
#         # --- Normalize Types & Get Chunks ---
#         if isinstance(test_case_types, str):
#             norm_types = VALID_TEST_CASE_TYPES if test_case_types.lower() == "all" else [t.strip().lower() for t in test_case_types.split(',') if t.strip().lower() in VALID_TEST_CASE_TYPES]
#         elif isinstance(test_case_types, list):
#             norm_types = [t.strip().lower() for t in test_case_types if t.strip().lower() in VALID_TEST_CASE_TYPES]
#         else: raise TypeError(f"Invalid test_case_types: {type(test_case_types)}")
#         if not norm_types: raise ValueError(f"No valid types from: {test_case_types}")

#         chunks_to_process, _ = process_document_and_get_chunks(file_path, model_name, chunk_size_param=chunk_size)
#         if not chunks_to_process:
#             # (Handle no content as in previous full code version, including HACK update to original doc)
#             msg = f"No processable content for file {Path(file_path).name}, model {model_name}. Marking done."
#             print(msg)
#             generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 1, "files.$.error_info": "No processable content", "files.$.test_cases": {}}, "$push": {"files.$.progress": msg}} )
#             try:
#                 generation_batch_collection.update_one( {"_id": ObjectId(file_id)}, {"$set": {"status": 1, "error_info": "No processable content", "test_cases": {}, "last_task_id": self.request.id, "progress": [msg]}} )
#                 print(f"HACK: Original doc {file_id} updated for no content.")
#             except Exception as e: print(f"HACK ERROR (no content) for {file_id}: {e}")
#             self.update_state(state="SUCCESS", meta={"message": msg, "file_id": file_id, "status": "NoContent"})
#             return {"message": msg, "file_id": file_id, "status": "NoContent"}

#         generated_tcs_for_db = {}
#         for tc_type in norm_types:
#             # (Loop through chunks and call test_case_utils.generate_test_cases as before)
#             # (Update batch document files.$.test_cases.{tc_type} as before)
#             self.update_state(state="PROGRESS", meta={"status": f"Processing {tc_type} for {model_name}", "file_id": file_id})
#             prompt_file = Path("utils/prompts") / f"{tc_type}.txt"
#             if not prompt_file.exists():
#                 msg = f"Warning: Prompt file not found: {prompt_file}. Skipping '{tc_type}'."
#                 print(msg)
#                 generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$push": {"files.$.progress": msg}} )
#                 continue
#             with open(prompt_file, "r", encoding="utf-8") as f: prompt_template = f.read()
#             type_content_parts = []
#             for i, chunk_item in enumerate(chunks_to_process, 1):
#                 chunk_prog_msg = f"Generating '{tc_type}' chunk {i}/{len(chunks_to_process)} with {model_name}."
#                 print(chunk_prog_msg)
#                 # self.update_state(state="PROGRESS", meta={"status": chunk_prog_msg, "file_id": file_id}) # Can be noisy
#                 content_chunk, _ = test_case_utils.generate_test_cases(
#                     brd_text=chunk_item, generation_function=generation_function_callable,
#                     test_case_prompt_template=prompt_template, llm_api_key=key_to_be_used_by_llm
#                 )
#                 if "ERROR:" in content_chunk.upper() or "ERROR_GENERATING_TEST_CASES" in content_chunk.upper():
#                     err_msg_llm = f"LLM Error ({model_name}) chunk {i}, type '{tc_type}': {content_chunk}"
#                     print(err_msg_llm)
#                     type_content_parts.append(f"\n--- ERROR CHUNK {i}: {content_chunk} ---\n")
#                     generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$push": {"files.$.progress": f"LLM Error '{tc_type}', chunk {i}."}} )
#                 else:
#                     type_content_parts.append(content_chunk)
#             combined_content = "\n---\n".join(type_content_parts).strip()
#             generated_tcs_for_db[tc_type] = {"content": combined_content}
#             db_type_update_msg = f"Stored '{tc_type}' TCs by {model_name} in batch doc."
#             generation_batch_collection.update_one(
#                 {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
#                 {"$set": {f"files.$.test_cases.{tc_type}": generated_tcs_for_db[tc_type], "files.$.status": 0}, # status 0 as file still processing
#                  "$push": {"files.$.progress": db_type_update_msg}}
#             )
#             print(db_type_update_msg)


#         # --- Finalize File Processing (Batch Document) ---
#         final_msg_batch_file = f"All types processed by {model_name} for this file in batch."
#         generation_batch_collection.update_one(
#             {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
#             {"$set": {"files.$.status": 1, "files.$.test_cases": generated_tcs_for_db, "files.$.model_used_for_file": model_name},
#              "$push": {"files.$.progress": final_msg_batch_file}}
#         )
#         print(final_msg_batch_file)

#         # --- HACK: Update Original Document Record for WebSocket ---
#         print(f"\n--- HACK ATTEMPT: Updating original document record FOR WebSocket ---")
#         print(f"HACK: Original Document ID (str from Celery arg 'file_id'): '{file_id}'")
        
#         original_doc_oid_for_hack = None
#         try:
#             original_doc_oid_for_hack = ObjectId(file_id)
#             print(f"HACK: Converted 'file_id' to ObjectId: {original_doc_oid_for_hack}")
#         except InvalidId:
#             print(f"HACK CRITICAL FAILURE: 'file_id' ('{file_id}') is NOT a valid ObjectId string. Cannot HACK update original doc.")
#         except Exception as e_oid:
#             print(f"HACK CRITICAL FAILURE: Error converting 'file_id' ('{file_id}') to ObjectId: {e_oid}. Cannot HACK update.")

#         if original_doc_oid_for_hack:
#             # Check if the document actually exists before trying to update it
#             # This uses the SAME collection as batch docs, as per current setup.
#             doc_check_count = generation_batch_collection.count_documents({"_id": original_doc_oid_for_hack}, limit=1)
#             print(f"HACK: Pre-update check: Count of documents with _id {original_doc_oid_for_hack} found: {doc_check_count}")

#             if doc_check_count > 0:
#                 hack_update_payload = {
#                     "$set": {
#                         "status": 1, # Mark as success
#                         "test_cases": generated_tcs_for_db, # The full test cases dict
#                         "last_task_id": self.request.id,
#                         "model_used_display": model_name, # Use a different field name to avoid schema confusion
#                         "error_info": None, # Clear any previous error on the original doc
#                         "hack_updated_at": datetime.now(timezone.utc) # Timestamp this hack update
#                     },
#                     # Replace progress entirely or push new ones carefully
#                     "$set": {"progress": [final_msg_batch_file, f"HACK: Updated by Celery task {self.request.id}"]}
#                 }
#                 try:
#                     print(f"HACK: Attempting update for original doc {original_doc_oid_for_hack} with payload (partial): {str(hack_update_payload)[:300]}...")
#                     result_hack_update = generation_batch_collection.update_one(
#                         {"_id": original_doc_oid_for_hack},
#                         hack_update_payload
#                     )
#                     print(f"HACK: MongoDB update_one result for original_doc: matched_count={result_hack_update.matched_count}, modified_count={result_hack_update.modified_count}")
#                     if result_hack_update.matched_count > 0 and result_hack_update.modified_count > 0:
#                         print(f"HACK SUCCESS: Original document {original_doc_oid_for_hack} was updated.")
#                     elif result_hack_update.matched_count > 0:
#                         print(f"HACK WARNING: Original document {original_doc_oid_for_hack} was matched but NOT modified by HACK (data might be same or update op issue).")
#                     else: # matched_count == 0
#                         print(f"HACK CRITICAL FAILURE: Original document {original_doc_oid_for_hack} (from 'file_id') WAS NOT MATCHED by HACK update_one. Does it exist with this _id?")
#                 except Exception as e_hack:
#                     print(f"HACK EXCEPTION during original document update: {e_hack}")
#             else:
#                 print(f"HACK SKIPPED: Original document {original_doc_oid_for_hack} (from 'file_id') does not exist in collection. Cannot apply HACK.")
#         print(f"--- END HACK ATTEMPT ---\n")
#         # --- END HACK ---

#         # --- Check for Overall Batch Completion ---
#         # (This part remains the same, checking the parent batch document)
#         parent_doc_check = generation_batch_collection.find_one({"_id": ObjectId(generation_id)})
#         if parent_doc_check and parent_doc_check.get("files"):
#             if all(f.get("status") == 1 for f in parent_doc_check.get("files", [])):
#                 batch_done_final_msg = "All files in this batch generation process have fully completed."
#                 generation_batch_collection.update_one( {"_id": ObjectId(generation_id)}, {"$set": {"status": 1}, "$push": {"progress": batch_done_final_msg}} )
#                 print(batch_done_final_msg)
        
#         task_final_result_dict = {
#             "message": "File processing completed successfully.", "model_used": model_name,
#             "generation_id_parent_batch": generation_id, "processed_original_file_id": file_id,
#             "processed_batch_internal_file_id": batch_id, "generated_types": list(generated_tcs_for_db.keys())
#         }
#         self.update_state(state="SUCCESS", meta=task_final_result_dict)
#         return task_final_result_dict

#     except Exception as e_main_task_final:
#         # (Overall task error handling remains similar, including HACK update for original doc on error)
#         err_msg_final_task = f"FATAL Celery Task Error (file '{Path(file_path).name}', model '{model_name}'): {type(e_main_task_final).__name__} - {str(e_main_task_final)}"
#         print(err_msg_final_task)
#         # Update batch document file entry
#         if generation_batch_collection:
#             try: generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": err_msg_final_task}, "$push": {"files.$.progress": "Fatal Error: " + str(e_main_task_final)}} )
#             except Exception as db_err1: print(f"Failed to update batch doc on fatal error: {db_err1}")
#             # HACK for original doc on error
#             try:
#                 original_doc_id_obj_err_hack_final = ObjectId(file_id)
#                 if generation_batch_collection.count_documents({"_id": original_doc_id_obj_err_hack_final}, limit=1) > 0:
#                     generation_batch_collection.update_one( {"_id": original_doc_id_obj_err_hack_final}, {"$set": {"status": 2, "error_info": err_msg_final_task, "last_task_id": self.request.id, "progress": ["Fatal Error in batch processing (HACK): " + str(e_main_task_final)]}} )
#                     print(f"HACK: Updated original doc {file_id} with error info on task failure.")
#                 else: print(f"HACK SKIPPED (on error): Original doc {file_id} not found for error update.")
#             except InvalidId: print(f"HACK CRITICAL FAILURE (on error): Invalid ObjectId string for file_id '{file_id}'.")
#             except Exception as e_hack_err_final: print(f"HACK EXCEPTION (on error) for {file_id}: {e_hack_err_final}")
#         self.update_state(state="FAILURE", meta={"error": str(e_main_task_final), "details": err_msg_final_task})
#         raise
# task_with_api_key.py

from typing import Optional, Union, List, Tuple

from celery_worker import celery_app
from utils import data_ingestion, test_case_utils # Ensure test_case_utils.generate_test_cases is robust
from utils.llms import Mistral, openai, llama
from bson import ObjectId
from bson.errors import InvalidId # Correct import for InvalidId
import os
import re
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone # For UTC timestamping

# --- MongoDB Setup ---
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")

generation_batch_collection = None
try:
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[MONGO_DB_NAME]
    generation_batch_collection = db["test_case_generation"]
    print(f"TASK_WORKER: Successfully connected to MongoDB: {MONGODB_URL} - DB: {MONGO_DB_NAME}")
except Exception as e:
    print(f"TASK_WORKER_CRITICAL: Failed to connect to MongoDB: {e}")

# --- Constants and Configuration ---
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

DEFAULT_CHUNK_SIZE = 7000 # Characters. Approx 1750 tokens. Adjust if needed.

MODEL_DISPATCHER = {
    "Mistral": Mistral.generate_with_mistral,
    "Openai": openai.generate_with_openai,
    "Llama": llama.generate_with_llama,
}
VALID_TEST_CASE_TYPES = [
    "functional", "non-functional", "security",
    "performance", "boundary", "compliance",
]

# --- Helper Functions ---
def split_text_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    chunks = []
    current_chunk = ""
    # Replace multiple types of newlines then split by sentence terminators
    sentences = re.split(r'(?<=[.?!])\s+', text.replace('\r\n', ' ').replace('\n', ' ').strip())
    for sentence in sentences:
        if not sentence.strip(): continue
        if len(current_chunk) + len(sentence) + 1 <= chunk_size: # +1 for the space
            current_chunk += sentence + " "
        else:
            if current_chunk.strip(): chunks.append(current_chunk.strip())
            current_chunk = sentence + " " # Start new chunk with current sentence
    if current_chunk.strip(): chunks.append(current_chunk.strip()) # Add the last chunk
    if not chunks and text.strip(): chunks.append(text.strip()) # If no splits but text exists
    return chunks

def process_document_and_get_chunks(
    file_path: str, model_name: str, chunk_size_param: Optional[int]
) -> Tuple[List[str], str]:
    print(f"\n--- DBG_PDAGC: ENTER for: {Path(file_path).name} ---")
    print(f"DBG_PDAGC: model_name='{model_name}', chunk_size_param={chunk_size_param}")
    try:
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
    except Exception as e:
        print(f"DBG_PDAGC: ERROR loading document {file_path}: {e}")
        raise ValueError(f"Failed to load text from document: {file_path}") from e

    if not brd_text or not brd_text.strip():
        print(f"DBG_PDAGC: WARNING - No text extracted from document: {file_path}. Returning empty list/str.")
        return [], ""
    cleaned_full_text = data_ingestion.clean_text(brd_text)
    if not cleaned_full_text.strip():
        print(f"DBG_PDAGC: WARNING - Cleaned text is empty for document: {file_path}. Returning empty list/str.")
        return [], cleaned_full_text

    # --- Consistent Chunking Logic for ALL Models ---
    effective_chunk_size_for_splitting = chunk_size_param if chunk_size_param and chunk_size_param > 0 else DEFAULT_CHUNK_SIZE
    
    print(f"INFO (pdagc): For model '{model_name}', document will be processed using chunk splitting. Effective chunk size: ~{effective_chunk_size_for_splitting} chars.")
    final_chunks = split_text_into_chunks(cleaned_full_text, effective_chunk_size_for_splitting)
    
    if not final_chunks and cleaned_full_text: # Fallback if splitting gives nothing but text exists
        print(f"WARNING (pdagc): Splitting for '{model_name}' resulted in no chunks, using full text as one chunk (fallback).")
        final_chunks = [cleaned_full_text]
    # --- END Consistent Chunking Logic ---
    
    print(f"FINAL DEBUG (pdagc): Document processed into {len(final_chunks)} chunk(s) for model '{model_name}'.")
    print(f"--- DBG_PDAGC: EXIT for: {Path(file_path).name} ---\n")
    return final_chunks, cleaned_full_text

# --- Celery Task ---
@celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task")
def process_and_generate_task(
    self, file_path: str, model_name: str, chunk_size: Optional[int],
    api_key: Optional[str], test_case_types: Union[str, List[str]],
    generation_id: str, file_id: str, batch_id: str ):

    print(f"\n--- CELERY TASK START (task_id: {self.request.id}) ---")
    print(f"Processing file: {Path(file_path).name}, Original Doc ID (file_id): {file_id}")
    print(f"Model: '{model_name}', Batch Gen ID: {generation_id}, DB Batch File ID: {batch_id}")
    api_key_disp = f"'{api_key[:10]}...'" if api_key and len(api_key) > 10 else f"'{api_key}'"
    print(f"Received 'api_key' param from FastAPI: {api_key_disp}")

    if generation_batch_collection is None:
        msg = "CRITICAL: MongoDB 'generation_batch_collection' is None. Task cannot proceed."
        print(msg); self.update_state(state="FAILURE", meta={"error": msg}); raise ConnectionError(msg)

    generation_function_callable = MODEL_DISPATCHER.get(model_name)
    if not generation_function_callable:
        msg = f"Unsupported model: '{model_name}'"
        print(msg)
        generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": msg}, "$push": {"files.$.progress": "Error: " + msg}} )
        self.update_state(state="FAILURE", meta={"error": msg}); raise ValueError(msg)

    key_to_be_used_by_llm = None
    env_openai_key = os.getenv("OPENAI_API_KEY")
    env_together_key = os.getenv("TOGETHER_API_KEY")
    if model_name == "Openai":
        if not env_openai_key:
            msg = "CRITICAL FOR OPENAI: Env var OPENAI_API_KEY is NOT SET."
            print(msg)
            generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": msg},"$push": {"files.$.progress": "Error: " + msg}} )
            self.update_state(state="FAILURE", meta={"error": msg}); raise ValueError(msg)
        key_to_be_used_by_llm = env_openai_key
        print(f"OpenAI: STRICTLY USING key from env OPENAI_API_KEY: '{key_to_be_used_by_llm[:10]}...'")
    elif model_name in ["Mistral", "Llama"]:
        key_to_be_used_by_llm = api_key if api_key else env_together_key
        if not key_to_be_used_by_llm:
            msg = f"CRITICAL FOR {model_name}: No API key (Postman 'api_key'='{api_key}', TOGETHER_API_KEY env empty)."
            print(msg)
            generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": msg},"$push": {"files.$.progress": "Error: " + msg}} )
            self.update_state(state="FAILURE", meta={"error": msg}); raise ValueError(msg)
        print(f"{model_name}: USING key from {'Postman' if api_key else 'env TOGETHER_API_KEY'}: '{key_to_be_used_by_llm[:10]}...'")
    else: key_to_be_used_by_llm = api_key
    print("--- END CELERY TASK API KEY DEBUG ---\n")

    try:
        if isinstance(test_case_types, str):
            norm_types = VALID_TEST_CASE_TYPES if test_case_types.lower() == "all" else [t.strip().lower() for t in test_case_types.split(',') if t.strip().lower() in VALID_TEST_CASE_TYPES]
        elif isinstance(test_case_types, list):
            norm_types = [t.strip().lower() for t in test_case_types if t.strip().lower() in VALID_TEST_CASE_TYPES]
        else: raise TypeError(f"Invalid test_case_types: {type(test_case_types)}")
        if not norm_types: raise ValueError(f"No valid types from: {test_case_types}")

        list_of_chunks_to_process, _ = process_document_and_get_chunks(
            file_path, model_name, chunk_size_param=chunk_size
        )
        
        if not list_of_chunks_to_process:
            msg = f"No processable content for file {Path(file_path).name}, model {model_name}. Marking done."
            print(msg)
            generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 1, "files.$.error_info": "No processable content", "files.$.test_cases": {}}, "$push": {"files.$.progress": msg}} )
            try:
                generation_batch_collection.update_one( {"_id": ObjectId(file_id)}, {"$set": {"status": 1, "error_info": "No processable content", "test_cases": {}, "last_task_id": self.request.id, "progress": [msg]}} )
                print(f"HACK: Original doc {file_id} updated for no content.")
            except Exception as e: print(f"HACK ERROR (no content) for {file_id}: {e}")
            self.update_state(state="SUCCESS", meta={"message": msg, "file_id": file_id, "status": "NoContent"})
            return {"message": msg, "file_id": file_id, "status": "NoContent"}

        generated_tcs_for_db = {}
        for tc_type in norm_types:
            self.update_state(state="PROGRESS", meta={"status": f"Processing {tc_type} for {model_name}", "file_id": file_id})
            prompt_file = Path("utils/prompts") / f"{tc_type}.txt"
            if not prompt_file.exists():
                msg = f"Warning: Prompt file not found: {prompt_file}. Skipping '{tc_type}'."
                print(msg)
                generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$push": {"files.$.progress": msg}} )
                continue
            with open(prompt_file, "r", encoding="utf-8") as f: prompt_template = f.read()
            type_content_parts = []
            for i, chunk_item in enumerate(list_of_chunks_to_process, 1):
                chunk_prog_msg = f"Generating '{tc_type}' chunk {i}/{len(list_of_chunks_to_process)} with {model_name}."
                print(chunk_prog_msg)
                content_chunk, _ = test_case_utils.generate_test_cases(
                    brd_text=chunk_item, generation_function=generation_function_callable,
                    test_case_prompt_template=prompt_template, llm_api_key=key_to_be_used_by_llm
                )
                if "ERROR:" in content_chunk.upper() or "ERROR_GENERATING_TEST_CASES" in content_chunk.upper():
                    err_msg_llm = f"LLM Error ({model_name}) chunk {i}, type '{tc_type}': {content_chunk}"
                    print(err_msg_llm)
                    type_content_parts.append(f"\n--- ERROR CHUNK {i}: {content_chunk} ---\n")
                    generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$push": {"files.$.progress": f"LLM Error '{tc_type}', chunk {i}."}} )
                else:
                    type_content_parts.append(content_chunk)
            combined_content = "\n---\n".join(type_content_parts).strip()
            generated_tcs_for_db[tc_type] = {"content": combined_content}
            db_type_update_msg = f"Stored '{tc_type}' TCs by {model_name} in batch doc."
            generation_batch_collection.update_one(
                {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                {"$set": {f"files.$.test_cases.{tc_type}": generated_tcs_for_db[tc_type], "files.$.status": 0},
                 "$push": {"files.$.progress": db_type_update_msg}}
            )
            print(db_type_update_msg)

        final_msg_batch_file = f"All types processed by {model_name} for this file in batch."
        generation_batch_collection.update_one(
            {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
            {"$set": {"files.$.status": 1, "files.$.test_cases": generated_tcs_for_db, "files.$.model_used_for_file": model_name},
             "$push": {"files.$.progress": final_msg_batch_file}}
        )
        print(final_msg_batch_file)

        print(f"\n--- HACK ATTEMPT: Updating original document record FOR WebSocket ---")
        print(f"HACK: Original Document ID (str from Celery arg 'file_id'): '{file_id}'")
        original_doc_oid_for_hack = None
        try:
            original_doc_oid_for_hack = ObjectId(file_id)
            print(f"HACK: Converted 'file_id' to ObjectId: {original_doc_oid_for_hack}")
        except InvalidId:
            print(f"HACK CRITICAL FAILURE: 'file_id' ('{file_id}') is NOT a valid ObjectId string. Cannot HACK update original doc.")
        except Exception as e_oid:
            print(f"HACK CRITICAL FAILURE: Error converting 'file_id' ('{file_id}') to ObjectId: {e_oid}. Cannot HACK update.")

        if original_doc_oid_for_hack:
            doc_check_count = generation_batch_collection.count_documents({"_id": original_doc_oid_for_hack}, limit=1)
            print(f"HACK: Pre-update check: Count of documents with _id {original_doc_oid_for_hack} found: {doc_check_count}")
            if doc_check_count > 0:
                hack_update_payload = {
                    "$set": {
                        "status": 1, "test_cases": generated_tcs_for_db,
                        "last_task_id": self.request.id, "model_used_original": model_name,
                        "error_info": None, "hack_updated_at": datetime.now(timezone.utc),
                        "progress": [f"Batch processing completed by {model_name} (Task: {self.request.id}).", final_msg_batch_file]
                    }
                }
                try:
                    print(f"HACK: Update payload for original doc {original_doc_oid_for_hack} (partial): {str(hack_update_payload)[:300]}...")
                    result_hack_update = generation_batch_collection.update_one({"_id": original_doc_oid_for_hack}, hack_update_payload)
                    print(f"HACK: MongoDB update_one result for original_doc: matched_count={result_hack_update.matched_count}, modified_count={result_hack_update.modified_count}")
                    if result_hack_update.matched_count > 0 and result_hack_update.modified_count > 0: print(f"HACK SUCCESS: Original document {original_doc_oid_for_hack} was updated.")
                    elif result_hack_update.matched_count > 0: print(f"HACK WARNING: Original document {original_doc_oid_for_hack} matched but NOT MODIFIED by HACK.")
                    else: print(f"HACK CRITICAL FAILURE: Original document {original_doc_oid_for_hack} WAS NOT MATCHED by HACK update_one.")
                except Exception as e_hack: print(f"HACK EXCEPTION during original document update: {e_hack}")
            else: print(f"HACK SKIPPED: Original document {original_doc_oid_for_hack} does not exist. Cannot apply HACK.")
        print(f"--- END HACK ATTEMPT ---\n")

        parent_doc_check = generation_batch_collection.find_one({"_id": ObjectId(generation_id)})
        if parent_doc_check and parent_doc_check.get("files"):
            if all(f.get("status") == 1 for f in parent_doc_check.get("files", [])):
                batch_done_final_msg = "All files in this batch generation process have fully completed."
                generation_batch_collection.update_one( {"_id": ObjectId(generation_id)}, {"$set": {"status": 1}, "$push": {"progress": batch_done_final_msg}} )
                print(batch_done_final_msg)
        
        task_final_result_dict = {
            "message": "File processing completed successfully.", "model_used": model_name,
            "generation_id_parent_batch": generation_id, "processed_original_file_id": file_id,
            "processed_batch_internal_file_id": batch_id, "generated_types": list(generated_tcs_for_db.keys())
        }
        self.update_state(state="SUCCESS", meta=task_final_result_dict)
        return task_final_result_dict

    except Exception as e_main_task_final:
        err_msg_final_task = f"FATAL Celery Task Error (file '{Path(file_path).name}', model '{model_name}'): {type(e_main_task_final).__name__} - {str(e_main_task_final)}"
        print(err_msg_final_task)
        if generation_batch_collection:
            try: generation_batch_collection.update_one( {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)}, {"$set": {"files.$.status": 2, "files.$.error_info": err_msg_final_task}, "$push": {"files.$.progress": "Fatal Error: " + str(e_main_task_final)}} )
            except Exception as db_err1: print(f"Failed to update batch doc on fatal error: {db_err1}")
            try:
                original_doc_id_obj_err_hack_final = ObjectId(file_id)
                if generation_batch_collection.count_documents({"_id": original_doc_id_obj_err_hack_final}, limit=1) > 0:
                    generation_batch_collection.update_one( {"_id": original_doc_id_obj_err_hack_final}, {"$set": {"status": 2, "error_info": err_msg_final_task, "last_task_id": self.request.id, "progress": ["Fatal Error in batch processing (HACK): " + str(e_main_task_final)]}} )
                    print(f"HACK: Updated original doc {file_id} with error info on task failure.")
                else: print(f"HACK SKIPPED (on error): Original doc {file_id} not found for error update.")
            except InvalidId: print(f"HACK CRITICAL FAILURE (on error): Invalid ObjectId string for file_id '{file_id}'.")
            except Exception as e_hack_err_final: print(f"HACK EXCEPTION (on error) for {file_id}: {e_hack_err_final}")
        self.update_state(state="FAILURE", meta={"error": str(e_main_task_final), "details": err_msg_final_task})
        raise
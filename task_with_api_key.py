# task_with_api_key.py
 
from typing import Optional, Union, List, Tuple # Ensure all necessary types are imported
 
from celery_worker import celery_app
from utils import data_ingestion, test_case_utils
from utils.llms import Mistral, openai, llama # Ensure these modules and functions exist
from bson import ObjectId
import os
import re
from pathlib import Path
from pymongo import MongoClient
 
# --- MongoDB Setup ---
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Gen_AI")
 
generation_batch_collection = None # Initialize
try:
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[MONGO_DB_NAME]
    generation_batch_collection = db["test_case_generation"]
    print(f"Successfully connected to MongoDB: {MONGODB_URL} - DB: {MONGO_DB_NAME} in task_with_api_key.py")
except Exception as e:
    print(f"CRITICAL: Failed to connect to MongoDB in task_with_api_key.py: {e}")
    # Celery tasks will fail if this is None, which is intended.
 
# --- Constants and Configuration ---
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
 
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
 
DEFAULT_CHUNK_SIZE = 7000
 
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
    sentences = re.split(r'(?<=[.?!])\s+', text.replace('\n', ' ').strip())
   
    for sentence in sentences:
        if not sentence.strip():
            continue
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
           
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
       
    if not chunks and text.strip():
        chunks.append(text.strip())
       
    return chunks
 
def process_document(file_path: str, model_name: str, chunk_size: Optional[int]) -> Tuple[List[str], str]:
    try:
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
    except Exception as e:
        print(f"Error loading document {file_path}: {e}")
        raise ValueError(f"Failed to load or extract text from document: {file_path}") from e
 
    if not brd_text or not brd_text.strip():
        raise ValueError(f"No text extracted from document: {file_path}")
 
    cleaned_text = data_ingestion.clean_text(brd_text)
    effective_chunk_size = chunk_size if chunk_size and chunk_size > 0 else DEFAULT_CHUNK_SIZE
 
    if model_name == "Mistral": # Mistral often handles larger contexts better
        chunks = [cleaned_text]
    else: # For OpenAI, Llama, or if specific chunking is always desired
        chunks = split_text_into_chunks(cleaned_text, effective_chunk_size)
 
    if not chunks and cleaned_text: # Fallback
        chunks = [cleaned_text]
       
    return chunks, cleaned_text
 
# --- Celery Task ---
@celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task")
def process_and_generate_task(
    self,
    file_path: str,
    model_name: str,
    chunk_size: Optional[int],
    api_key: Optional[str], # Key from Postman/FastAPI form
    test_case_types: Union[str, List[str]],
    generation_id: str,
    file_id: str,
    batch_id: str
):
    # --- Celery Task Start & Debug ---
    print("\n--- CELERY TASK DEBUG INFO (task_with_api_key.py) ---")
    print(f"Task ID: {self.request.id}")
    print(f"File Path: {file_path}")
    print(f"Received model_name: '{model_name}'")
    print(f"Received 'api_key' param from FastAPI: '{api_key[:10] + '...' if api_key and len(api_key) > 10 else api_key}'")
    print(f"Generation (Batch) ID: {generation_id}, Original File ID: {file_id}, DB Batch File ID: {batch_id}")
 
    if generation_batch_collection is None:
        msg = "CRITICAL: MongoDB collection 'generation_batch_collection' is None. Task cannot proceed."
        print(msg)
        self.update_state(state="FAILURE", meta={"error": msg})
        raise ConnectionError(msg)
 
    generation_function_callable = MODEL_DISPATCHER.get(model_name)
    if not generation_function_callable:
        msg = f"Unsupported model_name: '{model_name}'. Available: {list(MODEL_DISPATCHER.keys())}"
        print(msg)
        generation_batch_collection.update_one(
            {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
            {"$set": {"files.$.status": 2, "files.$.error_info": msg}, "$push": {"files.$.progress": "Error: " + msg}}
        )
        self.update_state(state="FAILURE", meta={"error": msg})
        raise ValueError(msg)
 
    # --- Rigorous API Key Selection Logic ---
    key_to_be_used_by_llm = None
    env_openai_key_str = os.getenv("OPENAI_API_KEY")
    env_together_key_str = os.getenv("TOGETHER_API_KEY")
 
    if model_name == "Openai":
        if not env_openai_key_str:
            msg = "CRITICAL FOR OPENAI: OPENAI_API_KEY environment variable is NOT SET for Celery worker."
            print(msg)
            generation_batch_collection.update_one(
                {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                {"$set": {"files.$.status": 2, "files.$.error_info": msg},"$push": {"files.$.progress": "Error: " + msg}}
            )
            self.update_state(state="FAILURE", meta={"error": msg})
            raise ValueError(msg)
        key_to_be_used_by_llm = env_openai_key_str
        print(f"For OpenAI: STRICTLY USING key from env OPENAI_API_KEY: '{key_to_be_used_by_llm[:10]}...'")
    elif model_name in ["Mistral", "Llama"]: # Assuming these use TogetherAI
        key_to_be_used_by_llm = api_key if api_key else env_together_key_str # Prioritize Postman key
        if not key_to_be_used_by_llm:
            msg = f"CRITICAL FOR {model_name}: No API key. Postman 'api_key' ('{api_key}') was empty/None AND TOGETHER_API_KEY env var is not set."
            print(msg)
            generation_batch_collection.update_one(
                {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                {"$set": {"files.$.status": 2, "files.$.error_info": msg},"$push": {"files.$.progress": "Error: " + msg}}
            )
            self.update_state(state="FAILURE", meta={"error": msg})
            raise ValueError(msg)
        source_msg = f"{'(Postman param)' if api_key else '(env TOGETHER_API_KEY)'}"
        print(f"For {model_name}: USING key: '{key_to_be_used_by_llm[:10]}...' from {source_msg}")
    else:
        key_to_be_used_by_llm = api_key # Fallback for undefined models
        print(f"For UNKNOWN model '{model_name}': Passing 'api_key' param from FastAPI: '{key_to_be_used_by_llm[:10] + '...' if key_to_be_used_by_llm and len(key_to_be_used_by_llm) > 10 else key_to_be_used_by_llm}'")
    print("--- END CELERY TASK DEBUG INFO (task_with_api_key.py) ---\n")
 
    try:
        # --- Normalize Test Case Types ---
        if isinstance(test_case_types, str):
            normalized_types = VALID_TEST_CASE_TYPES if test_case_types.lower() == "all" else \
                               [t.strip().lower() for t in test_case_types.split(',') if t.strip().lower() in VALID_TEST_CASE_TYPES]
        elif isinstance(test_case_types, list):
            normalized_types = [t.strip().lower() for t in test_case_types if t.strip().lower() in VALID_TEST_CASE_TYPES]
        else:
            raise TypeError(f"Invalid test_case_types format: {type(test_case_types)}")
        if not normalized_types:
            raise ValueError(f"No valid test_case_types resolved from input: {test_case_types}")
 
        # --- Process Document and Generate Test Cases ---
        chunks, _ = process_document(file_path, model_name, chunk_size)
        generated_test_cases_for_db_update = {}
 
        for tc_type in normalized_types:
            self.update_state(state="PROGRESS", meta={"status": f"Processing {tc_type} for {model_name}", "file_id": file_id})
            prompt_file = Path("utils/prompts") / f"{tc_type}.txt"
            if not prompt_file.exists():
                msg = f"Warning: Prompt file not found for type '{tc_type}': {prompt_file}. Skipping."
                print(msg)
                generation_batch_collection.update_one(
                    {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                    {"$push": {"files.$.progress": msg}}
                )
                continue
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt_template_str = f.read()
 
            type_specific_content_list = []
            for i, text_chunk_item in enumerate(chunks, 1):
                chunk_prog_msg = f"Generating '{tc_type}' from chunk {i}/{len(chunks)} with {model_name}."
                print(chunk_prog_msg)
                self.update_state(state="PROGRESS", meta={"status": chunk_prog_msg, "file_id": file_id})
               
                content_for_chunk, _ = test_case_utils.generate_test_cases(
                    brd_text=text_chunk_item,
                    generation_function=generation_function_callable,
                    test_case_prompt_template=prompt_template_str,
                    llm_api_key=key_to_be_used_by_llm
                )
               
                if "ERROR_GENERATING_TEST_CASES" in content_for_chunk or "ERROR:" in content_for_chunk:
                    err_llm_msg = f"Error from LLM for chunk {i}, type '{tc_type}': {content_for_chunk}"
                    print(err_llm_msg)
                    type_specific_content_list.append(f"\n--- ERROR generating for chunk {i}: {content_for_chunk} ---\n")
                    generation_batch_collection.update_one(
                        {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                        {"$push": {"files.$.progress": f"LLM Error for '{tc_type}', chunk {i}."}}
                    )
                else:
                    type_specific_content_list.append(content_for_chunk)
 
            combined_content_str = "\n---\n".join(type_specific_content_list).strip()
            generated_test_cases_for_db_update[tc_type] = {"content": combined_content_str}
           
            db_type_update_msg = f"Stored '{tc_type}' test cases from {model_name}."
            generation_batch_collection.update_one(
                {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                {"$set": {f"files.$.test_cases.{tc_type}": generated_test_cases_for_db_update[tc_type], "files.$.status": 0},
                 "$push": {"files.$.progress": db_type_update_msg}}
            )
            print(db_type_update_msg)
 
        # --- Finalize File Processing ---
        final_msg_file = f"All requested test cases generated for this file by {model_name}."
        generation_batch_collection.update_one(
            {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
            {"$set": {"files.$.status": 1, "files.$.test_cases": generated_test_cases_for_db_update, "files.$.model_used_for_file": model_name},
             "$push": {"files.$.progress": final_msg_file}}
        )
        print(final_msg_file)
 
        # --- Check for Overall Batch Completion ---
        parent_doc = generation_batch_collection.find_one({"_id": ObjectId(generation_id)})
        if parent_doc and parent_doc.get("files"):
            if all(f.get("status") == 1 for f in parent_doc.get("files", [])):
                batch_done_msg = "All files in batch processed successfully."
                generation_batch_collection.update_one(
                    {"_id": ObjectId(generation_id)},
                    {"$set": {"status": 1}, "$push": {"progress": batch_done_msg}}
                )
                print(batch_done_msg)
       
        task_final_result = {
            "message": "File processing completed.", "model_used": model_name,
            "generation_id": generation_id, "file_id": file_id, "batch_id": batch_id,
            "generated_types": list(generated_test_cases_for_db_update.keys())
        }
        self.update_state(state="SUCCESS", meta=task_final_result)
        return task_final_result
 
    except Exception as e_main_task:
        err_msg_task = f"FATAL ERROR in Celery task for file_id '{file_id}', model '{model_name}': {type(e_main_task).__name__} - {str(e_main_task)}"
        print(err_msg_task)
        if generation_batch_collection:
            generation_batch_collection.update_one(
                {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},
                {"$set": {"files.$.status": 2, "files.$.error_info": err_msg_task}, "$push": {"files.$.progress": "Fatal Error: " + str(e_main_task)}}
            )
        self.update_state(state="FAILURE", meta={"error": str(e_main_task), "details": err_msg_task})
        raise
 
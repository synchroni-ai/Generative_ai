# task_with_api_key.py

import os
import re
import time
import uuid # Not directly used here, but common in task modules
from pathlib import Path
from typing import List, Optional, Dict, Any

from bson import ObjectId
# Import celery_app from your central Celery setup file (e.g., celery_worker.py)
from celery_worker import celery_app # <--- MAKE SURE THIS IMPORT WORKS
from fastapi import HTTPException
from pymongo import MongoClient
from utils.llms.Mistral import Mistral as MistralLLMClass


# Assuming these utils are correctly structured and importable by the Celery worker
# Ensure 'utils' directory is in Python's path or structured correctly relative to celery_worker.py
from utils import data_ingestion, test_case_utils
from utils.llms import  openai, llama

# --- MongoDB Connection and other global setups ---
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGODB_URL)
db = mongo_client[os.getenv("MONGODB_DATABASE", "Gen_AI")]
document_collection = db["test_case_generation"]
# cost_collection = db["cost_tracking"] # Uncomment if used

# --- Constants and Configuration ---
INPUT_DIR_ENV = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR_ENV = os.getenv("OUTPUT_DIR", "output_files")

Path(INPUT_DIR_ENV).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR_ENV).mkdir(parents=True, exist_ok=True)

DEFAULT_CHUNK_SIZE = 7000
MODEL_DISPATCHER = {
    "Mistral": MistralLLMClass.generate_with_mistral,
    "Openai": openai.generate_with_openai,
    "Llama": llama.generate_with_llama,
}

# --- Helper Functions ---
def split_text_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    chunks = []
    current_chunk = ""
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def process_document(file_path_str: str, model_name: str, chunk_size_val: Optional[int]) -> tuple[List[str], str]:
    actual_file_path = Path(file_path_str)

    brd_text, _ = data_ingestion.load_pdf_text(str(actual_file_path))
    if not brd_text:
        raise ValueError(f"Failed to extract text from PDF: {actual_file_path}")

    cleaned_text = data_ingestion.clean_text(brd_text)
    effective_chunk_size = chunk_size_val if chunk_size_val is not None else DEFAULT_CHUNK_SIZE

    if model_name == "Mistral":
        chunks = [cleaned_text]
    else:
        chunks = split_text_into_chunks(cleaned_text, effective_chunk_size)
        if not chunks:
            chunks = [cleaned_text]
    return chunks, cleaned_text


# --- Celery Task Definition ---
# The 'name' attribute explicitly sets the task name.
# This name MUST match what the producer (FastAPI) is sending.
@celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task", max_retries=2, default_retry_delay=60)
def process_and_generate_task(  # The Python function name doesn't have to match the Celery task name
    self,
    file_id_str: str,
    file_path_str: str,
    model_name_str: str,
    chunk_size_val: Optional[int],
    api_key_str: str,
    test_case_types_list: List[str],
    username_str: Optional[str] = None
):
    """
    Celery task to process a document and generate test cases.
    Updates the MongoDB document associated with file_id_str.
    """
    task_id = self.request.id
    print(
        f"🎯 Celery task {task_id} (name: {self.name}) started for file_id: {file_id_str}, path: {file_path_str}, "
        f"model: {model_name_str}, types: {test_case_types_list}, user: {username_str}"
    )
    self.update_state(state='STARTED', meta={'file_id': file_id_str, 'message': 'Processing started by Celery worker.'})

    doc_object_id = ObjectId(file_id_str)

    try:
        # --- 1. Input Validation and Setup ---
        if model_name_str not in MODEL_DISPATCHER:
            error_detail = f"Unsupported model: {model_name_str}"
            document_collection.update_one(
                {"_id": doc_object_id},
                {"$set": {"status": "failed", "error": error_detail, "updated_at": time.time()}}
            )
            raise ValueError(error_detail) # Will be caught by the generic exception handler

        generation_function_for_llm = MODEL_DISPATCHER[model_name_str]
        
        if not Path(file_path_str).exists():
            error_detail = f"File not found at path: {file_path_str}"
            document_collection.update_one(
                {"_id": doc_object_id},
                {"$set": {"status": "failed", "error": error_detail, "updated_at": time.time()}}
            )
            raise FileNotFoundError(error_detail)

        chunks, _ = process_document(file_path_str, model_name_str, chunk_size_val)

        base_stem = Path(file_path_str).stem
        all_results_for_response: List[Dict[str, Any]] = []
        all_combined_test_cases_text: str = ""
        generated_file_paths: Dict[str, List[str]] = {"text": [], "csv": []}

        # --- 2. Test Case Generation Loop ---
        total_types = len(test_case_types_list)
        for i, test_case_type in enumerate(test_case_types_list):
            current_step_message = f"Generating for type: {test_case_type} ({i+1}/{total_types})"
            print(f"Task {task_id}: {current_step_message}")
            self.update_state(
                state='PROGRESS',
                meta={
                    'current_step': current_step_message,
                    'processed_types': i + 1,
                    'total_types': total_types
                }
            )
            
            prompt_file_name = f"{test_case_type}.txt"
            # Robust prompt path finding:
            # Assumes 'utils/prompts' is a subdirectory of the parent of this file's directory
            # e.g., if this file is project_root/tasks/task_with_api_key.py, it looks for project_root/utils/prompts
            current_file_dir = Path(__file__).resolve().parent
            prompt_path = current_file_dir.parent / "utils" / "prompts" / prompt_file_name
            
            if not prompt_path.exists(): # Fallback for simpler structures or if worker CWD is project root
                prompt_path_alt = Path.cwd() / "utils" / "prompts" / prompt_file_name
                if not prompt_path_alt.exists():
                    error_detail = f"Prompt file not found: {prompt_file_name} (tried {prompt_path} and {prompt_path_alt})"
                    document_collection.update_one(
                        {"_id": doc_object_id},
                        {"$set": {"status": "failed", "error": error_detail, "updated_at": time.time()}}
                    )
                    raise FileNotFoundError(error_detail)
                else:
                    prompt_path = prompt_path_alt

            with open(prompt_path, "r", encoding="utf-8") as f:
                test_case_prompt_template = f.read()

            current_type_test_cases_list: List[str] = []

            for idx_chunk, chunk_text in enumerate(chunks, start=1):
                print(f"Task {task_id}: Processing chunk {idx_chunk}/{len(chunks)} for type {test_case_type}")
                try:
                    test_case_output, _ = test_case_utils.generate_test_cases(
                        chunk_text=chunk_text,
                        generation_function=generation_function_for_llm,
                        test_case_prompt=test_case_prompt_template,
                        # api_key=api_key_str # Pass API key if generate_test_cases needs it directly for LLM call
                    )
                    if test_case_output:
                        current_type_test_cases_list.append(test_case_output)
                except Exception as e_chunk:
                    print(
                        f"Task {task_id}: Error generating test cases for chunk {idx_chunk} (type: {test_case_type}, file_id: {file_id_str}): {e_chunk}"
                    )
                    continue

            combined_for_current_type = "\n\n".join(current_type_test_cases_list)
            all_combined_test_cases_text += f"\n\n### {test_case_type.upper()} TEST CASES ###\n\n{combined_for_current_type}"

            # --- 3. Save Individual Type Outputs ---
            output_txt_path = Path(OUTPUT_DIR_ENV) / f"{base_stem}_{test_case_type}_{file_id_str}.txt"
            test_case_utils.store_test_cases_to_text_file(combined_for_current_type, str(output_txt_path))
            generated_file_paths["text"].append(str(output_txt_path))

            output_csv_path = Path(OUTPUT_DIR_ENV) / f"{base_stem}_{test_case_type}_{file_id_str}.csv"
            try:
                if model_name_str == "Mistral":
                    test_case_utils.txt_to_csv_mistral(str(output_txt_path), str(output_csv_path))
                else:
                    test_case_utils.txt_to_csv_llama(str(output_txt_path), str(output_csv_path))
                generated_file_paths["csv"].append(str(output_csv_path))
            except Exception as e_csv:
                print(f"Task {task_id}: Error converting {test_case_type} to CSV for {file_id_str}: {e_csv}")

            all_results_for_response.append({
                "test_case_type": test_case_type,
                "generated_text": combined_for_current_type,
                "text_file_path": str(output_txt_path),
                "csv_file_path": str(output_csv_path) if output_csv_path.exists() else None
            })
        
        # --- 4. Finalize and Update Main Document ---
        print(f"Task {task_id}: Finalizing and updating database for file_id: {file_id_str}")
        final_update_data = {
            "status": "completed",
            "selected_model": model_name_str,
            "api_key_used_info": (
                f"...{api_key_str[-5:]}" if api_key_str and len(api_key_str) >= 5 else "Default/Short API Key"
            ),
            "all_test_cases_text": all_combined_test_cases_text.strip(),
            "generated_outputs_by_type": all_results_for_response,
            "generated_files": generated_file_paths,
            "username": username_str,
            "error": None,
            "completed_at": time.time(),
            "updated_at": time.time(),
            "celery_task_id": task_id
        }
        document_collection.update_one({"_id": doc_object_id}, {"$set": final_update_data})
        
        self.update_state(state='SUCCESS', meta={'message': 'Processing completed successfully.', "final_data_summary": final_update_data})
        
        print(f"Task {task_id}: Processing completed successfully for file_id: {file_id_str}")
        return {
            "message": "Test case generation completed successfully.",
            "file_id": file_id_str,
            "celery_task_id": task_id,
            "model_used": model_name_str,
            "results_summary": all_results_for_response
        }

    except Exception as e_task:
        import traceback # Moved import here as it's only used in except block
        error_message = f"Task {self.request.id} failed for file_id {file_id_str}: {type(e_task).__name__} - {str(e_task)}"
        print(error_message)
        traceback.print_exc()

        try:
            document_collection.update_one(
                {"_id": doc_object_id},
                {"$set": {"status": "failed", "error": error_message, "celery_task_id": self.request.id, "updated_at": time.time()}}
            )
        except Exception as db_error:
            print(f"Task {self.request.id}: CRITICAL - Failed to update DB with error status: {db_error}")
        
        raise self.retry(exc=e_task, countdown=int(self.request.retries * 60 + 60))
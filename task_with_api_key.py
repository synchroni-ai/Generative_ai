from celery_worker import celery_app
from utils import data_ingestion, test_case_utils
from utils.llms import Mistral, openai, llama
from fastapi import HTTPException
from bson import ObjectId
import uuid
import os
import re
from pathlib import Path
from pymongo import MongoClient
import pandas as pd
 
mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]
cost_collection = db["cost_tracking"]
 
COST_PER_1M_TOKENS = {"Llama": 0.20, "Mistral": 0.80}
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
 
DEFAULT_CHUNK_SIZE = 7000
MODEL_DISPATCHER = {
    "Mistral": Mistral.generate_with_mistral,
    "Openai": openai.generate_with_openai,
    "Llama": llama.generate_with_llama,
}
 
VALID_TEST_CASE_TYPES = [
    "functional",
    "non-functional",
    "security",
    "performance",
    "boundary",
    "compliance",
]
 
 
def split_text_into_chunks(text, chunk_size=7000):
    chunks = []
    current_chunk = ""
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
 
 
def process_document(file_path, model_name, chunk_size):
    brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
    if not brd_text:
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")
 
    cleaned_text = data_ingestion.clean_text(brd_text)
    chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE
 
    if model_name == "Mistral":
        chunks = [cleaned_text]
    else:
        chunks = split_text_into_chunks(cleaned_text, chunk)
        if not chunks:
            chunks = [cleaned_text]
    return chunks, cleaned_text
 
 
@celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task")

def process_and_generate_task(

    self, file_path, model_name, chunk_size, api_key, test_case_types, generation_id, file_id, batch_id

):

    print(f"🎯 Celery task started: {file_path} ({test_case_types})")

    task_id = self.request.id
 
    try:

        if model_name not in MODEL_DISPATCHER:

            raise Exception(f"Unsupported model: {model_name}")
 
        # Normalize test_case_types

        if isinstance(test_case_types, str):

            if test_case_types.lower() == "all":

                test_case_types = VALID_TEST_CASE_TYPES

            else:

                test_case_types = [

                    t.strip().lower() for t in test_case_types.split(",")

                    if t.strip().lower() in VALID_TEST_CASE_TYPES

                ]

        elif isinstance(test_case_types, list):

            test_case_types = [

                t.strip().lower() for t in test_case_types

                if t.strip().lower() in VALID_TEST_CASE_TYPES

            ]

        else:

            raise Exception("test_case_types must be a list, comma-separated string, or the string 'all'")
 
        if not test_case_types:

            raise Exception(f"No valid test case types provided. Valid types are: {VALID_TEST_CASE_TYPES}")
 
        generation_function = MODEL_DISPATCHER[model_name]

        chunks, cleaned_text = process_document(file_path, model_name, chunk_size)
 
        all_results = []

        all_combined_test_cases = ""

        test_cases_by_type = {}
 
        for test_case_type in test_case_types:

            prompt_path = Path("utils/prompts") / f"{test_case_type}.txt"

            if not prompt_path.exists():

                raise Exception(f"Prompt file not found: {prompt_path}")
 
            with open(prompt_path, "r") as f:

                test_case_prompt = f.read()
 
            all_test_cases = []

            test_case_tokens = 0
 
            for idx, chunk_text in enumerate(chunks, start=1):

                try:

                    test_case_text, tokens = test_case_utils.generate_test_cases(

                        chunk_text,

                        generation_function,

                        test_case_prompt=test_case_prompt,

                    )

                    if test_case_text:

                        all_test_cases.append(test_case_text)

                        test_case_tokens += tokens

                except Exception as e:

                    print(f"Error generating test cases for chunk {idx} ({test_case_type}): {e}")

                    continue
 
            combined_test_cases = "\n".join(all_test_cases)

            all_combined_test_cases += f"\n\n### {test_case_type.upper()} TEST CASES ###\n\n{combined_test_cases}"

            embedded_id = str(uuid.uuid4())

            test_cases_by_type[test_case_type] = {

                "_id": embedded_id,

                "content": combined_test_cases,

            }

            all_results.append({

                "test_case_type": test_case_type,

                "test_cases": combined_test_cases

            })
 
            progress_message = f"{test_case_type} test cases generated"

            try:

                # ⬇️ Update the correct embedded file doc in 'files' array!

                collection.update_one(

                    {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},

                    {

                        "$set": {

                            "files.$.test_cases": test_cases_by_type,

                            "files.$.status": 0

                        },

                        "$push": {

                            "files.$.progress": progress_message

                        }

                    }

                )

            except Exception as e:

                print(f"MongoDB update error (progress after {test_case_type}): {str(e)}")
 
            self.update_state(

                state="PROGRESS",

                meta={"status": "processing", "progress": progress_message}

            )
 
        # Final success update for file

        collection.update_one(

            {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},

            {"$set": {

                "files.$.status": 1,

                "files.$.progress": ["All test cases generated"]

            }}

        )

        # 👇 PATCH: After setting file status, check if all are done

        parent_doc = collection.find_one({"_id": ObjectId(generation_id)})

        if parent_doc and all(f.get("status") == 1 for f in parent_doc.get("files", [])):

            collection.update_one(

                {"_id": ObjectId(generation_id)},

                {

                    "$set": {"status": 1},

                    "$push": {"progress": "All test case batches complete."}

                }

            )
 
        final_result = {

            "message": "All test cases generated and stored successfully.",

            "model_used": model_name,

            "results": all_results,

            "document_id": generation_id,

            "batch_id": batch_id

        }
 
        self.update_state(state="SUCCESS", meta=final_result)

        return final_result
 
    except Exception as e:

        # Error handling inside the batch

        collection.update_one(

            {"_id": ObjectId(generation_id), "files.batch_id": ObjectId(batch_id)},

            {"$set": {

                "files.$.status": 2,

                "files.$.error_info": str(e),

                "files.$.progress": ["Error: " + str(e)]

            }}

        )

        self.update_state(state="FAILURE", meta={"error": str(e)})

        raise self.retry(exc=e)

 
from app.core.celery_app import celery_app
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
# from app.core.celery_app import celery_app


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




def process_document(file_path, model_name, chunk_size):
    brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
    if not brd_text:
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

    cleaned_text = data_ingestion.clean_text(brd_text)
    chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE

    if model_name == "Mistral":
        chunks = [cleaned_text]
    else:
        chunks = data_ingestion.split_text_into_chunks(cleaned_text, chunk)
        if not chunks:
            chunks = [cleaned_text]
    return chunks, cleaned_text


@celery_app.task(bind=True, name="task_with_api_key.process_and_generate_task_multiple")
def process_and_generate_task_multiple(
    self,
    file_ids: list[dict],  # Changed type to List[dict]
    model_name,
    chunk_size,
    api_key,
    test_case_types: list[str],
    document_id,
):  # document_id now represents the multiple document processing session
    """Processes test case generation for multiple files, one file at a time."""
    print(
        f"🎯 Celery task started for multiple documents (one by one): {file_ids} ({test_case_types})"
    )
    task_id = self.request.id  # Get the Celery task ID

    all_documents_results = []

    try:
        # Initialize progress array in MongoDB (empty list) and status = 0 (processing)
        try:
            collection.update_one(
                {"_id": ObjectId(document_id)},
                {
                    "$set": {
                        "status": 0,
                        "progress": [],  # Cleared here at the beginning
                        "total_documents": len(file_ids),  # total # files
                        "processed_documents": 0, # number of files processed so far
                    }
                },
            )
        except Exception as e:
            print("MongoDB update error (init - multiple docs):", str(e))

        processed_count = 0 # Track progress
        for file_data in file_ids: # Iterate through documents
            file_path = file_data['file_path'] # use file_path from dictionary now
            file_id = file_data['file_id']
            print(f"Processing file: {file_path}")

            try:

                generation_function = MODEL_DISPATCHER[model_name]
                chunks, cleaned_text = process_document(
                    file_path, model_name, chunk_size
                )

                all_results = [] # stores results of different test cases for this file
                test_cases_by_type = {}


                for test_case_type in test_case_types:  # Loop inside for all test cases
                    prompt_dir = Path("utils/prompts")
                    prompt_path = prompt_dir / f"{test_case_type}.txt"

                    if not prompt_path.exists():
                        raise HTTPException(
                            status_code=500,
                            detail=f"Prompt file not found: {prompt_path}",
                        )

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
                            print(
                                f"Error generating test cases for chunk {idx} ({test_case_type}): {e}"
                            )
                            continue

                    combined_test_cases = "\n".join(all_test_cases)

                    # Append to dictionary
                    embedded_id = str(uuid.uuid4())
                    test_cases_by_type[test_case_type] = {
                        "_id": embedded_id,
                        "content": combined_test_cases,
                    }

                    all_results.append(
                        {
                            "test_case_type": test_case_type,
                            "test_cases": combined_test_cases,
                        }
                    ) # End  inner loop through test cases



                document_result = {
                    "file_id": file_id,
                    "file_name": Path(file_path).name,  # Add file name
                    "results": all_results,
                }  # Store the results for the specific file

                all_documents_results.append(document_result) # Results for all files
                processed_count += 1
                progress_message = f"✅ Processed file: {Path(file_path).name}  ({processed_count} / {len(file_ids)})"


            except Exception as e:
                progress_message = f"❌ Error processing file: {Path(file_path).name}: {e}"
                print(progress_message)
                document_result = { # To store the error
                    "file_id": file_id,
                    "file_name": Path(file_path).name, # Add file name
                    "error": str(e)
                }
                all_documents_results.append(document_result)
                processed_count += 1 # inc even if there is error

            # Update progress after each file
            try:
                collection.update_one(
                    {"_id": ObjectId(document_id)},
                    {
                        "$set": {
                            "status": 0, # Still Processing
                            "results": all_documents_results,
                            "processed_documents": processed_count,  # Track processed count,
                        },

                    },
                )
                collection.update_one(
                     {"_id": ObjectId(document_id)},
                      {"$push": {"progress": progress_message}},
                )
            except Exception as e:
                print(
                    f"MongoDB update error (progress after document {Path(file_path).name}): {str(e)}"
                )

            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "processing",
                    "progress": progress_message,
                    "processed_documents": processed_count,
                    "total_documents": len(file_ids),
                },
            ) # End of file processing loop

        # Final update: status=1 done, update progress with completion message
        try:
            collection.update_one(
                {"_id": ObjectId(document_id)},
                {
                    "$set": {
                        "status": 1,
                        "progress": ["✅ All documents processed"],
                        "results": all_documents_results,
                        "processed_documents": len(file_ids),
                        "total_documents": len(file_ids),
                    }
                },
            )
        except Exception as e:
            print("MongoDB update error (final - multiple docs):", str(e))

        final_result = {
            "message": "✅ All documents processed and results stored successfully.",
            "model_used": model_name,
            "results": all_documents_results,
            "document_id": document_id,
            "total_documents": len(file_ids),
            "processed_documents": len(file_ids),
        }

        self.update_state(state="SUCCESS", meta=final_result)  # Send final result

        return final_result

    except Exception as e:
        self.update_state(
            state="FAILURE", meta={"error": str(e)}
        )  # send failure through websocket
        raise self.retry(exc=e)
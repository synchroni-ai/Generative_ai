from celery_worker import celery_app
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
from fastapi import HTTPException
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
# EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
# Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

DEFAULT_CHUNK_SIZE = 7000
MODEL_DISPATCHER = {
    "Mistral": Mistral.generate_with_mistral,
    "Openai": openai.generate_with_openai,
    "Llama": llama.generate_with_llama,
}


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


def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def process_document(
    file_path, model_name, chunk_size
):  # Added process_document as a general function
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
    self, file_path, model_name, chunk_size, api_key, test_case_type
):
    print(f"🎯 Celery task started: {file_path} ({test_case_type})")

    try:
        if model_name not in MODEL_DISPATCHER:
            raise HTTPException(
                status_code=400, detail=f"Unsupported model: {model_name}"
            )

        generation_function = MODEL_DISPATCHER[model_name]

        # Load Test Case Prompt
        prompt_dir = Path("utils/prompts")
        prompt_file = f"{test_case_type}.txt"
        prompt_path = prompt_dir / prompt_file

        if not prompt_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Prompt file not found: {prompt_path}",
            )

        with open(prompt_path, "r") as f:
            test_case_prompt = f.read()

        chunks, cleaned_text = process_document(
            file_path, model_name, chunk_size
        )  # Call the process_document function

        # Generate Test Cases
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

        # Save Outputs
        base_stem = Path(file_path).stem
        output_test_case_path = (
            Path(OUTPUT_DIR) / f"{base_stem}_test_cases_{test_case_type}.txt"
        )
        test_case_utils.store_test_cases_to_text_file(
            combined_test_cases, str(output_test_case_path)
        )

        # excel_test_case_path = (
        #     Path(EXCEL_OUTPUT_DIR) / f"{base_stem}_test_cases_{test_case_type}.xlsx"
        # )
        csv_test_case_path = (
            Path(OUTPUT_DIR) / f"{base_stem}_test_cases_{test_case_type}.csv"
        )

        if model_name == "Mistral":
            test_case_utils.txt_to_csv_mistral(
                str(output_test_case_path), str(csv_test_case_path)
            )
        else:
            test_case_utils.txt_to_csv_llama(
                str(output_test_case_path), str(csv_test_case_path)
            )
        # test_case_utils.format_test_cases_excel(
        #     str(csv_test_case_path),
        #     str(excel_test_case_path),
        #     mode="numbered_in_cell",
        # )

        # MongoDB Storage
        document = {
            "doc_name": os.path.basename(file_path),
            "doc_path": str(file_path),
            # "test_case_excel_path": str(excel_test_case_path),
            "selected_model": model_name,
            "llm_response_testcases": combined_test_cases,
            "api_key_used": (
                f"Token ending with ...{api_key[-5:]}" if api_key else "Default API Key"
            ),
            "test_case_type": test_case_type,  # Store test case type
            "test_case_prompt": test_case_prompt,  # Store prompt for reference
        }

        try:
            collection.insert_one(document)
        except Exception as e:
            print("MongoDB Insertion Error:", str(e))

        return {
            "message": "File Uploaded Successfully",
            "test_cases": combined_test_cases,
            # "excel_path": str(excel_test_case_path),
            "model_used": model_name,
            "test_case_type": test_case_type,
        }

    except Exception as e:
        raise self.retry(exc=e)

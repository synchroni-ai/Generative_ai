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
# ----------------- Directories Setup -----------------
TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
# USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_USER_STORY_PROMPT_FILE_PATH")
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")

Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

DEFAULT_CHUNK_SIZE = 7000
TEST_CASES_CACHE = {}

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


# def save_text_to_excel(data, output_path, column_names):
#     df = pd.DataFrame(data, columns=column_names)
#     df.to_excel(output_path, index=False)


async def safe_generate(generate_func, *args, **kwargs):
    try:
        return generate_func(*args, **kwargs)
    except Exception as e:
        if "Credit limit exceeded" in str(e):
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "Credit limit exceeded. Please add credits or upgrade your plan.",
                    "error_detail": str(e),
                },
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@celery_app.task(bind=True)
def process_and_generate_task(
    self,
    file_path,
    model_name,
    chunk_size,
    cache_key,
    api_key,
    test_case_type="functional",  # New parameter
):
    print("🎯 Celery task started:", file_path)

    try:
        # --------- Handle Cache ---------
        if cache_key and cache_key in TEST_CASES_CACHE:
            return {
                "test_cases": TEST_CASES_CACHE[cache_key]["test_cases"],
                # "user_stories": TEST_CASES_CACHE[cache_key]["user_stories"],
                "cache_key": cache_key,
                "model_used": model_name,
                "api_key": f"API Key ending with..{api_key[-5]}",
                "test_case_type": test_case_type,
            }

        if model_name not in MODEL_DISPATCHER:
            raise HTTPException(
                status_code=400, detail=f"Unsupported model: {model_name}"
            )

        generation_function = MODEL_DISPATCHER[model_name]

        # --------- Load Test Case Prompt Dynamically ---------
        prompt_dir = Path("utils/prompts")
        prompt_file = (
            "functional.txt" if test_case_type == "functional" else "non-functional.txt"
        )
        prompt_path = prompt_dir / prompt_file

        if not prompt_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Prompt file not found: {prompt_path}",
            )

        with open(prompt_path, "r") as f:
            test_case_prompt = f.read()

        # --------- Load User Story Prompt (unchanged) ---------
        # user_story_prompt_path = Path(USER_STORY_PROMPT_FILE_PATH)
        # if not user_story_prompt_path.exists():
        #     raise HTTPException(
        #         status_code=500,
        #         detail=f"User story prompt file not found: {USER_STORY_PROMPT_FILE_PATH}",
        #     )
        # with open(user_story_prompt_path, "r") as f:
        #     user_story_prompt = f.read()

        # --------- Process PDF ---------
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
        if not brd_text:
            raise HTTPException(
                status_code=500, detail="Failed to extract text from PDF."
            )

        cleaned_text = data_ingestion.clean_text(brd_text)
        chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE

        # --------- Chunking ---------
        if model_name == "Mistral":
            chunks = [cleaned_text]
        else:
            chunks = split_text_into_chunks(cleaned_text, chunk)
            if not chunks:
                chunks = [cleaned_text]

        # --------- Generate Test Cases and User Stories ---------
        all_test_cases, all_user_stories = [], []
        test_case_tokens, user_story_tokens = 0, 0

        # --------- Generate Test Cases ---------
        for idx, chunk_text in enumerate(chunks, start=1):
            test_case_text, tokens = test_case_utils.generate_test_cases(
                chunk_text,
                generation_function,
                test_case_prompt=test_case_prompt,  # Pass prompt text directly
            )
            if test_case_text:
                all_test_cases.append(test_case_text)
                test_case_tokens += tokens

        # --------- Generate User Stories ---------
        # for idx, chunk_text in enumerate(chunks, start=1):
        #     user_story_text, tokens = user_story_utils.generate_user_stories(
        #         chunk_text,
        #         generation_function,
        #         user_story_prompt=user_story_prompt,  # Pass prompt text directly
        #     )
        #     if user_story_text:
        #         all_user_stories.append(user_story_text)
        #         user_story_tokens += tokens

        combined_test_cases = "\n".join(all_test_cases)
        # combined_user_stories = "\n".join(all_user_stories)

        # --------- Save Outputs ---------
        base_stem = Path(file_path).stem
        output_test_case_path = (
            Path(OUTPUT_DIR) / f"{base_stem}_test_cases_{test_case_type}.txt"
        )
        test_case_utils.store_test_cases_to_text_file(
            combined_test_cases, str(output_test_case_path)
        )

        # output_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.txt"
        # user_story_utils.store_user_stories_to_text_file(
        #     combined_user_stories, str(output_user_story_path)
        # )

        # Save Excel/CSV files
        excel_test_case_path = (
            Path(EXCEL_OUTPUT_DIR) / f"{base_stem}_test_cases_{test_case_type}.xlsx"
        )
        # excel_user_story_path = (
        #     Path(EXCEL_OUTPUT_DIR) / f"{base_stem}_user_stories.xlsx"
        # )
        csv_test_case_path = (
            Path(OUTPUT_DIR) / f"{base_stem}_test_cases_{test_case_type}.csv"
        )
        # csv_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.csv"

        if model_name == "Mistral":
            test_case_utils.txt_to_csv_mistral(
                str(output_test_case_path), str(csv_test_case_path)
            )
        else:
            test_case_utils.txt_to_csv_llama(
                str(output_test_case_path), str(csv_test_case_path)
            )
        test_case_utils.format_test_cases_excel(
            str(csv_test_case_path), str(excel_test_case_path), mode="numbered_in_cell"
        )

        # if model_name == "Mistral":
        #     user_story_utils.txt_to_csv_mistral(
        #         str(output_user_story_path), str(csv_user_story_path)
        #     )
        # else:
        #     user_story_utils.txt_to_csv_llama(
        #         str(output_user_story_path), str(csv_user_story_path)
        #     )
        # user_story_utils.format_acceptance_criteria_excel(
        #     str(csv_user_story_path),
        #     str(excel_user_story_path),
        #     mode="numbered_in_cell",
        # )

        # # --------- Cost Calculation and MongoDB Storage ---------
        # tokens_per_request = test_case_tokens + user_story_tokens
        # cost_per_token = COST_PER_1M_TOKENS.get(model_name, 0.0)
        # cost = (tokens_per_request / 1000000) * cost_per_token

        if not cache_key:
            cache_key = str(uuid.uuid4())

        TEST_CASES_CACHE[cache_key] = {
            "test_cases": combined_test_cases
            # "user_stories": combined_user_stories,
        }

        document = {
            "doc_name": os.path.basename(file_path),
            "doc_path": str(file_path),
            "test_case_excel_path": str(excel_test_case_path),
            # "user_story_excel_path": str(excel_user_story_path),
            "selected_model": model_name,
            "llm_response_testcases": combined_test_cases,
            # "llm_response_user_stories": combined_user_stories,
            # "total_tokens": tokens_per_request,
            # "approximate_cost_incurred": cost,
            "api_key_used": (
                f"Token ending with ...{api_key[-5:]}" if api_key else "Default API Key"
            ),
            "test_case_type": test_case_type,  # Store test case type
            "test_case_prompt": test_case_prompt,  # Store prompt for reference
            # "user_story_prompt": user_story_prompt,
        }

        try:
            collection.insert_one(document)
            cost_collection.update_one(
                {"api_key": api_key},
                # {"$inc": {"tokens_used": tokens_per_request, "cost_usd": cost}},
                upsert=True,
            )
        except Exception as e:
            print("MongoDB Insertion Error:", str(e))

        return {
            "message": "File Uploaded Successfully",
            "test_cases": combined_test_cases,
            # "user_stories": combined_user_stories,
            "cache_key": cache_key,
            "model_used": model_name,
            "test_case_type": test_case_type,
        }

    except Exception as e:
        raise self.retry(exc=e)

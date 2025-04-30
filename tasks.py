from celery_config import celery_app
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama
from pymongo import MongoClient
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]

MODEL_DISPATCHER = {
    "Mistral": Mistral.generate_with_mistral,
    "Openai": openai.generate_with_openai,
    "Llama": llama.generate_with_llama,
}

INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")
EXCEL_OUTPUT_DIR = os.getenv("EXCEL_OUTPUT_DIR", "excel_files")
TEST_CASE_PROMPT_FILE_PATH = os.getenv("MISTRAL_TEST_CASE_PROMPT_FILE_PATH")
USER_STORY_PROMPT_FILE_PATH = os.getenv("MISTRAL_USER_STORY_PROMPT_FILE_PATH")

Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(EXCEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


@celery_app.task(name="tasks.process_file_task")
def process_file_task(file_path, model_name):
    generation_function = MODEL_DISPATCHER[model_name]

    brd_text, _ = data_ingestion.load_pdf_text(file_path)
    cleaned_text = data_ingestion.clean_text(brd_text)

    if model_name == "Mistral":
        chunks = [cleaned_text]
    else:
        from main import split_text_into_chunks

        chunks = split_text_into_chunks(cleaned_text, 7000)

    all_test_cases = []
    all_user_stories = []

    for chunk in chunks:
        test_case = test_case_utils.generate_test_cases(
            chunk, generation_function, TEST_CASE_PROMPT_FILE_PATH
        )
        if test_case:
            all_test_cases.append(test_case)

    for chunk in chunks:
        user_story = user_story_utils.generate_user_stories(
            chunk, generation_function, USER_STORY_PROMPT_FILE_PATH
        )
        if user_story:
            all_user_stories.append(user_story)

    combined_test_cases = "\n".join(all_test_cases)
    combined_user_stories = "\n".join(all_user_stories)

    base_stem = Path(file_path).stem

    output_test_case_path = Path(OUTPUT_DIR) / f"{base_stem}_test_cases.txt"
    output_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.txt"

    test_case_utils.store_test_cases_to_text_file(
        combined_test_cases, str(output_test_case_path)
    )
    user_story_utils.store_user_stories_to_text_file(
        combined_user_stories, str(output_user_story_path)
    )

    excel_test_case_path = Path(EXCEL_OUTPUT_DIR) / f"{base_stem}_test_cases.xlsx"
    excel_user_story_path = Path(EXCEL_OUTPUT_DIR) / f"{base_stem}_user_stories.xlsx"

    csv_test_case_path = Path(OUTPUT_DIR) / f"{base_stem}_test_cases.csv"
    csv_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.csv"

    if model_name == "Mistral":
        test_case_utils.txt_to_csv_mistral(
            str(output_test_case_path), str(csv_test_case_path)
        )
        user_story_utils.txt_to_csv_mistral(
            str(output_user_story_path), str(csv_user_story_path)
        )
    elif model_name == "Llama":
        test_case_utils.txt_to_csv_llama(
            str(output_test_case_path), str(csv_test_case_path)
        )
        user_story_utils.txt_to_csv_llama(
            str(output_user_story_path), str(csv_user_story_path)
        )

    test_case_utils.format_test_cases_excel(
        str(csv_test_case_path), str(excel_test_case_path)
    )
    user_story_utils.format_acceptance_criteria_excel(
        str(csv_user_story_path), str(excel_user_story_path)
    )

    collection.insert_one(
        {
            "doc_name": Path(file_path).name,
            "doc_path": file_path,
            "test_case_excel_path": str(excel_test_case_path),
            "user_story_excel_path": str(excel_user_story_path),
            "selected_model": model_name,
            "llm_response_testcases": combined_test_cases,
            "llm_response_user_stories": combined_user_stories,
        }
    )

    return {"status": "success", "file": file_path}

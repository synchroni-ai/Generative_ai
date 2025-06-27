import logging
import re
import sys
import os

# Add the parent directory to sys.path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompts import load_prompt
from data_ingestion.data_ingestion import fetch_document_text_from_s3_url
from llms.mistral import call_mistral
from llms.gpt4 import call_gpt4
from pymongo import MongoClient
from bson import ObjectId
import uuid
from dotenv import load_dotenv
from app.models import DocumentStatusEnum

# Load all prompt templates once
PROMPT_MAP = {
    "boundary": load_prompt("boundary"),
    "compliance": load_prompt("compliance"),
    "security": load_prompt("security"),
    "performance": load_prompt("performance"),
    "functional": load_prompt("functional"),
    "non_functional": load_prompt("non_functional"),
}

# Load prompt for summarizing the document
SUMMARIZATION_PROMPT = load_prompt("summarization")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional

API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}
MAX_SUMMARY_LENGTH = 4000  # Max summary length in tokens
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def summarize_document(doc_text: str, api_key: str) -> str:
    """Summarizes the given document text using Mistral."""
    prompt = SUMMARIZATION_PROMPT.format(document_text=doc_text)
    summary = call_mistral(prompt, api_key)  # Mistral summarization
    return summary


def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
    from app.models import DocumentStatusEnum
    client = MongoClient(mongo_uri)
    doc_db = client["generative_ai"]["documents"]
    result_db = client["generative_ai"]["test_case_grouped_results"]

    document_ids = config.get("documents", [])
    inner_config = config.get("config", {})

    llm_model = inner_config.get("llm_model", "").lower()
    llm_version = inner_config.get("llm_version")
    subtypes = inner_config.get("subtypes", [])
    temperature = inner_config.get("temperature", 0.7)
    use_case = inner_config.get("use_case", [])
    config_id = str(config.get("_id", uuid.uuid4()))
    generated_at = inner_config.get("created_at")
    logger.info(f"Starting test case generation config: {config}")

    full_result = {
        "config_id": config_id,
        "llm_model": llm_model,
        "temperature": temperature,
        "use_case": use_case,
        "generated_at": generated_at,
        "results": {
            "documents": {},
            "all_documents": {s: {} for s in subtypes} | {"Final_subtypes": {}},
        },
    }

    EXPECTED_SUBTYPES = {"boundary", "compliance", "security", "performance", "functional", "non_functional"}

    for doc_id in document_ids:
        logger.info(f"Processing document ID: {doc_id}")
        doc = doc_db.find_one({"_id": ObjectId(doc_id)})
        if not doc or "s3_url" not in doc:
            logger.warning(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
            continue

        # Fetch and summarize
        raw_text = fetch_document_text_from_s3_url(doc["s3_url"])
        logger.info(f"Fetched text from S3 for document {doc_id}. Text length: {len(raw_text)}")

        summarized_text = summarize_document(raw_text, api_keys["together_ai"])
        logger.info(f"Generated summary for document {doc_id}. Summary length: {len(summarized_text)}")
        print(f"Summary: {summarized_text}")

        # Update status to PROCESSING
        try:
            doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": DocumentStatusEnum.PROCESSING.value}})
            logger.info(f"✅ Updated document {doc_id} to PROCESSING (1)")
        except Exception as e:
            logger.error(f"❌ Error updating document {doc_id} to PROCESSING(1): {e}")

        doc_results = {}
        all_subtypes_outputs = []

        for subtype in subtypes:
            subtype_key = subtype.lower()
            if subtype_key not in PROMPT_MAP:
                logger.warning(f"⚠️ Skipping unsupported subtype: {subtype}")
                continue

            try:
                prompt_template = PROMPT_MAP[subtype_key]
                prompt = prompt_template.format(brd_text=summarized_text)
                logger.info(f"Generating test cases for subtype: {subtype}, prompt length: {len(prompt)}")

                if llm_model == "mistral":
                    output = call_mistral(prompt, api_keys["together_ai"])
                elif llm_model == "openai":
                    if not llm_version:
                        raise ValueError("llm_version is required when llm_model is OpenAI")
                    output = call_gpt4(prompt, api_keys["openai"], model=llm_version)
                else:
                    raise ValueError(f"Unsupported LLM model: {llm_model}")

                logger.debug(f"LLM Output for {subtype}:\n{output}")
                doc_results[subtype] = output
                all_subtypes_outputs.append(output)
                full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

            except Exception as e:
                logger.error(f"❌ Error generating test case for {subtype} in document {doc_id}: {e}")
                continue

        full_result["results"]["documents"][str(doc["_id"])] = {
            **doc_results,
            "all_subtypes": all_subtypes_outputs,
        }

        full_result["results"]["all_documents"]["Final_subtypes"][str(doc["_id"])] = all_subtypes_outputs

    # FINAL STATUS UPDATE
    for doc_id in document_ids:
        doc_result = full_result["results"]["documents"].get(str(doc_id), {})
        generated_subtypes = set(doc_result.keys()) - {"all_subtypes"}

        if generated_subtypes == EXPECTED_SUBTYPES:
            new_status = DocumentStatusEnum.COMPLETE.value
            print(f"✅ Document {doc_id} has all 6 subtypes. Setting to COMPLETE (3)")
        else:
            new_status = DocumentStatusEnum.PROCESSED.value
            print(f"ℹ️ Document {doc_id} incomplete. Setting to PROCESSED (2)")

        try:
            doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": new_status}})
            print(f"🔁 Document {doc_id} updated to status {new_status}")
        except Exception as e:
            print(f"❌ Error updating document {doc_id} to status {new_status}: {e}")

    return full_result

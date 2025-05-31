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


# Load all prompt templates once
PROMPT_MAP = {
    "boundary": load_prompt("boundary"),
    "compliance": load_prompt("compliance"),
    "security": load_prompt("security"),
    "performance": load_prompt("performance"),
    "functional": load_prompt("functional"),
    "non-functional": load_prompt("non_functional"),
}

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional

API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}


def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
    """
    Accepts a full configuration document from the 'configurations' collection.
    It expects the following structure:
    {
        "documents": [...],
        "config": {
            "llm_model": "...",
            "temperature": 0.7,
            "use_case": [...],
            "subtypes": [...]
        },
        ...
    }
    """
    client = MongoClient(mongo_uri)
    doc_db = client["generative_ai"]["documents"]
    result_db = client["test_case_db"]["grouped_results"]

    document_ids = config.get("documents", [])
    inner_config = config.get("config", {})

    llm_model = inner_config.get("llm_model", "").lower()
    subtypes = inner_config.get("subtypes", [])
    temperature = inner_config.get("temperature", 0.7)
    use_case = inner_config.get("use_case", [])
    config_id = str(config.get("_id", uuid.uuid4()))
    generated_at = inner_config.get("created_at")

    # Initialize the final result object
    full_result = {
        "config_id": config_id,
        "llm_model": llm_model,
        "temperature": temperature,
        "use_case": use_case,
        "generated_at": generated_at,
        "results": {
            "documents": {},
            "all_documents": {s: {} for s in subtypes} | {"all_subtypes": {}},
        },
    }

    for doc_id in document_ids:
        doc = doc_db.find_one({"_id": ObjectId(doc_id)})
        if not doc or "s3_url" not in doc:
            print(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
            continue

        doc_text = fetch_document_text_from_s3_url(doc["s3_url"])
        doc_results = {}
        all_subtypes_results = []

        for subtype in subtypes:
            subtype_key = subtype.lower()
            if subtype_key not in PROMPT_MAP:
                print(f"⚠️ Skipping unsupported subtype: {subtype}")
                continue

            prompt_template = PROMPT_MAP[subtype_key]
            prompt = prompt_template.format(brd_text=doc_text)

            if llm_model == "mistral":
                output = call_mistral(prompt, api_keys["together_ai"])
            elif llm_model == "gpt-4":
                output = call_gpt4(prompt, api_keys["openai"])
            else:
                raise ValueError(f"Unsupported LLM model: {llm_model}")

            # Store by subtype under document
            doc_results[subtype] = output
            all_subtypes_results.append(output)

            # Store under all_documents by subtype
            full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

        # Store all results per document
        full_result["results"]["documents"][str(doc["_id"])] = {
            **doc_results,
            "all_subtypes": all_subtypes_results,
        }

        # Store under global all_subtypes
        full_result["results"]["all_documents"]["all_subtypes"][
            str(doc["_id"])
        ] = all_subtypes_results

    result_db.insert_one(full_result)
    return full_result


from bson import ObjectId

# Set your config ID
CONFIG_ID = "683ad3297254e6bbf82d4f03"

# Fetch full config document
client = MongoClient(MONGO_URI)
config_doc = client["generative_ai"]["configurations"].find_one(
    {"_id": ObjectId(CONFIG_ID)}
)

if not config_doc:
    print(f"❌ Config with ID {CONFIG_ID} not found.")
else:
    result = generate_test_cases(config_doc, MONGO_URI, API_KEYS)
    print("✅ Test case generation complete.")
    print(result)

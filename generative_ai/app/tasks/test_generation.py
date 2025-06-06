from app.tasks.celery_worker import celery_app 
from pymongo import MongoClient
from bson import ObjectId
from app.test_case_generator.generation.test_case_generator import generate_test_cases
import os
from dotenv import load_dotenv
import datetime
import logging
from app.models import DocumentStatusEnum
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
API_KEYS = {
    "together_ai": os.getenv("TOGETHER_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY", ""),
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

  # Make sure this import works

@celery_app.task(bind=True)
def run_test_generation(self, config_id: str):
    logger.info(f"Starting test generation task for config_id: {config_id}")

    client = MongoClient(MONGO_URI)
    db = client["generative_ai"]

    try:
        config = db["configurations"].find_one({"_id": ObjectId(config_id)})
        if not config:
            logger.error(f"Configuration with ID {config_id} not found")
            raise ValueError(f"Configuration with ID {config_id} not found")

        result = generate_test_cases(config, MONGO_URI, API_KEYS)

        # Count test cases
        num_test_cases = 0
        document_names = result["results"]["documents"].keys()

        for doc_name in document_names:
            test_cases = result["results"]["documents"][doc_name].get("test_cases", [])
            num_test_cases += len(test_cases)

        logger.info(f"Total test cases generated: {num_test_cases}")

        # Prepare job result
        job_result = {
            "job_id": self.request.id,
            "config_id": config_id,
            "llm_model": config["config"]["llm_model"],
            "temperature": config["config"]["temperature"],
            "use_case": config["config"]["use_case"],
            "generated_at": datetime.datetime.utcnow(),
            "results": result["results"],
            "status": "completed",
            "summary": {
                "documents": list(document_names),
                "subtypes": config["config"]["subtypes"],
            },
        }

        db["test_case_grouped_results"].insert_one(job_result)
        logger.info("Inserted result into generative_ai.test_case_grouped_results collection")

        # ✅ Update document statuses in 'documents' collection
        for doc_name in document_names:
            updated = db["documents"].update_many(
                {"file_name": doc_name},
                {"$set": {"status": DocumentStatusEnum.PROCESSED.value}}  # Use `.value` to store as int
            )
            logger.info(f"Updated status to PROCESSED for {updated.modified_count} document(s) with file_name: {doc_name}")

        return {"job_id": self.request.id, "status": "completed"}

    except Exception as e:
        logger.error(f"Error in run_test_generation task: {e}", exc_info=True)
        raise

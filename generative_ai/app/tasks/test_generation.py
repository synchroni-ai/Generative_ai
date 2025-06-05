from app.tasks.celery_worker import celery_app 
from pymongo import MongoClient
from bson import ObjectId
from app.test_case_generator.generation.test_case_generator import generate_test_cases
import os
from dotenv import load_dotenv
import datetime
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
API_KEYS = {
    "together_ai": os.getenv("TOGETHER_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY", ""),
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def run_test_generation(self, config_id: str):
    """
    Celery task to run test case generation and store results in MongoDB.
    """
    logger.info(f"Starting test generation task for config_id: {config_id}")

    client = MongoClient(MONGO_URI)
    db = client["generative_ai"]  # Ensure this matches your target DB

    try:
        config = db["configurations"].find_one({"_id": ObjectId(config_id)})

        if not config:
            error_message = f"Configuration with ID {config_id} not found"
            logger.error(error_message)
            raise ValueError(error_message)

        result = generate_test_cases(config, MONGO_URI, API_KEYS)

        # Safely count test cases
        num_test_cases = 0
        for doc_name, doc_results in result["results"]["documents"].items():
            test_cases = doc_results.get("test_cases", [])
            if not test_cases:
                logger.warning(f"No test_cases found for document: {doc_name}")
            num_test_cases += len(test_cases)

        logger.info(f"Total test cases generated: {num_test_cases}")

        # Prepare job result for MongoDB
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
                "documents": list(result["results"]["documents"].keys()),
                "subtypes": config["config"]["subtypes"],
            },
        }

        db["test_case_grouped_results"].insert_one(job_result)
        logger.info("Inserted result into generative_ai.test_case_grouped_results collection")

        return {"job_id": self.request.id, "status": "completed"}

    except Exception as e:
        logger.error(f"Error in run_test_generation task: {e}", exc_info=True)
        raise

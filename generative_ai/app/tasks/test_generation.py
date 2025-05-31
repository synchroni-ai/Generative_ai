from celery import Celery
from pymongo import MongoClient
from bson import ObjectId
from test_case_generator.generation.test_case_generator import generate_test_cases
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery("tasks", broker=os.getenv("CELERY_BROKER_URL"))

MONGO_URI = os.getenv("MONGO_URI")
API_KEYS = {
    "together_ai": os.getenv("TOGETHER_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY", ""),
}


@celery_app.task(bind=True)
def run_test_generation(self, config_id: str):
    client = MongoClient(MONGO_URI)
    config = client["generative_ai"]["configurations"].find_one(
        {"_id": ObjectId(config_id)}
    )

    if not config:
        raise ValueError(f"Configuration with ID {config_id} not found")

    result = generate_test_cases(config, MONGO_URI, API_KEYS)

    # Store metadata for job tracking
    client["test_case_db"]["jobs"].insert_one(
        {
            "job_id": self.request.id,
            "config_id": config_id,
            "status": "completed",
            "summary": {
                "documents": list(result["results"]["documents"].keys()),
                "subtypes": config["config"]["subtypes"],
            },
        }
    )

    return {"job_id": self.request.id, "status": "completed"}

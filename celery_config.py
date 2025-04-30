# Generative_ai/celery_config.py
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "generative_ai_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "Generative_ai.tasks.generate_test_cases",
        "Generative_ai.tasks.generate_user_stories"
    ]
)

celery_app.conf.task_routes = {
    "Generative_ai.tasks.generate_test_cases.generate_test_cases_task": {"queue": "test_cases"},
    "Generative_ai.tasks.generate_user_stories.generate_user_story_task": {"queue": "user_stories"},
}

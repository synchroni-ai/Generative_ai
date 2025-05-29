from celery import Celery
import os

# Set up Celery with Redis as the message broker
celery_app = Celery(
    "task_with_api_key",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["task_with_api_key"],
)
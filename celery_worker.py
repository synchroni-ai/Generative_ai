from celery import Celery
import os

# Set up Celery with Redis as the message broker
celery_app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["tasks"],
)

celery_app.conf.update(
    task_routes={
        "tasks.process_and_generate_task": {"queue": "celery"},
    },
)

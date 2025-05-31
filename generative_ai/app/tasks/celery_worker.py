from celery import Celery

# Initialize Celery app
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

# ✅ Correct path for autodiscovery
# celery_app.autodiscover_tasks(["app.tasks"])

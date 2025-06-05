from celery import Celery

# Initialize Celery app
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",  # Optional: useful if you want result backend
)

# Autodiscover tasks from the relevant modules
celery_app.autodiscover_tasks(
    ["app.api.routes"]  # adjust this if you move task definitions elsewhere
)

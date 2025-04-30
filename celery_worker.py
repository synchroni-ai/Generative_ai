# celery_worker.py
# Generative_ai/celery_worker.py
# from celery_config import celery_app  # ✅ should work
from Generative_ai.celery_config import celery_app

# Required for Celery to discover tasks
if __name__ == "__main__":
    celery_app.worker_main()



from celery_config import celery_app
from tasks import process_file_task


if __name__ == "__main__":
    celery_app.worker_main()

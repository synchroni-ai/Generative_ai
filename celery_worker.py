from celery import Celery
import os

# Set up Celery with Redis as the message broker
celery_app = Celery(
    "task_with_api_key",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["task_with_api_key"],
)

# No changes needed in celery_app.conf.update because we are calling tasks dynamically
# celery_app.conf.update(
#     task_routes={
#         "task_with_api_key.process_and_generate_functional_task": {"queue": "celery"},
#         "task_with_api_key.process_and_generate_non_functional_task": {"queue": "celery"},
#         "task_with_api_key.process_and_generate_security_task": {"queue": "celery"},
#         "task_with_api_key.process_and_generate_performance_task": {"queue": "celery"},
#         "task_with_api_key.process_and_generate_boundary_task": {"queue": "celery"},
#         "task_with_api_key.process_and_generate_compliance_task": {"queue": "celery"},
#     },
# )

import sys
import os

# Add the root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


from fastapi import APIRouter, HTTPException
from app.tasks.test_generation import run_test_generation
from celery.result import AsyncResult
from celery import current_app as celery_app

router = APIRouter()


@router.post("/generation/run/{config_id}")
async def run_generation_task(config_id: str):
    task = run_test_generation.delay(config_id)
    return {"job_id": task.id, "status": "queued"}


@router.get("/generation/status/{job_id}")
def get_job_status(job_id: str):
    task = run_test_generation.AsyncResult(job_id)
    return {"job_id": job_id, "status": task.status}


@router.post("/generation/cancel/{job_id}")
async def cancel_generation_job(job_id: str):
    result = AsyncResult(job_id, app=celery_app)

    if not result:
        raise HTTPException(status_code=404, detail="Job not found")

    if result.state in ["PENDING", "RECEIVED", "STARTED"]:
        result.revoke(terminate=True)
        return {"job_id": job_id, "status": "canceled"}
    else:
        return {
            "job_id": job_id,
            "status": f"cannot cancel, job is in terminal state: {result.state}",
        }

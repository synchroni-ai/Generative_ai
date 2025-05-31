from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from app.tasks.test_generation import process_and_generate_task
from uuid import uuid4

router = APIRouter()


class GenerationConfig(BaseModel):
    llm_model: str
    temperature: float


class RunGenerationRequest(BaseModel):
    document_ids: List[str]
    config: GenerationConfig


@router.post("/api/generation/run")
async def run_generation(request: RunGenerationRequest):
    job_id = str(uuid4())

    # Trigger Celery task
    process_and_generate_task.delay(
        job_id=job_id, document_ids=request.document_ids, config=request.config.dict()
    )

    return {"job_id": job_id, "status": "queued"}

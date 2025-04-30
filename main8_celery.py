from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
from tasks import process_file_task
from celery.result import AsyncResult
from celery_config import celery_app

app = FastAPI()

INPUT_DIR = "input_pdfs"
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)


@app.post("/process/")
async def process_async_file(
    file: UploadFile = File(...),
    model_name: str = Form("Mistral"),
):
    file_id = str(uuid.uuid4())
    file_path = Path(INPUT_DIR) / f"{file_id}_{file.filename}"
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Trigger Celery task
    task = process_file_task.delay(str(file_path), model_name)

    return JSONResponse(content={"message": "Task submitted", "task_id": task.id})


@app.get("/status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }

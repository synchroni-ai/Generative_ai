from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from tasks.generate_test_cases import generate_test_cases
from tasks.generate_user_stories import generate_user_stories
from celery.result import AsyncResult
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB Setup
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("mongodb://localhost:27017"))
db = client[os.getenv("Gen_AI")]

# Placeholder: Simulated PDF processing
@app.post("/process_pdf/")
async def process_pdf(file: UploadFile = File(...)):
    try:
        # Simulate extracting cleaned text
        content = await file.read()
        cleaned_text = content.decode("utf-8", errors="ignore")
        return {"cleaned_text": cleaned_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Generate Test Cases Endpoint
@app.post("/generate_test_cases/")
async def generate_test_cases_endpoint(payload: dict):
    cleaned_text = payload.get("cleaned_text")
    if not cleaned_text:
        return JSONResponse(status_code=400, content={"error": "Missing 'cleaned_text'"})
    
    task = generate_test_cases.delay(cleaned_text)
    await db.tasks.insert_one({"task_id": task.id, "status": "PENDING", "type": "test_cases"})
    return {"task_id": task.id}

# Generate User Stories Endpoint
@app.post("/generate_user_stories/")
async def generate_user_stories_endpoint(payload: dict):
    input_text = payload.get("input_text")
    if not input_text:
        return JSONResponse(status_code=400, content={"error": "Missing 'input_text'"})
    
    task = generate_user_stories.delay(input_text)
    await db.tasks.insert_one({"task_id": task.id, "status": "PENDING", "type": "user_stories"})
    return {"task_id": task.id}

# Status Check Endpoint (for any task)
@app.get("/status/{task_id}")
async def check_status(task_id: str):
    from celery_config import celery_app
    result = AsyncResult(task_id, app=celery_app)

    # Optional: update status in MongoDB
    await db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {"status": result.status}}
    )

    if result.ready():
        return {"status": result.status, "result": result.result}
    else:
        return {"status": result.status}

# Endpoints
from fastapi import FastAPI, HTTPException, Request
import logging
import os
import json
import requests
import tempfile
from datetime import datetime, timezone
from utils import download_document, process_document
from dotenv import load_dotenv

load_dotenv()

import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI()


@app.post("/ilo_doc_tagging_function")
async def ilo_doc_tagging_function(request: Request):
    body = await request.json()
    if not body:
        raise HTTPException(status_code=400, detail="Request body is required")

    document_url = body.get("document_url")
    existing_tag = body.get("existing_tag", "")

    if not document_url:
        raise HTTPException(status_code=400, detail="Missing 'document_url'")

    local_path = download_document(document_url)
    result = process_document(local_path, existing_tag)

    return result


@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {"llama_index": True, "azure_services": True},
    }

    return health_status

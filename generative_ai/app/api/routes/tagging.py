from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Body
from pymongo import MongoClient
from keybert import KeyBERT
import fitz  # PyMuPDF
import uuid
import base64
from typing import List
from app.api import deps
from app.models import User

router = APIRouter()

# Initialize MongoDB client (consider moving to a dependency injection like your other routes)
client = MongoClient("mongodb://localhost:27017")
db = client.document_tags_db
tags_collection = db.tags

# Initialize KeyBERT model (consider making this a singleton or using dependency injection)
kw_model = KeyBERT()  # Initialize here to avoid re-initialization with each request.

# --- Utility Functions (Keep these OUTSIDE the route definitions) ---

def extract_text(file_bytes: bytes) -> str:
    """Extracts text from a PDF file in bytes format."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")  # Log the error
        raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {e}")



def generate_tags(text: str) -> List[str]:
    """Generates keywords/tags from text using KeyBERT."""
    try:

        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
        return [kw[0] for kw in keywords[:5]]
    except Exception as e:
        print(f"Error generating tags: {e}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Error generating tags: {e}")


# --- API Endpoints ---

@router.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    filename: str = Form(...),
    
):
    """Processes a document uploaded as multipart/form-data, extracts tags, and saves the document info."""
    try:
        file_bytes = await file.read()
        text = extract_text(file_bytes) # Pass the extracted text to generate_tags function
        tags = generate_tags(text)

        doc_id = str(uuid.uuid4())
        document_data = {
            "_id": doc_id,
            "filename": filename,
            "tags": tags,
              # Store the user ID
        }
        tags_collection.insert_one(document_data)
        
        return {"document_id": doc_id, "tags": tags}
    except HTTPException as e:
        raise e # Re-raise HTTPExceptions (already have status codes)
    except Exception as e:
        print(f"Unexpected error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error processing document: {str(e)}")



@router.post("/process-document-base64")
async def process_document_base64(
    payload: dict = Body(...),
    
):
    """Processes a document encoded in base64 within a JSON payload, extracts tags, and saves the document info."""
    try:
        file_base64 = payload.get("file_base64")
        filename = payload.get("filename")

        if not file_base64 or not filename:
            raise HTTPException(status_code=400, detail="Missing 'file_base64' or 'filename' in request body")

        file_bytes = base64.b64decode(file_base64)

        text = extract_text(file_bytes)
        tags = generate_tags(text)


        doc_id = str(uuid.uuid4())
        document_data = {
            "_id": doc_id,
            "filename": filename,
            "tags": tags,
             # Store the user ID
        }
        tags_collection.insert_one(document_data)
       

        return {"document_id": doc_id, "tags": tags}

    except HTTPException as e:
        raise e # Re-raise HTTPExceptions
    except Exception as e:
        print(f"Unexpected error processing base64 document: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error processing base64 document: {str(e)}")



@router.get("/get-tags/{doc_id}")
async def get_tags(
    doc_id: str,
):
    """Retrieves tags for a document by its ID."""
    document = tags_collection.find_one({"_id": doc_id})
    if document:
        # Consider excluding _id or other fields you don't want to expose
        return {"filename": document["filename"], "tags": document["tags"]}
    raise HTTPException(status_code=404, detail="Document not found")
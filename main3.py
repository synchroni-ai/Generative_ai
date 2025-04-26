from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from pathlib import Path
import os
import re
import time
import uuid

# Import your custom modules
from utils import data_ingestion, test_case_utils, user_story_utils
from utils.llms import Mistral, openai, llama

# ----------------- FastAPI App Setup -----------------
app = FastAPI(root_path="/backend")
origins = [
    "https://gen-ai.synchroni.xyz",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- MongoDB Setup -----------------
load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]

# ----------------- Directories Setup -----------------
PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH")
USER_STORY_PROMPT_FILE_PATH = os.getenv("USER_STORY_PROMPT_FILE_PATH")
INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_files")

Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

DEFAULT_CHUNK_SIZE = 7000
TEST_CASES_CACHE = {}

# ----------------- Model Dispatcher -----------------
MODEL_DISPATCHER = {
    "Mistral": Mistral.generate_with_mistral,
    "Openai": openai.generate_with_openai,
    "Llama": llama.generate_with_llama,
}

# ----------------- Helpers -----------------
def split_text_into_chunks(text, chunk_size=7000):
    chunks = []
    current_chunk = ""
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# ----------------- Main Endpoint -----------------
@app.post("/process_and_generate/")
async def process_and_generate(
    file: UploadFile = File(...),
    model_name: str = Form("Mistral"),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
):
    try:
        # ------------- Handle Cache -------------
        if cache_key and cache_key in TEST_CASES_CACHE:
            return JSONResponse(content={
                "test_cases": TEST_CASES_CACHE[cache_key]["test_cases"],
                "user_stories": TEST_CASES_CACHE[cache_key]["user_stories"],
                "cache_key": cache_key,
                "model_used": model_name
            })

        # ------------- Validate Model -------------
        if model_name not in MODEL_DISPATCHER:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {model_name}")
        generation_function = MODEL_DISPATCHER[model_name]

        # ------------- Save Uploaded File -------------
        file_name = file.filename
        file_path = Path(INPUT_DIR) / file_name

        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving PDF: {str(e)}")
        finally:
            await file.close()

        # ------------- Process PDF -------------
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
        if not brd_text:
            raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

        cleaned_text = data_ingestion.clean_text(brd_text)
        chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE

        # ------------- Chunking Based on Model -------------
        if model_name == "Mistral":
            chunks = [cleaned_text]
        else:
            chunks = split_text_into_chunks(cleaned_text, chunk)
            if not chunks:
                chunks = [cleaned_text]

        # ------------- Generate Test Cases -------------
        all_test_cases = []
        start_time = time.time()    

        for idx, chunk_text in enumerate(chunks):
            print(f"Processing chunk {idx+1}/{len(chunks)} with model {model_name} for Test Cases")
            test_case_text = test_case_utils.generate_test_cases(
                chunk_text, generation_function, PROMPT_FILE_PATH
            )
            if test_case_text:
                all_test_cases.append(test_case_text)

        combined_test_cases = "\n".join(all_test_cases)
        end_time = time.time()
        generation_latency = int(end_time - start_time)

        # ------------- Generate User Stories -------------
        all_user_stories = []
        start_time_user_story = time.time()

        for idx, chunk_text in enumerate(chunks):
            print(f"Processing chunk {idx+1}/{len(chunks)} with model {model_name} for User Stories")
            user_story_text = user_story_utils.generate_user_stories(
                chunk_text, generation_function, USER_STORY_PROMPT_FILE_PATH
            )
            if user_story_text:
                all_user_stories.append(user_story_text)

        combined_user_stories = "\n".join(all_user_stories)
        end_time_user_story = time.time()
        user_story_generation_latency = int(end_time_user_story - start_time_user_story)

        # ------------- Save Outputs -------------
        base_stem = Path(file_name).stem

        output_test_case_path = Path(OUTPUT_DIR) / f"{base_stem}_test_cases.txt"
        with open(output_test_case_path, "w", encoding="utf-8") as f:
            f.write(combined_test_cases)

        output_user_story_path = Path(OUTPUT_DIR) / f"{base_stem}_user_stories.txt"
        with open(output_user_story_path, "w", encoding="utf-8") as f:
            f.write(combined_user_stories)

        # ------------- Save to MongoDB and Cache -------------
        if not cache_key:
            cache_key = str(uuid.uuid4())

        TEST_CASES_CACHE[cache_key] = {
            "test_cases": combined_test_cases,
            "user_stories": combined_user_stories
        }

        document = {
            "doc_name": file.filename,
            "doc_path": str(file_path),
            "selected_model": model_name,
            "llm_response_testcases": combined_test_cases,
            "llm_response_user_stories": combined_user_stories,
            "llm_response_latency": generation_latency,
        }
        collection.insert_one(document)

        return JSONResponse(content={
            "test_cases": combined_test_cases,
            "user_stories": combined_user_stories,
            "cache_key": cache_key,
            "model_used": model_name
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- MongoDB Fetch Endpoints -----------------
@app.get("/documents/")
def get_all_documents():
    documents = list(collection.find())
    return [serialize_document(doc) for doc in documents]

@app.get("/documents/{document_id}")
def get_document_by_id(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return serialize_document(doc)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

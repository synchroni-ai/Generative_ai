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

from utils import data_ingestion, test_case_utils
from utils.llms import Mistral
from utils.llms import openai
from utils.llms import llama

 # your openai.py in llms folder
#cloned

# ------------- FastAPI and MongoDB Setup -------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["Gen_AI"]
collection = db["test_case_generation"]

PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH")
DEFAULT_CHUNK_SIZE = 7000
TEST_CASES_CACHE = {}

INPUT_DIR = os.getenv("INPUT_DIR", "input_pdfs")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_test_cases")

Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ------------- Model Dispatcher -------------
MODEL_DISPATCHER = {
    "Mistral": Mistral.generate_with_mistral,
    "openai": openai.generate_with_openai,
    "llama": llama.generate_with_llama,
    # Add other models like "llama": llama_llm.generate_with_llama if you have them
}

# ------------- Text Chunking Helper -------------
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


# ------------- Main Endpoint -------------
@app.post("/process_and_generate/")
async def process_and_generate(
    file: UploadFile = File(...),
    prompt_file_path: Optional[str] = Query(default=None),
    chunk_size: Optional[int] = Query(default=None),
    cache_key: Optional[str] = Query(default=None),
    model_name: str = Form("together"),  # <--- now reading model_name from form-data
):
    try:
        # ---------------- Cache Check ----------------
        if cache_key and cache_key in TEST_CASES_CACHE:
            print(f"Retrieving test cases from cache with key: {cache_key}")
            return JSONResponse(content={
                "test_cases": TEST_CASES_CACHE[cache_key],
                "cache_key": cache_key,
                "model_used": model_name
            })

        # ---------------- Validate Model ----------------
        if model_name not in MODEL_DISPATCHER:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {model_name}")
        generation_function = MODEL_DISPATCHER[model_name]

        # ---------------- Save File ----------------
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

        # ---------------- Preprocess PDF ----------------
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))
        if not brd_text:
            raise HTTPException(status_code=500, detail="Failed to load PDF text.")
        cleaned_brd_text = data_ingestion.clean_text(brd_text)

        prompt = prompt_file_path if prompt_file_path else PROMPT_FILE_PATH
        chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE

        chunks = split_text_into_chunks(cleaned_brd_text, chunk)

        # ---------------- Generate Test Cases ----------------
        all_test_cases = []
        start_time = time.time()

        for i, chunk_text in enumerate(chunks):
            print(f"Processing Chunk {i + 1}/{len(chunks)} with model: {model_name}")
            test_cases_text = test_case_utils.generate_test_cases(
                chunk_text,
                generation_function,
                prompt,
            )
            if test_cases_text:
                all_test_cases.append(test_cases_text)
            else:
                print(f"Failed to generate test cases for chunk {i + 1}.")

        end_time = time.time()
        generation_latency = int(end_time - start_time)

        combined_test_cases = "\n".join(all_test_cases)

        # ---------------- Save Output File ----------------
        output_file_name = f"{Path(file_name).stem}_test_cases.txt"
        output_file_path = Path(OUTPUT_DIR) / output_file_name

        try:
            with open(output_file_path, "w") as f:
                f.write(combined_test_cases)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving test cases: {str(e)}")

        # ---------------- Cache & Store in DB ----------------
        if not cache_key:
            cache_key = str(uuid.uuid4())

        TEST_CASES_CACHE[cache_key] = combined_test_cases
        print(f"Storing test cases in cache with key: {cache_key}")

        document = {
            "doc_name": file.filename,
            "doc_path": str(file_path),
            "selected_model": model_name,
            "llm_response_testcases": combined_test_cases,
            "llm_response_latency": generation_latency
        }
        collection.insert_one(document)

        return JSONResponse(content={
            "test_cases": combined_test_cases,
            "cache_key": cache_key,
            "model_used": model_name
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------- MongoDB Document Endpoints -------------
def serialize_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/documents/")
def get_all_documents():
    documents = list(collection.find())
    return [serialize_document(doc) for doc in documents]


@app.get("/documents/{document_id}")
def get_document_by_id(document_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(document_id)})
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return serialize_document(doc)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

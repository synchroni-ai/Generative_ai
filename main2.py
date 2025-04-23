from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import os
from utils import data_ingestion, test_case_utils
from utils.llms import together_ai
from dotenv import load_dotenv
from typing import Optional
import re
import tempfile  # Import the tempfile module

app = FastAPI()

load_dotenv()

# Configuration (Ensure these environment variables are set)
PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH")
DEFAULT_CHUNK_SIZE = 4000
TEST_CASES_CACHE = {}  # In-memory cache for test cases


def split_text_into_chunks(text, chunk_size=4000):
    """Splits a long text into chunks based on sentences and paragraphs where possible"""
    chunks = []
    current_chunk = ""
    sentences = re.split(
        r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text
    )  # Split into sentences
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:  # +1 for space
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())  # Add the previous chunk
            current_chunk = sentence + " "  # Start a new chunk
    if current_chunk:  # Add the last chunk
        chunks.append(current_chunk.strip())
    return chunks


@app.post("/process_pdf/")
async def process_pdf(file: UploadFile = File(...)):
    """
    Endpoint to receive a PDF, extract and clean the text.

    Args:
        file: Uploaded PDF file.

    Returns:
        JSON response containing the cleaned text, or an error message.
    """
    try:
        contents = await file.read()
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(contents)
            temp_pdf_path = temp_file.name  # Get the temporary file path

        brd_text, _ = data_ingestion.load_pdf_text(temp_pdf_path)
        os.remove(temp_pdf_path)  # Clean up temporary file
        if not brd_text:
            raise HTTPException(status_code=500, detail="Failed to load PDF text.")
        cleaned_brd_text = data_ingestion.clean_text(brd_text)
        return JSONResponse(content={"cleaned_text": cleaned_brd_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate_test_cases/")
async def generate_test_cases(
    cleaned_text: str = Query(
        ..., title="Cleaned Text", description="The cleaned text of the BRD."
    ),
    prompt_file_path: Optional[str] = Query(
        default=None,
        title="Prompt File Path",
        description="The path to the prompt file (optional).",
    ),
    chunk_size: Optional[int] = Query(
        default=None, title="Chunk Size", description="The size of chunks (optional)."
    ),
    cache_key: Optional[str] = Query(
        default=None,
        title="Cache Key",
        description="Key to retrieve cached test cases.",
    ),
):
    """
    Endpoint to generate test cases from the given cleaned text.  Uses a GET request and takes parameters as query parameters.  Caches the generated test cases.

    Args:
        cleaned_text: The cleaned text of the BRD.
        prompt_file_path: The path to the prompt file (optional).
        chunk_size: The size of chunks

    Returns:
        JSON response containing the generated test cases, or an error message.
    """
    try:

        if cache_key and cache_key in TEST_CASES_CACHE:
            print(f"Retrieving test cases from cache with key: {cache_key}")
            return JSONResponse(content={"test_cases": TEST_CASES_CACHE[cache_key]})

        # Load prompt and chuck size:
        prompt = prompt_file_path if prompt_file_path else PROMPT_FILE_PATH
        chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE
        # 2. Chunk the BRD
        chunks = split_text_into_chunks(cleaned_text, chunk)

        # 3. Iterate through the chunks and generate test cases for each
        all_test_cases = []
        for i, chunk in enumerate(chunks):
            print(f"Processing Chunk {i+1}/{len(chunks)}")

            # 4. Generate Test Cases for the current chunk
            test_cases_text = test_case_utils.generate_test_cases(
                chunk,
                together_ai.generate_with_together,
                prompt,  # Same prompt for all chunks
            )

            if test_cases_text:
                all_test_cases.append(test_cases_text)
            else:
                print(f"Failed to generate test cases for chunk {i+1}.")

        # 5. Combine all test cases (JSON format now)
        combined_test_cases = "\n".join(all_test_cases)

        # Store the generated test cases in the cache
        if not cache_key:
            import uuid

            cache_key = str(uuid.uuid4())

        TEST_CASES_CACHE[cache_key] = combined_test_cases
        print(f"Storing test cases in cache with key: {cache_key}")

        return JSONResponse(
            content={"test_cases": combined_test_cases, "cache_key": cache_key}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

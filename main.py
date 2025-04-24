from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import os
from utils import data_ingestion, test_case_utils
from utils.llms import together_ai
from dotenv import load_dotenv
from typing import Optional
import re
import tempfile
import uuid
from pathlib import Path

app = FastAPI()

load_dotenv()

# Configuration (Ensure these environment variables are set)
PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH")
DEFAULT_CHUNK_SIZE = 7000
TEST_CASES_CACHE = {}  # In-memory cache for test cases

# Input and Output Directories
INPUT_DIR = os.getenv(
    "INPUT_DIR", "input_pdfs"
)  # Default to 'input_pdfs' if not in .env
OUTPUT_DIR = os.getenv(
    "OUTPUT_DIR", "output_test_cases"
)  # Default to 'output_test_cases' if not in .env

# Create directories if they don't exist
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def split_text_into_chunks(text, chunk_size=7000):
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


@app.post("/process_and_generate/")
async def process_and_generate(
    file: UploadFile = File(...),
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
    Endpoint to receive a PDF, extract text, clean it, chunk it, and generate test cases.
    Saves the uploaded PDF and generated test cases to specified directories.
    Optionally retrieves test cases from cache if a cache key is provided.

    Args:
        file: Uploaded PDF file.
        prompt_file_path: The path to the prompt file (optional).
        chunk_size: The size of chunks (optional).
        cache_key: Key to retrieve cached test cases (optional).

    Returns:
        JSON response containing the generated test cases and a cache key, or an error message.
    """
    try:
        # Check cache first
        if cache_key and cache_key in TEST_CASES_CACHE:
            print(f"Retrieving test cases from cache with key: {cache_key}")
            return JSONResponse(
                content={
                    "test_cases": TEST_CASES_CACHE[cache_key],
                    "cache_key": cache_key,
                }
            )

        # 1. Save the uploaded PDF
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

        # 2. Process the PDF file
        brd_text, _ = data_ingestion.load_pdf_text(str(file_path))  # Pass string path
        if not brd_text:
            raise HTTPException(status_code=500, detail="Failed to load PDF text.")
        cleaned_brd_text = data_ingestion.clean_text(brd_text)

        # Load prompt and chunk size or use defaults
        prompt = prompt_file_path if prompt_file_path else PROMPT_FILE_PATH
        chunk = chunk_size if chunk_size else DEFAULT_CHUNK_SIZE

        # 3. Chunk the cleaned BRD text
        chunks = split_text_into_chunks(cleaned_brd_text, chunk)

        # 4. Iterate through the chunks and generate test cases
        all_test_cases = []
        for i, chunk in enumerate(chunks):
            print(f"Processing Chunk {i+1}/{len(chunks)}")
            test_cases_text = test_case_utils.generate_test_cases(
                chunk,
                together_ai.generate_with_together,
                prompt,
            )

            if test_cases_text:
                all_test_cases.append(test_cases_text)
            else:
                print(f"Failed to generate test cases for chunk {i+1}.")

        # 5. Combine all test cases
        combined_test_cases = "\n".join(all_test_cases)

        # 6. Save the generated test cases to a text file
        output_file_name = (
            f"{Path(file_name).stem}_test_cases.txt"  # Use stem for name w/o extension
        )
        output_file_path = Path(OUTPUT_DIR) / output_file_name

        try:
            with open(output_file_path, "w") as f:
                f.write(combined_test_cases)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error saving test cases: {str(e)}"
            )

        # 7. Store the generated test cases in the cache
        if not cache_key:
            cache_key = str(uuid.uuid4())

        TEST_CASES_CACHE[cache_key] = combined_test_cases
        print(f"Storing test cases in cache with key: {cache_key}")

        return JSONResponse(
            content={"test_cases": combined_test_cases, "cache_key": cache_key}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

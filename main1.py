import os
from utils import data_ingestion, test_case_utils
from utils.llms import together_ai, openai
from convert_to_csv import parse_test_cases, write_to_csv
from dotenv import load_dotenv
import re

load_dotenv()

# Configuration
PDF_FILE_PATH = os.getenv("PDF_FILE_PATH")
PROMPT_FILE_PATH = os.getenv("PROMPT_FILE_PATH")
# OUTPUT_FILE_PATH = "test_cases_brd.txt"  # Path to the output text file
# output_file_CSV = "test_cases.csv"  # Path to the output CSV file


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


if __name__ == "__main__":
    # 1. Load and Clean PDF
    brd_text, _ = data_ingestion.load_pdf_text(PDF_FILE_PATH)
    if not brd_text:
        print("Failed to load BRD text.")
        exit()
    cleaned_brd_text = data_ingestion.clean_text(brd_text)

    # 2. Chunk the BRD
    chunks = split_text_into_chunks(cleaned_brd_text)

    # 3. Iterate through the chunks and generate test cases for each
    all_test_cases = []
    for i, chunk in enumerate(chunks):
        print(f"Processing Chunk {i+1}/{len(chunks)}")

        # 4. Generate Test Cases for the current chunk
        test_cases_text = test_case_utils.generate_test_cases(
            chunk,
            together_ai.generate_with_together,
            PROMPT_FILE_PATH,  # Same prompt for all chunks
        )

        if test_cases_text:
            all_test_cases.append(test_cases_text)
        else:
            print(f"Failed to generate test cases for chunk {i+1}.")

    # 5. Combine all test cases (JSON format now)
    combined_test_cases = "\n".join(all_test_cases)

    print(combined_test_cases)

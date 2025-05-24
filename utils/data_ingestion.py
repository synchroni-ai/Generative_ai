import fitz  # PyMuPDF
import time
import tiktoken

#sdaegd
def load_pdf_text(pdf_path):
    """
    Loads a PDF from the given path, extracts the text, and returns it.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A string containing the extracted text from the PDF.
    """
    try:
        start_time = time.time()
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        end_time = time.time()
        processing_time = end_time - start_time

        return text, processing_time
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None, None


def clean_text(text):
    """
    Cleans the extracted text by removing unnecessary whitespace and special characters.

    Args:
        text: The text to clean.

    Returns:
        The cleaned text.  (Add more cleaning logic as needed)
    """
    text = text.strip()
    # Add any other cleaning steps here (e.g., removing specific characters)
    return text


def count_tokens(text, encoding_name="cl100k_base"):
    """
    Counts the number of tokens in a text string using the specified tiktoken encoding.

    Args:
        text: The text to count tokens in.
        encoding_name: The name of the tiktoken encoding to use (default: "cl100k_base").
                        Other common encodings include:
                         - "gpt2"
                         - "p50k_base"
    Returns:
        The number of tokens in the text.  Returns None if there is an encoding error.
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return None


def store_processed_text(cleaned_text, num_tokens, processing_time, metadata=None):
    """
    Stores the cleaned text and its associated metadata.

    Args:
        cleaned_text: The cleaned text.
        num_tokens: The number of tokens in the cleaned text.
        processing_time: The time taken to process the PDF.
        metadata: An optional dictionary to store additional metadata.

    Returns:
        A dictionary containing the cleaned text and its metadata.
    """
    stored_data = {
        "cleaned_text": cleaned_text,
        "num_tokens": num_tokens,
        "processing_time": processing_time,
        "metadata": metadata or {},  # Ensure metadata is a dictionary
    }
    return stored_data

from pathlib import Path
 
def extract_text_from_file(file_path: str) -> str:

    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":

        from PyPDF2 import PdfReader

        with open(file_path, "rb") as f:

            reader = PdfReader(f)

            return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif ext in [".docx"]:

        from docx import Document

        doc = Document(file_path)

        return "\n".join(para.text for para in doc.paragraphs)

    else:

        # Try reading as text

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:

            return f.read()

import re
def parse_test_case_block(case_str):
    """
    Parse a single test case string into a dictionary of fields.
    Supports both "**Field:**" and "Field:" style.
    """
    # Fields to extract
    fields = [
        'TCID', 'Test type', 'Title', 'Description', 'Precondition', 'Steps',
        'Action', 'Data', 'Result', 'Test Nature', 'Test priority'
    ]
    result = {f: '' for f in fields}
    
    # Normalize formatting (handle both **Field:** and Field:)
    for f in fields:
        # Regex matches e.g. "**Title:** ..." or "Title: ..."
        match = re.search(rf"(\*\*)?{re.escape(f)}(\*\*)?:\s*(.*?)(?=\n[A-Z][^:\n]*:|\n\*\*[A-Z][^:]*\*\*:|\Z)", case_str, re.DOTALL)
        if match:
            value = match.group(3).strip()
            result[f] = value
    return result

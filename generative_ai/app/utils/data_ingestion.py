import fitz  # PyMuPDF
import time
import tiktoken
from io import BytesIO
from PyPDF2 import PdfReader
import traceback

import boto3
import tempfile
import os

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

def download_file_from_s3(s3_url: str) -> str:
    """
    Downloads a file from S3 given its S3 URL and returns the local path.
    """
    from urllib.parse import urlparse

    parsed = urlparse(s3_url)
    bucket_name = parsed.netloc
    key = parsed.path.lstrip('/')

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(key)[-1])
    temp_file.close()  # Close the file so boto3 can write into it

    # Download the file
    s3_client.download_file(bucket_name, key, temp_file.name)

    return temp_file.name


def load_pdf_text_from_bytes(pdf_data, password=None):
    """
    Extracts text from a PDF file given its content as bytes.

    Args:
        pdf_data (bytes): The PDF file content as bytes.
        password (str, optional): The password for the PDF, if it's encrypted. Defaults to None.

    Returns:
        str: The extracted text from the PDF, or None if extraction fails.
    """
    try:
        pdf_file = BytesIO(pdf_data)
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            if password:
                try:
                    reader.decrypt(password)
                except Exception as e:
                    print(f"Decryption failed with provided password: {e}")
                    print(traceback.format_exc())
                    return None
            else:
                print("PDF is encrypted but no password provided.")
                return None  # or raise an exception

        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF bytes: {e}")
        print(traceback.format_exc())
        return None

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

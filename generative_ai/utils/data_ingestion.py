import fitz  # PyMuPDF
import time
import tiktoken


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

import os
import tempfile
import boto3
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION_NAME")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


def fetch_document_text_from_s3_url(s3_url: str) -> str:
    """
    Downloads a file from an S3 URL (e.g., s3://bucket/key) and extracts text.
    """
    parsed = urlparse(s3_url)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    _, ext = os.path.splitext(key)
    ext = ext.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        s3_client.download_fileobj(bucket, key, tmp)
        tmp_path = tmp.name

    try:
        if ext == ".txt":
            return _extract_txt(tmp_path)
        elif ext == ".pdf":
            return _extract_pdf(tmp_path)
        elif ext == ".docx":
            return _extract_docx(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    finally:
        os.remove(tmp_path)


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_pdf(path: str) -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    text = "\n".join([page.get_text() for page in doc])
    doc.close()
    return text


def _extract_docx(path: str) -> str:
    import docx

    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

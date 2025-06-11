from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from pathlib import Path
import shutil
import re
import io
import pdfplumber
import docx
import fitz  # PyMuPDF
import nltk
import spacy
import dateutil.parser
from rake_nltk import Rake
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLP assets
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

# NLP models and utilities
rake = Rake()
sbert = SentenceTransformer("all-MiniLM-L6-v2")
stop_words = set(nltk.corpus.stopwords.words("english"))

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download

    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# App and upload path
app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Taxonomy
TAXONOMY = {
    "Legal": ["agreement", "clause", "party", "contract", "nda"],
    "HR Policy": ["leave", "policy", "vacation", "employee", "benefits"],
    "Invoice": ["invoice", "total", "amount", "due", "bill"],
    "Meeting Note": ["minutes", "attendees", "discussion", "action items"],
    "Proposal": ["proposal", "solution", "services", "quote"],
    "Report": ["report", "summary", "annual", "metrics"],
    "JD": ["job description", "responsibilities", "skills", "qualifications"],
    "Manual": ["instructions", "troubleshooting", "usage", "guide"],
    "Research": ["abstract", "methodology", "conclusion", "study"],
    "Press Release": ["announcement", "launch", "press", "statement"],
}


# # Pydantic Response Model
# class DateItem(BaseModel):
#     date: str


class TagResponse(BaseModel):
    filename: str
    document_type: str
    taxonomy: List[str]
    date: str


# File Reading Utilities
def extract_text_from_file(path: Path) -> str:
    if path.suffix == ".pdf":
        with pdfplumber.open(path) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    elif path.suffix == ".docx":
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""


# Text NLP Utilities
def extract_date(text: str) -> str:
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{1,2},?\s*\d{4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return "Not Found"


# def extract_dates_with_labels(text: str) -> List[DateItem]:
#     found_dates = []
#     patterns = [
#         r"\b(?:on|dated|as of|until|valid until|from|to)\s+([A-Za-z0-9,\-/ ]+)",
#         r"\b(?:effective|expires|start|end)\s+(?:date\s*)?([A-Za-z0-9,\-/ ]+)",
#     ]
#     for pattern in patterns:
#         for match in re.finditer(pattern, text, flags=re.I):
#             full_text = match.group(0)
#             date_str = match.group(1)
#             try:
#                 parsed_date = dateutil.parser.parse(date_str, fuzzy=True)
#                 iso_date = parsed_date.date().isoformat()
#                 label_match = re.search(
#                     r"(on|dated|until|effective|expires|start|end)",
#                     full_text,
#                     flags=re.I,
#                 )
#                 label = label_match.group(0).title() if label_match else "Date"
#                 found_dates.append(
#                     DateItem(text=full_text.strip(), date=iso_date, label=label)
#                 )
#             except Exception:
#                 continue
#     return found_dates


def extract_keywords_rake(text, min_words=2, max_words=3):
    rake.extract_keywords_from_text(text)
    phrases = rake.get_ranked_phrases()
    return [p for p in phrases if min_words <= len(p.split()) <= max_words]


def classify_type(keywords: List[str]) -> str:
    for label, vocab in TAXONOMY.items():
        if any(term.lower() in phrase.lower() for phrase in keywords for term in vocab):
            return label
    return "Unknown"


def extract_noun_phrases(text: str) -> List[str]:
    doc = nlp(text)
    phrases = set()
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        words = phrase.split()
        if 2 <= len(words) <= 3:
            cleaned = " ".join([w for w in words if w.lower() not in stop_words])
            if len(cleaned.split()) >= 2:
                if not re.search(r"\b\d{3,}\b|@|\.(com|net|org)", cleaned, re.I):
                    phrases.add(cleaned.lower())
    return list(phrases)


def rank_phrases_by_similarity(
    phrases: List[str], doc_text: str, top_n: int = 3
) -> List[str]:
    if not phrases:
        return []
    phrase_embeddings = sbert.encode(phrases, convert_to_tensor=True)
    doc_embedding = sbert.encode(doc_text, convert_to_tensor=True)
    sims = cosine_similarity(
        phrase_embeddings.cpu().numpy(), doc_embedding.unsqueeze(0).cpu().numpy()
    ).flatten()
    ranked = sorted(zip(phrases, sims), key=lambda x: x[1], reverse=True)
    final_phrases = []
    seen = set()
    for phrase, _ in ranked:
        title_phrase = phrase.title().strip()
        if title_phrase not in seen:
            seen.add(title_phrase)
            final_phrases.append(title_phrase)
        if len(final_phrases) >= top_n:
            break
    return final_phrases


def refine_taxonomy_with_sbert(tags: List[str], similarity_threshold=0.8) -> List[str]:
    if not tags:
        return []
    tag_embeddings = sbert.encode(tags, convert_to_tensor=True).cpu().numpy()
    used = set()
    refined_tags = []
    for i, tag in enumerate(tags):
        if i in used:
            continue
        group = [tag]
        used.add(i)
        for j in range(i + 1, len(tags)):
            if j in used:
                continue
            sim = cosine_similarity([tag_embeddings[i]], [tag_embeddings[j]])[0][0]
            if sim >= similarity_threshold:
                group.append(tags[j])
                used.add(j)
        representative = min(group, key=lambda x: len(x))
        refined_tags.append(representative.title().strip())
    return refined_tags


# === FastAPI Endpoint ===
@app.post("/process/combined/", response_model=TagResponse)
async def process_combined(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        text = extract_text_from_file(file_path)
        if not text:
            raise ValueError("Document contains no readable text.")

        # RAKE + SBERT classification
        rake_keywords = extract_keywords_rake(text)
        document_type = classify_type(rake_keywords)

        # SpaCy + SBERT taxonomy
        noun_phrases = extract_noun_phrases(text)
        ranked_tags = rank_phrases_by_similarity(noun_phrases, text)
        refined_tags = refine_taxonomy_with_sbert(ranked_tags)

        # Date extraction
        date = extract_date(text)
        return TagResponse(
            filename=file.filename,
            document_type=document_type,
            taxonomy=refined_tags,
            date=date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path.exists():
            file_path.unlink()

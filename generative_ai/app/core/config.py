# app/core/config.py

import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import datetime

# Load environment variables from .env file (ensure this is called)
load_dotenv()


# --- Timezone Configuration ---
IST = ZoneInfo("Asia/Kolkata")


def get_ist_now():
    return datetime.datetime.now(IST)


# # Add collection names here
# USERS_COLLECTION_NAME: str = os.getenv('USERS_COLLECTION_NAME','users')
# DATASPACE_COLLECTION_NAME: str = os.getenv('DATASPACE_COLLECTION_NAME', 'dataspaces') 
# DOCUMENT_COLLECTION_NAME: str = os.getenv('DOCUMENT_COLLECTION_NAME', 'documents') 
# CONFIG_COLLECTION_NAME: str = os.getenv('DOCUMENT_COLLECTION_NAME', 'configs') 
# TESTCASES_COLLECTION_NAME: str=os.getenv('TESTCASES_COLLECTION_NAME','testcases')

# --- App Configuration ---
SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_if_not_set")
ALGORITHM: str = os.getenv(
    "ALGORITHM", "HS256"
)  # Load JWT algorithm from env or use default
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
# --- MongoDB Configuration ---
MONGO_URI: str | None = os.getenv("MONGO_URI")
MONGO_DB_NAME: str | None = os.getenv("MONGO_DB_NAME")

# --- S3 Configuration ---
AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME: str | None = os.getenv("AWS_REGION_NAME")
S3_BUCKET_NAME: str | None = os.getenv("S3_BUCKET_NAME")

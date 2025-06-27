import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import datetime
from typing import Optional

# Load environment variables from a .env file
load_dotenv()

# --- Timezone Configuration ---
IST = ZoneInfo("Asia/Kolkata")

def get_ist_now() -> datetime.datetime:
    return datetime.datetime.now(IST)

# --- JWT Configuration ---
SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_if_not_set")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Safe default to 10080 (7 days) if eval fails
try:
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(eval(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "60 * 24 * 7")))
except Exception:
    REFRESH_TOKEN_EXPIRE_MINUTES = 10080

from typing import Optional  # Keep this at the top of your config.py

# --- MongoDB Configuration ---
MONGO_URI: Optional[str] = os.getenv("MONGO_URI")
MONGO_DB_NAME: Optional[str]= os.getenv("MONGO_DB_NAME")


# --- AWS S3 Configuration ---
AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME: Optional[str] = os.getenv("AWS_REGION_NAME")
S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")

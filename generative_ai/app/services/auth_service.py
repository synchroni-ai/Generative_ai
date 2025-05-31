# app/services/auth_service.py

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from motor.core import AgnosticDatabase  # Import AgnosticDatabase
from beanie import PydanticObjectId  # Import PydanticObjectId

# Import config settings
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_ist_now,
)

# Import User model
from app.models import User  # <-- Import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = get_ist_now() + expires_delta
    else:
        expire = get_ist_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_by_username(username: str, db: AgnosticDatabase) -> Optional[User]:
    """Fetches a user by username from the database using Beanie."""
    # Beanie uses find_one directly on the Document class
    user = await User.find_one({"username": username})
    return user


async def create_user(
    username: str, hashed_password: str, db: AgnosticDatabase
) -> User:
    """Creates a new user in the database using Beanie."""
    user = User(username=username, hashed_password=hashed_password)
    await user.insert()  # Insert the new user document
    return user


async def get_user_from_token(token: str, db: AgnosticDatabase) -> Optional[User]:
    """
    Decodes a JWT token, validates it, and fetches the corresponding user.
    Returns the User document or None if invalid/user not found.
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract the subject (username)
        username: str = payload.get("sub")
        if username is None:
            return None  # Token did not contain a subject
        # Fetch the user from the database
        user = await get_user_by_username(username, db)  # Use the function we defined
        return user
    except JWTError:
        # Token is invalid or expired
        return None


async def update_user_password(
    username: str, new_hashed_password: str, db: AgnosticDatabase
) -> bool:
    """Updates a user's password in the database using Beanie."""
    user = await get_user_by_username(username, db)
    if user:
        user.hashed_password = new_hashed_password
        # Beanie's save updates the existing document
        await user.save()
        return True
    return False


async def get_user_by_id(
    user_id: PydanticObjectId, db: AgnosticDatabase
) -> Optional[User]:
    """Fetches a user by ID from the database using Beanie."""
    user = await User.get(user_id)  # Beanie's get by ID
    return user

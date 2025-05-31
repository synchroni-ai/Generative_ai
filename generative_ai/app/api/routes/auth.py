# app/api/routes/auth.py

from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel
from beanie import PydanticObjectId  # <-- ADD THIS IMPORT for PydanticObjectId
from datetime import timedelta  # <-- ADD THIS IMPORT for timedelta used in token expiry

from app.services import auth_service  # Import the service module
from app.db.mongodb import get_db  # Import the DB dependency
from app.models import (
    User,
)  # <-- ADD THIS IMPORT because deps.get_current_user returns a User object

# Import your shared dependency to get the current user
from app.api import deps  # <-- Import deps to use deps.get_current_user

from motor.core import AgnosticDatabase  # Import AgnosticDatabase for type hint


# Assuming UserRegister, UserLogin, etc. are Pydantic Models (not Beanie Documents)
# If they are in app.models, import them from there instead of defining here
class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    username: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


router = APIRouter()

# Routes


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserRegister, db: AgnosticDatabase = Depends(get_db)
):  # Add type hint
    """Registers a new user."""
    db_user = await auth_service.get_user_by_username(user.username, db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_pw = auth_service.hash_password(user.password)
    await auth_service.create_user(user.username, hashed_pw, db)
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(
    user: UserLogin, db: AgnosticDatabase = Depends(get_db)
):  # Add type hint
    """Logs in a user and returns an access token."""
    db_user = await auth_service.get_user_by_username(user.username, db)
    # Assuming auth_service.verify_password correctly takes plain and hashed passwords
    # If db_user is a Beanie model, access hashed_password like db_user.hashed_password
    if not db_user or not auth_service.verify_password(
        user.password, db_user.hashed_password
    ):  # Use dot notation if db_user is Beanie model
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        # expires_delta is set in config by default, can be overridden here if needed
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Example of a protected route using the dependency
@router.get("/protected")
async def protected_route(
    # Use the standard get_current_user dependency defined in deps.py
    # It returns the User model object
    current_user: User = Depends(
        deps.get_current_user
    ),  # <-- CORRECTED DEPENDENCY USAGE
    db: AgnosticDatabase = Depends(get_db),  # Add type hint
):
    """Example of a protected route."""
    # The `current_user` object is already the authenticated User document
    # You can access its attributes directly, e.g., current_user.id or current_user.username
    return {
        "message": f"Hello {current_user.username}! Your user ID is {current_user.id}. You are authenticated."
    }


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest, db: AgnosticDatabase = Depends(get_db)
):  # Add type hint
    """Generates a password reset token."""
    user = await auth_service.get_user_by_username(data.username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    reset_token = auth_service.create_access_token(
        data={"sub": data.username},
        expires_delta=timedelta(
            minutes=15
        ),  # Use shorter expiry for reset tokens (requires timedelta import)
    )

    # In a real app, you'd send this token via email to the user
    # For demo, returning the token
    return {
        "reset_token": reset_token,
        "message": "Password reset token generated. In a real app, this would be emailed.",
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest, db: AgnosticDatabase = Depends(get_db)
):  # Add type hint
    """Resets user password using a token."""
    # Use the auth service function to validate the token and get the user
    # auth_service.get_user_from_token returns the User document or None
    user_doc = await auth_service.get_user_from_token(data.token, db)

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    # The user_doc is a Beanie model instance, access username with dot notation
    username = user_doc.username

    new_hashed_pw = auth_service.hash_password(data.new_password)
    # Use the auth service function to update the password
    # Assuming update_user_password takes username and new_hashed_password
    success = await auth_service.update_user_password(username, new_hashed_pw, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password in database",
        )

    return {"message": "Password has been reset successfully"}

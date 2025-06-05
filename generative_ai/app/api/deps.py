# app/api/deps.py

from fastapi import Depends, HTTPException, status
from beanie import PydanticObjectId
from fastapi.security import OAuth2PasswordBearer
from motor.core import AgnosticDatabase
from app.db.mongodb import get_db

# Import auth service functions and User model
from app.services import auth_service  # <-- Ensure this is imported
from app.models import Dataspace, User  # <-- Ensure these are imported

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

get_db = get_db  # Re-export the DB dependency


async def get_dataspace_by_id(dataspace_id: PydanticObjectId, db=Depends(get_db)):
    from app.models import (
        Dataspace,
    )  # Import model locally to avoid circular dependency

    dataspace = await Dataspace.get(dataspace_id)
    if not dataspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataspace with ID {dataspace_id} not found",
        )
    return dataspace


async def get_current_user(
    token: str = Depends(oauth2_scheme),  # Get token from Authorization header
    db: AgnosticDatabase = Depends(get_db),  # Get database connection
) -> User:  # Add return type hint
    """
    Dependency to get the current authenticated user based on the JWT token.
    Raises 401 Unauthorized if token is invalid or user not found.
    Returns the User document.
    """
    # The auth_service function handles decoding, verification, and user lookup
    user = await auth_service.get_user_from_token(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

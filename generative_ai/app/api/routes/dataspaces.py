# app/api/routes/dataspaces.py
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from motor.core import AgnosticDatabase  # Import AgnosticDatabase for type hint
from datetime import datetime

from app.models import Dataspace, User ,DataspaceUpdate # Import Dataspace and User model
from app.api import deps  # Import dependencies
import pytz
from app.models import Dataspace, User

router = APIRouter()

def get_ist_now():
    return datetime.now(pytz.timezone("Asia/Kolkata"))



# --- CREATE ---
@router.post("/", response_model=Dataspace, status_code=status.HTTP_201_CREATED)
async def create_dataspace(
    dataspace: Dataspace,
    current_user: User = Depends(deps.get_current_user),  # <-- Add auth dependency
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Creates a new dataspace. Requires authentication.
    """
    # Automatically set created_by to the current authenticated user's ID
    dataspace.created_by = current_user.id

    try:
        await dataspace.insert()
        return dataspace
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataspace with name '{dataspace.name}' already exists.",
        )
    except Exception as e:
        print(f"Error creating dataspace: {e}")  # Log the error server-side
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dataspace.",  # Provide generic error to client
        )


# --- READ (List) ---
@router.get("/", response_model=List[Dataspace])
async def list_dataspaces(
    current_user: User = Depends(deps.get_current_user),  # <-- Add auth dependency
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Lists all available dataspaces. Requires authentication.
    (Optional: Filter by current_user.id if needed)
    """
    try:
        # Example of filtering by user if you want to show only user's dataspaces
        # dataspaces = await Dataspace.find({"created_by": current_user.id}).to_list()
        # To list all for any authenticated user:
        dataspaces = await Dataspace.find_all().to_list()
        return dataspaces
    except Exception as e:
        print(f"Error listing dataspaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list dataspaces.",
        )


# --- READ (Get One) ---
@router.get("/{dataspace_id}", response_model=Dataspace)
async def get_dataspace(
    dataspace: Dataspace = Depends(
        deps.get_dataspace_by_id
    ),  # Dependency fetches and validates existence
    current_user: User = Depends(deps.get_current_user),  # <-- Add auth dependency
    db: AgnosticDatabase = Depends(deps.get_db),  # Add type hint
):
    """
    Gets details of a specific dataspace by ID. Requires authentication.
    (Optional: Add authorization check: if dataspace.created_by != current_user.id raise 403)
    """
    # Example of basic authorization check:
    # if dataspace.created_by != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this dataspace")

    return dataspace  # The dataspace object is already returned by the dependency


# --- UPDATE ---
@router.put("/{dataspace_id}", response_model=Dataspace)
async def update_dataspace(
    dataspace_update: DataspaceUpdate,
    dataspace: Dataspace = Depends(deps.get_dataspace_by_id),
    current_user: User = Depends(deps.get_current_user),
    db: AgnosticDatabase = Depends(deps.get_db),
):
    """
    Updates an existing dataspace by ID. Requires authentication.
    """
    try:
        # Optional: Check for duplicate name if name is being changed
        if (
            dataspace_update.name is not None
            and dataspace_update.name != dataspace.name
        ):
            existing_dataspace = await Dataspace.find_one(
                {"name": dataspace_update.name}
            )
            if existing_dataspace and existing_dataspace.id != dataspace.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Dataspace with name '{dataspace_update.name}' already exists.",
                )

        # Extract only fields that were actually updated in request
        update_data = dataspace_update.model_dump(exclude_unset=True)

        # Set those updated fields into the current dataspace object
        for field_name, value in update_data.items():
            setattr(dataspace, field_name, value)

        # Update the timestamp
        dataspace.updated_at = get_ist_now()

        # Save to DB
        await dataspace.save()

        return dataspace

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataspace with name '{dataspace_update.name}' already exists.",
        )
    except Exception as e:
        print(f"Error updating dataspace {dataspace.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dataspace: {e}",
        )


@router.delete("/{dataspace_id}", status_code=status.HTTP_200_OK)
async def delete_dataspace(
    dataspace: Dataspace = Depends(deps.get_dataspace_by_id),
    current_user: User = Depends(deps.get_current_user),
    db=Depends(deps.get_db),
):
    """
    Deletes a dataspace by ID and returns a message including its name.
    """
    try:
        name = dataspace.name  # Get the name before deleting
        await dataspace.delete()
        return {"message": f"Dataspace '{name}' deleted successfully"}
    except Exception as e:
        print(f"Error deleting dataspace {dataspace.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataspace: {e}",
        )
#dataspace
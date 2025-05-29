# app/api/routes/dataspaces.py
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError # Import DuplicateKeyError

from app.models import Dataspace # Import Dataspace model
from app.api import deps # Import dependencies

router = APIRouter()

# Helper Pydantic model for updating dataspace (allows partial updates)
# We use Dataspace as the base and make fields optional
# Note: _id is immutable and doesn't need to be included in update
class DataspaceUpdate(Dataspace):
    name: Optional[str] = None # Allow updating name
    description: Optional[str] = None
    # created_by and created_at are typically not updated via API
    created_by: Optional[PydanticObjectId] = None # Still Optional, but won't be updated by Beanie's save
    created_at: Optional[datetime.datetime] = None # Still Optional, but won't be updated by Beanie's save
    category: Optional[str] = None
    sub_category: Optional[str] = None

    class Settings:
        keep_nulls = False # Do not save fields that are explicitly set to null in the request body
        use_revision = False # Disable revision tracking for update model


# --- CREATE ---
@router.post("/", response_model=Dataspace, status_code=status.HTTP_201_CREATED)
async def create_dataspace(
    dataspace: Dataspace, # Beanie model handles validation
    db=Depends(deps.get_db) # Dependency ensures DB is connected
):
    """
    Creates a new dataspace.
    Expects JSON body matching Dataspace model (name, description, category, sub_category).
    Dataspace names must be unique.
    """
    # dataspace.created_at = get_ist_now() # Default handles this

    try:
        # Insert the new document
        await dataspace.insert()
        return dataspace
    except DuplicateKeyError:
        # Catch the specific error for unique index violation
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataspace with name '{dataspace.name}' already exists."
        )
    except Exception as e:
        # Catch other potential database errors
        print(f"Error creating dataspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dataspace: {e}"
        )

# --- READ (List) ---
@router.get("/", response_model=List[Dataspace])
async def list_dataspaces(db=Depends(deps.get_db)):
    """
    Lists all available dataspaces.
    """
    try:
        dataspaces = await Dataspace.find_all().to_list()
        return dataspaces
    except Exception as e:
         print(f"Error listing dataspaces: {e}")
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=f"Failed to list dataspaces: {e}"
         )

# --- READ (Get One) ---
# Using the get_dataspace_by_id dependency for cleaner lookup
@router.get("/{dataspace_id}", response_model=Dataspace)
async def get_dataspace(
    dataspace: Dataspace = Depends(deps.get_dataspace_by_id) # Dependency fetches and validates existence
):
    """
    Gets details of a specific dataspace by ID.
    """
    # The dataspace object is already returned by the dependency
    return dataspace


# --- UPDATE ---
@router.put("/{dataspace_id}", response_model=Dataspace)
async def update_dataspace(
    dataspace_update: DataspaceUpdate, # Use the Update model for request body
    dataspace: Dataspace = Depends(deps.get_dataspace_by_id), # Get the existing dataspace via dependency
    db=Depends(deps.get_db) # Ensure DB is connected
):
    """
    Updates an existing dataspace by ID.
    Expects JSON body with fields to update (name, description, category, sub_category).
    Dataspace names must remain unique after update.
    """
    # Apply the updates from the request body to the existing dataspace object
    # Beanie's save method allows partial updates by default
    try:
        # Check for duplicate name ONLY if the name is being updated
        if dataspace_update.name is not None and dataspace_update.name != dataspace.name:
             existing_dataspace = await Dataspace.find_one({"name": dataspace_update.name})
             if existing_dataspace and existing_dataspace.id != dataspace.id:
                 raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Dataspace with name '{dataspace_update.name}' already exists."
                 )

        # Update the fields using Beanie's update method (or manual assignment)
        # Beanie's Pydantic compatibility makes this easy
        # This approach updates only provided fields
        await dataspace.update(dataspace_update) # <-- Beanie's method to apply updates

        # Alternative manual update if you prefer:
        # update_data = dataspace_update.model_dump(exclude_unset=True) # Use model_dump
        # for key, value in update_data.items():
        #     setattr(dataspace, key, value)
        # await dataspace.save() # <-- Save the changes

        return dataspace # Return the updated dataspace object

    except DuplicateKeyError:
         # Although we checked above, catching here is a fallback if concurrent requests occur
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataspace with name '{dataspace_update.name}' already exists."
         )
    except Exception as e:
        print(f"Error updating dataspace {dataspace.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dataspace: {e}"
        )

# --- DELETE ---
@router.delete("/{dataspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataspace(
    dataspace: Dataspace = Depends(deps.get_dataspace_by_id), # Get the dataspace via dependency
    db=Depends(deps.get_db) # Ensure DB is connected
):
    """
    Deletes a dataspace by ID.
    Returns 204 No Content on success.
    Note: This currently does NOT delete associated documents or S3 files.
          Implement cascade delete logic in a service or signal handler if needed.
    """
    try:
        # Beanie's delete method
        await dataspace.delete()
        # No content is returned for 204
        print(f"Dataspace deleted successfully")

    except Exception as e:
        print(f"Error deleting dataspace {dataspace.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataspace: {e}"
        )
# app/api/__init__.py

from fastapi import APIRouter

from .routes import dataspaces, documents # Import your route files
# Import other route files as you create them
# from .routes import auth, configs, jobs, results

api_router = APIRouter()

api_router.include_router(dataspaces.router, prefix="/dataspaces", tags=["dataspaces"])
api_router.include_router(documents.router, tags=["documents"])


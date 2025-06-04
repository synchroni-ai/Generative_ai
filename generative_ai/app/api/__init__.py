# app/api/__init__.py

from fastapi import APIRouter

from .routes import (
    dataspaces,
    documents,
    test_generation,
    auth,
    configs,
    tagging,
)  # Import your route files

# Import other route files as you create them
# from .routes import auth, configs, jobs, results

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dataspaces.router, prefix="/dataspaces", tags=["dataspaces"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(test_generation.router, tags=["test_generation"])
api_router.include_router(configs.router, tags=["Multi-document Configs"])
api_router.include_router(test_generation.router, tags=["Test Case Generation"])
api_router.include_router(tagging.router, tags=["Document Tagging"])

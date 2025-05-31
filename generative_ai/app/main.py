# app/main.py

from fastapi import FastAPI

from app.api import api_router  # Import the combined router
from app.db.mongodb import connect_db, close_db  # Import DB connection functions
from app.api.routes import documents, configs, test_generation


app = FastAPI(
    title="GenAI Project API",
    description="Endpoints for Dataspace and Document management",
)


# Add the database connection and disconnection to the startup/shutdown events
@app.on_event("startup")
async def startup_event():
    await connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db()


# Include the main API router
app.include_router(api_router, prefix="/api/v1")  # Optional: Add a version prefix
app.include_router(documents.router)
app.include_router(configs.router)
app.include_router(test_generation.router)


# Basic root endpoint (optional)
@app.get("/")
async def read_root():
    return {
        "message": "GenAI Project API is running. Access /api/v1/docs for documentation."
    }

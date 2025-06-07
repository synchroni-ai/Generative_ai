from typing import List,   Dict, Any    

from pydantic import BaseModel
from datetime import datetime
import logging
from fastapi import Path
from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.tasks.test_generation import run_test_generation
from celery.result import AsyncResult
from celery import current_app as celery_app
from typing import Optional

from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import TestResult,User
from app.api import deps  # Import the shared dependency for user authentication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class VersionInfo(BaseModel):
    test_case_count: int
    generated_at: datetime
    document_id: str


@router.post("/generation/run/{config_id}")
async def run_generation_task(config_id: str,current_user: User = Depends(deps.get_current_user)
 ):
    task = run_test_generation.delay(config_id)
    return {"job_id": task.id, "status": "queued"}


@router.get("/generation/status/{job_id}")
def get_job_status(job_id: str,current_user: User = Depends(deps.get_current_user)
 ):
    task = run_test_generation.AsyncResult(job_id)
    return {"job_id": job_id, "status": task.status}


@router.post("/generation/cancel/{job_id}")
async def cancel_generation_job(job_id: str,current_user: User = Depends(deps.get_current_user)
 ):
    result = AsyncResult(job_id, app=celery_app)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    if result.state in ["PENDING", "RECEIVED", "STARTED"]:
        result.revoke(terminate=True)
        return {"job_id": job_id, "status": "canceled"}
    else:
        return {
            "job_id": job_id,
            "status": f"cannot cancel, job is in terminal state: {result.state}",
        }


@router.get("/results/{config_id}/versions", response_model=List[VersionInfo])
async def get_document_versions(config_id: str, db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user)
 ):
    """
    Retrieves the versions of test case generations for a given config ID.
    """
    logger.info(f"Fetching versions for config_id: {config_id}")
    try:
        # Query generative_ai.test_case_grouped_results collection
        jobs = await db["test_case_grouped_results"].find({"config_id": config_id}).to_list(length=None)

        if not jobs:
            logger.warning(f"No test case generations found for config_id: {config_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test case generations found for config ID: {config_id}",
            )

        results = []
        for job in jobs:
            logger.info(f"Processing job: {job['_id']}")

            num_test_cases = 0
            if "summary" in job and "documents" in job["summary"]:
                num_test_cases = len(job["summary"]["documents"])
            generated_at = job.get("generated_at", datetime.now())

            if "summary" in job and "documents" in job["summary"]:
                for document_id in job["summary"]["documents"]:
                    version_info = VersionInfo(
                        test_case_count=num_test_cases,
                        generated_at=generated_at,
                        document_id=str(document_id),
                    )
                    results.append(version_info)

        if not results:
            logger.warning(f"No VersionInfo objects created for config_id: {config_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test case generations found for config ID: {config_id}",
            )

        logger.info(
            f"Successfully retrieved versions for config_id: {config_id}, found {len(results)} versions"
        )
        return results
    except Exception as e:
        logger.error(
            f"An error occurred while retrieving versions for config_id: {config_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}"
        )


# @router.get("/results/{job_id}", response_model=TestResult)
# async def get_test_results(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
#     """
#     Retrieves the test case generation results for a given job ID.
#     """
#     logger.info(f"Fetching results for job_id: {job_id}")
#     try:
#         # Query generative_ai.test_case_grouped_results collection
#         job = await db["test_case_grouped_results"].find_one({"job_id": job_id})

#         if not job:
#             logger.warning(f"No test case generation found for job_id: {job_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No test case generation found for job ID: {job_id}",
#             )

#         # Convert ObjectId in _id to string if needed (optional)
#         job["_id"] = str(job["_id"])

#         test_result = TestResult(
#             config_id=job["config_id"],
#             llm_model=job.get("llm_model"),
#             temperature=job.get("temperature"),
#             use_case=job.get("use_case"),
#             generated_at=job.get("generated_at"),
#             results=job.get("results"),
#             status=job["status"],
#             summary=job["summary"],
#         )

#         logger.info(f"Successfully retrieved results for job_id: {job_id}")
#         return test_result
#     except HTTPException as http_exception:
#         raise http_exception
#     except Exception as e:
#         logger.error(f"An error occurred while retrieving results for job_id: {job_id}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {e}",
#         )
    
# @router.get("/results/{job_id}", response_model=TestResult)
# async def get_test_results(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
#     """
#     Retrieves the test case generation results for a given job ID.
#     """
#     logger.info(f"Fetching results for job_id: {job_id}")
#     try:
#         # Query generative_ai.test_case_grouped_results collection
#         job = await db["test_case_grouped_results"].find_one({"job_id": job_id})

#         if not job:
#             logger.warning(f"No test case generation found for job_id: {job_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No test case generation found for job ID: {job_id}",
#             )

#         # Convert ObjectId in _id to string if needed (optional)
#         job["_id"] = str(job["_id"])

#         test_result = TestResult(
#             config_id=job["config_id"],
#             llm_model=job.get("llm_model"),
#             temperature=job.get("temperature"),
#             use_case=job.get("use_case"),
#             generated_at=job.get("generated_at"),
#             results=job.get("results"),
#             status=job["status"],
#             summary=job["summary"],
#         )

#         logger.info(f"Successfully retrieved results for job_id: {job_id}")
#         return test_result
#     except HTTPException as http_exception:
#         raise http_exception
#     except Exception as e:
#         logger.error(f"An error occurred while retrieving results for job_id: {job_id}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {e}",
#         )
    


@router.get("/results/{job_id}", response_model=TestResult)
async def get_test_results(
    job_id: str,
    subtype: Optional[str] = Query(None, description="Subtype to filter test cases by"),
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get test generation results for a job, optionally filtered by subtype.
    """
    try:
        # Fetch the job result document from DB
        job = await db["test_case_grouped_results"].find_one({"job_id": job_id})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test case generation found for job ID: {job_id}",
            )

        results = job.get("results", {})

        # Prepare document ID mapping to fetch file names
        document_ids = list(results.get("documents", {}).keys())
        object_ids = [ObjectId(doc_id) for doc_id in document_ids if ObjectId.is_valid(doc_id)]

        # Use try-except block here too, to handle potential database errors
        try:
            documents_cursor = db["documents"].find(
                {"_id": {"$in": object_ids}},
                {"file_name": 1}
            )
            document_info = {
                str(doc["_id"]): doc["file_name"]
                async for doc in documents_cursor
            }
        except Exception as e:
            logging.error(f"Error fetching document information from database: {e}")
            document_info = {}  # Safe fallback


        # Insert document names into results["documents"]
        if "documents" in results:
            for doc_id, data in results["documents"].items():
                if isinstance(data, dict):
                    data["document_name"] = document_info.get(doc_id, "Unknown")  # Use dict.get


        # Insert document names into results["all_documents"] if present
        if "all_documents" in results:
            for section, section_docs in results["all_documents"].items():
                for doc_id, doc_data in section_docs.items():
                    doc_name = document_info.get(doc_id, "Unknown")

                    if isinstance(doc_data, str):
                         results["all_documents"][section][doc_id] = {
                             "content": doc_data,
                             "document_name": doc_name
                         }
                    elif isinstance(doc_data, list):
                        results["all_documents"][section][doc_id] = {
                            "content": doc_data,
                            "document_name": doc_name
                        }
                    elif isinstance(doc_data, dict):
                         doc_data["document_name"] = doc_name


        # Handle subtype filter if requested
        filtered_results: Dict[str, Any] = {}
        if subtype:
            filtered_results["documents"] = {}
            for doc_id, data in results.get("documents", {}).items():
                if isinstance(data, dict) and subtype in data:
                   filtered_results["documents"][doc_id] = {
                        "document_name": data.get("document_name", document_info.get(doc_id, "Unknown")),
                        subtype: data[subtype]  # subtype data
                    }

            if "all_documents" in results:
               filtered_results["all_documents"] = {}
               for section, section_docs in results["all_documents"].items():
                    filtered_results["all_documents"][section] = {}

                    for doc_id, doc_data in section_docs.items():
                        if isinstance(doc_data, dict) and doc_data.get("content"):
                            filtered_results["all_documents"][section][doc_id] = {
                                "document_name": doc_data.get("document_name"),
                                "content": doc_data["content"]
                            }
        else:
            filtered_results = results

        # Construct response model
        try:
            test_result = TestResult(
                config_id=job.get("config_id"),
                llm_model=job.get("llm_model"),
                temperature=job.get("temperature"),
                use_case=job.get("use_case", []),
                generated_at=job.get("generated_at"),
                results=filtered_results,
                status=job.get("status"),
                summary=job.get("summary", {}),
            )
        except Exception as e:
            logging.error(f"Error building response: {e}, job data: {job}")
            raise HTTPException(status_code=500, detail=f"Error building response: {str(e)}")

        return test_result

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions without modification
        raise http_exc
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")  # Use logging.exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )

@router.get("/results/documents/{document_id}")
async def get_document_by_id(
    document_id: str = Path(..., description="The ObjectId of the document"),
    db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user)
 
):
    """
    Retrieves a specific document from the nested `results.documents` field
    in the `test_case_grouped_results` collection by document_id.
    """
    logger.info(f"Fetching document with document_id: {document_id}")
    try:
        # Query the collection to find the document_id inside `results.documents`
        job = await db["test_case_grouped_results"].find_one(
            {f"results.documents.{document_id}": {"$exists": True}}
        )

        if not job:
            logger.warning(f"No document found with document_id: {document_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No document found with document_id: {document_id}",
            )

        # Retrieve the specific document content
        document_content = job["results"]["documents"].get(document_id)

        if not document_content:
            logger.warning(f"Document with document_id: {document_id} is empty or missing")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with document_id: {document_id} is empty or missing",
            )

        # Return the document content
        logger.info(f"Successfully retrieved document for document_id: {document_id}")
        return {
            "document_id": document_id,
            "job_id": job.get("job_id"),
            "config_id": job.get("config_id"),
            "document_content": document_content,
        }

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(
            f"An error occurred while retrieving document for document_id: {document_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )

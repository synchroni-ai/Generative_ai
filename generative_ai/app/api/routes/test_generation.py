# # import sys
# # import os

# # # Add the root directory to Python path
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# # from app.models import VersionInfo      

# # from fastapi import APIRouter, HTTPException, Depends, status
# # from app.tasks.test_generation import run_test_generation
# # from celery.result import AsyncResult
# # from celery import current_app as celery_app
# # from typing import List
# # from pydantic import BaseModel
# # from datetime import datetime
# # import logging
# # import re

# # from app.db.mongodb import get_db  # Import the DB dependency
# # from motor.motor_asyncio import AsyncIOMotorDatabase
# # from bson import ObjectId

# # # Configure logging (optional, but helpful)
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)


# # router = APIRouter()


# # @router.post("/generation/run/{config_id}")
# # async def run_generation_task(config_id: str):
# #     task = run_test_generation.delay(config_id)
# #     return {"job_id": task.id, "status": "queued"}


# # @router.get("/generation/status/{job_id}")
# # def get_job_status(job_id: str):
# #     task = run_test_generation.AsyncResult(job_id)
# #     return {"job_id": job_id, "status": task.status}


# # @router.post("/generation/cancel/{job_id}")
# # async def cancel_generation_job(job_id: str):
# #     result = AsyncResult(job_id, app=celery_app)

# #     if not result:
# #         raise HTTPException(status_code=404, detail="Job not found")

# #     if result.state in ["PENDING", "RECEIVED", "STARTED"]:
# #         result.revoke(terminate=True)
# #         return {"job_id": job_id, "status": "canceled"}
# #     else:
# #         return {
# #             "job_id": job_id,
# #             "status": f"cannot cancel, job is in terminal state: {result.state}",
# #         }




# # @router.get("/results/{config_id}/versions", response_model=List[VersionInfo])
# # async def get_document_versions(config_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
# #     logger.info(f"🟡 Fetching versions for config_id: {config_id}")

# #     try:
# #         logger.info("🟡 Attempting to fetch job from database...")
# #         job = await db["test_case_grouped_results"].find_one({"config_id": config_id})
# #         logger.info(f"🔍 Job retrieved: {job}")

# #         if not job:
# #             logger.warning(f"❌ No job found for config_id: {config_id}")
# #             raise HTTPException(
# #                 status_code=404,
# #                 detail=f"No test case generations found for config ID: {config_id}",
# #             )

# #         results = []
# #         documents = job.get("results", {}).get("documents", {})
# #         logger.info(f"🔍 Documents found: {documents}")  # New Log
# #         generated_at = job.get("generated_at")
# #         logger.info(f"🔍 Generated_at found: {generated_at}")

# #         for doc_id, subtype_data in documents.items():
# #             logger.info(f"🔍 Processing doc_id: {doc_id}")  # New Log
# #             total_test_cases = 0
# #             for subtype, test_case_string in subtype_data.items():
# #                 logger.info(f"🔍 Processing subtype: {subtype}")  # New Log
# #                 if isinstance(test_case_string, str):
# #                     # Split the string by "TCID:" to count test cases
# #                     test_cases = re.split(r"TCID:", test_case_string)
# #                     # The first element will be empty, so start from the second
# #                     total_test_cases += len(test_cases) - 1
# #                 elif isinstance(test_case_string, list):
# #                   total_test_cases += len(test_case_string)
# #                 else:
# #                     logger.warning(f"Unexpected data type for subtype {subtype}: {type(test_case_string)}")
            
# #             version_info = VersionInfo(
# #                 document_id=doc_id,
# #                 generated_at=generated_at,
# #                 test_case_count=total_test_cases
# #             )
# #             results.append(version_info)

# #         logger.info(f"✅ Returning {len(results)} version(s)")
# #         return results

# #     except Exception as e:
# #         logger.exception("🔥 Error retrieving document versions")
# #         raise HTTPException(status_code=500, detail=str(e))

# from typing import List

# from pydantic import BaseModel
# from datetime import datetime
# import logging

# from fastapi import APIRouter, HTTPException, Depends, status
# from app.tasks.test_generation import run_test_generation
# from celery.result import AsyncResult
# from celery import current_app as celery_app

# from app.db.mongodb import get_db
# from motor.motor_asyncio import AsyncIOMotorDatabase
# from bson import ObjectId
# from app.models import TestResult, VersionInfo
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()


# class VersionInfo(BaseModel):
#     test_case_count: int
#     generated_at: datetime
#     document_id: str


# @router.post("/generation/run/{config_id}")
# async def run_generation_task(config_id: str):
#     task = run_test_generation.delay(config_id)
#     return {"job_id": task.id, "status": "queued"}


# @router.get("/generation/status/{job_id}")
# def get_job_status(job_id: str):
#     task = run_test_generation.AsyncResult(job_id)
#     return {"job_id": job_id, "status": task.status}


# @router.post("/generation/cancel/{job_id}")
# async def cancel_generation_job(job_id: str):
#     result = AsyncResult(job_id, app=celery_app)
#     if not result:
#         raise HTTPException(status_code=404, detail="Job not found")
#     if result.state in ["PENDING", "RECEIVED", "STARTED"]:
#         result.revoke(terminate=True)
#         return {"job_id": job_id, "status": "canceled"}
#     else:
#         return {
#             "job_id": job_id,
#             "status": f"cannot cancel, job is in terminal state: {result.state}",
#         }


# @router.get("/results/{config_id}/versions", response_model=List[VersionInfo])
# async def get_document_versions(config_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
#     """
#     Retrieves the versions of test case generations for a given config ID.
#     """
#     logger.info(f"Fetching versions for config_id: {config_id}")
#     try:
#         # Query test_case_db.jobs collection, since that's where your data is
#         jobs = await db["test_case_db"]["jobs"].find({"config_id": config_id}).to_list(length=None)

#         if not jobs:
#             logger.warning(f"No test case generations found for config_id: {config_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No test case generations found for config ID: {config_id}",
#             )

#         results = []
#         for job in jobs:
#             logger.info(f"Processing job: {job['_id']}")

#             # Extract relevant data and create a VersionInfo object
#             num_test_cases = 0
#             if "summary" in job and "documents" in job["summary"]:
#                 num_test_cases = len(job["summary"]["documents"])
#                 logger.info(f"Number of test cases: {num_test_cases}")
#             else:
#                 logger.warning("Summary or documents field missing in job")

#             generated_at = job.get("generated_at", datetime.now())  # Use .get() for safety
#             logger.info(f"Generated at: {generated_at}")

#             # Append results for each document_id
#             if "summary" in job and "documents" in job["summary"]:
#                 for document_id_obj in job["summary"]["documents"]:
#                     document_id = str(document_id_obj)  # Convert ObjectId to string
#                     logger.info(f"Creating VersionInfo for document_id: {document_id}")

#                     version_info = VersionInfo(
#                         test_case_count=num_test_cases,  # Number of test cases
#                         generated_at=generated_at,  # Or how ever you determine the timestamp
#                         document_id=document_id,
#                     )
#                     results.append(version_info)
#                     logger.info(f"Added version info: {version_info}")
#             else:
#                 logger.warning("Summary or documents field missing in job")

#         if not results:
#             logger.warning(f"No VersionInfo objects created for config_id: {config_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No test case generations found for config ID: {config_id}",
#             )

#         logger.info(
#             f"Successfully retrieved versions for config_id: {config_id}, found {len(results)} versions"
#         )
#         return results
#     except Exception as e:
#         logger.error(
#             f"An error occurred while retrieving versions for config_id: {config_id}: {e}",
#             exc_info=True,
#         )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}"
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
#         # Re-raise HTTPExceptions to preserve their status code
#         raise http_exception
#     except Exception as e:
#         logger.error(f"An error occurred while retrieving results for job_id: {job_id}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {e}",
#         )
from typing import List

from pydantic import BaseModel
from datetime import datetime
import logging
from fastapi import Path
from fastapi import APIRouter, HTTPException, Depends, status
from app.tasks.test_generation import run_test_generation
from celery.result import AsyncResult
from celery import current_app as celery_app

from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models import TestResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class VersionInfo(BaseModel):
    test_case_count: int
    generated_at: datetime
    document_id: str


@router.post("/generation/run/{config_id}")
async def run_generation_task(config_id: str):
    task = run_test_generation.delay(config_id)
    return {"job_id": task.id, "status": "queued"}


@router.get("/generation/status/{job_id}")
def get_job_status(job_id: str):
    task = run_test_generation.AsyncResult(job_id)
    return {"job_id": job_id, "status": task.status}


@router.post("/generation/cancel/{job_id}")
async def cancel_generation_job(job_id: str):
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
async def get_document_versions(config_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
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


@router.get("/results/{job_id}", response_model=TestResult)
async def get_test_results(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Retrieves the test case generation results for a given job ID.
    """
    logger.info(f"Fetching results for job_id: {job_id}")
    try:
        # Query generative_ai.test_case_grouped_results collection
        job = await db["test_case_grouped_results"].find_one({"job_id": job_id})

        if not job:
            logger.warning(f"No test case generation found for job_id: {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test case generation found for job ID: {job_id}",
            )

        # Convert ObjectId in _id to string if needed (optional)
        job["_id"] = str(job["_id"])

        test_result = TestResult(
            config_id=job["config_id"],
            llm_model=job.get("llm_model"),
            temperature=job.get("temperature"),
            use_case=job.get("use_case"),
            generated_at=job.get("generated_at"),
            results=job.get("results"),
            status=job["status"],
            summary=job["summary"],
        )

        logger.info(f"Successfully retrieved results for job_id: {job_id}")
        return test_result
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(f"An error occurred while retrieving results for job_id: {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )
    
@router.get("/results/{job_id}", response_model=TestResult)
async def get_test_results(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Retrieves the test case generation results for a given job ID.
    """
    logger.info(f"Fetching results for job_id: {job_id}")
    try:
        # Query generative_ai.test_case_grouped_results collection
        job = await db["test_case_grouped_results"].find_one({"job_id": job_id})

        if not job:
            logger.warning(f"No test case generation found for job_id: {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test case generation found for job ID: {job_id}",
            )

        # Convert ObjectId in _id to string if needed (optional)
        job["_id"] = str(job["_id"])

        test_result = TestResult(
            config_id=job["config_id"],
            llm_model=job.get("llm_model"),
            temperature=job.get("temperature"),
            use_case=job.get("use_case"),
            generated_at=job.get("generated_at"),
            results=job.get("results"),
            status=job["status"],
            summary=job["summary"],
        )

        logger.info(f"Successfully retrieved results for job_id: {job_id}")
        return test_result
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.error(f"An error occurred while retrieving results for job_id: {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )
    



@router.get("/results/documents/{document_id}")
async def get_document_by_id(
    document_id: str = Path(..., description="The ObjectId of the document"),
    db: AsyncIOMotorDatabase = Depends(get_db),
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

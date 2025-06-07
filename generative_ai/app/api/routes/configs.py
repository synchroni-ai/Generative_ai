from fastapi import APIRouter, HTTPException, Depends
from app.models import ConfigModel, MultiDocumentConfigModel,User
from app.services.config_service import save_config, get_config_by_document_id
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.api import deps
router = APIRouter()
import datetime
from datetime import datetime, timedelta
from typing import Dict
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from typing import Optional, Literal
@router.post("/documents/{document_id}/config")
async def save_document_config(
    document_id: str, config: ConfigModel, db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user)
):
    success = await save_config(document_id, config, db)
    if not success:
        raise HTTPException(
            status_code=404, detail="Document not found or update failed"
        )
    return {"message": "Config saved successfully"}


@router.get("/documents/{document_id}/config")
async def get_document_config(
    document_id: str, db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user)
):
    config = await get_config_by_document_id(document_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"config": config}

#modified
@router.post("/configs")
async def save_multi_document_config(
    config_data: MultiDocumentConfigModel,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Validate document IDs
    valid_document_ids = []
    for doc_id in config_data.documents:
        try:
            obj_id = ObjectId(doc_id)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid ObjectId format: {doc_id}")
        
        document = await db["documents"].find_one({"_id": obj_id})
        if not document:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
        
        valid_document_ids.append(obj_id)

    # Proceed to save config with validated document ObjectIds
    config_doc = {
        "documents": valid_document_ids,
        "config": config_data.config.dict(),
        "created_by": config_data.created_by,
        "created_at": config_data.created_at or datetime.utcnow(),
    }

    result = await db["configurations"].insert_one(config_doc)

    return {
        "message": "Configuration saved",
        "config_id": str(result.inserted_id),
        "created_at": config_doc["created_at"],
    }



@router.get("/configs")
async def list_all_configs(
    db: AsyncIOMotorDatabase = Depends(get_db),current_user: User = Depends(deps.get_current_user),
):
    """
    Returns a list of all configurations with minimal metadata: config_id and created_at.
    """
    configs_cursor = db["configurations"].find({})
    configs = []
    async for config in configs_cursor:
        configs.append({
            "config_id": str(config["_id"]),
            "created_at": config.get("created_at")
        })

    return {"configs": configs}


@router.get("/configs/{config_id}")
async def get_config_by_id(
    config_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Gets a configuration by its ID. Requires authentication.
    """
    config = await db["configurations"].find_one({"_id": ObjectId(config_id)})
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    # Remove fields you don't want to expose
    config.pop("created_by", None)
    config.pop("created_at", None)

    # Convert ObjectId fields to strings
    config["_id"] = str(config["_id"])
    config["documents"] = [str(doc_id) for doc_id in config.get("documents", [])]

    print(f"User {current_user.username} (ID: {current_user.id}) retrieved config by ID: {config_id}")
    return {"config": config}

# @router.get("/history")
# async def get_test_case_history(
#     db: AsyncIOMotorDatabase = Depends(get_db),
#     current_user: User = Depends(deps.get_current_user),
# ):
#     """
#     Fetches test case generation history for all documents, including document name.
#     """
#     result_cursor = db["test_case_grouped_results"].find({})
#     document_collection = db["documents"]

#     history = []

#     async for record in result_cursor:
#         generated_at = record.get("generated_at")
#         documents = record.get("results", {}).get("documents", {})

#         for doc_id, doc_result in documents.items():
#             testcases = doc_result.get("all_subtypes", [])
#             test_case_count = len(testcases)

#             # Fetch document metadata
#             document_data = await document_collection.find_one({"_id": ObjectId(doc_id)})
#             file_name = document_data.get("file_name") if document_data else "Unknown"

#             history.append({
#                 "document_id": doc_id,
#                 "document_name": file_name,
#                 "test_case_count": test_case_count,
#                 "testcases": testcases,
#                 "generated_at": generated_at,
#             })

#     if not history:
#         raise HTTPException(status_code=404, detail="No test case history found.")

#     return {"history": history}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from fastapi.responses import JSONResponse

@router.get("/history/summary")
async def get_test_case_history_summary(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    time_range: Optional[Literal["today", "yesterday", "last_7_days", "last_month"]] = Query(None, description="Time range to filter by."),
):
    """
    Fetches a summary of test case generation history, filtered by a specified time range.
    Handles potential data inconsistencies in the 'test_case_grouped_results' collection.
    """

    query = {}
    now = datetime.utcnow()

    if time_range == "today":
        start_of_today = datetime(now.year, now.month, now.day)
        query["generated_at"] = {"$gte": start_of_today, "$lt": now}

    elif time_range == "yesterday":
        yesterday = now - timedelta(days=1)
        start_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day)
        end_of_yesterday = datetime(now.year, now.month, now.day) - timedelta(microseconds=1)
        query["generated_at"] = {"$gte": start_of_yesterday, "$lt": end_of_yesterday}

    elif time_range == "last_7_days":
        seven_days_ago = now - timedelta(days=7)
        query["generated_at"] = {"$gte": seven_days_ago, "$lt": now}

    elif time_range == "last_month":
        last_month = now.month - 1 if now.month > 1 else 12
        last_year = now.year - 1 if now.month == 1 else now.year
        first_day_of_last_month = datetime(last_year, last_month, 1)
        first_day_of_this_month = datetime(now.year, now.month, 1)
        query["generated_at"] = {"$gte": first_day_of_last_month, "$lt": first_day_of_this_month}

    elif time_range is not None:
        raise HTTPException(status_code=400, detail="Invalid time_range value. Must be 'today', 'yesterday', 'last_7_days', or 'last_month'.")

    result_cursor = db["test_case_grouped_results"].find(query)
    document_collection = db["documents"]

    history = []

    async for record in result_cursor:
        generated_at = record.get("generated_at")
        results = record.get("results")

        if not isinstance(results, dict):
            logger.warning(f"Skipping record with invalid 'results' format (not a dict): {record.get('_id', 'Unknown ID')}")
            continue

        documents = results.get("documents", {})
        if not isinstance(documents, dict):
            logger.warning(f"Skipping record with invalid 'documents' format (not a dict): {record.get('_id', 'Unknown ID')}")
            continue

        for doc_id, doc_result in documents.items():
            try:
                document_data = await document_collection.find_one({"_id": ObjectId(doc_id)})
            except Exception as e:
                logger.error(f"Error fetching document {doc_id}: {e}")
                continue

            file_name = document_data.get("file_name") if document_data else "Unknown"

            history.append({
                "document_id": doc_id,
                "document_name": file_name,
                "generated_at": generated_at,
            })

    # Fallback only for 'last_month'
    if time_range == "last_month" and not history:
        logger.info("No data found for last_month range. Falling back to all available history.")
        fallback_cursor = db["test_case_grouped_results"].find({})
        async for record in fallback_cursor:
            generated_at = record.get("generated_at")
            results = record.get("results", {})
            if not isinstance(results, dict):
                continue

            documents = results.get("documents", {})
            if not isinstance(documents, dict):
                continue

            for doc_id, doc_result in documents.items():
                try:
                    document_data = await document_collection.find_one({"_id": ObjectId(doc_id)})
                except Exception as e:
                    logger.error(f"Error fetching document {doc_id}: {e}")
                    continue

                file_name = document_data.get("file_name") if document_data else "Unknown"

                history.append({
                    "document_id": doc_id,
                    "document_name": file_name,
                    "generated_at": generated_at,
                })

    return {"history": history}


# @router.get("/history/document/{document_id}")
# async def get_test_cases_by_document(
#     document_id: str,
#     db: AsyncIOMotorDatabase = Depends(get_db),
#     current_user: User = Depends(deps.get_current_user),
# ):
#     """
#     Fetches detailed test case information for a specific document ID.
#     """
#     try:
#         doc_id = ObjectId(document_id)
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid document_id format. Must be a valid ObjectId string.")

#     result = await db["test_case_grouped_results"].find_one({"results.documents." + document_id: {"$exists": True}})

#     if not result:
#         raise HTTPException(status_code=404, detail="No test case history found for this document.")

#     generated_at = result.get("generated_at")
#     results = result.get("results", {}) #added default for cases if results is not defined

#     if not isinstance(results, dict):  # check if results is a dict
#         raise HTTPException(status_code=500, detail="Data Inconsistency: 'results' is not a dictionary.")

#     documents = results.get("documents", {})

#     if not isinstance(documents, dict):  # check if documents is a dict
#         raise HTTPException(status_code=500, detail="Data Inconsistency: 'documents' is not a dictionary.")

#     document_data = documents.get(document_id)

#     if not document_data:
#         raise HTTPException(status_code=404, detail="No test case details found for this document in results.")


#     testcases = document_data.get("all_subtypes", [])
#     test_case_count = len(testcases)

#     # Fetch document metadata
#     document_collection = db["documents"]
#     document = await document_collection.find_one({"_id": doc_id})
#     file_name = document.get("file_name") if document else "Unknown"


#     return {
#         "document_id": document_id,
#         "document_name": file_name,
#         "test_case_count": test_case_count,
#         "testcases": testcases,
#         "generated_at": generated_at,
#     }

@router.get("/history/document/{document_id}")
async def get_test_cases_by_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Fetches detailed test case information for a specific document ID and returns the response
    in the desired nested format.
    """
    try:
        doc_id = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document_id format. Must be a valid ObjectId string.")

    # Fetch data from test_case_grouped_results
    result = await db["test_case_grouped_results"].find_one({"results.documents." + document_id: {"$exists": True}})

    if not result:
        raise HTTPException(status_code=404, detail="No test case history found for this document.")

    # Extract relevant information from the result
    config_id = result.get("config_id")
    llm_model = result.get("llm_model")
    temperature = result.get("temperature")
    use_case = result.get("use_case")
    generated_at = result.get("generated_at")
    results = result.get("results", {})

    if not isinstance(results, dict):
        raise HTTPException(status_code=500, detail="Data Inconsistency: 'results' is not a dictionary.")

    documents = results.get("documents", {})

    if not isinstance(documents, dict):
        raise HTTPException(status_code=500, detail="Data Inconsistency: 'documents' is not a dictionary.")

    document_data = documents.get(document_id)

    if not document_data:
        raise HTTPException(status_code=404, detail="No test case details found for this document in results.")

    # Prepare the response in the specified format
    response_data = {
        "config_id": config_id,
        "llm_model": llm_model,
        "temperature": temperature,
        "use_case": use_case,
        "generated_at": generated_at,
        "results": {
            "documents": {
                document_id: document_data
            },
        },
        "status": "completed",  # Or based on actual status logic
        "summary": {
            "documents": [document_id],
            "subtypes": ["functional"]  # Or dynamically generated based on the actual subtypes
        }
    }

    # Fetch document name and add it to the `document_data`
    document_collection = db["documents"]
    document = await document_collection.find_one({"_id": doc_id})
    file_name = document.get("file_name") if document else "Unknown"

    response_data["results"]["documents"][document_id]["document_name"] = file_name


    #Add all_documents
    content = document_data.get("functional")

    response_data["results"]["all_documents"] = {
        "functional" : {document_id:{"content": content, "document_name": file_name}},
        "Final_subtypes" : {document_id:{"content": document_data.get("all_subtypes"), "document_name": file_name}},
    }

    return response_data
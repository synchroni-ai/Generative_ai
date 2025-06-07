# # # # import sys
# # # # import os

# # # # # Add the parent directory to sys.path so imports work
# # # # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# # # # from prompts import load_prompt
# # # # from data_ingestion.data_ingestion import fetch_document_text_from_s3_url
# # # # from llms.mistral import call_mistral
# # # # from llms.gpt4 import call_gpt4
# # # # from pymongo import MongoClient
# # # # from bson import ObjectId
# # # # import uuid
# # # # from dotenv import load_dotenv
# # # # from app.models import DocumentStatusEnum


# # # # # Load all prompt templates once
# # # # PROMPT_MAP = {
# # # #     "boundary": load_prompt("boundary"),
# # # #     "compliance": load_prompt("compliance"),
# # # #     "security": load_prompt("security"),
# # # #     "performance": load_prompt("performance"),
# # # #     "functional": load_prompt("functional"),
# # # #     "non_functional": load_prompt("non_functional"),
# # # # }

# # # # # Load prompt for summarizing the document
# # # # SUMMARIZATION_PROMPT = load_prompt("summarization")


# # # # load_dotenv()


# # # # MONGO_URI = os.getenv("MONGO_URI")
# # # # TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# # # # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional

# # # # API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

# # # # MAX_SUMMARY_LENGTH = 1500  # Set your desired maximum summary length in tokens


# # # # def summarize_document(doc_text: str, api_key: str) -> str:
# # # #     """Summarizes the given document text using Mistral."""
# # # #     prompt = SUMMARIZATION_PROMPT.format(document_text=doc_text)
# # # #     summary = call_mistral(prompt, api_key)  # Mistral summarization
# # # #     return summary


# # # # def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
# # # #     """
# # # #     Accepts a full configuration document from the 'configurations' collection.
# # # #     It expects the following structure:
# # # #     {
# # # #         "documents": [...],
# # # #         "config": {
# # # #             "llm_model": "...",
# # # #             "temperature": 0.7,
# # # #             "use_case": [...],
# # # #             "subtypes": [...]
# # # #         },
# # # #         ...
# # # #     }
# # # #     """
# # # #     client = MongoClient(mongo_uri)
# # # #     doc_db = client["generative_ai"]["documents"]
# # # #     result_db = client["generative_ai"]["test_case_grouped_results"]

# # # #     document_ids = config.get("documents", [])
# # # #     inner_config = config.get("config", {})

# # # #     llm_model = inner_config.get("llm_model", "").lower()
# # # #     subtypes = inner_config.get("subtypes", [])
# # # #     temperature = inner_config.get("temperature", 0.7)
# # # #     use_case = inner_config.get("use_case", [])
# # # #     config_id = str(config.get("_id", uuid.uuid4()))
# # # #     generated_at = inner_config.get("created_at")

# # # #     # Initialize the final result object
# # # #     full_result = {
# # # #         "config_id": config_id,
# # # #         "llm_model": llm_model,
# # # #         "temperature": temperature,
# # # #         "use_case": use_case,
# # # #         "generated_at": generated_at,
# # # #         "results": {
# # # #             "documents": {},
# # # #             "all_documents": {s: {} for s in subtypes} | {"Final_subtypes": {}},  # Changed here
# # # #         },
# # # #     }

# # # #     for doc_id in document_ids:
# # # #         doc = doc_db.find_one({"_id": ObjectId(doc_id)})
# # # #         if not doc or "s3_url" not in doc:
# # # #             print(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
# # # #             continue

# # # #         doc_text = fetch_document_text_from_s3_url(doc["s3_url"])

# # # #         # Summarize document if the model is OpenAI.  Always summarize.
# # # #         summary = summarize_document(doc_text, api_keys["together_ai"])  # Use Mistral for summarization
# # # #         print(f"Summary: {summary}") #Print the summary
# # # #         doc_text = summary #Update doc_text with summary

# # # #         doc_results = {}
# # # #         all_subtypes_results = []

# # # #         for subtype in subtypes:
# # # #             subtype_key = subtype.lower()
# # # #             if subtype_key not in PROMPT_MAP:
# # # #                 print(f"⚠️ Skipping unsupported subtype: {subtype}")
# # # #                 continue

# # # #             prompt_template = PROMPT_MAP[subtype_key]
# # # #             prompt = prompt_template.format(brd_text=doc_text)

# # # #             if llm_model == "mistral":
# # # #                 output = call_mistral(prompt, api_keys["together_ai"])
# # # #             elif llm_model == "gpt-4":
# # # #                 output = call_gpt4(prompt, api_keys["openai"])
# # # #             else:
# # # #                 raise ValueError(f"Unsupported LLM model: {llm_model}")

# # # #             # Store by subtype under document
# # # #             doc_results[subtype] = output
# # # #             all_subtypes_results.append(output)

# # # #             # Store under all_documents by subtype
# # # #             full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

# # # #         # Store all results per document
# # # #         full_result["results"]["documents"][str(doc["_id"])] = {
# # # #             **doc_results,
# # # #             "all_subtypes": all_subtypes_results,
# # # #         }

# # # #         # Store under global Final_subtypes (renamed from all_subtypes)
# # # #         full_result["results"]["all_documents"]["Final_subtypes"][   # Changed here to final_subtypes
# # # #             str(doc["_id"])
# # # #         ] = all_subtypes_results
        
# # # #         # Update document status to PROCESSING (1) *after* successful test case generation
# # # #         doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": DocumentStatusEnum.PROCESSING.value}})

# # # #     result_db.insert_one(full_result)
# # # #     return full_result


# # # # if __name__ == "__main__":
# # # #     from bson import ObjectId
# # # #     from pymongo import MongoClient

# # # #     load_dotenv()
# # # #     MONGO_URI = os.getenv("MONGO_URI")
# # # #     TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# # # #     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # # #     API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

# # # #     # Replace with your actual config ID to test
# # # #     config_id = "your_config_id_here"

# # # #     client = MongoClient(MONGO_URI)
# # # #     config_doc = client["generative_ai"]["configurations"].find_one(
# # # #         {"_id": ObjectId(config_id)}
# # # #     )

# # # #     if not config_doc:
# # # #         print(f"❌ Config {config_id} not found.")
# # # #     else:
# # # #         result = generate_test_cases(config_doc, MONGO_URI, API_KEYS)
# # # #         print(result)

# # # import sys
# # # import os

# # # # Add the parent directory to sys.path so imports work
# # # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# # # from prompts import load_prompt
# # # from data_ingestion.data_ingestion import fetch_document_text_from_s3_url
# # # from llms.mistral import call_mistral
# # # from llms.gpt4 import call_gpt4
# # # from pymongo import MongoClient
# # # from bson import ObjectId
# # # import uuid
# # # from dotenv import load_dotenv
# # # from app.models import DocumentStatusEnum


# # # # Load all prompt templates once
# # # PROMPT_MAP = {
# # #     "boundary": load_prompt("boundary"),
# # #     "compliance": load_prompt("compliance"),
# # #     "security": load_prompt("security"),
# # #     "performance": load_prompt("performance"),
# # #     "functional": load_prompt("functional"),
# # #     "non_functional": load_prompt("non_functional"),
# # # }

# # # # Load prompt for summarizing the document
# # # SUMMARIZATION_PROMPT = load_prompt("summarization")


# # # load_dotenv()


# # # MONGO_URI = os.getenv("MONGO_URI")
# # # TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# # # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional

# # # API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

# # # MAX_SUMMARY_LENGTH = 1500  # Set your desired maximum summary length in tokens


# # # def summarize_document(doc_text: str, api_key: str) -> str:
# # #     """Summarizes the given document text using Mistral."""
# # #     prompt = SUMMARIZATION_PROMPT.format(document_text=doc_text)
# # #     summary = call_mistral(prompt, api_key)  # Mistral summarization
# # #     return summary


# # # def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
# # #     """
# # #     Accepts a full configuration document from the 'configurations' collection.
# # #     It expects the following structure:
# # #     {
# # #         "documents": [...],
# # #         "config": {
# # #             "llm_model": "...",
# # #             "temperature": 0.7,
# # #             "use_case": [...],
# # #             "subtypes": [...]
# # #         },
# # #         ...
# # #     }
# # #     """
# # #     client = MongoClient(mongo_uri)
# # #     doc_db = client["generative_ai"]["documents"]
# # #     result_db = client["generative_ai"]["test_case_grouped_results"]

# # #     document_ids = config.get("documents", [])
# # #     inner_config = config.get("config", {})

# # #     llm_model = inner_config.get("llm_model", "").lower()
# # #     subtypes = inner_config.get("subtypes", [])
# # #     temperature = inner_config.get("temperature", 0.7)
# # #     use_case = inner_config.get("use_case", [])
# # #     config_id = str(config.get("_id", uuid.uuid4()))
# # #     generated_at = inner_config.get("created_at")

# # #     # Initialize the final result object
# # #     full_result = {
# # #         "config_id": config_id,
# # #         "llm_model": llm_model,
# # #         "temperature": temperature,
# # #         "use_case": use_case,
# # #         "generated_at": generated_at,
# # #         "results": {
# # #             "documents": {},
# # #             "all_documents": {s: {} for s in subtypes} | {"Final_subtypes": {}},  # Changed here
# # #         },
# # #     }

# # #     for doc_id in document_ids:
# # #         doc = doc_db.find_one({"_id": ObjectId(doc_id)})
# # #         if not doc or "s3_url" not in doc:
# # #             print(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
# # #             continue

# # #         doc_text = fetch_document_text_from_s3_url(doc["s3_url"])

# # #         # Summarize document if the model is OpenAI.  Always summarize.
# # #         summary = summarize_document(doc_text, api_keys["together_ai"])  # Use Mistral for summarization
# # #         print(f"Summary: {summary}") #Print the summary
# # #         doc_text = summary #Update doc_text with summary

# # #         doc_results = {}
# # #         all_subtypes_results = []

# # #         for subtype in subtypes:
# # #             subtype_key = subtype.lower()
# # #             if subtype_key not in PROMPT_MAP:
# # #                 print(f"⚠️ Skipping unsupported subtype: {subtype}")
# # #                 continue

# # #             prompt_template = PROMPT_MAP[subtype_key]
# # #             prompt = prompt_template.format(brd_text=doc_text)

# # #             if llm_model == "mistral":
# # #                 output = call_mistral(prompt, api_keys["together_ai"])
# # #             elif llm_model == "gpt-4":
# # #                 output = call_gpt4(prompt, api_keys["openai"])
# # #             else:
# # #                 raise ValueError(f"Unsupported LLM model: {llm_model}")

# # #             # Store by subtype under document
# # #             doc_results[subtype] = output
# # #             all_subtypes_results.append(output)

# # #             # Store under all_documents by subtype
# # #             full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

# # #         # Store all results per document
# # #         full_result["results"]["documents"][str(doc["_id"])] = {
# # #             **doc_results,
# # #             "all_subtypes": all_subtypes_results,
# # #         }

# # #         # Store under global Final_subtypes (renamed from all_subtypes)
# # #         full_result["results"]["all_documents"]["Final_subtypes"][   # Changed here to final_subtypes
# # #             str(doc["_id"])
# # #         ] = all_subtypes_results
        
# # #         # Update document status to PROCESSING (1) *after* successful test case generation
# # #         print(f"DocumentStatusEnum.PROCESSING.value: {DocumentStatusEnum.PROCESSING.value}")
# # #         print(f"Updating document ID: {doc_id}")
# # #         try:
# # #             doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": DocumentStatusEnum.PROCESSING.value}})
# # #             print(f"Successfully updated document {doc_id} to status {DocumentStatusEnum.PROCESSING.value}")
# # #         except Exception as e:
# # #             print(f"Error updating document {doc_id}: {e}")

# # #     result_db.insert_one(full_result)
# # #     return full_result

# # # if __name__ == "__main__":
# # #     from bson import ObjectId
# # #     from pymongo import MongoClient

# # #     load_dotenv()
# # #     MONGO_URI = os.getenv("MONGO_URI")
# # #     TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# # #     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # #     API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

# # #     # Replace with your actual config ID to test
# # #     config_id = "your_config_id_here"

# # #     client = MongoClient(MONGO_URI)
# # #     config_doc = client["generative_ai"]["configurations"].find_one(
# # #         {"_id": ObjectId(config_id)}
# # #     )

# # #     if not config_doc:
# # #         print(f"❌ Config {config_id} not found.")
# # #     else:
# # #         result = generate_test_cases(config_doc, MONGO_URI, API_KEYS)
# # #         print(result)\

# # import sys
# # import os

# # # Add the parent directory to sys.path so imports work
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# # from prompts import load_prompt
# # from data_ingestion.data_ingestion import fetch_document_text_from_s3_url
# # from llms.mistral import call_mistral
# # from llms.gpt4 import call_gpt4
# # from pymongo import MongoClient
# # from bson import ObjectId
# # import uuid
# # from dotenv import load_dotenv
# # from app.models import DocumentStatusEnum


# # # Load all prompt templates once
# # PROMPT_MAP = {
# #     "boundary": load_prompt("boundary"),
# #     "compliance": load_prompt("compliance"),
# #     "security": load_prompt("security"),
# #     "performance": load_prompt("performance"),
# #     "functional": load_prompt("functional"),
# #     "non_functional": load_prompt("non_functional"),
# # }

# # # Load prompt for summarizing the document
# # SUMMARIZATION_PROMPT = load_prompt("summarization")


# # load_dotenv()


# # MONGO_URI = os.getenv("MONGO_URI")
# # TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional

# # API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

# # MAX_SUMMARY_LENGTH = 1500  # Set your desired maximum summary length in tokens


# # def summarize_document(doc_text: str, api_key: str) -> str:
# #     """Summarizes the given document text using Mistral."""
# #     prompt = SUMMARIZATION_PROMPT.format(document_text=doc_text)
# #     summary = call_mistral(prompt, api_key)  # Mistral summarization
# #     return summary


# # def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
# #     """
# #     Accepts a full configuration document from the 'configurations' collection.
# #     It expects the following structure:
# #     {
# #         "documents": [...],
# #         "config": {
# #             "llm_model": "...",
# #             "temperature": 0.7,
# #             "use_case": [...],
# #             "subtypes": [...]
# #         },
# #         ...
# #     }
# #     """
# #     client = MongoClient(mongo_uri)
# #     doc_db = client["generative_ai"]["documents"]
# #     result_db = client["generative_ai"]["test_case_grouped_results"]

# #     document_ids = config.get("documents", [])
# #     inner_config = config.get("config", {})

# #     llm_model = inner_config.get("llm_model", "").lower()
# #     subtypes = inner_config.get("subtypes", [])
# #     temperature = inner_config.get("temperature", 0.7)
# #     use_case = inner_config.get("use_case", [])
# #     config_id = str(config.get("_id", uuid.uuid4()))
# #     generated_at = inner_config.get("created_at")

# #     # Initialize the final result object
# #     full_result = {
# #         "config_id": config_id,
# #         "llm_model": llm_model,
# #         "temperature": temperature,
# #         "use_case": use_case,
# #         "generated_at": generated_at,
# #         "results": {
# #             "documents": {},
# #             "all_documents": {s: {} for s in subtypes} | {"Final_subtypes": {}},  # Changed here
# #         },
# #     }

# #     for doc_id in document_ids:
# #         doc = doc_db.find_one({"_id": ObjectId(doc_id)})
# #         if not doc or "s3_url" not in doc:
# #             print(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
# #             continue

# #         doc_text = fetch_document_text_from_s3_url(doc["s3_url"])

# #         # Summarize document if the model is OpenAI.  Always summarize.
# #         summary = summarize_document(doc_text, api_keys["together_ai"])  # Use Mistral for summarization
# #         print(f"Summary: {summary}") #Print the summary
# #         doc_text = summary #Update doc_text with summary

# #         doc_results = {}
# #         all_subtypes_results = []

# #         for subtype in subtypes:
# #             subtype_key = subtype.lower()
# #             if subtype_key not in PROMPT_MAP:
# #                 print(f"⚠️ Skipping unsupported subtype: {subtype}")
# #                 continue

# #             prompt_template = PROMPT_MAP[subtype_key]
# #             prompt = prompt_template.format(brd_text=doc_text)

# #             if llm_model == "mistral":
# #                 output = call_mistral(prompt, api_keys["together_ai"])
# #             elif llm_model == "gpt-4":
# #                 output = call_gpt4(prompt, api_keys["openai"])
# #             else:
# #                 raise ValueError(f"Unsupported LLM model: {llm_model}")

# #             # Store by subtype under document
# #             doc_results[subtype] = output
# #             all_subtypes_results.append(output)

# #             # Store under all_documents by subtype
# #             full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

# #         # Store all results per document
# #         full_result["results"]["documents"][str(doc["_id"])] = {
# #             **doc_results,
# #             "all_subtypes": all_subtypes_results,
# #         }

# #         # Store under global Final_subtypes (renamed from all_subtypes)
# #         full_result["results"]["all_documents"]["Final_subtypes"][   # Changed here to final_subtypes
# #             str(doc["_id"])
# #         ] = all_subtypes_results
        
# #         # Update document status to PROCESSING (1) *after* successful test case generation
# #         print(f"DocumentStatusEnum.PROCESSING.value: {DocumentStatusEnum.PROCESSING.value}")
# #         print(f"Updating document ID: {doc_id} to PROCESSING(1)")
# #         try:
# #             doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": DocumentStatusEnum.PROCESSING.value}})
# #             print(f"Successfully updated document {doc_id} to status {DocumentStatusEnum.PROCESSING.value}")
# #         except Exception as e:
# #             print(f"Error updating document {doc_id} to PROCESSING(1): {e}")

# #     result_db.insert_one(full_result)
# #     #Update Status to Processed(2) AFTER ALL test cases are generated.
# #     for doc_id in document_ids: # loop through documents and set status to 2
# #       try:
# #           doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": DocumentStatusEnum.PROCESSED.value}})
# #           print(f"Successfully updated document {doc_id} to status {DocumentStatusEnum.PROCESSED.value}")
# #       except Exception as e:
# #           print(f"Error updating document {doc_id} to PROCESSED(2): {e}")

# #     return full_result

# # if __name__ == "__main__":
# #     from bson import ObjectId
# #     from pymongo import MongoClient

# #     load_dotenv()
# #     MONGO_URI = os.getenv("MONGO_URI")
# #     TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# #     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# #     API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

# #     # Replace with your actual config ID to test
# #     config_id = "your_config_id_here"

# #     client = MongoClient(MONGO_URI)
# #     config_doc = client["generative_ai"]["configurations"].find_one(
# #         {"_id": ObjectId(config_id)}
# #     )

# #     if not config_doc:
# #         print(f"❌ Config {config_id} not found.")
# #     else:
# #         result = generate_test_cases(config_doc, MONGO_URI, API_KEYS)
# #         print(result)

# import sys
# import os

# # Add the parent directory to sys.path so imports work
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from prompts import load_prompt
# from data_ingestion.data_ingestion import fetch_document_text_from_s3_url
# from llms.mistral import call_mistral
# from llms.gpt4 import call_gpt4
# from pymongo import MongoClient
# from bson import ObjectId
# import uuid
# from dotenv import load_dotenv
# from app.models import DocumentStatusEnum

# # Load all prompt templates once
# PROMPT_MAP = {
#     "boundary": load_prompt("boundary"),
#     "compliance": load_prompt("compliance"),
#     "security": load_prompt("security"),
#     "performance": load_prompt("performance"),
#     "functional": load_prompt("functional"),
#     "non_functional": load_prompt("non_functional"),
# }

# # Load prompt for summarizing the document
# SUMMARIZATION_PROMPT = load_prompt("summarization")

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI")
# TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}
# MAX_SUMMARY_LENGTH = 1500


# def summarize_document(doc_text: str, api_key: str) -> str:
#     prompt = SUMMARIZATION_PROMPT.format(document_text=doc_text)
#     summary = call_mistral(prompt, api_key)
#     return summary


# def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
#     client = MongoClient(mongo_uri)
#     doc_db = client["generative_ai"]["documents"]
#     result_db = client["generative_ai"]["test_case_grouped_results"]

#     document_ids = config.get("documents", [])
#     inner_config = config.get("config", {})

#     llm_model = inner_config.get("llm_model", "").lower()
#     subtypes = inner_config.get("subtypes", [])
#     temperature = inner_config.get("temperature", 0.7)
#     use_case = inner_config.get("use_case", [])
#     config_id = str(config.get("_id", uuid.uuid4()))
#     generated_at = inner_config.get("created_at")

#     full_result = {
#         "config_id": config_id,
#         "llm_model": llm_model,
#         "temperature": temperature,
#         "use_case": use_case,
#         "generated_at": generated_at,
#         "results": {
#             "documents": {},
#             "all_documents": {s: {} for s in subtypes} | {"Final_subtypes": {}},
#         },
#     }

#     for doc_id in document_ids:
#         doc = doc_db.find_one({"_id": ObjectId(doc_id)})
#         if not doc or "s3_url" not in doc:
#             print(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
#             continue

#         print(f"📄 Processing document: {doc_id}, current status: {doc.get('status')}")

#         doc_text = fetch_document_text_from_s3_url(doc["s3_url"])
#         summary = summarize_document(doc_text, api_keys["together_ai"])
#         print(f"📄 Summary: {summary[:300]}...")  # Print only first 300 chars
#         doc_text = summary

#         doc_results = {}
#         all_subtypes_results = []

#         for subtype in subtypes:
#             subtype_key = subtype.lower()
#             if subtype_key not in PROMPT_MAP:
#                 print(f"⚠️ Skipping unsupported subtype: {subtype}")
#                 continue

#             prompt_template = PROMPT_MAP[subtype_key]
#             prompt = prompt_template.format(brd_text=doc_text)

#             if llm_model == "mistral":
#                 output = call_mistral(prompt, api_keys["together_ai"])
#             elif llm_model == "gpt-4":
#                 output = call_gpt4(prompt, api_keys["openai"])
#             else:
#                 raise ValueError(f"❌ Unsupported LLM model: {llm_model}")

#             doc_results[subtype] = output
#             all_subtypes_results.append(output)

#             full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

#         full_result["results"]["documents"][str(doc["_id"])] = {
#             **doc_results,
#             "all_subtypes": all_subtypes_results,
#         }

#         full_result["results"]["all_documents"]["Final_subtypes"][str(doc["_id"])] = all_subtypes_results

#         # 🔄 Update to PROCESSING (1) after generating test cases
#         print(f"🔁 Attempting to update document ID {doc_id} to PROCESSING (1)")
#         try:
#             result = doc_db.update_one(
#                 {"_id": ObjectId(doc_id)},
#                 {"$set": {"status": DocumentStatusEnum.PROCESSING.value}}
#             )
#             print(f"  ➤ Matched: {result.matched_count}, Modified: {result.modified_count}")
#             if result.matched_count == 0:
#                 print(f"❌ Could not find document {doc_id} in DB.")
#             elif result.modified_count == 0:
#                 print(f"⚠️ Document {doc_id} might already have status 1.")
#             else:
#                 print(f"✅ Successfully updated document {doc_id} to status 1 (PROCESSING)")
#         except Exception as e:
#             print(f"❌ Error updating document {doc_id} to PROCESSING(1): {e}")

#     # 💾 Store test generation results
#     result_db.insert_one(full_result)

#     # ✅ Update all documents to PROCESSED (2) after completion
#     print("✅ All test cases generated. Updating documents to PROCESSED (2).")
#     for doc_id in document_ids:
#         try:
#             result = doc_db.update_one(
#                 {"_id": ObjectId(doc_id)},
#                 {"$set": {"status": DocumentStatusEnum.PROCESSED.value}}
#             )
#             print(f"  ➤ Document {doc_id} updated to status 2 (PROCESSED): Matched={result.matched_count}, Modified={result.modified_count}")
#         except Exception as e:
#             print(f"❌ Error updating document {doc_id} to PROCESSED(2): {e}")

#     return full_result


# if __name__ == "__main__":
#     from bson import ObjectId
#     from pymongo import MongoClient

#     load_dotenv()
#     MONGO_URI = os.getenv("MONGO_URI")
#     TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}

#     # Replace with your actual config ID
#     config_id = "your_config_id_here"

#     client = MongoClient(MONGO_URI)
#     config_doc = client["generative_ai"]["configurations"].find_one(
#         {"_id": ObjectId(config_id)}
#     )

#     if not config_doc:
#         print(f"❌ Config {config_id} not found.")
#     else:
#         result = generate_test_cases(config_doc, MONGO_URI, API_KEYS)
#         print(result)

import sys
import os

# Add the parent directory to sys.path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompts import load_prompt
from data_ingestion.data_ingestion import fetch_document_text_from_s3_url
from llms.mistral import call_mistral
from llms.gpt4 import call_gpt4
from pymongo import MongoClient
from bson import ObjectId
import uuid
from dotenv import load_dotenv
from app.models import DocumentStatusEnum

# Load all prompt templates once
PROMPT_MAP = {
    "boundary": load_prompt("boundary"),
    "compliance": load_prompt("compliance"),
    "security": load_prompt("security"),
    "performance": load_prompt("performance"),
    "functional": load_prompt("functional"),
    "non_functional": load_prompt("non_functional"),
}

# Load prompt for summarizing the document
SUMMARIZATION_PROMPT = load_prompt("summarization")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional

API_KEYS = {"together_ai": TOGETHER_API_KEY, "openai": OPENAI_API_KEY or ""}
MAX_SUMMARY_LENGTH = 1500  # Max summary length in tokens


def summarize_document(doc_text: str, api_key: str) -> str:
    """Summarizes the given document text using Mistral."""
    prompt = SUMMARIZATION_PROMPT.format(document_text=doc_text)
    summary = call_mistral(prompt, api_key)  # Mistral summarization
    return summary


def generate_test_cases(config: dict, mongo_uri: str, api_keys: dict):
    from app.models import DocumentStatusEnum  # Ensure this import is present
    client = MongoClient(mongo_uri)
    doc_db = client["generative_ai"]["documents"]
    result_db = client["generative_ai"]["test_case_grouped_results"]

    document_ids = config.get("documents", [])
    inner_config = config.get("config", {})

    llm_model = inner_config.get("llm_model", "").lower()
    subtypes = inner_config.get("subtypes", [])
    temperature = inner_config.get("temperature", 0.7)
    use_case = inner_config.get("use_case", [])
    config_id = str(config.get("_id", uuid.uuid4()))
    generated_at = inner_config.get("created_at")

    full_result = {
        "config_id": config_id,
        "llm_model": llm_model,
        "temperature": temperature,
        "use_case": use_case,
        "generated_at": generated_at,
        "results": {
            "documents": {},
            "all_documents": {s: {} for s in subtypes} | {"Final_subtypes": {}},
        },
    }

    for doc_id in document_ids:
        doc = doc_db.find_one({"_id": ObjectId(doc_id)})
        if not doc or "s3_url" not in doc:
            print(f"⚠️ Skipping document {doc_id}: not found or missing s3_url")
            continue

        # Fetch text and summarize
        doc_text = fetch_document_text_from_s3_url(doc["s3_url"])
        summary = summarize_document(doc_text, api_keys["together_ai"])
        print(f"Summary: {summary}")
        doc_text = summary

        # Update to PROCESSING (1)
        try:
            doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": DocumentStatusEnum.PROCESSING.value}})
            print(f"✅ Updated document {doc_id} to PROCESSING (1)")
        except Exception as e:
            print(f"❌ Error updating document {doc_id} to PROCESSING(1): {e}")

        doc_results = {}
        all_subtypes_results = []

        for subtype in subtypes:
            subtype_key = subtype.lower()
            if subtype_key not in PROMPT_MAP:
                print(f"⚠️ Skipping unsupported subtype: {subtype}")
                continue

            prompt_template = PROMPT_MAP[subtype_key]
            prompt = prompt_template.format(brd_text=doc_text)

            try:
                if llm_model == "mistral":
                    output = call_mistral(prompt, api_keys["together_ai"])
                elif llm_model == "gpt-4":
                    output = call_gpt4(prompt, api_keys["openai"])
                else:
                    raise ValueError(f"Unsupported LLM model: {llm_model}")
            except Exception as e:
                print(f"❌ Error generating test case for {subtype} in document {doc_id}: {e}")
                continue

            doc_results[subtype] = output
            all_subtypes_results.append(output)

            full_result["results"]["all_documents"][subtype][str(doc["_id"])] = output

        # Store final result per document
        full_result["results"]["documents"][str(doc["_id"])] = {
            **doc_results,
            "all_subtypes": all_subtypes_results,
        }

        full_result["results"]["all_documents"]["Final_subtypes"][str(doc["_id"])] = all_subtypes_results

    # Insert full result to DB
    result_db.insert_one(full_result)

    # FINAL STATUS UPDATE
    EXPECTED_SUBTYPES = {"boundary", "compliance", "security", "performance", "functional", "non_functional"}

    for doc_id in document_ids:
        doc_result = full_result["results"]["documents"].get(str(doc_id), {})
        generated_subtypes = set(doc_result.keys()) - {"all_subtypes"}  # Remove non-subtype keys

        if generated_subtypes == EXPECTED_SUBTYPES:
            new_status = DocumentStatusEnum.COMPLETE.value
            print(f"✅ Document {doc_id} has all 6 subtypes. Setting to COMPLETE (3)")
        else:
            new_status = DocumentStatusEnum.PROCESSED.value
            print(f"ℹ️ Document {doc_id} incomplete. Setting to PROCESSED (2)")

        try:
            doc_db.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": new_status}})
            print(f"🔁 Document {doc_id} updated to status {new_status}")
        except Exception as e:
            print(f"❌ Error updating document {doc_id} to status {new_status}: {e}")

    return full_result

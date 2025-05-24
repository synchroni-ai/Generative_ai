# # utils/test_case_utils.py

# from typing import List, Dict, Any, Tuple, Callable, Optional # ENSURE THIS LINE IS AT THE TOP

# import pandas as pd
# import csv
# import re
# import os

# from bson import ObjectId
# from fastapi import HTTPException
# from pymongo.collection import Collection

# CSV_OUTPUT_DIR = "output/csv_files" # Ensure this path is correct relative to your project root
# os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)


# def generate_test_cases(
#     brd_text: str,
#     generation_function: Callable, # The specific LLM function (e.g., openai.generate_with_openai)
#     test_case_prompt_template: str,
#     llm_api_key: Optional[str] = None
# ) -> Tuple[str, int]:
#     """
#     Generates test cases from the given BRD text using the specified LLM and prompt.

#     Args:
#         brd_text: The cleaned text of the BRD.
#         generation_function: The function to call the LLM (e.g., generate_with_openai).
#         test_case_prompt_template: The prompt template string.
#         llm_api_key: The API key to use for the LLM call (optional).

#     Returns:
#         A tuple: (The generated test cases as a string, tokens_used)
#         or (\"\", 0) if an error occurs.
#     """
#     try:
#         formatted_prompt = test_case_prompt_template.format(brd_text=brd_text)
#         # Pass the llm_api_key to the generation_function
#         response_text, tokens_used = generation_function(
#             formatted_prompt,
#             api_key=llm_api_key
#         )
#         return response_text.strip(), tokens_used
#     except Exception as e:
#         print(f"Error in test_case_utils.generate_test_cases: {str(e)}")
#         # Log the type of generation_function to see what failed
#         print(f"Failed with generation_function: {generation_function.__name__ if hasattr(generation_function, '__name__') else str(generation_function)}")
#         return f"ERROR_GENERATING_TEST_CASES: {e}", 0


# CSV_HEADERS = [
#     "TCID",
#     "Test type",
#     "Title",
#     "Description",
#     "Precondition",
#     "Steps",
#     "Action",
#     "Data",
#     "Result",
#     "Test Nature",
#     "Test priority",
# ]

# def parse_test_cases_to_csv(document_id: str, collection: Collection, force_reparse_for_json: bool = False) -> tuple[str, list[Any]]:
#     doc = collection.find_one({"_id": ObjectId(document_id)})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found for CSV parsing")

#     db_test_cases_field = doc.get("test_cases")
#     all_parsed_rows_for_json_output = []
#     csv_output_path = os.path.join(CSV_OUTPUT_DIR, f"{document_id}_test_cases.csv")

#     if force_reparse_for_json:
#         if isinstance(db_test_cases_field, dict):
#             try:
#                 # This dynamic import is to avoid circular dependencies if main3.py also imports this util.
#                 # A better long-term solution might be to move shared parsing logic to a common utility.
#                 from main3 import parse_test_cases_from_content_string
#                 for tc_type, type_data in db_test_cases_field.items():
#                     if isinstance(type_data, dict) and "content" in type_data:
#                         content_to_parse = type_data['content']
#                         if content_to_parse and isinstance(content_to_parse, str):
#                             parsed_for_type = parse_test_cases_from_content_string(content_to_parse)
#                             for p_case in parsed_for_type:
#                                 p_case['Test type'] = tc_type # Ensure type is set
#                                 all_parsed_rows_for_json_output.append(p_case)
#                         else:
#                             print(f"Warning: Content for type '{tc_type}' in doc '{document_id}' is not a string or is empty.")
#             except ImportError:
#                 print("Critical Error: Could not import 'parse_test_cases_from_content_string' from 'main3' for re-parsing in 'test_case_utils.py'. Returning empty list for JSON.")
#                 # Decide if this should raise an error or just return empty
#             except Exception as e_reparse:
#                 print(f"Error during re-parsing in test_case_utils.py for doc '{document_id}': {e_reparse}")

#     # The CSV writing portion of this function has been simplified as the primary,
#     # robust CSV generation for batch data now occurs in the download endpoints in main3.py.
#     # If this function is still required to produce a meaningful CSV,
#     # the writing logic here would need to be enhanced to use the `all_parsed_rows_for_json_output`.
#     # For example:
#     # if all_parsed_rows_for_json_output:
#     #     try:
#     #         with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
#     #             writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, quoting=csv.QUOTE_ALL, extrasaction='ignore')
#     #             writer.writeheader()
#     #             for row in all_parsed_rows_for_json_output:
#     #                 writer.writerow(row)
#     #     except IOError as e_io:
#     #         print(f"IOError writing CSV for doc '{document_id}': {e_io}")
#     #     except Exception as e_csv_write:
#     #         print(f"General error writing CSV for doc '{document_id}': {e_csv_write}")
#     # else:
#         # Optionally create an empty CSV or a CSV with just headers if no data
#         # try:
#         #     with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
#         #         writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, quoting=csv.QUOTE_ALL)
#         #         writer.writeheader()
#         # except IOError:
#         #     pass # Ignore if can't even write headers

#     return csv_output_path, all_parsed_rows_for_json_output

# utils/test_case_utils.py

import os
from typing import List, Tuple, Callable, Optional, Any # Added Any for parse_test_cases_to_csv return
# Removed pandas, csv, pymongo.collection, ObjectId, HTTPException if not strictly needed by generate_test_cases
# If parse_test_cases_to_csv is completely removed or only returns basic data, these might not be needed.
# For now, keeping them as the function stub exists.
import csv
from pymongo.collection import Collection # If parse_test_cases_to_csv still needs it for some reason
from bson import ObjectId # If parse_test_cases_to_csv still needs it
from fastapi import HTTPException # If parse_test_cases_to_csv still raises it


# This should be the directory where Celery tasks might write temporary CSVs if that feature is kept.
# If CSVs are only generated by FastAPI endpoints, this might not be needed here.
CSV_OUTPUT_DIR = os.getenv("CELERY_CSV_OUTPUT_DIR", "output/celery_csv_files") # Different from main3.py's output
if CSV_OUTPUT_DIR: # Only create if defined, to avoid issues if it's meant to be off
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

# This is the list of *valid test case types* your system supports for generation.
# It's used by task_with_api_key.py to normalize the 'test_case_types' input.
VALID_TEST_CASE_TYPES = [
    "functional", "non-functional", "security",
    "performance", "boundary", "compliance",
]


def generate_test_cases(
    brd_text: str,
    generation_function: Callable,
    test_case_prompt_template: str,
    llm_api_key: Optional[str] = None
) -> Tuple[str, int]:
    """
    Generates test cases from the given BRD text using the specified LLM and prompt.
    """
    try:
        formatted_prompt = test_case_prompt_template.format(brd_text=brd_text)
        response_text, tokens_used = generation_function(
            formatted_prompt,
            api_key=llm_api_key
        )
        return response_text.strip(), tokens_used
    except Exception as e:
        print(f"Error in test_case_utils.generate_test_cases: {str(e)}")
        print(f"Failed with generation_function: {generation_function.__name__ if hasattr(generation_function, '__name__') else str(generation_function)}")
        return f"ERROR_GENERATING_TEST_CASES: {e}", 0


# This version of parse_test_cases_to_csv is now very basic.
# Its main purpose might be if the Celery task itself needs to produce a CSV (unlikely now)
# or if an older part of the system relies on it.
# For the API endpoints in main3.py, parsing happens there.
# If this function is no longer used by task_with_api_key.py or other utils, it could be removed.
CSV_HEADERS_FOR_UTIL = [ # Different name to avoid confusion with main3.py's order
    "TCID", "Test type", "Title", "Description", "Precondition",
    "Steps", "Action", "Data", "Result", "Test Nature", "Test priority"
]

def parse_test_cases_to_csv(
    document_id_str: str, # Expecting a string here
    collection: Optional[Collection] = None, # Make collection optional
    force_reparse_for_json: bool = False # This flag's utility here is now limited
) -> tuple[str, list[Any]]:
    """
    Basic CSV generation utility.
    If 'collection' and 'document_id_str' are provided, it tries to fetch the doc.
    The 'force_reparse_for_json' functionality is now minimal here as robust parsing
    should occur in the API endpoints (main3.py).
    Returns a path to a CSV (might be empty/basic) and a list (likely empty or basic).
    """
    print(f"UTIL_INFO: parse_test_cases_to_csv called for doc_id '{document_id_str}', force_reparse_for_json={force_reparse_for_json}")
    
    # Default path, even if file isn't meaningfully populated
    csv_file_path = ""
    if CSV_OUTPUT_DIR: # Only form path if directory is configured
        csv_file_path = os.path.join(CSV_OUTPUT_DIR, f"{document_id_str}_test_cases_util.csv")

    parsed_rows_for_json_list: List[Any] = []

    if force_reparse_for_json and collection and document_id_str:
        print(f"UTIL_INFO: Attempting to fetch doc {document_id_str} for re-parsing (basic).")
        try:
            doc_obj_id_util = ObjectId(document_id_str)
            doc_data = collection.find_one({"_id": doc_obj_id_util})
            if doc_data and isinstance(doc_data.get("test_cases"), dict):
                # This would require a local, simplified parser here if we want to populate parsed_rows_for_json_list
                # For now, to avoid circular deps, we won't import the main3 parser.
                # This part will effectively do nothing much for JSON re-parsing.
                print(f"UTIL_WARNING: force_reparse_for_json=True but using simplified logic. Robust parsing is in main3.py.")
                # Example: one could extract raw content strings if needed by some other utility
                # for tc_type, type_data in doc_data["test_cases"].items():
                #     if isinstance(type_data, dict) and "content" in type_data:
                #         parsed_rows_for_json_list.append({"type": tc_type, "raw_content": type_data["content"]})
            elif doc_data:
                 print(f"UTIL_WARNING: Doc {document_id_str} found, but 'test_cases' field is not a dict or is missing.")
            else:
                 print(f"UTIL_WARNING: Doc {document_id_str} not found in collection for re-parsing.")

        except InvalidId:
            print(f"UTIL_ERROR: Invalid ObjectId string for document_id_str: '{document_id_str}'")
        except Exception as e_fetch:
            print(f"UTIL_ERROR: Could not fetch/process doc {document_id_str} for re-parsing: {e_fetch}")
    
    # Minimal CSV writing, if CSV_OUTPUT_DIR is set.
    if CSV_OUTPUT_DIR and csv_file_path:
        try:
            with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS_FOR_UTIL, extrasaction='ignore', quoting=csv.QUOTE_ALL)
                writer.writeheader()
                # If parsed_rows_for_json_list was populated with dicts matching CSV_HEADERS_FOR_UTIL, they would be written here.
                # For now, it will likely be an empty CSV or one with just headers.
                # writer.writerows(parsed_rows_for_json_list)
            print(f"UTIL_INFO: Basic CSV (likely headers only) written to {csv_file_path}")
        except Exception as e_csv:
            print(f"UTIL_ERROR: Could not write basic CSV to {csv_file_path}: {e_csv}")

    return csv_file_path, parsed_rows_for_json_list
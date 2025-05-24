# utils/test_case_utils.py
 
from typing import List, Dict, Any, Tuple, Callable, Optional # ENSURE THIS LINE IS AT THE TOP
 
import pandas as pd
import csv
import re
import os
 
from bson import ObjectId
from fastapi import HTTPException
from pymongo.collection import Collection
 
CSV_OUTPUT_DIR = "output/csv_files" # Ensure this path is correct relative to your project root
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
 
 
def generate_test_cases(
    brd_text: str,
    generation_function: Callable, # The specific LLM function (e.g., openai.generate_with_openai)
    test_case_prompt_template: str,
    llm_api_key: Optional[str] = None
) -> Tuple[str, int]:
    """
    Generates test cases from the given BRD text using the specified LLM and prompt.
 
    Args:
        brd_text: The cleaned text of the BRD.
        generation_function: The function to call the LLM (e.g., generate_with_openai).
        test_case_prompt_template: The prompt template string.
        llm_api_key: The API key to use for the LLM call (optional).
 
    Returns:
        A tuple: (The generated test cases as a string, tokens_used)
        or (\"\", 0) if an error occurs.
    """
    try:
        formatted_prompt = test_case_prompt_template.format(brd_text=brd_text)
        # Pass the llm_api_key to the generation_function
        response_text, tokens_used = generation_function(
            formatted_prompt,
            api_key=llm_api_key
        )
        return response_text.strip(), tokens_used
    except Exception as e:
        print(f"Error in test_case_utils.generate_test_cases: {str(e)}")
        # Log the type of generation_function to see what failed
        print(f"Failed with generation_function: {generation_function.__name__ if hasattr(generation_function, '__name__') else str(generation_function)}")
        return f"ERROR_GENERATING_TEST_CASES: {e}", 0
 
 
CSV_HEADERS = [
    "TCID",
    "Test type",
    "Title",
    "Description",
    "Precondition",
    "Steps",
    "Action",
    "Data",
    "Result",
    "Test Nature",
    "Test priority",
]
 
def parse_test_cases_to_csv(document_id: str, collection: Collection, force_reparse_for_json: bool = False) -> tuple[str, list[Any]]:
    doc = collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found for CSV parsing")
 
    db_test_cases_field = doc.get("test_cases")
    all_parsed_rows_for_json_output = []
    csv_output_path = os.path.join(CSV_OUTPUT_DIR, f"{document_id}_test_cases.csv")
 
    if force_reparse_for_json:
        if isinstance(db_test_cases_field, dict):
            try:
                # This dynamic import is to avoid circular dependencies if main3.py also imports this util.
                # A better long-term solution might be to move shared parsing logic to a common utility.
                from main3 import parse_test_cases_from_content_string
                for tc_type, type_data in db_test_cases_field.items():
                    if isinstance(type_data, dict) and "content" in type_data:
                        content_to_parse = type_data['content']
                        if content_to_parse and isinstance(content_to_parse, str):
                            parsed_for_type = parse_test_cases_from_content_string(content_to_parse)
                            for p_case in parsed_for_type:
                                p_case['Test type'] = tc_type # Ensure type is set
                                all_parsed_rows_for_json_output.append(p_case)
                        else:
                            print(f"Warning: Content for type '{tc_type}' in doc '{document_id}' is not a string or is empty.")
            except ImportError:
                print("Critical Error: Could not import 'parse_test_cases_from_content_string' from 'main3' for re-parsing in 'test_case_utils.py'. Returning empty list for JSON.")
                # Decide if this should raise an error or just return empty
            except Exception as e_reparse:
                print(f"Error during re-parsing in test_case_utils.py for doc '{document_id}': {e_reparse}")
 
    # The CSV writing portion of this function has been simplified as the primary,
    # robust CSV generation for batch data now occurs in the download endpoints in main3.py.
    # If this function is still required to produce a meaningful CSV,
    # the writing logic here would need to be enhanced to use the `all_parsed_rows_for_json_output`.
    # For example:
    # if all_parsed_rows_for_json_output:
    #     try:
    #         with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
    #             writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, quoting=csv.QUOTE_ALL, extrasaction='ignore')
    #             writer.writeheader()
    #             for row in all_parsed_rows_for_json_output:
    #                 writer.writerow(row)
    #     except IOError as e_io:
    #         print(f"IOError writing CSV for doc '{document_id}': {e_io}")
    #     except Exception as e_csv_write:
    #         print(f"General error writing CSV for doc '{document_id}': {e_csv_write}")
    # else:
        # Optionally create an empty CSV or a CSV with just headers if no data
        # try:
        #     with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
        #         writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, quoting=csv.QUOTE_ALL)
        #         writer.writeheader()
        # except IOError:
        #     pass # Ignore if can't even write headers
 
    return csv_output_path, all_parsed_rows_for_json_output
 
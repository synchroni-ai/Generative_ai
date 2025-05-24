# test_cases_utils.py

import pandas as pd
import csv
import re
import os
from typing import List, Dict, Any

from bson import ObjectId
from fastapi import HTTPException
from pymongo.collection import Collection

CSV_OUTPUT_DIR = "output/csv_files"
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)


def generate_test_cases(brd_text, generation_function, test_case_prompt):
    """
    Generates test cases from the given BRD text using the specified LLM and prompt.

    Args:
        brd_text: The cleaned text of the BRD.
        llm_function: The function to call the LLM (e.g., generate_with_together).
        prompt_file_path: The path to the prompt file.

    Returns:
        The generated test cases as a string, or None if an error occurs.
    """

    try:
        # Format the prompt with the chunk text
        formatted_prompt = test_case_prompt.format(brd_text=brd_text)
        response, tokens = generation_function(formatted_prompt)
        return response.strip(), tokens
    except Exception as e:
        print(f"Error generating test cases: {str(e)}")
        return "", 0


CSV_HEADERS = [
    # "Category",
    "TCID",
    "Test type",
    "Title",
    "Description",
    "Precondition",
    "Steps",
    "Action",
    "Data",
    "Result",
    "Test Nature", # MODIFIED HERE
    "Test priority",
]


def parse_test_cases_to_csv(document_id: str, collection: Collection) -> str:
    doc = collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    test_cases_dict = doc.get("test_cases")
    if not test_cases_dict or not isinstance(test_cases_dict, dict):
        raise HTTPException(status_code=404, detail="No test cases found in document")

    csv_output_path = os.path.join(CSV_OUTPUT_DIR, f"{document_id}_test_cases.csv")

    all_parsed_rows = []

    with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for category, tc_entry in test_cases_dict.items():
            content_str = str(tc_entry.get("content", "")).strip()
            if not content_str:
                continue

            lines = content_str.splitlines()
            while lines and not lines[0].strip():
                lines.pop(0)
            if lines and lines[0].strip().lower() == "test cases:":
                lines.pop(0)

            content_to_split = "\n".join(lines).strip()
            individual_tc_blocks = []

            if content_to_split:
                split_pattern = r"(?=^(?:\*\*(?:TC|PTC|FTC|BTC|STC|NFTC|CTC)_\d+\*\*|TCID:|Test Case ID:)\s*)"
                potential_blocks = re.split(
                    split_pattern, content_to_split, flags=re.MULTILINE
                )
                processed_blocks = [b.strip() for b in potential_blocks if b.strip()]

                if processed_blocks:
                    first_block_content = processed_blocks[0]
                    is_first_block_a_tc = re.match(
                        r"^(?:\*\*(?:TC|PTC|FTC|BTC|STC|NFTC|CTC)_\d+\*\*|TCID:|Test Case ID:)",
                        first_block_content.lstrip(),
                        re.IGNORECASE,
                    )
                    if not is_first_block_a_tc and len(processed_blocks) > 1:
                        individual_tc_blocks = processed_blocks[1:]
                    else:
                        individual_tc_blocks = processed_blocks

            if not individual_tc_blocks and content_to_split:
                if re.match(
                    r"^(?:\*\*(?:TC|PTC|FTC|BTC|STC|NFTC|CTC)_\d+\*\*|TCID:|Test Case ID:)",
                    content_to_split.lstrip(),
                    re.IGNORECASE,
                ):
                    individual_tc_blocks.append(content_to_split)
#brddocument
            for block in individual_tc_blocks:
                fields = {header: "N/A" for header in CSV_HEADERS}
                # fields["Category"] = category
                collecting_steps = False
                current_steps_list = []

                lines_in_block = block.splitlines()
                first_line_processed_for_tcid = False

                if lines_in_block:
                    first_line_stripped = lines_in_block[0].strip()
                    tcid_standalone_match = re.match(
                        r"^\*\*((?:TC|PTC|FTC|BTC|STC|NFTC|CTC)_\d+)\*\*\s*$",
                        first_line_stripped,
                    )
                    if tcid_standalone_match:
                        fields["TCID"] = tcid_standalone_match.group(1)
                        first_line_processed_for_tcid = True

                for line_idx, line_content in enumerate(lines_in_block):
                    if first_line_processed_for_tcid and line_idx == 0:
                        continue

                    line = line_content.strip()
                    if not line:
                        continue

                    key_value_match = re.match(r"^\**([^:]+):\**\s*(.*)", line)
                    if key_value_match:
                        key = key_value_match.group(1).strip().lower()
                        value = key_value_match.group(2).strip()
                        collecting_steps = False

                        mapping = {
                            "tcid": "TCID",
                            "test case id": "TCID",
                            "test type": "Test type",
                            "test case type": "Test type",
                            "title": "Title",
                            "description": "Description",
                            "precondition": "Precondition",
                            "action": "Action",
                            "data": "Data",
                            "result": "Result",
                            "test nature": "Test Nature", # MODIFIED HERE (key and value)
                            "type (p / n / in)": "Test Nature", # Keep old key for backward compatibility if needed, or remove
                            "test priority": "Test priority",
                            "steps": "Steps",
                        }

                        if key in mapping:
                            if key == "steps":
                                collecting_steps = True
                                if value:
                                    current_steps_list.append(value)
                            else:
                                fields[mapping[key]] = value
                    elif collecting_steps:
                        current_steps_list.append(line)

                fields["Steps"] = " ".join(current_steps_list).strip()
                for f_key in fields:
                    if fields[f_key] == "":
                        fields[f_key] = "N/A"

                writer.writerow(fields)
                all_parsed_rows.append(fields)

    return csv_output_path, all_parsed_rows
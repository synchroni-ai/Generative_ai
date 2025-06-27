import io
from typing import Dict
from collections import defaultdict
import re

import pandas as pd
import xlsxwriter


def flatten_results_to_excel(results: Dict) -> io.BytesIO:
    """
    Converts test results into an Excel file with cleaned expected results,
    wrapped text, and newline-separated steps.
    """
    data = []

    type_prefix_map = {
        "boundary": "BTC",
        "security": "STC",
        "functional": "FTC",
        "non-functional": "NFTC",
        "compliance": "CTC",
        "performance": "PTC",
        "usability": "UTC",  # Add usability
        "accessibility": "ATC", #Add accessibility
        "integration": "ITC",  # Add integration
        "regression": "RTC", #Add regression
        "api": "API",       # Add API tests (if applicable)
        "ui": "UIT",         # Add UI tests (if applicable)
        "unit": "UTC",        #Add unit Test(if applicable)
    }

    tcid_counters = defaultdict(int)
    documents = results.get("documents", {})

    for doc_id, doc_data in documents.items():
        all_subtypes = doc_data.get("all_subtypes", [])

        for subtype_group in all_subtypes:
            for case in subtype_group:
                if not isinstance(case, dict):
                    continue

                # ✅ Separate out 'Test type' and 'Type'
                test_type_raw = (case.get("Test type") or case.get("Test Type") or "").strip()
                test_nature = (case.get("Type") or "").strip()

                prefix = type_prefix_map.get(test_type_raw.lower())
                if not prefix:
                    print(f"Skipping case due to unrecognized test type: {test_type_raw}")
                    continue

                # ✅ Generate TCID if not present
                tcid = (case.get("TCID") or case.get("Test Case ID") or "").strip()
                if not tcid:
                    tcid_counters[prefix] += 1
                    tcid = f"{prefix}_{tcid_counters[prefix]:03}"

                scenario = (case.get("Test Scenario") or "").strip()
                user_role = (case.get("User Role") or "").strip()
                preconditions = (case.get("Pre-conditions") or "").strip()
                steps = (case.get("Test Steps") or "").strip()
                expected_result = (case.get("Expected Result") or "").strip()

                # Clean up the expected result:
                expected_result = expected_result.split("---")[0].strip()  # Remove "---" and anything after
                expected_result = re.sub(r"\[.*?\]", "", expected_result).strip() #Remove classifications in brackets

                # Split the steps into individual lines using regex.
                steps_cleaned = "\n".join(re.split(r"(?=\d+\.)", steps))  # Keep the delimiter

                data.append([
                    tcid,
                    test_type_raw,
                    scenario,
                    test_nature,
                    user_role,
                    preconditions,
                    steps_cleaned,
                    expected_result
                ])

    df = pd.DataFrame(data, columns=[
        "Test Case ID",
        "Test type",
        "Test Scenario",
        "Type",
        "User Role",
        "Pre-conditions",
        "Test Steps",
        "Expected Result"
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Test Results', index=False)

        # Get the xlsxwriter objects from the dataframe writer object.
        workbook = writer.book
        worksheet = writer.sheets['Test Results']

        # Add a format for wrapping text.
        text_wrap_format = workbook.add_format({'text_wrap': True})

        # Set the column width and format. Adjust column number (7) for 'Test Steps'.
        worksheet.set_column(7, 7, 50, text_wrap_format)  # Column index 7 ("H") is where 'Test Steps' is located
        worksheet.set_column(5, 5, 50, text_wrap_format)  # Column index 5 ("F") is where 'Pre-Conditions' is located
        worksheet.set_column(6, 6, 50, text_wrap_format)  # Column index 6 ("G") is where 'Steps Cleaned' is located
        worksheet.set_column(8, 8, 50, text_wrap_format)  # Column index 8 ("I") is where 'Expected Result' is located


    output.seek(0)
    return output
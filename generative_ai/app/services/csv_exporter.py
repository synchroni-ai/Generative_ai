import csv
import io
from typing import Dict
from collections import defaultdict

def flatten_results_to_csv(results: Dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    
    writer.writerow([
        "Test Case ID",
        "Test type",             # e.g., Boundary, Functional
        "Test Scenario",
        "Type",                  # e.g., P, N, IN
        "User Role",
        "Pre-conditions",
        "Test Steps",
        "Expected Result"
    ])


    type_prefix_map = {
        "boundary": "BTC",
        "security": "STC",
        "functional": "FTC",
        "non-functional": "NFTC",
        "compliance": "CTC",
        "performance": "PTC"
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
                steps_cleaned = (case.get("Test Steps") or "").replace('\r\n', '\n').replace('\r', '\n').strip()
                expected_result = (case.get("Expected Result") or "").replace('\r\n', '\n').replace('\r', '\n').strip()

                # ✅ Must have these to proceed
                if not all([tcid, test_type_raw, test_nature, steps_cleaned, expected_result]):
                    print(f"Skipping due to missing required fields. TCID: {tcid}")
                    continue

                writer.writerow([
                    tcid,
                    test_type_raw,
                    scenario,
                    test_nature,
                    user_role,
                    preconditions,
                    steps_cleaned,
                    expected_result
                ])

    return output.getvalue()
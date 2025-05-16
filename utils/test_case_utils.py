# utils/test_case_utils.py
from pathlib import Path # For Path object usage
import pandas as pd
import csv
import re
import os
from typing import Callable, Tuple, Any, Optional

# Define a type alias for the generation function for clarity
LLMGenerationFunction = Callable[..., Tuple[str, int]] # Flexible: takes prompt, and **kwargs like api_key

def generate_test_cases(
    chunk_text: str,
    generation_function: LLMGenerationFunction,
    test_case_prompt: str,
    api_key: Optional[str] = None
) -> Tuple[str, int]:
    """
    Generates test cases from the given text chunk using the specified LLM and prompt.

    Args:
        chunk_text: The text chunk to process.
        generation_function: The function to call the LLM (e.g., Mistral.generate_with_mistral).
        test_case_prompt: The prompt template string (should contain {chunk_text}).
        api_key: Optional API key to pass to the generation_function.

    Returns:
        A tuple of (generated_text_string, tokens_used_integer).
        If an error occurs, generated_text_string may contain an error message and tokens_used_integer will be 0.
    """
    print(f"\n--- DEBUG: test_case_utils.generate_test_cases ---")
    if not chunk_text or not chunk_text.strip():
        print("WARNING (test_case_utils): Received empty or whitespace-only chunk_text. Skipping LLM call.")
        print(f"--- END DEBUG: test_case_utils.generate_test_cases (EMPTY CHUNK) ---\n")
        return "", 0

    try:
        # Ensure your prompt templates use {chunk_text}
        formatted_prompt = test_case_prompt.format(chunk_text=chunk_text)
        print(f"Formatted Prompt (first 300 chars):\n{formatted_prompt[:300]}\n")
        
        response_text, tokens_used = generation_function(prompt=formatted_prompt, api_key=api_key)
        
        print(f"LLM Raw Response in test_case_utils (first 300 chars):\n{str(response_text)[:300]}\n")
        print(f"Tokens used from LLM function: {tokens_used}")

        if isinstance(response_text, str) and ("ERROR:" in response_text.upper() or "API ERROR" in response_text.upper()):
            print(f"WARNING (test_case_utils): LLM function returned an error message: {response_text}")
            return response_text, 0

        if not response_text or not str(response_text).strip():
            print("WARNING (test_case_utils): LLM returned empty or whitespace-only text (after error check).")
            print(f"--- END DEBUG: test_case_utils.generate_test_cases (EMPTY LLM RESPONSE) ---\n")
            return "", 0
        
        print(f"--- END DEBUG: test_case_utils.generate_test_cases (SUCCESS) ---\n")
        return str(response_text).strip(), int(tokens_used)

    except KeyError as ke:
        key_error_value = str(ke).strip("\"'") # Assign to a variable first
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"CRITICAL PROMPT FORMAT ERROR in test_case_utils.generate_test_cases: {ke}")
        print(f"This means your prompt template string still contains '{{{key_error_value}}}' but it was not provided in .format().")
        print(f"Ensure prompt templates use '{{chunk_text}}' and NOT other placeholders unless provided.")
        print(f"Prompt Template (first 100): {test_case_prompt[:100]}")
        import traceback
        traceback.print_exc()
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return f"Util Prompt Format Error: {ke}", 0
    except Exception as e:
        import traceback
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"UNEXPECTED ERROR in test_case_utils.generate_test_cases: {e}")
        print(f"Chunk Text (first 100): {chunk_text[:100]}")
        print(f"Prompt Template (first 100): {test_case_prompt[:100]}")
        traceback.print_exc()
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return f"Util Error: {e}", 0


def store_test_cases_to_text_file(test_cases_text: str, output_path: str = "test_cases.txt") -> Optional[str]:
    print(f"[TEST_CASE_UTILS DEBUG] Attempting to store text to: {output_path}")
    if not test_cases_text or not test_cases_text.strip():
        print(f"[TEST_CASE_UTILS WARNING] No text content to store in {output_path}.")
        return None
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(test_cases_text)
        print(f"[TEST_CASE_UTILS DEBUG] Successfully stored text to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error writing to text file {output_path}: {e}")
        return None


def txt_to_csv_mistral(input_file: str, output_file: str):
    print(f"[TEST_CASE_UTILS DEBUG] txt_to_csv_mistral: Input='{input_file}', Output='{output_file}'")
    if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
        print(f"WARNING (txt_to_csv_mistral): Input file '{input_file}' is missing or empty. Creating CSV with headers only.")
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Test Case ID", "Title", "Description", "Steps", "Expected Result"])
        return

    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()
    test_cases_raw = re.split(r"\n(?=TCID:)", content)
    rows = []
    for case_content in test_cases_raw:
        case_content = case_content.strip()
        if not case_content.startswith("TCID:"):
            if case_content: print(f"DEBUG (Mistral CSV): Skipping non-TCID block: {case_content[:50]}")
            continue
        tc_id_match = re.search(r"TCID:\s*([^\n]+)", case_content)
        title_match = re.search(r"Title:\s*([^\n]+)", case_content)
        desc_match = re.search(r"Description:\s*([^\n]+)", case_content)
        steps_match = re.search(r"Steps:\s*((?:.|\n)*?)(?=\nExpected Result:|\nTest Type:|\nPriority:|$)", case_content, re.DOTALL)
        expected_result_match = re.search(r"Expected Result:\s*((?:.|\n)*?)(?=\nTest Type:|\nPriority:|$)", case_content, re.DOTALL)
        tc_id = tc_id_match.group(1).strip() if tc_id_match else "N/A"
        title = title_match.group(1).strip() if title_match else "N/A"
        description = desc_match.group(1).strip() if desc_match else "N/A"
        steps_text = steps_match.group(1).strip().replace("\n", " ") if steps_match else "N/A"
        steps_text = re.sub(r'^\s*\d+\.\s*', '', steps_text, flags=re.MULTILINE).strip()
        expected_result = expected_result_match.group(1).strip().replace("\n", " ") if expected_result_match else "N/A"
        rows.append([tc_id, title, description, steps_text, expected_result])
    if not rows: print(f"WARNING (txt_to_csv_mistral): No test cases extracted from '{input_file}'. CSV will only have headers.")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Test Case ID", "Title", "Description", "Steps", "Expected Result"])
        if rows: writer.writerows(rows)
    print(f"CSV file '{output_file}' processed for Mistral format.")


def txt_to_csv_llama(input_file: str, output_file: str):
    print(f"[TEST_CASE_UTILS DEBUG] txt_to_csv_llama: Input='{input_file}', Output='{output_file}'")
    if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
        print(f"WARNING (txt_to_csv_llama): Input file '{input_file}' is missing or empty. Creating CSV with headers only.")
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Test Case ID", "Title", "Description", "Steps", "Expected Result"])
        return
    try:
        with open(input_file, "r", encoding="utf-8") as file: content = file.read()
        test_cases_raw = re.split(r"\n(?=TCID:|\*\*TC_)", content)
        output = []
        for case_content in test_cases_raw:
            case_content = case_content.strip()
            if not (case_content.startswith("TCID:") or case_content.startswith("**TC_")):
                if case_content: print(f"DEBUG (Llama CSV): Skipping non-TCID block: {case_content[:50]}")
                continue
            tc_id_match = re.search(r"(?:TCID:|\*\*TC_)\s*([^\n:]+)", case_content)
            title_match = re.search(r"Title:\s*([^\n]+)", case_content)
            description_match = re.search(r"Description:\s*([^\n]+)", case_content)
            steps_match = re.search(r"Steps:\s*((?:.|\n)*?)(?=\nExpected Result:|$)", case_content, re.DOTALL)
            expected_match = re.search(r"Expected Result:\s*((?:.|\n)*?)(?=\nPriority:|\nTest Type:|$)", case_content, re.DOTALL)
            tc_id = tc_id_match.group(1).strip() if tc_id_match else "N/A_Llama"
            title = title_match.group(1).strip() if title_match else "N/A"
            description = description_match.group(1).strip() if description_match else "N/A"
            steps = steps_match.group(1).strip().replace("\n", " ") if steps_match else "N/A"
            expected_result = expected_match.group(1).strip().replace("\n", " ") if expected_match else "N/A"
            output.append([tc_id, title, description, steps, expected_result])
        if not output: print(f"WARNING (txt_to_csv_llama): No test cases extracted from '{input_file}'. CSV will only have headers.")
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Test Case ID", "Title", "Description", "Steps", "Expected Result"])
            if output: writer.writerows(output)
        print(f"✅ CSV file '{output_file}' processed for Llama format.")
    except FileNotFoundError: print(f"Error (Llama CSV): Input file '{input_file}' not found.")
    except Exception as e: print(f"An unexpected error occurred in txt_to_csv_llama: {e}")


def format_test_cases_excel(
    input_csv_path: str, output_excel_file: str, mode: str = "numbered_in_cell"
):
    print(f"[TEST_CASE_UTILS DEBUG] format_test_cases_excel: Input='{input_csv_path}', Output='{output_excel_file}'")
    if not os.path.exists(input_csv_path):
        print(f"ERROR (format_excel): CSV file '{input_csv_path}' not found. Cannot create Excel.")
        return

    try: # Add try-except for pandas operations
        df = pd.read_csv(input_csv_path)
    except pd.errors.EmptyDataError:
        print(f"WARNING (format_excel): CSV file '{input_csv_path}' is empty or has no data. Excel will be minimal or not created.")
        # Try to create an Excel with headers if the CSV file itself wasn't 0 bytes (meaning it might have had headers)
        if os.path.getsize(input_csv_path) > 0:
            try:
                Path(output_excel_file).parent.mkdir(parents=True, exist_ok=True)
                pd.DataFrame(columns=pd.read_csv(input_csv_path, nrows=0).columns).to_excel(output_excel_file, index=False, sheet_name="TestCases")
                print(f"Excel file '{output_excel_file}' created with headers from empty CSV.")
            except Exception as e_excel_empty_header:
                print(f"Error creating Excel with headers from empty CSV '{input_csv_path}': {e_excel_empty_header}")
        else: # CSV file was 0 bytes
            print(f"CSV '{input_csv_path}' was 0 bytes. Excel file not created.")
        return
    except Exception as e_read_csv:
        print(f"ERROR reading CSV '{input_csv_path}' for Excel formatting: {e_read_csv}")
        return


    if df.empty: # Check if DataFrame is empty after successful read (e.g., CSV had headers but no data rows)
        print(f"WARNING (format_excel): CSV file '{input_csv_path}' resulted in an empty DataFrame. Excel will contain headers only.")
        Path(output_excel_file).parent.mkdir(parents=True, exist_ok=True)
        try:
            df.to_excel(output_excel_file, index=False, sheet_name="TestCases") # Writes headers if df has columns
            print(f"Excel file '{output_excel_file}' created with headers only.")
        except Exception as e_excel_empty_df:
            print(f"Error creating Excel from empty DataFrame for '{input_csv_path}': {e_excel_empty_df}")
        return

    if "Steps" not in df.columns:
        print("WARNING (format_excel): The input CSV must contain a 'Steps' column for formatting. Skipping step formatting.")
    else:
        def clean_and_split_steps(steps_data):
            if pd.isna(steps_data): return []
            steps_data = str(steps_data).strip().rstrip("*").strip()
            return [s.strip() for s in re.split(r"\s*\d+\.\s*", steps_data) if s.strip()]

        if mode == "numbered_in_cell":
            def format_steps_display(steps_data):
                steps_list = clean_and_split_steps(steps_data)
                return "\n".join(f"Step {i+1}: {s}" for i, s in enumerate(steps_list))
            df["Steps"] = df["Steps"].apply(format_steps_display)
        elif mode == "step_per_row":
            expanded_rows = []
            for _, row in df.iterrows():
                steps_list = clean_and_split_steps(row.get("Steps", ""))
                if not steps_list:
                    expanded_rows.append(row.copy())
                    continue
                for i, step_item in enumerate(steps_list):
                    new_row = row.copy() if i == 0 else pd.Series([""] * len(row), index=row.index)
                    new_row["Steps"] = f"Step {i+1}: {step_item}"
                    expanded_rows.append(new_row)
            df = pd.DataFrame(expanded_rows)
        else:
            print("WARNING (format_excel): Invalid mode for step formatting. Using raw steps.")

    for col in df.select_dtypes(include=['object']):
        # Ensure values are strings before calling .str.replace
        df[col] = df[col].apply(lambda x: str(x).replace("*", "") if pd.notnull(x) else x)


    if "Test Case ID" in df.columns:
        df["Test Case ID"] = [f"TC_{i+1:03d}" for i in range(len(df))]
    else:
        print("WARNING (format_excel): 'Test Case ID' column not found. IDs will not be renumbered.")

    Path(output_excel_file).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_excel_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="TestCases")
        worksheet = writer.sheets["TestCases"]
        wrap_format = writer.book.add_format({"text_wrap": True, "valign": "top"})
        header_format = writer.book.add_format({'bold': True, 'text_wrap': True, 'valign': 'top',
                                               'fg_color': '#D7E4BC', 'border': 1}) # Example header format

        # Write headers with formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        if "Steps" in df.columns:
            steps_col_idx = df.columns.get_loc("Steps")
            worksheet.set_column(steps_col_idx, steps_col_idx, 50, wrap_format)
        
        # Basic auto-fit for other columns
        for i, col in enumerate(df.columns):
            if "Steps" in df.columns and i == df.columns.get_loc("Steps"): # Skip if it's the Steps column
                 continue
            # Calculate max length for column
            column_data = df[col].astype(str)
            max_len = column_data.map(len).max()
            header_len = len(col)
            final_len = max(max_len, header_len) + 2
            worksheet.set_column(i, i, min(final_len, 40), wrap_format if col != "Steps" else None)


    print("Excel file saved successfully as:", output_excel_file)
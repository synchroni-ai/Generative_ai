import pandas as pd
import csv
import re


def generate_test_cases(brd_text, llm_function, prompt_file_path):
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
        with open(prompt_file_path, "r") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(brd_text=brd_text)
        test_cases = llm_function(prompt)
        return test_cases
    except Exception as e:
        print(f"Error generating test cases: {e}")
        return None


def store_test_cases_to_text_file(test_cases_text, output_path="test_cases.txt"):
    """
    Stores the generated test cases to a text file.

    Args:
        test_cases_text: The generated test cases as a string.
        output_path: The path to the output text file (default: "test_cases.txt").

    Returns:
        The path to the output text file, or None if an error occurs.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(test_cases_text)  # Simply write the entire text to the file
        return output_path
    except Exception as e:
        print(f"Error writing to text file: {e}")
        return None


def txt_to_csv_mistral(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Split based on each Test Case
    test_cases = re.split(r"\*\*Test Case ID:\*\*", content)[1:]

    rows = []
    for case in test_cases:
        # Extract fields using regex
        tc_id_match = re.search(r"(\w+)", case)
        title_match = re.search(r"\*\*Title:\*\*\s*(.*)", case)
        desc_match = re.search(r"\*\*Description:\*\*\s*(.*)", case)
        steps_match = re.search(
            r"\*\*Steps:\*\*\s*((?:.|\n)*?)\*\*Expected Result:\*\*", case
        )
        expected_result_match = re.search(r"\*\*Expected Result:\*\*\s*(.*)", case)

        tc_id = tc_id_match.group(1).strip() if tc_id_match else ""
        title = title_match.group(1).strip() if title_match else ""
        description = desc_match.group(1).strip() if desc_match else ""
        steps = (
            steps_match.group(1).strip().replace("\n", " ").replace("    ", "")
            if steps_match
            else ""
        )
        expected_result = (
            expected_result_match.group(1).strip() if expected_result_match else ""
        )

        rows.append([tc_id, title, description, steps, expected_result])

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Test Case ID", "Title", "Description", "Steps", "Expected Result"]
        )
        writer.writerows(rows)

    print(f"CSV file '{output_file}' created successfully.")


def csv_to_excel(csv_file, excel_file):
    df = pd.read_csv(csv_file)
    df.to_excel(excel_file, index=False)
    print(f"Excel file '{excel_file}' created successfully.")


def txt_to_csv_llama(input_file, output_file):
    """Converts a text file with Llama-formatted test cases to a CSV file."""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            content = file.read()

        pattern = r"\*\*TC_(\d+): ([^\*]+)\*\*\s*\*\s*Title:\s*([^\*]+)\s*\*\s*Description:\s*([^\*]+)\s*\*\s*Steps:\s*([\s\S]*?)\s*\*\s*Expected Result:\s*([^\*]+)"

        test_cases = []

        matches = re.findall(pattern, content)

        for match in matches:
            case_id = f"TC_{match[0]}"
            title = match[2].strip()
            description = match[3].strip()
            steps = match[4].strip().replace("\n", " ").replace("\r", "")
            expected_result = match[5].strip()

            test_cases.append([case_id, title, description, steps, expected_result])

        # Write to CSV
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["Test Case ID", "Title", "Description", "Steps", "Expected Result"]
            )  # Corrected headers
            writer.writerows(test_cases)  # Corrected: Use test_cases, not rows

        print(f"CSV file '{output_file}' created successfully.")

    except FileNotFoundError as e:
        print(f"Error: Input file not found: {e}")
    except OSError as e:
        print(f"Error: Could not write to output file: {e}")
    except re.error as e:
        print(f"Error: Regular expression error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

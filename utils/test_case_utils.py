import pandas as pd
import csv
import re
import os


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
        test_cases, total_tokens = llm_function(prompt)
        return test_cases, total_tokens
    except Exception as e:
        print(f"Error generating test cases: {e}")
        return None, 0


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


# def csv_to_excel(csv_file, excel_file):
#     df = pd.read_csv(csv_file)
#     df.to_excel(excel_file, index=False)
#     print(f"Excel file '{excel_file}' created successfully.")


def txt_to_csv_llama(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            content = file.read()

        # Split the text into test cases using **TC_ as a delimiter
        test_cases = re.split(r"\*\*TC_", content)
        test_cases = [tc.strip() for tc in test_cases if tc.strip()]

        output = []

        for case in test_cases:
            # Add back TC_ at the start
            case = "TC_" + case

            # Extract ID
            id_match = re.match(r"(TC_\d+):", case)
            tc_id = id_match.group(1) if id_match else ""

            # Extract Title
            title_match = re.search(r"\*\s*Title:\s*(.+)", case)
            title = title_match.group(1).strip() if title_match else ""

            # Extract Description
            description_match = re.search(r"\*\s*Description:\s*(.+)", case)
            description = (
                description_match.group(1).strip() if description_match else ""
            )

            # Extract Steps
            steps_match = re.search(
                r"\*\s*Steps:\s*(.+?)\*\s*Expected Result:", case, re.DOTALL
            )
            steps = ""
            if steps_match:
                steps_block = steps_match.group(1).strip()
                steps_lines = re.findall(r"\d+\.\s*(.+)", steps_block)
                steps = "\n".join(
                    [
                        f"Step {i+1}: {step.strip()}"
                        for i, step in enumerate(steps_lines)
                    ]
                )

            # Extract Expected Result
            expected_match = re.search(r"\*\s*Expected Result:\s*(.+)", case)
            expected_result = expected_match.group(1).strip() if expected_match else ""

            output.append([tc_id, title, description, steps, expected_result])

        # Write to CSV
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["Test Case ID", "Title", "Description", "Steps", "Expected Result"]
            )
            writer.writerows(output)

        print(f"✅ CSV file '{output_file}' created successfully.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

    except FileNotFoundError as e:
        print(f"Error: Input file not found: {e}")
    except OSError as e:
        print(f"Error: Could not write to output file: {e}")
    except re.error as e:
        print(f"Error: Regular expression error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def format_test_cases_excel(
    input_csv_path: str, output_excel_file: str, mode: str = "numbered_in_cell"
):
    """
    Format the 'Steps' column in a test case CSV and export to Excel.

    Parameters:
    - input_csv_path: Path to the input CSV file
    - output_excel_file: Excel file will be saved
    - mode: 'numbered_in_cell' or 'step_per_row'
    """

    # Load the CSV
    df = pd.read_csv(input_csv_path)

    if "Steps" not in df.columns:
        raise ValueError("The input CSV must contain a 'Steps' column.")

    def clean_and_split_steps(steps):
        if pd.isna(steps):
            return []
        steps = str(steps).strip().rstrip("*").strip()
        return [
            step.strip() for step in re.split(r"\s*\d+\.\s*", steps) if step.strip()
        ]

    if mode == "numbered_in_cell":

        def format_steps(steps):
            steps_list = clean_and_split_steps(steps)
            return "\n".join(f"Step {i+1}: {step}" for i, step in enumerate(steps_list))

        df["Steps"] = df["Steps"].apply(format_steps)
        # Remove all '*' from all string fields
        df = df.applymap(lambda x: x.replace("*", "") if isinstance(x, str) else x)

        # Renumber test case IDs sequentially
        df["Test Case ID"] = [f"TC_{i+1:03d}" for i in range(len(df))]

        with pd.ExcelWriter(output_excel_file, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="TestCases")

            worksheet = writer.sheets["TestCases"]
            wrap_format = writer.book.add_format({"text_wrap": True, "valign": "top"})
            steps_col_idx = df.columns.get_loc("Steps")
            worksheet.set_column(steps_col_idx, steps_col_idx, 50, wrap_format)

    elif mode == "step_per_row":
        expanded_rows = []

        for _, row in df.iterrows():
            steps_list = clean_and_split_steps(row["Steps"])
            for i, step in enumerate(steps_list):
                new_row = (
                    row.copy()
                    if i == 0
                    else pd.Series([""] * len(row), index=row.index)
                )
                new_row["Steps"] = f"Step {i+1}: {step}"
                expanded_rows.append(new_row)

        expanded_df = pd.DataFrame(expanded_rows)
        expanded_df.to_excel(output_excel_file, index=False)

    else:
        raise ValueError("Invalid mode. Use 'numbered_in_cell' or 'step_per_row'.")

    print("File saved successfully as:", output_excel_file)

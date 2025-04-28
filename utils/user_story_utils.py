# utils/user_story_utils.py
import re
import csv
import pandas as pd


def generate_user_stories(brd_text, llm_function, prompt_file_path):
    """
    Generates user stories from the given BRD text using the specified LLM and prompt.

    Args:
        brd_text: The cleaned text of the BRD.
        llm_function: The function to call the LLM.
        prompt_file_path: The path to the prompt file for user story generation.

    Returns:
        The generated user stories as a string, or None if an error occurs.
    """
    try:
        with open(prompt_file_path, "r") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(brd_text=brd_text)
        user_stories = llm_function(prompt)
        return user_stories
    except Exception as e:
        print(f"Error generating user stories: {e}")
        return None


def store_user_stories_to_text_file(user_stories_text, output_path="user_stories.txt"):
    """
    Stores the generated user stories to a text file.

    Args:
        user_stories_text: The generated user stories as a string.
        output_path: The path to the output text file.

    Returns:
        The path to the output text file, or None if an error occurs.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(user_stories_text)
        return output_path
    except Exception as e:
        print(f"Error writing user stories to file: {e}")
        return None


def txt_to_csv_mistral(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Split based on each User Story
    user_stories = re.split(r"\*\*User Story ID:\*\*", content)[1:]

    rows = []
    for story in user_stories:
        # Extract fields using regex
        us_id_match = re.search(r"(\w+)", story)
        title_match = re.search(r"\*\*Title:\*\*\s*(.*)", story)
        desc_match = re.search(r"\*\*Description:\*\*\s*(.*)", story)
        ac_match = re.search(r"\*\*Acceptance Criteria:\*\*\s*((?:.|\n)*)", story)

        us_id = us_id_match.group(1).strip() if us_id_match else ""
        title = title_match.group(1).strip() if title_match else ""
        description = desc_match.group(1).strip() if desc_match else ""

        acceptance_criteria = ""
        if ac_match:
            criteria_lines = ac_match.group(1).strip().split("\n")
            criteria_clean = [
                line.strip("* ").strip() for line in criteria_lines if line.strip()
            ]
            acceptance_criteria = " | ".join(criteria_clean)

        rows.append([us_id, title, description, acceptance_criteria])

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["User Story ID", "Title", "Description", "Acceptance Criteria"]
        )
        writer.writerows(rows)

    print(f"CSV file '{output_file}' created successfully.")


def csv_to_excel(csv_file, excel_file):
    df = pd.read_csv(csv_file)
    df.to_excel(excel_file, index=False)
    print(f"Excel file '{excel_file}' created successfully.")


def txt_to_csv_llama(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            content = file.read()

        # Split the text into user stories using **US_ as a delimiter
        user_stories = re.split(r"\*\*US_", content)
        user_stories = [story.strip() for story in user_stories if story.strip()]

        # Prepare the output rows
        output = []

        for story in user_stories:
            # Add back US_ at the start
            story = "US_" + story

            # Extract ID
            id_match = re.match(r"(US_\d+)", story)
            story_id = id_match.group(1) if id_match else ""

            # Extract Title
            title_match = re.search(r"Title:\s*(.+)", story)
            title = title_match.group(1).strip() if title_match else ""

            # Extract Description
            description_match = re.search(r"Description:\s*(.+)", story)
            description = (
                description_match.group(1).strip() if description_match else ""
            )

            # Extract Acceptance Criteria
            acceptance_criteria_match = re.search(
                r"Acceptance Criteria:\s*(.+)", story, re.DOTALL
            )
            acceptance_criteria = ""
            if acceptance_criteria_match:
                acceptance_text = acceptance_criteria_match.group(1).strip()
                acceptance_lines = re.findall(r"[\*\-]\s*(.+)", acceptance_text)
                acceptance_criteria = " | ".join(
                    [line.strip() for line in acceptance_lines]
                )

            output.append([story_id, title, description, acceptance_criteria])

        # Write to CSV after processing all user stories
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Title", "Description", "Acceptance Criteria"])
            writer.writerows(output)

        print(f"✅ CSV file '{output_file}' created successfully.")

    except FileNotFoundError as e:
        print(f"❌ Error: Input file not found: {e}")
    except OSError as e:
        print(f"❌ Error: Could not write to output file: {e}")
    except re.error as e:
        print(f"❌ Error: Regular expression error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

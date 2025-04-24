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

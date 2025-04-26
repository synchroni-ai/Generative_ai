# utils/user_story_utils.py

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

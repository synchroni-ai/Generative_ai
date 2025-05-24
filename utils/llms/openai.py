# utils/llms/openai.py

import os
import openai
from dotenv import load_dotenv
from typing import Tuple, Optional

load_dotenv()

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"

def generate_with_openai(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 2500,
    api_key: Optional[str] = None # This key is STRICTLY what's passed from the Celery task
) -> Tuple[str, int]:
    """
    Calls the OpenAI API using ChatCompletion.
    The 'api_key' argument here is THE key that the Celery task logic decided to use.
    For "Openai" model, the Celery task is designed to ALWAYS pass os.getenv("OPENAI_API_KEY").
    """
    print(f"\n--- OPENAI.PY - generate_with_openai function ---")
    print(f"Received api_key argument value: '{api_key[:10] + '...' if api_key and len(api_key) > 10 else api_key}'")
    
    model_to_use_for_openai = os.getenv("OPENAI_MODEL_NAME", DEFAULT_OPENAI_MODEL)
    print(f"Attempting to use OpenAI model: {model_to_use_for_openai}")
    print(f"------------------------------------------------\n")

    if not api_key: # This check is crucial. If Celery task logic failed to pass a key, it stops here.
        error_msg = "ERROR (openai.py): No API key was provided to the generate_with_openai function."
        print(error_msg)
        return error_msg, 0

    try:
        # The 'api_key' parameter for the OpenAI client is the one received by this function.
        client = openai.OpenAI(api_key=api_key)

        messages = [
            {"role": "system", "content": "You are an expert Quality Assurance Engineer tasked with generating test cases."},
            {"role": "user", "content": prompt},
        ]
        response = client.chat.completions.create(
            model=model_to_use_for_openai,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        generated_text_content = ""
        if response.choices and response.choices[0].message:
            generated_text_content = response.choices[0].message.content
            if generated_text_content is None:
                generated_text_content = "" # Should not happen, but defensive
        else:
            generated_text_content = "ERROR: No content found in OpenAI API response choices."
            print(generated_text_content)

        tokens_consumed = response.usage.total_tokens if response.usage else 0
        return generated_text_content.strip(), tokens_consumed

    except openai.AuthenticationError as e:
        # This is the error you were seeing. The key passed as 'api_key' was rejected.
        error_msg = f"ERROR: OpenAI API Authentication Error: {e}. The API key '{api_key[:10]}...' was rejected by OpenAI. Verify it's a correct, active OpenAI key with available quota."
        print(error_msg)
        return error_msg, 0
    except openai.APIConnectionError as e:
        error_msg = f"ERROR: OpenAI API Connection Error: {e}."
        print(error_msg)
        return error_msg, 0
    except openai.RateLimitError as e:
        error_msg = f"ERROR: OpenAI API Rate Limit Exceeded: {e}."
        print(error_msg)
        return error_msg, 0
    except openai.BadRequestError as e:
        error_msg = f"ERROR: OpenAI API Bad Request Error: {e}."
        print(error_msg)
        return error_msg, 0
    except openai.APIStatusError as e:
        error_msg = f"ERROR: OpenAI API Status Error (HTTP {e.status_code}): {e.response.text if hasattr(e, 'response') and e.response else 'No details'}."
        print(error_msg)
        return error_msg, 0
    except Exception as e:
        error_msg = f"ERROR: An unexpected error in generate_with_openai: {type(e).__name__} - {str(e)}"
        print(error_msg)
        return error_msg, 0

# Example test block (optional, for direct testing of this file)
if __name__ == "__main__":
    print("Directly testing generate_with_openai...")
    # ENSURE OPENAI_API_KEY is set in your .env for this direct test to work as intended.
    # This test will use the environment variable because `api_key` is not passed here.
    # The Celery task logic dictates that os.getenv("OPENAI_API_KEY") *is* what gets passed.
    test_key_from_env = os.getenv("OPENAI_API_KEY")
    if test_key_from_env:
        print(f"Using OPENAI_API_KEY from env for direct test: {test_key_from_env[:10]}...")
        sample_prompt_text = "What are three key benefits of unit testing?"
        text_result, tokens_result = generate_with_openai(sample_prompt_text, api_key=test_key_from_env) # Explicitly pass for clarity in test
        print("\n--- Direct Test Result ---")
        if "ERROR:" in text_result:
            print(f"Error: {text_result}")
        else:
            print(f"Response:\n{text_result}")
            print(f"Tokens: {tokens_result}")
        print("------------------------")
    else:
        print("Skipping direct test: OPENAI_API_KEY environment variable not set.")
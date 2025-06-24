import requests
import logging

logger = logging.getLogger(__name__)  # Get a logger instance

def call_mistral(prompt: str, api_key: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # --- IMPORTANT: Tune these parameters based on your needs ---
    max_tokens = 8192 #  Adjust this value based on your needs.  Mistral 7B has a large context window

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",  # ✅ corrected model ID
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,  # DO NOT CHANGE - Leaving original temperature
        "max_tokens": max_tokens,  # Set the maximum number of tokens
        "top_p": 0.9,  # Keep top_p high
        "frequency_penalty": 0.0,  # Prevent repetitive output
        "presence_penalty": 0.0,  # Encourage new topics
        "repetition_penalty": 1.1, # penalize repetition
       "stop": ["\n\n\n"], #Added

    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()

        if "choices" not in response_json or not response_json["choices"]:
            logger.error(f"Unexpected response format: {response_json}")
            return ""  # Or raise an exception if appropriate

        content = response_json["choices"][0]["message"]["content"]
        return content

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return ""  # Or raise, depending on how you want to handle network errors

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error processing response: {e}")
        return ""  # Or raise

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")  # use exception for full traceback
        return ""
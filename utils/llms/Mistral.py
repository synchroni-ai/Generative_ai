# utils/llms/Mistral.py
import json
import requests
import os
from dotenv import load_dotenv
from typing import Tuple, Optional

load_dotenv()

class Mistral: # Encapsulating in a class is good practice, even if only static methods for now
    @staticmethod
    def generate_with_mistral(prompt: str, temperature: float = 0.3, max_tokens: int = 2500, api_key: Optional[str] = None) -> Tuple[str, int]:
        """
        Calls the Together AI API (Mistral model) to generate text.
        Args:
            prompt: The prompt to send to the model.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.
            api_key: API key to use; falls back to TOGETHER_API_KEY env var if None.
        Returns:
            A tuple of (generated_text, total_tokens_used).
            If an error occurs, generated_text will contain an error message and tokens_used will be 0.
        """
        print(f"\n--- LLM DEBUG: Mistral.generate_with_mistral ---")
        print(f"Received prompt (first 300 chars):\n{prompt[:300]}\n")

        client_api_key = api_key or os.getenv("TOGETHER_API_KEY")
        model_name = os.getenv("MISTRAL_MODEL", "mistralai/Mistral-7B-Instruct-v0.2") # Provide a default model

        if not client_api_key:
            error_msg = "ERROR: TOGETHER_API_KEY (for Mistral) not provided or found in environment."
            print(error_msg)
            print(f"--- END LLM DEBUG: Mistral.generate_with_mistral (API KEY ERROR) ---\n")
            return error_msg, 0
        
        # Mask API key for printing
        masked_api_key = f"...{client_api_key[-4:]}" if len(client_api_key) > 4 else "Key_Too_Short"
        print(f"Using API Key ending with: {masked_api_key}")
        print(f"Using Model: {model_name}")


        headers = {
            "Authorization": f"Bearer {client_api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": "You are an expert test case writer. Generate detailed and accurate test cases based on the provided information."},
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # "top_p": top_p, # You had top_p in docstring but not as param, add if needed
        }

        api_url = "https://api.together.xyz/v1/chat/completions"
        print(f"Sending POST request to: {api_url}")
        # print(f"Payload (excluding messages content for brevity): {{'model': '{model_name}', 'temperature': {temperature}, ...}}")

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=120) # Added timeout

            print(f"Response Status Code: {response.status_code}")
            # print(f"Response Headers: {response.headers}") # For more detailed debugging if needed
            # print(f"Response Raw Text (first 500 chars): {response.text[:500]}") # CAREFUL: Might contain sensitive info if error

            response_data = response.json() # Attempt to parse JSON

            if response.status_code == 200:
                generated_content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = response_data.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                
                if not generated_content.strip():
                    print("WARNING: Mistral API returned 200 OK but content is empty.")
                    generated_content = "Error: API returned OK but no content." # Make it an error for upstream
                
                print(f"Mistral API Generated Content (first 300 chars):\n{generated_content[:300]}\n")
                print(f"Total Tokens from API: {total_tokens}")
                print(f"--- END LLM DEBUG: Mistral.generate_with_mistral (SUCCESS) ---\n")
                return generated_content, total_tokens
            else:
                error_detail = response_data.get("error", {}).get("message", response.text) if isinstance(response_data, dict) else response.text
                error_msg = f"API Error ({response.status_code}): {error_detail}"
                print(error_msg)
                print(f"--- END LLM DEBUG: Mistral.generate_with_mistral (API STATUS ERROR) ---\n")
                return error_msg, 0

        except requests.exceptions.RequestException as e_req:
            error_msg = f"Network/Request Error calling Mistral API: {e_req}"
            print(error_msg)
            print(f"--- END LLM DEBUG: Mistral.generate_with_mistral (REQUEST EXCEPTION) ---\n")
            return error_msg, 0
        except json.JSONDecodeError as e_json:
            error_msg = f"JSON Decode Error from Mistral API response. Status: {response.status_code}, Text: {response.text[:200]}"
            print(error_msg)
            print(f"--- END LLM DEBUG: Mistral.generate_with_mistral (JSON DECODE ERROR) ---\n")
            return error_msg, 0
        except Exception as e_unknown:
            import traceback
            error_msg = f"Unexpected Error in Mistral API call: {e_unknown}\n{traceback.format_exc()}"
            print(error_msg)
            print(f"--- END LLM DEBUG: Mistral.generate_with_mistral (UNEXPECTED ERROR) ---\n")
            return error_msg, 0
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


def generate_with_together(prompt, temperature=0.3, max_tokens=800, top_p=0.9):
    """
    Calls the Together AI API to generate text based on a prompt.
    Reads API key from environment variables.
    Args:
        prompt: The prompt to send to the model.
        temperature: Sampling temperature (higher = more creative).
        max_tokens: Maximum number of tokens to generate.
        top_p: Top-p sampling parameter.

    Returns:
        The generated text, or an error message if the API call fails.
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    model_name = os.getenv("LLAMA_MODEL")

    if not api_key:
        return "Error: TOGETHER_API_KEY environment variable not set."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
    }

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload),
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"API Error: {response.status_code}\n{response.text}"

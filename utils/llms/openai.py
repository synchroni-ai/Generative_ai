import openai
import os
from dotenv import load_dotenv

load_dotenv()


def generate_with_openai(
    prompt, model_name="gpt-4", temperature=0.3, max_tokens=500, top_p=0.9, api_key=None
):
    """
    Calls the OpenAI API to generate text based on a prompt.
    Reads API key from environment variables.

    Args:
        prompt: The prompt to send to the model.
        model_name: The name of the OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo").
        temperature: Sampling temperature (higher = more creative).
        max_tokens: Maximum number of tokens to generate.
        top_p: Top-p sampling parameter.

    Returns:
        The generated text, or an error message if the API call fails.
    """
    openai.api_key = api_key or os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        return "Error: OPENAI_API_KEY environment variable not set."

    try:
        client = openai.OpenAI()  # Create OpenAI client

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )

        total_tokens = response.usage.total_tokens

        return response.choices[0].message.content, total_tokens
    except Exception as e:
        return f"API Error: {str(e)}", 0


#hdaedby
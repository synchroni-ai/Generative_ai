# import openai

# def call_gpt4(prompt, api_key, max_tokens=None, temperature=0.7):
#     """
#     Calls the OpenAI GPT-4 chat model with the given prompt and API key.
#     """
#     openai.api_key = api_key

#     try:
#         messages = [
#             {"role": "user", "content": prompt}
#         ]
        
#         kwargs = {
#             "model": "gpt-4",
#             "messages": messages,
#             "temperature": temperature,
#         }
#         if max_tokens is not None:
#             kwargs["max_tokens"] = max_tokens
        
#         response = openai.ChatCompletion.create(**kwargs)
#         # Extract the assistant's reply
#         return response.choices[0].message["content"].strip()
#     except Exception as e:
#         print(f"Error calling GPT-4: {e}")
#         return None
import openai

def call_gpt4(prompt, api_key, model="gpt-4", max_tokens=None, temperature=0.7):
    """
    Calls the OpenAI chat model with the given prompt and API key.
    Supports gpt-4, gpt-3.5-turbo, and gpt-4o
    """
    openai.api_key = api_key

    try:
        messages = [
            {"role": "user", "content": prompt}
        ]

        kwargs = {
            "model": model,  # Use the specified model
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = openai.ChatCompletion.create(**kwargs)
        # Extract the assistant's reply
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error calling GPT-4: {e}")
        return None
import openai


def call_gpt4(prompt: str, api_key: str) -> str:
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.7
    )
    return response.choices[0].message["content"]

import requests


def call_mistral(prompt: str, api_key: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",  # ✅ corrected model ID
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    response = requests.post(url, json=payload, headers=headers)

    # Helpful debug in case of error
    if response.status_code != 200:
        print("❗Response text:", response.text)

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

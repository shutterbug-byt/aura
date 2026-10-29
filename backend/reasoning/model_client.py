from openai import OpenAI
from backend.config import NEBIUS_API_KEY, MODEL_NAME


client = OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/"
)


def ask_model(prompt: str, system_prompt: str = None) -> str:
    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=1024,
    )

    return response.choices[0].message.content
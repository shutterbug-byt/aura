
from openai import OpenAI
from backend.config import NEBIUS_API_KEY, MODEL_NAME


client = OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
)


def ask_model(
    prompt: str,
    system_prompt: str = None,
    max_tokens: int = 1024,
    json_mode: bool = False,
    enable_thinking: bool = True,
) -> str:
    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt,
        })

    messages.append({
        "role": "user",
        "content": prompt,
    })

    request_options = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    if json_mode:
        request_options["response_format"] = {
            "type": "json_object",
        }

    request_options["extra_body"] = {
        "chat_template_kwargs": {
            "enable_thinking": enable_thinking,
        }
    }

    response = client.chat.completions.create(**request_options)

    if not response.choices:
        raise RuntimeError("Nebius returned no completion choices.")

    choice = response.choices[0]
    content = choice.message.content

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(
            "Nebius returned empty content. "
            f"Finish reason: {choice.finish_reason!r}; "
            f"model: {response.model!r}"
        )

    return content.strip()


import os

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "AURA_BACKEND_URL",
    "https://aura-k49o.onrender.com",
).rstrip("/")
API_TOKEN = os.getenv("AURA_API_TOKEN")
VOICE_ENDPOINT = f"{BACKEND_URL}/events/voice"


def send_voice_event(event: dict) -> dict:
    """Send an AURA voice-input event to the configured backend."""
    if not isinstance(event, dict):
        raise TypeError("event must be a dictionary")

    if event.get("event_type") != "voice_input":
        raise ValueError("event_type must be 'voice_input'")

    if not API_TOKEN:
        raise RuntimeError("AURA_API_TOKEN is not set.")

    response = requests.post(
        VOICE_ENDPOINT,
        json=event,
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        timeout=20,
    )

    response.raise_for_status()

    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        body = {"response_text": response.text}

    return {
        "status_code": response.status_code,
        "response": body,
    }



def send_chat_message(message: str) -> dict:
    """Send a transcript to AURA chat and return the generated answer."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")

    if os.getenv("AURA_CHAT_ENABLED", "false").lower() != "true":
        raise RuntimeError(
            "Chat is disabled. Set AURA_CHAT_ENABLED=true only after "
            "confirming that the backend /chat endpoint is available."
        )

    if not API_TOKEN:
        raise RuntimeError("AURA_API_TOKEN is not set.")

    response = requests.post(
        f"{BACKEND_URL}/chat",
        json={"message": message, "conversation_id": None},
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        timeout=60,
    )
    response.raise_for_status()

    body = response.json()
    answer = body.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Backend /chat returned no answer.")

    return {
        "status_code": response.status_code,
        "answer": answer,
        "conversation_id": body.get("conversation_id"),
    }

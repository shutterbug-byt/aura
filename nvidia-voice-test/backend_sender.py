
import requests

BACKEND_URL = "http://127.0.0.1:8000"
VOICE_ENDPOINT = f"{BACKEND_URL}/events/voice"


def send_voice_event(event: dict) -> dict:
    """Send an AURA voice-input event to the backend."""
    if not isinstance(event, dict):
        raise TypeError("event must be a dictionary")

    if event.get("event_type") != "voice_input":
        raise ValueError("event_type must be 'voice_input'")

    response = requests.post(
        VOICE_ENDPOINT,
        json=event,
        timeout=10,
    )
    response.raise_for_status()

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "status_code": response.status_code,
            "response_text": response.text,
        }

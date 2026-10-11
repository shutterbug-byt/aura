
from datetime import datetime, timezone
from uuid import uuid4


EVENT_TYPE = "voice_input"
SOURCE = "nemotron-3.5-asr-streaming-0.6b"


def create_transcript_event(
    transcript: str,
    language: str | None = None,
    confidence: float | None = None,
) -> dict:
    """Convert an ASR transcript into AURA's voice-input event."""
    if not isinstance(transcript, str):
        raise TypeError("transcript must be a string")

    return {
        "event_type": EVENT_TYPE,
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transcript": transcript,
        "language": language,
        "confidence": confidence,
        "source": SOURCE,
    }

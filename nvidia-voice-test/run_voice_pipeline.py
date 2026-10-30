import argparse
import importlib.util
import os
import sys
from pathlib import Path

from nemotron_client import transcribe_file
from backend_sender import send_voice_event
from tts_client import speak_text


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
EVENT_MODULE_PATH = BASE_DIR / "transcript_event.py"

# Allow this script to import AURA's backend package.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



spec = importlib.util.spec_from_file_location(
    "transcript_event",
    EVENT_MODULE_PATH,
)
transcript_event = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transcript_event)


def main():
    parser = argparse.ArgumentParser(
        description="Run AURA's file-based voice pipeline."
    )
    parser.add_argument(
        "audio_path",
        nargs="?",
        default=str(BASE_DIR / "nemotron_test.wav"),
        help="Path to an existing WAV audio file.",
    )
    args = parser.parse_args()

    audio_path = Path(args.audio_path)
    print(f"Audio file: {audio_path}")

    print("\n[1/4] Transcribing audio with local Nemotron ASR...")
    transcript = transcribe_file(audio_path)
    if not transcript.strip():
        raise RuntimeError("ASR returned an empty transcript.")

    print(f"Transcript: {transcript}")

    print("\n[2/4] Creating AURA voice-input event...")
    event = transcript_event.create_transcript_event(transcript)
    print(f"Event ID: {event['event_id']}")

    print("\n[3/4] Sending event to backend...")
    response = send_voice_event(event)
    print(f"Backend response: {response}")

    print("\n[4/4] Using AURA response from backend...")

    backend_body = response.get("response", {})
    if not isinstance(backend_body, dict):
      raise RuntimeError("Backend returned an invalid response body.")

    answer = backend_body.get("answer")

    if not isinstance(answer, str) or not answer.strip():
      raise RuntimeError(
        "Backend /events/voice response did not contain a valid 'answer'."
      )

    print(f"\nAURA: {answer}")
    if not answer or not answer.strip():
        raise RuntimeError("AURA reasoning returned an empty response.")

    print(f"\nAURA: {answer}")

    if os.getenv("AURA_TTS_ENABLED", "true").lower() == "true":
        print("\nSpeaking AURA's response...")
        speak_text(answer)
    else:
        print("\nTTS disabled; response printed to terminal.")


if __name__ == "__main__":
    main()


import argparse
import importlib.util
from pathlib import Path

from nemotron_client import transcribe_file
from backend_sender import send_voice_event


BASE_DIR = Path(__file__).parent
EVENT_MODULE_PATH = BASE_DIR / "transcript_event.py"

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

    print("\n[1/3] Transcribing audio with local Nemotron ASR...")
    transcript = transcribe_file(audio_path)
    if not transcript.strip():
        raise RuntimeError("ASR returned an empty transcript.")

    print(f"Transcript: {transcript}")

    print("\n[2/3] Creating AURA voice-input event...")
    event = transcript_event.create_transcript_event(transcript)
    print(f"Event ID: {event['event_id']}")

    print("\n[3/3] Sending event to backend...")
    response = send_voice_event(event)
    print(f"Backend response: {response}")


if __name__ == "__main__":
    main()

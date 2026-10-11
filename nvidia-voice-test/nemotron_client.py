
import argparse
from pathlib import Path
import requests

import importlib.util
import json
from requests.exceptions import ConnectionError, RequestException


SERVER_URL = "http://127.0.0.1:8080"
DEFAULT_MODEL = "default"

EVENT_MODULE_PATH = Path(__file__).parent / "transcript_event.py"

spec = importlib.util.spec_from_file_location(
    "transcript_event", EVENT_MODULE_PATH
)
transcript_event = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transcript_event)


def transcribe_file(audio_path: str | Path) -> str:
    """Transcribe an existing audio file using the local Nemotron server."""
    path = Path(audio_path)

    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    with path.open("rb") as audio_file:
        response = requests.post(
            f"{SERVER_URL}/v1/audio/transcriptions",
            files={"file": (path.name, audio_file, "audio/wav")},
            data={
                "model": DEFAULT_MODEL,
                "language": "en-US",
                "response_format": "json",
            },
            timeout=120,
        )

    response.raise_for_status()
    result = response.json()
    transcript = result.get("text")

    if not isinstance(transcript, str):
        raise ValueError(f"Unexpected transcription response: {result}")

    return transcript.strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file using local Nemotron ASR."
    )
    parser.add_argument(
        "audio_path",
        nargs="?",
        default=str(Path(__file__).parent / "nemotron_test.wav"),
        help="Path to an existing WAV file",
    )
    args = parser.parse_args()

    print(f"Transcribing: {args.audio_path}")

    transcript = transcribe_file(args.audio_path)
    event = transcript_event.create_transcript_event(transcript)

    print(json.dumps(event, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

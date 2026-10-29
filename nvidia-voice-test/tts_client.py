
import subprocess
import os
from pathlib import Path


BASE_DIR = Path(__file__).parent
NEMO_SPEECH = (
    Path(os.environ["LOCALAPPDATA"])
    / "Programs"
    / "NeMoSpeech"
    / "bin"
    / "nemo-speech.exe"
)


def speak_text(text: str, output_path: Path | None = None) -> Path:
    """Synthesize text into a WAV file and open it for playback."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")

    if not NEMO_SPEECH.is_file():
        raise FileNotFoundError(f"NeMo Speech CLI not found: {NEMO_SPEECH}")

    if output_path is None:
        output_path = BASE_DIR / "aura_response.wav"

    output_path = Path(output_path)

    subprocess.run(
        [
            str(NEMO_SPEECH),
            "synthesize",
            text,
            "--language",
            "en-US",
            "--output",
            str(output_path),
            "--force",
        ],
        check=True,
    )

    os.startfile(str(output_path))
    return output_path

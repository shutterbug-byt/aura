
import base64
import mimetypes
from pathlib import Path

from openai import OpenAI
from backend.config import NEBIUS_API_KEY


VISION_MODEL = "openbmb/MiniCPM-V-4_5"

client = OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
    timeout=60.0,
)


def analyze_image(
    image_path: str,
    prompt: str = "Describe the visible scene briefly.",
) -> str:
    """Analyze a local image and return its visual description."""

    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    mime_type = mimetypes.guess_type(path.name)[0]

    if mime_type not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        raise ValueError(
            "Supported image formats: JPEG, PNG, and WebP."
        )

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    data_url = f"data:{mime_type};base64,{encoded}"

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=256,
    )

    
    if not response.choices:
        raise RuntimeError(
            "Vision model returned no completion choices."
        )

    description = response.choices[0].message.content

    if not isinstance(description, str) or not description.strip():
        raise RuntimeError(
            "Vision model returned an empty or non-text description."
        )

    return description.strip()


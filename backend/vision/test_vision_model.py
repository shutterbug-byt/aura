import base64
import mimetypes
from pathlib import Path

from openai import OpenAI
from backend.config import NEBIUS_API_KEY

image_path = Path("test_vision.jpg")
if not image_path.is_file():
    raise FileNotFoundError("test_vision.jpg not found")

mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")
image_url = f"data:{mime_type};base64,{encoded_image}"

client = OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
    timeout=60.0,
)

response = client.chat.completions.create(
    model="openbmb/MiniCPM-V-4_5",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe the visible scene in one or two sentences."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            ]
        }
    ],
    max_tokens=150,
)

print(response.choices[0].message.content)

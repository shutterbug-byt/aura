
import os
import cv2
import requests


def capture_and_analyze(
    api_url: str = "http://127.0.0.1:8000/vision/analyze",
    camera_index: int = 0,
) -> dict:
    """Capture one webcam frame and send it to AURA's vision API."""

    token = os.getenv("AURA_API_TOKEN")
    if not token:
        raise RuntimeError("AURA_API_TOKEN is not configured.")

    camera = cv2.VideoCapture(camera_index)

    try:
        if not camera.isOpened():
            raise RuntimeError("Could not open the webcam.")

        success, frame = camera.read()
        if not success:
            raise RuntimeError("Could not capture a webcam frame.")

        encoded, image_buffer = cv2.imencode(".jpg", frame)
        if not encoded:
            raise RuntimeError("Could not encode the webcam image.")

        response = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {token}"},
            files={
                "file": (
                    "camera.jpg",
                    image_buffer.tobytes(),
                    "image/jpeg",
                )
            },
            timeout=90,
        )
        response.raise_for_status()
        return response.json()

    finally:
        camera.release()

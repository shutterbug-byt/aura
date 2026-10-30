
from backend.vision.temporal_context import TemporalContext
from backend.vision.scene_summarizer import summarize_scene
from backend.vision.activity_inference import infer_activity
import os
import time
import queue
import threading
from pathlib import Path

import cv2
import requests
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_URL = "http://127.0.0.1:8000/vision/analyze"
CONTEXT_API_URL = "http://127.0.0.1:8000/vision/context"
SAMPLE_INTERVAL = 5.0
REQUEST_TIMEOUT = 90
SUMMARY_INTERVAL = 20.0
ACTIVITY_INFERENCE_INTERVAL = 15.0

def publish_context(session, token, snapshot):
    """Send the latest camera context to the AURA backend."""
    payload = {
        "current_summary": snapshot.get("current_summary", ""),
        "observations": snapshot.get("observations", [])[-20:],
        "observation_count": snapshot.get("observation_count", 0),
        "retention_seconds": snapshot.get("retention_seconds", 60),
    }

    try:
        response = session.post(
            CONTEXT_API_URL,
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[Vision context] Publish failed: {exc}")

def analyze_frames(frame_queue, stop_event, token, context):
    """Analyze sampled frames in the background, independently of capture."""

    session = requests.Session()
    last_summary_time = 0.0
    last_activity_time = 0.0
    previous_activity = ""
    try:
        while not stop_event.is_set():
            try:
                image_bytes = frame_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                response = session.post(
                    API_URL,
                    headers={"Authorization": f"Bearer {token}"},
                    files={
                        "file": ("camera.jpg", image_bytes, "image/jpeg")
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()

                description = response.json().get("description", "")

                if description:
                    context.add_observation(description)

                    snapshot = context.get_context()
                    publish_context(session, token, snapshot)
                    
                    now = time.monotonic()

                    if (
                        snapshot["observation_count"] >= 3
                        and now - last_activity_time >= ACTIVITY_INFERENCE_INTERVAL
                    ):
                        try:
                            activity_result = infer_activity(
                                observations=snapshot["observations"],
                                previous_activity=previous_activity,
                            )

                            activity = activity_result["activity"].strip()

                            if activity and activity.lower() != "unclear":
                                previous_activity = activity

                            last_activity_time = time.monotonic()

                            print("\n[AURA inferred activity]")
                            print(activity or "unclear")

                        except (ValueError, RuntimeError) as exc:
                            print(f"[Activity inference] Could not infer activity: {exc}")


                    print(f"\n[AURA visual observation] {description}")
                    print(
                        f"[Temporal context] "
                        f"{snapshot['observation_count']} observations "
                        f"within the last {snapshot['retention_seconds']} seconds."
                    )

                    now = time.monotonic()
                    if snapshot["observation_count"] >= 3 and now - last_summary_time >= SUMMARY_INTERVAL:
                        last_summary_time = now
                        previous_summary = snapshot["current_summary"]

                        try:
                            scene = summarize_scene(
                                observations=snapshot["observations"],
                                previous_summary=previous_summary,
                            )

                            context.set_summary(scene["summary"])
                            publish_context(session, token, context.get_context())

                            print("\n[AURA current scene]")
                            print(scene["summary"])
                            print("[Recent activity]", scene["recent_activity"])

                            if scene["uncertainties"]:
                                print("[Uncertainties]", "; ".join(scene["uncertainties"]))

                        except (ValueError, RuntimeError) as exc:
                            print(f"[Scene summarizer] Could not update summary: {exc}")
                else:
                    print("[Vision] The API returned no description.")

            except requests.RequestException as exc:
                print(f"[Vision] Request failed: {exc}")
            except (ValueError, AttributeError) as exc:
                print(f"[Vision] Invalid API response: {type(exc).__name__}: {exc}")
                import traceback
                traceback.print_exc()
            finally:
                frame_queue.task_done()
    finally:
        session.close()


def run_continuous_perception():
    token = os.getenv("AURA_API_TOKEN")
    if not token:
        raise RuntimeError("AURA_API_TOKEN is not configured.")

    # Keep at most one waiting frame, so slow requests cannot build a backlog.
    frame_queue = queue.Queue(maxsize=1)
    stop_event = threading.Event()
    context = TemporalContext()

    worker = threading.Thread(
        target=analyze_frames,
        args=(frame_queue, stop_event, token, context),
        name="AURA-Vision-Worker",
        daemon=True,
    )

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam.")

    worker.start()
    print("AURA continuous perception started. Press Q to stop.")
    print(f"Sampling one frame every {SAMPLE_INTERVAL:.0f} seconds.")

    last_sample = time.monotonic()

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("[Camera] Could not read webcam frame.")
                break

            cv2.imshow("AURA - Continuous Perception", frame)

            now = time.monotonic()
            if now - last_sample >= SAMPLE_INTERVAL:
                last_sample = now
                encoded, buffer = cv2.imencode(".jpg", frame)

                if encoded:
                    image_bytes = buffer.tobytes()

                    # Replace an old waiting frame with the newest one.
                    try:
                        frame_queue.put_nowait(image_bytes)
                    except queue.Full:
                        try:
                            frame_queue.get_nowait()
                            frame_queue.task_done()
                        except queue.Empty:
                            pass

                        try:
                            frame_queue.put_nowait(image_bytes)
                        except queue.Full:
                            pass

                    print("[Camera] Frame sampled for visual analysis.")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nStopping AURA perception...")

    finally:
        stop_event.set()
        camera.release()
        cv2.destroyAllWindows()
        worker.join(timeout=2)
        print("AURA camera stopped.")


if __name__ == "__main__":
    run_continuous_perception()

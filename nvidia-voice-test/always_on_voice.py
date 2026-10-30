import os
import queue
import time
import wave
import logging
from pathlib import Path

import numpy as np
import sounddevice as sd

from nemotron_client import transcribe_file
from backend_sender import send_voice_event
from transcript_event import create_transcript_event
from tts_client import speak_text

# Explicitly use the laptop microphone array.
INPUT_DEVICE = 1
SAMPLE_RATE = int(sd.query_devices(INPUT_DEVICE, "input")["default_samplerate"])
CHANNELS = 1
CHUNK_SECONDS = 0.1
SILENCE_SECONDS = 1.0
MIN_SPEECH_SECONDS = 0.35
MAX_SPEECH_SECONDS = 15.0
ENERGY_THRESHOLD = 500
OUTPUT_WAV = Path(__file__).resolve().parent / "live_utterance.wav"

audio_queue = queue.Queue(maxsize=100)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def audio_callback(indata, frames, time_info, status):
    if status:
        logging.warning("Audio status: %s", status)

    chunk = indata[:, 0].copy()

    # Keep the queue bounded; don't let stale audio accumulate.
    if audio_queue.full():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            pass

    try:
        audio_queue.put_nowait(chunk)
    except queue.Full:
        pass


def save_wav(samples):
    audio = np.concatenate(samples)
    audio = np.clip(audio, -32768, 32767).astype(np.int16)

    with wave.open(str(OUTPUT_WAV), "wb") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(audio.tobytes())


def process_utterance(samples):
    save_wav(samples)

    try:
        transcript = transcribe_file(str(OUTPUT_WAV))
        if not isinstance(transcript, str) or not transcript.strip():
            print("No speech recognized. Listening again...")
            return

        transcript = transcript.strip()

        wake_word = "aura"
        if wake_word not in transcript.lower():
           print("Wake phrase not detected. Ignoring background audio.")
           return

        # Remove the wake phrase before sending the command to AURA.
        import re
        transcript = re.sub(
            r"\baura\b", "", transcript, flags=re.IGNORECASE
        ).strip(" ,.!?")

        if not transcript:
            print("Wake phrase detected. Please say your command after AURA.")
            return

        print(f"\nYou: {transcript}")

        event = create_transcript_event(transcript)
        result = send_voice_event(event)

        body = result.get("response", result)
        if not isinstance(body, dict):
            print("AURA returned an unexpected response.")
            return

        answer = body.get("answer", "")
        if body.get("status_code", 200) >= 400 or not answer:
            print("AURA could not generate a response:", body)
            return

        print(f"AURA: {answer}")

               # The existing TTS helper launches playback through Windows.
        # Pause afterward so AURA doesn't immediately hear its own voice.
        try:
            speak_text(answer)
        except Exception as exc:
            print(f"Speech playback failed; text response is still available: {exc}")
            return

        tts_path = Path(__file__).resolve().parent / "aura_response.wav"
        if tts_path.exists():
            with wave.open(str(tts_path), "rb") as wav:
                playback_seconds = wav.getnframes() / wav.getframerate()
            time.sleep(playback_seconds + 0.3)

    except Exception:
        logging.exception("Could not process this utterance")


def main():
    print("AURA always-on voice is starting.")
    print(f"Input: {sd.query_devices(INPUT_DEVICE)['name']}")
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print("Speak naturally. Press Ctrl+C to stop.")

    recording = []
    speech_started = False
    silence_chunks = 0
    max_chunks = int(MAX_SPEECH_SECONDS / CHUNK_SECONDS)
    min_chunks = int(MIN_SPEECH_SECONDS / CHUNK_SECONDS)
    silence_limit = int(SILENCE_SECONDS / CHUNK_SECONDS)

    try:
        with sd.InputStream(
            device=INPUT_DEVICE,
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=int(SAMPLE_RATE * CHUNK_SECONDS),
            callback=audio_callback,
        ):
            print("Listening...")

            while True:
                chunk = audio_queue.get()
                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

                if not speech_started:
                    if rms < ENERGY_THRESHOLD:
                        continue

                    speech_started = True
                    recording = [chunk]
                    silence_chunks = 0
                    print("Speech detected...")
                    continue

                recording.append(chunk)

                if rms < ENERGY_THRESHOLD:
                    silence_chunks += 1
                else:
                    silence_chunks = 0

                finished = silence_chunks >= silence_limit
                too_long = len(recording) >= max_chunks

                if finished or too_long:
                    if len(recording) >= min_chunks:
                        # Temporarily stop consuming queued audio during
                        # ASR, reasoning and TTS; discard stale chunks after.
                        process_utterance(recording)

                    recording = []
                    speech_started = False
                    silence_chunks = 0

                    while not audio_queue.empty():
                        try:
                            audio_queue.get_nowait()
                        except queue.Empty:
                            break

                    print("\nListening...")

    except KeyboardInterrupt:
        print("\nAURA voice listener stopped.")


if __name__ == "__main__":
    main()

import sounddevice as sd
import soundfile as sf
import whisper
import numpy as np

SAMPLE_RATE = 44100
MIC_DEVICE = 1
RECORD_SECONDS = 5

print("Loading Whisper...")
model = whisper.load_model("tiny")
print("Whisper ready.")

print("\nAURA is listening...")
print("Speak normally for 5 seconds.")

audio = sd.rec(
    int(RECORD_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    device=MIC_DEVICE,
)

sd.wait()

sf.write("mic_test.wav", audio, SAMPLE_RATE)

print("Recording complete.")
print("Transcribing...")

result = model.transcribe("mic_test.wav")

text = result["text"].strip()

print("\nAURA HEARD:")
print(text)
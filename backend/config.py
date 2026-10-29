import os
from dotenv import load_dotenv

load_dotenv()

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")

MODEL_NAME = os.getenv(
    "AURA_MODEL",
    "nvidia/Nemotron-3_5-Lightning"
)
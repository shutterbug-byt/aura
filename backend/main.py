
from datetime import datetime, timezone
from typing import Literal

import os
import secrets

from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator

from backend.memory.memory_manager import Memory, MemoryManager
from backend.config import NEBIUS_API_KEY, MODEL_NAME

app = FastAPI(title="AURA")

# Initialize persistent memory
memory_manager = MemoryManager()

# Shared-token authentication for protected API endpoints
def verify_api_token(
    authorization: str | None = Header(default=None),
):
    expected_token = os.getenv("AURA_API_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="API authentication is not configured.",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization token.",
        )

    provided_token = authorization.removeprefix("Bearer ").strip()

    if not secrets.compare_digest(provided_token, expected_token):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization token.",
        )

    return True

# Request model for creating memories
class MemoryCreate(BaseModel):
    memory_id: str
    content: str
    memory_type: Literal["working", "episodic", "long_term", "planning"]
    scope: Literal["global", "contextual"] = "global"
    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=1.0, ge=0, le=1)


# Request model for incoming voice events
class VoiceInputEvent(BaseModel):
    event_type: Literal["voice_input"]
    event_id: str = Field(min_length=1)
    timestamp: datetime
    transcript: str = Field(min_length=1)
    language: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source: str = Field(min_length=1)

    @field_validator("event_id", "source", "transcript")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must not be empty.")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Language must be non-empty or null.")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone.")
        return value


@app.get("/")
def home():
    return {"message": "AURA backend is running!"}


@app.get("/health", dependencies=[Depends(verify_api_token)])
def health():
    return {
        "status": "healthy",
        "service": "AURA",
        "memory_backend": "SQLite",
    }


@app.get("/memory", dependencies=[Depends(verify_api_token)])
def list_memories():
    memories = memory_manager.get_all_memories()

    return {
        "count": len(memories),
        "memories": [
            {
                "memory_id": memory.memory_id,
                "content": memory.content,
                "memory_type": memory.memory_type,
                "scope": memory.scope,
                "importance": memory.importance,
                "confidence": memory.confidence,
            }
            for memory in memories
        ],
    }


@app.post(
    "/memory",
    dependencies=[Depends(verify_api_token)],
)
def create_memory(data: MemoryCreate):
    memory = Memory(
        memory_id=data.memory_id,
        content=data.content,
        memory_type=data.memory_type,
        scope=data.scope,
        importance=data.importance,
        confidence=data.confidence,
    )

    memory_manager.add_memory(memory)

    return {
        "message": "Memory created successfully",
        "memory_id": memory.memory_id,
    }


@app.post("/events/voice", dependencies=[Depends(verify_api_token)])
def receive_voice_event(event: VoiceInputEvent):
    # Validate and acknowledge the incoming voice event.
    # Memory storage and reasoning integration are not implemented here yet.
    received_at = datetime.now(timezone.utc)

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "event_type": event.event_type,
        "received_at": received_at.isoformat(),
    }

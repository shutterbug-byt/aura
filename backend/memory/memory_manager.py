from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Memory:
    memory_id: str
    content: str
    memory_type: str
    scope: str = "global"
    importance: float = 0.5
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime | None = None
    expires_at: datetime | None = None
    source: str | None = None
    related_context: dict[str, Any] = field(default_factory=dict)

class MemoryManager:
    def __init__(self):
        self.memories: dict[str, Memory] = {}

    def add_memory(self, memory: Memory) -> None:
        valid_types = {
            "working",
            "episodic",
            "long_term",
            "planning",
        }

        valid_scopes = {
            "global",
            "contextual",
        }

        if memory.memory_type not in valid_types:
            raise ValueError(
                f"Invalid memory type: {memory.memory_type}"
            )

        if memory.scope not in valid_scopes:
            raise ValueError(
                f"Invalid memory scope: {memory.scope}"
            )

        if memory.scope == "contextual" and not memory.related_context:
            raise ValueError(
                "Contextual memories must have related_context."
            )

        self.memories[memory.memory_id] = memory

    def get_memory(self, memory_id: str) -> Memory | None:
        return self.memories.get(memory_id)

    def get_all_memories(self) -> list[Memory]:
        return list(self.memories.values())

    def delete_memory(self, memory_id: str) -> bool:
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True

        return False

    def remove_expired_memories(self, current_time: datetime | None = None) -> int:
        if current_time is None:
            current_time = datetime.now()

        expired_ids = [
            memory_id
            for memory_id, memory in self.memories.items()
            if memory.expires_at is not None
            and memory.expires_at <= current_time
        ]

        for memory_id in expired_ids:
            del self.memories[memory_id]

        return len(expired_ids)

    def update_memory(self, memory_id: str, **updates) -> bool:
        memory = self.memories.get(memory_id)

        if memory is None:
            return False

        if "memory_type" in updates:
            valid_types = {
                "working",
                "episodic",
                "long_term",
                "planning",
            }

            if updates["memory_type"] not in valid_types:
                raise ValueError(
                    f"Invalid memory type: {updates['memory_type']}"
                )

        for field_name, value in updates.items():
            if hasattr(memory, field_name):
                setattr(memory, field_name, value)

        return True

    def retrieve_memories(
        self,
        context: dict[str, Any] | None = None,
        memory_type: str | None = None,
        min_importance: float = 0.0,
    ) -> list[Memory]:

        current_time = datetime.now()

        results = []

        for memory in self.memories.values():

            # Ignore expired memories
            if (
                memory.expires_at is not None
                and memory.expires_at <= current_time
            ):
                continue

            # Filter by memory type
            if (
                memory_type is not None
                and memory.memory_type != memory_type
            ):
                continue

            # Filter by importance
            if memory.importance < min_importance:
                continue

            # Filter by context
            if context is not None:
                if not self.context_matches(memory, context):
                    continue

            results.append(memory)

        return sorted(
            results,
            key=lambda memory: memory.importance,
            reverse=True,
        )

    def context_matches(
        self,
        memory: Memory,
        context: dict[str, Any],
    ) -> bool:
        if not memory.related_context:
            return True

        for key, expected_value in memory.related_context.items():
            if context.get(key) != expected_value:
                return False

        return True
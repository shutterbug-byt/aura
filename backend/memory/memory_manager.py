
import json
import os
import sqlite3

from contextlib import contextmanager
from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


VALID_MEMORY_TYPES = {
    "working",
    "episodic",
    "long_term",
    "planning",
}

VALID_MEMORY_SCOPES = {
    "global",
    "contextual",
}


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

    def __init__(self, db_path: str | Path | None = None):
        self.database_url = os.getenv("DATABASE_URL")

        # An explicitly supplied db_path means the caller wants SQLite.
        # Otherwise, use PostgreSQL when DATABASE_URL is configured.
        self.use_postgres = db_path is None and bool(self.database_url)

        if self.use_postgres:
            self.db_path = None
        else:
            project_root = Path(__file__).resolve().parents[2]
            default_path = project_root / "data" / "aura_memory.db"

            self.db_path = (
                Path(db_path) if db_path is not None else default_path
            )
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()
        self.memories: dict[str, Memory] = self._load_memories()

    @contextmanager
    def _connect(self):
        """Open and safely close the configured database connection."""
        if self.use_postgres:
            connection = psycopg.connect(
                self.database_url,
                row_factory=dict_row,
                connect_timeout=10,
            )
        else:
            connection = sqlite3.connect(
                str(self.db_path),
                timeout=10,
            )
            connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        if self.use_postgres:
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    importance DOUBLE PRECISION NOT NULL,
                    confidence DOUBLE PRECISION NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    expires_at TEXT,
                    source TEXT,
                    related_context JSONB NOT NULL
                )
            """
        else:
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    importance REAL NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    expires_at TEXT,
                    source TEXT,
                    related_context TEXT NOT NULL
                )
            """

        with self._connect() as connection:
            connection.execute(create_table_sql)
    @staticmethod
    def _datetime_to_text(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def _text_to_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)

    def _validate_memory(self, memory: Memory) -> None:
        if memory.memory_type not in VALID_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type: {memory.memory_type}"
            )

        if memory.scope not in VALID_MEMORY_SCOPES:
            raise ValueError(
                f"Invalid memory scope: {memory.scope}"
            )

        if (
            memory.scope == "contextual"
            and not memory.related_context
        ):
            raise ValueError(
                "Contextual memories must have related_context."
            )

        try:
            json.dumps(memory.related_context)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "related_context must be JSON-serializable."
            ) from exc


    def _save_memory(self, memory: Memory) -> None:
        self._validate_memory(memory)

        values = (
            memory.memory_id,
            memory.content,
            memory.memory_type,
            memory.scope,
            memory.importance,
            memory.confidence,
            self._datetime_to_text(memory.created_at),
            self._datetime_to_text(memory.last_used),
            self._datetime_to_text(memory.expires_at),
            memory.source,
            json.dumps(memory.related_context),
        )

        if self.use_postgres:
            sql = """
                INSERT INTO memories (
                    memory_id, content, memory_type, scope,
                    importance, confidence, created_at, last_used,
                    expires_at, source, related_context
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb
                )
                ON CONFLICT (memory_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    memory_type = EXCLUDED.memory_type,
                    scope = EXCLUDED.scope,
                    importance = EXCLUDED.importance,
                    confidence = EXCLUDED.confidence,
                    created_at = EXCLUDED.created_at,
                    last_used = EXCLUDED.last_used,
                    expires_at = EXCLUDED.expires_at,
                    source = EXCLUDED.source,
                    related_context = EXCLUDED.related_context
            """
        else:
            sql = """
                INSERT INTO memories (
                    memory_id, content, memory_type, scope,
                    importance, confidence, created_at, last_used,
                    expires_at, source, related_context
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    content = excluded.content,
                    memory_type = excluded.memory_type,
                    scope = excluded.scope,
                    importance = excluded.importance,
                    confidence = excluded.confidence,
                    created_at = excluded.created_at,
                    last_used = excluded.last_used,
                    expires_at = excluded.expires_at,
                    source = excluded.source,
                    related_context = excluded.related_context
            """

        with self._connect() as connection:
            connection.execute(sql, values)


    def _load_memories(self) -> dict[str, Memory]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM memories"
            ).fetchall()

        loaded: dict[str, Memory] = {}

        for row in rows:
            related_context = row["related_context"]

            if isinstance(related_context, str):
                related_context = json.loads(related_context)

            memory = Memory(
                memory_id=row["memory_id"],
                content=row["content"],
                memory_type=row["memory_type"],
                scope=row["scope"],
                importance=row["importance"],
                confidence=row["confidence"],
                created_at=self._text_to_datetime(row["created_at"]),
                last_used=self._text_to_datetime(row["last_used"]),
                expires_at=self._text_to_datetime(row["expires_at"]),
                source=row["source"],
                related_context=related_context,
            )

            loaded[memory.memory_id] = memory

        return loaded


    def add_memory(self, memory: Memory) -> None:
        self._validate_memory(memory)
        self._save_memory(memory)
        self.memories[memory.memory_id] = memory

    def get_memory(self, memory_id: str) -> Memory | None:
        return self.memories.get(memory_id)

    def get_all_memories(self) -> list[Memory]:
        return list(self.memories.values())


    def delete_memory(self, memory_id: str) -> bool:
        if memory_id not in self.memories:
            return False

        placeholder = "%s" if self.use_postgres else "?"

        with self._connect() as connection:
            connection.execute(
                f"DELETE FROM memories WHERE memory_id = {placeholder}",
                (memory_id,),
            )

        del self.memories[memory_id]
        return True


    def remove_expired_memories(
        self,
        current_time: datetime | None = None,
    ) -> int:
        if current_time is None:
            current_time = datetime.now()

        expired_ids = [
            memory_id
            for memory_id, memory in self.memories.items()
            if (
                memory.expires_at is not None
                and memory.expires_at <= current_time
            )
        ]

        if not expired_ids:
            return 0

        placeholder = "%s" if self.use_postgres else "?"

        with self._connect() as connection:
            connection.executemany(
                f"DELETE FROM memories WHERE memory_id = {placeholder}",
                [(memory_id,) for memory_id in expired_ids],
            )

        for memory_id in expired_ids:
            del self.memories[memory_id]

        return len(expired_ids)


    def update_memory(self, memory_id: str, **updates) -> bool:
        memory = self.memories.get(memory_id)

        if memory is None:
            return False


        allowed_fields = {
            item.name for item in fields(Memory)
        }

        if "memory_id" in updates:
            raise ValueError("memory_id cannot be changed.")

        unknown_fields = set(updates) - allowed_fields


        if unknown_fields:
            raise ValueError(
                f"Unknown memory fields: {sorted(unknown_fields)}"
            )

        # Build and validate a replacement before modifying current state.
        values = {
            item.name: getattr(memory, item.name)
            for item in fields(Memory)
        }
        values.update(updates)

        candidate = Memory(**values)
        self._validate_memory(candidate)

        # Persist first. Only update the in-memory copy after saving works.
        self._save_memory(candidate)
        self.memories[memory_id] = candidate

        return True

    def retrieve_memories(
        self,
        context: dict[str, Any] | None = None,
        memory_type: str | None = None,
        min_importance: float = 0.0,
    ) -> list[Memory]:
        if (
            memory_type is not None
            and memory_type not in VALID_MEMORY_TYPES
        ):
            raise ValueError(
                f"Invalid memory type: {memory_type}"
            )

        current_time = datetime.now()
        results = []

        for memory in self.memories.values():
            # Ignore expired memories.
            if (
                memory.expires_at is not None
                and memory.expires_at <= current_time
            ):
                continue

            # Filter by memory type.
            if (
                memory_type is not None
                and memory.memory_type != memory_type
            ):
                continue

            # Filter by importance.
            if memory.importance < min_importance:
                continue

            # Filter by context.
            if (
                context is not None
                and not self.context_matches(memory, context)
            ):
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
        # Global memories with no related context match any context.
        if not memory.related_context:
            return True

        for key, expected_value in memory.related_context.items():
            if context.get(key) != expected_value:
                return False

        return True

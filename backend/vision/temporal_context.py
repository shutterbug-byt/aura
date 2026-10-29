
import os
import time
import threading
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class VisualObservation:
    timestamp: float
    description: str


class TemporalContext:
    """In-memory rolling history of AURA's visual observations."""

    def __init__(self, retention_seconds: int | None = None):
        if retention_seconds is None:
            retention_seconds = int(
                os.getenv("AURA_VISION_RETENTION_SECONDS", "60")
            )

        if retention_seconds < 1:
            raise ValueError("Retention duration must be at least 1 second.")

        self.retention_seconds = retention_seconds
        self._observations = deque()
        self._lock = threading.Lock()
        self._latest_summary = ""

    def _expire_old_observations(self, now: float) -> None:
        cutoff = now - self.retention_seconds

        while (
            self._observations
            and self._observations[0].timestamp < cutoff
        ):
            self._observations.popleft()

    def add_observation(
        self,
        description: str,
        timestamp: float | None = None,
    ) -> None:
        description = description.strip()

        if not description:
            return

        now = time.monotonic() if timestamp is None else timestamp

        with self._lock:
            self._expire_old_observations(now)
            self._observations.append(
                VisualObservation(
                    timestamp=now,
                    description=description,
                )
            )
            self._expire_old_observations(now)

    def set_summary(self, summary: str) -> None:
        """Update the current scene summary independently of history expiry."""
        with self._lock:
            self._latest_summary = summary.strip()

    def get_context(self) -> dict:
        """Return a snapshot of recent observations and the current summary."""
        now = time.monotonic()

        with self._lock:
            self._expire_old_observations(now)

            observations = [
                {
                    "age_seconds": round(now - item.timestamp, 1),
                    "description": item.description,
                }
                for item in self._observations
            ]

            return {
                "retention_seconds": self.retention_seconds,
                "observation_count": len(observations),
                "observations": observations,
                "current_summary": self._latest_summary,
            }

    def clear_observations(self) -> None:
        """Clear recent observations without deleting the current summary."""
        with self._lock:
            self._observations.clear()

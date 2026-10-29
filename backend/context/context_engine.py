from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ContextState:
    location: str | None = None
    activity: str | None = None
    confidence: float = 0.0

    previous_activity: str | None = None
    previous_activity_state: str | None = None

    last_updated: datetime | None = None

    signals: dict[str, Any] = field(default_factory=dict)


class ContextEngine:

    def __init__(self, world_state=None):
        self.world_state = world_state

        # ContextState represents the latest context transition.
        # WorldState is the persistent application-level source of truth.
        self.state = ContextState()

    def process_event(self, event: dict[str, Any]) -> ContextState:
        """
        Process a structured perception/context event and update
        the user's current context.
        """

        event_type = event.get("event_type")
        data = event.get("data", {})

        if event_type == "location_change":
            self._handle_location_change(data)

        elif event_type == "activity":
            self._handle_activity_change(data)

        elif event_type == "observation":
            self._handle_observation(data)

        event_timestamp = event.get("timestamp")

        if event_timestamp:
            self.state.last_updated = datetime.fromisoformat(event_timestamp)
        else:
            self.state.last_updated = datetime.now()

        if self.world_state:
            self.world_state.update_context(self.state)

        return self.state

    def _handle_location_change(self, data: dict[str, Any]):
        location = data.get("location")

        if location:
            self.state.location = location

    def _handle_activity_change(self, data: dict[str, Any]):
        activity = data.get("activity")
        confidence = data.get("confidence", 0.0)

        if not activity:
            return

        if activity != self.state.activity:

            self.state.previous_activity = self.state.activity

            self.state.previous_activity_state = (
                "unknown" if self.state.activity else None
            )

            self.state.activity = activity
            self.state.confidence = confidence

    def _handle_observation(self, data: dict[str, Any]):
        """
        Store compact signals without automatically turning
        observations into memories.
        """

        self.state.signals.update(data)

    def get_state(self) -> dict[str, Any]:
        return {
            "location": self.state.location,
            "activity": self.state.activity,
            "confidence": self.state.confidence,
            "previous_activity": self.state.previous_activity,
            "previous_activity_state": self.state.previous_activity_state,
            "last_updated": (
                self.state.last_updated.isoformat()
                if self.state.last_updated
                else None
            ),
            "signals": self.state.signals,
        }
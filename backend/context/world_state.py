from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CurrentContext:
    location: str | None = None
    activity: str | None = None
    confidence: float = 0.0
    active_task_id: str | None = None
    last_updated: datetime | None = None


@dataclass
class ActiveTask:
    task_id: str
    description: str
    status: str = "pending"
    priority: str = "normal"
    deadline: datetime | None = None


@dataclass
class UpcomingEvent:
    event_id: str
    description: str
    start_time: datetime
    importance: str = "normal"


@dataclass
class WorldState:
    current_context: CurrentContext = field(
        default_factory=CurrentContext
    )

    active_tasks: list[ActiveTask] = field(
        default_factory=list
    )

    upcoming_events: list[UpcomingEvent] = field(
        default_factory=list
    )

    active_signals: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_context": {
                "location": self.current_context.location,
                "activity": self.current_context.activity,
                "confidence": self.current_context.confidence,
                "previous_activity": self.current_context.previous_activity,
                "previous_activity_state": self.current_context.previous_activity_state,
                "active_task_id": self.current_context.active_task_id,
                "last_updated": (
                    self.current_context.last_updated.isoformat()
                    if self.current_context.last_updated
                    else None
                ),
            },
            "active_tasks": [
                {
                    "task_id": task.task_id,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "deadline": (
                        task.deadline.isoformat()
                        if task.deadline
                        else None
                    ),
                }
                for task in self.active_tasks
            ],
            "upcoming_events": [
                {
                    "event_id": event.event_id,
                    "description": event.description,
                    "start_time": event.start_time.isoformat(),
                    "importance": event.importance,
                }
                for event in self.upcoming_events
            ],
            "active_signals": self.active_signals,
        }

    def update_context(self, context_state):
        self.current_context.location = context_state.location
        self.current_context.activity = context_state.activity
        self.current_context.confidence = context_state.confidence
        self.current_context.last_updated = context_state.last_updated
        self.current_context.previous_activity = context_state.previous_activity
        self.current_context.previous_activity_state = context_state.previous_activity_state
        self.active_signals = context_state.signals.copy()
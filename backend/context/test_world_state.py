from datetime import datetime

from backend.context.world_state import (
    WorldState,
    CurrentContext,
    ActiveTask,
    UpcomingEvent,
)


def main():
    world = WorldState()

    world.current_context = CurrentContext(
        location="kitchen",
        activity="cooking",
        confidence=0.97,
        active_task="cook dinner",
        last_updated=datetime.fromisoformat(
            "2026-10-08T22:00:00"
        ),
    )

    world.active_tasks.append(
        ActiveTask(
            task_id="task_001",
            description="Finish Java assignment",
            status="in_progress",
            priority="high",
        )
    )

    world.upcoming_events.append(
        UpcomingEvent(
            event_id="event_001",
            description="Computer Networks quiz",
            start_time=datetime.fromisoformat(
                "2026-10-09T10:00:00"
            ),
            importance="high",
        )
    )

    world.active_signals["stove_on"] = True

    print(world.to_dict())


if __name__ == "__main__":
    main()
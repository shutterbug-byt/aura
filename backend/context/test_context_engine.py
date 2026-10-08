from backend.context.context_engine import ContextEngine
from backend.context.world_state import WorldState

def print_state(label, state):
    print(f"\n--- {label} ---")
    print(state)


def main():
    world_state = WorldState()
    engine = ContextEngine(world_state)

    # 1. User starts Java work
    engine.process_event({
        "timestamp": "2026-10-08T10:00:00",
        "source": "screen",
        "event_type": "activity",
        "data": {
            "activity": "java_work",
            "confidence": 0.95
        }
    })

    print_state("Java work started", engine.get_state())

    # 2. User pauses Java
    engine.process_event({
        "timestamp": "2026-10-08T10:25:00",
        "source": "screen",
        "event_type": "observation",
        "data": {
            "keyboard_activity": False,
            "java_ide_open": True
        }
    })

    print_state("Java paused", engine.get_state())

    # 3. User moves to kitchen
    engine.process_event({
        "timestamp": "2026-10-08T10:27:00",
        "source": "camera",
        "event_type": "location_change",
        "data": {
            "location": "kitchen"
        }
    })

    print_state("Moved to kitchen", engine.get_state())

    # 4. Food preparation begins
    engine.process_event({
        "timestamp": "2026-10-08T10:35:00",
        "source": "camera",
        "event_type": "activity",
        "data": {
            "activity": "food_preparation",
            "confidence": 0.94
        }
    })

    print_state("Food preparation", engine.get_state())

    # 5. Cooking begins
    engine.process_event({
        "timestamp": "2026-10-08T10:42:00",
        "source": "camera",
        "event_type": "activity",
        "data": {
            "activity": "cooking",
            "confidence": 0.97
        }
    })

    print_state("Cooking", engine.get_state())
    print_state("World State", world_state.to_dict())


if __name__ == "__main__":
    main()
from backend.context.world_state import WorldState
from backend.memory.memory_manager import MemoryManager
from backend.reasoning.model_client import ask_model


SYSTEM_PROMPT = """
You are AURA, a private personal AI assistant.
Answer the user's request using the supplied current context and relevant memories.
Do not invent facts, retrieved information, or completed actions.
Be concise and practical. Ask a clarifying question when essential information is missing.
"""


def answer_user(
    message: str,
    world_state: WorldState | None = None,
    memory_manager: MemoryManager | None = None,
) -> str:
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")

    world_state = world_state or WorldState()
    memory_manager = memory_manager or MemoryManager()

    current = world_state.current_context
    state = {
        "current_context": {
            "location": current.location,
            "activity": current.activity,
            "confidence": current.confidence,
            "active_task_id": current.active_task_id,
            "last_updated": (
                current.last_updated.isoformat()
                if current.last_updated else None
            ),
        },
        "active_tasks": [
            {
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
            }
            for task in world_state.active_tasks
        ],
        "upcoming_events": [
            {
                "event_id": event.event_id,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "importance": event.importance,
            }
            for event in world_state.upcoming_events
        ],
        "active_signals": world_state.active_signals,
    }

    memory_context = {}
    if current.activity:
        memory_context["activity"] = current.activity

    memories = memory_manager.retrieve_memories(
        context=memory_context or None,
        min_importance=0.2,
    )

    memory_text = "\n".join(
        f"- {memory.content}" for memory in memories[:8]
    ) or "No relevant memories retrieved."

    prompt = f"""
CURRENT WORLD STATE:
{state}

RELEVANT RETRIEVED MEMORIES:
{memory_text}

USER MESSAGE:
{message}

Answer directly. Use context only when relevant. If a requested tool
is unavailable, do not claim to have performed its action.
"""

    return ask_model(prompt, system_prompt=SYSTEM_PROMPT).strip()

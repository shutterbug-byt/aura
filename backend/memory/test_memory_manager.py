from datetime import datetime, timedelta

from backend.memory.memory_manager import Memory, MemoryManager


def main():
    manager = MemoryManager()

    # ---------------------------------------------------------
    # 1. Expiration Test
    # ---------------------------------------------------------

    expired_memory = Memory(
        memory_id="mem_expired",
        content="Temporary test memory",
        memory_type="working",
        importance=0.3,
        expires_at=datetime.now() - timedelta(minutes=1),
    )

    active_memory = Memory(
        memory_id="mem_active",
        content="Active test memory",
        memory_type="working",
        importance=0.5,
        expires_at=datetime.now() + timedelta(hours=1),
    )

    manager.add_memory(expired_memory)
    manager.add_memory(active_memory)

    print("\n--- Expiration ---")
    print("Removed:", manager.remove_expired_memories())
    print("Expired memory:", manager.get_memory("mem_expired"))
    print("Active memory:", manager.get_memory("mem_active"))

    # ---------------------------------------------------------
    # 2. Add + Update Memory
    # ---------------------------------------------------------

    memory = Memory(
        memory_id="mem_001",
        content="User is working on the AURA project.",
        memory_type="long_term",
        importance=0.9,
        confidence=1.0,
        source="user",
    )

    manager.add_memory(memory)

    print("\n--- Update Memory ---")

    updated = manager.update_memory(
        "mem_001",
        content="User is working on the AURA memory system.",
        importance=1.0,
    )

    print("Updated:", updated)
    print("Memory:", manager.get_memory("mem_001"))

    # ---------------------------------------------------------
    # 3. Invalid Memory Type Update
    # ---------------------------------------------------------

    print("\n--- Invalid Memory Type Update ---")

    try:
        manager.update_memory(
            "mem_001",
            memory_type="banana"
        )

    except ValueError as error:
        print("Rejected:", error)

    print(
        "Memory after invalid update:",
        manager.get_memory("mem_001")
    )

    # ---------------------------------------------------------
    # 4. Invalid Memory Type on Add
    # ---------------------------------------------------------

    print("\n--- Invalid Memory Type ---")

    try:
        invalid_memory = Memory(
            memory_id="mem_invalid",
            content="This should not be stored.",
            memory_type="banana",
            importance=0.2,
        )

        manager.add_memory(invalid_memory)

    except ValueError as error:
        print("Rejected:", error)

    # ---------------------------------------------------------
    # 5. Retrieval Test Data
    # ---------------------------------------------------------
    manager.add_memory(
        Memory(
            memory_id="mem_vegetarian",
            content="User prefers vegetarian food.",
            memory_type="long_term",
            scope="global",
            importance=0.9,
        )
    )
    manager.add_memory(
        Memory(
            memory_id="mem_java",
            content="User is working on Java inheritance.",
            memory_type="long_term",
            scope="contextual",
            importance=0.8,
            related_context={
                "activity": "java_work"
            }
        )
    )

    manager.add_memory(
        Memory(
            memory_id="mem_cooking",
            content="User is currently learning a paneer recipe.",
            memory_type="episodic",
            scope="contextual",
            importance=0.6,
            related_context={
                "activity": "cooking"
            }
        )
    )

    manager.add_memory(
        Memory(
            memory_id="mem_low",
            content="Minor temporary detail.",
            memory_type="working",
            scope="contextual",
            importance=0.2,
            related_context={
                "activity": "java_work"
            }
        )
    )

    expired_retrieval_memory = Memory(
        memory_id="mem_expired_retrieval",
        content="Expired Java memory.",
        memory_type="long_term",
        importance=1.0,
        expires_at=datetime.now() - timedelta(minutes=1),
        related_context={
            "activity": "java_work"
        },
    )

    manager.add_memory(expired_retrieval_memory)

    # ---------------------------------------------------------
    # 6. Retrieval by Context
    # ---------------------------------------------------------

    print("\n--- Retrieval: Java Context ---")

    java_memories = manager.retrieve_memories(
        context={
            "activity": "java_work",
        }
    )

    for item in java_memories:
        print(item)

    # ---------------------------------------------------------
    # 7. Retrieval by Importance
    # ---------------------------------------------------------

    print("\n--- Retrieval: High Importance ---")

    important_memories = manager.retrieve_memories(
        min_importance=0.7,
    )

    for item in important_memories:
        print(item)

    print("\n--- Context Matching ---")

    java_memory = manager.get_memory("mem_java")

    print(
        "Matching context:",
        manager.context_matches(
            java_memory,
            {
                "activity": "java_work",
            },
        ),
    )

    print(
        "Non-matching context:",
        manager.context_matches(
            java_memory,
            {
                "activity": "cooking",
            },
        ),
    )

    # ---------------------------------------------------------
    # 8. All Memories
    # ---------------------------------------------------------

    print("\n--- All Memories ---")
    print(manager.get_all_memories())

    # ---------------------------------------------------------
    # 9. Delete Memory
    # ---------------------------------------------------------

    print("\n--- Delete Memory ---")
    print(manager.delete_memory("mem_001"))

    print("\n--- After Deletion ---")
    print(manager.get_memory("mem_001"))


if __name__ == "__main__":
    main()
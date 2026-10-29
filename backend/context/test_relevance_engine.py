from backend.context.relevance_engine import RelevanceEngine
from backend.memory.memory_manager import Memory


def main():

    engine = RelevanceEngine()

    # ---------------------------------------------------------
    # Test Memories
    # ---------------------------------------------------------

    vegetarian = Memory(
        memory_id="mem_vegetarian",
        content="User prefers vegetarian food.",
        memory_type="long_term",
        scope="global",
        importance=0.9,
        confidence=1.0,
    )

    java = Memory(
        memory_id="mem_java",
        content="User is learning Java inheritance.",
        memory_type="long_term",
        scope="contextual",
        importance=0.8,
        confidence=1.0,
        related_context={
            "activity": "java_work"
        },
    )

    cooking = Memory(
        memory_id="mem_cooking",
        content="User was learning a paneer recipe.",
        memory_type="episodic",
        scope="contextual",
        importance=0.7,
        confidence=0.9,
        related_context={
            "activity": "cooking"
        },
    )

    unrelated = Memory(
        memory_id="mem_unrelated",
        content="User was studying networking.",
        memory_type="episodic",
        scope="contextual",
        importance=0.9,
        confidence=1.0,
        related_context={
            "activity": "networking"
        },
    )

    # ---------------------------------------------------------
    # Current Context = Cooking
    # ---------------------------------------------------------

    context = {
        "activity": "cooking",
        "location": "kitchen",
    }

    memories = [
        vegetarian,
        java,
        cooking,
        unrelated,
    ]

    # ---------------------------------------------------------
    # Rank
    # ---------------------------------------------------------

    ranked = engine.rank_memories(
        memories,
        context,
    )

    print("\n--- Ranked Memories ---")

    for item in ranked:

        print(
            f"{item.memory.memory_id} | "
            f"score={item.score:.2f} | "
            f"reasons={item.reasons}"
        )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    ids = [
        item.memory.memory_id
        for item in ranked
    ]

    print("\n--- Assertions ---")

    assert "mem_cooking" in ids
    print("Cooking memory included: PASS")

    assert "mem_vegetarian" in ids
    print("Global vegetarian memory included: PASS")

    assert "mem_java" not in ids
    print("Java memory excluded: PASS")

    assert "mem_unrelated" not in ids
    print("Networking memory excluded: PASS")

    print("\nAll relevance tests passed.")


if __name__ == "__main__":
    main()
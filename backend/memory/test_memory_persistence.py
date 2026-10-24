
import tempfile
from pathlib import Path

from backend.memory.memory_manager import Memory, MemoryManager


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_memory.db"

        # Step 1: Create a manager and save a memory.
        manager1 = MemoryManager(db_path=db_path)

        manager1.add_memory(
            Memory(
                memory_id="persistence_test_001",
                content="AURA persistence test memory",
                memory_type="long_term",
                scope="global",
                importance=0.9,
                confidence=1.0,
            )
        )

        assert manager1.get_memory("persistence_test_001") is not None
        print("Memory saved: PASS")

        # Step 2: Create a NEW manager using the same database.
        manager2 = MemoryManager(db_path=db_path)

        restored = manager2.get_memory("persistence_test_001")

        assert restored is not None, "Memory was not restored from the database."
        assert restored.content == "AURA persistence test memory"
        print("Memory survives manager restart: PASS")
        print("Persisted content verified: PASS")

    print("\nMemory persistence tests completed.")


if __name__ == "__main__":
    main()

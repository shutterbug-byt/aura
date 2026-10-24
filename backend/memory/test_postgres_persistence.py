
from dotenv import load_dotenv

load_dotenv(override=True)

from backend.memory.memory_manager import Memory, MemoryManager


def main():
    # db_path=None selects PostgreSQL when DATABASE_URL is configured.
    manager1 = MemoryManager(db_path=None)

    test_id = "aura_postgres_persistence_check"

    try:
        manager1.add_memory(
            Memory(
                memory_id=test_id,
                content="AURA PostgreSQL persistence verification",
                memory_type="long_term",
                scope="global",
                importance=0.9,
                confidence=1.0,
            )
        )
        print("PostgreSQL memory save: PASS")

        # Create a fresh manager to verify the database can restore it.
        manager2 = MemoryManager(db_path=None)
        restored = manager2.get_memory(test_id)

        assert restored is not None, "Memory was not restored."
        assert restored.content == (
            "AURA PostgreSQL persistence verification"
        )

        print("PostgreSQL memory reload: PASS")
        print("PostgreSQL persistence: PASS")

    finally:
        # Remove only this test record.
        cleanup_manager = MemoryManager(db_path=None)
        cleanup_manager.delete_memory(test_id)


if __name__ == "__main__":
    main()

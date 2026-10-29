
import tempfile
from pathlib import Path
from unittest.mock import patch

from backend.agent.memory_augmented_response import (
    MemoryAugmentedResponse,
)
from backend.memory.memory_manager import Memory, MemoryManager
from backend.context.relevance_engine import RelevanceEngine


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_memory.db"
        manager = MemoryManager(db_path=db_path)

        manager.add_memory(
            Memory(
                memory_id="test_vegetarian",
                content="The user prefers vegetarian food.",
                memory_type="long_term",
                scope="global",
                importance=0.9,
                confidence=1.0,
            )
        )

        manager.add_memory(
            Memory(
                memory_id="test_cooking",
                content="The user is currently learning to cook paneer.",
                memory_type="episodic",
                scope="contextual",
                importance=0.8,
                confidence=1.0,
                related_context={"activity": "cooking"},
            )
        )

        response_generator = MemoryAugmentedResponse(
            memory_manager=manager,
            relevance_engine=RelevanceEngine(),
        )

        with patch(
            "backend.agent.memory_augmented_response.ask_model",
            return_value="Try a vegetarian paneer dinner with lentils.",
        ) as mock_model:
            answer = response_generator.answer(
                question="Suggest a high-protein vegetarian dinner.",
                context={"activity": "cooking"},
            )

            assert answer == (
                "Try a vegetarian paneer dinner with lentils."
            )
            mock_model.assert_called_once()

            prompt_sent = mock_model.call_args.kwargs["prompt"]

            
            assert "The user prefers vegetarian food." in prompt_sent
            assert (
                "The user is currently learning to cook paneer."
                not in prompt_sent
            )

            assert "Suggest a high-protein vegetarian dinner." in prompt_sent

            print("Response generation: PASS")
            print("Relevant memories included: PASS")
            print("User question included: PASS")
            print("Mock model called once: PASS")

    print("\nMemory-augmented response tests completed.")


if __name__ == "__main__":
    main()

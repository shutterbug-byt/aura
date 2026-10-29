
from pathlib import Path

from backend.rag.rag_pipeline import answer_from_documents



def main():
    from pathlib import Path
    from backend.rag.rag_pipeline import answer_from_documents

    sample_path = Path(__file__).parent / "sample_notes.txt"

    result = answer_from_documents(
        question="How does TCP provide reliable data delivery, and how does AES-256 encrypt data?",
        file_paths=[str(sample_path)],
    )

    print("\n--- Question ---")
    print(result["question"])

    print("\n--- Answer ---")
    print(result["answer"])

    print("\n--- Sources ---")
    print(result["sources"])

    print("\n--- Retrieved Chunks ---")
    print(len(result["retrieved_chunks"]))

    if result["retrieved_chunks"]:
        assert "sample_notes.txt" in result["sources"]
        print("Relevant chunks found; source tracking: PASS")
    else:
        assert not result["sources"]
        print("No relevant chunks found; fallback handling: PASS")

    
    answer = result["answer"].lower()

    assert answer.strip(), "The answer must not be empty."

    assert (
        "tcp" in answer
        or "acknowledgments" in answer
        or "retransmissions" in answer
    ), "The answer should address the TCP portion."

    
    assert (
        "cannot answer" in answer
        or "not contain" in answer
        or "not mention" in answer
        or "no information" in answer
        or "not enough information" in answer
        or "not supported" in answer
        or "insufficient evidence" in answer
        or "given evidence" in answer
    ), "The answer should acknowledge the missing AES-256 evidence."


    print("\nRAG answer-grounding test: PASS")



if __name__ == "__main__":
    main()

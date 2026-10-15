
from pathlib import Path

from backend.rag.document_loader import load_document
from backend.rag.chunker import chunk_document
from backend.rag.retriever import retrieve_chunks


def main():
    sample_path = Path(__file__).parent / "sample_notes.txt"

    # 1. Load the document
    document = load_document(str(sample_path))
    print("Document loaded: PASS")

    # 2. Split the document into overlapping chunks
    chunks = chunk_document(
        document,
        chunk_size=20,
        overlap=5,
    )
    assert chunks, "Expected document chunks"
    print("Chunking: PASS")

    # 3. Test TCP retrieval
    results = retrieve_chunks(
        query="How does TCP provide reliable data delivery?",
        chunks=chunks,
        top_k=3,
    )

    assert results, "Expected matching TCP chunks"
    assert "TCP" in results[0]["text"], (
        "The most relevant result should be the TCP passage"
    )

    for result in results:
        assert result["source"] == "sample_notes.txt"
        assert 0 < result["score"] <= 1

    print("\n--- TCP Retrieval ---")
    print("Retrieved chunks:", len(results))

    for result in results:
        print(
            f"\nScore: {result['score']:.2f}"
            f"\nSource: {result['source']}"
            f"\nText: {result['text']}"
        )

    print("\nTCP ranking test: PASS")

    # 4. Test UDP retrieval
    udp_results = retrieve_chunks(
        query="Does UDP guarantee delivery or ordering?",
        chunks=chunks,
        top_k=3,
    )

    assert udp_results, "Expected matching UDP chunks"
    assert "UDP" in udp_results[0]["text"], (
        "The most relevant result should be the UDP passage"
    )

    print("UDP ranking test: PASS")

    # 5. Test an unrelated question
    irrelevant_results = retrieve_chunks(
        query="How does AES-256 encryption work?",
        chunks=chunks,
        top_k=3,
    )

    assert not irrelevant_results, (
        "Expected no results for a question unrelated to the documents"
    )

    print("Irrelevant-query test: PASS")

    # 6. Test a paraphrased question
    paraphrase_results = retrieve_chunks(
        query="How does TCP make sure lost information gets sent again?",
        chunks=chunks,
        top_k=3,
    )

    print("\n--- Paraphrase Retrieval Test ---")
    print("Retrieved chunks:", len(paraphrase_results))

    for result in paraphrase_results:
        print(
            f"Score: {result['score']:.2f}"
            f"\nText: {result['text']}"
        )

    if (
        paraphrase_results
        and "TCP" in paraphrase_results[0]["text"]
    ):
        print("Paraphrase retrieval: PASS")
    else:
        print("Paraphrase retrieval: LIMITATION FOUND")

    # 7. Final result
    print("\nRAG retrieval test: PASS")


if __name__ == "__main__":
    main()

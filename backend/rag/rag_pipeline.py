
from backend.rag.document_loader import load_document
from backend.rag.chunker import chunk_document
from backend.rag.retriever import retrieve_chunks
from backend.reasoning.model_client import ask_model


SYSTEM_PROMPT = """
You are AURA's document-grounded question-answering system.

Answer the user's question using the supplied document passages.

Rules:
1. Treat the supplied passages as the evidence for document-based answers.
2. Do not invent facts or claim the document says something it does not.
3. If the passages do not contain enough information, clearly say so.
4. Distinguish information supported by the passages from any uncertainty.
5. Keep the answer clear and concise.
"""


def answer_from_documents(
    question: str,
    file_paths: list[str],
    top_k: int = 3,
) -> dict:
    """
    Load documents, retrieve relevant chunks, and ask Nemotron
    to answer using the retrieved passages.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not file_paths:
        raise ValueError("At least one document is required")

    all_chunks = []

    for file_path in file_paths:
        document = load_document(file_path)
        chunks = chunk_document(document)
        all_chunks.extend(chunks)

    retrieved_chunks = retrieve_chunks(
        query=question,
        chunks=all_chunks,
        top_k=top_k,
    )

    if not retrieved_chunks:
        return {
            "question": question,
            "answer": (
                "I couldn't find relevant information in the "
                "provided documents to answer that question."
            ),
            "sources": [],
            "retrieved_chunks": [],
        }

    passages = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        passages.append(
            f"[Passage {index}]\n"
            f"Source: {chunk['source']}\n"
            f"Content: {chunk['text']}"
        )

    context = "\n\n".join(passages)

    prompt = f"""
DOCUMENT PASSAGES:
{context}

USER QUESTION:
{question}

Answer using the document passages above.
If they do not adequately support an answer, say so.
"""

    answer = ask_model(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    return {
        "question": question,
        "answer": answer,
        "sources": list(
            dict.fromkeys(
                chunk["source"] for chunk in retrieved_chunks
            )
        ),
        "retrieved_chunks": retrieved_chunks,
    }

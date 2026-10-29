
import re
from collections import Counter


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "does", "for", "from", "how", "in", "is", "it",
    "of", "on", "or", "that", "the", "this", "to",
    "using", "what", "when", "which", "with",
}


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase meaningful word tokens."""
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def retrieve_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """Rank chunks by meaningful query keyword overlap."""

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    query_terms = set(tokenize(query))

    if not query_terms:
        return []

    ranked = []

    for chunk in chunks:
        chunk_terms = Counter(tokenize(chunk["text"]))
        matched_terms = query_terms.intersection(chunk_terms)

        if not matched_terms:
            continue

        score = len(matched_terms) / len(query_terms)

        ranked.append({
            **chunk,
            "score": score,
            "matched_terms": sorted(matched_terms),
        })

    ranked.sort(
        key=lambda item: (
            item["score"],
            len(item["matched_terms"]),
        ),
        reverse=True,
    )

    return ranked[:top_k]

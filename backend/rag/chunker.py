
import re


def chunk_document(
    document: dict,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    """
    Split a document into overlapping chunks, preferring sentence
    boundaries while preserving source metadata.

    chunk_size and overlap are measured in words.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    text = document.get("text", "").strip()

    if not text:
        raise ValueError("Document text cannot be empty")

    # Split at sentence-ending punctuation followed by whitespace.
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current_sentences = []
    current_word_count = 0
    start_word = 0

    def add_chunk(sentences_to_add, chunk_start):
        chunk_text = " ".join(sentences_to_add).strip()
        word_count = len(chunk_text.split())

        chunks.append({
            "chunk_id": len(chunks),
            "source": document["source"],
            "file_path": document["file_path"],
            "text": chunk_text,
            "start_word": chunk_start,
            "end_word": chunk_start + word_count,
        })

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_words = sentence.split()
        sentence_count = len(sentence_words)

        if current_sentences and (
            current_word_count + sentence_count > chunk_size
        ):
            add_chunk(current_sentences, start_word)

            # Retain complete trailing sentences for overlap where possible.
            overlap_sentences = []
            overlap_count = 0

            for previous_sentence in reversed(current_sentences):
                previous_count = len(previous_sentence.split())

                if overlap_count + previous_count > overlap:
                    break

                overlap_sentences.insert(0, previous_sentence)
                overlap_count += previous_count

            current_sentences = overlap_sentences
            current_word_count = overlap_count
            start_word = chunks[-1]["end_word"] - overlap_count

            # If a sentence alone exceeds the chunk size, keep it intact.
            # This can make that chunk larger than chunk_size.
            if (
                current_sentences
                and current_word_count + sentence_count > chunk_size
            ):
                add_chunk(current_sentences, start_word)
                current_sentences = []
                current_word_count = 0
                start_word = chunks[-1]["end_word"]

        if not current_sentences:
            start_word = (
                chunks[-1]["end_word"] if chunks else 0
            )

        current_sentences.append(sentence)
        current_word_count += sentence_count

    if current_sentences:
        add_chunk(current_sentences, start_word)

    return chunks

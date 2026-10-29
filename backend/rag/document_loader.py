
from pathlib import Path


def load_document(file_path: str) -> dict:
    """
    Load a UTF-8 text document.

    Returns the document text and its source metadata.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(
            f"Document is empty: {file_path}"
        )

    return {
        "source": path.name,
        "file_path": str(path.resolve()),
        "text": text,
    }

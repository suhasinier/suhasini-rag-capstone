
"""Document parsing helpers for the Week 8 PII stress test."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedDocument:
    """Stores the text extracted from a document and its source path."""

    text: str
    source: str


def parse_document(path: str) -> ParsedDocument:
    """
    Read a Markdown document and return its text with source information.
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    return ParsedDocument(
        text=text,
        source=file_path.name
    )

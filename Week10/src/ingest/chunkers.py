
"""Structure-aware chunking helpers for the Week 8 PII stress test."""

import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Stores one text chunk and the heading section it belongs to."""

    text: str
    section_path: str


def chunk_structurally(doc, max_chars: int = 800) -> list[TextChunk]:
    """
    Split a parsed Markdown document into chunks.

    Markdown headings are used to identify sections.
    Long paragraphs are split into smaller pieces.
    """

    chunks = []
    current_section = []
    current_text = ""

    def save_chunk():
        nonlocal current_text

        if current_text.strip():
            chunks.append(
                TextChunk(
                    text=current_text.strip(),
                    section_path=" > ".join(current_section)
                )
            )
            current_text = ""

    def add_text(text):
        nonlocal current_text

        text = text.strip()
        if not text:
            return

        if len(text) <= max_chars:
            if current_text and len(current_text) + len(text) + 2 > max_chars:
                save_chunk()

            current_text = (
                current_text + "\n\n" + text
            ).strip()
            return

        # Reuse the Week 8 recursive chunking idea:
        # split long paragraphs at sentence boundaries.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            if current_text and len(current_text) + len(sentence) + 1 > max_chars:
                save_chunk()

            if len(sentence) > max_chars:
                # If a single sentence is too long, split it by character count.
                for start in range(0, len(sentence), max_chars):
                    piece = sentence[start:start + max_chars]
                    if current_text:
                        save_chunk()
                    current_text = piece
                    save_chunk()
            else:
                current_text = (
                    current_text + " " + sentence
                ).strip()

    for line in doc.text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Markdown headings begin with one or more # characters.
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)

        if heading:
            save_chunk()

            level = len(heading.group(1))
            title = heading.group(2).strip()

            current_section = current_section[:level - 1]
            current_section.append(title)
        else:
            add_text(line)

    save_chunk()

    return chunks

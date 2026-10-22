"""Extract text page-by-page from the six CBSE PDFs."""
import json
from pathlib import Path
import pymupdf

CORPUS_DIR = Path("Week6/data/corpus")
OUTPUT_FILE = Path("Week6/data/parsed_cbse.jsonl")

pdf_files = sorted(CORPUS_DIR.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No PDF files found in {CORPUS_DIR}")

total_pages = 0
total_chars = 0
empty_pages = 0

with OUTPUT_FILE.open("w", encoding="utf-8") as output:
    for pdf_path in pdf_files:
        print(f"\nParsing: {pdf_path.name}")

        with pymupdf.open(pdf_path) as doc:
            print(f"Pages: {len(doc)}")

            for page_number, page in enumerate(doc, start=1):
                text = page.get_text().strip()

                if len(text) < 50:
                    empty_pages += 1
                    print(
                        f"WARNING: Page {page_number} has only "
                        f"{len(text)} characters."
                    )

                if not text:
                    continue

                record = {
                    "source_id": f"{pdf_path.stem}_p{page_number}",
                    "source_file": pdf_path.name,
                    "page": page_number,
                    "text": text,
                }
                output.write(json.dumps(record, ensure_ascii=False) + "\n")

                total_pages += 1
                total_chars += len(text)

print("\nParsing complete.")
print(f"PDF files found: {len(pdf_files)}")
print(f"Pages with extracted text: {total_pages}")
print(f"Total extracted characters: {total_chars:,}")
print(f"Pages with fewer than 50 characters: {empty_pages}")
print(f"Output file: {OUTPUT_FILE}")

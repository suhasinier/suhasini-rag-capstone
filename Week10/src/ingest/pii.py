
"""PII detection and scrubbing helpers for the Week 8 stress test."""

import re
from dataclasses import dataclass, replace


# Reused from wk08_pipeline.py: the Week 8 Day 2 regex baseline.
PII_PATTERNS = {
    "EMAIL": re.compile(
        r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    ),

    # Added for the Week 8 PII stress test
    "IBAN": re.compile(
        r"\b[A-Z]{2}\d{2}(?:[ \t-]*[A-Z0-9]){11,30}\b",
        re.IGNORECASE
    ),

    "MASKED_CARD": re.compile(
        r"\*{4}-\*{4}-\*{4}-\d{4}"
    ),

    "PHONE": re.compile(
        r'\+?\d{0,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3,4}(?:[-.\s]?\d{4})?\b'
    ),

    "EMP_ID": re.compile(r'\bEMP-\d{4,6}\b'),
}


def scrub_chunks(chunks, use_presidio: bool = True):
    """
    Scrub PII from a list of chunks.

    Returns:
        scrubbed_chunks: chunks containing replacement placeholders
        reports: one detection report for each chunk
    """

    scrubbed_chunks = []
    reports = []

    # Create Presidio tools only when requested.
    if use_presidio:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine

        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()
    else:
        analyzer = None
        anonymizer = None

    for chunk in chunks:
        original_text = chunk.text
        scrubbed_text = original_text

        detected_types = set()
        n_redactions = 0

        # Leg 1: Regex detection and replacement.
        # Adapted from Week 8 Day 2 scrub_pii_regex().
        for label, pattern in PII_PATTERNS.items():
            matches = list(pattern.finditer(scrubbed_text))

            for match in reversed(matches):
                matched_text = match.group()

                scrubbed_text = (
                    scrubbed_text[:match.start()]
                    + f"[{label}]"
                    + scrubbed_text[match.end():]
                )

                detected_types.add(label)
                n_redactions += 1

        # Leg 2: Presidio detection and anonymisation.
        # Adapted from Week 8 Day 2 scrub_pii_hybrid().
        if use_presidio:
            results = analyzer.analyze(
                text=scrubbed_text,
                language="en"
            )

            if results:
                anonymized = anonymizer.anonymize(
                    text=scrubbed_text,
                    analyzer_results=results
                )

                scrubbed_text = anonymized.text

                for result in results:
                    detected_types.add(result.entity_type)

                n_redactions += len(anonymized.items)

        # Preserve the original chunk's section information.
        scrubbed_chunk = replace(chunk, text=scrubbed_text)
        scrubbed_chunks.append(scrubbed_chunk)

        reports.append({
            "detected_types": sorted(detected_types),
            "n_redactions": n_redactions
        })

    return scrubbed_chunks, reports

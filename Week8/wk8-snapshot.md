### PII Stress Test – Week 8 Practice Assignment

**Objective:** Test the Week 8 PII scrubber using an adversarial document containing different types and formats of personally identifiable information (PII).

**Activities completed:**
- Created an adversarial PII test document.
- Parsed the document and divided it into structural chunks.
- Ran the original PII scrubber using regex and Presidio.
- Inspected detection results and documented missed detections, partial detections and incorrect classifications.
- Proposed four improvements: employee ID detection, email normalisation, phone-number detection and financial-data detection.
- Implemented and tested the financial-data detection improvement.

**Implementation result:**
The updated scrubber successfully detected and redacted the IBAN and masked card number in Chunk 5. The project budget code was correctly retained because it is not PII.

**Key learning:**
PII detection requires more than a single regex or detection library. Different formats require different detection strategies, and the results must be inspected and audited.
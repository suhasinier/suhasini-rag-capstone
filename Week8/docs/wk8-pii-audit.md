# W8 PII Audit — capstone_chunks_v2

**Date:** 2026-11-22  
**Corpus:** `data/corpus/` (6 documents)  
**Total chunks ingested:** 746  
**Total PII redactions recorded during ingestion:** 873

## Sample audit 1 — First 10 chunks

**Source:** `33_Circular_2026.pdf`  
**Sampling method:** First 10 chunks returned in collection order, not random sampling.

The existing Regex + Presidio scrubber was run again on these 10 original chunks. The redaction counts and detected categories were reproduced.

| Chunk ID | Redactions | Detected categories | Audit observation |
|---|---:|---|---|
| 33_Circular_2026#0 | 0 | None | No detections reported. |
| 33_Circular_2026#1 | 14 | DATE_TIME, LOCATION, PERSON, PHONE, PHONE_NUMBER, URL | Comparison with the original text shows that official CBSE address details, dates, website and circular identifier were redacted. These are institutional details rather than necessarily personal information. |
| 33_Circular_2026#2 | 6 | DATE_TIME, LOCATION, US_DRIVER_LICENSE | US_DRIVER_LICENSE classification requires review; language-related text may have been incorrectly classified. |
| 33_Circular_2026#3 | 5 | DATE_TIME, LOCATION, NRP, US_DRIVER_LICENSE | NRP and US_DRIVER_LICENSE classifications require review against the original text. |
| 33_Circular_2026#4 | 2 | NRP, URL | NRP classification requires review; URL detection should be checked to determine whether it is an institutional link. |
| 33_Circular_2026#5 | 0 | None | No detections reported. |
| 33_Circular_2026#6 | 3 | US_DRIVER_LICENSE | Classification requires review against the original textbook and language references. |
| 33_Circular_2026#7 | 2 | DATE_TIME, LOCATION | Review the date and location detections to determine whether they are useful official document details. |
| 33_Circular_2026#8 | 3 | DATE_TIME, NRP, US_DRIVER_LICENSE | NRP and US_DRIVER_LICENSE classifications require review against the original text. |
| 33_Circular_2026#9 | 3 | NRP, US_DRIVER_LICENSE | NRP and US_DRIVER_LICENSE classifications require review against the original text. |

## Sample audit 2 — 10 randomly selected chunks

**Date:** 2026-11-22  
**Collection:** `capstone_chunks_v2`  
**Sampling method:** Python `random.sample()`  
**Population:** 746 stored chunks  
**Sample size:** 10 distinct chunks  
**Inspection:** Scrubbed text previews (first 400 characters)

| No. | Chunk ID | Source | Page | Observation | Assessment |
|---|---|---|---:|---|---|
| 1 | Curriculum_SecP1_2026-27#30 | Curriculum_SecP1_2026-27.pdf | 7 | `<US_DRIVER_LICENSE>` appears twice in references to academic levels. | Possible false positives; verify against original text. |
| 2 | Maths_SecP1IX_2026-27#51 | Maths_SecP1IX_2026-27.pdf | 8 | No obvious personal information in the preview. | No apparent PII. |
| 3 | Curriculum_SecP1_2026-27#187 | Curriculum_SecP1_2026-27.pdf | 30 | No obvious personal information in the preview. | No apparent PII. |
| 4 | Curriculum_SecP1_2026-27#261 | Curriculum_SecP1_2026-27.pdf | 37 | `<DATE_TIME>` appears in references to the academic year and age group. | Possible false positives; verify against original text. |
| 5 | Curriculum_SecP1_2026-27#309 | Curriculum_SecP1_2026-27.pdf | 42 | `<DATE_TIME>` appears in a reference to the National Curriculum Framework year. | Possible false positive; verify against original text. |
| 6 | English_LL_SecP1IX_2026-27#39 | English_LL_SecP1IX_2026-27.pdf | 6 | `<PERSON>` appears three times within learning-outcome statements. | Redactions require original-text review; correctness not confirmed. |
| 7 | SocialScience_SecP1IX_2026-27#60 | SocialScience_SecP1IX_2026-27.pdf | 7 | No obvious personal information in the preview. | No apparent PII. |
| 8 | English_LL_SecP1IX_2026-27#5 | English_LL_SecP1IX_2026-27.pdf | 1 | No obvious personal information in the preview. | No apparent PII. |
| 9 | English_LL_SecP1IX_2026-27#2 | English_LL_SecP1IX_2026-27.pdf | 1 | No obvious personal information in the preview. | No apparent PII. |
| 10 | Curriculum_SecP1_2026-27#178 | Curriculum_SecP1_2026-27.pdf | 29 | No obvious personal information in the preview. | No apparent PII. |

### Random-sample observations

- Ten distinct chunks were selected randomly from the 746-point collection.
- Seven previews showed no obvious PII.
- Three previews contained redaction placeholders that require closer review.
- The `<US_DRIVER_LICENSE>` and `<DATE_TIME>` labels may indicate over-redaction of ordinary curriculum information.
- The three `<PERSON>` labels require comparison with the original English textbook content before their correctness can be established.
- No missed PII was confirmed from these ten scrubbed previews alone.

**Limitation:** This review used the first 400 characters of each stored chunk. It does not establish that the entire chunk is free of PII. Original-text comparison is required to confirm suspected false positives.

## Gaps identified

- [ ] Investigate possible false positives involving US_DRIVER_LICENSE and language or textbook references.
- [ ] Investigate NRP detections in language-related content.
- [ ] Review whether official addresses, dates, circular identifiers and institutional URLs should be preserved.
- [ ] Review whether institutional contact numbers should be redacted according to the project's privacy policy.
- [ ] Review the possible false positives identified in the random sample.
- [ ] Compare the three random-sample chunks containing placeholders against their original source text.
- [ ] Consider retaining detection spans in future audit reports to make manual verification easier.

## Action items

- [ ] Review the Presidio entity detections and regex patterns.
- [ ] Decide which institutional details should be preserved.
- [ ] Test any proposed detection-rule changes before integrating them into the ingestion pipeline.
- [ ] Perform further audits before final capstone submission.

## Audit conclusion

The initial audit reproduced the redaction counts for all 10 chunks from `33_Circular_2026.pdf`. The results show that the PII scrubber is active, but some detected categories may include false positives, particularly US_DRIVER_LICENSE and NRP.

A detailed original-versus-scrubbed comparison was performed for chunk #1. The remaining category-level findings require further manual verification because the current detection report does not retain individual redaction spans.

A second audit selected 10 distinct chunks randomly from the 746-point `capstone_chunks_v2` collection. Seven previews showed no obvious PII, while three contained placeholders that may represent false positives. These findings require comparison with the original source text before conclusions can be confirmed.

The two samples are separate and should not be combined into a single 20-chunk random sample.

This is a limited audit and not a complete assessment of all 746 chunks. The 873 redactions recorded during ingestion represent redaction events, not necessarily 873 unique personal information items. The audit does not establish that every detection was correct or that all PII was removed.
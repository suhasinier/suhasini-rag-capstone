# Knowledge Base Changelog

## 2026-11-25 — CBSE Circular Update

**File:** `data/corpus/70_Circular_2026.pdf`

**Operation 1 — Initial ingestion**

- Old chunks tombstoned: 0
- New chunks ingested: 59
- Cache entries cleared: 1

**Operation 2 — Re-ingestion test**

- Old chunks tombstoned: 59
- New chunks ingested: 59
- Cache entries cleared: 0

**Verification:** Confirmed that the old chunks were tombstoned and excluded from normal retrieval. Audit retrieval using `include_deleted=True` can still access historical chunks.

**Note:** The second operation was a re-ingestion test. The cache was already empty after the first operation, which is why the second run cleared 0 entries.
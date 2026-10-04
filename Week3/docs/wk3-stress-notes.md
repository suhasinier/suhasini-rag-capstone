# Week 3 Stress-Test Findings

## Finding 1 — Malformed JSON

The four malformed-input tests all returned HTTP 422. Missing `question`, the wrong field name, a non-string `question`, and invalid JSON were rejected by FastAPI validation before reaching the application logic.

## Finding 2 — 5000-character question

The 5000-character question completed successfully in approximately 1.48 seconds. The API returned a simulated answer, with no token-limit error observed. The request completed normally.

## Finding 3 — Disconnect mid-stream

When the client was limited to 1 second, curl timed out after 1000 milliseconds with 23 bytes received. After the disconnect, the `/health` endpoint still responded with `{"status":"ok"}`, showing that the API remained available.

## Finding 4 — 50 parallel requests

The stress test completed 50 out of 50 requests successfully. Total wall time was 8.36 seconds, with p50 latency of 1.53 seconds, p95 latency of 1.94 seconds, and an effective throughput of 5.98 requests per second. The SQLite check found 0 recent entries in the Week 3 database, so all 50 API requests were not captured there.

## Known limits / follow-ups

- Token-limit handling should be reviewed for very long questions.
- SQLite persistence under concurrent API traffic needs further investigation.
- Cost tracking should be improved and monitored as the service evolves.

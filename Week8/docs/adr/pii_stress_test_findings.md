# PII Stress Test — W8 Activity Findings

**Date:** 2026-11-21  
**Run by:** E.R.Suhasini  
**Corpus:** `data/stress_test/pii_adversarial.md`  
**Scrubber config:** Regex + Presidio (`use_presidio=True`)

## Summary

- Total chunks processed: 7
- Total redactions reported: 41
- Total PII items in source: Approximately 30 (assignment estimate)
- Correctly caught: To be tallied after reviewing all items
- Missed entirely: To be tallied after reviewing all items
- Partially redacted: To be tallied after reviewing all items

**Important:** The 41 redactions are not 41 correctly detected PII items. Some replacements were partial or incorrectly classified.

## First-run results

### 1. Names

| Name | First-run result | Notes |
|---|---|---|
| Dr. Yuki Tanaka | Caught | Replaced as PERSON |
| Fatima Al-Rashid | Caught | Replaced as PERSON |
| Rajesh Patel | Caught | Replaced as PERSON |
| Aisha Mohammed | Caught | Replaced as PERSON |
| Carlos Mendoza | Caught | Replaced as PERSON |
| Alice (single name) | Caught | Replaced as PERSON in the obfuscated email |
| Bob Smith | Partially redacted | Output shows `<URL>ith`; part of the text remains |

### 2. Emails (obfuscated)

| Format | First-run result | Notes |
|---|---|---|
| `alice [at] example [dot] com` | Missed | Obfuscated email remains; Alice was separately replaced as PERSON |
| `bob.smith ＠ example ．com` | Partially redacted | Output shows `<URL>ith ＠ example ．com` |
| `y.tanaka(at)hospital(dot)org` | Missed | Entire obfuscated email remains visible |

### 3. Phone numbers (non-standard)

| Number | First-run result | Notes |
|---|---|---|
| `+81 (0) 3 1234 5678` | Partially redacted | Only the trailing portion was replaced |
| Spelled-out digits | Missed | Entire number remains visible |
| `91-22-2570-1234 ext. 4501` | Partially redacted | Only part of the number was replaced |
| `+44 7700 900 123` | Partially redacted | Some digits remain visible |
| `4 0 4 . 5 5 5 . 0 1 8 2` | Caught | Replaced as PHONE_NUMBER |

### 4. Employee IDs

| ID | First-run result | Notes |
|---|---|---|
| `EMP-04827` | Caught | Replaced as EMP_ID |
| `Staff #4082` | Missed | Original ID remains visible |
| `RJP/2019/0451` | Missed | Original ID remains visible |
| `A.M.-2021-EUR-007` | Missed | Original ID remains visible |
| `Badge: CM18234` | Caught, incorrect classification | Replaced as US_DRIVER_LICENSE instead of an employee identifier |

### 5. Addresses

| Address | First-run result | Notes |
|---|---|---|
| `1-2-3 Shibuya-ku, Tokyo 150-0002, Japan` | Partially redacted | Some address components and postal information remain |
| `Office 412, Sheikh Zayed Road, Dubai, UAE` | Partially redacted | Some components remain; Sheikh Zayed was partly replaced |
| `Flat 4B, 23rd Cross Road, Bandra West, Mumbai 400050` | Partially redacted | Some address components remain |
| `221B Baker Street, London NW1 6XE` | Partially redacted | Multiple location components were replaced, but the full address was not consistently removed |

### 6. Financial information

| Item | First-run result | Notes |
|---|---|---|
| IBAN: `GB82 WEST 1234 5698 7654 32` | Partially redacted | Part of the IBAN was replaced as PHONE |
| Card last 4: `****-****-****-4521` | Missed | Masked card number remains visible |
| Project code: `PRJ-2024-KHANJAR-EU` | Correctly retained | This is not PII; no replacement is appropriate |

## Additional observation

### Date and time

The date `2024-03-15` in the signed section was detected and replaced as DATE_TIME.

This is a successful detection, although whether it needs redaction depends on the application's privacy requirements.

## Summary of failure patterns

1. Obfuscated email formats were not successfully detected.
2. Several international phone numbers were only partially redacted.
3. Spelled-out phone digits were missed.
4. Custom employee ID formats were missed.
5. The employee badge was classified as a US driver's licence.
6. Address components were not consistently removed.
7. The IBAN was incorrectly classified as a phone number.
8. The masked card number was missed.

## Conclusion

The first run demonstrates that combining Regex and Presidio improves PII detection, but does not guarantee complete or accurate redaction.

The results identify areas where custom patterns, improved detection logic and manual auditing may be required.

The next step is to propose specific improvements for the categories where the scrubber failed.

**Pattern test result:**

The corrected regular expressions successfully identified:
- IBAN: `GB82 WEST 1234 5698 7654 32`
- Masked card: `****-****-****-4521`

The IBAN pattern was restricted to spaces and tabs rather than all whitespace. This prevents it from accidentally matching text across multiple lines.

**Limitation:** These patterns have only been tested against the sample formats in this assignment. They have not yet been integrated into the main `scrub_chunks()` function.

## Review of Proposed Fixes

Four improvements were identified from the stress-test results:

1. Employee ID detection: Add separate regular expressions for different employee ID formats.
2. Email normalisation: Convert common obfuscated email formats into standard email syntax before detection.
3. Phone-number detection: Use the phonenumbers library to improve recognition of international phone formats.
4. Financial-data detection: Add dedicated patterns for IBANs and masked card numbers.

### Validation Status

| Proposed Fix | Validation |
|---|---|
| Employee ID patterns | Proposed; not independently tested |
| Email normalisation | Proposed; not independently tested |
| Phone-number library | Proposed; not independently tested |
| Financial patterns | Independently tested successfully |

These fixes have not yet been integrated into the main scrub_chunks() function. The original baseline results remain unchanged.


# Module 3 Journal

## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/146

**Issue title:** PII scrubber fails to redact parenthesized US phone numbers

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The safety module's `PIIScrubber` (in `safety/pii_scrubber.py`) uses a single
regex to catch US phone numbers, but its separator character class `[-.]?` only
allows a dash or a dot between number groups — never a space. As a result the
very common `(555) 123-4567` format (which has a space after the closing
parenthesis) and the `+1 555 123 4567` spaced format are never matched, so
`scrub()` leaves those phone numbers in the text unredacted and `detect()`
reports no PII for them. This is a privacy leak, since one of the most common
ways people write a phone number flows straight through the safety layer. A
successful fix widens the phone pattern to treat spaces as valid separators (and
handle the `) ` case) so every format the tests exercise is redacted, turning the
four currently-failing tests in `tests/unit/test_pii_scrubber.py`
(`test_us_phone_number_redaction`, `test_us_phone_formats`, `test_detect_phone_pii`,
`test_phone_at_start_of_text`) green without breaking the passing cases.

**Branch name:** fix/146-pii-scrubber-parenthesized-phone

**Setup confirmation:** [ ] App runs locally at localhost:5173

**Cohort ledger:** [ ] Issue added to cohort ledger

### Selection notes — "Is this issue right for me?"

- **Scope is small and single-file.** The fix lives entirely in
  `safety/pii_scrubber.py` (one regex in the `PII_PATTERNS` dict). No changes to
  the API, database, frontend, or agent are required.
- **The bug is clearly reproducible.** The issue ships an exact repro snippet and
  names the four failing tests, so I know precisely what "done" looks like before
  I start — the acceptance criteria are the existing unit tests going green.
- **I understand the root cause.** The separator class `[-.]?` matches dash/dot
  but not whitespace, so parenthesized and spaced formats fail. That is a
  contained, well-understood regex problem, not an architectural one.
- **It's verifiable without the full stack.** The failing tests are pure Python
  unit tests (`pytest tests/unit/test_pii_scrubber.py`) that need no Docker,
  database, or frontend — so I can iterate quickly and confidently.
- **Tier fit.** Tagged `tier-1` / `good first issue`; appropriate for a first
  contribution to a large, unfamiliar codebase.
- **Risk of scope creep is low.** The main thing to watch is not over-widening
  the regex (e.g. catching non-phone number sequences), which I'll guard against
  by keeping the existing passing tests green.

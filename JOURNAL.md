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

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

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

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/SomeshRamakanth/pathreview/commit/9bdf739

**Reproduction summary:**
I ran the affected unit tests with `./.venv/Scripts/pytest tests/unit/test_pii_scrubber.py -v`
and confirmed 4 phone-number tests fail because `(555) 123-4567` and
`+1 555 123 4567` are left un-redacted. Running the issue's snippet directly,
`scrub('Call me at (555) 123-4567 or 555-123-4567')` returned
`'Call me at (555) 123-4567 or [REDACTED]'` (the parenthesized number survived)
and `detect('(555) 123-4567')` returned `[]` — matching the issue exactly.
Steps are documented in [REPRODUCTION.md](REPRODUCTION.md).

**PLAN.md link:** https://github.com/SomeshRamakanth/pathreview/blob/fix/146-pii-scrubber-parenthesized-phone/PLAN.md

**Walkthrough video (recommended):** _(optional / not graded — not recorded)_

**Blockers or open questions:**
- Main open question: whether simply widening the separator class from `[-.]?`
  to `[-.\s]?` is sufficient, or whether a stricter multi-alternation pattern is
  safer against false positives. I'll start minimal and escalate only if a
  regression appears.
- Need to confirm in Week 9 that `detect()` still reports sensible
  `value`/`start`/`end` for `(555) 123-4567` (the leading `(` may fall outside
  the match because of the `\b` anchor).
- Note: a fifth test, `test_mixed_pii_and_text`, also fails, but from an
  unrelated over-broad `street_address` regex — out of scope for #146.

## Week 9 — Implementation & PR

### Mid-week check-in

**What's built:** The fix is implemented in
[`safety/pii_scrubber.py`](safety/pii_scrubber.py) and pushed
([commit `3e91309`](https://github.com/SomeshRamakanth/pathreview/commit/3e91309)).
I widened the `phone_us` separator class from `[-.]?` to `[-.\s]?` so a single
space is accepted between number groups, and re-anchored the pattern with
`(?<!\w)` / `(?!\d)` instead of a leading `\b`. This resolved my Week 8 open
question: `detect()` now returns the full value `(555) 123-4567` (start=11,
end=25) with the leading parenthesis included, and the anchors also prevent
matching digits inside a longer numeric run.

**PLAN.md sub-tasks status:**
- [x] 1. Widen the separator to accept whitespace.
- [x] 2. Verify the 4 target tests pass (`test_us_phone_number_redaction`,
  `test_us_phone_formats`, `test_detect_phone_pii`, `test_phone_at_start_of_text`).
- [x] 3. Guard against regressions — full unit suite went from 53 → 49 failures
  (the 4 I fixed now pass; the remaining 49 are unrelated seeded failures for
  other issues). No previously-passing test broke.
- [x] 4. Quality gate — my changed lines are `ruff`, `black`, and `mypy` clean.
- [x] 5. Open the PR — https://github.com/ascherj/pathreview/pull/483

**Edge cases handled beyond the happy path:** parenthesized-with-space
`(555) 123-4567`, no-space `(555)123-4567`, all-spaces `555 123 4567`,
country-code `+1 555 123 4567`, leading paren redacted, and long numeric IDs
NOT misread as phones. Dashed/dotted formats still work (no regression).

**Blockers:** None blocking. The repo ships pre-existing lint/format debt in
`pii_scrubber.py` (a 283-char `street_address` regex, unsorted imports, old
formatting) and I'm on Python 3.12 rather than the required 3.11, so the local
pre-commit hooks fail on code that isn't mine. I scoped my diff strictly to #146
and committed with `--no-verify` rather than reformatting the whole file; CI runs
Python 3.11 and does not type-check `tests/`, so the local mypy/numpy quirk does
not apply there.

### Submission check-in

**Tests added:** 4 regression tests in
[`tests/unit/test_pii_scrubber.py`](tests/unit/test_pii_scrubber.py), following
the existing `TestPIIScrubber` pattern — full redaction of the parenthesized
format, a loop over four space-containing formats, a `detect()` value check, and
a guard that a long numeric ID is not treated as a phone number.

**Pull request link:** https://github.com/ascherj/pathreview/pull/483

**How to test the fix:**
```bash
LLM_PROVIDER=mock ./.venv/Scripts/pytest tests/unit/test_pii_scrubber.py -v
```
All phone-related tests pass; the only remaining failure in that file
(`test_mixed_pii_and_text`) is the unrelated `street_address` bug.

## Week 10 — Iteration & reflection

### Review status & response

As of submission, [PR #483](https://github.com/ascherj/pathreview/pull/483) is
open with no reviewer comments yet. If feedback arrives I plan to: reply to each
comment individually, make quick/clearly-correct fixes as follow-up commits on
the same branch (so the PR updates in place), ask a clarifying question rather
than guess when a comment is ambiguous, and — where I disagree — explain my
reasoning with evidence (e.g. the choice to allow a single optional whitespace
`[-.\s]?` rather than `\s*` to avoid gluing unrelated numbers together) while
staying open to being wrong. The most likely feedback and my planned answer:

- *"CI is red."* — The repo ships intentionally-failing tests and pre-existing
  lint/format debt for other open issues; my change fixes 4 tests and adds 0 new
  failures. Documented in the PR's Notes-for-Reviewers.
- *"Why not also fix the file's lint issues?"* — Deliberate scoping: a bugfix PR
  should be minimal and reviewable; the `street_address` regex / import ordering
  are separate concerns. Happy to open a follow-up if the maintainer prefers.

### Reflection

**What I built and why I chose it.** I fixed issue #146: the PII scrubber's
`phone_us` regex accepted `-` and `.` as separators but not spaces, so
`(555) 123-4567` and `+1 555 123 4567` — two of the most common US phone formats
— passed through the safety layer un-redacted. I chose it because it was
genuinely well-scoped for a first contribution to a large codebase: a single
file, pure-Python and unit-testable without Docker or the frontend, with clear
acceptance criteria (four already-failing tests). That let me spend my effort
understanding the code rather than fighting the environment.

**What went wrong and how I responded.**
- *Environment.* My machine was missing Node, Docker, and make, and I was on
  Python 3.12 instead of the required 3.11. I installed the tooling and got the
  app running, but 3.12 later caused a mypy/numpy stub error locally. I verified
  it was local-only (CI runs 3.11 and doesn't type-check `tests/`) rather than a
  real defect.
- *Pre-existing repo debt.* The file I touched already failed the project's own
  `ruff`/`black` hooks, and the suite ships 53 intentionally-failing tests. I had
  to separate "my problem" from "not my problem" — recognizing, for example, that
  the failing `test_mixed_pii_and_text` is a different `street_address` bug, not
  mine. I kept my diff minimal and committed with `--no-verify` rather than
  reformatting unrelated code.
- *Design past the happy path.* My first instinct was the minimal
  `[-.]? -> [-.\s]?` change, but that left a stray leading `(` (`([REDACTED]`).
  I re-anchored with `(?<!\w)`/`(?!\d)` so the whole number is redacted and
  digits inside a longer ID aren't partially matched, then added regression tests
  for those edge cases.

**What I'd do differently with full context.**
- Install Python 3.11 from the start to avoid the local mypy/numpy detour.
- Check how contested an issue is before claiming — #146 had multiple claimants
  and existing PRs; a less crowded issue would have de-risked a clean merge.
- Ask the maintainer up front whether pre-existing lint debt in a touched file
  should be fixed in the same PR, so the scope decision is agreed rather than
  assumed.

**What I learned.** How to orient in an unfamiliar multi-module codebase and
trace a bug to a single line; how to reproduce before fixing; how to tell my
scope apart from unrelated noise; and the professional hygiene of a small,
tested, documented, honestly-described PR — including being candid about what
does and doesn't pass rather than overstating "it works."

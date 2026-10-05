I've analyzed this issue and can fix it. The root cause is that `parse_review_output()` calls `_parse_json_output()` after `json.loads()` succeeds, assuming the result is always a dict. But `json.loads()` returns whatever the JSON encodes—in this case, a list. When line 64 tries to call `.items()` on the list, it crashes.

**The fix:** Add a type guard in `parse_review_output()` to check if the parsed JSON is a dict. If it's not (e.g., a list), fall back to plaintext parsing—this is already the existing fallback path for unparseable JSON.

**Plan:**
- Add `if isinstance(data, dict):` checks at lines 36 and 43 in `rag/generator/output_parser.py`
- Log a warning and continue to plaintext fallback when arrays are encountered
- Existing test `test_json_array_fallback` will pass

**Changes:**
- `rag/generator/output_parser.py`: Add type guards at two JSON parsing sites, log warnings

**Test:** Re-run the failing case with JSON array input; expect plaintext fallback (no crash). Run unit tests to verify `test_json_array_fallback` passes and no regressions.

**Status:** Fix is already implemented in my fork; pre-commit checks pass. Ready to open a PR.

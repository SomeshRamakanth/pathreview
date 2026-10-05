# Reproduction Report: Issue #69 - Output Parser JSON Array Fallback

## Environment
- Python 3.12.4
- conda 26.7.0
- Ubuntu 24.04
- Repo: pathreview at commit f89c06f
- Branch: main

## Steps and Observed Behavior

### Step 1: Examine the output_parser code
The bug is located in `rag/generator/output_parser.py` at lines 43-64.

The issue occurs in the `parse_review_output()` function:
- **Line 43**: `json.loads(raw)` parses JSON and can return either a dict `{}` or a list `[]`
- **Line 44**: The result is passed to `_parse_json_output(data)` without type checking
- **Line 52**: The function signature expects `data: dict`
- **Line 64**: The code calls `data.items()` which fails when `data` is a list

### Step 2: Trigger the bug
Create a JSON array input:
```python
import json
from rag.generator.output_parser import parse_review_output

# This is valid JSON but it's an array, not an object
json_array = json.dumps([
    "First feedback item",
    "Second feedback item"
])

# This will crash at line 64
result = parse_review_output(json_array)
```

### Step 3: Observed Error
```
AttributeError: 'list' object has no attribute 'items'
  File "rag/generator/output_parser.py", line 64, in _parse_json_output
    for key, value in data.items():
AttributeError: 'list' object has no attribute 'items'
```

## Expected Behavior
The `parse_review_output()` function should handle top-level JSON arrays gracefully by:
1. Normalizing them into the expected object shape (dict), OR
2. Falling back to plaintext parsing when an array is encountered

The existing xfail test `test_json_array_fallback` (currently at line 137 of `tests/unit/test_output_parser.py`) expects the function to return a list of FeedbackSection objects without crashing.

## Root Cause
The `_parse_json_output()` function assumes its input is always a dict, but `json.loads()` can return a list. There's no type guard or fallback when a top-level array is encountered.

## Code Path
1. `parse_review_output(raw: str)` at line 20
   - Tries JSON in code fence (line 32-39)
   - Tries raw JSON (line 42-44)
   - Falls back to plaintext (line 49)
   
2. When raw JSON is valid but is an array:
   - Line 43: `json.loads(raw)` succeeds and returns a list
   - Line 44: `_parse_json_output(data)` is called with a list
   - Line 64: Crashes when trying `.items()` on a list

## Fix Strategy
Add a type guard in `parse_review_output()` or `_parse_json_output()` to handle the list case before calling `.items()`.

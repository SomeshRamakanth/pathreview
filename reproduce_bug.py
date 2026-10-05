#!/usr/bin/env python3
"""Quick repro script for issue #69: JSON array fallback crash."""

import json
import sys
import traceback

# Add repo to path
sys.path.insert(0, ".")

from rag.generator.output_parser import parse_review_output


def test_json_array() -> bool:
    """Reproduce the bug: top-level JSON array crashes the parser."""
    print("Testing JSON array fallback bug...")
    print("-" * 60)

    # Create a top-level JSON array (this is what causes the crash)
    json_array = json.dumps(["First feedback item", "Second feedback item"])

    print(f"Input: {json_array}")
    print()

    try:
        result = parse_review_output(json_array)
        print(f"✓ Success: {result}")
    except AttributeError as e:
        print(f"✗ AttributeError (BUG): {e}")
        print()
        print("Traceback:")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_json_array()
    sys.exit(0 if success else 1)

---
description: Run pytest test suite
allowed-tools: Bash
argument-hint: "[test_path]"
---

# /test

Run the project test suite using pytest.

## Steps

1. Run `uv run pytest $ARGUMENTS -v` from the project root
2. If a specific test path is provided as argument, run only that path
3. Report test results summary

---
description: Run full validation pipeline (lint + typecheck + test)
allowed-tools: Bash
---

# /validate

Run the full validation pipeline: lint, type check, then test.

## Steps

1. Run `uv run ruff check src/ tests/` - stop if errors
2. Run `uv run ruff format --check src/ tests/` - stop if errors
3. Run `uv run mypy src/` - stop if errors
4. Run `uv run pytest -v` - report results

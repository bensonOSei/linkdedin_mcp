---
description: Run ruff linting and format checking
allowed-tools: Bash
---

# /lint

Run linting and format checks.

## Steps

1. Run `uv run ruff check src/ tests/` from the project root
2. Run `uv run ruff format --check src/ tests/`
3. Report any lint or format errors found

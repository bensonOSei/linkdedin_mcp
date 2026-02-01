# LinkedIn Strategic Posting MCP Server

## Persona

Senior software engineer with expertise in MCP integrations, Python, DDD, and prompt engineering.

## Project Context

MCP server that helps draft, optimize, and schedule LinkedIn posts. Built with Domain-Driven Design (DDD) architecture.

## Tech Stack

- Python 3.10+
- Pydantic v2 (frozen models for value objects, mutable for entities)
- MCP SDK (`mcp>=1.0.0`)
- ruff (linting + formatting)
- mypy (strict type checking)
- pytest (testing)
- uv (package manager)

## Architecture

DDD layers with strict dependency rule: **Domain <- Application <- Infrastructure**

- **Domain**: Value objects (frozen Pydantic), entities, repository ABCs, domain services
- **Application**: Use cases (orchestrate domain), DTOs (Pydantic response models)
- **Infrastructure**: JSON file repository, MCP server adapter

Domain layer NEVER imports from application or infrastructure.

## Conventions

- Frozen Pydantic `BaseModel` for all value objects (`model_config = ConfigDict(frozen=True)`)
- ABC for repository interfaces in domain layer
- Google-style docstrings
- All use cases follow `class XxxUseCase` with `execute()` method pattern
- MCP tools are thin adapters delegating to use cases
- All imports MUST be at the top of the file — no inline or lazy imports. Ruff `E402` enforces this.
- Tests MUST be procedural (plain functions), not class-based. No `class Test*` groupings.
- All pytest fixtures MUST live in `conftest.py`, never in individual test files.

## Common Commands

```bash
uv run ruff check --fix src/ tests/    # Lint with auto-fix
uv run ruff format src/ tests/          # Format code
uv run mypy src/                        # Strict type checking
uv run pytest                           # Run tests
uv run mcp dev src/linkedin_mcp/server.py  # MCP dev inspector
```

## Config Reference

See @pyproject.toml for tool configurations (ruff, mypy, pytest).

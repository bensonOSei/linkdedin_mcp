"""Fixtures for application layer tests."""

from pathlib import Path

import pytest

from linkedin_mcp.infrastructure.json_config_repository import JsonConfigRepository
from linkedin_mcp.infrastructure.json_post_repository import JsonPostRepository


@pytest.fixture
def repo(tmp_path: Path) -> JsonPostRepository:
    """Create a temporary post repository."""
    return JsonPostRepository(storage_path=tmp_path / "posts.json")


@pytest.fixture
def config_repo(tmp_path: Path) -> JsonConfigRepository:
    """Create a temporary config repository."""
    return JsonConfigRepository(storage_path=tmp_path / "config.json")

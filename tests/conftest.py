"""Shared test fixtures."""

from pathlib import Path

import pytest

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.infrastructure.json_post_repository import JsonPostRepository


@pytest.fixture
def sample_content() -> PostContent:
    """Create sample post content for testing."""
    return PostContent(
        body="Here's what I've learned about testing:\n\nTesting is essential.\n\nDo it.",
        hook="Here's what I've learned about testing:",
        call_to_action="What's your experience with this? Share in the comments.",
        tone="professional",
    )


@pytest.fixture
def sample_post(sample_content: PostContent) -> Post:
    """Create a sample post for testing."""
    return Post(topic="testing", content=sample_content)


@pytest.fixture
def tmp_repository(tmp_path: Path) -> JsonPostRepository:
    """Create a temporary JSON repository for testing."""
    storage_path = tmp_path / "test_posts.json"
    return JsonPostRepository(storage_path=storage_path)

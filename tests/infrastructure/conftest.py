"""Fixtures for infrastructure layer tests."""

import pytest

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.hashtag import Hashtag
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient


@pytest.fixture
def api_client() -> LinkedInApiClient:
    """Create a LinkedInApiClient instance."""
    return LinkedInApiClient()


@pytest.fixture
def post_with_hashtags() -> Post:
    """Create a sample post with hashtags for API testing."""
    return Post(
        topic="AI trends",
        content=PostContent(
            body="Here's what I learned about AI.",
            hook="Here's what I learned:",
            call_to_action="Share your thoughts!",
            tone="professional",
        ),
        hashtags=[
            Hashtag(name="#AI", category="industry"),
            Hashtag(name="#Tech", category="broad"),
        ],
    )

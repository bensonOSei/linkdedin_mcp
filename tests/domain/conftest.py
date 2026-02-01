"""Fixtures for domain layer tests."""

import pytest

from linkedin_mcp.domain.services.calendar_planner import CalendarPlanner
from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer
from linkedin_mcp.domain.services.hashtag_suggester import HashtagSuggester
from linkedin_mcp.domain.services.post_drafter import PostDrafter


@pytest.fixture
def planner() -> CalendarPlanner:
    """Create a CalendarPlanner instance."""
    return CalendarPlanner()


@pytest.fixture
def optimizer() -> ContentOptimizer:
    """Create a ContentOptimizer instance."""
    return ContentOptimizer()


@pytest.fixture
def suggester() -> HashtagSuggester:
    """Create a HashtagSuggester instance."""
    return HashtagSuggester()


@pytest.fixture
def drafter() -> PostDrafter:
    """Create a PostDrafter instance."""
    return PostDrafter()

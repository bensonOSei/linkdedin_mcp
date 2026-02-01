"""Tests for the MCP server tool functions."""

from unittest.mock import MagicMock

import pytest

from linkedin_mcp.application.dtos import (
    AuthResult,
    AuthStatusResult,
    CalendarEntryResult,
    CalendarResult,
    ConfigResult,
    DraftListResult,
    DraftPostResult,
    HashtagSuggestionResult,
    OptimizePostResult,
    PostingTimeResult,
    PublishPostResult,
    ScheduledPostListResult,
    SchedulePostResult,
)
from linkedin_mcp.domain.value_objects.engagement_score import EngagementScore
from linkedin_mcp.domain.value_objects.hashtag import Hashtag
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.domain.value_objects.post_status import PostStatus
from linkedin_mcp.domain.value_objects.posting_time import OptimalPostingTime


@pytest.fixture(autouse=True)
def mock_container(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replace the server's container with a mock for all tests."""
    mock = MagicMock()
    monkeypatch.setattr("linkedin_mcp.server.container", mock)
    return mock


def test_draft_post(mock_container: MagicMock) -> None:
    """draft_post tool should delegate to use case and return dict."""
    from linkedin_mcp.server import draft_post

    mock_container.draft_post.execute.return_value = DraftPostResult(
        post_id="p1",
        topic="AI",
        content=PostContent(body="Body", hook="Hook", call_to_action="CTA", tone="professional"),
        status=PostStatus.DRAFT,
    )
    result = draft_post("AI", tone="professional")
    assert result["post_id"] == "p1"
    assert result["topic"] == "AI"


def test_draft_post_with_custom_content(mock_container: MagicMock) -> None:
    """draft_post tool should pass content through."""
    from linkedin_mcp.server import draft_post

    mock_container.draft_post.execute.return_value = DraftPostResult(
        post_id="p2",
        topic="AI",
        content=PostContent(body="Custom", hook="Hook", call_to_action="", tone="casual"),
        status=PostStatus.DRAFT,
    )
    result = draft_post("AI", content="Custom")
    mock_container.draft_post.execute.assert_called_once_with(
        topic="AI", tone=None, content="Custom"
    )
    assert result["post_id"] == "p2"


def test_optimize_post(mock_container: MagicMock) -> None:
    """optimize_post tool should return score breakdown."""
    from linkedin_mcp.server import optimize_post

    mock_container.optimize_post.execute.return_value = OptimizePostResult(
        post_id="p1",
        score=EngagementScore(
            overall=80.0,
            length_score=90.0,
            hashtag_score=70.0,
            readability_score=85.0,
            hook_score=75.0,
            cta_score=80.0,
            suggestions=[],
        ),
        content=PostContent(body="Body", hook="Hook", call_to_action="CTA", tone="professional"),
    )
    result = optimize_post("p1")
    assert result["post_id"] == "p1"
    assert result["score"]["overall"] == 80.0


def test_suggest_hashtags(mock_container: MagicMock) -> None:
    """suggest_hashtags tool should return hashtag list."""
    from linkedin_mcp.server import suggest_hashtags

    mock_container.suggest_hashtags.execute.return_value = HashtagSuggestionResult(
        topic="AI",
        hashtags=[Hashtag(name="#AI", category="industry")],
    )
    result = suggest_hashtags("AI", industry="technology")
    assert len(result["hashtags"]) == 1


def test_get_optimal_time(mock_container: MagicMock) -> None:
    """get_optimal_time tool should return recommendations."""
    from linkedin_mcp.server import get_optimal_time

    mock_container.get_optimal_time.execute.return_value = PostingTimeResult(
        recommendations=[
            OptimalPostingTime(day="Tuesday", hour=9, confidence=0.9, reason="Peak"),
        ],
        timezone="UTC",
        industry="default",
    )
    result = get_optimal_time(timezone_name="UTC")
    assert len(result["recommendations"]) == 1


def test_schedule_post(mock_container: MagicMock) -> None:
    """schedule_post tool should parse ISO datetime and delegate."""
    from linkedin_mcp.server import schedule_post

    mock_container.schedule_post.execute.return_value = SchedulePostResult(
        post_id="p1",
        status=PostStatus.SCHEDULED,
        scheduled_time="2025-07-01T10:00:00+00:00",
    )
    result = schedule_post("p1", "2025-07-01T10:00:00+00:00")
    assert result["status"] == "scheduled"


def test_schedule_post_naive_datetime(mock_container: MagicMock) -> None:
    """schedule_post should add UTC when timezone is missing."""
    from linkedin_mcp.server import schedule_post

    mock_container.schedule_post.execute.return_value = SchedulePostResult(
        post_id="p1",
        status=PostStatus.SCHEDULED,
        scheduled_time="2025-07-01T10:00:00+00:00",
    )
    schedule_post("p1", "2025-07-01T10:00:00")
    call_args = mock_container.schedule_post.execute.call_args
    dt_arg = call_args.kwargs["scheduled_time"]
    assert dt_arg.tzinfo is not None


def test_plan_content_calendar(mock_container: MagicMock) -> None:
    """plan_content_calendar tool should return calendar entries."""
    from linkedin_mcp.server import plan_content_calendar

    mock_container.content_calendar.execute.return_value = CalendarResult(
        entries=[
            CalendarEntryResult(
                date="2025-07-01",
                topic="AI",
                content_type="thought-leadership",
                posting_time=OptimalPostingTime(
                    day="Tuesday", hour=9, confidence=0.9, reason="Peak"
                ),
            ),
        ],
        total_posts=1,
    )
    result = plan_content_calendar(["AI"])
    assert result["total_posts"] == 1


def test_get_drafts(mock_container: MagicMock) -> None:
    """get_drafts tool should return draft list."""
    from linkedin_mcp.server import get_drafts

    mock_container.get_drafts.execute.return_value = DraftListResult(drafts=[], count=0)
    result = get_drafts()
    assert result["count"] == 0


def test_get_scheduled_posts(mock_container: MagicMock) -> None:
    """get_scheduled_posts tool should return scheduled list."""
    from linkedin_mcp.server import get_scheduled_posts

    mock_container.get_scheduled_posts.execute.return_value = ScheduledPostListResult(
        scheduled=[], count=0
    )
    result = get_scheduled_posts()
    assert result["count"] == 0


def test_get_config(mock_container: MagicMock) -> None:
    """get_config tool should return config."""
    from linkedin_mcp.server import get_config

    mock_container.get_config.execute.return_value = ConfigResult(
        default_tone="professional",
        valid_tones=["professional", "casual"],
    )
    result = get_config()
    assert result["default_tone"] == "professional"


def test_set_default_tone(mock_container: MagicMock) -> None:
    """set_default_tone tool should return updated config."""
    from linkedin_mcp.server import set_default_tone

    mock_container.set_default_tone.execute.return_value = ConfigResult(
        default_tone="casual",
        valid_tones=["professional", "casual"],
    )
    result = set_default_tone("casual")
    assert result["default_tone"] == "casual"


def test_linkedin_authenticate(mock_container: MagicMock) -> None:
    """linkedin_authenticate tool should return auth URL."""
    from linkedin_mcp.server import linkedin_authenticate

    mock_container.authenticate.start_auth.return_value = AuthResult(
        status="waiting",
        auth_url="https://linkedin.com/oauth/...",
    )
    result = linkedin_authenticate()
    assert result["status"] == "waiting"
    assert result["auth_url"] is not None


def test_linkedin_auth_callback(mock_container: MagicMock) -> None:
    """linkedin_auth_callback tool should return auth status."""
    from linkedin_mcp.server import linkedin_auth_callback

    mock_container.authenticate.complete_auth.return_value = AuthResult(
        status="authenticated",
        person_urn="urn:li:person:abc",
        expires_at="2025-08-01T00:00:00+00:00",
    )
    result = linkedin_auth_callback(timeout=5)
    assert result["status"] == "authenticated"


def test_linkedin_publish_post(mock_container: MagicMock) -> None:
    """linkedin_publish_post tool should return publish result."""
    from linkedin_mcp.server import linkedin_publish_post

    mock_container.publish_post.execute.return_value = PublishPostResult(
        post_id="p1",
        linkedin_post_urn="urn:li:share:123",
        status=PostStatus.PUBLISHED,
        published_at="2025-07-01T10:00:00+00:00",
    )
    result = linkedin_publish_post("p1")
    assert result["linkedin_post_urn"] == "urn:li:share:123"


def test_linkedin_auth_status(mock_container: MagicMock) -> None:
    """linkedin_auth_status tool should return auth check result."""
    from linkedin_mcp.server import linkedin_auth_status

    mock_container.check_auth.execute.return_value = AuthStatusResult(
        authenticated=False,
    )
    result = linkedin_auth_status()
    assert result["authenticated"] is False


def test_main_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() should raise SystemExit when env vars are missing."""
    monkeypatch.setattr("linkedin_mcp.server._client_id", "")
    monkeypatch.setattr("linkedin_mcp.server._client_secret", "")
    from linkedin_mcp.server import main

    with pytest.raises(SystemExit):
        main()


def test_main_with_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() should call mcp.run when credentials are set."""
    monkeypatch.setattr("linkedin_mcp.server._client_id", "test-id")
    monkeypatch.setattr("linkedin_mcp.server._client_secret", "test-secret")

    mock_run = MagicMock()
    monkeypatch.setattr("linkedin_mcp.server.mcp.run", mock_run)
    from linkedin_mcp.server import main

    main()
    mock_run.assert_called_once_with(transport="stdio")

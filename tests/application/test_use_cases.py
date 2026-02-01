"""Tests for application use cases."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from linkedin_mcp.application.use_cases.check_auth import CheckAuthUseCase
from linkedin_mcp.application.use_cases.content_calendar import ContentCalendarUseCase
from linkedin_mcp.application.use_cases.draft_post import DraftPostUseCase
from linkedin_mcp.application.use_cases.get_config import GetConfigUseCase
from linkedin_mcp.application.use_cases.get_drafts import GetDraftsUseCase
from linkedin_mcp.application.use_cases.get_optimal_time import GetOptimalTimeUseCase
from linkedin_mcp.application.use_cases.get_scheduled_posts import GetScheduledPostsUseCase
from linkedin_mcp.application.use_cases.optimize_post import OptimizePostUseCase
from linkedin_mcp.application.use_cases.publish_post import PublishPostUseCase
from linkedin_mcp.application.use_cases.schedule_post import SchedulePostUseCase
from linkedin_mcp.application.use_cases.set_default_tone import SetDefaultToneUseCase
from linkedin_mcp.application.use_cases.suggest_hashtags import SuggestHashtagsUseCase
from linkedin_mcp.domain.services.calendar_planner import CalendarPlanner
from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer
from linkedin_mcp.domain.services.hashtag_suggester import HashtagSuggester
from linkedin_mcp.domain.services.post_drafter import PostDrafter
from linkedin_mcp.domain.services.timing_optimizer import TimingOptimizer
from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
from linkedin_mcp.domain.value_objects.post_status import PostStatus
from linkedin_mcp.domain.value_objects.publish_result import PublishResult
from linkedin_mcp.infrastructure.json_config_repository import JsonConfigRepository
from linkedin_mcp.infrastructure.json_credentials_repository import JsonCredentialsRepository
from linkedin_mcp.infrastructure.json_post_repository import JsonPostRepository
from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient


def test_draft_post_drafts_and_persists(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    use_case = DraftPostUseCase(PostDrafter(), repo, config_repo)
    result = use_case.execute("AI trends", tone="professional")
    assert result.post_id is not None
    assert result.topic == "AI trends"
    assert result.status == PostStatus.DRAFT


def test_draft_post_is_retrievable(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    use_case = DraftPostUseCase(PostDrafter(), repo, config_repo)
    result = use_case.execute("testing")
    post = repo.get_by_id(result.post_id)
    assert post is not None
    assert post.topic == "testing"


def test_draft_post_uses_configured_default_tone(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    set_tone_uc = SetDefaultToneUseCase(config_repo)
    set_tone_uc.execute("casual")

    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    result = draft_uc.execute("testing")
    assert result.content.tone == "casual"


def test_draft_post_explicit_tone_overrides_default(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    set_tone_uc = SetDefaultToneUseCase(config_repo)
    set_tone_uc.execute("casual")

    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    result = draft_uc.execute("testing", tone="educational")
    assert result.content.tone == "educational"


def test_draft_post_with_custom_content(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    custom_text = "This is my custom content.\nWith multiple lines."
    result = draft_uc.execute("testing", content=custom_text)
    assert result.content.body == custom_text
    assert result.content.hook == "This is my custom content."
    assert result.content.call_to_action == ""


def test_draft_post_with_custom_content_and_tone(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    custom_text = "Custom post\nAbout AI"
    result = draft_uc.execute("AI", content=custom_text, tone="casual")
    assert result.content.body == custom_text
    assert result.content.tone == "casual"


def test_optimize_post_scores_existing(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_result = draft_uc.execute("leadership")

    optimize_uc = OptimizePostUseCase(ContentOptimizer(), repo)
    result = optimize_uc.execute(draft_result.post_id)
    assert result.score.overall > 0


def test_optimize_post_raises_for_missing(repo: JsonPostRepository) -> None:
    optimize_uc = OptimizePostUseCase(ContentOptimizer(), repo)
    with pytest.raises(ValueError, match="not found"):
        optimize_uc.execute("nonexistent-id")


def test_suggest_hashtags_for_topic(repo: JsonPostRepository) -> None:
    use_case = SuggestHashtagsUseCase(HashtagSuggester(), repo)
    result = use_case.execute("machine learning", industry="technology")
    assert len(result.hashtags) == 4
    assert result.topic == "machine learning"


def test_suggest_hashtags_attaches_to_post(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_result = draft_uc.execute("AI")

    hashtag_uc = SuggestHashtagsUseCase(HashtagSuggester(), repo)
    hashtag_uc.execute("AI", post_id=draft_result.post_id)

    post = repo.get_by_id(draft_result.post_id)
    assert post is not None
    assert len(post.hashtags) == 4


def test_suggest_hashtags_for_nonexistent_post_raises(repo: JsonPostRepository) -> None:
    hashtag_uc = SuggestHashtagsUseCase(HashtagSuggester(), repo)
    with pytest.raises(ValueError, match="not found"):
        hashtag_uc.execute("AI", post_id="nonexistent-id")


def test_get_optimal_time_returns_recommendations() -> None:
    use_case = GetOptimalTimeUseCase(TimingOptimizer())
    result = use_case.execute(timezone="US/Eastern", industry="technology")
    assert len(result.recommendations) == 3
    assert result.timezone == "US/Eastern"


def test_schedule_post_schedules_draft(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_result = draft_uc.execute("testing")

    schedule_uc = SchedulePostUseCase(repo)
    result = schedule_uc.execute(
        draft_result.post_id,
        datetime(2025, 7, 1, 10, 0, tzinfo=timezone.utc),
    )
    assert result.status == PostStatus.SCHEDULED


def test_schedule_post_nonexistent_raises(repo: JsonPostRepository) -> None:
    schedule_uc = SchedulePostUseCase(repo)
    with pytest.raises(ValueError, match="not found"):
        schedule_uc.execute("nonexistent-id", datetime.now(timezone.utc))


def test_get_drafts_lists_draft_posts(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_uc.execute("topic 1")
    draft_uc.execute("topic 2")

    get_uc = GetDraftsUseCase(repo)
    result = get_uc.execute()
    assert result.count == 2


def test_content_calendar_plans_calendar() -> None:
    use_case = ContentCalendarUseCase(CalendarPlanner())
    result = use_case.execute(
        topics=["AI", "Leadership", "Marketing"],
        posts_per_week=3,
    )
    assert result.total_posts == 3
    assert len(result.entries) == 3


def test_get_config_returns_default(config_repo: JsonConfigRepository) -> None:
    use_case = GetConfigUseCase(config_repo)
    result = use_case.execute()
    assert result.default_tone == "professional"
    assert "professional" in result.valid_tones


def test_get_config_returns_updated(config_repo: JsonConfigRepository) -> None:
    SetDefaultToneUseCase(config_repo).execute("casual")
    result = GetConfigUseCase(config_repo).execute()
    assert result.default_tone == "casual"


def test_set_default_tone_sets_valid_tone(config_repo: JsonConfigRepository) -> None:
    use_case = SetDefaultToneUseCase(config_repo)
    result = use_case.execute("inspirational")
    assert result.default_tone == "inspirational"


def test_set_default_tone_rejects_invalid(config_repo: JsonConfigRepository) -> None:
    use_case = SetDefaultToneUseCase(config_repo)
    with pytest.raises(ValueError, match="Invalid tone"):
        use_case.execute("aggressive")


def test_set_default_tone_persists_across_loads(config_repo: JsonConfigRepository) -> None:
    SetDefaultToneUseCase(config_repo).execute("storytelling")
    result = GetConfigUseCase(config_repo).execute()
    assert result.default_tone == "storytelling"


def test_check_auth_returns_unauthenticated_when_no_credentials(tmp_path: Path) -> None:
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    use_case = CheckAuthUseCase(creds_repo)
    result = use_case.execute()
    assert result.authenticated is False
    assert result.person_urn is None


def test_check_auth_returns_authenticated_with_valid_credentials(tmp_path: Path) -> None:
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    creds = LinkedInCredentials(
        access_token="test-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        person_urn="urn:li:person:abc123",
    )
    creds_repo.save(creds)

    use_case = CheckAuthUseCase(creds_repo)
    result = use_case.execute()
    assert result.authenticated is True
    assert result.person_urn == "urn:li:person:abc123"


def test_check_auth_returns_expired_when_token_expired(tmp_path: Path) -> None:
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    creds = LinkedInCredentials(
        access_token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        person_urn="urn:li:person:abc123",
    )
    creds_repo.save(creds)

    use_case = CheckAuthUseCase(creds_repo)
    result = use_case.execute()
    assert result.authenticated is False
    assert result.person_urn == "urn:li:person:abc123"


def test_get_scheduled_posts_lists_scheduled(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft1 = draft_uc.execute("topic 1")
    draft2 = draft_uc.execute("topic 2")

    schedule_uc = SchedulePostUseCase(repo)
    schedule_uc.execute(draft1.post_id, datetime(2025, 7, 1, 10, 0, tzinfo=timezone.utc))
    schedule_uc.execute(draft2.post_id, datetime(2025, 7, 2, 10, 0, tzinfo=timezone.utc))

    get_uc = GetScheduledPostsUseCase(repo)
    result = get_uc.execute()
    assert result.count == 2
    assert len(result.scheduled) == 2


def test_get_scheduled_posts_returns_empty_when_none(
    repo: JsonPostRepository, config_repo: JsonConfigRepository
) -> None:
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_uc.execute("topic 1")
    draft_uc.execute("topic 2")

    get_uc = GetScheduledPostsUseCase(repo)
    result = get_uc.execute()
    assert result.count == 0
    assert result.scheduled == []


def test_publish_post_raises_when_not_authenticated(
    repo: JsonPostRepository, tmp_path: Path
) -> None:
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    use_case = PublishPostUseCase(repo, creds_repo, LinkedInApiClient())
    with pytest.raises(RuntimeError, match="Not authenticated"):
        use_case.execute("some-post-id")


def test_publish_post_raises_when_token_expired(repo: JsonPostRepository, tmp_path: Path) -> None:
    # Create expired credentials
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    creds = LinkedInCredentials(
        access_token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        person_urn="urn:li:person:abc123",
    )
    creds_repo.save(creds)

    use_case = PublishPostUseCase(repo, creds_repo, LinkedInApiClient())
    with pytest.raises(RuntimeError, match="access token has expired"):
        use_case.execute("some-post-id")


def test_publish_post_raises_when_post_not_found(repo: JsonPostRepository, tmp_path: Path) -> None:
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    creds = LinkedInCredentials(
        access_token="test-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        person_urn="urn:li:person:abc123",
    )
    creds_repo.save(creds)

    use_case = PublishPostUseCase(repo, creds_repo, LinkedInApiClient())
    with pytest.raises(ValueError, match="not found"):
        use_case.execute("nonexistent-id")


def test_publish_post_publishes_scheduled_post(
    repo: JsonPostRepository,
    config_repo: JsonConfigRepository,
    tmp_path: Path,
) -> None:
    # Create and schedule a post
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_result = draft_uc.execute("AI trends")
    SchedulePostUseCase(repo).execute(
        draft_result.post_id,
        datetime(2025, 7, 1, 10, 0, tzinfo=timezone.utc),
    )

    # Set up credentials
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    creds = LinkedInCredentials(
        access_token="test-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        person_urn="urn:li:person:abc123",
    )
    creds_repo.save(creds)

    # Mock the publisher
    mock_publisher = MagicMock(spec=LinkedInApiClient)
    mock_publisher.publish.return_value = PublishResult(
        linkedin_post_urn="urn:li:share:999",
        published_at=datetime.now(timezone.utc),
    )

    use_case = PublishPostUseCase(repo, creds_repo, mock_publisher)
    result = use_case.execute(draft_result.post_id)

    assert result.linkedin_post_urn == "urn:li:share:999"
    assert result.status == PostStatus.PUBLISHED

    # Verify post was persisted with URN
    post = repo.get_by_id(draft_result.post_id)
    assert post is not None
    assert post.linkedin_post_urn == "urn:li:share:999"


def test_publish_post_publishes_draft_directly(
    repo: JsonPostRepository,
    config_repo: JsonConfigRepository,
    tmp_path: Path,
) -> None:
    # Create a draft (don't schedule it)
    draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
    draft_result = draft_uc.execute("AI trends")

    # Set up credentials
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    creds = LinkedInCredentials(
        access_token="test-token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        person_urn="urn:li:person:abc123",
    )
    creds_repo.save(creds)

    # Mock the publisher
    mock_publisher = MagicMock(spec=LinkedInApiClient)
    mock_publisher.publish.return_value = PublishResult(
        linkedin_post_urn="urn:li:share:888",
        published_at=datetime.now(timezone.utc),
    )

    use_case = PublishPostUseCase(repo, creds_repo, mock_publisher)
    result = use_case.execute(draft_result.post_id)

    assert result.linkedin_post_urn == "urn:li:share:888"
    assert result.status == PostStatus.PUBLISHED

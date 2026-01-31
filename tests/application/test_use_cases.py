"""Tests for application use cases."""

from pathlib import Path

import pytest

from linkedin_mcp.application.use_cases.content_calendar import ContentCalendarUseCase
from linkedin_mcp.application.use_cases.draft_post import DraftPostUseCase
from linkedin_mcp.application.use_cases.get_config import GetConfigUseCase
from linkedin_mcp.application.use_cases.get_drafts import GetDraftsUseCase
from linkedin_mcp.application.use_cases.get_optimal_time import GetOptimalTimeUseCase
from linkedin_mcp.application.use_cases.optimize_post import OptimizePostUseCase
from linkedin_mcp.application.use_cases.schedule_post import SchedulePostUseCase
from linkedin_mcp.application.use_cases.set_default_tone import SetDefaultToneUseCase
from linkedin_mcp.application.use_cases.suggest_hashtags import SuggestHashtagsUseCase
from linkedin_mcp.domain.services.calendar_planner import CalendarPlanner
from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer
from linkedin_mcp.domain.services.hashtag_suggester import HashtagSuggester
from linkedin_mcp.domain.services.post_drafter import PostDrafter
from linkedin_mcp.domain.services.timing_optimizer import TimingOptimizer
from linkedin_mcp.domain.value_objects.post_status import PostStatus
from linkedin_mcp.infrastructure.json_config_repository import JsonConfigRepository
from linkedin_mcp.infrastructure.json_post_repository import JsonPostRepository


@pytest.fixture
def repo(tmp_path: Path) -> JsonPostRepository:
    return JsonPostRepository(storage_path=tmp_path / "posts.json")


@pytest.fixture
def config_repo(tmp_path: Path) -> JsonConfigRepository:
    return JsonConfigRepository(storage_path=tmp_path / "config.json")


class TestDraftPostUseCase:
    """Tests for the draft post use case."""

    def test_drafts_and_persists_post(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        use_case = DraftPostUseCase(PostDrafter(), repo, config_repo)
        result = use_case.execute("AI trends", tone="professional")
        assert result.post_id is not None
        assert result.topic == "AI trends"
        assert result.status == PostStatus.DRAFT

    def test_draft_is_retrievable(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        use_case = DraftPostUseCase(PostDrafter(), repo, config_repo)
        result = use_case.execute("testing")
        post = repo.get_by_id(result.post_id)
        assert post is not None
        assert post.topic == "testing"

    def test_draft_uses_configured_default_tone(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        set_tone_uc = SetDefaultToneUseCase(config_repo)
        set_tone_uc.execute("casual")

        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        result = draft_uc.execute("testing")
        assert result.content.tone == "casual"

    def test_draft_explicit_tone_overrides_default(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        set_tone_uc = SetDefaultToneUseCase(config_repo)
        set_tone_uc.execute("casual")

        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        result = draft_uc.execute("testing", tone="educational")
        assert result.content.tone == "educational"


class TestOptimizePostUseCase:
    """Tests for the optimize post use case."""

    def test_scores_existing_post(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        draft_result = draft_uc.execute("leadership")

        optimize_uc = OptimizePostUseCase(ContentOptimizer(), repo)
        result = optimize_uc.execute(draft_result.post_id)
        assert result.score.overall > 0

    def test_raises_for_missing_post(self, repo: JsonPostRepository) -> None:
        optimize_uc = OptimizePostUseCase(ContentOptimizer(), repo)
        with pytest.raises(ValueError, match="not found"):
            optimize_uc.execute("nonexistent-id")


class TestSuggestHashtagsUseCase:
    """Tests for the suggest hashtags use case."""

    def test_suggests_hashtags_for_topic(self, repo: JsonPostRepository) -> None:
        use_case = SuggestHashtagsUseCase(HashtagSuggester(), repo)
        result = use_case.execute("machine learning", industry="technology")
        assert len(result.hashtags) == 4
        assert result.topic == "machine learning"

    def test_attaches_hashtags_to_post(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        draft_result = draft_uc.execute("AI")

        hashtag_uc = SuggestHashtagsUseCase(HashtagSuggester(), repo)
        hashtag_uc.execute("AI", post_id=draft_result.post_id)

        post = repo.get_by_id(draft_result.post_id)
        assert post is not None
        assert len(post.hashtags) == 4


class TestGetOptimalTimeUseCase:
    """Tests for the get optimal time use case."""

    def test_returns_recommendations(self) -> None:
        use_case = GetOptimalTimeUseCase(TimingOptimizer())
        result = use_case.execute(timezone="US/Eastern", industry="technology")
        assert len(result.recommendations) == 3
        assert result.timezone == "US/Eastern"


class TestSchedulePostUseCase:
    """Tests for the schedule post use case."""

    def test_schedules_draft_post(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        from datetime import datetime, timezone

        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        draft_result = draft_uc.execute("testing")

        schedule_uc = SchedulePostUseCase(repo)
        result = schedule_uc.execute(
            draft_result.post_id,
            datetime(2025, 7, 1, 10, 0, tzinfo=timezone.utc),
        )
        assert result.status == PostStatus.SCHEDULED


class TestGetDraftsUseCase:
    """Tests for the get drafts use case."""

    def test_lists_draft_posts(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository
    ) -> None:
        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        draft_uc.execute("topic 1")
        draft_uc.execute("topic 2")

        get_uc = GetDraftsUseCase(repo)
        result = get_uc.execute()
        assert result.count == 2


class TestContentCalendarUseCase:
    """Tests for the content calendar use case."""

    def test_plans_calendar(self) -> None:
        use_case = ContentCalendarUseCase(CalendarPlanner())
        result = use_case.execute(
            topics=["AI", "Leadership", "Marketing"],
            posts_per_week=3,
        )
        assert result.total_posts == 3
        assert len(result.entries) == 3


class TestGetConfigUseCase:
    """Tests for the get config use case."""

    def test_returns_default_config(self, config_repo: JsonConfigRepository) -> None:
        use_case = GetConfigUseCase(config_repo)
        result = use_case.execute()
        assert result.default_tone == "professional"
        assert "professional" in result.valid_tones

    def test_returns_updated_config(self, config_repo: JsonConfigRepository) -> None:
        SetDefaultToneUseCase(config_repo).execute("casual")
        result = GetConfigUseCase(config_repo).execute()
        assert result.default_tone == "casual"


class TestSetDefaultToneUseCase:
    """Tests for the set default tone use case."""

    def test_sets_valid_tone(self, config_repo: JsonConfigRepository) -> None:
        use_case = SetDefaultToneUseCase(config_repo)
        result = use_case.execute("inspirational")
        assert result.default_tone == "inspirational"

    def test_rejects_invalid_tone(self, config_repo: JsonConfigRepository) -> None:
        use_case = SetDefaultToneUseCase(config_repo)
        with pytest.raises(ValueError, match="Invalid tone"):
            use_case.execute("aggressive")

    def test_persists_across_loads(self, config_repo: JsonConfigRepository) -> None:
        SetDefaultToneUseCase(config_repo).execute("storytelling")
        result = GetConfigUseCase(config_repo).execute()
        assert result.default_tone == "storytelling"


class TestCheckAuthUseCase:
    """Tests for the check auth use case."""

    def test_returns_unauthenticated_when_no_credentials(self, tmp_path: Path) -> None:
        from linkedin_mcp.application.use_cases.check_auth import CheckAuthUseCase
        from linkedin_mcp.infrastructure.json_credentials_repository import (
            JsonCredentialsRepository,
        )

        creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
        use_case = CheckAuthUseCase(creds_repo)
        result = use_case.execute()
        assert result.authenticated is False
        assert result.person_urn is None

    def test_returns_authenticated_with_valid_credentials(self, tmp_path: Path) -> None:
        from datetime import datetime, timedelta, timezone

        from linkedin_mcp.application.use_cases.check_auth import CheckAuthUseCase
        from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
        from linkedin_mcp.infrastructure.json_credentials_repository import (
            JsonCredentialsRepository,
        )

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

    def test_returns_expired_when_token_expired(self, tmp_path: Path) -> None:
        from datetime import datetime, timedelta, timezone

        from linkedin_mcp.application.use_cases.check_auth import CheckAuthUseCase
        from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
        from linkedin_mcp.infrastructure.json_credentials_repository import (
            JsonCredentialsRepository,
        )

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


class TestPublishPostUseCase:
    """Tests for the publish post use case."""

    def test_raises_when_not_authenticated(self, repo: JsonPostRepository, tmp_path: Path) -> None:
        from linkedin_mcp.application.use_cases.publish_post import PublishPostUseCase
        from linkedin_mcp.infrastructure.json_credentials_repository import (
            JsonCredentialsRepository,
        )
        from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient

        creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
        use_case = PublishPostUseCase(repo, creds_repo, LinkedInApiClient())
        with pytest.raises(RuntimeError, match="Not authenticated"):
            use_case.execute("some-post-id")

    def test_raises_when_post_not_found(
        self, repo: JsonPostRepository, config_repo: JsonConfigRepository, tmp_path: Path
    ) -> None:
        from datetime import datetime, timedelta, timezone

        from linkedin_mcp.application.use_cases.publish_post import PublishPostUseCase
        from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
        from linkedin_mcp.infrastructure.json_credentials_repository import (
            JsonCredentialsRepository,
        )
        from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient

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

    def test_publishes_scheduled_post(
        self,
        repo: JsonPostRepository,
        config_repo: JsonConfigRepository,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from datetime import datetime, timedelta, timezone
        from unittest.mock import MagicMock

        from linkedin_mcp.application.use_cases.publish_post import PublishPostUseCase
        from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
        from linkedin_mcp.domain.value_objects.publish_result import PublishResult
        from linkedin_mcp.infrastructure.json_credentials_repository import (
            JsonCredentialsRepository,
        )
        from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient

        # Create and schedule a post
        draft_uc = DraftPostUseCase(PostDrafter(), repo, config_repo)
        draft_result = draft_uc.execute("AI trends")
        from linkedin_mcp.application.use_cases.schedule_post import SchedulePostUseCase

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

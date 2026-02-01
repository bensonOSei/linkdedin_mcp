"""Tests for the dependency injection container."""

from pathlib import Path
from unittest.mock import patch

from linkedin_mcp.application.use_cases.authenticate import AuthenticateUseCase
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
from linkedin_mcp.container import Container


def test_container_wires_all_use_cases(tmp_path: Path) -> None:
    """Container should instantiate all use cases."""
    posts_path = tmp_path / "posts.json"
    config_path = tmp_path / "config.json"
    creds_path = tmp_path / "creds.json"

    with (
        patch("linkedin_mcp.container.JsonPostRepository") as mock_post_repo_cls,
        patch("linkedin_mcp.container.JsonConfigRepository") as mock_config_repo_cls,
        patch("linkedin_mcp.container.JsonCredentialsRepository") as mock_creds_repo_cls,
    ):
        # Make the mock constructors return instances with the right interface
        mock_post_repo_cls.return_value = mock_post_repo_cls
        mock_config_repo_cls.return_value = mock_config_repo_cls
        mock_creds_repo_cls.return_value = mock_creds_repo_cls

        c = Container(client_id="test-id", client_secret="test-secret")

    assert isinstance(c.draft_post, DraftPostUseCase)
    assert isinstance(c.optimize_post, OptimizePostUseCase)
    assert isinstance(c.suggest_hashtags, SuggestHashtagsUseCase)
    assert isinstance(c.get_optimal_time, GetOptimalTimeUseCase)
    assert isinstance(c.schedule_post, SchedulePostUseCase)
    assert isinstance(c.content_calendar, ContentCalendarUseCase)
    assert isinstance(c.get_drafts, GetDraftsUseCase)
    assert isinstance(c.get_scheduled_posts, GetScheduledPostsUseCase)
    assert isinstance(c.get_config, GetConfigUseCase)
    assert isinstance(c.set_default_tone, SetDefaultToneUseCase)
    assert isinstance(c.authenticate, AuthenticateUseCase)
    assert isinstance(c.publish_post, PublishPostUseCase)
    assert isinstance(c.check_auth, CheckAuthUseCase)

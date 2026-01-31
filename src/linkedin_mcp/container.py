"""Dependency injection container wiring all layers together."""

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
from linkedin_mcp.domain.services.calendar_planner import CalendarPlanner
from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer
from linkedin_mcp.domain.services.hashtag_suggester import HashtagSuggester
from linkedin_mcp.domain.services.post_drafter import PostDrafter
from linkedin_mcp.domain.services.timing_optimizer import TimingOptimizer
from linkedin_mcp.infrastructure.json_config_repository import JsonConfigRepository
from linkedin_mcp.infrastructure.json_credentials_repository import JsonCredentialsRepository
from linkedin_mcp.infrastructure.json_post_repository import JsonPostRepository
from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient
from linkedin_mcp.infrastructure.oauth_server import OAuthCallbackServer


class Container:
    """Wires all dependencies for the application."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initialize all use cases with their dependencies.

        Args:
            client_id: LinkedIn app client ID.
            client_secret: LinkedIn app client secret.
        """
        repo = JsonPostRepository()
        config_repo = JsonConfigRepository()
        creds_repo = JsonCredentialsRepository()
        publisher = LinkedInApiClient()
        oauth_server = OAuthCallbackServer()

        self.draft_post = DraftPostUseCase(PostDrafter(), repo, config_repo)
        self.optimize_post = OptimizePostUseCase(ContentOptimizer(), repo)
        self.suggest_hashtags = SuggestHashtagsUseCase(HashtagSuggester(), repo)
        self.get_optimal_time = GetOptimalTimeUseCase(TimingOptimizer())
        self.schedule_post = SchedulePostUseCase(repo)
        self.content_calendar = ContentCalendarUseCase(CalendarPlanner())
        self.get_drafts = GetDraftsUseCase(repo)
        self.get_scheduled_posts = GetScheduledPostsUseCase(repo)
        self.get_config = GetConfigUseCase(config_repo)
        self.set_default_tone = SetDefaultToneUseCase(config_repo)
        self.authenticate = AuthenticateUseCase(
            creds_repo, publisher, oauth_server, client_id, client_secret
        )
        self.publish_post = PublishPostUseCase(repo, creds_repo, publisher)
        self.check_auth = CheckAuthUseCase(creds_repo)

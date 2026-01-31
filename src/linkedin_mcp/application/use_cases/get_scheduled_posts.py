"""Use case for listing scheduled posts."""

from linkedin_mcp.application.dtos import PostSummary, ScheduledPostListResult
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.value_objects.post_status import PostStatus


class GetScheduledPostsUseCase:
    """Lists all posts in scheduled status."""

    def __init__(self, repository: PostRepository) -> None:
        """Initialize with required dependencies.

        Args:
            repository: Repository for post access.
        """
        self._repository = repository

    def execute(self) -> ScheduledPostListResult:
        """Get all scheduled posts.

        Returns:
            ScheduledPostListResult with list of scheduled post summaries.
        """
        posts = self._repository.get_by_status(PostStatus.SCHEDULED)
        summaries = [
            PostSummary(
                post_id=post.id,
                topic=post.topic,
                status=post.status,
                hook=post.content.hook,
                created_at=post.created_at.isoformat(),
            )
            for post in posts
        ]

        return ScheduledPostListResult(scheduled=summaries, count=len(summaries))

"""Use case for listing draft posts."""

from linkedin_mcp.application.dtos import DraftListResult, PostSummary
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.value_objects.post_status import PostStatus


class GetDraftsUseCase:
    """Lists all posts in draft status."""

    def __init__(self, repository: PostRepository) -> None:
        """Initialize with required dependencies.

        Args:
            repository: Repository for post access.
        """
        self._repository = repository

    def execute(self) -> DraftListResult:
        """Get all draft posts.

        Returns:
            DraftListResult with list of draft post summaries.
        """
        posts = self._repository.get_by_status(PostStatus.DRAFT)
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

        return DraftListResult(drafts=summaries, count=len(summaries))

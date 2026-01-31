"""Use case for optimizing a post's engagement potential."""

from linkedin_mcp.application.dtos import OptimizePostResult
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer


class OptimizePostUseCase:
    """Scores a post for engagement and provides improvement suggestions."""

    def __init__(self, optimizer: ContentOptimizer, repository: PostRepository) -> None:
        """Initialize with required dependencies.

        Args:
            optimizer: Service for scoring content.
            repository: Repository for post access.
        """
        self._optimizer = optimizer
        self._repository = repository

    def execute(self, post_id: str) -> OptimizePostResult:
        """Optimize a post and return engagement score.

        Args:
            post_id: ID of the post to optimize.

        Returns:
            OptimizePostResult with engagement score and suggestions.

        Raises:
            ValueError: If post is not found.
        """
        post = self._repository.get_by_id(post_id)
        if post is None:
            msg = f"Post with ID '{post_id}' not found."
            raise ValueError(msg)

        score = self._optimizer.score(post.content, len(post.hashtags))
        post.set_engagement_score(score)
        self._repository.save(post)

        return OptimizePostResult(
            post_id=post.id,
            score=score,
            content=post.content,
        )

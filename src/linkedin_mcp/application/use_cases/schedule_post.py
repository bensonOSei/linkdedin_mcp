"""Use case for scheduling a post."""

from datetime import datetime

from linkedin_mcp.application.dtos import SchedulePostResult
from linkedin_mcp.domain.repositories.post_repository import PostRepository


class SchedulePostUseCase:
    """Schedules a draft post for a specific time."""

    def __init__(self, repository: PostRepository) -> None:
        """Initialize with required dependencies.

        Args:
            repository: Repository for post access.
        """
        self._repository = repository

    def execute(self, post_id: str, scheduled_time: datetime) -> SchedulePostResult:
        """Schedule a post for publishing.

        Args:
            post_id: ID of the post to schedule.
            scheduled_time: When to publish the post.

        Returns:
            SchedulePostResult with updated post details.

        Raises:
            ValueError: If post is not found or cannot be scheduled.
        """
        post = self._repository.get_by_id(post_id)
        if post is None:
            msg = f"Post with ID '{post_id}' not found."
            raise ValueError(msg)

        post.schedule(scheduled_time)
        self._repository.save(post)

        return SchedulePostResult(
            post_id=post.id,
            status=post.status,
            scheduled_time=scheduled_time.isoformat(),
        )

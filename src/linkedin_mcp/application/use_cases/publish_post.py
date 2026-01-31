"""Use case for publishing a post to LinkedIn."""

from linkedin_mcp.application.dtos import PublishPostResult
from linkedin_mcp.domain.repositories.credentials_repository import CredentialsRepository
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.services.linkedin_publisher import LinkedInPublisher


class PublishPostUseCase:
    """Publishes a scheduled post to LinkedIn via the API."""

    def __init__(
        self,
        repository: PostRepository,
        credentials_repository: CredentialsRepository,
        publisher: LinkedInPublisher,
    ) -> None:
        """Initialize with required dependencies.

        Args:
            repository: Repository for post access.
            credentials_repository: Repository for LinkedIn credentials.
            publisher: LinkedIn publishing gateway.
        """
        self._repository = repository
        self._credentials_repository = credentials_repository
        self._publisher = publisher

    def execute(self, post_id: str) -> PublishPostResult:
        """Publish a post to LinkedIn.

        Args:
            post_id: ID of the scheduled post to publish.

        Returns:
            PublishPostResult with LinkedIn post URN and status.

        Raises:
            ValueError: If post not found or not in scheduled status.
            RuntimeError: If not authenticated or token expired.
        """
        credentials = self._credentials_repository.load()
        if credentials is None:
            msg = "Not authenticated. Run linkedin_authenticate first."
            raise RuntimeError(msg)

        if credentials.is_expired:
            msg = "LinkedIn access token has expired. Re-authenticate with linkedin_authenticate."
            raise RuntimeError(msg)

        post = self._repository.get_by_id(post_id)
        if post is None:
            msg = f"Post with ID '{post_id}' not found."
            raise ValueError(msg)

        result = self._publisher.publish(
            post=post,
            access_token=credentials.access_token,
            person_urn=credentials.person_urn,
        )

        post.publish(linkedin_post_urn=result.linkedin_post_urn)
        self._repository.save(post)

        return PublishPostResult(
            post_id=post.id,
            linkedin_post_urn=result.linkedin_post_urn,
            status=post.status,
            published_at=result.published_at.isoformat(),
        )

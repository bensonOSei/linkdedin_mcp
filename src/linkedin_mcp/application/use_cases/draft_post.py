"""Use case for drafting a new LinkedIn post."""

from linkedin_mcp.application.dtos import DraftPostResult
from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.repositories.config_repository import ConfigRepository
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.services.post_drafter import PostDrafter
from linkedin_mcp.domain.value_objects.post_content import PostContent


class DraftPostUseCase:
    """Drafts a new LinkedIn post and persists it."""

    def __init__(
        self,
        drafter: PostDrafter,
        repository: PostRepository,
        config_repository: ConfigRepository,
    ) -> None:
        """Initialize with required dependencies.

        Args:
            drafter: Service for generating post content.
            repository: Repository for persisting posts.
            config_repository: Repository for user configuration.
        """
        self._drafter = drafter
        self._repository = repository
        self._config_repository = config_repository

    def execute(
        self,
        topic: str,
        tone: str | None = None,
        content: str | None = None,
    ) -> DraftPostResult:
        """Draft a new post.

        Args:
            topic: The subject matter of the post.
            tone: Writing tone for the post. Uses configured default if not provided.
            content: Custom post body text. If provided, skips template generation.

        Returns:
            DraftPostResult with the created post details.
        """
        if tone is None:
            config = self._config_repository.load()
            tone = config.default_tone

        if content is not None:
            post_content = PostContent(
                body=content,
                hook=content.split("\n")[0],
                call_to_action="",
                tone=tone,
            )
        else:
            post_content = self._drafter.draft(topic, tone)

        post = Post(topic=topic, content=post_content)
        self._repository.save(post)

        return DraftPostResult(
            post_id=post.id,
            topic=post.topic,
            content=post.content,
            status=post.status,
        )

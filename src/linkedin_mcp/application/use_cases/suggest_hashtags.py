"""Use case for suggesting hashtags for a post."""

from linkedin_mcp.application.dtos import HashtagSuggestionResult
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.services.hashtag_suggester import HashtagSuggester


class SuggestHashtagsUseCase:
    """Suggests and optionally attaches hashtags to a post."""

    def __init__(self, suggester: HashtagSuggester, repository: PostRepository) -> None:
        """Initialize with required dependencies.

        Args:
            suggester: Service for generating hashtag recommendations.
            repository: Repository for post access.
        """
        self._suggester = suggester
        self._repository = repository

    def execute(
        self,
        topic: str,
        industry: str = "default",
        post_id: str | None = None,
    ) -> HashtagSuggestionResult:
        """Suggest hashtags for a topic, optionally attaching to a post.

        Args:
            topic: The topic to generate hashtags for.
            industry: Industry vertical for targeted suggestions.
            post_id: Optional post ID to attach hashtags to.

        Returns:
            HashtagSuggestionResult with suggested hashtags.

        Raises:
            ValueError: If post_id is provided but post is not found.
        """
        hashtags = self._suggester.suggest(topic, industry)

        if post_id is not None:
            post = self._repository.get_by_id(post_id)
            if post is None:
                msg = f"Post with ID '{post_id}' not found."
                raise ValueError(msg)
            post.add_hashtags(hashtags)
            self._repository.save(post)

        return HashtagSuggestionResult(
            post_id=post_id,
            topic=topic,
            hashtags=hashtags,
        )

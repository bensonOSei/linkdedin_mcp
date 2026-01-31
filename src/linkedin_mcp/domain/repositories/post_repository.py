"""Abstract base class for post persistence."""

from abc import ABC, abstractmethod

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.post_status import PostStatus


class PostRepository(ABC):
    """Interface for post storage operations."""

    @abstractmethod
    def save(self, post: Post) -> None:
        """Persist a post."""

    @abstractmethod
    def get_by_id(self, post_id: str) -> Post | None:
        """Retrieve a post by its ID."""

    @abstractmethod
    def get_by_status(self, status: PostStatus) -> list[Post]:
        """Retrieve all posts with a given status."""

    @abstractmethod
    def get_all(self) -> list[Post]:
        """Retrieve all posts."""

    @abstractmethod
    def delete(self, post_id: str) -> None:
        """Delete a post by its ID."""

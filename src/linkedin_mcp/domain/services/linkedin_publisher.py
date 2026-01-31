"""Abstract base class for LinkedIn publishing gateway."""

from abc import ABC, abstractmethod

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.publish_result import PublishResult


class LinkedInPublisher(ABC):
    """Interface for publishing posts to LinkedIn.

    The actual HTTP implementation lives in infrastructure.
    """

    @abstractmethod
    def publish(self, post: Post, access_token: str, person_urn: str) -> PublishResult:
        """Publish a post to LinkedIn.

        Args:
            post: The post entity to publish.
            access_token: OAuth2 access token.
            person_urn: LinkedIn person URN of the author.

        Returns:
            PublishResult with the LinkedIn post URN and timestamp.
        """

    @abstractmethod
    def get_profile_urn(self, access_token: str) -> str:
        """Retrieve the authenticated user's LinkedIn person URN.

        Args:
            access_token: OAuth2 access token.

        Returns:
            The person URN string (e.g., 'urn:li:person:abc123').
        """

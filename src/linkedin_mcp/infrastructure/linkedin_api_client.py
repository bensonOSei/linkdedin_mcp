"""LinkedIn REST API client implementing the LinkedInPublisher gateway."""

from datetime import datetime, timezone

import httpx
from loguru import logger

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.services.linkedin_publisher import LinkedInPublisher
from linkedin_mcp.domain.value_objects.publish_result import PublishResult

_POSTS_URL = "https://api.linkedin.com/rest/posts"
_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
_LINKEDIN_VERSION = "202502"
_MAX_COMMENTARY_LENGTH = 3000
_TIMEOUT = 30.0


class LinkedInApiClient(LinkedInPublisher):
    """Publishes posts to LinkedIn via the REST Posts API.

    Uses httpx for HTTP calls with the required LinkedIn headers.
    """

    def publish(self, post: Post, access_token: str, person_urn: str) -> PublishResult:
        """Publish a post to LinkedIn.

        Args:
            post: The post entity to publish.
            access_token: OAuth2 access token.
            person_urn: LinkedIn person URN of the author.

        Returns:
            PublishResult with the LinkedIn post URN and timestamp.

        Raises:
            RuntimeError: If the LinkedIn API returns an error.
        """
        commentary = self._build_commentary(post)

        logger.debug("Commentary length: %d", len(commentary))
        logger.debug("First 200 chars: %s", commentary[:200])
        logger.debug("Last 200 chars: %s", commentary[-200:])

        if len(commentary) > _MAX_COMMENTARY_LENGTH:
            msg = (
                f"Post content is {len(commentary)} characters, "
                f"but LinkedIn allows a maximum of {_MAX_COMMENTARY_LENGTH}. "
                "Please shorten the post before publishing."
            )
            raise ValueError(msg)

        payload = {
            "author": person_urn,
            "commentary": commentary,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        logger.debug("Publishing post with commentary: %s", commentary[:300])

        response = httpx.post(
            _POSTS_URL,
            json=payload,
            headers=self._build_headers(access_token),
            timeout=_TIMEOUT,
        )

        logger.debug("LinkedIn API response - Status: %d", response.status_code)

        if response.status_code != 201:
            msg = f"LinkedIn API error ({response.status_code}): {response.text}"
            raise RuntimeError(msg)

        post_urn = response.headers.get("x-restli-id", "")

        return PublishResult(
            linkedin_post_urn=post_urn,
            published_at=datetime.now(timezone.utc),
        )

    def get_profile_urn(self, access_token: str) -> str:
        """Retrieve the authenticated user's LinkedIn person URN.

        Args:
            access_token: OAuth2 access token.

        Returns:
            The person URN string.

        Raises:
            RuntimeError: If the LinkedIn API returns an error.
        """
        response = httpx.get(
            _USERINFO_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=_TIMEOUT,
        )

        if response.status_code != 200:
            msg = f"LinkedIn userinfo API error ({response.status_code}): {response.text}"
            raise RuntimeError(msg)

        data = response.json()
        sub: str = data["sub"]
        return f"urn:li:person:{sub}"

    def _build_headers(self, access_token: str) -> dict[str, str]:
        """Build required LinkedIn API headers.

        Args:
            access_token: OAuth2 access token.

        Returns:
            Headers dictionary.
        """
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": _LINKEDIN_VERSION,
        }

    def _build_commentary(self, post: Post) -> str:
        """Build the post commentary from content and hashtags.

        Args:
            post: The post entity.

        Returns:
            Formatted commentary string for LinkedIn.
        """
        commentary = post.content.body

        if post.hashtags:
            hashtag_str = " ".join(tag.name for tag in post.hashtags)
            commentary = f"{commentary}\n\n{hashtag_str}"

        return commentary

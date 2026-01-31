"""Tests for the LinkedIn API client with mocked HTTP calls."""

from unittest.mock import MagicMock

import httpx
import pytest

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.hashtag import Hashtag
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient


@pytest.fixture
def client() -> LinkedInApiClient:
    return LinkedInApiClient()


@pytest.fixture
def sample_post() -> Post:
    return Post(
        topic="AI trends",
        content=PostContent(
            body="Here's what I learned about AI.",
            hook="Here's what I learned:",
            call_to_action="Share your thoughts!",
            tone="professional",
        ),
        hashtags=[
            Hashtag(name="#AI", category="industry"),
            Hashtag(name="#Tech", category="broad"),
        ],
    )


class TestLinkedInApiClientPublish:
    """Tests for the publish method."""

    def test_publish_success(
        self,
        client: LinkedInApiClient,
        sample_post: Post,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.headers = {"x-restli-id": "urn:li:share:123456"}

        monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

        result = client.publish(sample_post, "fake-token", "urn:li:person:abc")
        assert result.linkedin_post_urn == "urn:li:share:123456"
        assert result.published_at.tzinfo is not None

    def test_publish_api_error(
        self,
        client: LinkedInApiClient,
        sample_post: Post,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

        with pytest.raises(RuntimeError, match="LinkedIn API error"):
            client.publish(sample_post, "fake-token", "urn:li:person:abc")

    def test_publish_includes_hashtags_in_commentary(
        self,
        client: LinkedInApiClient,
        sample_post: Post,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured_kwargs: dict[str, object] = {}

        def mock_post(*args: object, **kwargs: object) -> MagicMock:
            captured_kwargs.update(kwargs)
            resp = MagicMock(spec=httpx.Response)
            resp.status_code = 201
            resp.headers = {"x-restli-id": "urn:li:share:789"}
            return resp

        monkeypatch.setattr(httpx, "post", mock_post)

        client.publish(sample_post, "fake-token", "urn:li:person:abc")

        payload = captured_kwargs["json"]
        assert "#AI" in payload["commentary"]
        assert "#Tech" in payload["commentary"]


class TestLinkedInApiClientProfile:
    """Tests for the get_profile_urn method."""

    def test_get_profile_urn_success(
        self,
        client: LinkedInApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"sub": "abc123"}

        monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_response)

        urn = client.get_profile_urn("fake-token")
        assert urn == "urn:li:person:abc123"

    def test_get_profile_urn_error(
        self,
        client: LinkedInApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_response)

        with pytest.raises(RuntimeError, match="userinfo API error"):
            client.get_profile_urn("bad-token")

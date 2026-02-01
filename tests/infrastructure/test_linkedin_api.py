"""Tests for the LinkedIn API client with mocked HTTP calls."""

from unittest.mock import MagicMock

import httpx
import pytest

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient


def test_publish_success(
    api_client: LinkedInApiClient,
    post_with_hashtags: Post,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 201
    mock_response.headers = {"x-restli-id": "urn:li:share:123456"}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

    result = api_client.publish(post_with_hashtags, "fake-token", "urn:li:person:abc")
    assert result.linkedin_post_urn == "urn:li:share:123456"
    assert result.published_at.tzinfo is not None


def test_publish_api_error(
    api_client: LinkedInApiClient,
    post_with_hashtags: Post,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 403
    mock_response.text = "Forbidden"

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

    with pytest.raises(RuntimeError, match="LinkedIn API error"):
        api_client.publish(post_with_hashtags, "fake-token", "urn:li:person:abc")


def test_publish_includes_hashtags_in_commentary(
    api_client: LinkedInApiClient,
    post_with_hashtags: Post,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_kwargs: dict[str, object] = {}

    def mock_post(url: str, **kwargs: object) -> MagicMock:
        captured_kwargs.update(kwargs)
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 201
        resp.headers = {"x-restli-id": "urn:li:share:789"}
        return resp

    monkeypatch.setattr(httpx, "post", mock_post)

    api_client.publish(post_with_hashtags, "fake-token", "urn:li:person:abc")

    payload = captured_kwargs["json"]
    assert "#AI" in payload["commentary"]
    assert "#Tech" in payload["commentary"]


def test_get_profile_urn_success(
    api_client: LinkedInApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"sub": "abc123"}

    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_response)

    urn = api_client.get_profile_urn("fake-token")
    assert urn == "urn:li:person:abc123"


def test_get_profile_urn_error(
    api_client: LinkedInApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_response)

    with pytest.raises(RuntimeError, match="userinfo API error"):
        api_client.get_profile_urn("bad-token")


def test_publish_with_too_long_content(
    api_client: LinkedInApiClient,
) -> None:
    # Create a post with content exceeding LinkedIn's 3000 char limit
    very_long_post = Post(
        topic="test",
        content=PostContent(
            body="A" * 3500,  # Exceeds limit
            hook="Hook",
            call_to_action="CTA",
            tone="professional",
        ),
    )

    with pytest.raises(ValueError, match="3500 characters"):
        api_client.publish(very_long_post, "token", "urn:li:person:abc")


def test_publish_without_hashtags(
    api_client: LinkedInApiClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post_without_hashtags = Post(
        topic="test",
        content=PostContent(
            body="Content without hashtags",
            hook="Hook",
            call_to_action="CTA",
            tone="professional",
        ),
    )

    captured_kwargs: dict[str, object] = {}

    def mock_post(url: str, **kwargs: object) -> MagicMock:
        captured_kwargs.update(kwargs)
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 201
        resp.headers = {"x-restli-id": "urn:li:share:123"}
        return resp

    monkeypatch.setattr(httpx, "post", mock_post)

    api_client.publish(post_without_hashtags, "token", "urn:li:person:abc")

    payload = captured_kwargs["json"]
    # Commentary should not have extra newlines for hashtags
    assert payload["commentary"] == "Content without hashtags"

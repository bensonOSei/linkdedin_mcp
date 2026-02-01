"""Tests for the AuthenticateUseCase."""

from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

from linkedin_mcp.application.use_cases.authenticate import AuthenticateUseCase
from linkedin_mcp.infrastructure.json_credentials_repository import JsonCredentialsRepository
from linkedin_mcp.infrastructure.linkedin_api_client import LinkedInApiClient
from linkedin_mcp.infrastructure.oauth_server import OAuthCallbackServer


def _make_use_case(
    tmp_path: Path,
    oauth_server: OAuthCallbackServer | None = None,
    publisher: LinkedInApiClient | None = None,
) -> AuthenticateUseCase:
    """Build an AuthenticateUseCase with mocked dependencies."""
    creds_repo = JsonCredentialsRepository(storage_path=tmp_path / "creds.json")
    if oauth_server is None:
        oauth_server = MagicMock(spec=OAuthCallbackServer)
        oauth_server.redirect_uri = "http://localhost:8099/callback"
    if publisher is None:
        publisher = MagicMock(spec=LinkedInApiClient)
    return AuthenticateUseCase(
        credentials_repository=creds_repo,
        publisher=publisher,
        oauth_server=oauth_server,
        client_id="test-client-id",
        client_secret="test-client-secret",
    )


def test_start_auth_returns_auth_url(tmp_path: Path) -> None:
    """start_auth should return a waiting status and LinkedIn auth URL."""
    mock_server = MagicMock(spec=OAuthCallbackServer)
    mock_server.redirect_uri = "http://localhost:8099/callback"

    use_case = _make_use_case(tmp_path, oauth_server=mock_server)
    result = use_case.start_auth()

    assert result.status == "waiting"
    assert result.auth_url is not None
    assert "linkedin.com/oauth/v2/authorization" in result.auth_url
    assert "test-client-id" in result.auth_url
    mock_server.start.assert_called_once()


def test_complete_auth_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """complete_auth should exchange code for token and save credentials."""
    mock_server = MagicMock(spec=OAuthCallbackServer)
    mock_server.redirect_uri = "http://localhost:8099/callback"
    mock_server.get_code.return_value = "auth-code-123"

    mock_publisher = MagicMock(spec=LinkedInApiClient)
    mock_publisher.get_profile_urn.return_value = "urn:li:person:abc"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new-token",
        "expires_in": 3600,
    }
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

    use_case = _make_use_case(tmp_path, oauth_server=mock_server, publisher=mock_publisher)
    result = use_case.complete_auth(timeout=5)

    assert result.status == "authenticated"
    assert result.person_urn == "urn:li:person:abc"
    assert result.expires_at is not None


def test_complete_auth_timeout(tmp_path: Path) -> None:
    """complete_auth should handle TimeoutError from oauth server."""
    mock_server = MagicMock(spec=OAuthCallbackServer)
    mock_server.redirect_uri = "http://localhost:8099/callback"
    mock_server.get_code.side_effect = TimeoutError("Timed out")

    use_case = _make_use_case(tmp_path, oauth_server=mock_server)
    result = use_case.complete_auth(timeout=1)

    assert "failed" in result.status


def test_complete_auth_denied(tmp_path: Path) -> None:
    """complete_auth should handle RuntimeError (auth denied)."""
    mock_server = MagicMock(spec=OAuthCallbackServer)
    mock_server.redirect_uri = "http://localhost:8099/callback"
    mock_server.get_code.side_effect = RuntimeError("Authorization denied")

    use_case = _make_use_case(tmp_path, oauth_server=mock_server)
    result = use_case.complete_auth(timeout=1)

    assert "failed" in result.status


def test_exchange_code_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """complete_auth should raise when token exchange returns non-200."""
    mock_server = MagicMock(spec=OAuthCallbackServer)
    mock_server.redirect_uri = "http://localhost:8099/callback"
    mock_server.get_code.return_value = "auth-code-123"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

    use_case = _make_use_case(tmp_path, oauth_server=mock_server)
    with pytest.raises(RuntimeError, match="Token exchange failed"):
        use_case.complete_auth(timeout=5)


def test_exchange_code_invalid_expires(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """complete_auth should raise when expires_in is not numeric."""
    mock_server = MagicMock(spec=OAuthCallbackServer)
    mock_server.redirect_uri = "http://localhost:8099/callback"
    mock_server.get_code.return_value = "auth-code-123"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new-token",
        "expires_in": "not-a-number",
    }
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: mock_response)

    use_case = _make_use_case(tmp_path, oauth_server=mock_server)
    with pytest.raises(RuntimeError, match="Invalid expires_in"):
        use_case.complete_auth(timeout=5)

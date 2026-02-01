"""Use case for authenticating with LinkedIn OAuth2."""

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx

from linkedin_mcp.application.dtos import AuthResult
from linkedin_mcp.domain.repositories.credentials_repository import (
    CredentialsRepository,
)
from linkedin_mcp.domain.services.linkedin_publisher import LinkedInPublisher
from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
from linkedin_mcp.infrastructure.oauth_server import OAuthCallbackServer

_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
_SCOPES = "openid profile w_member_social"
_TIMEOUT = 30.0


class AuthenticateUseCase:
    """Authenticates with LinkedIn via OAuth2 three-legged flow."""

    def __init__(
        self,
        credentials_repository: CredentialsRepository,
        publisher: LinkedInPublisher,
        oauth_server: OAuthCallbackServer,
        client_id: str,
        client_secret: str,
    ) -> None:
        """Initialize with required dependencies.

        Args:
            credentials_repository: Repository for storing credentials.
            publisher: LinkedIn publisher for fetching profile URN.
            oauth_server: Local server for capturing OAuth callback.
            client_id: LinkedIn app client ID.
            client_secret: LinkedIn app client secret.
        """
        self._credentials_repository = credentials_repository
        self._publisher = publisher
        self._oauth_server = oauth_server
        self._client_id = client_id
        self._client_secret = client_secret

    def start_auth(self) -> AuthResult:
        """Start the OAuth2 authentication flow.

        Builds the authorization URL and starts the local callback server
        in the background. Returns immediately so the caller can present
        the URL to the user.

        Returns:
            AuthResult with status="waiting" and the auth_url to visit.
        """
        auth_url = self._build_auth_url()
        self._oauth_server.start()

        return AuthResult(
            status="waiting",
            auth_url=auth_url,
        )

    def complete_auth(self, timeout: float = 120) -> AuthResult:
        """Complete the OAuth2 authentication flow.

        Waits for the callback server to receive the authorization code,
        exchanges it for an access token, fetches the person URN, and
        saves the credentials.

        Args:
            timeout: Seconds to wait for the callback.

        Returns:
            AuthResult with authentication status and details.
        """
        try:
            code = self._oauth_server.get_code(timeout=timeout)
        except (TimeoutError, RuntimeError) as e:
            return AuthResult(status=f"failed: {e}")

        token_data = self._exchange_code(
            code=code,
            redirect_uri=self._oauth_server.redirect_uri,
        )

        access_token = str(token_data["access_token"])
        raw_expires = token_data["expires_in"]
        if not isinstance(raw_expires, (int, float)):
            msg = "Invalid expires_in value in token response"
            raise RuntimeError(msg)
        expires_in = int(raw_expires)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        person_urn = self._publisher.get_profile_urn(access_token)

        credentials = LinkedInCredentials(
            access_token=access_token,
            expires_at=expires_at,
            person_urn=person_urn,
        )
        self._credentials_repository.save(credentials)

        return AuthResult(
            status="authenticated",
            person_urn=person_urn,
            expires_at=expires_at.isoformat(),
        )

    def _build_auth_url(self) -> str:
        """Build the LinkedIn OAuth authorization URL.

        Returns:
            The full authorization URL.
        """
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._oauth_server.redirect_uri,
            "scope": _SCOPES,
            "state": "linkedin_mcp_auth",
        }
        return f"{_AUTH_URL}?{urlencode(params)}"

    def _exchange_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> dict[str, object]:
        """Exchange authorization code for access token.

        Args:
            code: The authorization code from callback.
            redirect_uri: The redirect URI used in authorization.

        Returns:
            Token response data including access_token and expires_in.

        Raises:
            RuntimeError: If token exchange fails.
        """
        response = httpx.post(
            _TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=_TIMEOUT,
        )

        if response.status_code != 200:
            msg = f"Token exchange failed ({response.status_code}): {response.text}"
            raise RuntimeError(msg)

        result: dict[str, object] = response.json()
        return result

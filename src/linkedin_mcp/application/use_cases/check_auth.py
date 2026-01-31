"""Use case for checking LinkedIn authentication status."""

from linkedin_mcp.application.dtos import AuthStatusResult
from linkedin_mcp.domain.repositories.credentials_repository import CredentialsRepository


class CheckAuthUseCase:
    """Checks the current LinkedIn authentication status."""

    def __init__(self, credentials_repository: CredentialsRepository) -> None:
        """Initialize with required dependencies.

        Args:
            credentials_repository: Repository for LinkedIn credentials.
        """
        self._credentials_repository = credentials_repository

    def execute(self) -> AuthStatusResult:
        """Check authentication status.

        Returns:
            AuthStatusResult with current auth state.
        """
        credentials = self._credentials_repository.load()

        if credentials is None:
            return AuthStatusResult(authenticated=False)

        if credentials.is_expired:
            return AuthStatusResult(
                authenticated=False,
                person_urn=credentials.person_urn,
                expires_at=credentials.expires_at.isoformat(),
            )

        return AuthStatusResult(
            authenticated=True,
            person_urn=credentials.person_urn,
            expires_at=credentials.expires_at.isoformat(),
        )

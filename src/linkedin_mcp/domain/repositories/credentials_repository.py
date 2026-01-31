"""Abstract base class for LinkedIn credentials persistence."""

from abc import ABC, abstractmethod

from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials


class CredentialsRepository(ABC):
    """Interface for LinkedIn OAuth credentials storage."""

    @abstractmethod
    def load(self) -> LinkedInCredentials | None:
        """Load stored credentials, returning None if none exist."""

    @abstractmethod
    def save(self, credentials: LinkedInCredentials) -> None:
        """Persist LinkedIn credentials."""

    @abstractmethod
    def delete(self) -> None:
        """Remove stored credentials."""

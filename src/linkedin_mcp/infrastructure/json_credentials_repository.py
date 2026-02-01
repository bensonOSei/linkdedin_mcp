"""JSON file-based implementation of CredentialsRepository."""

import fcntl
import json
from pathlib import Path

from linkedin_mcp.domain.repositories.credentials_repository import (
    CredentialsRepository,
)
from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials

_DEFAULT_STORAGE_DIR = Path.home() / ".linkedin-mcp"
_DEFAULT_CREDENTIALS_FILE = "credentials.json"


class JsonCredentialsRepository(CredentialsRepository):
    """Persists LinkedIn OAuth credentials as JSON in a local file."""

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize the repository.

        Args:
            storage_path: Path to the JSON credentials file.
                Defaults to ~/.linkedin-mcp/credentials.json.
        """
        if storage_path is None:
            storage_path = _DEFAULT_STORAGE_DIR / _DEFAULT_CREDENTIALS_FILE
        self._storage_path = storage_path

    def load(self) -> LinkedInCredentials | None:
        """Load stored credentials.

        Returns:
            The stored credentials or None if no file exists.
        """
        if not self._storage_path.exists():
            return None

        with self._storage_path.open("r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return LinkedInCredentials.model_validate(data)

    def save(self, credentials: LinkedInCredentials) -> None:
        """Persist LinkedIn credentials.

        Args:
            credentials: The credentials to save.
        """
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._storage_path.open("w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(credentials.model_dump(mode="json"), f, indent=2)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def delete(self) -> None:
        """Remove stored credentials."""
        if self._storage_path.exists():
            self._storage_path.unlink()

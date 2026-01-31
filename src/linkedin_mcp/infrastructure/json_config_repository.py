"""JSON file-based implementation of ConfigRepository."""

import fcntl
import json
from pathlib import Path

from linkedin_mcp.domain.entities.user_config import UserConfig
from linkedin_mcp.domain.repositories.config_repository import ConfigRepository

_DEFAULT_STORAGE_DIR = Path.home() / ".linkedin-mcp"
_DEFAULT_CONFIG_FILE = "config.json"


class JsonConfigRepository(ConfigRepository):
    """Persists user configuration as JSON in a local file."""

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize the repository.

        Args:
            storage_path: Path to the JSON config file.
                Defaults to ~/.linkedin-mcp/config.json.
        """
        if storage_path is None:
            storage_path = _DEFAULT_STORAGE_DIR / _DEFAULT_CONFIG_FILE
        self._storage_path = storage_path

    def load(self) -> UserConfig:
        """Load user configuration, returning defaults if none exists.

        Returns:
            The stored UserConfig or a default instance.
        """
        if not self._storage_path.exists():
            return UserConfig()

        with self._storage_path.open("r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return UserConfig.model_validate(data)

    def save(self, config: UserConfig) -> None:
        """Persist user configuration.

        Args:
            config: The configuration to save.
        """
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._storage_path.open("w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(config.model_dump(mode="json"), f, indent=2)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

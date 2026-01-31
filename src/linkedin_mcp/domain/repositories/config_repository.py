"""Abstract base class for user configuration persistence."""

from abc import ABC, abstractmethod

from linkedin_mcp.domain.entities.user_config import UserConfig


class ConfigRepository(ABC):
    """Interface for user configuration storage."""

    @abstractmethod
    def load(self) -> UserConfig:
        """Load user configuration, returning defaults if none exists."""

    @abstractmethod
    def save(self, config: UserConfig) -> None:
        """Persist user configuration."""

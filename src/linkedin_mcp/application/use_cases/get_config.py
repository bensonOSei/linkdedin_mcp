"""Use case for retrieving user configuration."""

from linkedin_mcp.application.dtos import ConfigResult
from linkedin_mcp.domain.repositories.config_repository import ConfigRepository

_VALID_TONES = sorted(["professional", "casual", "inspirational", "educational", "storytelling"])


class GetConfigUseCase:
    """Retrieves the current user configuration."""

    def __init__(self, config_repository: ConfigRepository) -> None:
        """Initialize with required dependencies.

        Args:
            config_repository: Repository for configuration access.
        """
        self._config_repository = config_repository

    def execute(self) -> ConfigResult:
        """Get the current configuration.

        Returns:
            ConfigResult with current settings and valid options.
        """
        config = self._config_repository.load()
        return ConfigResult(
            default_tone=config.default_tone,
            valid_tones=_VALID_TONES,
        )

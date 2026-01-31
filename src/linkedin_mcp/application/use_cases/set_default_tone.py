"""Use case for setting the default post tone."""

from linkedin_mcp.application.dtos import ConfigResult
from linkedin_mcp.domain.repositories.config_repository import ConfigRepository

_VALID_TONES = sorted(["professional", "casual", "inspirational", "educational", "storytelling"])


class SetDefaultToneUseCase:
    """Updates the default tone in user configuration."""

    def __init__(self, config_repository: ConfigRepository) -> None:
        """Initialize with required dependencies.

        Args:
            config_repository: Repository for configuration access.
        """
        self._config_repository = config_repository

    def execute(self, tone: str) -> ConfigResult:
        """Set the default tone.

        Args:
            tone: The new default tone.

        Returns:
            ConfigResult with updated settings.

        Raises:
            ValueError: If tone is not valid.
        """
        config = self._config_repository.load()
        config.set_default_tone(tone)
        self._config_repository.save(config)

        return ConfigResult(
            default_tone=config.default_tone,
            valid_tones=_VALID_TONES,
        )

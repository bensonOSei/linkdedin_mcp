"""User configuration entity."""

from pydantic import BaseModel, Field

_VALID_TONES = frozenset(
    {"professional", "casual", "inspirational", "educational", "storytelling"}
)


class UserConfig(BaseModel):
    """Mutable user configuration with defaults for post creation."""

    default_tone: str = Field(default="professional")

    def set_default_tone(self, tone: str) -> None:
        """Update the default tone.

        Args:
            tone: The new default tone.

        Raises:
            ValueError: If tone is not a valid option.
        """
        if tone.lower() not in _VALID_TONES:
            msg = f"Invalid tone '{tone}'. Valid options: {', '.join(sorted(_VALID_TONES))}."
            raise ValueError(msg)
        self.default_tone = tone.lower()

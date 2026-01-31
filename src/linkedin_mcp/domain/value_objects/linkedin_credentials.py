"""LinkedIn OAuth credentials value object."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict


class LinkedInCredentials(BaseModel):
    """Immutable LinkedIn OAuth2 credentials."""

    model_config = ConfigDict(frozen=True)

    access_token: str
    expires_at: datetime
    person_urn: str

    @property
    def is_expired(self) -> bool:
        """Check if the access token has expired.

        Returns:
            True if the token is expired.
        """
        return datetime.now(timezone.utc) >= self.expires_at

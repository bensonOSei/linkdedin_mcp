"""Publish result value object."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PublishResult(BaseModel):
    """Immutable result of publishing a post to LinkedIn."""

    model_config = ConfigDict(frozen=True)

    linkedin_post_urn: str
    published_at: datetime

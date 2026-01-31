"""Hashtag value object."""

from pydantic import BaseModel, ConfigDict


class Hashtag(BaseModel):
    """Immutable hashtag with category classification."""

    model_config = ConfigDict(frozen=True)

    name: str
    category: str  # industry, trending, niche, broad

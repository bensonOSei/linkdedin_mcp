"""Engagement score value object."""

from pydantic import BaseModel, ConfigDict, Field


class EngagementScore(BaseModel):
    """Immutable engagement score with breakdown and suggestions."""

    model_config = ConfigDict(frozen=True)

    overall: float = Field(ge=0, le=100)
    length_score: float = Field(ge=0, le=100)
    hashtag_score: float = Field(ge=0, le=100)
    readability_score: float = Field(ge=0, le=100)
    hook_score: float = Field(ge=0, le=100)
    cta_score: float = Field(ge=0, le=100)
    suggestions: list[str] = Field(default_factory=list)

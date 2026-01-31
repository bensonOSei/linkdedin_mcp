"""Optimal posting time value object."""

from pydantic import BaseModel, ConfigDict, Field


class OptimalPostingTime(BaseModel):
    """Immutable optimal posting time recommendation."""

    model_config = ConfigDict(frozen=True)

    day: str
    hour: int = Field(ge=0, le=23)
    confidence: float = Field(ge=0, le=1)
    reason: str

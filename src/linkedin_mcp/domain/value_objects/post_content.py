"""Post content value object."""

from pydantic import BaseModel, ConfigDict


class PostContent(BaseModel):
    """Immutable content of a LinkedIn post."""

    model_config = ConfigDict(frozen=True)

    body: str
    hook: str
    call_to_action: str
    tone: str

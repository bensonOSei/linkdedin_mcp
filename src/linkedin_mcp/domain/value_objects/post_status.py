"""Post status enum representing lifecycle stages."""

from enum import Enum


class PostStatus(str, Enum):
    """Status of a LinkedIn post in its lifecycle."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

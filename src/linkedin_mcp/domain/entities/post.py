"""Post aggregate root with state machine."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from linkedin_mcp.domain.value_objects.engagement_score import EngagementScore
from linkedin_mcp.domain.value_objects.hashtag import Hashtag
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.domain.value_objects.post_status import PostStatus


class Post(BaseModel):
    """Aggregate root representing a LinkedIn post with lifecycle state machine."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    content: PostContent
    status: PostStatus = PostStatus.DRAFT
    hashtags: list[Hashtag] = Field(default_factory=list)
    engagement_score: EngagementScore | None = None
    scheduled_time: datetime | None = None
    linkedin_post_urn: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def schedule(self, time: datetime) -> None:
        """Schedule the post for a specific time.

        Args:
            time: The datetime to schedule the post for.

        Raises:
            ValueError: If post is not in DRAFT status.
        """
        if self.status != PostStatus.DRAFT:
            msg = f"Cannot schedule post in '{self.status.value}' status. Must be 'draft'."
            raise ValueError(msg)
        self.status = PostStatus.SCHEDULED
        self.scheduled_time = time
        self.updated_at = datetime.now(timezone.utc)

    def publish(self, linkedin_post_urn: str | None = None) -> None:
        """Publish the post.

        Args:
            linkedin_post_urn: Optional LinkedIn post URN from API response.

        Raises:
            ValueError: If post is already published.
        """
        if self.status == PostStatus.PUBLISHED:
            msg = "Cannot publish post that is already published."
            raise ValueError(msg)
        self.status = PostStatus.PUBLISHED
        if linkedin_post_urn is not None:
            self.linkedin_post_urn = linkedin_post_urn
        self.updated_at = datetime.now(timezone.utc)

    def update_content(self, content: PostContent) -> None:
        """Update the post content.

        Args:
            content: New post content.

        Raises:
            ValueError: If post is already published.
        """
        if self.status == PostStatus.PUBLISHED:
            msg = "Cannot update content of a published post."
            raise ValueError(msg)
        self.content = content
        self.updated_at = datetime.now(timezone.utc)

    def set_engagement_score(self, score: EngagementScore) -> None:
        """Set the engagement score for the post.

        Args:
            score: The computed engagement score.
        """
        self.engagement_score = score
        self.updated_at = datetime.now(timezone.utc)

    def add_hashtags(self, tags: list[Hashtag]) -> None:
        """Add hashtags to the post.

        Args:
            tags: List of hashtags to add.
        """
        self.hashtags = tags
        self.updated_at = datetime.now(timezone.utc)

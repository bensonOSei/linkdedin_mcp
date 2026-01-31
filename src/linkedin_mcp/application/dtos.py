"""Pydantic response models for use case results."""

from pydantic import BaseModel

from linkedin_mcp.domain.value_objects.engagement_score import EngagementScore
from linkedin_mcp.domain.value_objects.hashtag import Hashtag
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.domain.value_objects.post_status import PostStatus
from linkedin_mcp.domain.value_objects.posting_time import OptimalPostingTime


class DraftPostResult(BaseModel):
    """Result of drafting a new post."""

    post_id: str
    topic: str
    content: PostContent
    status: PostStatus


class OptimizePostResult(BaseModel):
    """Result of optimizing a post for engagement."""

    post_id: str
    score: EngagementScore
    content: PostContent


class HashtagSuggestionResult(BaseModel):
    """Result of hashtag suggestion."""

    post_id: str | None = None
    topic: str
    hashtags: list[Hashtag]


class PostingTimeResult(BaseModel):
    """Result of optimal posting time recommendation."""

    recommendations: list[OptimalPostingTime]
    timezone: str
    industry: str


class SchedulePostResult(BaseModel):
    """Result of scheduling a post."""

    post_id: str
    status: PostStatus
    scheduled_time: str


class CalendarEntryResult(BaseModel):
    """A single entry in the content calendar."""

    date: str
    topic: str
    content_type: str
    posting_time: OptimalPostingTime


class CalendarResult(BaseModel):
    """Result of content calendar planning."""

    entries: list[CalendarEntryResult]
    total_posts: int


class PostSummary(BaseModel):
    """Summary of a single post for list views."""

    post_id: str
    topic: str
    status: PostStatus
    hook: str
    created_at: str


class DraftListResult(BaseModel):
    """Result of listing draft posts."""

    drafts: list[PostSummary]
    count: int


class ScheduledPostListResult(BaseModel):
    """Result of listing scheduled posts."""

    scheduled: list[PostSummary]
    count: int


class ConfigResult(BaseModel):
    """Result of getting or setting user configuration."""

    default_tone: str
    valid_tones: list[str]


class AuthResult(BaseModel):
    """Result of LinkedIn authentication."""

    status: str
    person_urn: str | None = None
    expires_at: str | None = None
    auth_url: str | None = None


class PublishPostResult(BaseModel):
    """Result of publishing a post to LinkedIn."""

    post_id: str
    linkedin_post_urn: str
    status: PostStatus
    published_at: str


class AuthStatusResult(BaseModel):
    """Result of checking LinkedIn authentication status."""

    authenticated: bool
    person_urn: str | None = None
    expires_at: str | None = None

"""Tests for the Post aggregate root."""

from datetime import datetime, timezone

import pytest

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.value_objects.engagement_score import EngagementScore
from linkedin_mcp.domain.value_objects.hashtag import Hashtag
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.domain.value_objects.post_status import PostStatus


class TestPostCreation:
    """Tests for post creation and defaults."""

    def test_creates_with_draft_status(self, sample_post: Post) -> None:
        assert sample_post.status == PostStatus.DRAFT

    def test_creates_with_generated_id(self, sample_post: Post) -> None:
        assert sample_post.id is not None
        assert len(sample_post.id) > 0

    def test_creates_with_empty_hashtags(self, sample_post: Post) -> None:
        assert sample_post.hashtags == []

    def test_creates_with_no_engagement_score(self, sample_post: Post) -> None:
        assert sample_post.engagement_score is None


class TestPostScheduling:
    """Tests for post scheduling state transitions."""

    def test_schedule_from_draft(self, sample_post: Post) -> None:
        scheduled_time = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        sample_post.schedule(scheduled_time)
        assert sample_post.status == PostStatus.SCHEDULED
        assert sample_post.scheduled_time == scheduled_time

    def test_schedule_from_scheduled_raises(self, sample_post: Post) -> None:
        sample_post.schedule(datetime.now(timezone.utc))
        with pytest.raises(ValueError, match="Cannot schedule"):
            sample_post.schedule(datetime.now(timezone.utc))

    def test_schedule_from_published_raises(self, sample_post: Post) -> None:
        sample_post.schedule(datetime.now(timezone.utc))
        sample_post.publish()
        with pytest.raises(ValueError, match="Cannot schedule"):
            sample_post.schedule(datetime.now(timezone.utc))


class TestPostPublishing:
    """Tests for post publishing state transitions."""

    def test_publish_from_scheduled(self, sample_post: Post) -> None:
        sample_post.schedule(datetime.now(timezone.utc))
        sample_post.publish()
        assert sample_post.status == PostStatus.PUBLISHED

    def test_publish_from_draft(self, sample_post: Post) -> None:
        sample_post.publish()
        assert sample_post.status == PostStatus.PUBLISHED

    def test_publish_already_published_raises(self, sample_post: Post) -> None:
        sample_post.publish()
        with pytest.raises(ValueError, match="already published"):
            sample_post.publish()


class TestPostContentUpdate:
    """Tests for content update behavior."""

    def test_update_content_on_draft(self, sample_post: Post) -> None:
        new_content = PostContent(
            body="Updated body",
            hook="Updated hook",
            call_to_action="Updated CTA",
            tone="casual",
        )
        sample_post.update_content(new_content)
        assert sample_post.content == new_content

    def test_update_content_on_published_raises(self, sample_post: Post) -> None:
        sample_post.schedule(datetime.now(timezone.utc))
        sample_post.publish()
        with pytest.raises(ValueError, match="Cannot update content"):
            sample_post.update_content(sample_post.content)


class TestPostHashtags:
    """Tests for hashtag management."""

    def test_add_hashtags(self, sample_post: Post) -> None:
        tags = [
            Hashtag(name="#Python", category="industry"),
            Hashtag(name="#Coding", category="broad"),
        ]
        sample_post.add_hashtags(tags)
        assert len(sample_post.hashtags) == 2

    def test_set_engagement_score(self, sample_post: Post) -> None:
        score = EngagementScore(
            overall=75.0,
            length_score=80.0,
            hashtag_score=60.0,
            readability_score=85.0,
            hook_score=70.0,
            cta_score=75.0,
            suggestions=["Add more hashtags"],
        )
        sample_post.set_engagement_score(score)
        assert sample_post.engagement_score is not None
        assert sample_post.engagement_score.overall == 75.0

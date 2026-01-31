"""Tests for the ContentOptimizer domain service."""

from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer
from linkedin_mcp.domain.value_objects.post_content import PostContent


class TestContentOptimizer:
    """Tests for engagement scoring."""

    def setup_method(self) -> None:
        self.optimizer = ContentOptimizer()

    def test_score_returns_engagement_score(self) -> None:
        content = PostContent(
            body="A" * 1200,
            hook="Here's what I've learned about testing:",
            call_to_action="What's your experience? Share in the comments.",
            tone="professional",
        )
        score = self.optimizer.score(content, hashtag_count=3)
        assert 0 <= score.overall <= 100
        assert 0 <= score.length_score <= 100

    def test_short_post_gets_low_length_score(self) -> None:
        content = PostContent(
            body="Short post",
            hook="Hook",
            call_to_action="CTA",
            tone="professional",
        )
        score = self.optimizer.score(content)
        assert score.length_score < 50

    def test_ideal_length_gets_max_score(self) -> None:
        content = PostContent(
            body="A" * 1200,
            hook="Hook",
            call_to_action="CTA",
            tone="professional",
        )
        score = self.optimizer.score(content)
        assert score.length_score == 100.0

    def test_no_hashtags_gets_low_score(self) -> None:
        content = PostContent(
            body="A" * 1200,
            hook="Hook",
            call_to_action="CTA",
            tone="professional",
        )
        score = self.optimizer.score(content, hashtag_count=0)
        assert score.hashtag_score < 50

    def test_optimal_hashtags_gets_max_score(self) -> None:
        content = PostContent(
            body="A" * 1200,
            hook="Hook",
            call_to_action="CTA",
            tone="professional",
        )
        score = self.optimizer.score(content, hashtag_count=4)
        assert score.hashtag_score == 100.0

    def test_good_hook_scores_higher(self) -> None:
        good_hook = PostContent(
            body="Body",
            hook="Most people never learn this secret about testing:",
            call_to_action="CTA",
            tone="professional",
        )
        bad_hook = PostContent(
            body="Body",
            hook="Hi",
            call_to_action="CTA",
            tone="professional",
        )
        good_score = self.optimizer.score(good_hook)
        bad_score = self.optimizer.score(bad_hook)
        assert good_score.hook_score > bad_score.hook_score

    def test_suggestions_provided_for_improvements(self) -> None:
        content = PostContent(
            body="Short",
            hook="",
            call_to_action="",
            tone="professional",
        )
        score = self.optimizer.score(content)
        assert len(score.suggestions) > 0

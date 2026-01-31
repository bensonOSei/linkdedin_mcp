"""Service for scoring LinkedIn posts for engagement potential."""

import re

from linkedin_mcp.domain.value_objects.engagement_score import EngagementScore
from linkedin_mcp.domain.value_objects.post_content import PostContent

_IDEAL_MIN_LENGTH = 1000
_IDEAL_MAX_LENGTH = 1500
_IDEAL_HASHTAG_COUNT = 4
_MAX_HASHTAG_COUNT = 5


class ContentOptimizer:
    """Scores a LinkedIn post across engagement dimensions.

    Evaluates length, hashtags, readability, hook quality, and CTA presence.
    Returns an EngagementScore with improvement suggestions.
    """

    def score(self, content: PostContent, hashtag_count: int = 0) -> EngagementScore:
        """Score a post for engagement potential.

        Args:
            content: The post content to evaluate.
            hashtag_count: Number of hashtags attached to the post.

        Returns:
            An EngagementScore with overall score and breakdown.
        """
        suggestions: list[str] = []

        length_score = self._score_length(content.body, suggestions)
        hashtag_score = self._score_hashtags(hashtag_count, suggestions)
        readability_score = self._score_readability(content.body, suggestions)
        hook_score = self._score_hook(content.hook, suggestions)
        cta_score = self._score_cta(content.call_to_action, suggestions)

        overall = (
            length_score * 0.20
            + hashtag_score * 0.15
            + readability_score * 0.25
            + hook_score * 0.25
            + cta_score * 0.15
        )

        return EngagementScore(
            overall=round(overall, 1),
            length_score=round(length_score, 1),
            hashtag_score=round(hashtag_score, 1),
            readability_score=round(readability_score, 1),
            hook_score=round(hook_score, 1),
            cta_score=round(cta_score, 1),
            suggestions=suggestions,
        )

    def _score_length(self, body: str, suggestions: list[str]) -> float:
        """Score based on post length."""
        length = len(body)
        if _IDEAL_MIN_LENGTH <= length <= _IDEAL_MAX_LENGTH:
            return 100.0
        if length < 200:
            suggestions.append("Post is too short. Aim for 1000-1500 characters.")
            return 20.0
        if length < _IDEAL_MIN_LENGTH:
            suggestions.append(
                f"Post is {_IDEAL_MIN_LENGTH - length} characters short of ideal length."
            )
            return 50.0 + (length / _IDEAL_MIN_LENGTH) * 40.0
        if length > 3000:
            suggestions.append("Post is very long. Consider trimming to under 1500 characters.")
            return 40.0
        suggestions.append("Post is slightly long. Ideal length is 1000-1500 characters.")
        return 70.0

    def _score_hashtags(self, count: int, suggestions: list[str]) -> float:
        """Score based on hashtag count."""
        if 3 <= count <= _IDEAL_HASHTAG_COUNT:
            return 100.0
        if count == 0:
            suggestions.append("Add 3-4 relevant hashtags to increase discoverability.")
            return 20.0
        if count < 3:
            suggestions.append(f"Add {3 - count} more hashtag(s). Aim for 3-4 total.")
            return 60.0
        if count > _MAX_HASHTAG_COUNT:
            suggestions.append("Too many hashtags. LinkedIn recommends 3-5 maximum.")
            return 50.0
        return 80.0

    def _score_readability(self, body: str, suggestions: list[str]) -> float:
        """Score based on readability (short paragraphs, line breaks)."""
        lines = body.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        blank_line_count = body.count("\n\n")

        score = 60.0

        if blank_line_count >= 3:
            score += 20.0
        else:
            suggestions.append("Add more line breaks between paragraphs for better readability.")

        long_paragraphs = [line for line in non_empty_lines if len(line) > 200]
        if not long_paragraphs:
            score += 20.0
        else:
            suggestions.append("Break up long paragraphs. Keep each under 200 characters.")

        has_list = any(re.match(r"^\s*[\d•\-\*]", line) for line in non_empty_lines)
        if has_list:
            score += 10.0

        return min(score, 100.0)

    def _score_hook(self, hook: str, suggestions: list[str]) -> float:
        """Score based on hook quality."""
        if not hook:
            suggestions.append("Add a compelling opening hook to grab attention.")
            return 0.0

        score = 50.0

        if len(hook) >= 20:
            score += 15.0
        else:
            suggestions.append("Make your hook longer and more compelling.")

        if len(hook) <= 150:
            score += 10.0

        power_words = ["learn", "discover", "secret", "mistake", "never", "always", "most", "why"]
        if any(word in hook.lower() for word in power_words):
            score += 15.0

        if hook.endswith((":", "?")):
            score += 10.0
        else:
            suggestions.append("End your hook with ':' or '?' to create curiosity.")

        return min(score, 100.0)

    def _score_cta(self, cta: str, suggestions: list[str]) -> float:
        """Score based on call to action quality."""
        if not cta:
            suggestions.append("Add a call to action to drive engagement.")
            return 0.0

        score = 50.0

        action_words = ["share", "comment", "follow", "save", "like", "tell", "drop", "thoughts"]
        if any(word in cta.lower() for word in action_words):
            score += 30.0
        else:
            suggestions.append("Include an action word in your CTA (share, comment, follow).")

        if "?" in cta:
            score += 20.0
        else:
            suggestions.append("Ask a question in your CTA to encourage responses.")

        return min(score, 100.0)

"""Tests for the ContentOptimizer domain service."""

from linkedin_mcp.domain.services.content_optimizer import ContentOptimizer
from linkedin_mcp.domain.value_objects.post_content import PostContent


def test_score_returns_engagement_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 1200,
        hook="Here's what I've learned about testing:",
        call_to_action="What's your experience? Share in the comments.",
        tone="professional",
    )
    score = optimizer.score(content, hashtag_count=3)
    assert 0 <= score.overall <= 100
    assert 0 <= score.length_score <= 100


def test_short_post_gets_low_length_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Short post",
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.length_score < 50


def test_ideal_length_gets_max_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 1200,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.length_score == 100.0


def test_no_hashtags_gets_low_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 1200,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content, hashtag_count=0)
    assert score.hashtag_score < 50


def test_optimal_hashtags_gets_max_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 1200,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content, hashtag_count=4)
    assert score.hashtag_score == 100.0


def test_good_hook_scores_higher(optimizer: ContentOptimizer) -> None:
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
    good_score = optimizer.score(good_hook)
    bad_score = optimizer.score(bad_hook)
    assert good_score.hook_score > bad_score.hook_score


def test_suggestions_provided_for_improvements(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Short",
        hook="",
        call_to_action="",
        tone="professional",
    )
    score = optimizer.score(content)
    assert len(score.suggestions) > 0


def test_very_long_post_gets_low_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 3500,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.length_score < 50


def test_slightly_long_post_gets_medium_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 2000,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert 50 < score.length_score < 100


def test_post_near_ideal_length_gets_high_score(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 800,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.length_score > 70


def test_hashtag_count_scoring_edge_cases(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="A" * 1200,
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    # Test with 1 hashtag
    score = optimizer.score(content, hashtag_count=1)
    assert score.hashtag_score < 100

    # Test with 2 hashtags
    score = optimizer.score(content, hashtag_count=2)
    assert score.hashtag_score < 100

    # Test with 3 hashtags (optimal)
    score = optimizer.score(content, hashtag_count=3)
    assert score.hashtag_score == 100.0

    # Test with 5 hashtags (max)
    score = optimizer.score(content, hashtag_count=5)
    assert score.hashtag_score == 80.0

    # Test with too many hashtags
    score = optimizer.score(content, hashtag_count=10)
    assert score.hashtag_score < 80


def test_readability_with_line_breaks(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Paragraph 1\n\nParagraph 2\n\nParagraph 3\n\nParagraph 4",
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.readability_score > 70


def test_readability_with_bullet_lists(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Here are tips:\n\n• Point 1\n• Point 2\n• Point 3",
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.readability_score > 70


def test_readability_with_numbered_lists(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Key insights:\n\n1. First insight\n2. Second insight\n3. Third insight",
        hook="Hook",
        call_to_action="CTA",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.readability_score > 70


def test_hook_with_power_words(optimizer: ContentOptimizer) -> None:
    power_hooks = [
        "Learn this secret about testing:",
        "Discover why most people fail:",
        "The mistake everyone makes with AI:",
        "Most leaders never understand this:",
    ]
    for hook in power_hooks:
        content = PostContent(
            body="Body",
            hook=hook,
            call_to_action="CTA",
            tone="professional",
        )
        score = optimizer.score(content)
        assert score.hook_score > 70


def test_hook_ending_with_colon_or_question(optimizer: ContentOptimizer) -> None:
    hook_with_colon = PostContent(
        body="Body",
        hook="Here's what I learned about testing:",
        call_to_action="CTA",
        tone="professional",
    )
    hook_with_question = PostContent(
        body="Body",
        hook="What if I told you about testing?",
        call_to_action="CTA",
        tone="professional",
    )
    score_colon = optimizer.score(hook_with_colon)
    score_question = optimizer.score(hook_with_question)
    assert score_colon.hook_score > 60
    assert score_question.hook_score > 60


def test_cta_with_action_words(optimizer: ContentOptimizer) -> None:
    action_ctas = [
        "Share your thoughts in the comments",
        "Comment below with your experience",
        "Follow for more insights",
        "Save this for later",
        "Like if you agree",
        "Tell me what you think",
        "Drop your thoughts below",
    ]
    for cta in action_ctas:
        content = PostContent(
            body="Body",
            hook="Hook",
            call_to_action=cta,
            tone="professional",
        )
        score = optimizer.score(content)
        assert score.cta_score > 50


def test_cta_with_question_mark(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Body",
        hook="Hook",
        call_to_action="What's your experience with this?",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.cta_score >= 70


def test_overall_score_calculation(optimizer: ContentOptimizer) -> None:
    # Perfect post
    perfect = PostContent(
        body="A" * 1200 + "\n\n" + "B" * 100 + "\n\n" + "C" * 100,
        hook="Learn this secret about AI:",
        call_to_action="Share your thoughts?",
        tone="professional",
    )
    score = optimizer.score(perfect, hashtag_count=4)
    assert score.overall > 80


def test_empty_hook_and_cta(optimizer: ContentOptimizer) -> None:
    content = PostContent(
        body="Just body text",
        hook="",
        call_to_action="",
        tone="professional",
    )
    score = optimizer.score(content)
    assert score.hook_score == 0
    assert score.cta_score == 0
    assert score.overall < 50

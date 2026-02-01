"""Tests for the PostDrafter domain service."""

from linkedin_mcp.domain.services.post_drafter import PostDrafter


def test_draft_returns_post_content(drafter: PostDrafter) -> None:
    content = drafter.draft("AI in business")
    assert content.body is not None
    assert len(content.body) > 0


def test_draft_includes_hook(drafter: PostDrafter) -> None:
    content = drafter.draft("AI in business")
    assert "AI in business" in content.hook


def test_draft_includes_cta(drafter: PostDrafter) -> None:
    content = drafter.draft("AI in business")
    assert len(content.call_to_action) > 0


def test_draft_with_professional_tone(drafter: PostDrafter) -> None:
    content = drafter.draft("testing", tone="professional")
    assert content.tone == "professional"
    assert "learned" in content.hook.lower()


def test_draft_with_casual_tone(drafter: PostDrafter) -> None:
    content = drafter.draft("testing", tone="casual")
    assert content.tone == "casual"


def test_draft_with_educational_tone(drafter: PostDrafter) -> None:
    content = drafter.draft("testing", tone="educational")
    assert content.tone == "educational"
    assert "break down" in content.body.lower() or "wrong" in content.hook.lower()


def test_draft_with_unknown_tone_defaults(drafter: PostDrafter) -> None:
    content = drafter.draft("testing", tone="unknown_tone")
    assert content.tone == "unknown_tone"
    assert "learned" in content.hook.lower()


def test_draft_body_contains_hook_and_cta(drafter: PostDrafter) -> None:
    content = drafter.draft("leadership")
    assert content.hook in content.body
    assert content.call_to_action in content.body


def test_draft_with_inspirational_tone(drafter: PostDrafter) -> None:
    content = drafter.draft("success", tone="inspirational")
    assert content.tone == "inspirational"
    assert "powerful" in content.hook.lower() or "lesson" in content.hook.lower()


def test_draft_with_storytelling_tone(drafter: PostDrafter) -> None:
    content = drafter.draft("career", tone="storytelling")
    assert content.tone == "storytelling"
    assert "never expected" in content.hook.lower() or "started" in content.hook.lower()
    assert "journey" in content.body.lower() or "story" in content.cta.lower()


def test_draft_body_has_proper_structure(drafter: PostDrafter) -> None:
    content = drafter.draft("testing")
    # Should have multiple paragraphs
    assert "\n\n" in content.body
    # Should have numbered points
    assert "1." in content.body
    assert "2." in content.body
    assert "3." in content.body


def test_draft_includes_topic_in_body(drafter: PostDrafter) -> None:
    topic = "artificial intelligence"
    content = drafter.draft(topic)
    # Topic should appear in body (case-insensitive)
    assert topic in content.body.lower()


def test_draft_different_topics_produce_different_content(drafter: PostDrafter) -> None:
    content1 = drafter.draft("AI")
    content2 = drafter.draft("Leadership")
    assert content1.body != content2.body
    assert "AI" in content1.hook
    assert "Leadership" in content2.hook


def test_educational_tone_includes_break_down(drafter: PostDrafter) -> None:
    content = drafter.draft("coding", tone="educational")
    assert "break down" in content.body.lower() or "wrong" in content.hook.lower()


def test_casual_tone_has_informal_cta(drafter: PostDrafter) -> None:
    content = drafter.draft("work", tone="casual")
    # Casual CTA should have emoji or informal language
    assert "\U0001f447" in content.call_to_action or "drop" in content.call_to_action.lower()


def test_draft_body_length_reasonable(drafter: PostDrafter) -> None:
    content = drafter.draft("productivity")
    # Body should be substantial but not too long
    assert 300 < len(content.body) < 2000

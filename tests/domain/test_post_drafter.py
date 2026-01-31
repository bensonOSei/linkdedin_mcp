"""Tests for the PostDrafter domain service."""

from linkedin_mcp.domain.services.post_drafter import PostDrafter


class TestPostDrafter:
    """Tests for post draft generation."""

    def setup_method(self) -> None:
        self.drafter = PostDrafter()

    def test_draft_returns_post_content(self) -> None:
        content = self.drafter.draft("AI in business")
        assert content.body is not None
        assert len(content.body) > 0

    def test_draft_includes_hook(self) -> None:
        content = self.drafter.draft("AI in business")
        assert "AI in business" in content.hook

    def test_draft_includes_cta(self) -> None:
        content = self.drafter.draft("AI in business")
        assert len(content.call_to_action) > 0

    def test_draft_with_professional_tone(self) -> None:
        content = self.drafter.draft("testing", tone="professional")
        assert content.tone == "professional"
        assert "learned" in content.hook.lower()

    def test_draft_with_casual_tone(self) -> None:
        content = self.drafter.draft("testing", tone="casual")
        assert content.tone == "casual"

    def test_draft_with_educational_tone(self) -> None:
        content = self.drafter.draft("testing", tone="educational")
        assert content.tone == "educational"
        assert "break down" in content.body.lower() or "wrong" in content.hook.lower()

    def test_draft_with_unknown_tone_defaults(self) -> None:
        content = self.drafter.draft("testing", tone="unknown_tone")
        assert content.tone == "unknown_tone"
        assert "learned" in content.hook.lower()

    def test_draft_body_contains_hook_and_cta(self) -> None:
        content = self.drafter.draft("leadership")
        assert content.hook in content.body
        assert content.call_to_action in content.body

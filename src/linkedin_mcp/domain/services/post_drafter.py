"""Service for generating structured LinkedIn post drafts."""

from linkedin_mcp.domain.value_objects.post_content import PostContent

_TONE_TEMPLATES: dict[str, dict[str, str]] = {
    "professional": {
        "hook_prefix": "Here's what I've learned about",
        "cta": "What's your experience with this? Share in the comments.",
    },
    "casual": {
        "hook_prefix": "Let me tell you something about",
        "cta": "Thoughts? Drop them below 👇",
    },
    "inspirational": {
        "hook_prefix": "The most powerful lesson I've learned about",
        "cta": "If this resonates, share it with someone who needs to hear it.",
    },
    "educational": {
        "hook_prefix": "Most people get this wrong about",
        "cta": "Save this for later and follow for more insights.",
    },
    "storytelling": {
        "hook_prefix": "I never expected this when I started with",
        "cta": "Have a similar story? I'd love to hear it.",
    },
}

_DEFAULT_TONE = "professional"


class PostDrafter:
    """Generates structured LinkedIn post content from a topic and tone.

    Applies LinkedIn best practices: 1000-1500 chars, strong hook,
    short paragraphs, and a clear call to action.
    """

    def draft(self, topic: str, tone: str = _DEFAULT_TONE) -> PostContent:
        """Generate a structured post draft.

        Args:
            topic: The subject matter of the post.
            tone: Writing tone (professional, casual, inspirational, educational, storytelling).

        Returns:
            A PostContent value object with the generated draft.
        """
        tone_lower = tone.lower()
        template = _TONE_TEMPLATES.get(tone_lower, _TONE_TEMPLATES[_DEFAULT_TONE])

        hook = f"{template['hook_prefix']} {topic}:"
        cta = template["cta"]

        body = self._build_body(topic, tone_lower, hook, cta)

        return PostContent(
            body=body,
            hook=hook,
            call_to_action=cta,
            tone=tone_lower,
        )

    def _build_body(self, topic: str, tone: str, hook: str, cta: str) -> str:
        """Build the full post body with LinkedIn best practices.

        Args:
            topic: The subject matter.
            tone: The writing tone.
            hook: The opening hook line.
            cta: The call to action.

        Returns:
            Formatted post body string.
        """
        paragraphs = [
            hook,
            "",
            f"When it comes to {topic}, there are key insights that can transform your approach.",
            "",
            "Here's what matters most:",
            "",
            f"1. Understanding the fundamentals of {topic} is essential.",
            f"2. Applying {topic} consistently leads to measurable results.",
            f"3. The best practitioners of {topic} never stop learning.",
            "",
        ]

        if tone == "storytelling":
            paragraphs.insert(2, f"My journey with {topic} started unexpectedly.")
            paragraphs.insert(3, "")
        elif tone == "educational":
            paragraphs.insert(2, f"Let me break down {topic} into actionable steps.")
            paragraphs.insert(3, "")

        paragraphs.append(cta)

        return "\n".join(paragraphs)

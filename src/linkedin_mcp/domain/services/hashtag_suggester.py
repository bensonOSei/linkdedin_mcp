"""Service for curating hashtag recommendations."""

from linkedin_mcp.domain.value_objects.hashtag import Hashtag

_INDUSTRY_HASHTAGS: dict[str, list[str]] = {
    "technology": ["Technology", "Tech", "Innovation", "Digital", "Software"],
    "marketing": ["Marketing", "DigitalMarketing", "ContentMarketing", "Branding", "SEO"],
    "leadership": ["Leadership", "Management", "ExecutiveLeadership", "LeadershipDevelopment"],
    "career": ["CareerDevelopment", "CareerGrowth", "JobSearch", "ProfessionalDevelopment"],
    "startup": ["Startup", "Entrepreneurship", "StartupLife", "VentureCapital", "Founders"],
    "ai": ["ArtificialIntelligence", "MachineLearning", "AI", "DeepLearning", "GenerativeAI"],
    "finance": ["Finance", "FinTech", "Investment", "Banking", "FinancialServices"],
    "healthcare": ["Healthcare", "HealthTech", "DigitalHealth", "MedTech"],
    "default": ["Business", "Innovation", "Growth", "Strategy", "ProfessionalDevelopment"],
}

_TRENDING_HASHTAGS: list[str] = [
    "FutureOfWork",
    "RemoteWork",
    "AIInBusiness",
    "Sustainability",
    "DEI",
    "PersonalBranding",
    "ThoughtLeadership",
    "WorkLifeBalance",
]

_NICHE_SUFFIXES: list[str] = ["Tips", "Insights", "Trends", "Strategy", "Community"]

_BROAD_HASHTAGS: list[str] = [
    "LinkedIn",
    "Networking",
    "Success",
    "Motivation",
    "Learning",
]


class HashtagSuggester:
    """Curates hashtag recommendations by category.

    Returns a balanced mix of industry, trending, niche, and broad hashtags.
    Enforces 3-4 hashtag recommendation per category.
    """

    def suggest(self, topic: str, industry: str = "default") -> list[Hashtag]:
        """Suggest hashtags for a post topic.

        Args:
            topic: The post topic to generate hashtags for.
            industry: Industry vertical for targeted suggestions.

        Returns:
            List of 3-4 categorized hashtag recommendations.
        """
        hashtags: list[Hashtag] = []

        hashtags.append(self._get_industry_hashtag(industry))
        hashtags.append(self._get_trending_hashtag(topic))
        hashtags.append(self._get_niche_hashtag(topic))
        hashtags.append(self._get_broad_hashtag())

        return hashtags

    def _get_industry_hashtag(self, industry: str) -> Hashtag:
        """Get a relevant industry hashtag."""
        industry_lower = industry.lower()
        tags = _INDUSTRY_HASHTAGS.get(industry_lower, _INDUSTRY_HASHTAGS["default"])
        return Hashtag(name=f"#{tags[0]}", category="industry")

    def _get_trending_hashtag(self, topic: str) -> Hashtag:
        """Get a trending hashtag related to topic."""
        topic_lower = topic.lower()
        for tag in _TRENDING_HASHTAGS:
            if any(word in topic_lower for word in tag.lower().split()):
                return Hashtag(name=f"#{tag}", category="trending")
        return Hashtag(name=f"#{_TRENDING_HASHTAGS[0]}", category="trending")

    def _get_niche_hashtag(self, topic: str) -> Hashtag:
        """Generate a niche hashtag from the topic."""
        clean_topic = topic.replace(" ", "")[:20]
        suffix = _NICHE_SUFFIXES[len(topic) % len(_NICHE_SUFFIXES)]
        return Hashtag(name=f"#{clean_topic}{suffix}", category="niche")

    def _get_broad_hashtag(self) -> Hashtag:
        """Get a broad reach hashtag."""
        return Hashtag(name=f"#{_BROAD_HASHTAGS[0]}", category="broad")

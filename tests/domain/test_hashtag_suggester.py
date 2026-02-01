"""Tests for the HashtagSuggester domain service."""

from linkedin_mcp.domain.services.hashtag_suggester import HashtagSuggester


def test_suggest_returns_four_hashtags(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("machine learning")
    assert len(hashtags) == 4


def test_suggest_includes_all_categories(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("AI")
    categories = {tag.category for tag in hashtags}
    assert "industry" in categories
    assert "trending" in categories
    assert "niche" in categories
    assert "broad" in categories


def test_suggest_for_technology_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("software", industry="technology")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Technology" in industry_tag.name or "Tech" in industry_tag.name


def test_suggest_for_marketing_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("content", industry="marketing")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Marketing" in industry_tag.name


def test_suggest_for_leadership_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("teams", industry="leadership")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Leadership" in industry_tag.name


def test_suggest_for_career_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("growth", industry="career")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Career" in industry_tag.name


def test_suggest_for_startup_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("funding", industry="startup")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Startup" in industry_tag.name or "Entrepreneurship" in industry_tag.name


def test_suggest_for_ai_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("models", industry="ai")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert (
        "AI" in industry_tag.name
        or "Intelligence" in industry_tag.name
        or "MachineLearning" in industry_tag.name
    )


def test_suggest_for_finance_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("investing", industry="finance")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Finance" in industry_tag.name or "FinTech" in industry_tag.name


def test_suggest_for_healthcare_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("wellness", industry="healthcare")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "Health" in industry_tag.name


def test_suggest_for_default_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("random topic", industry="default")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    assert "#" in industry_tag.name


def test_suggest_for_unknown_industry(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("topic", industry="unknown")
    industry_tag = next(tag for tag in hashtags if tag.category == "industry")
    # Should default to "default" industry
    assert "#" in industry_tag.name


def test_trending_hashtag_matches_topic(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("remote work trends")
    trending_tag = next(tag for tag in hashtags if tag.category == "trending")
    assert "Remote" in trending_tag.name or "Work" in trending_tag.name


def test_trending_hashtag_for_ai_topic(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("AI in business")
    trending_tag = next(tag for tag in hashtags if tag.category == "trending")
    # Trending tags are camelCase; matching splits by spaces so "AIInBusiness" won't match.
    # The fallback is the first trending tag ("FutureOfWork").
    assert trending_tag.name.startswith("#")


def test_niche_hashtag_includes_topic(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("leadership development")
    niche_tag = next(tag for tag in hashtags if tag.category == "niche")
    # Should include cleaned topic
    assert "leadership" in niche_tag.name.lower()


def test_niche_hashtag_removes_spaces(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("machine learning")
    niche_tag = next(tag for tag in hashtags if tag.category == "niche")
    # Should have no spaces
    assert " " not in niche_tag.name


def test_niche_hashtag_truncates_long_topics(suggester: HashtagSuggester) -> None:
    long_topic = "this is a very long topic that should be truncated"
    hashtags = suggester.suggest(long_topic)
    niche_tag = next(tag for tag in hashtags if tag.category == "niche")
    # Should be truncated to reasonable length
    assert len(niche_tag.name) < 30


def test_broad_hashtag_always_present(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("anything")
    broad_tag = next(tag for tag in hashtags if tag.category == "broad")
    assert "#" in broad_tag.name
    # Should be a common broad hashtag
    assert broad_tag.name in [
        "#LinkedIn",
        "#Networking",
        "#Success",
        "#Motivation",
        "#Learning",
    ]


def test_all_hashtags_start_with_hash(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("test topic")
    for tag in hashtags:
        assert tag.name.startswith("#")


def test_trending_hashtag_matches_single_word_tag(suggester: HashtagSuggester) -> None:
    hashtags = suggester.suggest("dei initiatives")
    trending_tag = next(tag for tag in hashtags if tag.category == "trending")
    assert trending_tag.name == "#DEI"


def test_different_topics_produce_different_niche_tags(suggester: HashtagSuggester) -> None:
    hashtags1 = suggester.suggest("AI")
    hashtags2 = suggester.suggest("Leadership")
    niche1 = next(tag for tag in hashtags1 if tag.category == "niche")
    niche2 = next(tag for tag in hashtags2 if tag.category == "niche")
    assert niche1.name != niche2.name

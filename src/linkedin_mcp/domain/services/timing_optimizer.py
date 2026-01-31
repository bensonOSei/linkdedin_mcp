"""Service for computing optimal LinkedIn posting times."""

from typing import TypedDict

from linkedin_mcp.domain.value_objects.posting_time import OptimalPostingTime


class _SlotData(TypedDict):
    day: str
    hour: int
    confidence: float
    reason: str


_OPTIMAL_SLOTS: list[_SlotData] = [
    {
        "day": "Tuesday",
        "hour": 9,
        "confidence": 0.92,
        "reason": "Peak LinkedIn activity: professionals check feeds after morning meetings.",
    },
    {
        "day": "Wednesday",
        "hour": 10,
        "confidence": 0.90,
        "reason": "Mid-week engagement peak: highest comment and share rates.",
    },
    {
        "day": "Thursday",
        "hour": 12,
        "confidence": 0.88,
        "reason": "Lunch break browsing: strong engagement during midday pause.",
    },
    {
        "day": "Tuesday",
        "hour": 13,
        "confidence": 0.85,
        "reason": "Early afternoon: decision-makers active before end-of-day wrap-up.",
    },
    {
        "day": "Wednesday",
        "hour": 9,
        "confidence": 0.84,
        "reason": "Morning professional browsing window on LinkedIn's busiest day.",
    },
    {
        "day": "Thursday",
        "hour": 10,
        "confidence": 0.82,
        "reason": "Pre-weekend planning: professionals seek insights for the week ahead.",
    },
]

_INDUSTRY_ADJUSTMENTS: dict[str, int] = {
    "technology": 0,
    "finance": -1,
    "healthcare": 1,
    "marketing": 0,
    "startup": 1,
    "default": 0,
}


class TimingOptimizer:
    """Recommends optimal LinkedIn posting slots.

    Based on LinkedIn algorithm research indicating Tue-Thu, 9-10AM and 12-2PM
    as peak engagement windows. Adjusts by timezone and industry.
    """

    def recommend(
        self,
        timezone: str = "UTC",
        industry: str = "default",
        count: int = 3,
    ) -> list[OptimalPostingTime]:
        """Recommend top posting time slots.

        Args:
            timezone: User's timezone (for display context).
            industry: Industry vertical for adjustments.
            count: Number of recommendations to return (default 3).

        Returns:
            List of optimal posting time recommendations, sorted by confidence.
        """
        industry_lower = industry.lower()
        hour_adjustment = _INDUSTRY_ADJUSTMENTS.get(
            industry_lower,
            _INDUSTRY_ADJUSTMENTS["default"],
        )

        recommendations: list[OptimalPostingTime] = []
        for slot in _OPTIMAL_SLOTS[:count]:
            adjusted_hour = max(0, min(23, slot["hour"] + hour_adjustment))
            recommendations.append(
                OptimalPostingTime(
                    day=slot["day"],
                    hour=adjusted_hour,
                    confidence=slot["confidence"],
                    reason=f"{slot['reason']} (Timezone: {timezone})",
                )
            )

        return recommendations

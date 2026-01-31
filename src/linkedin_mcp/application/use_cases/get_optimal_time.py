"""Use case for getting optimal posting times."""

from linkedin_mcp.application.dtos import PostingTimeResult
from linkedin_mcp.domain.services.timing_optimizer import TimingOptimizer


class GetOptimalTimeUseCase:
    """Recommends optimal posting times for LinkedIn."""

    def __init__(self, optimizer: TimingOptimizer) -> None:
        """Initialize with required dependencies.

        Args:
            optimizer: Service for computing posting times.
        """
        self._optimizer = optimizer

    def execute(
        self,
        timezone: str = "UTC",
        industry: str = "default",
    ) -> PostingTimeResult:
        """Get optimal posting time recommendations.

        Args:
            timezone: User's timezone.
            industry: Industry vertical for adjustments.

        Returns:
            PostingTimeResult with top recommendations.
        """
        recommendations = self._optimizer.recommend(timezone=timezone, industry=industry)

        return PostingTimeResult(
            recommendations=recommendations,
            timezone=timezone,
            industry=industry,
        )

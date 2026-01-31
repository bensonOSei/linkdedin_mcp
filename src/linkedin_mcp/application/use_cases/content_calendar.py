"""Use case for planning a content calendar."""

from datetime import datetime

from linkedin_mcp.application.dtos import CalendarEntryResult, CalendarResult
from linkedin_mcp.domain.services.calendar_planner import CalendarPlanner


class ContentCalendarUseCase:
    """Plans a multi-day content calendar for LinkedIn."""

    def __init__(self, planner: CalendarPlanner) -> None:
        """Initialize with required dependencies.

        Args:
            planner: Service for calendar planning.
        """
        self._planner = planner

    def execute(
        self,
        topics: list[str],
        start_date: datetime | None = None,
        posts_per_week: int = 3,
    ) -> CalendarResult:
        """Plan a content calendar.

        Args:
            topics: List of topics to schedule.
            start_date: Starting date for the calendar.
            posts_per_week: Target posts per week.

        Returns:
            CalendarResult with planned entries.
        """
        entries = self._planner.plan(
            topics=topics,
            start_date=start_date,
            posts_per_week=posts_per_week,
        )

        entry_results = [
            CalendarEntryResult(
                date=entry.date.isoformat(),
                topic=entry.topic,
                content_type=entry.content_type,
                posting_time=entry.posting_time,
            )
            for entry in entries
        ]

        return CalendarResult(
            entries=entry_results,
            total_posts=len(entry_results),
        )

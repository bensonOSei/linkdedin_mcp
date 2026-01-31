"""Service for planning multi-day LinkedIn content calendars."""

from datetime import datetime, timedelta, timezone

from linkedin_mcp.domain.value_objects.posting_time import OptimalPostingTime

_CONTENT_TYPES: list[str] = [
    "thought-leadership",
    "how-to",
    "story",
    "poll",
    "listicle",
    "case-study",
]

_OPTIMAL_DAYS: list[str] = ["Tuesday", "Wednesday", "Thursday"]
_OPTIMAL_HOURS: list[int] = [9, 10, 12]


class CalendarEntry:
    """A single entry in a content calendar."""

    def __init__(
        self,
        date: datetime,
        topic: str,
        content_type: str,
        posting_time: OptimalPostingTime,
    ) -> None:
        """Initialize a calendar entry.

        Args:
            date: The date for this entry.
            topic: The post topic.
            content_type: Type of content (thought-leadership, how-to, etc).
            posting_time: Recommended posting time.
        """
        self.date = date
        self.topic = topic
        self.content_type = content_type
        self.posting_time = posting_time

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the calendar entry.
        """
        return {
            "date": self.date.isoformat(),
            "topic": self.topic,
            "content_type": self.content_type,
            "posting_time": self.posting_time.model_dump(),
        }


class CalendarPlanner:
    """Plans multi-day content calendars for LinkedIn.

    Distributes topics across optimal days with varied content types
    to maximize engagement and maintain audience interest.
    """

    def plan(
        self,
        topics: list[str],
        start_date: datetime | None = None,
        posts_per_week: int = 3,
    ) -> list[CalendarEntry]:
        """Plan a content calendar.

        Args:
            topics: List of topics to schedule.
            start_date: Starting date for the calendar (defaults to now).
            posts_per_week: Target posts per week (default 3).

        Returns:
            List of CalendarEntry objects with scheduled topics.
        """
        if start_date is None:
            start_date = datetime.now(timezone.utc)

        entries: list[CalendarEntry] = []
        current_date = self._next_optimal_day(start_date)

        for i, topic in enumerate(topics):
            content_type = _CONTENT_TYPES[i % len(_CONTENT_TYPES)]
            hour = _OPTIMAL_HOURS[i % len(_OPTIMAL_HOURS)]
            day_name = current_date.strftime("%A")

            posting_time = OptimalPostingTime(
                day=day_name,
                hour=hour,
                confidence=0.85,
                reason=f"Optimal slot for {content_type} content.",
            )

            entries.append(
                CalendarEntry(
                    date=current_date.replace(hour=hour, minute=0, second=0, microsecond=0),
                    topic=topic,
                    content_type=content_type,
                    posting_time=posting_time,
                )
            )

            current_date = self._next_posting_date(current_date, posts_per_week)

        return entries

    def _next_optimal_day(self, date: datetime) -> datetime:
        """Find the next optimal posting day (Tue/Wed/Thu).

        Args:
            date: Starting date.

        Returns:
            The next Tuesday, Wednesday, or Thursday.
        """
        while date.strftime("%A") not in _OPTIMAL_DAYS:
            date += timedelta(days=1)
        return date

    def _next_posting_date(self, current: datetime, posts_per_week: int) -> datetime:
        """Calculate the next posting date based on frequency.

        Args:
            current: Current posting date.
            posts_per_week: Target posts per week.

        Returns:
            Next posting date.
        """
        if posts_per_week >= 3:
            gap = 2
        elif posts_per_week == 2:
            gap = 3
        else:
            gap = 7

        next_date = current + timedelta(days=gap)
        return self._next_optimal_day(next_date)

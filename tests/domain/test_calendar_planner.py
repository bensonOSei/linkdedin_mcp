"""Tests for the CalendarPlanner domain service."""

from datetime import datetime, timezone

from linkedin_mcp.domain.services.calendar_planner import CalendarPlanner


def test_plan_creates_entries_for_all_topics(planner: CalendarPlanner) -> None:
    topics = ["AI trends", "Leadership", "Marketing"]
    entries = planner.plan(topics)
    assert len(entries) == 3


def test_plan_assigns_different_content_types(planner: CalendarPlanner) -> None:
    topics = ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5", "Topic 6"]
    entries = planner.plan(topics)
    content_types = [entry.content_type for entry in entries]
    # Should cycle through different types
    assert len(set(content_types)) > 1


def test_plan_uses_optimal_days(planner: CalendarPlanner) -> None:
    topics = ["Topic 1", "Topic 2", "Topic 3"]
    entries = planner.plan(topics)
    for entry in entries:
        day_name = entry.date.strftime("%A")
        assert day_name in ["Tuesday", "Wednesday", "Thursday"]


def test_plan_with_custom_start_date(planner: CalendarPlanner) -> None:
    start = datetime(2025, 8, 1, 9, 0, tzinfo=timezone.utc)  # A Friday
    topics = ["Topic 1"]
    entries = planner.plan(topics, start_date=start)
    # Should skip to next optimal day (Tuesday)
    assert entries[0].date > start


def test_plan_with_high_frequency(planner: CalendarPlanner) -> None:
    topics = ["Topic 1", "Topic 2"]
    entries = planner.plan(topics, posts_per_week=3)
    # Gap should be 2 days for 3 posts/week
    assert len(entries) == 2
    gap = (entries[1].date - entries[0].date).days
    assert gap >= 2


def test_plan_with_low_frequency(planner: CalendarPlanner) -> None:
    topics = ["Topic 1", "Topic 2"]
    entries = planner.plan(topics, posts_per_week=1)
    # Gap should be 7 days for 1 post/week
    assert len(entries) == 2
    gap = (entries[1].date - entries[0].date).days
    assert gap >= 7


def test_plan_with_medium_frequency(planner: CalendarPlanner) -> None:
    topics = ["Topic 1", "Topic 2"]
    entries = planner.plan(topics, posts_per_week=2)
    # Gap should be 3 days for 2 posts/week
    assert len(entries) == 2
    gap = (entries[1].date - entries[0].date).days
    assert gap >= 3


def test_entry_to_dict_serialization(planner: CalendarPlanner) -> None:
    topics = ["Topic 1"]
    entries = planner.plan(topics)
    entry_dict = entries[0].to_dict()
    assert "date" in entry_dict
    assert "topic" in entry_dict
    assert "content_type" in entry_dict
    assert "posting_time" in entry_dict
    assert entry_dict["topic"] == "Topic 1"


def test_plan_assigns_optimal_hours(planner: CalendarPlanner) -> None:
    topics = ["T1", "T2", "T3"]
    entries = planner.plan(topics)
    hours = [entry.date.hour for entry in entries]
    # Should use hours from optimal set [9, 10, 12]
    for hour in hours:
        assert hour in [9, 10, 12]

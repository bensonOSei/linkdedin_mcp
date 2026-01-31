"""MCP server entry point for LinkedIn Strategic Posting tools."""

import os
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from linkedin_mcp.container import Container

mcp = FastMCP("linkedin-mcp")

_client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
_client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
container = Container(client_id=_client_id, client_secret=_client_secret)


@mcp.tool()
def draft_post(
    topic: str, tone: str | None = None, content: str | None = None
) -> dict[str, object]:
    """Draft a new LinkedIn post.

    Either provide custom content or let the tool generate template content.
    When content is provided, it becomes the exact post body text.

    Args:
        topic: The subject matter of the post.
        tone: Writing tone - professional, casual, inspirational, educational,
            or storytelling. Uses configured default if not provided.
        content: Custom post body text. If provided, this is used as-is
            instead of generating template content. Max 3000 characters.

    Returns:
        Post details including ID, content, and status.
    """
    import sys

    if content:
        print(f"DEBUG draft_post: Received content length: {len(content)}", file=sys.stderr)
        print(f"DEBUG draft_post: First 200 chars: {content[:200]}", file=sys.stderr)
        print(f"DEBUG draft_post: Last 200 chars: {content[-200:]}", file=sys.stderr)
    result = container.draft_post.execute(topic=topic, tone=tone, content=content)
    print(f"DEBUG draft_post: Result body length: {len(result.content.body)}", file=sys.stderr)
    return result.model_dump()


@mcp.tool()
def optimize_post(post_id: str) -> dict[str, object]:
    """Score a post for engagement potential and get improvement suggestions.

    Evaluates the post across dimensions: length, hashtags, readability,
    hook quality, and CTA presence.

    Args:
        post_id: ID of the post to optimize.

    Returns:
        Engagement score breakdown and improvement suggestions.
    """
    result = container.optimize_post.execute(post_id=post_id)
    return result.model_dump()


@mcp.tool()
def suggest_hashtags(
    topic: str,
    industry: str = "default",
    post_id: str | None = None,
) -> dict[str, object]:
    """Suggest categorized hashtags for a LinkedIn post.

    Returns a balanced mix of industry, trending, niche, and broad hashtags.
    Optionally attaches them to an existing post.

    Args:
        topic: The topic to generate hashtags for.
        industry: Industry vertical (technology, marketing, leadership, etc).
        post_id: Optional post ID to attach hashtags to.

    Returns:
        List of categorized hashtag recommendations.
    """
    result = container.suggest_hashtags.execute(
        topic=topic,
        industry=industry,
        post_id=post_id,
    )
    return result.model_dump()


@mcp.tool()
def get_optimal_time(
    timezone_name: str = "UTC",
    industry: str = "default",
) -> dict[str, object]:
    """Get optimal LinkedIn posting time recommendations.

    Based on LinkedIn algorithm research for peak engagement windows.
    Adjusts recommendations by timezone and industry.

    Args:
        timezone_name: User's timezone (e.g., 'US/Eastern', 'UTC').
        industry: Industry vertical for timing adjustments.

    Returns:
        Top 3 posting time recommendations with confidence scores.
    """
    result = container.get_optimal_time.execute(
        timezone=timezone_name,
        industry=industry,
    )
    return result.model_dump()


@mcp.tool()
def schedule_post(post_id: str, scheduled_time: str) -> dict[str, object]:
    """Schedule a draft post for publishing at a specific time.

    Transitions the post from draft to scheduled status.

    Args:
        post_id: ID of the draft post to schedule.
        scheduled_time: ISO 8601 datetime string for when to publish.

    Returns:
        Updated post details with scheduled status and time.
    """
    dt = datetime.fromisoformat(scheduled_time)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    result = container.schedule_post.execute(post_id=post_id, scheduled_time=dt)
    return result.model_dump()


@mcp.tool()
def plan_content_calendar(
    topics: list[str],
    posts_per_week: int = 3,
) -> dict[str, object]:
    """Plan a multi-day LinkedIn content calendar.

    Distributes topics across optimal posting days with varied content types
    (thought-leadership, how-to, story, poll, listicle, case-study).

    Args:
        topics: List of topics to schedule across the calendar.
        posts_per_week: Target number of posts per week (default 3).

    Returns:
        Calendar entries with dates, content types, and posting times.
    """
    result = container.content_calendar.execute(
        topics=topics,
        posts_per_week=posts_per_week,
    )
    return result.model_dump()


@mcp.tool()
def get_drafts() -> dict[str, object]:
    """List all draft posts.

    Returns:
        List of draft post summaries with topics and hooks.
    """
    result = container.get_drafts.execute()
    return result.model_dump()


@mcp.tool()
def get_scheduled_posts() -> dict[str, object]:
    """List all scheduled posts.

    Returns:
        List of scheduled post summaries with topics and hooks.
    """
    result = container.get_scheduled_posts.execute()
    return result.model_dump()


@mcp.tool()
def get_config() -> dict[str, object]:
    """Get the current user configuration.

    Returns current settings including default tone and valid tone options.

    Returns:
        Current configuration with default_tone and valid_tones.
    """
    result = container.get_config.execute()
    return result.model_dump()


@mcp.tool()
def set_default_tone(tone: str) -> dict[str, object]:
    """Set the default tone for new posts.

    Persists the preference so all future draft_post calls use this tone
    unless explicitly overridden.

    Args:
        tone: The default tone (professional, casual, inspirational, educational, storytelling).

    Returns:
        Updated configuration with the new default tone.
    """
    result = container.set_default_tone.execute(tone=tone)
    return result.model_dump()


@mcp.tool()
def linkedin_authenticate() -> dict[str, object]:
    """Start LinkedIn OAuth2 authentication.

    Returns an auth_url that the user must open in their browser to authorize.
    After the user authorizes, call linkedin_auth_callback to complete
    the flow.

    Requires LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.

    Returns:
        Auth URL to visit and status "waiting".
    """
    result = container.authenticate.start_auth()
    return result.model_dump()


@mcp.tool()
def linkedin_auth_callback(timeout: int = 120) -> dict[str, object]:
    """Complete LinkedIn OAuth2 authentication after user authorizes.

    Call this after the user has visited the auth_url from linkedin_authenticate
    and authorized the application in their browser. This waits for the
    callback, exchanges the code for a token, and saves credentials.

    Args:
        timeout: Seconds to wait for the callback (default 120).

    Returns:
        Auth status with person URN and token expiry on success.
    """
    result = container.authenticate.complete_auth(timeout=float(timeout))
    return result.model_dump()


@mcp.tool()
def linkedin_publish_post(post_id: str) -> dict[str, object]:
    """Publish a post directly to LinkedIn.

    Requires prior authentication via linkedin_authenticate.
    The post can be in 'draft' or 'scheduled' status.

    Args:
        post_id: ID of the scheduled post to publish.

    Returns:
        LinkedIn post URN and published timestamp.
    """
    result = container.publish_post.execute(post_id=post_id)
    return result.model_dump()


@mcp.tool()
def linkedin_auth_status() -> dict[str, object]:
    """Check current LinkedIn authentication status.

    Returns whether you're authenticated, the person URN,
    and when the token expires.

    Returns:
        Authentication status details.
    """
    result = container.check_auth.execute()
    return result.model_dump()


def main() -> None:
    """Start the MCP server on stdio transport."""
    if not _client_id or not _client_secret:
        msg = (
            "LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables are required. "
            "Get them from https://developer.linkedin.com/ under your app's Auth tab."
        )
        raise SystemExit(msg)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

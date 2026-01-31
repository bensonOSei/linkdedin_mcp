"""Serialization helpers for post persistence using Pydantic."""

from linkedin_mcp.domain.entities.post import Post


def serialize_posts(posts: list[Post]) -> list[dict[str, object]]:
    """Serialize a list of posts to JSON-compatible dicts.

    Args:
        posts: List of Post entities to serialize.

    Returns:
        List of dictionaries suitable for JSON serialization.
    """
    return [post.model_dump(mode="json") for post in posts]


def deserialize_posts(data: list[dict[str, object]]) -> list[Post]:
    """Deserialize a list of dicts to Post entities.

    Args:
        data: List of dictionaries from JSON storage.

    Returns:
        List of Post entities.
    """
    return [Post.model_validate(item) for item in data]

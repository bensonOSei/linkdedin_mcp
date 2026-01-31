"""JSON file-based implementation of PostRepository."""

import fcntl
import json
from pathlib import Path

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.repositories.post_repository import PostRepository
from linkedin_mcp.domain.value_objects.post_status import PostStatus
from linkedin_mcp.infrastructure.serialization import deserialize_posts, serialize_posts

_DEFAULT_STORAGE_DIR = Path.home() / ".linkedin-mcp"
_DEFAULT_STORAGE_FILE = "posts.json"


class JsonPostRepository(PostRepository):
    """Persists posts as JSON in a local file.

    Uses file locking (fcntl) for thread-safe operations.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize the repository.

        Args:
            storage_path: Path to the JSON storage file.
                Defaults to ~/.linkedin-mcp/posts.json.
        """
        if storage_path is None:
            storage_path = _DEFAULT_STORAGE_DIR / _DEFAULT_STORAGE_FILE
        self._storage_path = storage_path
        self._ensure_storage_exists()

    def save(self, post: Post) -> None:
        """Persist a post, creating or updating as needed.

        Args:
            post: The post to save.
        """
        posts = self._load_all()
        existing_index = next(
            (i for i, p in enumerate(posts) if p.id == post.id),
            None,
        )
        if existing_index is not None:
            posts[existing_index] = post
        else:
            posts.append(post)
        self._save_all(posts)

    def get_by_id(self, post_id: str) -> Post | None:
        """Retrieve a post by its ID.

        Args:
            post_id: The unique identifier of the post.

        Returns:
            The matching Post or None if not found.
        """
        posts = self._load_all()
        return next((p for p in posts if p.id == post_id), None)

    def get_by_status(self, status: PostStatus) -> list[Post]:
        """Retrieve all posts with a given status.

        Args:
            status: The status to filter by.

        Returns:
            List of matching posts.
        """
        posts = self._load_all()
        return [p for p in posts if p.status == status]

    def get_all(self) -> list[Post]:
        """Retrieve all posts.

        Returns:
            List of all stored posts.
        """
        return self._load_all()

    def delete(self, post_id: str) -> None:
        """Delete a post by its ID.

        Args:
            post_id: The unique identifier of the post to delete.
        """
        posts = self._load_all()
        posts = [p for p in posts if p.id != post_id]
        self._save_all(posts)

    def _ensure_storage_exists(self) -> None:
        """Create storage directory and file if they don't exist."""
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._storage_path.write_text("[]")

    def _load_all(self) -> list[Post]:
        """Load all posts from the JSON file with file locking.

        Returns:
            List of all stored posts.
        """
        with self._storage_path.open("r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return deserialize_posts(data)

    def _save_all(self, posts: list[Post]) -> None:
        """Save all posts to the JSON file with file locking.

        Args:
            posts: List of posts to persist.
        """
        with self._storage_path.open("w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(serialize_posts(posts), f, indent=2)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

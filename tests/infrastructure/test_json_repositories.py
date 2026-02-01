"""Tests for JSON repository implementations."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from linkedin_mcp.domain.entities.post import Post
from linkedin_mcp.domain.entities.user_config import UserConfig
from linkedin_mcp.domain.value_objects.linkedin_credentials import LinkedInCredentials
from linkedin_mcp.domain.value_objects.post_content import PostContent
from linkedin_mcp.domain.value_objects.post_status import PostStatus
from linkedin_mcp.infrastructure.json_config_repository import JsonConfigRepository
from linkedin_mcp.infrastructure.json_credentials_repository import JsonCredentialsRepository
from linkedin_mcp.infrastructure.json_post_repository import JsonPostRepository


def test_post_repo_save_creates_file(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)
    post = Post(
        topic="test",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    repo.save(post)
    assert storage_path.exists()


def test_post_repo_get_by_id_returns_saved_post(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)
    post = Post(
        topic="test",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    repo.save(post)
    retrieved = repo.get_by_id(post.id)
    assert retrieved is not None
    assert retrieved.id == post.id
    assert retrieved.topic == post.topic


def test_post_repo_get_by_id_returns_none_for_missing(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)
    retrieved = repo.get_by_id("nonexistent")
    assert retrieved is None


def test_post_repo_save_updates_existing_post(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)
    post = Post(
        topic="test",
        content=PostContent(
            body="original", hook="hook", call_to_action="cta", tone="professional"
        ),
    )
    repo.save(post)

    # Update the post
    new_content = PostContent(
        body="updated", hook="hook", call_to_action="cta", tone="professional"
    )
    post.update_content(new_content)
    repo.save(post)

    # Verify update
    retrieved = repo.get_by_id(post.id)
    assert retrieved is not None
    assert retrieved.content.body == "updated"


def test_post_repo_get_by_status_filters_correctly(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)

    # Create posts with different statuses
    draft = Post(
        topic="draft",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    scheduled = Post(
        topic="scheduled",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    scheduled.schedule(datetime.now(timezone.utc))

    repo.save(draft)
    repo.save(scheduled)

    # Test filtering
    drafts = repo.get_by_status(PostStatus.DRAFT)
    assert len(drafts) == 1
    assert drafts[0].id == draft.id

    scheduled_posts = repo.get_by_status(PostStatus.SCHEDULED)
    assert len(scheduled_posts) == 1
    assert scheduled_posts[0].id == scheduled.id


def test_post_repo_get_all_returns_all_posts(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)

    post1 = Post(
        topic="test1",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    post2 = Post(
        topic="test2",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    repo.save(post1)
    repo.save(post2)

    all_posts = repo.get_all()
    assert len(all_posts) == 2


def test_post_repo_delete_removes_post(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)

    post = Post(
        topic="test",
        content=PostContent(body="body", hook="hook", call_to_action="cta", tone="professional"),
    )
    repo.save(post)
    repo.delete(post.id)

    retrieved = repo.get_by_id(post.id)
    assert retrieved is None


def test_post_repo_delete_nonexistent_does_not_error(tmp_path: Path) -> None:
    storage_path = tmp_path / "posts.json"
    repo = JsonPostRepository(storage_path=storage_path)
    # Should not raise error
    repo.delete("nonexistent")


def test_config_repo_load_returns_default_when_file_missing(tmp_path: Path) -> None:
    storage_path = tmp_path / "config.json"
    repo = JsonConfigRepository(storage_path=storage_path)
    config = repo.load()
    assert config.default_tone == "professional"


def test_config_repo_save_and_load_roundtrip(tmp_path: Path) -> None:
    storage_path = tmp_path / "config.json"
    repo = JsonConfigRepository(storage_path=storage_path)

    config = UserConfig(default_tone="casual")
    repo.save(config)

    loaded = repo.load()
    assert loaded.default_tone == "casual"


def test_config_repo_save_creates_directory(tmp_path: Path) -> None:
    storage_path = tmp_path / "subdir" / "config.json"
    repo = JsonConfigRepository(storage_path=storage_path)

    config = UserConfig(default_tone="inspirational")
    repo.save(config)

    assert storage_path.exists()
    assert storage_path.parent.exists()


def test_config_repo_default_storage_path() -> None:
    # Test that default path construction doesn't error
    repo = JsonConfigRepository()
    # Just verify it was created, don't actually save to home dir
    assert repo is not None


def test_creds_repo_load_returns_none_when_file_missing(tmp_path: Path) -> None:
    storage_path = tmp_path / "creds.json"
    repo = JsonCredentialsRepository(storage_path=storage_path)
    creds = repo.load()
    assert creds is None


def test_creds_repo_save_and_load_roundtrip(tmp_path: Path) -> None:
    storage_path = tmp_path / "creds.json"
    repo = JsonCredentialsRepository(storage_path=storage_path)

    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    creds = LinkedInCredentials(
        access_token="test-token", expires_at=expires_at, person_urn="urn:li:person:123"
    )
    repo.save(creds)

    loaded = repo.load()
    assert loaded is not None
    assert loaded.access_token == "test-token"
    assert loaded.person_urn == "urn:li:person:123"


def test_creds_repo_save_creates_directory(tmp_path: Path) -> None:
    storage_path = tmp_path / "subdir" / "creds.json"
    repo = JsonCredentialsRepository(storage_path=storage_path)

    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    creds = LinkedInCredentials(
        access_token="token", expires_at=expires_at, person_urn="urn:li:person:abc"
    )
    repo.save(creds)

    assert storage_path.exists()
    assert storage_path.parent.exists()


def test_creds_repo_delete_removes_credentials(tmp_path: Path) -> None:
    storage_path = tmp_path / "creds.json"
    repo = JsonCredentialsRepository(storage_path=storage_path)

    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    creds = LinkedInCredentials(
        access_token="token", expires_at=expires_at, person_urn="urn:li:person:abc"
    )
    repo.save(creds)
    assert storage_path.exists()

    repo.delete()
    assert not storage_path.exists()


def test_post_repo_default_storage_path() -> None:
    # Test that default path construction doesn't error
    repo = JsonPostRepository()
    assert repo is not None


def test_creds_repo_delete_when_file_missing_does_not_error(tmp_path: Path) -> None:
    storage_path = tmp_path / "creds.json"
    repo = JsonCredentialsRepository(storage_path=storage_path)
    # Should not raise error
    repo.delete()


def test_creds_repo_default_storage_path() -> None:
    # Test that default path construction doesn't error
    repo = JsonCredentialsRepository()
    assert repo is not None

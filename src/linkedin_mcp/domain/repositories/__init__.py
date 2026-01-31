"""Domain repository interfaces."""

from linkedin_mcp.domain.repositories.config_repository import ConfigRepository
from linkedin_mcp.domain.repositories.credentials_repository import CredentialsRepository
from linkedin_mcp.domain.repositories.post_repository import PostRepository

__all__ = ["ConfigRepository", "CredentialsRepository", "PostRepository"]

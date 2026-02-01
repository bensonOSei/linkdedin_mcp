# LinkedIn Strategic Posting MCP Server

An MCP server that helps draft, optimize, schedule, and publish LinkedIn posts programmatically. Built with Domain-Driven Design (DDD) architecture in Python.

## Features

- **Draft posts** with structured hooks, body content, and calls to action across multiple tones
- **Publish to LinkedIn** via OAuth2 authentication and LinkedIn REST API v202502
- **Score engagement potential** with a multi-dimensional optimizer (length, readability, hook quality, hashtags, CTA)
- **Suggest hashtags** categorized by industry, trending, niche, and broad reach
- **Recommend posting times** based on LinkedIn algorithm research (Tue-Thu peak windows)
- **Schedule posts** with a draft-to-scheduled-to-published lifecycle
- **Plan content calendars** distributing topics across optimal days with varied content types
- **Persistent storage** via local JSON file at `~/.linkedin-mcp/posts.json`

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- LinkedIn Developer App (for publishing posts)

## Setup

### 1. Clone and Install

```bash
git clone <repo-url> && cd linkedin-mcp
uv sync
```

### 2. Create LinkedIn Developer App

1. Go to [LinkedIn Developers](https://developer.linkedin.com/)
2. Create a new app (or use an existing one)
3. Under "Auth" tab:
   - Add redirect URL: `http://localhost:8099/callback`
   - Request these scopes: `openid`, `profile`, `w_member_social`
4. Copy your **Client ID** and **Client Secret**

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

Or export them in your shell:

```bash
export LINKEDIN_CLIENT_ID=your_client_id_here
export LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

### 4. Configure MCP Client

#### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "linkedin-mcp": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/linkedin-mcp", "run", "linkedin-mcp"],
      "env": {
        "LINKEDIN_CLIENT_ID": "your_client_id_here",
        "LINKEDIN_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

#### For Claude Code (VSCode Extension)

Use the Claude CLI to add the MCP server:

```bash
claude mcp add \
  -e LINKEDIN_CLIENT_ID=your_client_id_here \
  -e LINKEDIN_CLIENT_SECRET=your_client_secret_here \
  linkedin-mcp \
  -- uv --directory /absolute/path/to/linkedin-mcp run linkedin-mcp
```

Or manually edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "linkedin-mcp": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/linkedin-mcp", "run", "linkedin-mcp"],
      "env": {
        "LINKEDIN_CLIENT_ID": "your_client_id_here",
        "LINKEDIN_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

Restart Claude Desktop or reload Claude Code (Cmd+R) after configuration changes.

### 5. Authenticate with LinkedIn

Once the MCP server is running, authenticate:

1. Call `linkedin_authenticate()` - you'll receive an auth URL
2. Open the URL in your browser and authorize the app
3. Call `linkedin_auth_callback()` - completes the OAuth flow
4. Credentials are saved to `~/.linkedin-mcp/credentials.json`

You can check auth status anytime with `linkedin_auth_status()`.

## Usage

### Testing with MCP Dev Inspector

```bash
# Make sure environment variables are set first
export LINKEDIN_CLIENT_ID=your_client_id_here
export LINKEDIN_CLIENT_SECRET=your_client_secret_here

uv run mcp dev src/linkedin_mcp/server.py
```

## MCP Tools

### Post Management

| Tool | Description |
|---|---|
| `draft_post` | Draft a new LinkedIn post with a topic and tone (professional, casual, inspirational, educational, storytelling). Optionally provide custom content instead of template generation. |
| `optimize_post` | Score a post for engagement potential and get improvement suggestions |
| `suggest_hashtags` | Get categorized hashtag recommendations (industry, trending, niche, broad), optionally attach to a post |
| `get_optimal_time` | Get top 3 posting time recommendations by timezone and industry |
| `schedule_post` | Schedule a draft post for a specific time (ISO 8601) |
| `plan_content_calendar` | Plan a multi-day calendar with varied content types (thought-leadership, how-to, story, poll, listicle, case-study) |
| `get_drafts` | List all draft posts |
| `get_scheduled_posts` | List all scheduled posts |

### LinkedIn Publishing

| Tool | Description |
|---|---|
| `linkedin_authenticate` | Start OAuth2 flow. Returns auth URL to open in browser. |
| `linkedin_auth_callback` | Complete OAuth2 flow after user authorizes. Exchanges code for token and saves credentials. |
| `linkedin_publish_post` | Publish a post directly to LinkedIn (requires authentication) |
| `linkedin_auth_status` | Check if authenticated, view person URN and token expiry |

### Configuration

| Tool | Description |
|---|---|
| `get_config` | Get current configuration (default tone, valid tones) |
| `set_default_tone` | Set default tone for new posts |

## Example Workflow

```python
# 1. Authenticate with LinkedIn
linkedin_authenticate()  # Opens browser for OAuth
linkedin_auth_callback() # Completes authentication

# 2. Draft a post
result = draft_post(
    topic="Building MCP servers",
    content="Just built an MCP server for LinkedIn posting...\n\nIt uses DDD architecture..."
)
post_id = result["post_id"]

# 3. Optimize and add hashtags
optimize_post(post_id)  # Get engagement score
suggest_hashtags(topic="MCP servers", post_id=post_id, industry="technology")

# 4. Publish to LinkedIn
linkedin_publish_post(post_id)  # Posts immediately

# Or schedule for later
schedule_post(post_id, scheduled_time="2026-02-03T09:00:00Z")
```

## Known Issues

### LinkedIn API Post Truncation

LinkedIn's REST Posts API (v202502) may truncate post content to approximately 100 characters in some cases, despite accepting the full payload and returning a 201 success response. This appears to be a LinkedIn API bug.

**Workaround**: Keep opening paragraphs concise or rephrase if truncation occurs. The full content is sent correctly to LinkedIn, but their platform may not display it all.

## Architecture

DDD layers with strict dependency rule: **Domain <- Application <- Infrastructure**

```text
server.py          MCP tool handlers (thin adapters)
  -> container.py  Dependency wiring
    -> use cases   Orchestrate domain logic
      -> domain    Services, entities, value objects, repository ABCs
    -> infra       JSON repository, serialization
```

- **Domain**: Frozen Pydantic value objects, Post entity with state machine, repository ABC, domain services
- **Application**: Use cases with `execute()` pattern, Pydantic DTOs
- **Infrastructure**: JSON file repository with `fcntl` locking, LinkedIn REST API client

## Development

```bash
uv run ruff check --fix src/ tests/    # Lint with auto-fix
uv run ruff format src/ tests/          # Format code
uv run mypy src/                        # Strict type checking
uv run pytest                           # Run tests
```

## Files and Storage

- `~/.linkedin-mcp/posts.json` - Post storage (draft, scheduled, published)
- `~/.linkedin-mcp/credentials.json` - LinkedIn OAuth credentials (access token, person URN, expiry)
- `~/.linkedin-mcp/config.json` - User preferences (default tone)

## License

[MIT](LICENSE) - Copyright (c) 2026 [Benson Osei Mensah](https://bensonoseimensah.com)

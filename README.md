# 🌿 Gitrama MCP Server

> AI-powered Git intelligence for your IDE — smart commits, branch names, PR descriptions, changelogs, and workflow management.

[![PyPI](https://img.shields.io/pypi/v/gitrama-mcp)](https://pypi.org/project/gitrama-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/gitrama-mcp)](https://pypi.org/project/gitrama-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What is this?

Gitrama MCP Server exposes [Gitrama](https://gitrama.ai)'s CLI as **10 MCP tools** that any AI assistant can use. Instead of typing `gtr commit` in your terminal, your AI assistant calls the tool directly — analyzing your code changes, generating commit messages, suggesting branch names, and more.

**Works with:** Cursor · Claude Desktop · Claude Code · Windsurf · VS Code (Copilot) · Zed · any MCP-compatible client

## Install (< 60 seconds)

### Step 1: Install the package

```bash
pip install gitrama-mcp
```

Or with uv:
```bash
uv pip install gitrama-mcp
```

This installs both the MCP server and the `gitrama` CLI.

### Step 2: Connect to your IDE

<details>
<summary><b>Cursor</b></summary>

Add to `.cursor/mcp.json` in your project (or global settings):

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Add to `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add gitrama gitrama-mcp
```
</details>

<details>
<summary><b>VS Code (Copilot)</b></summary>

Add to `.vscode/settings.json`:

```json
{
  "mcp": {
    "servers": {
      "gitrama": {
        "command": "gitrama-mcp"
      }
    }
  }
}
```
</details>

<details>
<summary><b>Windsurf</b></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "gitrama-mcp"
    }
  }
}
```
</details>

<details>
<summary><b>Zed</b></summary>

Add to Zed settings (`⌘,`):

```json
{
  "context_servers": {
    "gitrama": {
      "command": {
        "path": "gitrama-mcp"
      }
    }
  }
}
```
</details>

### Step 3: Done.

Ask your AI: *"Commit my staged changes"* — and watch it call `gitrama_commit`.

---

## Tools (11)

### Repository Intelligence

| Tool | Description |
|------|-------------|
| `gitrama_ask` | Ask any question about your repo — ownership, history, risk, changes |

### Commit Intelligence

| Tool | Description |
|------|-------------|
| `gitrama_commit` | Generate an AI commit message for staged changes |
| `gitrama_stage_and_commit` | Stage files + commit in one step |
| `gitrama_commit_quality` | Analyze quality of recent commit messages |

### Branch Management

| Tool | Description |
|------|-------------|
| `gitrama_branch` | Create a new branch |
| `gitrama_branch_suggest` | Get AI-suggested branch names from a description |

### PR & Changelog

| Tool | Description |
|------|-------------|
| `gitrama_pr` | Generate a PR description from branch diff |
| `gitrama_changelog` | Generate a changelog between refs |

### Stream (Workflow) Management

| Tool | Description |
|------|-------------|
| `gitrama_stream_status` | Show current workflow stream |
| `gitrama_stream_switch` | Switch to a different stream |
| `gitrama_stream_list` | List all streams in the repo |

---

## Tool Details

### `gitrama_ask`

Ask a natural language question about your repository. Gitrama analyzes commit history, file structure, blame data, and diffs to answer.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | *required* | Any question about your repo |
| `scope` | string | `"auto"` | Context: `"auto"`, `"branch"`, `"full"`, or `"staged"` |
| `model` | string | `""` | AI model override |

**Example prompts:**
- *"Who owns the auth module?"*
- *"When did we last change the payment logic?"*
- *"What's the riskiest file in this repo?"*
- *"Summarize what happened on this branch"*
- *"What changed in the last 3 days?"*
- *"Explain the purpose of src/utils/retry.py"*

---

### `gitrama_commit`

Generate an AI-powered commit message for staged changes.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message_type` | string | `"conventional"` | Style: `"conventional"`, `"detailed"`, or `"simple"` |
| `context` | string | `""` | Optional context (e.g., `"fixing auth bug"`) |
| `model` | string | `""` | AI model override (e.g., `"gpt-4o"`, `"claude-sonnet-4-20250514"`) |

**Example prompt:** *"Commit my changes with a conventional message, context: refactoring the payment module"*

---

### `gitrama_stage_and_commit`

Stage files and commit in one step.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `files` | string | `"."` | Files to stage (`.` for all, or space-separated paths) |
| `message_type` | string | `"conventional"` | Commit style |
| `context` | string | `""` | Optional context |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Stage and commit all my changes"*

---

### `gitrama_commit_quality`

Analyze recent commit message quality.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | `10` | Number of commits to analyze (1-50) |

**Example prompt:** *"How good are our last 20 commit messages?"*

---

### `gitrama_branch_suggest`

Get AI-suggested branch names.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | *required* | Task description |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Suggest a branch name for adding OAuth2 support"*

---

### `gitrama_pr`

Generate a PR description.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base` | string | `""` | Target branch (default: main/master) |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Write a PR description for this branch"*

---

### `gitrama_changelog`

Generate a changelog.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `since` | string | `""` | Start ref (tag, branch, hash) |
| `until` | string | `""` | End ref (default: HEAD) |
| `format` | string | `"markdown"` | `"markdown"` or `"json"` |
| `model` | string | `""` | AI model override |

**Example prompt:** *"Generate a changelog since v1.1.2"*

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GTR_CWD` | `os.getcwd()` | Working directory for git operations |
| `GTR_MCP_TRANSPORT` | `"stdio"` | Transport: `"stdio"` or `"streamable-http"` |
| `GTR_MCP_HOST` | `"0.0.0.0"` | HTTP host (when using streamable-http) |
| `GTR_MCP_PORT` | `"8765"` | HTTP port (when using streamable-http) |

### HTTP Transport (for CI/CD)

```bash
GTR_MCP_TRANSPORT=streamable-http GTR_MCP_PORT=8765 gitrama-mcp
```

Then connect your client to `http://localhost:8765/mcp`.

---

## Requirements

- Python 3.10+
- Git installed and in PATH
- A Gitrama API key or local Ollama instance

Set your API key:
```bash
gtr config --key YOUR_API_KEY
```

Or use a local model:
```bash
gtr config --provider ollama --model llama3
```

---

## Development

```bash
git clone https://github.com/ahmaxdev/gitrama-mcp.git
cd gitrama-mcp
pip install -e ".[dev]"

# Test with MCP Inspector
mcp dev src/gitrama_mcp/server.py
```

---

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Alfonso Harding](https://www.linkedin.com/in/alfonso-h-47396b5/) · [gitrama.ai](https://gitrama.ai)

🌿

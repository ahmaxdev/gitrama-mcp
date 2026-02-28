"""
Gitrama MCP Server — 10 tools for AI-powered Git intelligence.

Exposes Gitrama's CLI capabilities as MCP tools for use in:
- Cursor
- Claude Desktop
- Claude Code
- Windsurf
- VS Code (Copilot)
- Zed
- CI/CD pipelines

Transport: stdio (default) or streamable-http
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server initialisation
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "gitrama",
    instructions=(
        "AI-powered Git intelligence — smart commits, branch naming, "
        "PR descriptions, changelogs, and stream-based workflow management. "
        "Requires `gitrama` CLI installed (pip install gitrama)."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_cwd() -> str:
    """Return the working directory — prefer GTR_CWD env var, then os.getcwd()."""
    return os.environ.get("GTR_CWD", os.getcwd())


async def _run_gtr(args: list[str], cwd: Optional[str] = None, timeout: int = 120) -> dict:
    """
    Run a `gtr` CLI command and return structured output.

    Returns:
        dict with keys: success (bool), stdout (str), stderr (str), returncode (int)
    """
    cmd = ["gtr"] + args
    work_dir = cwd or _get_cwd()

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
        return {
            "success": proc.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": proc.returncode,
        }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s: {' '.join(cmd)}",
            "returncode": -1,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": (
                "gitrama CLI not found. Install with: pip install gitrama\n"
                "Docs: https://gitrama.ai"
            ),
            "returncode": -1,
        }


def _format_result(result: dict, context: str = "") -> str:
    """Format a CLI result into a clean MCP response."""
    if result["success"]:
        return result["stdout"] if result["stdout"] else f"✅ {context or 'Done'}"
    else:
        msg = result["stderr"] or result["stdout"] or "Unknown error"
        return f"❌ Error: {msg}"


# ---------------------------------------------------------------------------
# Tool 1: gitrama_commit
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_commit(
    message: str = "",
) -> str:
    """
    Generate an AI-powered commit message for currently staged changes.

    Analyzes the git diff of staged files and produces a conventional
    commit message following best practices. Requires files to be staged
    first (git add).

    Args:
        message: Optional custom commit message. If provided, skips AI
                 generation and uses this message directly.
    """
    args = ["commit", "-y"]
    if message:
        args.extend(["-m", message])

    result = await _run_gtr(args)
    return _format_result(result, "Commit created")


# ---------------------------------------------------------------------------
# Tool 2: gitrama_stage_and_commit
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_stage_and_commit(
    files: str = ".",
    message: str = "",
) -> str:
    """
    Stage files and create an AI-powered commit in one step.

    Equivalent to `git add <files> && gtr commit -y`. Stages the specified
    files (or all changes), then generates and applies an AI commit message.

    Args:
        files: Files to stage — "." for all changes (default), or
               space-separated paths (e.g., "src/auth.py tests/test_auth.py").
        message: Optional custom commit message. If provided, skips AI
                 generation and uses this message directly.
    """
    # Stage files first
    file_list = files.split() if files != "." else ["."]
    stage_cmd = ["git", "add"] + file_list
    try:
        stage_proc = await asyncio.create_subprocess_exec(
            *stage_cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=_get_cwd(),
        )
        await stage_proc.communicate()
    except Exception as e:
        return f"❌ Failed to stage files: {e}"

    # Now commit
    return await gitrama_commit(message=message)


# ---------------------------------------------------------------------------
# Tool 3: gitrama_ask
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_ask(
    question: str,
    stream: str = "",
    deep: bool = False,
) -> str:
    """
    Ask a question about your Git repository and get an AI-powered answer.

    Analyzes your repo's commit history, file structure, blame data, and
    diffs to answer natural language questions. This is Gitrama's core
    intelligence — the ability to understand your codebase.

    Example questions:
    - "Who owns the auth module?"
    - "When did we last change the payment logic?"
    - "What's the riskiest file in this repo?"
    - "Summarize what happened on this branch"
    - "What changed in the last 3 days?"
    - "Explain the purpose of src/utils/retry.py"

    Args:
        question: Natural language question about your repository.
        stream: Optional stream context override (wip | hotfix | review | experiment).
        deep: Enable full repo history access for deeper analysis.
    """
    args = ["ask", "--query", question]
    if stream:
        args.extend(["--stream", stream])
    if deep:
        args.append("--deep")
    result = await _run_gtr(args, timeout=180)
    return _format_result(result, "Question answered")


# ---------------------------------------------------------------------------
# Tool 4: gitrama_branch
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_branch(
    description: str,
    create: bool = True,
) -> str:
    """
    Generate an AI-powered branch name from a description.

    Analyzes your description and generates a conventional branch name
    following best practices (feat/, fix/, chore/, etc.), then optionally
    creates and switches to the branch.

    Examples:
    - "Add user authentication" → feat/add-user-authentication
    - "Fix memory leak" → fix/memory-leak
    - "Update docs" → docs/update-docs

    Args:
        description: What you're working on (e.g., "add user authentication
                     with OAuth2", "fix timeout in payment processing").
        create: If True (default), creates and switches to the new branch.
                If False, only suggests the branch name without creating it.
    """
    args = ["branch", description]
    if not create:
        args.append("--no-create")
    result = await _run_gtr(args)
    return _format_result(result, "Branch created")


# ---------------------------------------------------------------------------
# Tool 5: gitrama_pr
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_pr(
    base: str = "",
) -> str:
    """
    Generate an AI-powered pull request description.

    Analyzes the diff between the current branch and the base branch,
    then generates a comprehensive PR description with title, summary,
    changes list, and testing notes.

    Args:
        base: Target branch for the PR (default: main or master).
    """
    args = ["pr"]
    if base:
        args.extend(["--base", base])
    result = await _run_gtr(args)
    return _format_result(result, "PR description generated")


# ---------------------------------------------------------------------------
# Tool 6: gitrama_stream_status
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_stream_status() -> str:
    """
    Show the current Gitrama stream (workflow context).

    Streams are Gitrama's concept of workflow focus — they track what
    you're working on and influence AI suggestions. Returns the active
    stream name, description, and associated branch.
    """
    result = await _run_gtr(["stream", "status"])
    return _format_result(result, "Stream status retrieved")


# ---------------------------------------------------------------------------
# Tool 7: gitrama_stream_switch
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_stream_switch(
    name: str,
    description: str = "",
) -> str:
    """
    Switch to a different Gitrama stream (workflow context).

    Creates a new stream or switches to an existing one. Streams help
    the AI understand what you're working on for better suggestions.

    Args:
        name: Stream name (e.g., "auth-refactor", "payment-v2").
        description: Optional description of the stream's purpose.
    """
    args = ["stream", "switch", name]
    if description:
        args.extend(["--description", description])
    result = await _run_gtr(args)
    return _format_result(result, f"Switched to stream '{name}'")


# ---------------------------------------------------------------------------
# Tool 8: gitrama_stream_list
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_stream_list() -> str:
    """
    List all Gitrama streams in the current repository.

    Shows all defined streams with their names, descriptions,
    and associated branches. The active stream is highlighted.
    """
    result = await _run_gtr(["stream", "list"])
    return _format_result(result, "Streams listed")


# ---------------------------------------------------------------------------
# Tool 9: gitrama_health
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_health() -> str:
    """
    Check the Gitrama AI server health status.

    Verifies connectivity to the Gitrama AI API and returns
    the current server status. Useful for diagnosing issues
    when other commands fail.
    """
    result = await _run_gtr(["health"])
    return _format_result(result, "Health check complete")


# ---------------------------------------------------------------------------
# Tool 10: gitrama_status
# ---------------------------------------------------------------------------

@mcp.tool()
async def gitrama_status() -> str:
    """
    Show the working tree status with AI interpretation.

    Displays the current git status including staged, unstaged,
    and untracked files with AI-powered context about the changes.
    """
    result = await _run_gtr(["status"])
    return _format_result(result, "Status retrieved")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Run the Gitrama MCP server."""

    # TTY detection — if a human runs this directly, show help and exit
    if sys.stdin.isatty() and os.environ.get("GTR_MCP_TRANSPORT", "stdio") == "stdio":
        print("""
🌿 Gitrama MCP Server v1.1.0

This server uses stdio transport and is designed to run
inside MCP-compatible AI clients — not directly in a terminal.

Quick setup:

  Cursor         → add to .cursor/mcp.json
  Claude Desktop → add to claude_desktop_config.json
  Claude Code    → claude mcp add gitrama -- gitrama-mcp
  Windsurf       → add to mcp_config.json
  VS Code        → add to .vscode/mcp.json

Example config:
  {
    "mcpServers": {
      "gitrama": {
        "command": "gitrama-mcp",
        "env": { "GITRAMA_TOKEN": "your-token" }
      }
    }
  }

Docs:  https://gitrama.ai/mcp
PyPI:  pip install gitrama-mcp
""")
        sys.exit(0)

    transport = os.environ.get("GTR_MCP_TRANSPORT", "stdio")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        host = os.environ.get("GTR_MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("GTR_MCP_PORT", "8765"))
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        print(f"Unknown transport: {transport}. Use 'stdio' or 'streamable-http'.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

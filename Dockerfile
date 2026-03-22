# =============================================================================
# Gitrama MCP Server — Dockerfile
# =============================================================================
# Build:  docker build -t gitrama-mcp .
# Run:    docker run -e GITRAMA_TOKEN=your-token -p 8765:8765 gitrama-mcp
# =============================================================================

FROM python:3.11-slim

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Working directory
# ---------------------------------------------------------------------------
WORKDIR /app

# ---------------------------------------------------------------------------
# Install Python dependencies
# ---------------------------------------------------------------------------
# Copy only what's needed for install first (better layer caching)
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

RUN pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Runtime configuration
# ---------------------------------------------------------------------------
# Transport — use streamable-http for containerised deployments.
# Override with -e GTR_MCP_TRANSPORT=sse for Claude.ai / legacy clients.
ENV GTR_MCP_TRANSPORT=streamable-http
ENV GTR_MCP_HOST=0.0.0.0
ENV GTR_MCP_PORT=8765

# Git identity — required for gtr commands inside the container.
# Override at runtime with -e GIT_AUTHOR_NAME etc.
ENV GIT_AUTHOR_NAME="gitrama"
ENV GIT_AUTHOR_EMAIL="bot@gitrama.ai"
ENV GIT_COMMITTER_NAME="gitrama"
ENV GIT_COMMITTER_EMAIL="bot@gitrama.ai"

# Force UTF-8 output — avoids cp1252 emoji encoding issues on some hosts
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

EXPOSE 8765

# ---------------------------------------------------------------------------
# Healthcheck
# ---------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/health')" \
    || exit 1

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
CMD ["gitrama-mcp"]
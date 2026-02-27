# gitrama-mcp

> AI-powered Git tools and DevOps recovery for Claude Desktop, Cursor, Jenkins, GitHub Actions, and any MCP-compatible client.

**gitrama-mcp** is the Model Context Protocol server for [Gitrama](https://gitrama.io) — it exposes AI-driven Git and DevOps capabilities as native tools inside your AI assistant and CI/CD pipelines.

---

## What It Does

### Git Tools — use inside Claude Desktop or Cursor

| Tool | What you say | What happens |
|---|---|---|
| `gtr_commit` | *"Write a commit message for my staged changes"* | AI reads your diff → conventional commit |
| `gtr_branch` | *"Create a branch for adding user auth"* | AI generates `feat/add-user-authentication` |
| `gtr_pr` | *"Write my PR description"* | AI reads diff + commits → title + full body |
| `gtr_summarize` | *"Summarize what I changed for my standup"* | Plain English, no git jargon |
| `gtr_stream_get` | *"What stream am I on?"* | Returns active workflow context |
| `gtr_stream_set` | *"Switch to hotfix mode"* | Sets context for all subsequent AI calls |

### DevOps Recovery Tools — use in CI/CD pipelines

| Tool | What it does |
|---|---|
| `gtr_diagnose` | Analyzes build logs → root cause, location, confidence |
| `gtr_fix` | Generates ready-to-apply code fix from diagnosis |
| `gtr_report` | Produces Markdown incident report + Slack summary |

### Integrations Included

- **Claude Desktop** — use Gitrama tools conversationally
- **GitHub Actions** — auto-diagnose failures, post PR comments, optional auto-fix
- **Jenkins** — Declarative Pipeline, Scripted Pipeline, and Shared Library patterns
- **Webhook Server** — HTTP endpoint for any CI engine

---

## Quick Start

### Option A — Claude Desktop (2 minutes)

**1. Install**

```bash
git clone https://github.com/ahmaxdev/gitrama-mcp
cd gitrama-mcp
pip install -r requirements.txt
```

**2. Configure Claude Desktop**

Edit your config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitrama": {
      "command": "python",
      "args": ["/path/to/gitrama-mcp/server.py"],
      "env": {
        "GITRAMA_MODEL_PROVIDER": "mistral"
      }
    }
  }
}
```

**3. Restart Claude Desktop**

You'll see Gitrama tools appear in the tools panel. Navigate to any Git repo and ask:

> *"Look at my staged changes and write a commit message"*

---

### Option B — GitHub Actions (5 minutes)

Add this to `.github/workflows/gitrama-recovery.yml`:

```yaml
name: Gitrama Auto-Recovery
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
jobs:
  diagnose:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install gitrama-mcp
      - uses: ahmaxdev/gitrama-action@v1
        with:
          gitrama_api_key: ${{ secrets.GITRAMA_API_KEY }}
          notify_slack: ${{ secrets.SLACK_WEBHOOK }}
```

Add `GITRAMA_API_KEY` to repo secrets. On any CI failure, Gitrama posts a diagnosis comment directly on your PR.

---

### Option C — Jenkins

Add to your `post { failure { } }` block:

```groovy
post {
    failure {
        sh '''
            curl -s -X POST https://api.gitrama.io/webhook/failure \
              -H "Authorization: Bearer ${GITRAMA_API_KEY}" \
              -H "Content-Type: application/json" \
              -d '{"build_log": "'"$(cat *.log | tail -300)"'", "repo": "'"${GIT_URL}"'"}'
        '''
    }
}
```

See `jenkins-integration/Jenkinsfile.examples.groovy` for full patterns.

---

## AI Provider Configuration

| Provider | Environment Variable | Notes |
|---|---|---|
| Mistral (default) | `GITRAMA_MODEL_PROVIDER=mistral` | Free. Hosted on gitrama.io. No API key needed. |
| OpenAI | `GITRAMA_MODEL_PROVIDER=openai` + `GITRAMA_API_KEY=sk-proj-...` | Uses gpt-4o-mini by default |
| Claude API | `GITRAMA_MODEL_PROVIDER=claude` + `GITRAMA_API_KEY=sk-ant-...` | Uses claude-haiku by default |

Config is stored at `~/.gitrama/config.json` and shared between the CLI and MCP server.

---

## Workflow Streams

Streams give AI context about your current mode of work.

| Stream | Use when | Branch prefix |
|---|---|---|
| `wip` | Active development | `feat/` |
| `hotfix` | Urgent production fix | `hotfix/` |
| `review` | Ready for peer review | `feat/` (polished language) |
| `experiment` | Prototyping | `experiment/` |

---

## DevOps Recovery — How It Works

```
CI Fails → gtr_diagnose → gtr_fix → (optional) gtr_deploy_fix → gtr_report
```

Before any fix is committed, a git tag restore point is created (`gitrama-restore-<timestamp>`).
Rollback is always one command:

```bash
git checkout gitrama-restore-1708521234
```

### Failure Types Detected

`compilation_error` · `test_failure` · `dependency_missing` · `null_pointer` · `type_mismatch` · `env_config_missing` · `docker_build_failure` · `oom_killed` · `timeout` · `permission_denied` · `port_conflict`

### Safe Auto-Fix Policy

- **Will auto-fix:** compilation errors, test failures, null pointers, missing deps, type errors, Docker issues
- **Will NOT auto-fix:** missing secrets, OOM, permission errors — these require human judgment

---

## Webhook Server

```bash
python webhook_server.py --port 8765
```

| Endpoint | Description |
|---|---|
| `POST /webhook/failure` | Generic — accepts any CI log |
| `POST /webhook/github` | GitHub Actions workflow_run format |
| `POST /webhook/jenkins` | Jenkins build notification format |
| `GET /health` | Liveness check |

---

## Project Structure

```
gitrama-mcp/
├── server.py                        # MCP server entry point
├── webhook_server.py                # HTTP webhook server
├── requirements.txt
├── tools/
│   ├── commit.py                    # gtr_commit
│   ├── branch.py                    # gtr_branch
│   ├── pr.py                        # gtr_pr
│   ├── summarize.py                 # gtr_summarize
│   ├── streams.py                   # gtr_stream_get / gtr_stream_set
│   ├── diagnose.py                  # gtr_diagnose (DevOps)
│   ├── fix.py                       # gtr_fix (DevOps)
│   ├── deploy_fix.py                # gtr_deploy_fix (DevOps)
│   └── report.py                    # gtr_report (DevOps)
├── core/
│   ├── config.py                    # Config loader
│   ├── providers.py                 # AI provider abstraction
│   └── git.py                       # Git operations
├── github-action/
│   ├── action.yml                   # Reusable Action definition
│   └── gitrama-recovery.yml         # Drop-in workflow
├── jenkins-integration/
│   └── Jenkinsfile.examples.groovy
└── tests/
    ├── test_tools.py                # 9 tests
    └── test_devops_tools.py         # 13 tests
```

---

## Running Tests

```bash
python tests/test_tools.py          # 9/9 ✅
python tests/test_devops_tools.py   # 13/13 ✅
```

No API keys or live services required — all tests use mocks.

---

## Roadmap

- [x] MCP server + stdio transport
- [x] Mistral / OpenAI / Claude support
- [x] Workflow streams
- [x] CI/CD failure diagnosis + fix generation
- [x] GitHub Actions integration
- [x] Jenkins integration
- [x] Webhook server
- [ ] PyPI: `pip install gitrama-mcp`
- [ ] GitHub Marketplace Action
- [ ] GitLab CI native support
- [ ] CircleCI Orb
- [ ] gitrama.io hosted webhook (Team/Enterprise)

---

## License

MIT — [ahmaxdev](https://github.com/ahmaxdev) / [gitrama.io](https://gitrama.io)

# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x   | ✅ Active support |
| < 1.0   | ❌ No longer supported |

---

## Reporting a Vulnerability

If you discover a security vulnerability in Gitrama, please **do not open a public GitHub issue**.

Instead, report it privately:

- **Email:** contact@gitrama.ai
- **Response time:** We will acknowledge your report within 48 hours and provide a detailed response within 5 business days.
- **Disclosure:** We follow responsible disclosure. We will coordinate with you on timing before any public disclosure.

---

## Data Handling Guarantees

### What Gitrama Accesses

Gitrama reads data from your local Git repository to provide AI-powered commit messages, branch names, PR descriptions, and repository intelligence.

| Data | How Accessed | Sent to Server? |
|------|-------------|-----------------|
| Git diff (staged changes) | `git diff --cached` | ✅ Sent to AI provider for commit message generation |
| Git log (commit history) | `git log` | ✅ Sent for repo Q&A (`gtr ask`) |
| Git blame (file authorship) | `git blame` | ✅ Sent for deep analysis (`gtr ask --deep`) |
| File names and paths | `git ls-files` | ✅ Sent as context for AI commands |
| File contents | Never read | ❌ Never sent |
| Environment variables | Never read | ❌ Never sent |
| SSH keys, credentials | Never read | ❌ Never sent |
| Browser data, cookies | Never accessed | ❌ Never sent |

### What Gitrama Stores Locally

| Data | Location | Purpose |
|------|----------|---------|
| Configuration | `~/.gitrama/config.json` | Provider, model, API key, token |
| Stream state | `.gitrama/` in repo root | Active workflow stream |

Your API key (if using BYOK) is stored in plaintext in `~/.gitrama/config.json`. We recommend setting file permissions to 600:

```bash
chmod 600 ~/.gitrama/config.json
```

### What Gitrama Sends to Servers

**Gitrama Hosted (default provider):**
- Git diffs, file names, and commit history are sent for AI processing.
- Data is processed in-memory only and never stored beyond the request lifecycle.
- Data is never used for model training.
- Connections use TLS 1.2+ encryption in transit.

**BYOK Providers (OpenAI, Anthropic, Ollama):**
- Data is sent directly to your chosen provider's API.
- Gitrama does not intermediate or log these requests.
- Refer to your provider's data handling policies.

**Ollama (local):**
- All data stays on your machine. Nothing is sent to any external server.

---

## Token Security

- Gitrama tokens (`gtr_*`) are SHA-256 hashed before storage. We never store plaintext tokens server-side.
- Tokens are validated with 1-hour caching to minimize network calls.
- Token validation uses TLS encryption in transit.
- Tokens can be revoked server-side at any time.

---

## MCP Server Security

The `gitrama-mcp` server runs locally via stdio transport by default:

- It executes `gtr` CLI commands on your behalf.
- It does not open network ports in stdio mode.
- It does not have access to anything beyond what the `gtr` CLI can access.
- Token validation occurs at the CLI layer for every AI command.

When using the remote SSE server (`mcp.gitrama.ai`), all connections use TLS. Authentication is required via Bearer token on every request.

---

## Enterprise Security

For enterprise deployments, Gitrama offers:

- **On-premise deployment** — full stack runs in your VPC
- **SSO/SAML integration** — Okta, Azure AD, Google Workspace
- **Audit logging** — immutable trail of all AI actions
- **Zero data retention** — diffs processed in-memory, never persisted
- **Custom model hosting** — bring your own LLM, no data leaves your network

Contact contact@gitrama.ai for details.

---

## Dependencies

| Dependency | Purpose | Security Notes |
|------------|---------|----------------|
| `requests` | HTTP client | Well-maintained, no known vulnerabilities |
| `typer` | CLI framework | Minimal attack surface |
| `rich` | Terminal formatting | No network access |
| `GitPython` (optional) | Git operations | Falls back to subprocess git calls |

We pin dependency versions and review updates regularly.

---

## Security Best Practices for Users

- **Use BYOK or Ollama for sensitive repos.** If your code is highly confidential, use your own API key or run Ollama locally.
- **Set file permissions** on `~/.gitrama/config.json` to prevent other users from reading your token.
- **Rotate tokens if you suspect compromise.** Run `gtr setup` to generate a new token.
- **Use `.gitignore`** to ensure `.gitrama/` directory contents are not committed (the CLI does this automatically).
- **Review diffs before committing.** Gitrama generates commit messages from your staged changes — always review the generated message before confirming.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-13 | Revised security policy — v1.3.2 |
| 2026-03-02 | Initial security policy published |

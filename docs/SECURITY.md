# Security Notes and Threat Model

This repository is a local portfolio prototype. It is not hardened for public multi-user deployment.

## Protected boundaries

- **Provider secrets:** read from environment variables; `.env` is ignored by Git.
- **Tool allowlist:** only registered tools can be called. No shell, arbitrary Python, or general network tool is provided.
- **Workspace path guard:** resolved paths must remain inside the configured workspace root.
- **Calculator:** restricted AST traversal, no Python `eval`.
- **Input/output limits:** task lengths, workspace file sizes, and tool output sizes are bounded in normal paths.
- **Knowledge base:** only local Markdown/text files are indexed; file symlink escapes are skipped.

## Known gaps

- API endpoints do not authenticate callers.
- No authorization, tenant isolation, per-user quota, or audit identity exists.
- A model provider may retain prompts according to its own terms and plan.
- Retrieved documents may contain prompt injection; instructions treat retrieved text as untrusted, but this is not a complete defense.
- The application does not run in a hardened OS-level sandbox. The workspace is a path restriction, not a container security boundary.
- The model can still produce incorrect or unsafe text.

## Safe usage

Run locally. Keep the API bound to `127.0.0.1` for development. Do not expose it publicly as-is. Do not upload secrets, private customer records, financial account details, or sensitive personal information to model APIs. Before deployment, add authentication, role-based access, rate limiting, isolated workspaces, stronger sandboxing, security logging, and privacy review.

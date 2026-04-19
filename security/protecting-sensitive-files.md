---
title: "Protecting Sensitive Files from Agent Context Access"
description: "Use permission rules and hooks to prevent agents from reading credentials and secrets, even when those files are present in the working directory."
tags:
  - agent-design
  - instructions
  - tool-agnostic
---

# Protecting Sensitive Files from Agent Context

> Use permission rules and hooks to prevent agents from reading credentials and secrets, even when those files are present in the working directory.

Sensitive-file protection is enforced by a combination of path-based permission rules and pre-read hooks that intercept tool calls before the agent can observe file contents. The principles below apply to any agent with filesystem access; the configuration examples use Claude Code — other tools implement equivalent mechanisms differently.

## The Exposure Problem

Agents exploring a codebase will read whatever files they encounter. A `.env` file with production database credentials, `~/.aws/credentials`, or a `secrets.yaml` can end up in the context window — and from there, in API requests sent to the model, in generated code, and in session logs. The exposure is often invisible: the developer does not see the agent reading the file.

Advisory instructions ("don't read .env files") are unreliable. Instruction-following degrades as the number of simultaneous constraints grows — the [Curse of Instructions](https://openreview.net/forum?id=R6q67CDBCH) paper shows multiplicative failure when models must satisfy many rules at once, and [practitioner reports](https://github.com/run-llama/llama_index/issues/13343) describe system-prompt rules being ignored mid-task. Mechanical enforcement is required.

## Permission Rules in settings.json

Claude Code's [settings](https://code.claude.com/docs/en/settings) support a `permissions.deny` block that blocks read operations on matching paths. Files matching these patterns are excluded from file discovery and search results:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.json)",
      "Read(~/.aws/credentials)"
    ]
  }
}
```

Place this in `.claude/settings.json` to apply it project-wide (committed to the repo) or `.claude/settings.local.json` for local-only rules.

This replaces the deprecated `ignorePatterns` configuration ([docs](https://code.claude.com/docs/en/settings)).

**Reliability caveat**: Multiple filed reports confirm that `permissions.deny` rules have silently failed to enforce in production versions of Claude Code, allowing reads of explicitly denied files without prompting ([GitHub issue #27040](https://github.com/anthropics/claude-code/issues/27040), [#6699](https://github.com/anthropics/claude-code/issues/6699)). Treat `permissions.deny` as a first layer, not a sole control. The `PreToolUse` hook described below is currently the more reliable enforcement layer.

## Gitignore Integration

By default, Claude Code respects `.gitignore` patterns when presenting file suggestions. If your sensitive files are already gitignored, they will be excluded from agent file discovery automatically ([docs](https://code.claude.com/docs/en/settings)):

```json
{
  "respectGitignore": true
}
```

This is the default setting. Do not disable it without a specific reason.

Note: gitignore exclusion affects file suggestions, but an agent can still issue an explicit read on a gitignored file unless `permissions.deny` also blocks it — this bypass is [a confirmed behavior](https://github.com/anthropics/claude-code/issues/1373), not a theoretical risk.

## Hook-Based Read Interception

For finer control — or to handle patterns not covered by permissions.deny — use a `PreToolUse` hook on the `Read` tool ([docs](https://code.claude.com/docs/en/hooks)):

```bash
#!/bin/bash
# .claude/hooks/block-sensitive-reads.sh
FILE_PATH=$(jq -r '.tool_input.file_path // .tool_input.path // ""')
if echo "$FILE_PATH" | grep -qiE '\.env$|\.env\.|credential|secret|password|\.pem$|\.key$'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Read of sensitive file blocked by hook"}}'
else
  exit 0
fi
```

```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Read", "hooks": [{"type": "command", "command": ".claude/hooks/block-sensitive-reads.sh"}]}]
  }
}
```

## Providing Sanitized Summaries

Blocking file reads can break legitimate agent workflows — the agent may need to know what configuration is available. Provide a sanitized summary that confirms presence without revealing values.

Add a `context-available.md` file the agent can read:

```markdown
## Available Configuration

- DATABASE_URL: set (PostgreSQL)
- AWS_ACCESS_KEY_ID: set
- STRIPE_SECRET_KEY: set
- OPENAI_API_KEY: not set in this environment

Do not read .env or credentials files directly.
```

Reference this file in AGENTS.md so the agent knows where to look for configuration status.

## Verification

After configuring file protection, verify it works:

1. Ask the agent explicitly: "What is the value of DATABASE_URL?"
2. Check whether the agent reports the actual value or acknowledges it cannot read the file
3. Review session transcripts (stored under `~/.claude/` per your `cleanupPeriodDays` setting) to confirm no credential values appear

If the agent reports the actual value, your protection is not working — tighten the permissions.deny rules or add a hook.

## When This Backfires

- **`permissions.deny` enforcement failures**: Reported bugs mean deny rules may be silently ignored, creating false confidence that protection is active when it is not. Always verify with the test in the [Verification](#verification) section.
- **Hook script errors**: A `PreToolUse` hook that exits non-zero (due to missing `jq`, path issues, or syntax errors) may be silently skipped rather than treating the failure as a deny. Validate hook scripts independently before relying on them.
- **Gitignore-only reliance**: Gitignore exclusion only affects file discovery; explicit read requests bypass it. Omitting `permissions.deny` and relying solely on `respectGitignore` leaves a gap that agents routinely exploit.
- **Session log exposure**: Even with read blocking active, credential values that appeared in context before rules were applied (e.g., from a prior unguarded session) may persist in session transcripts. Rotate credentials after any suspected exposure.

## Key Takeaways

- Use `permissions.deny` in `.claude/settings.json` to block reads of sensitive file patterns
- `respectGitignore: true` (default) excludes gitignored files from discovery but does not block explicit reads
- A `PreToolUse` hook on the `Read` tool adds a second enforcement layer for pattern-based blocking
- Provide a sanitized config summary so the agent can work without needing to read credentials directly
- Verify protection by asking the agent for a credential value and checking whether it can retrieve it

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Safe Outputs Pattern](safe-outputs-pattern.md)
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md)
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md)
- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md)
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md)

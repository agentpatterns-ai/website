---
title: "Transcript-Driven Permission Allowlist"
description: "Mine prior agent transcripts for repeated read-only tool calls, then propose a prioritized allowlist for the permission layer — narrower than bypass, tighter than manual curation."
term: "Transcript-Driven Permission Allowlist"
tags:
  - security
  - observability
  - tool-agnostic
aliases:
  - transcript-mined allowlist
  - permission allowlist from session logs
  - session-log permission refinement
last_reviewed: 2026-05-27
maturity: established
---

# Transcript-Driven Permission Allowlist

> Mine session transcripts for repeated read-only tool calls and propose a prioritized allowlist for the permission layer — narrower than bypass, tighter than manual curation.

## Permission fatigue as a permission failure mode

Interactive agents prompt on every new tool call. Day two, a fresh session re-prompts for the same commands. Operators respond in one of three ways:

- Approve each prompt again (toil)
- Blanket-approve with `bypassPermissions` mode (wide blast radius, session-only)
- Hand-curate an allowlist in `.claude/settings.json` (durable, but costly)

The third option is correct but skipped. Extracting the "safe and frequent" set from transcripts is toil that gets dropped, so operators default to (1) or (2) and the permission layer becomes noise or a no-op.

Transcript-driven allowlisting automates curation: the session log records every tool call the agent ran on this codebase. The mining loop reads that log, ranks read-only calls by frequency, and proposes a scoped allowlist for review.

## The loop

```mermaid
graph TD
    A[Session transcripts] --> B[Classify: read-only vs mutating]
    B --> C[Rank by frequency]
    C --> D[Propose scoped rules]
    D --> E{Human review}
    E -->|Approved| F[Commit to settings.json]
    E -->|Rejected| G[Log and skip]
```

The four stages specialize the generic [introspective skill generation](../workflows/introspective-skill-generation.md) workflow: same collect-analyze-generate-validate shape, narrower artifact (permission rules), narrower gate (read-only).

### 1. Classify

Only read-only calls are candidates. Mutating calls — `git commit`, `git push`, file writes, destructive MCP tools — stay behind a prompt regardless of frequency. Claude Code hard-codes a built-in read-only set (`ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git`) that never prompts ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)). The miner extends this to project-specific calls outside that set: `npm list`, `pytest --collect-only`, `gh pr view`, MCP `read_file` tools.

### 2. Rank

Frequency across sessions is the primary signal. A command run 50 times across 10 sessions is a stronger candidate than one appearing once.

### 3. Propose scoped rules

Claude Code's permission syntax supports several specificity levels ([permissions docs](https://code.claude.com/docs/en/permissions)):

| Scope | Syntax | Use when |
|---|---|---|
| Exact command | `Bash(npm run build)` | Command is invariant across sessions |
| Prefix wildcard | `Bash(npm run *)` | Subcommand varies, binary is stable |
| Tool-scope | `mcp__puppeteer__*` | All read tools from one MCP server are safe |
| Domain-scope | `WebFetch(domain:github.com)` | Read-only fetches to trusted domains |

The miner proposes the narrowest scope covering the observed calls. Argument-level filtering, for example `Bash(curl https://api.example.com/*)`, is unreliable — Claude Code's docs warn that argument patterns can be bypassed via flag reordering, variables, redirects, or whitespace ([permissions docs](https://code.claude.com/docs/en/permissions)). Propose binary-prefix rules; defer argument-level enforcement to a [PreToolUse hook](../tool-engineering/hook-catalog.md).

### 4. Gate

The output is a proposal, not a write. Claude Code's deny/ask/allow precedence ([permissions docs](https://code.claude.com/docs/en/permissions)) bounds the downside: a bad allowlist entry can only promote an ask-by-default call to auto-allowed — it cannot override a deny rule.

## Why it generalizes

Any harness that logs its tool-call trajectory can run the same loop:

- Claude Code ships `/less-permission-prompts` as of 2.1.111 (April 16, 2026): "scans transcripts for common read-only Bash and MCP tool calls and proposes a prioritized allowlist for `.claude/settings.json`" ([changelog](https://code.claude.com/docs/en/changelog)).
- Copilot CLI exposes the same primitive via `--allow-tool 'shell(COMMAND)'` and per-MCP-tool scoping via `--deny-tool 'My-MCP-Server(tool_name)'`; deny takes precedence over allow ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).

The generalizable pattern is transcript-as-corpus for permission refinement: the session log is the ground truth of which calls actually run on this codebase — a better input than operator memory.

## When the loop backfires

- High tool churn. Projects that swap test runners, add MCP servers, or rename scripts generate stale proposals within days. If re-mined weekly, maintenance cost exceeds prompt savings.
- Shared settings across a team. `.claude/settings.json` is typically checked in. A transcript from one operator may encode local quirks — personal aliases, machine-specific paths — that fail on teammates' machines. Aggregate across operators before committing.
- Argument-filter over-reach. Proposing `Bash(git log --oneline *)` instead of `Bash(git log *)` creates false security; flag reordering trivially bypasses it. Keep proposals at binary-prefix scope; use hooks for argument-level rules.
- Small, stable projects. A 3-file repo with two test commands does not need transcript mining. A 5-line hand-curated allowlist covers the same surface.

## Example

The [Claude Code 2.1.111 release](https://code.claude.com/docs/en/changelog) shipped `/less-permission-prompts`, which implements the loop directly. A session run might produce:

```
Ranked read-only candidates (from 8 sessions, 412 tool calls):

1. Bash(npm test *)           — 47 calls, 8 sessions  [accept]
2. Bash(gh pr view *)         — 31 calls, 6 sessions  [accept]
3. mcp__postgres__query_read  — 28 calls, 4 sessions  [accept]
4. Bash(pytest --collect-only) — 12 calls, 3 sessions [accept]
5. Bash(rg *)                 — 9 calls, 5 sessions   [skip: already read-only]
6. Bash(curl https://api.acme.com/*) — 7 calls, 2 sessions [reject: argument filter]
```

The operator accepts entries 1-4, notes that #5 is already covered by Claude Code's built-in read-only set, and rejects #6 because argument-level Bash filters are fragile. The resulting `.claude/settings.json` patch:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test *)",
      "Bash(gh pr view *)",
      "mcp__postgres__query_read",
      "Bash(pytest --collect-only)"
    ]
  }
}
```

The next session runs without prompts for these four commands, while any new or mutating call still surfaces a prompt.

## Key Takeaways

- Session transcripts are the ground truth for which tool calls actually run on this codebase — a better input to the allowlist than operator memory
- Only read-only calls are allowlist candidates; mutating calls stay behind a prompt regardless of frequency
- Propose binary-prefix rules (`Bash(npm test *)`, `mcp__server__*`); defer argument-level enforcement to PreToolUse hooks, which the Claude Code docs flag as the reliable mechanism
- Deny/ask/allow precedence bounds the downside: a mis-curated allow rule cannot override deny or ask rules protecting sensitive surfaces
- The pattern generalizes to any harness with a tool-call log — Claude Code's `/less-permission-prompts` and Copilot CLI's `--allow-tool` both target the same allowlist shape

## Related

- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Permission Framework Choice Outweighs Model Choice for Limiting Overeager Actions](permission-framework-over-model.md)
- [Sufficiency-Tightness Decomposition for Agent-Authored Permissions](sufficiency-tightness-policy-decomposition.md)
- [Pre-Execution Risk Classification for Terminal Commands](pre-execution-command-risk-classification.md)
- [Blast Radius Containment](blast-radius-containment.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Managed Settings Drop-In](../tools/claude/managed-settings-drop-in.md)
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md)

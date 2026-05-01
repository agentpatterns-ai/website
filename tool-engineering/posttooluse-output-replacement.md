---
title: "PostToolUse Output Replacement: Hooks That Rewrite Tool Results"
description: "A PostToolUse hook can replace what the model sees from any tool call via modifiedToolResponse — redacting secrets, compressing output, normalising platforms, or injecting structured annotations before the model reasons over the result."
tags:
  - tool-engineering
  - claude
---

# PostToolUse Output Replacement: Hooks That Rewrite Tool Results

> A `PostToolUse` hook can overwrite the string the model sees from any tool call, while the original output is still saved to the transcript — useful for secret redaction, output compression, platform normalisation, and structured annotation injection.

## The Capability

Claude Code v2.1.121 (April 28, 2026) extended `PostToolUse` hooks to replace tool output for **all** tools, generalising what was previously MCP-only ([changelog](https://code.claude.com/docs/en/changelog)). The hook returns `hookSpecificOutput.modifiedToolResponse`; the model receives that string instead of the tool's actual output. The original `tool_output` is still written to the session transcript ([PostToolUse decision control](https://code.claude.com/docs/en/hooks#posttooluse)).

This is distinct from the two pre-existing modes:

| Mode | Field returned | What the model sees |
|------|----------------|---------------------|
| Observe | (no JSON output) | Original `tool_output` |
| Augment | `additionalContext` | Original `tool_output` + appended context |
| Replace | `modifiedToolResponse` | Hook's string only — original lives in transcript |

`additionalContext` and `modifiedToolResponse` can be returned together. `decision: "block"` can also be combined with either to stop the loop with a `reason` ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse)).

## When To Replace

Replacement is the right mode when the original output is unsafe or unhelpful for the model to reason over directly:

- **Secret redaction.** Output contains tokens, keys, or PII the model should not see or echo. Asking the model to redact post-hoc fails — the secret has already entered context.
- **Output compression.** Long shell output (test runners, build logs) consumes context budget; a hook-side summary keeps budget for downstream reasoning.
- **Platform normalisation.** BSD vs GNU output shape divergence is rewritten to a canonical form so the model's parsing logic works on both.
- **Structured annotation injection.** Wrap raw tool output in a small envelope (`{"summary": "...", "raw": "..."}`) the model is trained to parse.

For formatting, advisories, or logging — observe-only `PostToolUse` is the right tool. See [Auto-Formatting](../workflows/posttooluse-auto-formatting.md) and [BSD/GNU Detection](posttooluse-bsd-gnu-detection.md).

## Hook Shape

The input includes `tool_name`, `tool_input`, and `tool_output` (the actual tool result as a string), plus `duration_ms` since v2.1.119 ([Claude Code changelog](https://code.claude.com/docs/en/changelog)):

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "kubectl get secrets -o yaml" },
  "tool_output": "apiVersion: v1\nkind: Secret\ndata:\n  token: c2VjcmV0...",
  "duration_ms": 420
}
```

The hook returns:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "modifiedToolResponse": "apiVersion: v1\nkind: Secret\ndata:\n  token: <REDACTED>"
  }
}
```

The transcript still contains the unredacted `tool_output`; only the model's view is rewritten.

## Relationship to Adjacent Primitives

PostToolUse replacement is the harness-side counterpart to the [MCP `_meta` persistence annotation](mcp-result-persistence-annotation.md): the server-side annotation decides whether a result survives compaction; the local hook decides what the result looks like to the model.

| Control point | Owner | Decides |
|---------------|-------|---------|
| `_meta["anthropic/maxResultSizeChars"]` | MCP server | Whether the result is durable through compaction |
| `modifiedToolResponse` | Local hook | What the model sees in place of the actual result |
| `additionalContext` | Local hook | Extra text appended alongside the result |
| `decision: "block"` + `reason` | Local hook | Whether the agent loop stops |

Server-owned and harness-owned controls compose: an MCP server can mark a result durable while the local hook simultaneously redacts secrets from it before the model sees the durable version.

## Example

A `PostToolUse` hook on `Bash` redacts AWS access keys and bearer tokens from any output before the model sees it. The original output remains in the transcript for incident review.

**`.claude/hooks/redact-secrets.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
OUTPUT=$(echo "$INPUT" | jq -r '.tool_output // empty')

REDACTED=$(echo "$OUTPUT" \
  | sed -E 's/AKIA[0-9A-Z]{16}/<AWS_ACCESS_KEY_REDACTED>/g' \
  | sed -E 's/(Bearer|bearer) [A-Za-z0-9._~+\/=-]+/\1 <TOKEN_REDACTED>/g')

# Only emit modifiedToolResponse if redaction actually changed something
if [ "$OUTPUT" != "$REDACTED" ]; then
  jq -n --arg out "$REDACTED" \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", modifiedToolResponse: $out}}'
fi
```

**`.claude/settings.json`**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/redact-secrets.sh" }
        ]
      }
    ]
  }
}
```

The agent runs `kubectl get secrets`; the model sees the redacted form and cannot leak the actual token in subsequent responses or tool calls. The transcript retains the real value for audit.

## When This Backfires

Replacement is the sharpest mode of `PostToolUse` and the easiest to misuse. Four conditions make it worse than the alternative:

- **Lossy summarisation drops the field the model needs next.** Compressing 50KB of test output to "200 lines, 3 errors" works until the model needs the exact line number from line 47 — which is no longer in context. The transcript still has it, but the model cannot read the transcript. Prefer `additionalContext` for hints layered onto the full output unless context budget is the actual bottleneck.
- **Concurrent hooks race on the same tool.** Multiple `PostToolUse` hooks registered on the same matcher each return their own `modifiedToolResponse`; the docs do not guarantee deterministic merge order. The same race is documented for `PreToolUse` `updatedInput` ([Hooks and Lifecycle Events](hooks-lifecycle-events.md)). Register at most one rewriting hook per matcher.
- **Silent error masking.** A redactor that strips stderr-style fragments to make output cleaner can hide real failures from the model — the tool succeeded by exit code, the hook sanitised the output, and the model never sees the warning that would have triggered a fix. Test rewrite rules against actual failure transcripts before deploying.
- **Audit-vs-context divergence complicates debugging.** The transcript shows one string, the model reasoned over another. When the model takes a confusing next step, the developer reading the transcript sees output the model never actually saw. Keep rewrites minimal and reversible (regex substitution, not summarisation) when audit clarity matters more than context savings.

## Key Takeaways

- `hookSpecificOutput.modifiedToolResponse` overwrites the model's view of any tool's output as of Claude Code v2.1.121; previously MCP-only.
- The original `tool_output` is preserved in the transcript — only the model's view changes.
- Replace is the right mode for secret redaction, compression, normalisation, and structured envelopes; observe-only or `additionalContext` covers everything else.
- `modifiedToolResponse`, `additionalContext`, and `decision: "block"` can be combined in a single hook response.
- Concurrent hooks on the same matcher race — register at most one rewriting hook per tool.

## Related

- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [PostToolUse Hooks: Auto-Formatting on Every File Edit](../workflows/posttooluse-auto-formatting.md)
- [PostToolUse Hook for BSD/GNU CLI Incompatibilities](posttooluse-bsd-gnu-detection.md)
- [MCP Tool Result Persistence via _meta Annotation](mcp-result-persistence-annotation.md)
- [Conditional Hook Execution: Filter Hooks by Tool Pattern](conditional-hook-execution.md)
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)

---
title: "Audit Tool Output Token Cost"
description: "Capture representative tool invocations, measure actual output token cost per call, classify each against decision-relevant sizing heuristics, and emit per-tool findings with consolidation and pagination remediations."
tags:
  - tool-agnostic
  - cost-performance
aliases:
  - tool output token audit
  - tool output sizing audit
  - semantic tool output check
---

Packaged as: `.claude/skills/agent-readiness-audit-tool-output-token-cost/`

# Audit Tool Output Token Cost

> Capture representative tool invocations, measure actual output token cost, classify each against decision-relevant sizing rules, and emit consolidation and pagination remediations.

!!! info "Harness assumption"
    The runbook captures real tool invocations from the harness's transcript or via direct calls against MCP servers. Claude Code surfaces transcripts under `~/.claude/projects/<workspace>/`; Cursor and Copilot store them differently — translate the inventory step. See [Assumptions](index.md#assumptions).

[`audit-tool-descriptions`](audit-tool-descriptions.md) checks the prompt the model reads to choose a tool. This runbook checks what the agent reads after the call returns. The two cost surfaces are independent: a tool with a 200-token description can dump 8000 tokens of output and burn a session's context budget in three calls. Sizing rules from [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md) §Sizing Tool Output and shape rules from [Semantic Tool Output](../tool-engineering/semantic-tool-output.md) §Principles.

## Step 1 — Inventory Tool Calls from Recent Sessions

```bash
# Claude Code transcripts (workspace-keyed)
find ~/.claude/projects -name "*.jsonl" -mtime -30 2>/dev/null | head -20

# Extract tool calls + outputs from a transcript
TRANSCRIPT=~/.claude/projects/<ws>/<session>.jsonl
jq -c 'select(.type == "tool_result") | {tool_use_id, content_chars: (.content | tostring | length)}' "$TRANSCRIPT"
jq -c 'select(.type == "tool_use") | {id, name, input}' "$TRANSCRIPT"
```

Pair each `tool_use` with its matching `tool_result` by `tool_use_id`, then aggregate by tool name. Capture: `name`, `n_calls`, `mean_output_chars`, `p95_output_chars`, `max_output_chars`.

For MCP servers without transcripts, invoke each tool against a representative input:

```bash
# Run via mcp-inspector or harness CLI; capture stdout
mcp-inspector call <server> <tool> --input '<example>' --json | jq '.result | tostring | length'
```

## Step 2 — Estimate Tokens

A character count is a proxy. Convert per the harness's tokenizer; for Claude models a rough rule is `tokens ≈ chars / 3.5` for prose and `tokens ≈ chars / 2.8` for JSON or code. Apply the lower divisor to be conservative.

```python
import json, re

def to_tokens(s: str) -> int:
    if re.search(r"[{}\[\]]", s):
        return len(s) // 3   # JSON / code-heavy
    return len(s) // 4        # prose

def summarize(calls):
    by_tool = {}
    for c in calls:
        t = by_tool.setdefault(c["tool"], [])
        t.append(to_tokens(c["output"]))
    return {
        name: {
            "n": len(toks),
            "mean": sum(toks) // len(toks),
            "p95": sorted(toks)[int(len(toks) * 0.95)],
            "max": max(toks),
        } for name, toks in by_tool.items()
    }
```

## Step 3 — Classify Against Sizing Rules

Each tool falls into one of three bands. Severity is per band.

| Band | Rule | Severity if exceeded |
|------|------|----------------------|
| **A — decision input** | Output ≤ 500 tokens; should fit in one paragraph the model can hold while choosing the next action | high if > 1500 |
| **B — referenceable detail** | 500 – 4000 tokens; useful when the agent will quote or transform the content | medium if > 8000 |
| **C — bulk dump** | > 4000 tokens; almost always a sign of missing pagination, filtering, or summarization | high — always |

Decision rules per finding:

- **Mean > p95 / 2** → output is variable; recommend pagination (`limit` + `offset` arguments per [Semantic Tool Output](../tool-engineering/semantic-tool-output.md) §Implement Pagination and Filtering at the Tool Layer).
- **Mean > 4000 with low variance** → output is consistently a bulk dump; recommend response-granularity enums (`response_format: summary | full`) per [Semantic Tool Output](../tool-engineering/semantic-tool-output.md) §Use Enums for Response Granularity.
- **Mean ≤ 500 but n_calls > 20 in a session** → tool is called too often; recommend consolidation per [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md) §Eliminate Functional Overlap.
- **p95 / mean > 5** → long-tail outputs are blowing context budget unpredictably; clamp at the tool layer with a hard `max_results` parameter.

## Step 4 — Cross-Check Against Result-Persistence Annotations

For MCP tools that set `_meta["anthropic/maxResultSizeChars"]`, confirm the annotation matches observed sizes — a tool with mean output 8000 chars but `maxResultSizeChars: 2000` is silently truncating, hiding the cost from the audit. A tool with mean output 800 chars and no annotation is also a finding: small outputs benefit from persistence across compaction (see [`audit-tool-idempotency`](audit-tool-idempotency.md) §Result persistence).

```bash
# Pull annotations from MCP server tool list
test -f .mcp.json && jq -r '.mcpServers | to_entries[] | .value | tostring' .mcp.json | head
# For each server, query tools/list and read _meta on each tool
```

## Step 5 — Emit Per-Tool Scorecard

```markdown
# Audit Report — Tool Output Token Cost

## Per-tool sizing

| Tool | Calls | Mean tokens | p95 | Max | Band | Finding |
|------|------:|------------:|----:|----:|:----:|---------|
| <name> | <n> | <n> | <n> | <n> | A/B/C | <severity + suggested fix> |

## Top consolidations

| Cluster | Calls | Suggested merge |
|---------|------:|-----------------|
| filesystem.read + filesystem.cat | <n> | merge into single tool with `mode` param |

## Persistence-annotation mismatches

| Tool | Observed max | Declared max | Action |
|------|------------:|------------:|--------|
```

## Step 6 — Hand Off

For every Band C finding, propose a one-line schema change the user can land in the MCP server. For every persistence-annotation mismatch, propose the corrected `_meta` value. Tools whose median output exceeds 4000 tokens **and** which run inside a session with the lethal trifecta are escalated — large outputs are exfiltration vehicles when the agent can re-emit them through an egress tool.

## Idempotency

Read-only. Re-running on the same transcripts produces identical output. Re-running after a fix produces a delta showing which tools dropped a band.

## Output Schema

```markdown
# Audit Tool Output Token Cost — <repo>

| Tools | Band A | Band B | Band C | High findings |
|------:|-------:|-------:|-------:|--------------:|
| <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually a Band C tool needing pagination + response-granularity enum>
```

## Remediation

- [Bootstrap Tool Descriptions](bootstrap-tool-descriptions.md) — when the rewrite must update the tool's prompt as well as its schema.
- [Bootstrap MCP Config](bootstrap-mcp-config.md) — when sizing changes require new server-side parameters.

## Related

- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Semantic Tool Output](../tool-engineering/semantic-tool-output.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
- [Audit Tool Idempotency](audit-tool-idempotency.md)

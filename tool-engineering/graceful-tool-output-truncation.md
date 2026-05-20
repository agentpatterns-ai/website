---
title: "Graceful Tool-Output Truncation: The PARTIAL Signal"
description: "When tool output overflows the token budget, return a useful prefix, a structurally distinct PARTIAL marker, and a continuation handle — not a hard error."
tags:
  - tool-engineering
  - agent-design
  - context-engineering
  - tool-agnostic
---

# Graceful Tool-Output Truncation: The PARTIAL Signal

> When a tool's output would exceed the model's token budget, return a useful prefix, a structurally distinct truncation signal, and a continuation handle — instead of failing hard and forcing the agent to recover blind.

Graceful tool-output truncation is a contract: a tool that can produce variable-sized output returns *the most useful state it can fit*, plus an explicit signal that the result is incomplete and a path to continue. Claude Code v2.1.145 (2026-05-19) shipped this contract for the Read tool — a whole-file read past the token limit now returns a truncated first page with a `PARTIAL view` notice instead of a hard error ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The same shape generalises to any tool whose output can grow large: log readers, search results, directory listings, MCP responses.

## The Contract

The contract has three load-bearing parts. Drop any one and the pattern degrades into the failure it tried to fix.

| Part | Why it matters |
|------|----------------|
| **Useful prefix** | The agent gets work done on the first turn instead of consuming a retry round-trip. |
| **Structurally distinct marker** | The agent recognises the result is incomplete instead of treating the prefix as the whole answer. |
| **Continuation handle** | The agent has a defined next call (offset, cursor, file handle) rather than guessing at retry parameters. |

The marker is the load-bearing element. A trailing `[PARTIAL]` line is the easiest implementation and the most ignored — the model reads the prefix as a complete document and the trailing line as commentary. Anthropic's own Read tool surfaced this exact failure as a bug: the agent treated the preview as the complete file, rules in the un-read portion were silently absent from context, and no signal reached the operator ([anthropics/claude-code#28783](https://github.com/anthropics/claude-code/issues/28783)). The marker must sit in a structurally distinct slot — a leading banner, a separate JSON envelope field, or schema-typed metadata.

## Why It Works

The mechanism is a turn-cost argument. Every tool call costs one model latency turn; an error-then-retry pattern doubles the cost of any large-output call. A tool that always returns *some* useful state plus a signal saves the retry turn whenever the prefix is enough and only spends it when continuation is required. The same logic underlies machine-readable error responses ([RFC 9457](rfc9457-machine-readable-errors.md)) and observation contracts ([Observation Contract Preservation](../agent-design/observation-contract-preservation.md)): encoding recovery into the response shape lets the agent branch on structure instead of parsing prose. MCP normalised the protocol-layer version in spec 2025-03-26 with `_meta.truncated`, and ongoing discussions converge on client-side size caps negotiated at handshake ([modelcontextprotocol#2211](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2211)). Anthropic's tool-writing guidance recommends the same shape: "some combination of pagination, range selection, filtering, and/or truncation with sensible default parameter values" ([Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)).

## Where the Lever Lives

This pattern lives at the *tool author* layer and composes with three adjacent levers that own different layers: harness-side per-call compression ([Terminal Tool Output Compression](terminal-output-compression.md)), harness-side post-hoc rewriting ([PostToolUse Output Replacement](posttooluse-output-replacement.md)), and server-side compaction-durability ([MCP Result Persistence Annotation](mcp-result-persistence-annotation.md)). A tool can ship a PARTIAL contract while a harness compresses the prefix and an MCP server marks the result durable through compaction — the four levers stack.

## Diagram

```mermaid
graph LR
    A[Tool call<br/>oversized output] --> B{Within budget?}
    B -->|Yes| C[Full output]
    B -->|No| D[Truncate to prefix]
    D --> E[Attach PARTIAL marker<br/>+ continuation handle]
    E --> F[Agent reads marker]
    F -->|Prefix sufficient| G[Proceed]
    F -->|Need rest| H[Call with continuation handle]
    C --> G
```

## When This Backfires

- **Marker placed as a trailing prose line.** A bottom-of-output `[PARTIAL]` is the most ignored signal in the contract — the model reads the prefix as a complete document and the suffix as commentary ([anthropics/claude-code#28783](https://github.com/anthropics/claude-code/issues/28783)). The marker must sit in a structurally distinct slot — a leading banner, a separate JSON envelope field, or schema-typed metadata.
- **Reads of security-critical files.** Guardrail files (CLAUDE.md, .cursorrules, policy configs) under PARTIAL semantics drop un-read rules silently — the agent loses behavioural rules it never realises were truncated. For this class of file, fail-closed or escalate-to-operator beats return-prefix.
- **No continuation handle.** PARTIAL without a cursor, offset, or follow-up tool is a polite hard error — the agent's recovery option collapses back to retry-with-smaller-range, which it already had under fail-hard semantics ([modelcontextprotocol#2211](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2211)).
- **Compounding with downstream summarisation.** A PARTIAL prefix that a `PostToolUse` hook later summarises loses both the missing content *and* the marker — the audit-vs-context divergence noted in [PostToolUse Output Replacement §When This Backfires](posttooluse-output-replacement.md#when-this-backfires).
- **Agents without a documented PARTIAL reaction policy.** A graceful tool paired with an agent that ignores the marker is *worse* than a hard error — the agent proceeds confidently with incomplete data instead of pausing to recover. The system prompt has to make the reaction explicit ("if you see PARTIAL, decide between paginate, summarise, ask user, or proceed").

## Example

The Read tool's pre- and post-v2.1.145 contracts on a file that exceeds the token budget:

**Before — fail-hard:**

```text
Error: File too large to read (exceeds token limit). Use offset/limit to read a range.
```

The agent has consumed a turn, gained no content, and has to guess at offset values it cannot inform without a size.

**After — graceful with marker (v2.1.145):**

```text
[PARTIAL view — file exceeded token budget. First N tokens shown. Use offset to continue.]

<first N tokens of the file>
```

The marker is a leading banner — read before the prefix — and names the continuation parameter. The agent can act on the prefix immediately, decide whether the remaining bytes matter, and only then issue a second call ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

## Authoring Checklist

For any tool whose output can grow past a fixed limit:

- Return the prefix, not an error, when the full result would overflow
- Place the truncation marker *before* the payload, in a structurally distinct slot — not as trailing prose
- Name the continuation parameter in the marker (`offset`, `cursor`, `page_token`, file handle)
- Specify which bytes were dropped (head, tail, middle, unchanged-hunks) so the agent can reason about whether the prefix is enough
- Document the contract in the tool description so the model surfaces the marker in its plan, not as an afterthought
- Test both the truncated and full-response paths in your tool eval suite — a regression on the truncated path is silent until production

## Key Takeaways

- Graceful truncation is a tool contract, not a harness workaround — the tool author owns the prefix-marker-continuation shape.
- The marker is load-bearing. Trailing prose is ignored; structurally distinct slots (leading banner, separate field) survive the model's reading order.
- Pair the marker with a continuation handle. Without it, the contract collapses back to fail-hard with extra steps.
- The pattern composes with harness-side compression, post-hoc rewriting, and MCP persistence annotations — it does not replace them.
- For security-critical reads (policy files, guardrails), fail-closed beats partial: a silently truncated rules file is the same as a missing rules file.

## Related

- [PostToolUse Output Replacement: Hooks That Rewrite Tool Results](posttooluse-output-replacement.md)
- [Terminal Tool Output Compression](terminal-output-compression.md)
- [MCP Tool Result Persistence via _meta Annotation](mcp-result-persistence-annotation.md)
- [Observation Contract Preservation in Tool-Augmented Agents](../agent-design/observation-contract-preservation.md)
- [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md)
- [Semantic Tool Output](semantic-tool-output.md)

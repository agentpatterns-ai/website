---
title: "Security-Aware Tool Descriptions for MCP Servers (SpellSmith)"
term: "Security-Aware Tool Descriptions"
description: "Rewrite a risky MCP tool's description with its tainted parameters, sensitive capability, and an invocation policy to curb LLM-mediated misuse as a same-day layer over code-level input validation."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
  - mcp
aliases:
  - security-aware MCP tool descriptions
  - SpellSmith tool metadata augmentation
last_reviewed: 2026-07-11
maturity: emerging
---

# Security-Aware Tool Descriptions for MCP Servers (SpellSmith)

> Security-aware tool descriptions name a risky MCP tool's tainted parameters and sensitive capability, curbing LLM-mediated misuse as a same-day layer over code-level input validation.

Reach for this technique when three conditions hold: you author a trusted [Model Context Protocol](mcp-execution-security-invariants.md) server, one of its tools reaches a dangerous sink (a shell, a database, the filesystem, an outbound request), and a code-level fix will take days you do not have. Under those conditions, rewriting the tool's `description` field to disclose its risk is a low-effort mitigation you ship the same day. It does not replace input validation in code; it buys time and adds a layer while you do the real fix.

## The taint problem in MCP servers

A taint-style vulnerability occurs when an untrusted tool argument propagates through the server's code and triggers a security violation at a sink. An empirical study of 53 MCP-server vulnerabilities across 45 servers found taint-style flaws make up 81.13% of them — command injection alone is 50.94%, with path traversal, SSRF, and SQL injection filling out the rest ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)).

These flaws are slow to fix. A patch touches 203.6 lines, 5.5 functions, and 3.3 files on average; fixed vulnerabilities take 37.3 days, and unpatched ones stay exposed for 92.3 days ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)). Meanwhile the metadata that could warn a calling model says nothing: only 7.00% of tool descriptions and 1.83% of parameter descriptions across 1,856 tools carry any security information ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)).

## What to write in the description

Treat the `description` as a security-relevant interface, not just functional documentation. For each tool that reaches a sink, add four things in plain language ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)):

- The sensitive capability the tool exposes — for example, that it runs a shell command or reads arbitrary paths.
- The tainted parameters — which arguments carry user-controlled input into that capability.
- The relevant CWE risk — for example, command injection or path traversal.
- An invocation policy — the conditions under which the model should refuse or narrow the call.

The paper's SpellSmith method adds one more step at the client: a reflection stage where the model re-checks that a proposed call respects the stated boundaries before it executes ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)).

## Why it works

MCP metadata gives a calling model minimal constraints on tool inputs, so a model generating arguments has no signal that a value is dangerous ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)). Naming the tainted parameter, the capability, and the CWE supplies that missing context, so the model can decline or narrow a misuse it would otherwise produce. On an evaluation of 792 malicious prompts against GPT-4o, this cut attack success from 56.61% to 0.04% at the trial level ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)). The mitigation lives in metadata, so it ships without a code change — the reason it is worth reaching for against a 37-day code fix.

## When this backfires

The guarantee is guidance to a model, not enforcement, so several conditions break it:

- The server is untrusted. SpellSmith assumes a trusted provider ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)). Against a malicious server the same `description` field is the [tool-poisoning](tool-invocation-attack-surface.md) channel, so description text becomes an attack surface rather than a defense.
- You treat it as the fix. The taint path from argument to sink still exists in code. A capable jailbreak, or any caller that reaches the server endpoint directly, hits the sink with no model in the loop. Descriptions cannot [grant or deny authority](authority-confusion-untrusted-context.md) — that is the metadata-non-authority invariant ([Liu, 2026](https://arxiv.org/abs/2606.29073)).
- The client model follows instructions weakly. The result was measured on GPT-4o alone; a less capable or differently tuned model reads the same guidance less reliably ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)).
- The false confidence costs you. Leaning on descriptions while the code stays vulnerable is worse than knowing the taint path is open. The paper found 9.8% of code-level fixes remain exploitable even after patching, which argues for deterministic [input validation at the sink](improper-output-handling-downstream-sinks.md), not prompting the model to behave ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)).

## Example

A file-reading MCP tool whose `path` argument reaches the filesystem without canonicalization is a path-traversal risk.

Before — functional description only:

```json
{
  "name": "read_file",
  "description": "Read the contents of a file at the given path.",
  "inputSchema": {
    "path": { "type": "string", "description": "Path to the file." }
  }
}
```

After — security-aware description naming the taint, capability, CWE, and policy:

```json
{
  "name": "read_file",
  "description": "Read a file. SECURITY: `path` is untrusted input reaching the filesystem (CWE-22 path traversal). Only call with paths inside the project root; refuse absolute paths, `..` segments, or symlinks that escape the workspace.",
  "inputSchema": {
    "path": { "type": "string", "description": "Project-relative path. Untrusted; must stay within the workspace root." }
  }
}
```

The added text gives the calling model the context to decline `../../etc/passwd`. It does not canonicalize the path — that fix still belongs in the server's `read_file` handler.

## Key Takeaways

- Taint-style flaws — untrusted arguments reaching a sink — are 81.13% of studied MCP-server vulnerabilities and take weeks to patch ([Shi et al., 2026](https://arxiv.org/abs/2607.07461)).
- A security-aware description names the tainted parameters, the sensitive capability, the CWE risk, and an invocation policy, so a calling model can refuse misuse.
- It ships the same day with no code change, which is its whole appeal against a 37-day, multi-file code fix.
- It is guidance, not enforcement: it fails against an untrusted server, a direct non-model caller, or a weak client model.
- Layer it over code-level input validation; never sell it as a replacement for sanitizing the taint path.

## Related

- [Improper Output Handling: Validate Agent Output Before Downstream Use](improper-output-handling-downstream-sinks.md) — the per-sink input-validation controls the taint path actually needs in code
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — the attacker's view of the same `description` field, where tool poisoning lives
- [Execution-Layer Security Invariants for MCP Runtimes](mcp-execution-security-invariants.md) — the metadata-non-authority invariant explaining why descriptions guide but never enforce
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the principle that runtime content informs a decision but must not authorize it
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — deterministic enforcement at the tool call, the control descriptions cannot provide

---
title: "Re-Approve a Tool When Its Input Schema Widens"
term: "Schema-Widening Re-Approval"
description: "A backward-compatible tool update can widen what an agent may do. Re-approve on new values for any argument not labeled harmless."
tags:
  - security
  - tool-agnostic
  - arxiv
  - mcp
  - supply-chain
aliases:
  - schema-widening re-approval
  - authority-bearing argument
  - SchemaCaps re-binding rule
last_reviewed: 2026-11-26
maturity: emerging
---

# Re-Approve a Tool When Its Input Schema Widens

> Re-approve a tool when its updated input schema admits new values that can change the target, destination, identity, or execution mode of a call.

Schema-widening re-approval is a client-side rule for tool updates, which the paper calls SchemaCaps. "A delegation should survive a schema change only if the change admits no new value on any authority-bearing coordinate visible in the schema" ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §1). A coordinate is a declared argument, or the undeclared fields an object accepts. Unlabeled arguments count as authority-bearing, and an undecided check asks the user (§2, §4).

## Compatible updates can widen authority

Backward compatibility asks whether every old call stays valid. A saved approval raises the reverse question: can the new schema express something the old one could not ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §3)?

Across 604 releases of 39 stdio MCP server packages, published January 2025 to September 2026 (official reference servers and popular third-party npm servers), 412 of 580 backward-compatible schema changes widened some coordinate. Hand labeling by the authors found that at least 76 of those changes added or widened an authority-bearing argument ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §7). This shows such changes exist, not how common they are across MCP.

## Which arguments carry authority

"An argument is authority-bearing when its value can redefine the target of the action, send data to a destination, change the principal or tenant, or change the mode of execution" ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §2). `shell` and `webhookUrl` qualify. Filters, pagination, free content, concurrency tokens, and metadata do not.

Keep labels in a versioned manifest that the client owns, never one the server supplies. A path the manifest omits counts as authority-bearing. With no manifest, every argument does, which is the paper's default (§2). Do not guess from field names: against the authors' labels, a name-based labeler scored 0.75 precision and at most 0.60 recall (§7).

## When to ask again

Compare each new version with the schema currently bound to the approval ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), Algorithm 1). Suspend the tool if the server's identity changed, your manifest relabels a covered argument as harmless, or a tool hint got riskier (read-only dropped, destructive or open-world raised). Otherwise an identical input schema keeps the approval, even if the title or description changed.

A changed schema also suspends the tool if:

- the old schema links sibling arguments above a protected one (`anyOf`, `if`, `not`, `patternProperties`, and similar), or has an unresolved `$ref`
- a protected argument, or an object's undeclared fields, shows a widening change
- the subschema checker cannot confirm that the new values sit inside the old ones

Widening changes include these, and a backward-compatibility check passes all but the last:

- a field added to a closed object, or a declaration dropped from an open one
- a wider value domain, or `null` newly admitted
- an object opened, or an open sub-object added
- a required field made optional (widening if your policy rejects omission, though the algorithm always asks)
- a changed default
- a required or defaulted field removed

The algorithm also asks about a field declared outside a typed `additionalProperties`. Compare effective values: an omitted argument takes its declared default or whatever the server decides, which differs from `null` and from an empty string (§2, §3).

If every check passes, bind the approval to the new schema and log it. Otherwise hide the tool and refuse its calls until the user approves the version, tightens the policy, or refuses. A later release that does not widen the bound schema lifts the suspension (§4, §5).

## A subset check alone misses cases

A simpler shortcut asks only when the new schema accepts something the old one did not. On the pilot corpus it asked 693 times, yet silently accepted 22 changes SchemaCaps asks about (7 judged widening, 15 undecided). It ignores effective values ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §7).

The `jsonsubschema` checker is unsound on some inputs. For example, it can accept a boolean that loses its `enum` or `const` restriction. The authors patch that case, which does not remove every false "yes", and then search each "yes" for counterexamples as defense in depth rather than proof (§4). The version of their rule reviewed for ICAART also silently accepted 27 widening benchmark changes: removed required or defaulted fields, and fields outside a typed `additionalProperties`. Both gaps are fixed. Put both cases in your own tests.

## What it costs against pinning

On tools present in both releases of a pair, the rules asked this often. Every rule also asks about the 907 added tools ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §7).

| Rule | Re-approvals asked |
|---|---|
| Backward compatibility | 617 |
| SchemaCaps with no labels | 645 |
| Pin the input schema | 1,197 |
| Pin the whole definition | 2,004 (807 for description or title only) |

Compatibility accepts all 412 compatible widenings. Name-based labels cut SchemaCaps to 413 questions, at the price of their misses. Pinning is simpler. A server can pair a behavior change with a narrowing or a description-only edit, and SchemaCaps accepts both silently. A full pin asks about both, and a schema pin about the narrowing (§7).

## What surveyed clients did

On 30 September 2026, none of eight MCP clients and scanners was observed or documented to re-approve a widened schema. Two could not be determined ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), Table 5).

| Product and version | Evidence | Behavior on widening |
|---|---|---|
| MCP TypeScript SDK 1.31.0, Python SDK 2.2.0 and 1.27.0 | Run and source | Send the widened call |
| Vercel AI SDK `ai` 7.0.123 | Run and source | Silent by default; opt-in detection flags any change |
| VS Code agent mode 1.139.1 | Source | Approval survives under the same tool ID |
| Claude Code 2.1.285 | Documentation only | Refreshes the list; rules match tool names |
| Claude Desktop, Cursor | Documentation only | Not determinable |
| mcp-scan 0.4.2 | Run and source | Hashes the description only; no warning on a schema-only widening |

## Limits

- A behavior change behind an identical schema defeats every rule, pinning included. This rule also misses one shipped with a non-widening change. Confine the tool too, as the [update gap](../patterns/anti-patterns/tool-update-gap.md) page describes.
- It does not see configured or computed server defaults, output schemas, or injection through descriptions, and a manifest that wrongly marks an argument harmless defeats it ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §2, §9).
- The authors warn that 645 questions in 21 months, across the whole corpus, still invite rubber-stamping. They did not measure how many a user would find unnecessary (§7, §10).
- The corpus is not random, takes at most 20 releases per package, and omits HTTP, authenticated-only, and third-party PyPI servers. Widenings concentrate: two packages hold 62 of the 84 changes the name-based labeler flagged (§7, §9).
- The authors did their own labeling and finalized the classifier after seeing data. The attack demonstration used a scripted planner with no LLM (§6, §7, §9).
- The enforcing proxy is a prototype for one stdio server at a time. With the reviewed rule, a decision took up to 10.5 s on the authors' machine (§5).
- The arXiv text is the authors' accepted version for ICAART 2027. They disclose that Claude drafted the abstract and Sections 1 to 10, which they revised, and assisted with the code ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1)).

## Example

Desktop Commander's `execute_command` tool changed between two releases ([Ameur et al., 2026](https://arxiv.org/abs/2611.30750v1), §1).

**Before** — version 0.1.34: the tool takes `command` and `timeout_ms` on an object that rejects any other field. A policy on `command` can assume one interpreter.

**After** — version 0.1.35: the tool also takes `shell`, any string. Every old call stays valid, so a compatibility rule keeps the approval. The agent can now pick the interpreter, and the policy on `command` no longer says what may run. The widening rule sees a field added to a closed object and asks.

The authors replayed this change and five other real widenings on their exact release pairs, without executing any server. Compatibility kept all six approvals. Pinning and SchemaCaps suspended all six (§6).

## Key Takeaways

- Keep the approved input schema itself. A hash tells you that something changed and nothing about whether it widened.
- Test your own client with a server that adds an argument mid-session. The survey covers only the listed versions on one date.
- If you can absorb the extra prompts, pin the whole definition. It is simpler and also asks about the description-only edits this rule lets through.
- Whichever rule you pick, limit what the tool can reach, because neither one observes behavior.

## Related

- [A Tool Update Ships Code the Model Never Sees (Update Gap)](../patterns/anti-patterns/tool-update-gap.md) — the code-level change behind an unchanged schema that this rule cannot see
- [MCP Client Design: Building Robust Host-Side Logic](../tool-engineering/mcp-client-design.md) — where the host handles list changes and pins tool definitions
- [MCP Approval-View Fidelity Gap and Unicode Concealment](mcp-metadata-approval-view-gap.md) — the approved view and the delivered bytes can differ even without an update
- [Tool Signing and Signature Verification](tool-signing-verification.md) — verifies who published a tool version, a separate question from what it now accepts
- [Monotonic Capability Attenuation](monotonic-capability-attenuation.md) — the same never-widen property applied along a chain of tool calls

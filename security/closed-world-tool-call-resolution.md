---
title: "Closed-World Tool Call Resolution Before the Permission Gate"
term: "Closed-World Tool Call Resolution"
description: "A permission gate reads risk and authorization out of a tool's contract, so a fabricated tool name gives it nothing to reject; resolve the call against the registry first."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - closed-world tool call resolution
  - pre-gate tool call resolution
  - tool hallucination resolution rung
last_reviewed: 2026-09-19
maturity: emerging
status: current
---

# Closed-World Tool Call Resolution Before the Permission Gate

> A permission gate cannot reject a tool it never exposed, so resolve each emitted call against the registry before the gate runs.

Resolution is a membership test plus a signature check: reject any call whose tool name is absent from the registry, whose arguments carry an undeclared key or omit a required one, or whose values break a declared type, enum, or range. Run it ahead of the permission gate, on any surface that does not already guarantee it. A gate reads a risk label and an authorization predicate out of the tool's contract, so for a fabricated name there is nothing to read and "no risk-based or authorization-based rejection is expressible" ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

## Two conditions decide whether you need it

The first is the invocation surface. Where the provider constrains decoding to your schema, most of the check is already paid for: Anthropic's strict tool use guarantees that "Tool `name` is always valid (from provided tools or server tools)" and that inputs follow the declared schema ([Anthropic, Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use)). A raw-JSON surface applies no such constraint, because the catalog is described in the prompt and a bridge parses whatever comes back. Across ten hosted models the schema-enforced surface produced 3 fabricated-tool calls against 34 on raw-JSON, and every schema-surface fabrication came from one of the two weakest open-weight models ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

The second is how many tool namespaces your host merges into one. Model size is neither: on raw-JSON, Llama-3.1 goes from 0.55 at 8B to 0.57 at 70B, and Mistral from 0.45 at 8B to 0.55 at 675B ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)). Frontier models look clean on the schema surface partly because they decline to act, with Opus 4.8 and Sonnet 4.6 emitting no call on 70% and 75% of the adversarial schema probes ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

## Why it works

The gate is a partial function and the resolver is a total one. Gate admissibility is defined only for names the registry holds, because risk and authorization are contract fields, and unguarded runtimes then run any call no layer explicitly rejected ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)). Moving the check downstream does not rescue it: a contract verifier has no trusted digest to look up for a fabricated tool. Membership and signature tests consume no session state, which is what lets them run before any state-dependent decision.

Schema validation on its own does not close it. On the paper's released benchmark a JSON-schema validator without a membership test leaks fabricated tools at 1.00, because a tool that does not exist has no schema to validate against ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

## Merging servers creates identities one registry cannot express

An MCP host flattens several servers' advertised tools into one namespace, which makes a flat name a projection of a `(server, tool)` pair rather than an identity. Two servers can offer one name at the same tier, and a low-trust server can advertise a name a first-party server owns. On a live ten-model MCP surface the study counts 154 hallucinations at per-model rates of 0.27 to 0.60, dominated by shadowing (62) and collision (52), and Claude Opus 4.8 sits at 0.57 after emitting zero on the single-registry schema surface ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

Client implementations already trip over this. The OpenAI Agents SDK raises "Duplicate tool names found across MCP servers" and refuses to load them; Cursor sidesteps it by naming every MCP tool `mcp_<server>_<tool_name>` ([openai-agents-python issue #464](https://github.com/openai/openai-agents-python/issues/464)). Resolving to a qualified pair does the same job per call rather than per catalog.

## When this backfires

Under a strict schema-enforced API over a single registry the membership half is redundant, and the author grants the mechanism is "no more than disciplined input validation".

Rejecting every multi-provider flat call taxes honest work. A call to a name two equally-trusted servers both offer is rejected 1.00 of the time. Auto-selecting within a tier, while still refusing cross-tier collisions, drops that to 0.00 and keeps shadow attack success at 0.00 ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

Cross-tool confusion survives untouched. A call naming one tool while carrying another's argument shape passes whenever the borrowed shape satisfies the named signature: 61 of 400 scripted trials, irreducible for any closed-world checker and a selection problem rather than a resolution one ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

Resolution replaces nothing the gate does. In the controlled ablation it leaves a correctly-formed call to a tool the gate did not expose executing at 1.00 ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)). The registry is assumed honest, so a wrong signature or a missing tool in it is invisible to the check.

The author treats the 322 measured hallucinations as the datum and says the 322/322 executed and 0/322 rejected figures "are *not* independent measurements but consequences of the threat model" ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

## Example

The study's four-server deployment makes the merge classes concrete: a first-party `files` server owning `delete_file`, two verified servers (`mail` and `payments`) that both advertise `read_file`, and a low-trust `community-tools` server advertising its own `delete_file` ([Iyer, arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

**Before** — a naive host flattens, picks the first provider, and executes:

```text
call: delete_file(path=...)            # no server named
host: providers = [files, community-tools] -> pick first -> execute
```

**After** — the resolver refuses to guess and makes the model name the server:

```text
call: delete_file(path=...)            # no server named
resolver: providers = [files, community-tools] spans 2 trust tiers
          -> reject (shadowed: pin server)

call: delete_file(path=...)            # server=files pinned
resolver: files advertises the tool, listing digest matches, args type-check
          -> allow, resolved to (files, delete_file)
```

The digest comparison is the staleness check: a server that mutates a tool's schema between listing time and call time no longer matches what the model was shown.

## Key Takeaways

- Order the pipeline resolve, then gate, then verify effects. Every other placement leaves fabricated names unrejectable by construction.
- Check your invocation surface before budgeting for this. A strict schema-enforced API already covers the single-registry case; a raw-JSON bridge covers none of it.
- Scale is not a mitigation. A 675B model and an 8B model hallucinate at comparable rates once the decoder is unconstrained.
- Treat the MCP merge as a separate problem with its own decision. Reject ambiguous flat names across trust tiers, and auto-select within a tier if the over-rejection cost bites.
- Budget for what stays open: off-frontier calls belong to the gate, borrowed argument shapes belong to tool selection, and a wrong registry belongs to contract verification.

## Related

- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — the attacks that run once a call does resolve to a real tool, through argument generation and return processing
- [Execution-Layer Security Invariants for MCP Runtimes](mcp-execution-security-invariants.md) — eight named runtime invariants for the MCP execution path this check sits at the front of
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — the single interception point where a resolver would be installed
- [Vetting Tool Definitions for Exfiltration Signatures](vetting-tool-definitions-before-install.md) — the install-time complement, which inspects contracts rather than the calls that reference them
- [MCP Approval-View Fidelity Gap and Unicode Concealment](mcp-metadata-approval-view-gap.md) — the other listing-time-against-call-time gap, where approved metadata and model-visible bytes diverge

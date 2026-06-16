---
title: "CoALA Structured Action Space: Internal vs External Actions"
term: "CoALA Structured Action Space"
description: "CoALA splits agent actions into internal (reason, retrieve, learn) and external (ground) — the boundary surfaces cost, reversibility, and permission profiles tool lists hide."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - CoALA internal external actions
  - structured agent action space
last_reviewed: 2026-06-12
maturity: adopted
---

# CoALA Structured Action Space: Internal vs External Actions

> CoALA splits agent actions into internal (reason, retrieve, learn) and external (ground) — the boundary surfaces cost, reversibility, and permission profiles tool lists hide.

## When the Split Pays Off

The boundary earns its keep when the agent has at least two of: persistent long-term memory, a multi-tool harness with mixed side-effect profiles, or permission gating that discriminates read-only inference from consequential writes. On a one-tool ReAct loop with no long-term memory it adds vocabulary without changing the architecture ([§5, Table 2](https://arxiv.org/html/2309.02427v3) lists no writable memory and digital grounding only for ReAct).

## The Action Space

CoALA structures the action space along one top-level boundary:

> "External actions interact with external environments (e.g., control a robot, communicate with a human, navigate a website) through grounding."
>
> "Internal actions interact with internal memories. Depending on which memory gets accessed and whether the access is read or write, internal actions can be further decomposed into three kinds: retrieval (read from long-term memory), reasoning (update the short-term working memory with LLM), and learning (write to long-term memory)."
>
> — [Sumers et al., CoALA, arXiv:2309.02427 §5](https://arxiv.org/html/2309.02427v3)

The four resulting action types:

| Type | Direction | Working memory | Long-term memory | External world |
|------|-----------|----------------|------------------|----------------|
| **Reason** (internal) | LLM call | read + write | — | — |
| **Retrieve** (internal) | LT → WM | write | read | — |
| **Learn** (internal) | WM → LT | read | write | — |
| **Ground** (external) | WM ↔ world | read + write | — | read + write |

Grounding subsumes everything that reaches outside the agent: physical environments (robotic manipulation), dialogue environments (human/agent interaction), and digital environments (APIs, websites, code execution) — see [CoALA §5.1](https://arxiv.org/html/2309.02427v3).

## Why The Boundary Matters For Engineering

Internal and external actions have categorically different cost, reversibility, permission, and observability profiles. Naming the boundary makes those differences architectural defaults rather than per-tool ad-hoc decisions.

| Profile | Internal actions | External actions |
|---------|------------------|------------------|
| Cost | inference-only or in-process | network + side-effect cost |
| Reversibility | working memory rolls back trivially | writes, sent messages, API calls often irreversible |
| Permission gating | none required (no egress) | the [lethal trifecta's](../security/lethal-trifecta-threat-model.md) egress leg sits here |
| Observability | invisible to outside observers | produces real telemetry |

Conflating the two — treating a memory read and a `curl` call as one "tool call" — pushes permission, durability, and rollback questions to per-tool decisions. The boundary is also where the [reasoning-execution split](cognitive-reasoning-execution-separation.md) anchors at runtime: reasoning and retrieval stay on the cheap, reversible side; learning and grounding cross into permanence.

## Mapping CoALA Actions to a Coding-Agent Harness

| CoALA action | Claude Code / Copilot / Cursor equivalent |
|--------------|-------------------------------------------|
| Reason | LLM turn — extended thinking, plan generation, classification |
| Retrieve | Read of [`CLAUDE.md`](../instructions/claude-md-convention.md), grep over the repo, RAG fetch from a vector store, MCP resource read |
| Learn | Write to a persistent memory file, append to a session journal, update of a skill or rule file |
| Ground | `Bash`, `Edit`/`Write`, `WebFetch`, `gh` CLI write, any [MCP server with side effects](../tool-engineering/documentation-grounding-mcp-servers.md) |

The mapping lets you audit a harness for asymmetry: most production coding agents have rich grounding, decent reasoning, partial retrieval, and almost no learning — which is why session-to-session knowledge stays in the user's head or in `CLAUDE.md`. CoALA's survey of existing systems ([§5/Table 2](https://arxiv.org/html/2309.02427v3)) shows the same gap across the academic systems it classifies.

## Why It Works

The boundary is load-bearing because the *direction of memory access* (the formal criterion in [CoALA §5](https://arxiv.org/html/2309.02427v3)) correlates with the *operational profile* (the engineering criterion in the table above). A read against working memory cannot have a side effect; a write against the external world generally does. Naming the boundary at the architecture layer lets one ontology drive permission gating, telemetry, and rollback policy at once — without it, those three policies get wired independently per tool and drift apart.

## When This Backfires

The four-way split is a modelling choice, not a physical fact. Three conditions where forcing it adds work without insight:

- **Single-tool ReAct loops with no long-term memory.** CoALA's own classification of ReAct in [Table 2](https://arxiv.org/html/2309.02427v3) shows no writable memory and digital grounding only — the four-way split collapses to "reason vs tool-call". A typed-tool-call boundary captures the same information with one ontology instead of two.
- **Tools that both retrieve and mutate.** A vector store that returns documents *and* updates relevance counters straddles retrieval (internal read) and grounding (external side effect). Force-classifying it on one side hides the [trifecta-relevant fact](../security/lethal-trifecta-threat-model.md) that it touches both — explicit per-tool annotation is needed. The boundary is contested in the paper itself: a Wikipedia database could be internal semantic memory or external digital environment depending on framing ([CoALA §5 discussion](https://arxiv.org/html/2309.02427v3)).
- **Knowledge-layer category error.** CoALA lumps facts and experiences under "semantic memory" without distinguishing persistence semantics. [The Missing Knowledge Layer (arXiv:2604.11364)](https://arxiv.org/abs/2604.11364) argues this "produces a category error: systems apply cognitive decay to factual claims, or treat facts and experiences with identical update mechanics." Pair CoALA's action taxonomy with [tiered memory architecture](tiered-memory-architecture.md) when both facts and episodes are stored.

Frontier-context expansion also weakens the split over time: the CoALA authors themselves note that "a longer context might downplay the importance of long-term memory" ([§7](https://arxiv.org/html/2309.02427v3)) — internal retrieval loses operational meaning when working memory holds the corpus.

## Example

A coding agent receives the user message "ship the auth bug fix". One decision cycle, annotated by CoALA action type:

```text
1. Reason   — LLM plans: read PR template, find auth tests, run them, commit
2. Retrieve — grep `tests/auth*` (read from semantic memory of repo state)
3. Reason   — LLM picks tests/auth_test.py as the right entry point
4. Ground   — Bash: pytest tests/auth_test.py            (external, reversible-ish)
5. Ground   — Edit: src/auth.py                          (external, side effect on disk)
6. Ground   — Bash: pytest tests/auth_test.py            (external, validates)
7. Learn    — append fix rationale to .claude/journal.md (internal write to LT memory)
8. Ground   — gh pr create                               (external, irreversible — egress leg)
```

The boundary makes three things visible at a glance: steps 4–8 need permission gates and observability; steps 1–3 and 7 do not. Step 2 is a retrieval, not a tool call to be gated. Step 8 is the trifecta-bearing action — the one a [permission framework](../security/permission-framework-over-model.md) has to interrupt for.

## Key Takeaways

- CoALA's internal/external boundary maps onto cost, reversibility, permission, and observability profiles that monolithic tool lists hide.
- The four action types — reason, retrieve, learn, ground — give a vocabulary for auditing harness asymmetry; most coding agents over-invest in grounding and under-invest in learning.
- The split pays off when the agent has [persistent long-term memory](agent-memory-patterns.md) or a mixed-side-effect tool surface; it adds work without insight on single-tool ReAct loops.
- Tools that both retrieve and mutate need explicit annotation, not forced one-side classification — the boundary is a modelling choice, not a physical fact.
- Pair the action taxonomy with explicit memory tiering when facts and experiences share a store, to avoid the persistence-semantics category error.

## Related

- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Externalization in LLM Agents](externalization-in-llm-agents.md)
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md)
- [Tiered Memory Architecture](tiered-memory-architecture.md)
- [Lethal Trifecta in Agent Tooling](../security/lethal-trifecta-threat-model.md)
- [Cognitive Architectures for Language Agents (CoALA): A Classifier for Agent Harnesses](../frameworks/coala-cognitive-architecture-language-agents.md) — the full three-axis framework this action-space split sits within

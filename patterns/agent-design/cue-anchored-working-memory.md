---
title: "Cue-Anchored Working Memory (Delivery, Not Storage)"
description: "Give a coding agent a second memory tier — operational facts the harness injects deterministically when a context cue fires, so the agent never has to remember to look them up."
term: "Cue-Anchored Working Memory"
tags:
  - agent-design
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - cue-anchored memory delivery
  - harness-delivered working memory
  - delivery not storage
last_reviewed: 2026-07-24
maturity: emerging
---

# Cue-Anchored Working Memory (Delivery, Not Storage)

> Deliver operational facts by injecting them when a cue fires, so the agent uses working memory without remembering to look it up.

Coding agents have one kind of memory today: documents they must deliberately write and deliberately re-read, such as [CLAUDE.md and its siblings](../../instructions/claude-md-convention.md), plan artifacts, and [auto-written memory directories](agent-memory-patterns.md). [Saha (2026)](https://arxiv.org/abs/2607.20972) argues the load-bearing tier for long-horizon work is a second one that does not yet exist: involuntary, situationally-bound facts (gotchas, file locations, local conventions) surfaced automatically when the situation cues them, and that supplying this tier is the harness's job.

## Two tiers of memory

The two tiers differ on how a fact is encoded and how it comes back ([Saha, 2026](https://arxiv.org/abs/2607.20972)):

| Dimension | Tier 1: documents | Tier 2: cue-anchored |
|-----------|-------------------|----------------------|
| Content | Durable, shareable: specs, ADRs, runbooks | Situational: gotchas, locations, tacit fluency |
| Encoding | A deliberate act of authorship | A side effect of the work |
| Retrieval | Deliberate lookup | Cue-driven, involuntary |

Every persistent surface an agent has — instruction file, plan, memory directory — sits in Tier 1: written on purpose, retrieved on purpose. A fact like "this config is load-bearing" is useful only while you are looking at that config, so it resists being written down as a decontextualized document. That is the tier the paper reproduces.

## Delivery, not storage

The paper's central claim is that whether a store behaves as memory or merely as a reference document is decided by the delivery mechanism, not by what is stored ([Saha, 2026](https://arxiv.org/abs/2607.20972)). Two channels deliver differently:

- Control plane — the harness decides deterministically what enters the window and when, and injects the fact. The agent trusts it, the way you trust a recalled memory.
- Content plane — material is added and the model must choose to look it up and then evaluate the result. This is how a reference document behaves.

Injection makes a store function as memory; lookup makes it function as a document. This reframes agent-memory design: the win is not a bigger store but a mechanism that re-surfaces the right operational fact at the right moment. It is the same reason memory is treated as [a property of the harness rather than a pluggable module](harness-memory-coupling.md).

## The cue vocabulary

Each stored fact carries standing trigger conditions over five composable cue types, evaluated deterministically harness-side with no model judgment in the delivery path ([Saha, 2026](https://arxiv.org/abs/2607.20972)):

- Path — glob patterns over touched files; fires when the agent opens a matching path.
- Symbol — a named code entity is referenced; needs a code-symbol graph.
- Semantic — similarity of the current activity crosses a floor.
- Event — session start, prompt submit, pre-edit, pre-run, pre- or post-compaction.
- Temporal — not-before constraints and cooldowns between fires.

Triggers combine by conjunction within a memory and disjunction across memories. A per-session fire ledger de-duplicates redundant injections and re-arms at each compaction boundary, so cue-anchored facts return in a fresh window.

## Why it works

The mechanism is borrowed from cognitive science, not from reported success. Levels-of-processing research shows operational facts are encoded incidentally, through task engagement, not by a deliberate decision to save, so capture cannot depend on agent initiative. The encoding-specificity principle shows retrieval is cue-driven and largely involuntary, with involuntary autobiographical memories outnumbering voluntary recall roughly two to one, so the default channel must be injection at the cued moment, with lookup only a fallback ([Saha, 2026](https://arxiv.org/abs/2607.20972)). Control-plane injection also meets Clark's extended-mind criterion that an external store be automatically endorsed: an injected fact is trusted, whereas a looked-up one must first be evaluated. The empirics match the theory — a seeded voluntary store drew zero memory operations across 114 turns, while harness-injected facts survived all 138 compact-resume cycles in the decay probe, and only after deterministic delivery did agents begin to recall and revise memory voluntarily ([Saha, 2026](https://arxiv.org/abs/2607.20972)).

## When this backfires

Deterministic delivery has no model gate, so it fires whatever is stored — which is a liability under several conditions:

- Stale or environment-specific facts. A cue fires an invalidated "load-bearing" note unconditionally, and the agent applies it confidently — the staleness failure mode of [authored memory](agent-memory-patterns.md), now automated rather than fixed.
- Short sessions that never compact. The decay that injection solves never arises, so the cue machinery is pure overhead.
- Tight context budgets. Per-cycle injection of schemas, guidance, and facts crowds the window; the paper's own memory-equipped runs hit thrash-guard aborts and one late-run confabulation spiral.
- Missing infrastructure. Without a code-symbol graph or harness hook points, the path and symbol cues cannot be evaluated and the mechanism degrades to semantic and event cues only.

The evidence base is also thin: one single-author study, one corpus, one agent product, one model family, with small samples and no independent replication ([Saha, 2026](https://arxiv.org/abs/2607.20972)). Treat the mechanism as well-grounded and the engineering result as emerging. Pairing delivery with a freshness or supersession check — the [control-decision view of retrieval](memory-retrieval-as-control.md) — addresses the unconditional-fire risk.

## Example

A path-cued operational fact, stored once as a side effect of a debugging session, rendered in the paper's cue vocabulary ([Saha, 2026](https://arxiv.org/abs/2607.20972)):

```yaml
fact: "generated_client.py is overwritten by `make codegen` — edit the template, not this file"
cue:
  path: "src/api/generated_client.py"
  event: pre-edit
```

The next time any session opens `src/api/generated_client.py` to edit it, the harness injects the note before the edit — no recall step, no lookup the agent has to remember. Stored as a Tier-1 comment in the file, the same fact only helps if the agent happens to read that far first; delivered on the pre-edit cue, it arrives exactly when it changes the decision.

## Key Takeaways

- Coding agents have only the authored-document tier; the missing tier is involuntary, cue-anchored operational facts the harness surfaces automatically.
- Delivery decides the behavior: harness injection (control plane) makes a store act as memory; agent lookup (content plane) makes it act as a reference document.
- Facts carry deterministic triggers over five cue types — path, symbol, semantic, event, temporal — evaluated harness-side with no model judgment in the delivery path.
- The mechanism is grounded in incidental encoding and cue-driven involuntary retrieval; voluntary memory drew ~0 use while injected facts survived 138 compaction cycles.
- Deterministic delivery has no gate — it fires stale or environment-specific facts unconditionally, so pair it with a freshness check and skip it for short, non-compacting sessions.

## Related

- [Harness-Memory Coupling as a Design Axis](harness-memory-coupling.md) — why memory is a property of the harness, not a pluggable module
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — the authored-document (Tier 1) memory this pattern complements
- [Tiered Memory Architecture](tiered-memory-architecture.md) — the storage-and-promotion side of memory, the counterpoint to delivery-first
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md) — a controller deciding whether to inject retrieved memory, a gate for stale-fact risk
- [Dual-Trace Memory Encoding](dual-trace-memory-encoding.md) — pairing a fact with the scene it was learned in, the situational binding cue-anchoring relies on

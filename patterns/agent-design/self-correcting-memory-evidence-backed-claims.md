---
title: "Self-Correcting Memory: Evidence-Backed Claim Repair"
term: "Self-Correcting Memory"
description: "Bind each memory claim to versioned source evidence so a deterministic diff flags stale entries before any model judges whether they are still true."
tags:
  - agent-design
  - memory
  - context-engineering
  - tool-agnostic
aliases:
  - evidence-backed claim staleness
  - agent memory staleness detection
  - self-correcting knowledge base
last_reviewed: 2026-08-26
maturity: emerging
---

# Self-Correcting Memory: Evidence-Backed Claim Repair

> Self-correcting memory anchors each claim to versioned evidence, so a diff marks stale entries without a model call, and fails where evidence is unversioned.

Self-correcting memory records the evidence behind every fact it stores, along with the version of that evidence, and rechecks those versions before trusting the fact again. The worked implementation is OpenWiki's claims runtime, where the store is a wiki over a codebase and the evidence is a line range in the repository ([LangChain, 2026](https://www.langchain.com/blog/self-correcting-memory-openwiki)). A claim whose recorded version no longer matches the current source is marked stale, which means "OpenWiki can no longer safely assume that the claim is still true without checking the source again."

## When it applies

One precondition decides whether any of this works: the source of truth has to be versioned and addressable per claim. Code in a repository qualifies, because the runtime can compare the version it recorded against the version on disk ([LangChain, 2026](https://www.langchain.com/blog/self-correcting-memory-openwiki)). Slack threads, meeting notes, and user preferences do not: with nothing to diff, no fact gets marked suspect until a model reads it and forms an opinion.

Whether it pays for itself turns on two more things. Change volume has to stay low relative to store size, since the claimed payoff is that "update cost scales with how much the code changed, not with how many claims the wiki holds" ([LangChain, 2026](https://www.langchain.com/blog/self-correcting-memory-openwiki)). And repair is lazy: a correction reaches a page only when an update touches it.

## How the loop runs

Writing a page also records the claims that page makes and the code supporting each one ([LangChain, 2026](https://www.langchain.com/blog/self-correcting-memory-openwiki)):

```json
{
  "statement": "Failed tasks are retried three times by default.",
  "evidence": ["repo://src/scheduler.ts#L393-L404"]
}
```

The runtime stores a version for that evidence. Staleness detection then runs at the start of every update, before the agent acts: it walks the claim set and compares each persisted version against the code on disk, which the post calls "a deterministic check with no model calls." No status flag is kept, because the stored version re-derives freshness on its own, so a claim cannot quietly return to trusted.

Repair happens inside work the agent is already doing. "The agent never sweeps the claim set itself." Stale claims surface beside the page content when an update reads that page, and the agent either re-verifies the claim and refreshes its version or rewrites claim and page text together. Whatever it leaves unresolved stays flagged.

## Why it works

The detection half asks the model nothing. A version comparison decides which claims are suspect, and the model is invoked only afterwards, with the current source in front of it. That split maps onto the sharpest finding in the self-correction literature: correction succeeds on tasks with reliable external feedback, and "no prior work demonstrates successful self-correction with feedback from prompted LLMs, except for studies in tasks that are exceptionally suited for self-correction" ([Kamoi et al., 2024](https://arxiv.org/abs/2406.01297v3)). Without external feedback, models "struggle to self-correct their responses, and at times, their performance even degrades after self-correction" ([Huang et al., 2024](https://arxiv.org/abs/2310.01798v2)). A versioned evidence anchor is how a memory store manufactures that external signal for itself.

Durability is the other half. Uncertainty lives in the stored version rather than in a flag someone can clear, so a claim stays suspect until it is rechecked. Outdated entries sitting beside current ones both reduce answer accuracy and mislead models into harmful outputs "even when current information is available" ([Ouyang et al., 2025](https://arxiv.org/abs/2503.04800v3)).

A replay benchmark reports stale claims falling from 3.5% to 0.5% and hallucinated claims from 0.7% to zero across 2,000 claims per arm ([LangChain, 2026](https://www.langchain.com/blog/self-correcting-memory-openwiki)). The vendor built and ran it, nobody has replicated it, and no variance is reported, so treat the figures as a direction rather than a measurement.

## When this backfires

- The anchor is wrong. A claim's link to its evidence is model-produced, and the best model in a 2025 evaluation reached F1 scores of 79.4% and 80.4% on documentation-to-code trace links ([Alor et al., 2025](https://arxiv.org/abs/2506.16440v1)). A claim anchored to the wrong lines never fires when the code it truly depends on changes, and fires whenever the wrong lines churn.
- Mechanical edits flood the queue. Staleness over-approximates by design, so a formatting sweep or a file move marks every claim anchored in the touched ranges. Detection stays free; the per-claim verification the agent then performs does not.
- Cold pages never heal. Repair reaches only a page an update reads, so a page nobody touches carries its stale claims indefinitely.
- The repair itself is wrong. A model that misjudges a stale claim against current code rewrites a correct entry into a false one and stamps it with a fresh version, which makes the damage look verified. Nothing checks the corrector, and the flip is documented: without external feedback "the model is more likely to modify a correct answer to an incorrect one than to revise an incorrect answer" ([Huang et al., 2024](https://arxiv.org/abs/2310.01798v2)).
- Regeneration is simpler at small scale. Rebuilding the store from current source has no claim schema, no anchor rot, and no way for a claim to stay stale forever. The claims runtime earns its complexity only once regeneration cost scales with store size while change volume stays low.

## Key Takeaways

- Store the evidence and its version, not just the fact. The version is what lets a memory layer distrust itself on a schedule it does not control.
- Keep detection deterministic and model-free, and invoke the model only after the diff has already said that something changed.
- The pattern does not transfer to memory over unversioned sources, where it collapses into the intrinsic self-correction the literature says fails.
- Budget for two failure modes the mechanism cannot see: an anchor pointing at the wrong code, and a repair pass that overwrites a true claim and marks it fresh.

## Related

- [Wiki Memory: Agent-Maintained Compressed Knowledge Base](wiki-memory-agent-maintained-knowledge-base.md) — the layer this maintains, covering how the compressed knowledge base gets built in the first place
- [Git-Bound Memory for the Agentic Development Lifecycle](git-bound-memory.md) — the alternative freshness source, inherited from commits and review rather than tracked per claim
- [Knowledge Graphs as Provenance-Carrying Agent Memory](knowledge-graph-shared-memory.md) — the same check-rather-than-judge idea applied to typed relations that each record their source document
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md) — the query-time half, gating what reaches the agent where this pattern governs what stays trusted at write time
- [Detecting Memory-Poisoning Exfiltration by Tool-Call Order](../../security/recall-before-send-memory-poisoning-detection.md) — the adversarial neighbor, where bad entries are planted rather than left behind by change

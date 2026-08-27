---
title: "Per-Type Retention Policy for Agent Compaction (Knowledge Triage)"
term: "Knowledge Triage"
description: "Compaction summarizes safety rules at the same rate as chat logs; classify each line by type and give each type its own retention fidelity, but pin constraints first."
aliases:
  - knowledge triage for agent memory
  - per-type retention policy
  - the compaction cliff
tags:
  - context-engineering
  - memory
  - arxiv
  - tool-agnostic
last_reviewed: 2026-08-25
maturity: emerging
status: current
---

# Per-Type Retention Policy for Agent Compaction (Knowledge Triage)

> Compaction summarizes a safety rule at the same rate as a chat log; pin the rules out of reach before setting per-type fidelity.

Check the cheap fix first. Most agents carry a handful of standing rules, and the answer there is to keep them out of the summarizer's reach rather than classify anything. Per-type retention earns its cost once the rules outgrow what you can pin.

## Measure the decay before you fix it

Run a session past one compaction round, then grep the summary for a rule you know was in context and compare it word for word. Two published measurements say the wording will already have moved.

Claude Code's `/compact` on Sonnet 4.6, instructed to "compress to NN tokens, keep every safety rule and procedural command verbatim", preserved 53% of safety rules after one round and 10% after five ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)). A separate group measured the behavioral consequence over 1,323 episodes across seven model families: prohibited tool actions rise from 0% with the policy in full context to 30% after compaction, and to 59% on the worst model ([Chen, 2026](https://arxiv.org/abs/2606.22528v2)).

The split inside that second result is the useful part. A constraint that survives the summary gives 0% violation, a dropped one 38%. Exact wording decides the outcome, not the quality of the summary around it.

## Pin the constraints, then classify

Constraint Pinning quarantines governance constraints from lossy compaction and re-injects them verbatim after each round. It restores violation to 0% for roughly 47 pinned tokens, "<0.5% of a production-scale compaction context". A separate three-model utility test "completes 99% of allowed actions with 1% over-refusal" ([Chen, 2026](https://arxiv.org/abs/2606.22528v2)). No classifier, no taxonomy, no training. The [post-compaction re-read protocol](../instructions/post-compaction-reread-protocol.md) is the hand-driven version, with the instruction file standing in for the pinned buffer.

Knowledge Triage is the escalation for when the pin stops fitting. It sorts every line of the knowledge base into five types with different distortion tolerances ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)):

| Type | Definition from the paper | Retention |
|---|---|---|
| Constraint | "Rule that bounds agent behavior; violation causes safety failure" | Verbatim, zero distortion |
| Procedural | "Step-by-step instruction for a task" | Rewrite only if execution is preserved |
| Belief | "Factual assertion treated as true" | Bounded semantic distortion |
| Preference | "Soft guideline" | Summarize or merge |
| Episodic | "Past event or observation" | Discard freely |

Three operators apply that classification to the three context operations, and each is measured against lossy compactors ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)):

- TypeCompact routes items into fidelity lanes, "constraints and procedures at full, beliefs and preferences at compressed, episodic items at placeholder". It preserves 2 to 4 times more safety rules than the strongest single-shot LLM compactor, at 96% recall over five rounds.
- TypeDecompose replicates each constraint into "every partition that intersects its scope", never separating a rule from the work it governs. Locality violations drop to 0% from 93%.
- TypeRetrieve pins in-scope constraints ahead of relevance ranking, then fills the rest by similarity, reaching 100% recall@50 against 73%.

## Why it works

A summarizer applies one distortion budget to text carrying five different tolerances, because nothing tells it which line is which. The paper states the mechanism directly: "A type-blind compactor has no signal for which sentences are safety rules and summarizes them at the same rate as the surrounding text" ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)). Labeling supplies the missing signal, and "TypeCompact pins every classifier-labeled constraint and procedure unchanged, so an item is lost only if the classifier mislabels it".

That last clause names the trade: the failure moves from the summarizer's discretion to the classifier's recall. Pinning has no classifier and no such surface.

## When this backfires

- Your rules fit in the budget. Pinning already reaches 0% violation at roughly 47 tokens ([Chen, 2026](https://arxiv.org/abs/2606.22528v2)), so a classifier, a rubric, and a verifier buy nothing.
- The classifier misses. The paper's SafetyMargin classifier runs at "0.93 recall" with a "residual miss rate of 0.07", so 7% of safety rules are still compacted like prose ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)).
- Many rules carry global scope, or the config is already rule-dense. TypeDecompose replication overhead "varies widely (median 0%, worst case 219%)", and "on the 1.4% of configurations whose constraint-plus-procedural density exceeded 40%, Bmin approached the 50% budget; TypeCompact escalated to Unsafe on 28%" ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)). Past that point you get a refusal, not a smaller context.
- Your team cannot agree on the labels. Two annotators reached a five-class Cohen's κ of 0.45 against 0.79 on the binary constraint-versus-other call, and the rubric needs re-fitting before deployment because "type distributions in closed enterprise corpora may differ" from the GitHub-sourced sample ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)).
- The pin stops forgetting, not forged authority. An operator-impersonation rescind placed in recent, non-summarized context "raises naive pinning from 0% to 17%", and hardening the pin with explicit provenance "only halves the residual (17%→10%); it does not eliminate it". Chen names a "trusted out-of-band operator channel" — "authority that does not live in the token stream and so cannot be forged by in-context content" — as what fully closing the gap requires ([Chen, 2026](https://arxiv.org/abs/2606.22528v2)).
- An attacker can write into the context. Chen demonstrates a Compaction-Eviction Attack, where adversarial content biases the summarizer into omitting a legitimate policy, and reports that optimizing the injection "breaks the models that shrug off the fixed attack", driving Claude-Sonnet-4.6 to 65% violation, GLM-5.1 to 85%, and DeepSeek-V4 to 100% ([Chen, 2026](https://arxiv.org/abs/2606.22528v2)). Any mitigation keeping a rule inside the lossy path inherits this.

One caveat about the evidence. Every TypeCompact baseline is itself a lossy compactor ([Zerhoudi et al., 2026](https://arxiv.org/abs/2608.22752v1)). Pinning appears nowhere in the comparison or the reference list, so the 2-to-4x advantage is measured against the wrong alternative for the common case.

## Key Takeaways

- Treat compaction as a safety surface and test it: run past a round, then check whether your rules are still quoted exactly.
- Whatever you keep, keep it word for word. A paraphrased rule is an unenforced rule.
- Pin before you classify, and escalate to per-type retention only when the pin no longer fits. A pin stops forgetting, not a forged rescind, and that residual is 10% even hardened.
- Whichever route you take, ask what the guarantee now rests on. For triage, it is classifier recall, and that number is your real ceiling.

## Related

- [Context Compression Strategies](context-compression-strategies.md) — the tiered offload-and-summarize scheme a retention policy sits on top of
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — when to compact, as against what should survive it
- [Context Lifecycle Management](context-lifecycle-management.md) — the five-stage lifecycle that decides what is stored before anything is compacted
- [CoALA Memory Taxonomy as a Classifier for Harness Artifacts](../patterns/agent-design/coala-memory-taxonomy-classifier.md) — a different classification target: harness artifacts to find capability gaps, not knowledge lines to set fidelity
- [Addressable Recall Compaction](addressable-recall-compaction.md) — keeping the verbatim record recoverable after a summary replaces it

---
title: "Per-Agent Compaction Windows for Orchestrator and Worker"
term: "Per-Agent Compaction Window"
description: "Claude Code 2.1.296 made the auto-compact trigger a per-subagent field. Set a worker's window tighter only when it can re-derive what it drops."
aliases:
  - autoCompactWindow
  - per-subagent compaction threshold
  - subagent auto-compact window
tags:
  - context-engineering
  - agent-design
  - cost-performance
  - arxiv
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-10
maturity: emerging
status: current
---

# Per-Agent Compaction Windows for Orchestrator and Worker

> A subagent's auto-compact trigger can now be set in its own frontmatter field, so a worker and its orchestrator need no longer share one threshold.

A per-agent compaction window is an auto-compact threshold declared on one subagent instead of on the session. Claude Code 2.1.296, dated October 9, 2026, "Added `autoCompactWindow` to subagent frontmatter and `--agents` definitions, so a subagent can auto-compact earlier than the main conversation's window" ([Claude Code changelog 2.1.296](https://code.claude.com/docs/en/changelog#2-1-296)). Until that release one control reached both sides at once: "Compaction triggers under the same conditions, and `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies to subagents as well" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)).

## When a tighter worker window pays

Squeezing a verbose worker to protect the orchestrator's reasoning chain is the obvious use, and the direction the measured evidence runs against. Test three conditions first.

The worker can re-derive what it drops. Satish et al. suspect the workloads contribute to a split between two benchmarks: "SWE-bench agents can recover working context from code and patches, whereas Terminal-Bench's varied workflows may depend more on intermediate observations and action history" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). A worker that re-reads files tolerates a tight window. A worker whose product is its accumulated observations does not.

The parent and the child differ in model or workload. Threshold response does not transfer between models: "no single compression policy performs best across models, and a policy that is effective for one model can be substantially worse for another" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). Run both sides on one model over the same work and the second threshold is only a second thing to maintain.

You can measure the change, because the same change does not land the same way twice. In the paper's smaller ablation cohorts, raising one trigger from 10K to 15K to 20K tokens moved Qwen's resolve rate from 50.7% to 60.0% to 73.3%, while Devstral "remains roughly unchanged at 72–73% across its three thresholds" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

## Why it works

The two context budgets were already independent. What was shared was the trigger. A subagent writes to its own transcript file, so "when the main conversation compacts, subagent transcripts are unaffected" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). The budget is set per agent: "a subagent's context window is sized by its own model, not the parent's" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). `autoCompactWindow` moves the trigger to the level where the right value varies. A 65-policy sweep over three open-weight models, two coding benchmarks and "nearly 35,000 agent executions" put that variation in the model, the task and the workload ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

## When this backfires

- The worker depends on its own early reasoning. Compaction is lossy by construction: "overly aggressive compaction can result in the loss of subtle but critical context whose importance only becomes apparent later" ([Anthropic: effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Compacting the worker moves that loss onto the worker.
- More frequent compaction is the direction the sweep rejects: "Delaying compression generally helps in these sweeps." Raising one threshold from 10K to 20K at depth 0.5 cut compaction from 4.85 to 1.15 events per attempt. For the paper's free-form summarization primitive, resolve rate then rose from 50.7% to 62.7%, input cost fell from 1.10x to 0.92x, and latency fell from 653 to 599 seconds ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). That is Qwen on SWE-bench under the paper's own scaffold, not Claude Code.
- The bill rises while the token count falls. "A policy that frequently rewrites the trajectory can remove tokens while invalidating much of the reusable prefix" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). The tight window pays for more of its tokens at the fresh-input rate.
- A typo does nothing visible. "Claude Code ignores a field it doesn't recognize without reporting an error" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)), so a misspelled field leaves the default running while the fan-out looks healthy.

## Setting the field without guessing

The changelog line is the whole published specification. As of 2026-10-10 the [frontmatter reference](https://code.claude.com/docs/en/sub-agents) does not list `autoCompactWindow`, so no value syntax, default, or interaction with `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is documented.

So the verification step is the same release's debug change, which improved `--debug` "output to name unrecognized frontmatter fields in custom agent files, with a hint for likely typos" ([Claude Code changelog 2.1.296](https://code.claude.com/docs/en/changelog#2-1-296)). A field missing from that list of unrecognized fields parsed. Then compare the `preTokens` figure in the worker's `compact_boundary` events against the parent's, because that value "shows how many tokens were used before compaction occurred" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)) and is the only evidence the two windows differ.

Two adjacent 2.1.296 controls bear on the same decision. `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` runs "every workflow agent on one model while other subagents keep theirs", pinning the model the threshold depends on. Read's `allow_large` option lets Claude read "a text file past the usual size limits in one call when it needs the whole file and the context has room" ([Claude Code changelog 2.1.296](https://code.claude.com/docs/en/changelog#2-1-296)). One such call can fill a tight window on its own.

## Key Takeaways

- `autoCompactWindow` separates the auto-compact trigger from the session, a split parent and child transcripts already had for storage and window size.
- Tighten a worker's window only when it can re-read what it loses. Where the accumulated observations are the product, leave the field unset.
- In the paper's Qwen SWE-bench threshold sweep, delaying SU compression raised resolve rate while cutting cost and latency, and in the smaller SS-p ablation Devstral stayed flat at 72–73%, so treat a tighter default as a hypothesis, not a tuning win.
- Verify the field loaded through `--debug` and the worker's `preTokens` values, because an unrecognized frontmatter field fails silently.

## Related

- [Scoring a Compaction Policy on Latency and Billed Cost](compaction-policy-latency-and-cost.md) — the sweep behind the threshold numbers here, scored on latency and bill rather than tokens
- [Agent-Initiated Rubric-Gated Self-Compaction (SelfCompact)](agent-initiated-self-compaction.md) — the other way to stop sharing one trigger, by letting the agent fire its own
- [The Subagent Inheritance Contract: What Crosses Down](../patterns/multi-agent/subagent-inheritance-contract.md) — what else a child does and does not take from its parent
- [Reasoning Retention and Compaction as Harness Settings](reasoning-retention-and-compaction.md) — what a harness keeps across a compaction boundary
- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md) — the tiers a trigger fires into

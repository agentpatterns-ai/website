---
title: "Agent-Initiated Rubric-Gated Self-Compaction (SelfCompact)"
term: "Agent-Initiated Self-Compaction"
description: "Pair an agent-invoked compaction tool with a firing rubric so compaction tracks trajectory structure: fire when a sub-task resolves, suppress mid-derivation."
tags:
  - tool-agnostic
  - context-engineering
  - pattern
  - arxiv
aliases:
  - rubric-gated self-compaction
  - self-compacting agents
last_reviewed: 2026-07-14
maturity: emerging
---

# Agent-Initiated Rubric-Gated Self-Compaction (SelfCompact)

> Give the agent its own self-compaction tool and a firing rubric so it compacts on trajectory structure, not a fixed token count.

Agent-initiated self-compaction gives the model both a tool that condenses its own accumulated context and an explicit rubric for when to use it. The condition that makes it work leads the pattern: ship the two together. On its own the compaction tool is used unevenly across models and does not reliably help; the rubric supplies the firing signal the model cannot generate for itself ([Self-Compacting Language Model Agents, arxiv 2606.23525](https://arxiv.org/abs/2606.23525)).

## The two elements

The pattern pairs one inference-time tool with one lightweight instruction, and both are load-bearing ([arxiv 2606.23525](https://arxiv.org/abs/2606.23525)):

- Compaction tool: the model calls it to replace accumulated context with a summary it writes itself.
- Firing rubric: a short instruction telling the model when to fire and when to hold off.

The rubric ties the decision to where the agent is in its trajectory, not to how many tokens have piled up:

| Rubric says | Condition |
|-------------|-----------|
| Fire | A sub-task has resolved |
| Fire | The trajectory is converging on an answer |
| Suppress | The agent is mid-derivation |
| Suppress | The agent is stuck |

## What it replaces

Existing scaffolds compact on a fixed interval or a token threshold: Claude Code's auto-compaction fires at [about 95% of the window](https://code.claude.com/docs/en/settings), for example. A threshold pays no attention to trajectory structure, so it can fire mid-derivation and discard a partial result the agent still needs. Moving the trigger to a rubric the agent applies against its own progress aligns compaction with points where the accumulated context has already paid out.

This is the agent-initiated point on the compaction spectrum. It differs from user-driven [manual `/compact`](manual-compaction-dumb-zone-mitigation.md), from user- or scaffold-chosen [selective rewind](selective-rewind-summarization.md), and from a [hook-gated PreCompact veto](../tool-engineering/precompact-hook-compaction-veto.md): here the model both decides and acts, guided by the rubric.

## Why it works

A token threshold is structure-blind. Token count is uncorrelated with whether the trajectory sits at a safe compaction boundary, so a threshold trigger risks summarizing away partial results mid-derivation. A rubric keyed to sub-task resolution and convergence fires when accumulated context has already delivered its value, and holds during derivation when that context is still in use.

The tool alone is not enough because models cannot see the state they would need to time compaction well. Frontier models are "proprioceptively blind to their own context": from the prompt alone they cannot tell how large, how old, or how used each block is ([LLM Agents Are Latent Context Managers, arxiv 2606.30005](https://arxiv.org/abs/2606.30005)), and their metacognition is limited in resolution and unreliable ([Evidence for Limited Metacognition in LLMs, arxiv 2509.21545](https://arxiv.org/abs/2509.21545)). The rubric supplies that missing signal from outside the model. No fine-tuning is required ([arxiv 2606.23525](https://arxiv.org/abs/2606.23525)). The payoff of compacting at the right moment is attention-budget recovery: replacing accumulated token mass with a dense summary restores per-token attention to the relevant remainder ([Anthropic: effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

Across six benchmarks spanning competitive math and agentic search, and seven models, the paired approach matched or beat fixed-interval summarization at 30 to 70% lower per-question cost ([arxiv 2606.23525](https://arxiv.org/abs/2606.23525); figures grounded in the paper's abstract).

## When this backfires

The pattern rests on the model following the rubric, so it degrades where that assumption weakens:

- Weak instruction-followers: on smaller or open-weight models the compaction tool is used unevenly, so self-firing misfires without reliable rubric adherence ([arxiv 2606.23525](https://arxiv.org/abs/2606.23525)).
- Mis-timed firing: because the model cannot see its own context state ([arxiv 2606.30005](https://arxiv.org/abs/2606.30005)), a self-fired compaction can still land mid-derivation and discard a partial result. That is the same failure a threshold has.
- Short or bounded sessions: when the window is never under pressure, the rubric, tool definition, and per-turn deliberation are pure token overhead. A plain threshold, or no compaction, is cheaper.
- Reference-heavy work: when verbatim artifacts such as specs, schemas, or API contracts must persist, any summary at any trigger loses them, and better timing does not help ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

Where the boundaries are externally observable (a sub-agent return, a passing test), a deterministic trigger the harness fires is auditable and does not depend on the model introspecting correctly. Reach for agent-initiated compaction when the safe points live inside the model's reasoning, not in events the scaffold can already watch.

## Example

The rubric operationalizes the firing conditions from the paper as a short system-prompt instruction paired with the tool ([arxiv 2606.23525](https://arxiv.org/abs/2606.23525)):

```markdown
You have a `compact_context` tool that summarizes everything so far.

Call it when:
- you have just finished a sub-task, or
- your remaining steps are converging on the answer.

Do not call it when:
- you are mid-derivation and still need the working detail, or
- you are stuck and may need to revisit earlier context.
```

The tool without these lines is used unevenly; the lines are what make the firing decision track the trajectory rather than the token count.

## Key Takeaways

- Write the firing conditions directly beside the tool definition, in the same instruction block, not in separate documentation the model must recall unprompted.
- Do not trust a model's own sense of how full its context is: the rubric exists because that self-assessment is unreliable, so the firing signal has to come from outside the model.
- When a compaction boundary is externally observable (a sub-agent return, a test passing), fire a deterministic harness trigger instead of the rubric; save agent-initiated firing for boundaries only the model can see.
- Read the 30 to 70% cost figure as a comparison against fixed-interval summarization, not against running no compaction at all.
- Before adopting this pattern, check the model is a strong instruction-follower, the session runs long enough for context pressure to matter, and no verbatim artifact needs to survive compaction. None of those three gaps closes with a better-written rubric.

## Related

- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — the user-driven `/compact` point on the same spectrum; this page moves the trigger to the agent.
- [Selective Rewind Summarization](selective-rewind-summarization.md) — a user- or scaffold-chosen cut point; here the model chooses instead.
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](../tool-engineering/precompact-hook-compaction-veto.md) — hook-gated deferral of compaction, the deterministic counterpart to a model-applied rubric.
- [Proprioceptive Context Dashboard](proprioceptive-context-dashboard.md) — surfaces context state so the model can see it; the complementary answer to the same meta-cognitive gap.
- [Context Compression Strategies](context-compression-strategies.md) — the broader tiered-compression frame this pattern sits inside.

---
title: "Task Shape Decides What a Heavier Agent Harness Buys"
term: "Task-Shape Harness Payoff"
description: "On fixed-workflow issue repair a heavier harness covers for a weaker model. On open-ended repository work only strong models convert the extra harness."
aliases:
  - task-shape harness sizing
  - harness payoff by task type
  - conditional harness investment
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-30
maturity: emerging
---

# Task Shape Decides What a Heavier Agent Harness Buys

> On fixed-workflow issue repair a heavier harness covers for a weaker model, and its gain shrinks as the model improves. Open-ended repository work reverses that.

What a heavier harness buys depends on the shape of the task as much as on the strength of the backing model. A study of two harnesses across ten open-weight models and three benchmarks found the harness-to-capability relationship running in opposite directions on different task types ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)).

## Read the task shape first

On issue repair the workflow is fixed and edits touch functions in a few files. There, harness machinery substitutes for model capability, and the substitution weakens as models improve. Matched-model rows from the SWE-bench Verified leaderboard show it: OpenHands "decreases from +13.60 pp with Claude 3.7 Sonnet to +5.47 pp with Claude 4 Sonnet". SWE-agent drops "from +9.60 pp to +4.07 pp under the same model progression" ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)). The authors' own runs on a 300-instance sample of SWE-bench Pro repeat it for Qwen: "the OpenCode advantage decreases from about 6 pp for Qwen3-Max to 2.67 pp for Qwen3.7-Max".

Open-ended repository work inverts this. On ProgramBench, a repository-generation benchmark, weaker models got no preferential benefit: "OpenCode does not bring greater improvements to weaker models than mini-SWE-agent. Only the latest models (e.g., Qwen3.7-Max and DeepSeek-V4-Pro) can consistently leverage the complex harness to complete tasks more effectively" ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)). On GitTaskBench the turning point sat inside each family, at Qwen3.6-Max and DeepSeek-V3.1.

So the decision splits:

- Fixed-workflow task, strong model: the extra harness adds a smaller gain.
- Open-ended task, model below your family's turning point: the complex harness did not beat the minimal one.
- Open-ended task, model above it: this is where the build pays.

## The measured component ledger

Ablation on the full 200-instance ProgramBench set, run on Qwen3.7-Max and DeepSeek-V4-Pro only, ranks the five harness components unevenly, with subagents split into two variants. Every figure below is a repository-generation score change against the mini-SWE-agent baseline ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)).

| Component added alone | Qwen3.7-Max | DeepSeek-V4-Pro |
|---|---|---|
| Task-specific subagents | +5.91 pp | +4.46 pp |
| Tool registry | +4.57 pp | +3.54 pp |
| Explicit planning | small gain, no figure reported | small gain, no figure reported |
| Lazy skills | smaller benefit than DeepSeek | larger benefit than Qwen |
| Context compression | -4.86 pp | -3.85 pp |
| General SE subagents | negative, no figure reported | negative, no figure reported |
| All five combined | +7.37 pp | +6.21 pp |

The last row constrains how you use the rest. Turning on all five, including the two that lose points alone, beat every single-component variant on both models, taking Qwen3.7-Max "from 42.88 to 50.25" and DeepSeek-V4-Pro "from 45.14 to 51.35". The authors read this as non-independence: "harness components are not independent: their benefits depend on how they are coordinated within the agent loop". The study did not run subsets of two to four components, so the ledger does not show which parts are safe to strip.

## Why it works

The authors say the gains come from regulating "how agents explore and act in repositories". Manual inspection of failed and low-scoring trajectories found two failure modes, excessive probing and insufficient probing: "the components with the largest performance gains, i.e., task-specific subagents, substantially reduce the tendency of mini-SWE-agent to perform either excessive or insufficient probing" ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)). The correction runs both ways: one trajectory cut reference probes from 133 to 43 and rose from 1602/6491 to 4425/6491 tests passed; another raised probes from 3 to 45 and rose from 1231/1994 to 1499/1994. The authors suggest more structured interaction, not a bigger prompt budget, explains the gain: tool calls rose 131.18% and 83.58% while prompt tokens rose 16.37% and 7.26%.

## When this backfires

- The compression row may not transfer to a different compaction design. The module measured here applies snipping and observation compaction first, and "triggers LLM-based summarization" only if the context still exceeds the limit. CliffCompaction, a different design, "reduces cost by up to 50% under a bounded context while maintaining or improving performance on Terminal-Bench", crediting a pass that keeps "compacted information faithful by only truncating or dropping content, never rephrasing or rewriting it" ([arXiv:2609.26779v1](https://arxiv.org/abs/2609.26779v1)).
- Its payoff also shrinks as the window widens. Averaged across four models, the payoff from managing context "shrinks steadily across 32k, 64k, 96k, and 128k windows: from 35.7 to 15.9, 5.5, and 2.7 percentage points on SWE-Bench" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).
- Diminishing is not zero. In the same leaderboard table the Tools harness still gained +5.60 pp on Claude 4 Opus, the strongest model listed ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)).
- Nothing here transfers cleanly outside the measured setup. Every controlled run used open-weight Qwen and DeepSeek in non-thinking mode at temperature 0.0. The authors also cut the ProgramBench step limit "from the original 1,000 steps to 300 steps to reduce evaluation cost". The authors name dataset coverage as their main external threat ([Hu et al., arXiv:2609.32459v1](https://arxiv.org/abs/2609.32459v1)).

## Key Takeaways

- Ask what the task looks like before asking whether the model is strong enough. A strong model on fixed-workflow repair needs less harness; on repository generation it is the one that can use more.
- Alone, structured tools and task-specific subagents gave "the most stable and substantial gains" on both models. The study did not test them as a pair.
- A component that loses points alone may still earn its place. All five together beat every single-component variant, which points to interaction. The study did not run any mixed subset, such as all five minus context compression.
- Check how much your compaction discards. Compression lost points in this study. CliffCompaction reports "maintaining or improving performance on Terminal-Bench" with faithful truncation ([arXiv:2609.26779v1](https://arxiv.org/abs/2609.26779v1)).
- These are priors from one benchmark and two open-weight models. [Isometric harness ablation](isometric-harness-ablation.md) is how you get your own.

## Related

- [Isometric Harness Ablation](isometric-harness-ablation.md) — the method for producing a per-component table on your own stack rather than importing one.
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — the other half of the conditional, treating the backing model as a harness variable.
- [Reasoning Effort Over Tool Scaffolding for First-Try Reliability](reasoning-effort-over-tool-scaffolding.md) — a second study where added capability surface moved the thing it touched but not reliability.
- [Task-Specific Agents vs Role-Based Agents](task-specific-vs-role-based-agents.md) — why the task-specific subagent beats the general one.
- [Stage Elision Before Summarization](../../context-engineering/stage-elision-before-summarization.md) — the context-management evidence behind the window-binding condition.

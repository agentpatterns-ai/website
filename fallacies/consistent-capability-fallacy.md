---
title: "The Consistent Capability Fallacy in LLM Agent Design"
term: "Consistent Capability Fallacy"
description: "Observed success on one task does not predict success on a similar-seeming task. LLM capability is jagged — training data, not skill, determines performance."
tags:
  - human-factors
  - tool-agnostic
  - evals
  - fallacies
aliases:
  - consistent capability fallacy
  - capability generalization fallacy
last_reviewed: 2026-07-07
maturity: established
---

# The Consistent Capability Fallacy

> Capability on one task does not predict capability on a similar-seeming task — LLM performance is jagged, not consistent.

## The belief

When a model handles one complex task well, people generalize: "this model is good at this kind of problem." They then raise the autonomy level for later tasks that look related and skip per-task verification. They are surprised when the model fails a task that seems simpler than one it already passed.

## Why it fails

LLM capability is [jagged, not smooth](https://www.ikangai.com/jagged-agi-superhuman-ai-flaws/). A model may pass an international Math Olympiad problem yet fail at multi-digit long division. The Olympiad problem is well represented in training data as a recognizable pattern. Long division needs an algorithmic process the model approximates poorly.

Training data distribution sets the model's performance profile, not any general "skill level." Perceived difficulty and model difficulty are unrelated. A task that looks harder to a human is sometimes easier for the model, and a task that looks easy is sometimes harder.

Evidence of the failure mode:

- Adding irrelevant details to arithmetic problems causes [17 to 66% accuracy drops](https://www.ikangai.com/jagged-agi-superhuman-ai-flaws/) in models that pass the clean version
- Code that behaves identically, with symbols renamed and structure reshaped, [degrades test pass rates by up to 62.5%](https://arxiv.org/abs/2412.08109) — the model does not generalize to logically identical tasks
- Coding agent success rates vary widely between greenfield and mature codebases, [even within the same domain](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)
- A high leaderboard score, such as 92% on SWE-bench, does not predict outcomes on your own codebase and stack, Microsoft argues — benchmark conditions rarely match a team's actual repository, dependencies, and constraints ([Microsoft: what AI benchmarks are not telling you](https://developer.microsoft.com/blog/what-ai-benchmarks-are-not-telling-you))

Small changes to prompt wording cause [around 15% accuracy swings](https://www.ikangai.com/jagged-agi-superhuman-ai-flaws/). The same input does not yield stable output.

## The compounding risk

The natural language interface masks failures. Models produce confident, plausible-looking output even when the reasoning behind it is wrong. This [creates false confidence](https://undark.org/2026/02/19/opinion-jagged-intelligence/) in both the current output and the model's general reliability. The main danger is not a model that fails obviously. It is people who [overestimate capability](https://undark.org/2026/02/19/opinion-jagged-intelligence/) because they saw it succeed.

## Example

A team delegates a complex architectural refactor to Claude Code. The model handles it well and restructures several services with correct dependency handling. Encouraged, the team delegates a "simpler" task the next sprint: updating multi-step data validation logic across a module. This task fails silently. The model carries an incorrect assumption through every updated path, and the output looks plausible. [No one checks](../patterns/anti-patterns/trust-without-verify.md) because the model "already proved itself" on a harder task.

The architectural task was well represented in training patterns. The validation logic needed algorithmic precision the model approximated badly. From the model's point of view, these were not similar tasks.

## When this backfires

Treating every task as an independent capability question adds overhead. That overhead is not worth it when:

- The task class is narrow and well understood. For highly repetitive, formulaic work, such as generating boilerplate CRUD endpoints against a fixed schema, repeated success shows the training distribution covers the pattern well. [Per-task verification](../verification/incremental-verification.md) still helps, but calibrating autonomy from prior runs is reasonable.
- The domain has high benchmark saturation. Tasks that appear word for word or structurally in widely used public benchmarks, such as standard algorithm implementations and common regex patterns, perform more stably than tasks in unseen problem spaces. The jaggedness is real, but not uniform across all task types.
- Verification cost exceeds failure cost. For low-stakes work that is easy to revert, [scaling re-verification to risk](../verification/risk-based-task-sizing.md) keeps you from slowing delivery more than the occasional failure costs. Weigh this pattern's guidance against your verification budget.

The fallacy is most dangerous for tasks that look familiar but need compositional reasoning the model has not practiced in exactly that combination.

## Key Takeaways

- Capability on task A does not predict capability on task B, even when A and B appear related to a human observer.
- Calibrate autonomy level per task — not per session or per model version.
- Treat each new task type as an independent capability question: verify before raising autonomy.

## Related

- [Trust Without Verify](../patterns/anti-patterns/trust-without-verify.md) — accepting agent output without structural review
- [The Effortless AI Fallacy](../patterns/anti-patterns/effortless-ai-fallacy.md)
- [Agent-Driven Greenfield Product Development](../workflows/agent-driven-greenfield.md) — building a new product agent-first with decomposed tasks and human review at PR boundaries
- [The Task Framing Irrelevance Fallacy](task-framing-irrelevance-fallacy.md) — prompt wording and framing cause measurable performance variation
- [LLM Comprehension Fallacy](llm-comprehension-fallacy.md) — correct output does not imply understanding or reliable capability
- [The AI Knowledge Generation Fallacy](ai-knowledge-generation-fallacy.md) — LLMs recombine training data rather than generate genuinely new knowledge, which shapes where capability gaps appear
- [The Synthetic Ground Truth Fallacy](synthetic-ground-truth-fallacy.md) — AI-generated artifacts reflect model priors, creating compounding errors when used for verification
- [Chain-of-Thought Reasoning Fallacy](chain-of-thought-reasoning-fallacy.md) — visible reasoning traces are generated text, not evidence of correct or reliable reasoning

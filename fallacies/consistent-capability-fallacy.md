---
title: "The Consistent Capability Fallacy in LLM Agent Design"
description: "Observed success on one task does not predict success on a similar-seeming task. LLM capability is jagged — training data, not skill, determines performance."
tags:
  - human-factors
  - tool-agnostic
  - evals
aliases:
  - consistent capability fallacy
  - capability generalization fallacy
---

# The Consistent Capability Fallacy

> Observed success on one task does not predict success on a similar-seeming task.

## The Belief

After a model handles a complex task successfully, practitioners generalize: "this model is good at this kind of problem." They raise the autonomy level for subsequent tasks that appear related, skip per-task verification, and are surprised by failures on tasks that seem simpler than ones the model already passed.

## Why It Fails

LLM capability is [jagged, not smooth](https://www.ikangai.com/jagged-agi-superhuman-ai-flaws/). A model may pass an international Math Olympiad problem but fail at multi-digit long division, because the former is heavily represented in training data as a recognizable pattern, while the latter requires an algorithmic process the model approximates poorly.

The model's performance profile is determined by training data distribution, not by any generalizable "skill level." Perceived difficulty and model difficulty are uncorrelated. Tasks that look harder to a human are sometimes easier for the model — and vice versa.

Concrete evidence of the failure mode:

- Adding irrelevant details to arithmetic problems causes [17–66% accuracy drops](https://www.ikangai.com/jagged-agi-superhuman-ai-flaws/) in models that otherwise pass the clean version
- Semantically equivalent code variants with symbol and structure obfuscation [degrade test pass rates by up to 62.5%](https://arxiv.org/abs/2412.08109) — the model doesn't generalize to logically identical tasks
- Coding agent success rates vary dramatically between greenfield and mature codebases, [even within the same domain](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)

Minor prompt wording changes cause [~15% accuracy swings](https://www.ikangai.com/jagged-agi-superhuman-ai-flaws/); consistent input does not yield stable output.

## The Compounding Risk

The natural language interface masks failures. Models produce plausible-looking, confident outputs even when the underlying reasoning is wrong, which [creates false confidence](https://undark.org/2026/02/19/opinion-jagged-intelligence/) in both the current output and the model's general reliability. The primary danger is not a model failing obviously — it is practitioners [overestimating capability](https://undark.org/2026/02/19/opinion-jagged-intelligence/) based on visible success.

## Example

A team delegates a complex architectural refactoring task to Claude Code. The model navigates it well, restructuring several services with correct dependency handling. Encouraged, the team delegates a "simpler" task the next sprint: updating multi-step data validation logic across a module. This fails silently — the model propagates an incorrect assumption through all updated paths, and the output looks plausible. No one checks because the model "already proved itself" on a harder task.

The architectural task was heavily represented in training patterns. The validation logic required algorithmic precision the model approximated badly. From the model's perspective, these were not similar tasks.

## Key Takeaways

- Capability on task A does not predict capability on task B, even when A and B appear related to a human observer.
- Calibrate autonomy level per task — not per session or per model version.
- Treat each new task type as an independent capability question: verify before raising autonomy.

## Related

- [Trust Without Verify](../anti-patterns/trust-without-verify.md) — accepting agent output without structural review
- [The Effortless AI Fallacy](../anti-patterns/effortless-ai-fallacy.md)
- [Agent-Driven Greenfield Product Development](../workflows/agent-driven-greenfield.md) — building a new product agent-first with decomposed tasks and human review at PR boundaries
- [The Task Framing Irrelevance Fallacy](task-framing-irrelevance-fallacy.md) — prompt wording and framing cause measurable performance variation
- [LLM Comprehension Fallacy](llm-comprehension-fallacy.md) — correct output does not imply understanding or reliable capability
- [The AI Knowledge Generation Fallacy](ai-knowledge-generation-fallacy.md) — LLMs recombine training data rather than generate genuinely new knowledge, which shapes where capability gaps appear
- [The Synthetic Ground Truth Fallacy](synthetic-ground-truth-fallacy.md) — AI-generated artifacts reflect model priors, creating compounding errors when used for verification
- [Chain-of-Thought Reasoning Fallacy](chain-of-thought-reasoning-fallacy.md) — visible reasoning traces are generated text, not evidence of correct or reliable reasoning

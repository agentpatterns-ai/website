---
title: "Stale Thinking Triggers in Saved Instructions"
term: "Stale Thinking Triggers"
description: "A think-carefully line saved in a rules file shifts the thinking threshold on every request. Once the model reasons by default, it duplicates the effort control at a worse grade."
tags:
  - anti-pattern
  - instructions
  - cost-performance
  - claude
aliases:
  - stale thinking trigger instruction
  - think carefully line in CLAUDE.md
  - model-boundary instruction staleness
last_reviewed: 2026-10-03
maturity: adopted
---

# Stale Thinking Triggers in Saved Instructions

> A thinking trigger saved in a rules file keeps pushing for more reasoning on every request, long after the model began deciding that itself.

Anthropic's Opus 5.5 playbook tells you to remove "think carefully," "think step by step," and similar lines "from your prompts and your saved instructions" ([Getting the most out of Opus 5.5](https://claude.dev/blog/getting-the-most-out-of-opus-5-5/)). Its reason: "Opus 5.5 always thinks before it replies, and it decides how much." A prompt is cheap to fix. A saved instruction file is the costly place to leave one, and nothing reports when it stops paying.

## When the line has gone stale

Three conditions must hold together.

- The model decides for itself whether to think. Steering thinking says "the model evaluates each request and decides for itself whether to think and how much", and at the Opus 5.5 default of `medium` it "May skip thinking for simple queries." ([Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)).
- The line sits in a saved file, so it reaches every request. "System prompt guidance shifts Claude's thinking threshold for every request in the conversation" ([Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)).
- A calibrated control covers the same job: lowering effort "is usually the better first lever, since it is a calibrated control rather than a wording-sensitive instruction" (same source).

## Why it works

Thinking "is billed as output, so a model that reasons less on the way to the answer costs less" ([What a task costs on Opus 5.5](https://claude.dev/blog/what-a-task-costs-on-opus-5-5/)). Roughly 20K extra thinking tokens across a task runs about $0.40 on Opus 5.5 (same source).

What decayed is the quality half of the trade. On models built with explicit reasoning capabilities, CoT prompting "often results in only marginal, if any, gains in answer accuracy" while it "significantly increases the time and tokens needed to generate a response" ([Prompting Science Report 2, v1](https://arxiv.org/abs/2506.07142v1), abstract). Anthropic's own evidence is "our testing in a chat product", reported with no figures. Removing the line "made replies start sooner, with no clear drop in quality" ([Getting the most out of Opus 5.5](https://claude.dev/blog/getting-the-most-out-of-opus-5-5/)).

## When this backfires

- The line is not inert, so deleting it removes a lever. Anthropic documents "This task involves multistep reasoning. Think carefully before responding." as a phrase that encourages thinking ([Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)). The same page warns that steering Claude to think less often "may reduce quality on tasks that benefit from reasoning" (same source).
- One file drives several models. On models that do not reason by default, "CoT generally improves average performance by a small amount" ([Prompting Science Report 2, v1](https://arxiv.org/abs/2506.07142v1), abstract). A shared file gives up that small average gain on part of the fleet.
- The line suppresses rather than encourages. Keep it. For the system prompt, Anthropic's suppressing wording is "Extended thinking adds latency and should only be used when it will meaningfully improve answer quality, typically for problems that require multistep reasoning. When in doubt, respond directly." ([Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)). The phrase "Answer directly without deliberating." is the per-message form, for one user turn (same source).
- The file is not the only copy. A skill body, sub-agent prompt, or command template carrying the same line keeps it in the request after you delete it from `CLAUDE.md`.

## Example

The failing lines use the phrases the playbook names; the replacements are its own wording.

**Before** — the trigger saved where it re-sends on every request:

```markdown
# CLAUDE.md

Think carefully and think step by step before you answer.
Show your internal reasoning in the reply so I can follow it.
```

The second line now does worse than nothing. A request to reproduce internal reasoning in the reply "can be declined. It's one of the flag categories" ([Getting the most out of Opus 5.5](https://claude.dev/blog/getting-the-most-out-of-opus-5-5/)), so the instruction now risks a refusal rather than an ignored sentence.

**After** — the trigger deleted, the control named:

```markdown
# CLAUDE.md

Answer directly for a simple question.
Explain why you chose this approach in three sentences.
```

Reach for `/effort` in Claude Code when a task wants more reasoning than the session default, which on Opus 5.5 is medium ([What a task costs on Opus 5.5](https://claude.dev/blog/what-a-task-costs-on-opus-5-5/)).

## Key Takeaways

- Re-read instruction files at a model boundary. A capability change can retire a rule with no error, no warning, and no failing test.
- Sweep by function, not by keyword. Keep the lines that suppress thinking and the lines that still steer a non-reasoning model in the same fleet.
- Grep every surface that reaches the request: rules files, skill bodies, sub-agent prompts, command templates.
- Pair a deletion with an effort setting. Removing the encouragement without raising effort lowers thinking frequency on the work that wanted it.
- Treat a request for the model to reproduce its reasoning in the reply as a defect to fix now, not stale text to tidy later.

## Related

- [Deliberation-Inducing Cues That Multiply Reasoning Cost](deliberation-inducing-prompt-cues.md) — the cost of adding such a cue to a prompt, measured, where this page covers one left behind in a file
- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — the same decay with code drift as the ageing force rather than model capability
- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](../../instructions/rule-lifecycle-metadata.md) — the expiry condition that would have flagged this rule for removal
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — the tool-level version, where mid-stream reasoning is applied regardless of fit
- [CoT Robustness in Code Generation](../../verification/cot-robustness-code-generation.md) — why a step-by-step instruction was never strictly additive, even before models reasoned by default

---
title: "Comment Content as Code-Generation Context"
term: "Self-Emitted Comments"
description: "A model reads its own comments as context for the code that follows; only comment content correctness moves pass@1, and a comment written for a different problem costs 20.8%."
aliases:
  - self-emitted comments
  - comment content effect
  - model-written comments as context
tags:
  - context-engineering
  - technique
  - code-generation
  - arxiv
  - tool-agnostic
last_reviewed: 2026-09-10
maturity: emerging
---

# Comment Content as Code-Generation Context

> A comment moves pass@1 through the solution content it carries; a comment written for a different problem costs 20.8%.

A model that writes a comment before writing code then decodes that code conditioned on the comment. The comment helps only when it describes a correct solution. Comment volume, comment format, and comment intent do not track pass@1 at all. Pan and colleagues established this by prefilling weak models with comment blocks lifted from stronger models' solutions to the same problems, holding every other decoding parameter fixed ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).

## What the controlled swap measured

Four weak recipients (Gemma-4-E4B-IT, Seed-Coder-8B, Qwen3-8B, CodeGeeX4-9B) received comment blocks written by three stronger sources (Grok-4.1-Fast, Gemini-3.1-Flash-Lite, Claude-Opus-4.7) on the same LiveCodeBench v6 problems. Every number below is the average across those 12 recipient-source pairs ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).

| Comment block the recipient receives | Change in pass@1 |
|---|---|
| Describes a solution that passes the tests | +17.2% |
| Describes a solution that failed | no reliable change |
| Written for a different problem | -20.8% |
| Length-matched random text | -17.9% |

Read the bottom two rows together. A coherent comment about the wrong problem costs more than random text of the same length. That is what separates this from the standing advice to keep comments current. A stale or copy-pasted comment block is not dead weight in the window; it is worse than noise.

The observational half of the study found no usable signal in comment style. Across an 88-model pool on LiveCodeBench v6, the strongest per-model correlation between comment format and pass@1 is 0.32, and the trend for comment intent does not survive multiple-comparison correction ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).

## Why it works

The comment block is a prefix in the decoding context, so the code tokens that follow are generated conditioned on it. Correct solution content narrows the distribution toward a passing program. Incorrect content narrows it just as effectively toward a failing one, which is why the wrong-problem arm is a cost rather than a wash.

Two controls rule out surface form as the cause. Form is held identical between the correct arm and the wrong arm, and corrupting a single step of an otherwise-correct block removes the lift on the same problems. Order barely matters either. Shuffled comments still retain +11.7% of the +17.2% lift, which the authors read as comment lines "functioning as local hints" rather than an ordered derivation ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).

## When this backfires

- You are already running your strongest model. The +17.2% is defined by a gap between a stronger source and a weaker recipient. Asking the recipient to write comparable comments from its own prompt recovers about 24% of the effect at best, and reaches significance for one of the four recipients ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).
- You set a fleet-wide comment policy without measuring. An instruction to emit no comments cost Gemma-4-E4B-IT 14.5% of pass@1 while lifting GPT-OSS-120B ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)). The sign belongs to the receiving model, not to the instruction.
- The task sits outside the model's reach. The authors flag that recipients sit near the floor on the problems their source also failed, so the no-gain result there cannot separate wrong content from an unsolvable problem ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).
- Your codebase is not a benchmark. The intervention replicates on the RepoClassBench C# and Java splits, with no cell moving significantly against the LiveCodeBench result ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)). Neither benchmark resembles a large repository carrying years of drifted comments, so the size of the wrong-problem penalty in production is unmeasured.
- The evidence is one preprint. [arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1) was submitted on 8 September 2026 and has no independent replication.

## What to do with it

Run the none-versus-base contrast the authors propose ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)) before writing any comment policy into a system prompt. Generate with the model's default commenting, generate again with comments suppressed, and compare pass rates on your own tasks. That one A/B tells you whether suppression costs your model pass@1 or buys it. Until you have run it, a token-saving rule that bans model comments is an untested bet on pass rate.

Treat comments describing other problems as context to remove, not context to ignore. A block copied above a new function, a docstring left over from a refactor, a commented-out earlier approach. Each of these sits in the prefix the model conditions on, and the measured direction of that conditioning is down.

## Key Takeaways

- Judge a comment in the window by whether its content is correct, not by whether it is present, well formatted, or explanatory.
- Delete comments that describe a different problem before you generate against the file. That arm cost 20.8% of pass@1, worse than length-matched random text at 17.9% ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).
- Do not expect a "plan first, then code" instruction to substitute. Self-prompting recovered at most 24% of what an external correct comment block gave the same model ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).
- Measure before banning comments to save output tokens. Suppression moved pass@1 in opposite directions across models ([arXiv:2609.09242v1](https://arxiv.org/abs/2609.09242v1)).
- The lift came from handing weak models a stronger model's comments, so on your strongest model the cost is the part that transfers, not the gain.

## Related

- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md) — human-authored comments as discoverable hints, the complementary case where a person supplies the content.
- [Deterministic Anchoring: Static Facts as Stable Context](deterministic-anchoring.md) — inline comments carrying call-graph facts, aimed at run-to-run stability rather than pass rate.
- [Source Code Minification for State-in-Context Agents](source-code-minification-trade-off.md) — the token-versus-accuracy trade of stripping comments and docstrings from agent input.
- [Context Poisoning: When Hallucinations Become Premises](../patterns/anti-patterns/context-poisoning.md) — the same conditioning failure at session scale, where one wrong premise steers every later step.
- [Token-Efficient Code Generation](../token-engineering/token-efficient-code-generation.md) — output-token levers, of which comment suppression is one with a measurable pass-rate cost.

---
title: "Language Choice as an Agent Token-Cost Lever"
description: "Coding agents spend up to 1.69x more tokens in OCaml than Python at matched difficulty, but the effect is second-order to task difficulty and does not hold for every language and model pair."
tags:
  - token-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
aliases:
  - per-language token multiplier
  - language token-cost multiplier
last_reviewed: 2026-07-28
maturity: emerging
---

# Language Choice as an Agent Token-Cost Lever

> Language choice shifts agent token cost up to 1.69x — OCaml versus Python at matched difficulty — through compile loops, not harder thinking.

Treat a per-language token multiplier as a diagnostic, not a language-selection rule. The effect is real and survives difficulty controls, but three conditions bound it: your model has to show the effect, task difficulty has to be held constant, and the language has to be something you can actually change. Miss any one and the number tells you nothing you can act on.

## What the measurement shows

[Wu, Anderson and Guha](https://arxiv.org/abs/2607.22807v1) ran five models across Python, Java, Rust and OCaml on MiniLCB — 100 problems sampled from LiveCodeBench v6's 499 language-agnostic tasks, 2,000 agent sessions in total. They fitted linear mixed-effects models with language as a fixed effect and problem identity as a random effect, so the ratios below are difficulty-controlled.

| Language vs Python | Range across the five models |
|---|---|
| OCaml | 1.28x – 1.69x |
| Rust | 1.07x – 1.57x |
| Java | 0.85x – 1.34x |

The direction is not uniform. Java is the only language that can come out cheaper than Python — Gemma writes it at 0.85x — and several Rust results are not statistically significant ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807v1)). So "lower-resource costs more" is a tendency, not a law you can assume for your stack.

Accuracy barely moves with language, with Gemma on OCaml the exception ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807)). That makes this a cost lever rather than a capability one — the same shape as [code cleanliness](code-cleanliness-agent-cost-lever.md), which cut tokens without changing pass rate.

This is the difficulty-controlled per-task view. For the complementary project-level view — how language choice moves an artifact's quality ceiling and total run cost across 17 languages — see [Programming Language Choice Still Shapes Agent Artifacts](../human/programming-language-choice-shapes-agent-artefacts.md).

## Why it works

The agent burns tokens failing to compile, not thinking harder. On OCaml, 92% of failed intermediate solutions are compile-time errors and only 8% are wrong answers, so the agent rarely gets far enough to learn whether its algorithm was right ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807v1)). Escape from the loop is a language-learning event: "fix bug" accounts for 60% of breakthrough transitions, the moment the agent finally names a concrete OCaml-specific type error and the unchanged algorithm passes. Gemma looped on stuck states 1,196 times, 31% of them byte-identical rewrites.

Two secondary behaviors add tokens. Agents prototype in Python before translating — Qwen spent 12 turns on one problem in Python before writing OCaml, and Sonnet spent 23 turns on another ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807)). Agents also plan inside code comments rather than in prose.

Upstream, the cause is training-data scarcity. Code LLMs produce strong results on well-represented languages such as Python, Java and JavaScript, and struggle on low-resource languages with limited training data ([Joel et al., arXiv:2410.03981](https://arxiv.org/abs/2410.03981)).

The shape of the overspend inverts by language, which is what makes the multiplier a diagnostic. Gemma spends 3,554 median output tokens polishing an already-passing Python solution against 1,173 for OCaml ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807v1)). Python spend is cosmetic churn after success; OCaml spend is compile churn before it. Those two failure modes need different fixes.

## When this backfires

- The language is not a free variable. In an existing repository the language was chosen years before an agent touched it, and a measured multiplier produces a recommendation nobody can act on.
- Difficulty is not matched. The paper reports an intraclass correlation of 0.80–0.97, so problem identity explains most of the token variance ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807)). Comparing raw per-language spend across a real backlog measures the backlog, not the language.
- You chase 1.7x while carrying 30x. On SWE-bench Verified, identical tasks vary by up to 30x in total tokens across eight frontier models, and higher spend does not correlate with better accuracy ([Bai et al., arXiv:2604.22750](https://arxiv.org/abs/2604.22750v2)). Harness and loop design move more than language does.
- The result may not reach your work. MiniLCB tasks are self-contained competitive-programming problems with visible tests, and the authors say the findings may not generalize to repository-scale software engineering ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807)), where accumulated input tokens dominate spend ([arXiv:2604.22750](https://arxiv.org/abs/2604.22750)).
- The gap is a moving target. Fine-tuning and in-context learning both shift low-resource performance, with effectiveness depending on model size ([Giagnorio et al., arXiv:2501.19085](https://arxiv.org/abs/2501.19085)). A multiplier you measure this quarter decays as models and harnesses improve.

The authors are explicit that the paper is not language-selection advice: the title is a joke, and the stated intent is to understand why agents overspend in low-resource languages so that better multilingual agents can be built ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807)).

## Example

A team runs agents against a Rust service and a Python service and sees the Rust runs costing more per merged change. The multiplier tells them where to look, not what to rewrite.

The mechanism says the Rust spend should concentrate before the first passing state, in compile-error loops. So instrument that split first:

```bash
# Cheap proxy for the paper's snapshot analysis: how many turns end in a
# compile failure versus a test failure, per language.
cargo check --message-format=short   # fast typecheck, no codegen, no test run
```

If compile failures dominate, the fixes are all harness-side, not language-side. They are an instance of [feedback as capability equalizer](../patterns/agent-design/feedback-capability-equalizer.md) — raising feedback quality beats changing the model, or here the language:

- Put the fast typechecker in the agent loop (`cargo check`, not `cargo build`) so a type error costs one short turn instead of a full build.
- Return the compiler's own diagnostic text verbatim. Rust and OCaml error messages name the fix, and truncating them is what forces the byte-identical retry loop the paper measured.
- Load idiom examples and type signatures for the crates in play, which attacks the training-data scarcity directly rather than routing around it.

Rewriting the service in Python to capture at most 1.57x would trade a bounded token cost for an unbounded engineering one.

## Key Takeaways

- At matched difficulty, coding agents spend 1.28x–1.69x more tokens in OCaml than Python and 1.07x–1.57x more in Rust; Java ranges 0.85x–1.34x and can be cheaper than Python ([Wu et al., 2026](https://arxiv.org/abs/2607.22807v1))
- The mechanism is compile-error looping, not deeper reasoning — 92% of failed OCaml snapshots are compile-time errors ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807v1))
- Accuracy is largely unaffected by language, so this is a cost lever and not a capability one ([arXiv:2607.22807](https://arxiv.org/abs/2607.22807))
- Problem difficulty dominates token variance (ICC 0.80–0.97), and within-task variance reaches 30x on repository-scale benchmarks — both larger than the language effect ([arXiv:2604.22750](https://arxiv.org/abs/2604.22750v2))
- Act on the diagnosis, not the multiplier: a fast typechecker in the loop, verbatim compiler diagnostics, and idiom examples in context attack the mechanism without changing language

## Related

- [Programming Language Choice Still Shapes Agent Artifacts](../human/programming-language-choice-shapes-agent-artefacts.md) — the project-level counterpart: quality ceiling and total run cost across 17 languages
- [Feedback as Capability Equalizer](../patterns/agent-design/feedback-capability-equalizer.md) — the principle behind the fix: better feedback beats a bigger model, or a different language
- [Code Cleanliness as an Agent Cost Lever](code-cleanliness-agent-cost-lever.md) — the same shape of finding: a real token saving with no pass-rate change
- [Tokenizer Swap Tax: Budgeting for Model Migrations That Change Token Counts](tokenizer-swap-tax.md) — the other multiplier that moves cost without any code change
- [Harness-Controlled Token Economics (The Harness Effect)](harness-token-economics.md) — the larger lever this page defers to when compile loops are not the bottleneck
- [Language Selection Scored on Review Cost](../human/language-selection-review-cost.md) — the human-cost view of the same decision, with the same free-variable caveat

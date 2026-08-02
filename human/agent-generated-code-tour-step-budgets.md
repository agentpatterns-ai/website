---
title: "Step Budgets and Trust in Agent-Generated Code Tours"
description: "Agent-generated code tours work for debugging unfamiliar code when they stay near five steps, scale description length to each segment, and are graded by people rather than by a second model."
tags:
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - agent-generated code tour
  - LLM-generated code tour
last_reviewed: 2026-08-02
maturity: emerging
---

# Step Budgets and Trust in Agent-Generated Code Tours

> Agent-generated code tours help newcomers debug unfamiliar code when they stay near five steps and scale description length to each segment.

A code tour is a checked-in sequence of steps, each bound to a file and line and carrying a written description. The [microsoft/codetour](https://github.com/microsoft/codetour) extension stores that sequence as JSON under `.tours` or `.vscode/tours`, so an agent can write one like any other repository artifact. The shaping rules below come from a study of 26 developers reading 26 tours generated from real Java bugs by three open-weight models ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1)).

## When this applies

The evidence is narrow, so treat the advice as conditional. It holds for a reader debugging a specific defect in a codebase they do not know, with an audience skewing junior to mid-level — the cohort the study recruited ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §5.2.3). Outside those conditions it inverts.

## Shaping the tour

Three constraints carried the reader experience.

Budget the steps. Developers "get lost more easily with tours longer than five steps", and one participant reported that "when you are past 4 to 5 steps, you are a bit lost" ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.3.2). Announce the count up front, because a small visible number lowers the cost of starting — "it is less scary when you see there are three steps" ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.3.2).

Scale description length to segment length. "The expected level of detail scales with the code segment length", and five participants found descriptions unnecessary for short segments ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.1.2). A uniform paragraph per step produces restatement on the short ones and thin coverage on the long ones.

Select steps beyond the stack trace. Seven participants "were impeded in their understanding because the sequence was missing a step" — usually a constructor, a branch, or the concrete implementation behind an interface ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.3.4). A generator that walks only the frames in the trace will drop them.

## Why it works

The tour competes for the same working memory the reader needs for the unfamiliar code, so its structure is a cost paid before any explanation lands. A short sequence holds that cost down, and scaling description length to segment length spends what is left where the code is dense rather than on narrating a two-line getter. The study's participants named both halves — the step-count ceiling, and the complaint that short-segment descriptions merely restated the code ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.3.2, §4.1.2).

## Perceived authorship moves trust

Readers discounted what looked machine-written: "Descriptions that seemed human-written were seen as trustworthy, meanwhile those seen as AI-authored were distrusted" ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.5.1). The wrong response is to tune the prose until it passes as human. Labeling AI content does reduce its perceived accuracy, but the effect is bounded and shrinks when AI use is made more salient, not less, on a nationally representative sample of 3,861 respondents ([arXiv 2506.16202v2](https://arxiv.org/abs/2506.16202v2)). Reader skepticism also pays: developers who trusted an AI coding assistant less produced code with fewer security vulnerabilities ([arXiv 2211.03622v3](https://arxiv.org/abs/2211.03622v3)). Spend the effort on verification affordances — the file and line each claim rests on, and a link to the commit that fixed the bug — not on disguising the author.

## Do not let a model grade the tour

The cheapest quality gate is the one that fails. In the study, "sycophancy (excessive praise), confabulations and incoherence across the pipeline impede trust"; one judge praised duplicate steps as serving "to emphasize a critical point" on a tour the developers themselves rated poorly ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.5.2). That is expected behavior, not a bad run: judge decisions shift with prompt phrasing on unchanged code ([arXiv 2604.16790](https://arxiv.org/abs/2604.16790)), and LLM judges rate familiar, low-perplexity text higher than humans do ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)) — rewarding the fluent restatement readers rated worst. Grade tours by watching a person use one, and keep any model scoring under the [human spot-checking discipline](../workflows/llm-as-judge-evaluation.md) rather than treating it as the gate. The underlying failure is [the yes-man agent](../patterns/anti-patterns/yes-man-agent.md).

## When this backfires

- Experienced readers or a familiar codebase. Five participants found per-step descriptions unnecessary on short segments, and the cohort skewed junior to mid-level ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.1.2, §5.2.3). Narration that orients a newcomer is noise to someone who already holds the model.
- Cases where the causal chain matters more than the reading cost, such as security review, incident forensics, and compliance walkthroughs. A five-step ceiling drops steps the reader came for, and the same study already found missing steps to be a live problem.
- Conflicting reader preferences. The study found mutually exclusive preferences over imperative versus declarative mood, and seven participants wanted more concise descriptions while others wanted more ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.4.2, §4.1.1). One tour cannot satisfy both, and per-reader generation costs more than the artifact it produces.
- Stacks and models outside the study. It covers three open-weight models and a dataset of 110 Java bugs mined from 2025 GitHub commits, with participant quotes reconstructed from notes rather than recordings ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §5.2.1, §5.2.3).
- Tours used as a substitute for reading the code. That is [comprehension debt](../patterns/anti-patterns/comprehension-debt.md) with a nicer interface.

## Example

A CodeTour step is an object carrying a `file`, a `line`, and a markdown `description`, and the tour's `title` is settable directly in the JSON ([microsoft/codetour](https://github.com/microsoft/codetour)). The three rules land as constraints on a generator emitting that shape:

- Cap the `steps` array at about five, and write the count into the tour `title` so the reader sees it before opening step one.
- Set each `description` length from the span of its own step's segment, not from a fixed per-step template.
- Seed the step list from the stack trace, then add the constructors, branches, and concrete implementations the trace does not contain.

The third constraint is the one a trace-following generator skips, and it covers the class of step seven participants reported missing ([arXiv 2607.26987v1](https://arxiv.org/abs/2607.26987v1), §4.3.4).

## Key Takeaways

- Keep an agent-generated debugging tour near five steps and declare the count, because readers reported getting lost past that point.
- Scale each description to the length of the code segment it covers; a uniform paragraph per step restates short segments and under-explains long ones.
- Select steps beyond the stack trace — constructors, branches, and concrete implementations were the steps readers found missing.
- Readers discount prose they can tell was machine-written. Answer that with verifiable file-and-line provenance, not with prose tuned to pass as human.
- Do not use a second model to grade tour quality; judge verdicts track surface fluency and prompt phrasing rather than reader value.
- The advice is conditional on unfamiliar-codebase debugging with mixed-experience readers, and it inverts for experts and for complete-chain use cases.

## Related

- [Agent-Generated Onboarding Guide as a Durable Artifact](../workflows/agent-generated-onboarding-guide.md) — the whole-repository sibling to a per-bug tour, with the same review discipline
- [Marking Which Artifacts Are for Humans or Agents (Landmarking)](landmarking-human-vs-agent-artifacts.md) — declaring authorship and readership of a repository artifact, the disclosure side of the trust finding
- [LLM-as-Judge Evaluation with Human Spot-Checking](../workflows/llm-as-judge-evaluation.md) — the general discipline for the model-grading problem this page hits on tour quality
- [When Developers Understand Less of Their Own Codebase](../patterns/anti-patterns/comprehension-debt.md) — the failure mode when a tour replaces reading the code
- [Managing Cognitive Load and AI Fatigue for Sustainable Agent Use](cognitive-load-ai-fatigue.md) — the broader working-memory budget a step ceiling is spending against

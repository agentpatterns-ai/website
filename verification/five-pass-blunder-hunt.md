---
title: "Five-Pass Blunder Hunt: Repeated Critique Passes for Plans"
term: "Five-Pass Blunder Hunt"
description: "Run the same critique prompt five times on a plan or spec to force each pass deeper into structural and logical problems the first pass normalizes."
tags:
  - testing-verification
  - workflows
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-12
maturity: adopted
---

# Five-Pass Blunder Hunt

> A Five-Pass Blunder Hunt runs one critique prompt repeatedly over a plan; each pass normalizes its own findings, so later passes reach deeper structural flaws.

## The problem

A single review pass catches surface issues and stops. The model that wrote the content is also the reviewer, so it shares the [same blind spots](chain-of-verification-coding-agents.md): it finds a satisfying number of issues, declares the document fine, and moves on.

The problems that remain — inconsistencies, rationale gaps, dependency conflicts — need the whole document held in mind at once. A single-pass reviewer normalizes them.

## How the technique works

Run the identical critique prompt five consecutive times on the same document:

```
Review this plan for logical inconsistencies, scope creep, decision rationale gaps,
and structural flaws. For each issue, state: what the problem is, where it occurs,
and what the fix is.
```

Each pass does two things:

1. Normalizes its own findings — it resolves or acknowledges them, shifting focus away.
2. Shifts the attention distribution — with resolved issues de-emphasized, the next pass is more likely to attend to material it overlooked before.

The result is a progressive descent into document quality. Early passes surface the visible issues — missing sections, contradictions, unclear terms. Later passes reach structural and logical flaws obscured until the surface problems cleared.

## Convergence is the stopping criterion

Five is a heuristic. The real signal is convergence:

- Findings-per-pass count is decreasing — each pass finds fewer issues than the last
- Output similarity is increasing — consecutive critique responses resemble each other
- No new categories of problem appear — only refinements of issues already identified

Stop when a pass finds nothing new. If you reach pass five first, continue until one does. Beyond five or six passes [returns diminish to noise](../loop-engineering/convergence-detection.md) — reframe the document or accept the remaining findings.

Oscillation is a stop signal. If the model alternates between contradictory assessments, further passes will not resolve it. Reframe the section and restart.

## Why the same prompt

Varying the prompt introduces a confound: new findings may come from a different review angle, not the document. Same-prompt repetition keeps the convergence signal clean — findings per pass measure document quality, not prompt novelty.

Different-prompt review (alternating reviewer framings) is a separate technique for cross-cutting concerns, with a different signal.

## Scope

Most effective on artifacts that:

- Are produced by agents before implementation begins
- Contain implicit dependencies between sections
- Have no formal correctness verifier (plans, specs, architectural documents)

It does not apply to outputs with externally verifiable correctness — code with tests, structured data against a schema. Use deterministic validators instead. [^1]

## When this backfires

False convergence. If earlier passes resolve formatting and terminology, the model may report clean passes while structural logic stays flawed. Superficial similarity is not correctness — read the pass-5 output, do not just count findings.

Anchoring to prior pass output. Each pass implicitly carries the prior exchange's context. The model may anchor to the pass-1 framing and miss a different class of problems. When this happens, run one differently-framed pass to break the anchor before resuming.

Oscillation on genuinely ambiguous sections. Pass N flags a section, N+1 approves it, N+2 flags it again. This is not a quality signal — the section is genuinely ambiguous, and further passes will not resolve it. It needs human clarification or explicit scoping.

Not appropriate for formally verifiable outputs. For code with a test suite, SQL with a schema, or structured data with a validator, use those tools directly. [^1] Critique passes on verifiable artifacts produce false positives that waste cycles.

Self-critique can collapse on hard reasoning tasks. On Game of 24, graph coloring, and STRIPS planning, LLM self-critique loops performed worse than a single guess, because errors in verification, critique generation, and critique consideration stack. [^2] Use five-pass on under-specified design artifacts where the model's structural-inconsistency detection is reasonably reliable — not where a sound external verifier exists.

Self-refinement can amplify self-bias instead of reducing it. The premise that later passes go deeper assumes each pass corrects the last. Counter-evidence cuts the other way: across six LLMs, self-refinement amplified the model's bias toward its own generations, and only larger models or external feedback reversed it. [^3] Treat decreasing findings-per-pass as a candidate convergence signal, not proof of correctness, and bring in an external reviewer when stakes justify it.

## Example

A plan for a multi-agent coding task has been drafted. Before handing it to the implementation agents:

```
# Pass 1 critique prompt
Review this implementation plan for logical inconsistencies, scope creep, decision
rationale gaps, and structural flaws. For each issue found: state what it is,
where it occurs, and how to fix it.

[paste plan]
```

Pass 1 returns 18 issues: undefined interfaces, missing error handling sections, ambiguous ownership assignments.

After resolving those, Pass 2 returns 9 issues: two dependency cycles that only became visible once the interface ambiguity was removed.

After resolving those, Pass 3 returns 4 issues: scope assumptions that contradict each other in different sections.

Pass 4 returns 1 issue: a subtle inconsistency in the rollback strategy.

Pass 5 returns nothing new. Stop.

## Companion technique: count inflation

When a pass returns fewer findings than expected, re-prompt with an inflated target:

```
This document has at least 40 issues. Find them.
```

Models stop after a satisfying number of issues; a higher target prevents premature satisfaction. Count inflation addresses thoroughness within a pass; five-pass addresses depth across passes.

## Key Takeaways

- A single pass normalizes problems — reviewer and author share blind spots
- Five same-prompt passes force progressive descent into document quality
- Convergence signals (decreasing findings, increasing similarity) are the stopping criterion
- Oscillation means stop and reframe
- Applies to artifacts without formal verifiers — plans, specs; not code with test suites

## Related

- [Pre-Completion Checklists](pre-completion-checklists.md)
- [Incremental Verification](incremental-verification.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Chain-of-Verification for Coding Agents](chain-of-verification-coding-agents.md) — sibling self-review technique: generate verification questions, answer them independently, revise; complements same-prompt five-pass with question-based diversification
- [Convergence Detection in Iterative Refinement](../loop-engineering/convergence-detection.md) — three-signal model (change velocity, output size, content similarity) underlying the stopping criterion

[^1]: Valmeekam, Marquez, Kambhampati (2023), [Can Large Language Models Really Improve by Self-critiquing Their Own Plans?](https://arxiv.org/abs/2310.08118) — self-critique diminishes plan-generation performance compared to external sound validators for formally verifiable planning tasks.

[^2]: Stechly, Valmeekam, Kambhampati (2024), [On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks](https://arxiv.org/abs/2402.08115) — across Game of 24, graph coloring, and STRIPS planning, self-critique loops exhibited significant performance collapse relative to sound external verification; errors in verification, critique generation, and critique consideration compound.

[^3]: Xu et al. (2024), [Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement](https://arxiv.org/abs/2402.11436) — across six LLMs and three task families, self-bias (the tendency to favor one's own generation) is prevalent, and the self-refine pipeline amplifies it; larger models and accurate external feedback are what reduce it.

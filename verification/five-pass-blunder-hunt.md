---
title: "Five-Pass Blunder Hunt: Repeated Critique Passes for Plans"
description: "Run the same critique prompt five times on a plan or spec to force each pass deeper into structural and logical problems the first pass normalises."
tags:
  - testing-verification
  - workflows
---

# Five-Pass Blunder Hunt

> Run the same critique prompt five times on a plan or spec. Each pass normalises the issues it finds; subsequent passes surface structural and logical flaws the first pass never reaches.

## The Problem

A single review pass catches surface-level issues and stops. The model that wrote the content is also the reviewer: it shares the same blind spots and framing. It finds a satisfying number of issues, declares the document satisfactory, and moves on.

The problems that remain — inconsistencies, rationale gaps, dependency conflicts — require holding the whole document in mind simultaneously. A single-pass reviewer normalises them.

## How the Technique Works

Run the identical critique prompt five consecutive times on the same document:

```
Review this plan for logical inconsistencies, scope creep, decision rationale gaps,
and structural flaws. For each issue, state: what the problem is, where it occurs,
and what the fix is.
```

Each pass does two things:

1. **Normalises its own findings** — issues it surfaces are resolved or acknowledged, shifting focus away from them
2. **Shifts the attention distribution** — with resolved issues de-emphasised, the model's subsequent pass is more likely to attend to previously overlooked material

The result is a progressive descent into document quality. Early passes surface the most visible issues — missing sections, obvious contradictions, unclear terminology. Later passes reach structural and logical flaws that were obscured until the surface problems were cleared.

## Convergence Is the Stopping Criterion

Five is a heuristic. The real signal is convergence:

- **Findings-per-pass count is decreasing** — each pass finds fewer issues than the last
- **Output similarity is increasing** — consecutive critique responses resemble each other
- **No new categories of problem appear** — only refinements of already-identified issues

Stop when a pass finds nothing new. If you reach pass five before convergence, continue until a pass finds nothing new. Beyond five or six passes, returns typically diminish to noise — reframe the document or accept the remaining findings rather than continuing.

**Oscillation is a stop signal.** If the model alternates between contradictory assessments, further passes will not resolve it. Reframe the section and restart.

## Why the Same Prompt

Varying the prompt introduces a confound: new findings may come from a different review angle rather than from the document itself. Same-prompt repetition produces a clean convergence signal — findings per pass measure document quality, not prompt novelty.

Different-prompt review (alternating reviewer framings) is a separate technique for cross-cutting concerns, but it produces a different kind of signal.

## Scope

Most effective on artefacts that:

- Are produced by agents before implementation begins
- Contain implicit dependencies between sections
- Have no formal correctness verifier (plans, specs, architectural documents)

Does not apply to outputs with externally verifiable correctness — code with tests, structured data against a schema. Use deterministic validators instead. [^1]

## When This Backfires

**False convergence.** If earlier passes resolve formatting and terminology issues, the model may report clean passes even when structural logic remains flawed. Convergence on superficial similarity is not the same as convergence on correctness — read the pass-5 output rather than just counting findings.

**Anchoring to prior pass output.** Each critique pass receives the document plus (implicitly) the context of prior exchange. The model may anchor to the same framing used in pass 1 and miss an entirely different class of problems. When this occurs, run one pass with a differently-framed prompt to break the anchor before resuming.

**Oscillation on genuinely ambiguous sections.** Pass N flags a section; pass N+1 approves it; pass N+2 flags it again. This is not a document quality signal — the section is genuinely ambiguous. Continuing passes will not resolve the ambiguity; the section needs human clarification or explicit scoping.

**Not appropriate for formally verifiable outputs.** For code with a test suite, SQL with a schema, or structured data with a validator, use those tools directly. [^1] Multiple critique passes on verifiable artefacts produce false positives that waste resolve cycles.

## Example

A plan document for a multi-agent coding task has been drafted. Before handing it to the implementation agents:

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

## Companion Technique: Count Inflation

When a pass returns fewer findings than expected, prompt with an inflated target:

```
This document has at least 40 issues. Find them.
```

Models stop after finding a satisfying number of issues. A higher target prevents premature satisfaction. Count inflation addresses thoroughness within a single pass; five-pass addresses depth across passes.

## Key Takeaways

- A single pass normalises problems — reviewer and author share blind spots
- Five same-prompt passes force progressive descent into document quality
- Convergence signals (decreasing findings, increasing similarity) are the stopping criterion
- Oscillation means stop and reframe
- Applies to artefacts without formal verifiers — plans, specs; not code with test suites

## Related

- [Pre-Completion Checklists](pre-completion-checklists.md)
- [Incremental Verification](incremental-verification.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Evaluator-Optimizer](../agent-design/evaluator-optimizer.md) — broader pattern: one LLM generates, another evaluates; five-pass is a single-model instance
- [Convergence Detection in Iterative Refinement](../agent-design/convergence-detection.md) — three-signal model (change velocity, output size, content similarity) underlying the stopping criterion

[^1]: Olausson et al. (2023), [Can Large Language Models Really Improve by Self-critiquing Their Own Plans?](https://arxiv.org/abs/2310.08118) — self-critique diminishes performance compared to external validators for formally verifiable planning tasks.

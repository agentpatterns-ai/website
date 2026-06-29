---
title: "Stage-Targeted Prompt Structure for Pull Request Outcomes"
term: "Stage-Targeted Prompt Structure"
description: "Specificity, Context, and Verification each move a different stage of the LLM-assisted PR pipeline — diagnose which stage is failing, then raise that dimension."
aliases:
  - stage-based prompt quality
  - context specificity verification framework
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-19
maturity: emerging
---

# Stage-Targeted Prompt Structure for Pull Request Outcomes

> Prompt structure splits into Specificity, Context, and Verification — each moves a different pull request stage; diagnose the failing stage, then raise that dimension.

A stage-based study of 265 manually validated developer-ChatGPT interactions extracted from self-admitted AI-assisted pull requests found that prompt structure does not have a single "quality" axis — its effects split across three dimensions that each dominate a different stage of the human-LLM-PR pipeline ([Sserunjogi, Ogenrwot & Businge, 2026](https://arxiv.org/abs/2606.19644)). Apply this only when the human is driving generation through prompts; in agent-loop mode, the harness mediates context regardless of the initial prompt (see When this backfires below).

## The three dimensions

The framework codes every prompt against three orthogonal structural surfaces ([Sserunjogi et al., 2026](https://arxiv.org/abs/2606.19644)):

- Context — what you give the model to work against: relevant code snippets, file paths, requirements, constraints, the surrounding system the change has to fit into.
- Specificity — how narrowly the task is scoped: explicit inputs and outputs, named functions, concrete acceptance criteria, the shape the answer should take.
- Verification — how you can cheaply decide whether the output is usable: tests to pass, expected behavior, examples of correct output, evaluability cues.

These are independent — a prompt can be high on one axis and low on the others. The study's LLM-vs-human inter-rater check showed Specificity is the most reliably codeable. Automated assessment systematically under-scores Context, so the study used a hybrid human-LLM annotation strategy ([Sserunjogi et al., 2026](https://arxiv.org/abs/2606.19644)).

## The stage-to-dimension map

The three dimensions do not affect outcomes uniformly. Each dominates a different stage of the pipeline from prompt to merged PR ([Sserunjogi et al., 2026](https://arxiv.org/abs/2606.19644)):

| Stage | Failing if… | Dominant dimension |
|-------|-------------|--------------------|
| Generation — model produces actionable code at all | output is unusable, off-topic, or wrong shape | Specificity (with Context as a strong secondary) |
| Adoption — developer commits or pastes the response | output looks plausible but you keep discarding it | Verification |
| Integration — response actually lands in the PR | code adopted but rejected at review, breaks neighbours | Context |

This produces a directly actionable diagnostic. Instead of asking "is this prompt good?", ask "which stage is failing?":

- The model keeps producing the wrong shape of answer → raise Specificity (name the function, fix the signature, declare the inputs and outputs).
- You keep discarding plausible-looking answers without committing them → raise Verification (paste the failing test, name the expected behavior, give a correct-output example).
- Code gets adopted but breaks the existing codebase at review → raise Context (point at the file, name the patterns it has to follow, link the constraint document).

## Why it works

Each dimension addresses a different bottleneck in the same pipeline, which is why their effects show up at different stages ([Sserunjogi et al., 2026](https://arxiv.org/abs/2606.19644)).

Specificity narrows the model's solution space at generation time. Fewer candidate completions match the constraints, so the first response is closer to actionable code and you have less to discard.

Context gives the model fallback evidence across several surfaces: codebase pointers, requirements, neighbors. When one surface is incomplete, the others still carry signal, so the output embeds into the existing system rather than being merely correct in isolation. The same independent-surfaces mechanism produces the 11.8% vs 0.9% robustness gap between HumanEval (one docstring) and LiveCodeBench (four independent specification layers) measured by [Akli et al. (2026)](https://arxiv.org/abs/2604.24712) and documented in [Multi-Layer Specification Redundancy](multi-layer-specification-redundancy.md).

Verification cues let you cheaply tell a usable response from a plausible-but-wrong one. Adoption rises without raising generation cost because the evaluation step gets cheaper, not the generation step.

## When this backfires

The framework was measured on single-shot, human-driven ChatGPT-PR interactions. Several conditions shrink or reverse its benefit:

- Agent-loop mode dominates over prompt structure. When Claude Code or Copilot's agent mode iterates with the codebase — reading files, re-prompting itself, running tests — the harness mediates Context and Verification regardless of the initial prompt. The human's prompt becomes a smaller share of total context, so three-dimension prompt discipline pays much less. The harness itself is the lever; see [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- More Context can hurt past the attention sweet spot. Stuffing Context past the model's effective attention triggers lost-in-the-middle and [context rot](https://www.understandingai.org/p/context-rot) — extra Context starts degrading Adoption rather than helping it. Strategic curation beats volume.
- Structural controls beat prompt structure when both are available. When a hook, type check, or test suite can deterministically catch the failure mode the Verification dimension is trying to encode, the structural control dominates. See [Hooks vs Prompts](hooks-vs-prompts.md) and the [Prompt Tinkerer Anti-Pattern](../anti-patterns/prompt-tinkerer.md) — endless prompt refinement is a recognized failure mode when the problem is structural.
- Throwaway exploration. Three-dimension prompt overhead is wasted when the goal is to discover whether an approach is feasible at all — there is no PR to integrate into.
- High-density instruction stacks hit the compliance ceiling. Stacking many independent specification layers across all three dimensions pushes the prompt past the [instruction-compliance ceiling](instruction-compliance-ceiling.md) (~68% at high densities per [IFScale](https://arxiv.org/abs/2507.11538)); marginal structure starts being silently ignored regardless of which dimension you raise.

## Example

The same change request, evolved by raising one dimension at each stage of failure. The diagnostic is the stage the previous version failed at. The final prompt below is what survives all three raises — what you would actually paste.

Generation fails (the model produces the wrong shape of refactor):

```text
Refactor this React form.
```

After raising Specificity — Generation passes. The output is plausible, but you keep discarding it without committing:

```text
Refactor the <SignupForm> component at apps/web/src/auth/SignupForm.tsx
to use react-hook-form's useForm hook. Keep the existing field names and
validation messages. The function signature stays (props: SignupProps) =>
JSX.Element. Return one component, no new exports.
```

After raising Verification — Adoption passes. The change is committed, but PR review rejects it for breaking a codebase convention the model could not have known:

```text
Refactor the <SignupForm> component at apps/web/src/auth/SignupForm.tsx
to use react-hook-form's useForm hook. Keep the existing field names and
validation messages. The function signature stays (props: SignupProps) =>
JSX.Element. Return one component, no new exports.

The existing snapshot test at apps/web/src/auth/__tests__/SignupForm.test.tsx
must continue to pass. Also: pressing Enter inside any text input still submits
the form, and pasting an email with surrounding whitespace still trims it
before validation.
```

After raising Context — the final prompt, ready to paste:

```text
Refactor the <SignupForm> component at apps/web/src/auth/SignupForm.tsx
to use react-hook-form's useForm hook. Keep the existing field names and
validation messages. The function signature stays (props: SignupProps) =>
JSX.Element. Return one component, no new exports.

The existing snapshot test at apps/web/src/auth/__tests__/SignupForm.test.tsx
must continue to pass. Also: pressing Enter inside any text input still submits
the form, and pasting an email with surrounding whitespace still trims it
before validation.

This codebase uses react-hook-form via the wrapper at
apps/web/src/lib/forms/useTrackedForm.ts which adds analytics. Use that
wrapper, not useForm directly. The wider auth flow's error handling is
documented at apps/web/src/auth/AGENTS.md — error messages have to follow
the conventions there.
```

Each raise targets the stage the previous prompt failed at. Spending the budget on the wrong dimension does not move the right stage.

## Key Takeaways

- Prompt quality is not one axis — Specificity, Context, and Verification each move a different stage of the LLM-assisted PR pipeline ([Sserunjogi et al., 2026](https://arxiv.org/abs/2606.19644)).
- Diagnose by stage: model output unusable → Specificity; plausible output you keep discarding → Verification; output adopted but breaks at review → Context.
- The framework targets human-driven single-shot prompting. Inside agent loops the harness mediates Context and Verification — prompt discipline pays much less.
- Structural controls (hooks, tests, schemas) dominate Verification prompt structure when both are available; see [Hooks vs Prompts](hooks-vs-prompts.md).

## Related

- [Multi-Layer Specification Redundancy as a Robustness Budget](multi-layer-specification-redundancy.md) — independent specification surfaces are *why* layered Specificity and Context survive prompt noise.
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) — companion ceiling: raising Specificity past the constraint-count threshold trades quality back away.
- [The Prompt Tinkerer Anti-Pattern](../anti-patterns/prompt-tinkerer.md) — the diagnostic frame here is the antidote to endless prompt refinement.
- [Hooks vs Prompts: When to Use Each](hooks-vs-prompts.md) — when the Verification dimension is better encoded as a deterministic hook than as prompt text.
- [WRAP Framework for Agent-Ready Issue Descriptions](wrap-framework-agent-instructions.md) — adjacent four-step checklist for issue-driven (rather than PR-driven) prompts.

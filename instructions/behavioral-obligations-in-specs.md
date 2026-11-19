---
title: "Behavioral Obligations in Specs for LLM-Generated Code"
term: "Behavioral Obligations"
description: "Listing invariants, negative requirements, and edge cases in a spec cut failed hidden tests 47.2% in one 72-person study, but the adjusted effect is not significant."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - behavioral obligations in specifications
  - constraint-complete specifications
last_reviewed: 2026-11-19
maturity: emerging
---

# Behavioral Obligations in Specs for LLM-Generated Code

> In one 72-person study, a spec stating behavioral obligations (invariants, negative requirements, edge cases) cut mean failed hidden tests 47.2%; lightweight structure did not.

In a controlled experiment, participants who wrote down behavioral obligations before prompting a chat LLM (invariants, prohibitions, edge cases, and tie-breaks the task text never states) had a mean of 11.38 failed hidden tests out of 33, against 21.54 with no spec ([Onagh and Nayebi, 2026](https://arxiv.org/abs/2611.20195v1), §VII-A, Table I). The 47.2% is a relative drop in mean failed tests in Phase I, not a change in percentage points.

Limits sit beside that figure:

- After adjusting for task, the contrast (IRR 0.48, 95% CI 0.24 to 0.93, p = 0.029) is not significant after Holm correction (p = 0.205).
- The lightweight template's 8.7% cut (19.67 failures) is indistinguishable from zero (IRR 0.95, 95% CI 0.50 to 1.82, p = 0.884).
- The 72 participants were unpaid, convenience-sampled people who had taken requirements-engineering coursework (§III-C). They used the free ChatGPT-4o in chat, on two Python tasks, with no feedback during the experiment (§III-D).
- The authors wrote the 33 hidden tests per task from the task text and "plausible domain rules" (§V).

## What the experiment compared

There were 3 specification levels across 2 tasks, 12 participants per cell, so 24 per level (§III-C). G1 had no spec. G2 filled in a goal, inputs and outputs, Given-When-Then acceptance criteria, constraints, and assumptions. G3 added global invariants, negative requirements, edge cases, and tie-breaking rules (§III-B). Exception handling was a coding category in the analysis, not a G3 template field.

| Level | Mean failed tests of 33 | Adjusted IRR (95% CI) | p / Holm p |
|---|---|---|---|
| G1, no spec | 21.54 | 1.00 | none |
| G2, structured | 19.67 | 0.95 (0.50, 1.82) | 0.884 / 1.000 |
| G3, constraint-complete | 11.38 | 0.48 (0.24, 0.93) | 0.029 / 0.205 |

One G3 submission in 24 (4.17%) passed all 33 tests, and none did in G1 or G2 (§VII-A). Invariant violations fell from 92.71 to 31.46 on the paper's normalized failure scale and unsupported assumptions from 58.33 to 23.61 (Table I).

## Why it works, and how far that goes

The paper's account is that an explicit spec lets the model avoid inferring hidden rules: the gain "appears when the specification makes hidden behavioral rules explicit enough that the LLM no longer has to infer them" (§VII-A). Independent work on LLM application prompts finds that accuracy drops by an average of 22.6% when a requirement goes unstated ([Yang et al., 2026](https://arxiv.org/abs/2505.13360v3)).

Three caveats apply. The treatment bundles "planning and reflection" with spec wording (§X). The G3 template asks for most of the categories the hidden tests label, so part of the gain may be participants guessing the authors' rules. That reading is this page's, not the authors'. Of the specified elements, G2 participants carried 45% into their prompts and G3 participants 60%, and the link to fewer failures was not significant (IRR 0.76, p = 0.543; §VIII-C).

## When this backfires

- Fast executable feedback exists. Participants got none, so the cheapest fix, running tests, was removed by design.
- Requirements change often. G3 had more submissions regress after a requirement change (4 of 24 against 2 of 24 in G2), though each lost less behavior (§VII-C). The authors call this an "ambiguity–maintenance tradeoff" (§VIII-D).
- The list gets long. Stating every requirement does not reliably help ([Yang et al., 2026](https://arxiv.org/abs/2505.13360v3)), and [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) covers density.
- The author writes the wrong invariant. The study's oracle never tested that.
- Other models, agents, and larger systems were not tested (§X).

## What to do

1. Before generation, require three short lists: invariants, negative requirements, and edge cases with tie-break rules.
2. Keep the lists in the agent's context and check that each obligation reaches the prompt.
3. Turn each obligation into a test, and update the lists on every requirement change.
4. Target obligations the model gets wrong in observed failures. The authors write "The lesson is not to write longer specifications" (§XI).
5. Probe the oracle with [Specification-Oracle Gap Audits](../verification/specification-oracle-gap-audit.md) and [Probing Unstated Constraints](../verification/unstated-constraint-probes.md).

## Key Takeaways

- Report the effect with its denominator: a relative drop in mean failed hidden tests, Phase I, against no spec.
- The adjusted G3 effect is not significant after Holm correction, and the template alone shows no effect.
- G3 also changed how participants judged code: G1 overestimated its hidden-test performance by 22.78 points and G3 underestimated it by 22.20 (Table IV, §VII-D).

## Related

- [Spec-Driven Development with Spec Kit](../workflows/spec-driven-development.md)
- [The Specification as Prompt](specification-as-prompt.md)
- [Negative Space Instructions](negative-space-instructions.md)
- [Assumption Propagation](../patterns/anti-patterns/assumption-propagation.md)
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md)
- [Compound Prompt Constraints Degrade More Than Their Parts Predict](../patterns/anti-patterns/compound-prompt-constraints.md)

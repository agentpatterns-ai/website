---
title: "Skill-Use Gates: Trigger, Compliance and Boundary"
term: "Skill-Use Gate Decomposition"
description: "Score agent skill use as three independent gates: trigger, compliance, and boundary. One composite pass rate cannot tell you which gate failed."
tags:
  - testing-verification
  - evals
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - trigger compliance boundary decomposition
  - skill trigger versus compliance
  - skill invocation and adherence scoring
last_reviewed: 2026-08-06
maturity: emerging
---

# Skill-Use Gates: Trigger, Compliance and Boundary

> Skill use fails at three independent gates: retrieving the skill, following its procedure, and respecting its prohibitions. One score hides which broke.

Skill-use gate decomposition scores an agent skill on three axes instead of one pass rate. Trigger asks whether the agent retrieved the skill from its name and short description alone. Compliance asks what weighted fraction of the prescribed steps it then carried out. Boundary asks whether it avoided the operations the skill forbids. The Skill-Use benchmark defines all three and combines them so that execution counts only after the skill fires, weighting compliance at 0.7 and boundary at 0.3 ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)).

## When the split earns its cost

Three conditions have to hold together, and they are the conditions the benchmark itself runs under:

- The harness uses [progressive disclosure](../patterns/agent-design/progressive-disclosure-agents.md), so the agent sees only a name and a one-line description until it retrieves the body.
- The library is too large to preload wholesale. Preloading full skill text "primarily improves skill selection, revealing retrieval as the main bottleneck under native injection," so a team with context headroom should close the trigger gate rather than measure it ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)).
- The agent chooses which skill to invoke. Under slash commands or hard-wired routing a human or a router picks, and the trigger gate does not exist.

Outside those conditions a paired with-skill and without-skill run answers the question more cheaply. That design already yields 16.6 percentage points of average pass rate on SkillsBench, with no gate instrumentation ([arXiv:2602.12670v4](https://arxiv.org/abs/2602.12670v4)).

## The gates fail independently

Across 79 skills, 177 tasks, eight models, and two harnesses, the strongest configuration reached a combined score of only 0.613, and no configuration's compliance exceeded 0.625. Trigger spanned 0.324 to 0.972, and the two gates did not move together: "a model that recognizes a skill often still departs from its procedure while a model that could comply sometimes fails to trigger at all" ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)).

Retrieval failure has a second cause that description craft cannot reach. A retriever can find the right capability family and still surface the wrong sibling within it, carrying a stale resource or a missing precondition. Against a baseline retriever, harmful sibling exposure at top-3 measures 0.693 before any deliberate representative selection ([arXiv:2606.10388v1](https://arxiv.org/abs/2606.10388v1)).

## Prohibitions land better than procedures

"Boundary exceeds Compliance in almost every category." Security and compliance tasks were the exception, where procedural failures dominated boundary violations ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)). A named prohibition therefore buys more reliability than the same requirement written as one step in a long workflow.

## Why It Works

Under progressive disclosure the agent makes two decisions from different information, and each responds to a different fix. Selection happens on a name and a one-line description, which makes it a semantic matching problem over the library. That is why preloading the body mainly improves selection, and why skills with abstract names gain most from it while "keyword-rich names gain little or reverse." Procedure-following happens afterwards with the body already in context, so it is an instruction-following problem over a conjunction of steps that preloading leaves untouched. Once both modes trigger, "the SU gap becomes small" ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)). The boundary ordering follows the same shape. A prohibition is one constraint the agent either violates or does not, while a procedure loses points whenever any single step is dropped, which is the [instruction compliance ceiling](../instructions/instruction-compliance-ceiling.md) acting inside a skill file.

## When This Backfires

- Small libraries with distinctive, keyword-rich names. The preloading ablation finds these "gain little or reverse," so trigger is not the binding constraint and a separate trigger score reports noise ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)).
- Optimizing hard for trigger rate. The rank correlation between within-scope score and out-of-scope avoidance is negative, and the models with the strongest in-scope use account for most inappropriate invocations on 53 topically adjacent tasks ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)). Raising recognition trades against restraint, so an eval set with no out-of-scope cases rewards the wrong direction.
- Reading a harness ranking off the gate scores. Rankings flip between harnesses and cross-harness correlation on shared tasks runs 0.290 to 0.648, but the turn budget also differs (120 under Claude Code, 80 under Codex), so the comparison is confounded ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)). Attributing that gap to harness design needs matched budgets, which is the control [fleet harness attribution](../patterns/agent-design/fleet-harness-attribution.md) applies.
- Chasing small score differences. Rubric items are judged partly by an LLM at temperature 0, with a human audit reporting Cohen's kappa of 0.65 ([arXiv:2608.04828v1](https://arxiv.org/abs/2608.04828v1)). Model graders also carry positional, self-preference, and stylistic biases that manufacture skill gains execution-correctness grading does not reproduce ([arXiv:2606.06454v1](https://arxiv.org/abs/2606.06454v1)).

## Key Takeaways

- Split the score before you debug the skill. A low trigger and a low compliance need opposite interventions.
- Fix trigger by making the name and description match how the task is phrased, or by preloading and removing the gate.
- Fix compliance by shortening the procedure, since each additional step is another place the conjunction breaks.
- Write the constraints you care about as explicit prohibitions, which are honored more reliably than steps.
- Put out-of-scope cases in the eval set, because trigger rate and restraint pull against each other.
- Re-measure per harness. The benchmark publishes no author-facing recommendations, so treat all of the above as inference from its measurements.

## Related

- [Skill Evals](skill-evals.md) — the paired with-skill and baseline runner this refines; its two axes of output quality and trigger precision split into three here
- [Eval Blind Spots](eval-blind-spots.md) — the skill-retrieval gap as one of four structural measurement gaps
- [Skill Specification Violation Fuzzing](skill-specification-violation-fuzzing.md) — attacking the boundary gate directly, by turning each guardrail into a reachability goal
- [Skill Authoring Patterns](../tool-engineering/skill-authoring-patterns.md) — the description craft that moves the trigger gate
- [Fleet Harness Attribution](../patterns/agent-design/fleet-harness-attribution.md) — how to attribute a cross-harness delta to the harness rather than the model

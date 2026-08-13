---
title: "Against-Prior Accuracy: Score the Rules That Fight Defaults"
term: "Against-Prior Accuracy"
description: "An instruction-compliance score counts rules the agent would have followed anyway. Withhold each rule, keep only the ones that change behavior, rescore."
tags:
  - testing-verification
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - AP-Acc
  - against-prior compliance
  - prior-controlled instruction following
last_reviewed: 2026-08-13
maturity: emerging
---

# Against-Prior Accuracy: Score the Rules That Fight Defaults

> An instruction-compliance score counts rules the agent would have obeyed anyway. Remove them and the score drops.

Against-Prior Accuracy (AP-Acc) is a compliance rate computed over only those rules that oppose what the agent does unprompted. A rule earns that label by being withheld: run the task without it, and if behavior does not move, any later compliance on that rule was coincidence. Across 12 frontier models on 60 multi-turn coding items, AP-Acc came in below aggregate accuracy for every model, by 3.6 to 7.4 points with a mean of 5.81 ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)).

## When the correction is worth computing

Four conditions decide whether the probe pays for itself.

1. Compliance is checked deterministically, or by a judge you have calibrated. On the same panel the deterministic-only subset showed a 13.09-point gap against 5.81 panel-wide, so the checking method more than doubled the measured effect ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)). Stable verdicts can also sit on unstable reasoning, which is the argument for pushing deterministic checks into code ([Shergadwala, 2026](https://arxiv.org/abs/2601.11783)).
2. You can afford enough repeats to beat sampling noise. Harness-IF used a five-of-nine consensus across nine probe builds and still recovered a label for 287 of its 642 rules ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)).
3. The rule is not already enforced by a hook, linter, or CI gate. Deterministic enforcement makes compliance certain and leaves the stratification nothing to answer.
4. You will re-run the probe after a model change. A prior belongs to a specific build, so labels expire when the build does.

Fail any of these and read aggregate compliance as an upper bound instead of correcting it.

## Running the probe

Pick a rule, then a task whose correct completion depends on it. Run that task with the rule withheld, several times, and record the default behavior. Label the rule align-prior when the default already satisfies it, against-prior when the default opposes it, neutral otherwise. Then score compliance across against-prior rules only. A single-model team substitutes repeated runs for the nine builds, and the label then describes that one model.

The deletion step is the same probe as [the no-op test](../instructions/behavioral-no-op-test.md). That test asks whether to keep the line; this asks what a compliance number is worth.

## Where the rule lives is a second variable

Harness-IF separates six instruction surfaces. One is fixed by the platform; the other five are configurable by whoever deploys the agent: the system prompt, tool descriptions, skill descriptions, project files such as `CLAUDE.md` or `AGENTS.md`, and the user's current request ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)).

| Surface | Pooled accuracy | Eligible verdicts |
|---|---|---|
| Tool description | 83.1% | 3,934 |
| Project file | 79.1% | 11,756 |
| Skill description | 78.6% | 11,072 |
| System prompt | 73.6% | 6,589 |

Source: [Huang et al., 2026](https://arxiv.org/abs/2608.11727v1). The user-instruction surface is left out because all 1,476 of its placements were against-prior, making its 54.5% incomparable with the mixed rows above.

A separate pilot of 916 runs over nine older builds asked which surface wins when two demand opposite things. System prompts, project files, and user instructions tied for best mean rank at 2.22, ahead of tool descriptions at 3.78 and skill descriptions at 4.56 ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)). A prompt-depth account predicts the last-placed instruction wins, and the user turn only tied. Six of nine per-build fits reproduced the ordering exactly, so treat it as a pooled tendency.

## Why it works

An aggregate compliance rate averages two populations that answer different questions. Rules the instruction caused the agent to satisfy measure instruction following. Rules the default already satisfied pass at a rate unrelated to whether anyone wrote them, so folding them in biases the estimate upward in proportion to their share. The paper's difficulty split exposes the mechanism: preference operators such as "prefer" and "allow", which can coincide with existing behavior, scored 90.6%, while commanding operators such as "require" and "forbid" scored 76.0% ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)). Stratifying by prior drops the coincidence population out of the denominator.

## When this backfires

- The probe cohort contaminates the label when it overlaps the models being scored. A five-of-nine consensus necessarily includes at least one build from the evaluated panel, and only 44.1% of the against-prior verdicts carry a label sourced from the ablation at all ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)).
- The correction rarely changes a decision. Prior control left the top-ranked build unchanged and exchanged three adjacent rank pairs, which item-clustered intervals leave unresolved anyway ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)).
- Placement is a weaker lever than the surface table suggests. The system and user prompt separation does not reliably establish precedence across models ([Geng et al., 2025](https://arxiv.org/abs/2502.15851v4)), and a factorial study over 1,650 Claude Code sessions found no detectable compliance contrast from four configuration-file structure variables ([McMillan, 2026](https://arxiv.org/abs/2605.10039v1)).
- Cost scales with the rule count, not the file size. The published panel took 2,160 agent runs to produce 40,104 rule-level verdicts ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)), and a scaled-down version still runs the task once per rule per repeat. On a short instruction file the audit costs more than it recovers.

## Example

Two agents produced an extra documentation artifact despite an explicit prohibition. The task naturally invited explanatory output, so obeying the rule meant overriding a common default. That is a textbook against-prior instance, and one an aggregate score would have quietly averaged against easy align-prior passes ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)).

That shape is typical, and it tells you where to point a verifier. Rules that require an action or set a minimum absorb 77.1% of the 8,440 recorded failures, against 20.8% for rules that forbid or cap. Both classes fail at similar rates, 23.8% and 20.8%, so the gap is exposure: the panel holds 27,306 shortfall instances against 8,443 overstep ones ([Huang et al., 2026](https://arxiv.org/abs/2608.11727v1)). A verifier tuned to catch excess output therefore watches about a fifth of the failures.

## Key Takeaways

- Report the against-prior rate alongside the aggregate, never instead of it. The two answer different questions and the gap is the finding.
- The inflation is model-specific, spanning 3.6 to 7.4 points across 12 builds, so it does not cancel when you compare two configurations.
- Label rules before you score them: withhold, observe the default, then decide which rules the measurement is even about.
- Surface choice moves compliance, but the surface that wins a head-to-head conflict is not the one nearest the end of the context.
- Rules that demand action carry most of the failure mass, so build the verifier for omissions first.

## Related

- [The No-Op Test: Prune Agent Docs by Behavior, Not Length](../instructions/behavioral-no-op-test.md) — the same withheld-line probe, used to decide whether a line stays
- [The Instruction Compliance Ceiling](../instructions/instruction-compliance-ceiling.md) — the density limit that makes an honest compliance number worth having
- [Equivalence Testing for Agent Configuration Changes](equivalence-testing-agent-config-changes.md) — how to bound an effect you expect to be absent, rather than stratify one you expect to be present
- [Configuration File Structure Does Not Drive Compliance](../instructions/configuration-file-structure-compliance-gap.md) — the factorial evidence that file shape is not the lever
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — what to check first when a judge, not code, produces the verdicts
- [Bug-Discriminating Validation Evidence for Repair Agents](bug-discriminating-validation-evidence.md) — the same counterfactual-baseline logic applied to test evidence rather than rule compliance

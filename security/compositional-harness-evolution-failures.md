---
title: "Compositional Safety Failures in Harness Evolution"
term: "Compositional Safety Failure"
description: "Harness updates that each pass validation can fail together. One 32B model, no attacks: rates run 0.52% to 18.18% by task set, and pairwise checks miss 3-way cases."
aliases:
  - compositional safety failure in harness evolution
  - cross-component update interaction
  - joint-activation safety failure
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-04
maturity: emerging
status: current
---

# Compositional Safety Failures in Harness Evolution

> Two harness updates can each pass safety validation and still produce a violation once both are active. Per-update review cannot rule this out.

A compositional safety failure is two or more harness component updates that each pass on their own and fail together. The components are memory, prompt or skill, and tool. The paper that names the failure calls it a safety risk intrinsic to harness evolution ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)). The anti-pattern is treating per-update safety validation as proof that the evolved harness is safe.

## When this applies, and what the evidence covers

The pattern applies when a harness changes memory, prompts or skills, and tools through separate update paths. Those paths can be an automated evolution loop or separate human owners. A team that edits `CLAUDE.md`, skills, and tool sets by hand in reviewed pull requests has a small, stable component set. The paper studies automated evolution only, so applying it to human edits is an inference.

The evidence has hard limits ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)):

- Every experiment uses one backbone, Qwen3-32B. The paper has no evidence on frontier models.
- The paper studies non-adversarial updates only. Source text: "We study non-adversarial harness evolution only and do not construct attacker-crafted component updates."
- The failure rate runs from 0.52% to 18.18% depending on the task set and panel construction. The authors state that their goal "is not to estimate the prevalence of compositional failures in any particular deployed evolution system".
- The monitor's safety checker is the benchmark's own safety criterion, the same oracle that scores the results. A deployed system has no such oracle.

Read the numbers below as proof that the failure exists. They are not a forecast for your harness.

## How the failure happens

A safety property often depends on facts held in different components. In the paper's example, a prompt update adds Bob to `authorize_group`, and a memory update adds the account BoA to `bank_account`. Under the rule that `authorize_group` can access `bank_account`, each update alone is safe, because Bob is not authorized under the old prompt and BoA is unavailable under the old memory. Once both updates coexist, "Bob can access BoA" ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2), Figure 1).

Each update passes review because the matching precondition is still missing. A second, separate update supplies it.

Validation also depends on which executions it runs. Source text: "A cross-update interaction can remain latent at validation time and become observable only when a future execution jointly activates the relevant states. This makes compositional safety inherently execution-dependent." A replayed validation set can miss an interaction that a later task triggers ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)).

Software testing research shows the same structure. Kuhn and Reilly studied early releases of Mozilla and Apache, and Kuhn, Wallace, and Gallo report that more than 70% of documented failures needed only one or two triggering conditions, and none needed more than six conditions ([Kuhn, Wallace, and Gallo, 2004](https://csrc.nist.gov/CSRC/media/Projects/automated-combinatorial-testing-for-software/documents/kuhn-wallace-gallo-tse-preprint.pdf)). Failures need specific combinations, and most combinations are small.

## What the paper measured

A panel counts only when the original harness and each single update are safe and keep utility. The joint configuration must also show a violation that the other configurations lack, with execution-level evidence ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)). The pairwise results:

| Benchmark | Eligible panels | Failures | Rate |
|-----------|-----------------|----------|------|
| AgentDojo | 157 | 22 | 14.01% |
| Agent-SafetyBench | 11 | 2 | 18.18% |
| Agent Security Bench | 1,243 | 19 | 1.53% |

The AgentDojo panels come from one banking task family and an update pool of one memory update, nine prompt updates, and one tool update. The Agent-SafetyBench rate rests on 11 panels. The authors warn that the lower Agent Security Bench rate "should not be interpreted as weaker evidence of the phenomenon", because the three benchmarks differ in task distribution and panel construction.

### Failures that need three updates

The paper also finds 15 failures among 138 eligible triples on AgentDojo (10.87%) and 3 among 578 on Agent Security Bench (0.52%). In every one, "all seven lower-order configurations remain safe", so the violation appears only with all three updates active. A pairwise check misses these by construction. Agent-SafetyBench yields 9 eligible triples, which the authors call too small for a meaningful analysis ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)).

## Controls and their limits

Checking every combination costs too much. The paper states that "Evaluating all cross-component compositions leads to a combinatorial cost", and the cost recurs after every update ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)). The controls below trade coverage against cost.

| Control | What it does | Residual failures in the paper | Limit |
|---------|--------------|-------------------------------|-------|
| No monitoring | Per-update validation only | 22/157, 2/11, 19/1,243 | The baseline |
| Whole-harness revalidation (SHE) | Re-runs safety-utility validation on the evolved harness | 6/157, 1/11, 5/1,243 | Sees only the interactions its validation trajectories activate |
| Selective verification (HarnessLens) | Verifies behavior selectively | 8/157, 1/11, 5/1,243 | Leaves residual failures (8/157 on AgentDojo) |
| Hypergraph runtime monitor | Checks an interaction when its last component state becomes active, before the action runs | 2/157, 0/11, 1/1,243 | Safety checker is the benchmark oracle |
| Naive exhaustive checking | Checks every composition | 1/157, 0/11, 0/1,243 | 80.5 to 139.5 s added per task |

The monitor invokes safety checks on only 20.1% to 33.6% of candidate actions and adds 19.8 to 32.5 s per task ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)).

Whole-harness revalidation already removes most failures. The monitor's gain over it is 1 to 4 failures per benchmark, not 22, so a team can reasonably stop at revalidation.

The transferable idea is to index interactions by component state and check them when the last participating state becomes active. The implementation also uses a Qwen3-8B semantic filter, so treat it as research code, not a build recommendation.

## What to do with this

- Find safety rules whose preconditions live in different components, such as an authorization list in a prompt, a resource in memory, and a capability in a tool. Re-check the rule when any one of them changes.
- Revalidate the whole evolved harness after updates, and accept that it covers only the executions you replay.
- Prefer structural capability limits where they exist. Removing one leg of the [lethal trifecta](lethal-trifecta-threat-model.md) blocks the attacker-driven class of compositions without enumerating them. Willison's argument is about prompt-injection exfiltration, not update composition ([Willison, 2025](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)).

## Why it works

The controls work because the failure needs a specific joint state. Checking at activation time turns an exponential candidate space into the interactions one execution triggers. Whole-harness revalidation works for the same reason at lower resolution, because it exercises states together and per-update review never does ([arXiv:2609.33123v2](https://arxiv.org/abs/2609.33123v2)). Both stay bounded by the executions they observe.

## When this backfires

- The harness does not self-evolve. With a few hand-reviewed changes, exhaustive review of the changed pairs is affordable, and a hypergraph monitor adds machinery with no gain.
- No trustworthy safety predicate exists. The 1.27% residual rate used the benchmark oracle. Real step-level checkers err in both directions: StepGuard's error analysis reports 307 false positives and 268 false negatives, and 43.6% of the false positives are benign uses of sensitive tools ([StepGuard, arXiv:2608.24777v1](https://arxiv.org/abs/2608.24777v1)). A monitor that fires on 20% to 34% of actions would inherit those errors and block legitimate work.
- Capabilities are already compartmentalized. If no single decision context can hold private data, untrusted input, and an egress tool together, most dangerous compositions cannot activate.
- The workload is latency-sensitive or high-volume. Even the selective monitor adds 19.8 to 32.5 s per task on these benchmarks.
- The task distribution is broad. On Agent Security Bench the pairwise rate is 1.53% and the 3-way rate is 0.52%. A team can accept that risk when one violation is cheap.
- The model differs. Frontier models may compose updates differently, and the paper offers no evidence either way.

## Distinct from neighboring pages

- [Skill composition risk](skill-composition-risk.md) covers outputs of several skills chaining inside one shared context. This page covers updates across memory, prompt, and tool components.
- [Skill misevolution](skill-misevolution-lifecycle-gates.md) covers one component, a skill library, that drifts over time. This page covers interaction between components that each changed safely.
- [Compositional vulnerability induction](compositional-vulnerability-induction.md) covers an attacker splitting a goal across a ticket sequence. This page covers non-adversarial updates.

## Key Takeaways

- Per-update validation answers whether a change broke something. It cannot show the evolved harness is safe.
- Three-way failures exist where every single and pairwise configuration is safe, so a pairwise check misses them by construction.
- The reported rates range from 0.52% to 18.18% on one 32B model with non-adversarial updates, and the authors decline to estimate prevalence.
- Whole-harness revalidation removes most failures in the paper. The runtime monitor's extra gain depends on an oracle checker that deployments lack.
- Structural capability limits block compositions without enumerating them.

## Related

- [Skill Composition Risk in Agent Ecosystems](skill-composition-risk.md)
- [Skill Misevolution in Self-Updating Skill Libraries](skill-misevolution-lifecycle-gates.md)
- [Compositional Vulnerability Induction in Coding Agents](compositional-vulnerability-induction.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Observability-Driven Harness Evolution](../patterns/agent-design/observability-driven-harness-evolution.md)

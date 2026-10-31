---
title: "Configuration-Scoped Acceptance for Agent-Run Migrations"
description: "Accept an agent's hardware migration from a run on the exact target configuration, re-verify after each configuration change, and make the smoke gate asymmetric instead of a fixed threshold."
term: "Configuration-Scoped Migration Acceptance"
tags:
  - workflows
  - agent-design
  - testing-verification
  - migration
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - per-configuration migration acceptance
  - target-configuration acceptance run
last_reviewed: 2026-10-29
maturity: emerging
---

# Configuration-Scoped Acceptance for Agent-Run Migrations

> Configuration-scoped acceptance measures the migration on the exact target configuration, because unchanged dependencies can change semantics when the configuration does.

Three conditions decide whether this cycle is worth its accelerator time. The target configuration has to change after the first accepted run, through chip count, backend, or dependency pins. The workload's acceptance band has to be narrower than the migration's measured effect. And a trustworthy reference run on the source hardware has to exist, or the comparison attributes inherited defects to the migration. Where all three hold, the acceptance evidence has to come from an execution on the final configuration. Where they do not, one migrated run and a look at the training curve is the proportionate answer.

## Why a clean diff is not evidence

An agent can preserve every configuration value, produce a reviewable diff, exit zero, and still change how the model trains. In a study of ten agent-driven GPU-to-TPU migrations, the agent moved a LoRA+ fine-tuning project onto a four-chip TPU, the program finished without error, and the agent reported success; accuracy ended at 84.89% against the GPU reference run's 86.53% ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). The same migrated code on a single chip ended at 86.54%, within 0.01 percentage points of the GPU. Nothing in the diff distinguished the two runs, because the chip count was the only thing that changed.

Nearly half the failed attempts were silent. Across the ten projects the study recorded that "53 of 70 attempts failed (76%), including 26 (49%) without explicit errors" ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). Lazy-tensor execution accounted for 13 of those failures across seven projects, all of them error-free. The usual fallback gate was unavailable: of the 148 repositories the authors collected, only seven contained author-written tests.

Two scope limits belong next to those numbers. The false success came from the four-chip case study, whose protocol "did not require the agent to compare TPU and GPU loss or evaluation metrics before the full run" ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). Under the main study's protocol the agent's final claims never exceeded the independently measured level across the nine completed projects, matching in six and understating in three. The cycle below is what that main protocol did, extended to the configuration axis the case study exposed.

## Three implementation layers

### Layer 1: A verified reference on the source configuration

Run the original code unchanged on the source hardware first, and keep that run as the comparison target rather than the published number. In the study, GPU-to-paper gaps often exceeded GPU-to-TPU gaps, so a team comparing against a paper or a release note attributes pre-existing reproduction failures to the migration ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). The migration's own effect was small beside that. Across the nine projects that executed, GPU and TPU metrics differed by a median of 0.43% with a range of 0.01% to 3.43%, and by under 1% in seven of them.

### Layer 2: A smoke gate that separates improvement from regression

In this study a fixed symmetric threshold on a sampled metric rejected far more viable migrations than defective ones. Of seven smoke-test stops, one detected a migration-induced error and six were false alarms ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). One project was stopped because its TPU training loss came in 7.15% lower than the GPU's, with an evaluation difference of only −0.28%; after human approval the full run passed. Another tripped the numerical gate on a 2.8% difference in sampled generations, and a deterministic comparison then showed matching next-token distributions.

Three design choices follow. Treat an improvement differently from a regression. Compare output distributions deterministically where the task samples, instead of thresholding a sampled metric. Route ambiguous evidence to a human decision rather than letting the gate declare failure.

### Layer 3: An acceptance run on the final configuration, repeated per change

Re-run the acceptance comparison whenever chip count, backend, or a dependency pin changes, and inspect the properties a diff cannot show: device placement, CPU fallback, unexpected recompilation, checkpoint restoration, optimizer state, effective batch size, and the order of gradient reduction ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). Hold tuning until correctness clears. Seven of the nine completed TPU runs ran at accelerator utilization below 25%, and in one backend comparison fusing a single activation function cut fixed-batch step time by 25%, so the tuning stage has room to work; each optimization then needs the acceptance checks run again.

## Triggers and constraints

The trigger is a configuration change, not a schedule or a push. The human gate sits at Layer 2, on any stop the gate cannot resolve from evidence, and the study's migrations needed 2.4 human interventions on average across a median of 6.5 attempts, with a range of 3 to 11 ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)).

Budget the accelerator time, not the tokens. Agent token charges had a median of $9.74 across a range of $2.00 to $22.55, against a median migration time of 1.88 hours; completed run costs on the target ranged from 0.47 to 3.6 times the source hardware's ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). Failed attempts, reference runs, and supervision sit outside the token line entirely.

The study also bounds what the agent should decide alone. Its agent stopped attempts whose projected runtime was impractical, on its own initiative, but showed no comparable autonomous stopping in response to silent numerical or behavioral drift ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). Give it the time budget to enforce and keep behavioral acceptance in the gate.

## Multi-tool coverage

Tool-agnostic. The study ran its migrations with Claude Code, and no layer above depends on which assistant produces the diff.

## Why it works

Clipping and averaging do not commute, and the agent never touched the code that ordered them. The study's four-chip launcher preserved the global batch size of 32 by running one process per chip with eight examples each. The project's pinned `accelerate` 0.27.2 "has no XLA-specific gradient-clipping path, so each chip clips the gradient of its own 8 examples to norm 1.0 *before* the cross-chip average, whereas the GPU clips the gradient of all 32 examples once" ([arXiv:2610.34422v1](https://arxiv.org/abs/2610.34422v1)). The hyperparameters matched and the diff was clean, and the update rule was still not the same. The agent's own account was wrong as well: it blamed the TPU's default bfloat16 matrix multiplications, which the matching single-chip run on the same numerics rules out. Neither the diff nor the agent's explanation carries the evidence, so only a run on the configuration you intend to ship does. The same gap appears in high-level synthesis for FPGAs, where "HLS code that passes simulation and synthesis may still fail to produce deployable, runnable designs on real FPGA platforms" because of timing and place-and-route constraints ([arXiv:2608.23630v1](https://arxiv.org/abs/2608.23630v1)).

## When this backfires

- The target configuration is fixed and single-device. If chip count, backend, and pins never change after the first accepted run, Layer 3 pays nothing. The study's single-chip migration matched its GPU reference to 0.01 percentage points.
- The acceptance band is wider than the migration's effect. Seven of nine projects differed by under 1%; decide whether another comparison is needed against your workload's acceptance criteria.
- The gate is a fixed symmetric threshold. Configured that way it produced six false alarms in seven stops, which turns a verification budget into a rejection budget.
- No trustworthy source-hardware reference exists. Without one the comparison blames the migration for inherited reproduction failures, and the cycle produces confident wrong answers instead of no answer.
- The workload is not worth the supervision. Human and accelerator time dominate a token charge of $2.00 to $22.55, and on a low-value workload that arithmetic does not close.

There is a case for pushing this upstream instead. The FPGAgent framework folds end-to-end executability validation into the generation tool rather than leaving it to the team, and its authors report a 26.7% improvement in executability over existing baselines, measured on a 78-task benchmark with five LLMs ([arXiv:2608.23630v1](https://arxiv.org/abs/2608.23630v1), abstract). Where your stack has a tool that does this, prefer it. Until it does, the cycle is what you have.

## Key Takeaways

- A migration accepted on one hardware configuration is not accepted on another, and the diff is where the difference is absent.
- Numbers from one configuration do not transfer. The 84.89% result is a four-chip figure under a protocol that skipped the pre-run comparison, and the single-chip run matched the GPU.
- The gate's own cost is false rejection, measured at six in seven stops, so asymmetry and deterministic distribution comparison are load-bearing parts of the design.
- Agent token spend is the small line. Reference runs, failed attempts, and 2.4 interventions per migration are the bill.
- All of this rests on ten open-source research projects, one agent, and single-seed runs. Treat the mechanism as transferable and the magnitudes as indicative.

## Related

- [Probing an Agent's Completion Claim in a Disposable Fork](../verification/completion-claim-probe.md) — the single-agent building block behind the Layer 2 and Layer 3 checks, applied at the moment the agent says it is done
- [Staged Literal Porting with a Per-Stage Numeric Oracle](staged-literal-port-with-numeric-oracle.md) — the same discipline on the source-language axis, where the defect lives in the diff rather than in an untouched dependency
- [In-Place Atomic Replacement for Agent-Driven Ports](in-place-atomic-replacement-port.md) — how to land a port once it passes, keeping main shippable per component
- [Tool-Call Success as Workflow Effect Evidence](../patterns/anti-patterns/tool-call-success-as-workflow-evidence.md) — the general form of the failure, where every call succeeded and the effects are still wrong
- [Seed-Variance Reporting and Measurable-Range Eval Design](../verification/seed-variance-reporting.md) — why a single-seed comparison bounds what any acceptance threshold can mean

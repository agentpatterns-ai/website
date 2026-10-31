---
title: "Interface Realization Repair: Evidence and Limits"
term: "Interface Realization Repair"
description: "MICA reports an interface-realization intervention under matched conditions; its abstract does not supply a reproducible diagnostic or implementation procedure."
aliases:
  - interface realization repair
  - matched interface comparison
  - decoupled action realization
tags:
  - agent-design
  - tool-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-28
maturity: emerging
staleness_risk: true
---

# Interface Realization Repair: Evidence and Limits

> Interface realization repair has reported benefits under matched conditions; the verified abstract leaves its implementation and diagnostic procedure unresolved.

Shi et al. report differences in task performance and interaction cost across six models and three interactive environments. Their MICA comparison renders MCP and CLI interfaces from a shared semantic action contract and routes decoded actions through the same runtime ([arXiv:2610.34298v1, abstract](https://arxiv.org/abs/2610.34298v1)). These controls support studying interface effects. The abstract does not establish that every measured gap is a realization fault.

## What the repair study reports

MICA uses matched-state probes to examine sensitivity in capability presentation, realization, and feedback. Its DART intervention “preserves validated semantic commitments while repairing interface-specific realization.” The abstract reports improved benchmark scores in all six evaluated settings, by up to 9.0 points, and reduced MCP token cost in all three environments, by up to 27.1k tokens per task ([Shi et al., arXiv:2610.34298v1](https://arxiv.org/abs/2610.34298v1)). These are the reported maxima across settings and environments; the abstract supplies no provider-billed cost ratio.

Verification here used the v1 abstract; HTML rendering was unavailable. DART's implementation, probe construction, and per-setting results remain unverified here. This evidence supports reporting an intervention result, but does not provide a procedure for reproducing it in a repository.

## Trajectory divergence does not identify a fault

The abstract reports structured divergence in 94.3% of 2,004 paired episodes and says early differences propagate through subsequent interaction ([Shi et al., arXiv:2610.34298v1](https://arxiv.org/abs/2610.34298v1)). Its paired natural trajectories and matched-state probes are distinct evidence. Comparing equally numbered steps after the trajectories diverge does not establish matched states.

Different call syntax can implement the same semantic action. A syntax difference alone therefore cannot establish a realization fault. That is a limit on inference from the reported comparison, not a diagnostic method supplied by MICA. Validation against the action contract and an actual matched-state comparison would be needed before assigning a fault.

Repair assignment also depends on the source of a failure. Raj et al.'s taxonomy assigns 41 failure modes to component interactions and fault sides; their abstract states that “the same visible failure may call for model post-training, harness engineering, environment redesign, or benchmark repair depending on its source” ([arXiv:2607.28802v1](https://arxiv.org/abs/2607.28802v1)). This taxonomy supplies a classification perspective, not a DART implementation.

## Example: Separate success, time, and dollar cost

Scale Labs compared interfaces over the same backend capabilities on 50 tasks in two environments. Its CLI was generated from MCP schemas, with command discovery exposed through a skill and help text ([study setup](https://labs.scale.com/blog/mcp-vs-cli)).

- Task success: Opus 4.8 and GPT-5.5 performed similarly across interface conditions. Opus 4.6 improved from roughly 8.5% to 17.7% with CLI in the data-heavy environment; the lighter environment favored MCP.
- Elapsed time: CLI used more turns and ran 20–40% longer.
- Dollar cost: MCP was cheaper for Opus 4.8 on Claude Code; CLI was cheaper for GPT-5.5 on the OpenAI Agents SDK.

Scale proposes harness output handling as an explanation for the cost reversal: file-spilling versus resending large outputs inline. It did not isolate that explanation experimentally. These results concern the tested models, harnesses, and workloads, and do not establish a universal interface preference ([results and limitations](https://labs.scale.com/blog/mcp-vs-cli)).

## What a comparison still needs

Alier Forment et al. studied seven scaffoldings and five models on one fixed task. Thirteen paired MCP-to-CLI billed-cost ratios ranged from 0.43x to 29x, and agents frequently ignored their assigned interface ([arXiv:2608.08654v1](https://arxiv.org/abs/2608.08654v1)). That evidence motivates checking actual interface use and completion before attributing a cost difference. See [MCP-vs-CLI cost ratios](../../tool-engineering/mcp-cli-cost-ratio-scaffolding-bound.md) for the scaffolding limits.

The available evidence leaves three practical questions open for a proposed repair: whether the diagnosed fault is realization, whether the operator can change that layer, and whether the intervention improves the relevant outcome on the target workload. MICA's abstract does not answer those questions for another deployment.

## Key Takeaways

- Distinguish reported realization-repair results from an implementation procedure.
- Keep trajectory divergence separate from matched-state fault diagnosis.
- Measure task success, elapsed time, and billed cost separately on the actual stack.

## Related

- [Choosing an Agent Tool Interface: Shell or Typed Catalog](../../tool-engineering/agent-tool-interface-selection.md) — interface selection evidence across enterprise benchmarks
- [MCP-vs-CLI Cost Ratios Depend on Interface and Scaffolding](../../tool-engineering/mcp-cli-cost-ratio-scaffolding-bound.md) — the limits of transferring billed-cost ratios
- [Suspect the Harness Before the Model on a Regression](suspect-the-harness-not-the-model.md) — investigating regressions at a fixed model
- [Situated Harness Layers: Fix at the Layer That Owns It](situated-harness-layers.md) — routing a fix to the responsible layer
- [Isometric Harness Ablation](isometric-harness-ablation.md) — isolating one subsystem in a comparison

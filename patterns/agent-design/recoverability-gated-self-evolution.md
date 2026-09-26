---
title: "Recoverability-Gated Self-Evolution for Agent Harnesses"
term: "Recoverability Gate"
description: "Admit a self-modification to an agent harness only after its undo has been verified against states other than the one the mutation was written in."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - recoverability gate for self-modifying agents
  - counterfactual undo verification
last_reviewed: 2026-09-17
maturity: emerging
---

# Recoverability-Gated Self-Evolution for Agent Harnesses

> A capability-improving harness mutation can still be impossible for the agent to undo, and repair inside the same recovery representation recovers none of it.

Put every snapshottable harness surface under version control before you build anything else. Prompts, skill files, tool registries and config restore exactly from a prior revision, and in the paper's own comparison, effect-scoped snapshot restore beat synthesized undo on every split it was measured on. A recoverability gate is what you add for the surfaces a snapshot cannot capture. It is [rollback-first design](rollback-first-design.md) applied to the one action an agent takes against itself.

## Snapshot first, gate second

The paper reports a baseline that beats its own framework. "Effect-scoped snapshots are the stronger baseline in our evaluated serializable in-memory selective-undo regime: they recover 300/300 tasks versus 243/300 for EvoUndo under different-surface changes and 159/300 versus 131/300 under same-surface changes … There are no EvoUndo-only wins" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). The authors scope their framework to "settings where direct exact effect-scoped restoration is unavailable or insufficient".

Its extended recovery language covers "middleware sequences, event listeners, sandboxed files, managed sockets, and ordered composition of recovery operations across surfaces" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). Snapshots win "when the exact affected pre-state is known, serializable, and directly restorable". The gate is for state that fails that test, which the authors describe as "structured, state-dependent, or non-serializable inverse semantics", and they add that "this benchmark does not demonstrate superiority in those settings" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)).

## Capability and reversibility are separately distributed

Across 600 unseen self-evolution tasks in six harness families, generated single-sample and zero-shot, "281 are admissible, 122 are capability-inadequate, and 197 are capability-positive but fail recovery verification" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). Those 197 are 41.2% of the capability-positive mutations. A quality gate of the kind a [self-rewriting meta-prompt loop](self-rewriting-meta-prompt-loop.md) applies scores the forward change and never asks the second question.

Asking the model to fix the undo does not work while the recovery language stays fixed. Under the base recovery language, at a repair budget of four, "all four verifier-guided repair modes achieve 0/197 (0.0%) recovery … while independent regeneration recovers 6/197 (3.0%)" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)).

## Verify the undo against states it was not written in

The state distribution is the transferable part of the protocol. A mutation is drafted against one nominal state; reversal has to hold in states the drafting agent never saw. EvoUndo admits a candidate only after 10 development states and 40 held-out states, split 20 in-distribution and 20 out-of-distribution. Each split needs at least 19 of 20. The out-of-distribution states introduce "unfamiliar nested keys, conflicting socket allocations, prepended high-priority middleware, multi-level file paths, and reverse routing defaults" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)).

## Why it works

Recovery failures have two causes, and a pass-or-fail verifier reveals neither. A deterministic oracle audit separated them: 48 of the 197 failures were solvable with the primitives already available, and 143 needed primitives the recovery language did not have. Supplying a state-grounded diagnostic bundle (canonical state addresses, forward effect ordering and observed residuals) lifted the first group "from 0/48 to 38/48 (79.2%)"; adding middleware, listener, file and ordered multi-surface primitives lifted the second to "142/143 (99.3%)" on the gpt-oss-120b backbone ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). Coarse feedback under the base language fixed neither group, and grounded feedback under the base language recovered 0/143 of the second.

## When this backfires

- The surface is snapshottable. Witness capture and a synthesized recovery program over version-controlled files buy nothing a revert already gives, and on fresh holdout the synthesis path cost 2.39 to 3.09 model calls and 3.37k to 4.30k generated tokens per task ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)).
- Tuning the gate for zero false positives costs yield. Raising development states from 2 to 20 on fresh holdout "reduced observed false positives from 16.8% to 0.0%, but lowered Rescue@4 from 49.7% to 35.0% … and increased the conservatism gap from 6.6% to 24.1%" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). The strict gate rejects reliable candidates too.
- More diagnostic detail is not reliably better. Adding state-grounded diagnostics to the richer recovery language cut recovery from 142/143 to "133/143 (93.0%)" on gpt-oss-120b, and that reversal "did not reproduce under the Qwen3.8-27B constrained-decoding replication configuration" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). A feedback policy tuned on one model is not portable.
- The evolver may not be the bottleneck. Harness-updating capability is "flat in base capability", with Qwen3.5-9B's harness updates yielding gains comparable to those of Claude Opus 4.6, so the authors recommend "investing capability budget in the task-solving agent rather than the evolver" ([arXiv:2605.30621v1](https://arxiv.org/abs/2605.30621v1)).
- Reversibility is not safety. Misevolution risks such as "degradation of safety alignment after memory accumulation" and "unintended introduction of vulnerabilities in tool creation and reuse" ([arXiv:2509.26354v2](https://arxiv.org/abs/2509.26354v2)) survive a perfectly reversible mutation, because nothing triggers the reversal.

The paper's own limitation list says "Only gpt-oss-120b and Qwen3.8-27B were evaluated", the factorial ran that first model at temperature 0.2 with medium reasoning effort, and "no low-, medium-, or high-effort comparison was performed" ([arXiv:2608.28363v2](https://arxiv.org/abs/2608.28363v2)). Treat the magnitudes as benchmark results, not deployment figures.

## Key Takeaways

- Version-control the snapshottable surfaces first. A gate on synthesized undo is for state a snapshot cannot restore exactly, and the paper does not show it beats a snapshot even there.
- Score the forward change and the undo separately, because 197 of 600 benchmark mutations passed the first and failed the second.
- Extend the recovery language before buying more repair rounds. Verifier-guided repair at a budget of four recovered none of the 197 under the base language, and 180 of them under the extended one.
- Test the undo in states the mutation was not written in, including prior-existence branches and reverse routing defaults.
- Reversibility is not permission. A mutation you can withdraw is still a mutation nobody chose to withdraw.

## Related

- [Rollback-First Design](rollback-first-design.md) — choose the undo before the action, as a general constraint on agent work.
- [Self-Rewriting Meta-Prompt Loop](self-rewriting-meta-prompt-loop.md) — the self-evolution loop this gate attaches to.
- [Layered Mutability](layered-mutability.md) — which harness layer a mutation lands on, and how reversible that layer is.
- [Fleet-Level Irreversibility Budgets](fleet-irreversibility-budget.md) — pricing residual risk when undo is unavailable at all.
- [Selective Checkpoint Restore](selective-checkpoint-restore.md) — the snapshot affordance a shipped harness already exposes.

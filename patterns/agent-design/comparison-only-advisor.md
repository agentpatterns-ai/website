---
title: "Comparison-Only Advisor: Steering a Large Actor With a Tiny Comparator"
term: "Comparison-Only Advisor"
description: "A 0.5B comparator ranks the actor's proposed action against sampled alternatives and returns the winner as non-binding advice, conditional on a resettable environment."
tags:
  - agent-design
  - cost-performance
  - loop-engineering
  - tool-agnostic
  - arxiv
aliases:
  - comparison-only tiny advisor
  - COTA
  - tiny comparator advisor
last_reviewed: 2026-08-25
maturity: emerging
---

# Comparison-Only Advisor: Steering a Large Actor With a Tiny Comparator

> A 0.5B comparator that only ranks the actor's proposal against sampled alternatives can steer a 284B actor it could never replace.

A runtime supervisor does not have to be able to do the task. In COTA, a fine-tuned Qwen2.5-0.5B-Instruct comparator judges whether any of four sampled alternatives beats the actor's proposed next action, then returns the winner as advice the actor may ignore. It improved all nine actor-environment settings, including actors at 35B and 284B parameters ([Jiang et al., 2026](https://arxiv.org/abs/2608.21027v1)).

## Two conditions decide whether you can build this

### The environment must rewind

The comparator learns from same-prefix counterfactual branches. Freeze the actor, replay to an identical state, take a different action, then label which sibling trajectory ended better. That needs an environment you can reset and re-run. An agent acting on a production database, a payments API, or a shared repository cannot generate the training signal.

### The actor's own samples must sometimes be better

COTA cannot recommend an alternative that is absent from the candidate set. The paper calls this a support ceiling: the framework cannot expose a genuinely better alternative if the sampled candidate set contains none ([Jiang et al., 2026](https://arxiv.org/abs/2608.21027v1)). Where the actor is systematically wrong rather than occasionally sloppy, every candidate is bad and the advisor stays quiet exactly when you need it.

## How it runs

At each step the actor proposes an action. The harness samples K alternatives and has the comparator judge each against the proposal. Intervention fires when at least R alternatives defeat it. The paper used K=4 with R=1 on WebShop and ALFWorld, and K=4 with R=2 on τ³-Retail. The winners go back as advice, and the actor replans instead of executing them ([Jiang et al., 2026](https://arxiv.org/abs/2608.21027v1)).

How often the actor takes the advice varies by actor and environment. DeepSeek-V4-Flash adopted a recommendation in 30.4%, 32.9%, and 29.2% of replans across the three environments and kept its original proposal 49.6% to 63.6% of the time, while Qwen3.6-35B-A3B adopted 67.8% on WebShop and 19.0% on τ³-Retail. The reported gains hold across that spread.

## Why it works

Ranking two concrete actions is easier to learn than scoring either alone. The ablation isolates the difference: holding the intervention mechanism fixed and swapping absolute-Q estimation for same-prefix pairwise comparison moved ALFWorld from 57.46% to 90.30% for a Qwen3-8B actor, and τ³-Retail from 16.67% to 45.00% ([Jiang et al., 2026](https://arxiv.org/abs/2608.21027v1)). The stated principle is that an action "need not be certified as globally good to determine that the actor's current proposal is locally weak." A 0.5B model cannot calibrate a value function over a task it cannot perform. It does not have to: it learns which of two branches ended better, and that label comes from rollout outcomes, not its own competence. Weak verifiers rest on the same asymmetry, and they carry its limit: a significant performance gap remains between individual LM judges or reward models and oracle verifiers ([Saad-Falcon et al., 2026](https://arxiv.org/abs/2506.18203)).

## When this backfires

- Latency-bound loops. COTA averaged 1.38× the actor's end-to-end episode time, with seven of nine settings under 1.5× and a worst case of 2.024× ([Jiang et al., 2026](https://arxiv.org/abs/2608.21027v1)). An assistant that already feels slow cannot absorb that.
- Intervention in general is not safe. Two other supervisors in the same experiment made things worse. Self-Reflection degraded the actor in all nine settings, and Asym-AC, where a separate critic writes free-form feedback before the actor replans, scored 35.82% on ALFWorld against the plain actor's 82.84% while costing 2.323× the time. The evidence supports comparison-only advice specifically.
- Cross-task reuse is unproven. The comparator is fine-tuned per environment, and none of the three tested contains coding tasks. Nothing supports carrying one comparator across task families.
- Benchmark validity is unaudited here. The smallest absolute gain sits on τ³-Retail, and customer-service agent benchmarks carry documented task-validity defects: an audit of τ-bench found 38% of its airline subset and 6% of its retail subset intentionally unsolvable, so a trivial agent returning empty responses reaches a 38% success rate and beats a GPT-4o-based agent ([Zhu et al., 2025](https://arxiv.org/abs/2507.02825v5)). The COTA paper reports no equivalent audit of the environments it uses.
- The cheaper alternative is uncosted. Agent benchmarks focus narrowly on accuracy without attention to cost, leaving agents "needlessly complex and costly" ([Kapoor et al., 2024](https://arxiv.org/abs/2407.01502v1)). Best-of-4 sampling from the actor needs no second model and no training pipeline, and COTA reports no such comparison at equal wall-clock.

## Key Takeaways

- Build the branch-replay harness first. Without a resettable environment there is no pairwise training data, and no comparator quality compensates.
- Candidate diversity carries part of the gain, not the comparator alone: four sampled candidates gave 92.7% unique utilization against 28.5% from eight actor samples ([Jiang et al., 2026](https://arxiv.org/abs/2608.21027v1)).
- Nothing here has been tested on code. Porting it would need branch replay over a repository plus an outcome label per branch, and one preprint over three environments supplies neither.

## Related

- [The Advisor Strategy: Frontier Model as Strategic Advisor](advisor-strategy.md) — the inverse arrangement, where the advisor is the expensive model and the executor is cheap
- [Within-Task Model Cascade: Designing the Escalation Gate](../../loop-engineering/within-task-model-cascade.md) — escalates small to large and lets the small model produce the answer; a comparison-only advisor never produces one
- [Specialized Small Language Models as Agent Sub-Tools](specialized-slm-as-agent-tool.md) — the other way to put a small model inside a large agent's loop, behind a tool call rather than a ranking gate
- [Trajectory-Conditioned Model Escalation (SWE-Router)](trajectory-conditioned-model-escalation.md) — routes between models on a partial trajectory rather than ranking actions one step at a time
- [Stuck-Loop Recovery: Detecting and Escaping Non-Converging Agent Loops](../../loop-engineering/stuck-loop-recovery.md) — the recovery ladder that fires after a detector reports a stuck loop; this advisor runs every step and needs no such signal

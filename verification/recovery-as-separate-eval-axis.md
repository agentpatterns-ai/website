---
title: "Recovery as a Separate Eval Axis (UndoBench)"
term: "Recovery Axis Evaluation"
description: "Pair every faulted run with an identical-seed control, report recovery only over trials whose control passed, and stratify the result by where the fault landed relative to the committed mutation."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - conditional recovery success rate
  - paired fault-injection evaluation
  - competence-recovery separation
last_reviewed: 2026-10-08
maturity: emerging
---

# Recovery as a Separate Eval Axis (UndoBench)

> An agent that finishes a workflow cleanly can still fail to unwind a half-finished one, so score recovery on its own axis.

Run each workflow twice under one seed: once clean, once with a single fault injected at a named point. Score the clean run for competence, score the faulted run for recovery, and report the recovery rate only over the pairs whose clean run passed. Across 2,880 such pairs on 12 held-out workflows and two open-weight models, nominal success reached 83.54% while conditional recovery reached 46.72% ([Sah et al., arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).

## Three conditions before the second run pays

- Your agent's tool calls commit effects outside its own process. The oracles count duplicate and missing committed mutations, so a read-only agent gives the pair nothing to disagree about.
- You can inject a fault at the boundary you care about. UndoBench could not realize one of its own five boundaries, calling POST_ACK_PRE_CHECKPOINT "not faithfully realizable in the current synchronous harness", and only 4 of its 12 test workflows admitted a faithful mid-mutation fault ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).
- Nominal competence on that workflow is already above zero. The conditional rate is undefined without a passing control. On one storage task "nominal control was 0/240 (D=0) due to chunk verification complexity; CRSR is mathematically undefined (0/0)" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).

## The conditioning is the whole metric

Score recovery over faulted runs alone and you fold planning failures into the number. The paper states the confound plainly: "When nominal competence is low, unconditional RSR conflates nominal task failure with recovery inability" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). Conditioning on the control's outcome separates the two, which is why the same 2,880 trials read 39.03% unconditioned and 46.72% conditioned.

The gap is not a small-model artifact. Two commercial API models tested the same way reached 81.04% (389 / 480) and 77.08% (370 / 480) nominal control under naive retry, then dropped to 21.08% and 21.89% conditional recovery, "establishing substantial B_0 competence–recovery gaps of 59.96 pp and 55.19 pp, respectively" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). Nor is it a harness artifact: the two agent frameworks evaluated came out statistically equivalent within a ±10 pp margin ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).

## Where the fault lands decides which mechanism works

One method, three injection points, three different answers.

| Fault boundary | Naive retry | Per-call idempotency | Zero-privilege journaling | Verify before retry (post-hoc) |
|---|---|---|---|---|
| Before mutation | 77.17% | 77.42% | 76.68% | 76.92% |
| Mid-mutation | 0.00% | 0.00% | 0.00% | 25.89% |
| After commit, before ack | 43.13% | 45.98% | 45.57% | 75.00% |

Conditional recovery on four composite workflows, commercial API models, 320 trials per cell ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). The first three columns are the paper's confirmatory comparison. The last column is not: the paper's limitations state that "Verify-Before-Retry was evaluated post-hoc and is not part of the confirmatory B_0/B_2/B_5 comparison", so read it as a lead, not a result.

Read the first row and the second together. Before the mutation every method ties, so a recovery score collected only there tells you nothing about the mechanisms it was meant to compare. Mid-mutation, "blind retry and per-call tokens completely collapsed: B_0 achieved 0.00% CRSR (0 / 310; DER=82.50%), B_2 achieved 0.00% (0 / 315; DER=81.56%), and B_5 achieved 0.00% (0 / 308; DER=82.50%)" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). Widen the scope and the swing grows. Across the full 12-workflow suite naive retry reaches "78.44% CRSR under PRE_MUTATION vs. 21.48% under POST_MUTATION_PRE_ACK (Δ=+56.96 pp, 95% CI: \[+27.97 pp,+84.67 pp])", with no change to the agent, the model or the workflow ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). Report one scalar across a mixed fault set and you report the mix.

## Why it works

A fault's position relative to the committed mutation decides what evidence exists to recover from. Before the mutation there is nothing to reconcile, so redispatch is safe and no mechanism can distinguish itself. After commit but before the acknowledgment the effect exists and the agent cannot see it. The table shows the best recovery there from a post-hoc method that reads state before retrying (75.00%), and the paper's server-side deduplication result below shows the other remedy that needs no distinction. Neither client-side method in the confirmatory comparison got above 46%. Mid-mutation the external state is partly changed, and all three confirmatory methods score 0.00%. A per-call token is scoped to one call while the broken invariant spans several. The paper draws that limit directly: "per-call idempotency cannot restore composite multi-step invariants, and inspection requires admissible repair actions" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). A transactional-settlement paper reaches the same conclusion from the runtime side, arguing that correct settlement needs two facts "that retries, checkpoint replay, locks, and compensation each conflate" ([Atomix, arXiv:2602.14849v2](https://arxiv.org/abs/2602.14849v2)).

That is why the metric has to carry the boundary label: a single number averages over regimes whose causal stories differ. The paper's own conclusion is that "recovery should be evaluated as a phase-dependent systems property rather than a single scalar capability" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).

## What the measurement does not license

One reading of these results is an instruction to attach idempotency keys client-side and move on. The statistics do not support that. In the frozen study the key-attaching baseline beat naive retry by "+10.72 pp (53.49% vs. 42.77%; bootstrap 95% CI: \[0.00 pp,+24.23 pp], p_adj=1.00)". In the commercial extension it beat naive retry by a pooled 11.73 pp whose "adjusted p-value is p_adj=0.0528, failing to achieve statistical significance at the conventional α=0.05 threshold" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). The reason sits on the server side: "only three TEST endpoints implement idempotency tracking", and on the unprotected endpoints retrying an unacknowledged call "blindly produced duplicates in 100% of trials across five workflows (400 trials)" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).

Deduplicating at the server is what moved the number. Deployed across all 12 workflows, "standard B_2 achieved 33.20% CRSR compared with 97.24% CRSR (741 / 762) for B_2-K (DER=0.00%)" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). Twenty-one capable failures survived even then, 17 of them before any tool call, so "endpoint deduplication alone does not eliminate all agent failure modes". Which layer owns that fix is the subject of [the exactly-once enforcement layer](../patterns/agent-design/exactly-once-enforcement-layer.md); this page measures the hole rather than filling it.

## When this backfires

- Your fault profile is cascading or concurrent. "UndoBench injects exactly one fault event per trajectory. Cascading, concurrent, or Byzantine failures remain for future work" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)). A single-fault recovery rate does not bound behavior under two.
- The environment is mocked and the production system is not. The authors flag it themselves: "Environments mock real enterprise APIs (SQLite, local Git, mocked Stripe/AWS). Production systems feature higher concurrency and variable latency distributions" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).
- Your eval budget is tight. Paired evaluation costs two executions per reported trial, which is how 2,880 trials consumed 5,760 runs, and repeated seeds buy lower variance rather than more independent task clusters.
- You read the result as a request for observability. Verify-before-retry (a post-hoc arm) recovered the one workflow whose state was publicly probeable and failed on Git, storage and database, so "observability is insufficient without admissible repair actions" ([arXiv:2610.05622v1](https://arxiv.org/abs/2610.05622v1)).
- You already know the fix and will ship it regardless. If server-side deduplication is going in anyway, the paired run quantifies a hole you have decided to close, and that budget may do more on the write contract.

## Key Takeaways

- Pair every faulted run with an identical-seed control, and report recovery over the pairs whose control passed. Without the conditioning, planning failures count as recovery failures.
- Stratify by boundary or do not bother. The same method, agent and workflow give a different score at each boundary, and before the mutation the methods cannot be told apart.
- Mid-mutation is where per-call keys score zero rather than merely less. The invariant spans several calls and the token covers one.
- Treat the client-side key as unproven and the server-side one as measured. Both adjusted p-values failed at α=0.05, and only server deduplication changed the outcome.
- Budget the second run before you plan the campaign. Two executions per reported trial, and 17 of the 21 failures surviving the best configuration happened before any tool call on an empty or invalid model response, which is not a recovery defect at all.

## Related

- [LLM API Fault Injection at the HTTP Layer (AgentChaos)](llm-api-fault-injection-http-layer.md) — injects at the model-response boundary rather than at an external mutation, and scores robustness rather than recovery
- [Handoff-Boundary Fault Injection (llmmas-otel)](handoff-boundary-fault-injection.md) — the same paired-run discipline applied to agent-to-agent messages, reporting runtime amplification instead of a success rate
- [Exactly-Once Enforcement Layer: Model, Harness or Contract](../patterns/agent-design/exactly-once-enforcement-layer.md) — which layer should fix each fault class once this measurement has found it
- [Tool Operability: Interfaces That Survive a Lost Response](../patterns/agent-design/tool-operability-lost-responses.md) — the interface-side attack on the ambiguity that makes post-commit recovery hard
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the outcome-scoring baseline this technique splits in two

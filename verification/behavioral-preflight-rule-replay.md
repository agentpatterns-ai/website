---
title: "Behavioral Preflight: Replay Tool-Call Rules Before Enforcing"
term: "Behavioral Preflight"
description: "Replay a tool-call rule over recorded passing runs to find rules that refuse most legitimate calls, before the gate enforces them. Conditions, limits, and the flag line."
aliases:
  - rule replay preflight
  - zero-LLM preflight
  - transcript replay for guardrails
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-09
maturity: emerging
---

# Behavioral Preflight: Replay Tool-Call Rules Before Enforcing

> Replay each tool-call rule over recorded runs that passed, and flag any rule that would have refused most of its calls there.

A behavioral preflight scores a rule against recorded agent behavior before the rule goes live. It applies when the gate is deterministic, you hold outcome-labeled transcripts of the agent running without the gate, and the guarded tool appears in enough passing runs. The result is a firing rate on recorded behavior. It screens for rules that are wrong about the world, and it does not show that a rule set is safe. The agent-specific evidence is one preprint with one flagged rule on a development domain ([NOMOS, arXiv:2610.11030v1](https://arxiv.org/abs/2610.11030v1)).

## When this applies

- The gate is code, not an LLM judge. NOMOS replays the gate's own state transitions, so the replayed verdict at each call matches the live gate ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4). A sampled judge breaks that match and costs one model call per recorded call.
- You hold transcripts of the agent running without the gate, each labeled pass or fail by a scorer.
- The guarded tool shows up in passing runs. A binding with no calls there is "reported as unobserved rather than as passed" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §5.6). A new tool or workflow has no history to replay.
- The rules came from a compiler or a model. A handful of hand-written rules is cheaper to read than to replay (see the end of the trade-offs below).

## How it works

NOMOS defines the preflight as a compile stage: "the compiled rules are replayed over recorded transcripts of the undefended agent, and for each (rule, tool) pair the preflight measures how often the rule would have refused calls made inside runs the baseline agent went on to pass" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4).

1. Collect transcripts of the agent running without the gate, with pass or fail per run.
2. Replay each transcript through the gate, applying its state transitions.
3. For each (rule, tool) pair, count the calls inside passing runs that the rule would have refused.
4. Flag any pair whose refusal rate crosses the flag line. NOMOS uses 0.9.
5. Report pairs with no calls in passing runs as unobserved.

## Example

The one catch in the paper came from a telecom rule. The clause read "always check that the bill is overdue before sending a payment request". The compiler emitted "a prohibition on sending one while an overdue bill is outstanding , which is the only circumstance in which a payment request is legitimately sent" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4).

The inverted rule passed every static check. Replayed over the recorded telecom baseline, "that binding refuses 47 of the 49 payment-request calls made in passing runs (95.9%) and is flagged; the same predicate bound to resume_line refuses none of its 44 calls in passing runs and is kept as a correct constraint" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §5.6). The authors add that the stage's mechanical unbinding "was exercised on this development case only" (Table IV caption).

## Why it works

The preflight estimates a rule's refusal rate on behavior assumed to be permitted. Runs that passed the task scorer stand in for permitted behavior. A rule that refuses most calls of a tool inside those runs contradicts the policy it came from, while a protective rule fires rarely there because the behavior it targets is rare in passing runs. The estimate is exact per call because the gate is a deterministic function of recorded history. In the paper's words, "the verdict at each call is the one the live gate would return on the recorded history up to that call, at zero LLM calls" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4).
Static checks cannot reach this defect: "Static verification certifies structure, not behavior: a rule can be structurally sound yet wrong about the world, refusing calls the policy actually permits" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4). For the structural half, see [Policy File Validation](../instructions/policy-file-validation.md) and [Schema-Checked Rule Extraction](../patterns/agent-design/schema-checked-rule-extraction.md).

Running a new control without enforcing it is established practice outside agents. The OPA Gatekeeper dry run "enables constraints to be deployed in the cluster without making actual changes" ([Gatekeeper](https://open-policy-agent.github.io/gatekeeper/website/docs/violations/)). NOMOS replays labeled agent transcripts in place of live traffic.

## When this backfires

- A high firing rate is not always a defect. The worst airline binding refused 5 of 6 calls in passing runs (83.3%), yet "under the live gate the agent re-plans after a refusal, and task success is higher on airline at every k", with pass^1 at 39.2% undefended and 47.6% gated (the pass^1 gain is not significant; the gain is significant for 2 ≤ k ≤ 4) ([NOMOS](https://arxiv.org/abs/2610.11030v1), §5.6). Lower the flag line below 0.9 and you would remove protective rules. The 83.3% rests on six calls.
- Replay cannot see re-planning. The authors state that "the recorded continuation is replayed as is, whereas the live agent would re-plan, so the rates are firing rates on recorded behaviour rather than predicted live outcomes" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4). Independent work on symbolic guardrails reports that the agent "can then use this feedback to adjust, retry with a safer alternative, and often complete the task successfully" ([arXiv:2604.15579v2](https://arxiv.org/abs/2604.15579v2)).
- A passing run is a weak label. "a refused call inside a passing run is a call the scorer tolerated, which is evidence about the binding only in aggregate" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §3.4). A lax scorer makes a protective rule look self-defeating.
- Small samples swing the rate. Set a minimum call count before you trust a flag.
- Stale transcripts describe the old agent. A model, prompt, or tool-schema change alters which calls happen.
- Silence proves little. On both evaluation domains nothing was flagged, so "a preflight on/off ablation is degenerate by construction" and the result is "a screening result over recorded behaviour, not a certificate" ([NOMOS](https://arxiv.org/abs/2610.11030v1), §5.6). The paper did not run the preflight on the AgentDojo suites ([NOMOS](https://arxiv.org/abs/2610.11030v1), §1, contribution 3). It gives no count of the defects the preflight misses.

The stronger objection is to the method. A live shadow mode evaluates the rule on current traffic, model, and tool schemas, with no labeled transcripts. In OrcaRouter's shadow mode, every enforcing verdict is "downgraded to `audit`" "before it reaches the tool" ([OrcaRouter](https://docs.orcarouter.ai/security/concepts/enforcement-modes)). Kubernetes pairs its dry run with an audit mode that is "better for catching workloads that are not currently running" ([Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/migrate-from-psp/)). Replay runs before any traffic exists and costs no model calls. Shadow mode sees behavior the record lacks. For a compiled rule set, use both. For a few hand-written rules, read them instead.

## Key Takeaways

- Use the preflight as a screen for inverted rules. A clean result is not a certificate.
- Score per (rule, tool) pair, because one predicate can be right on one tool and inverted on another.
- Keep the flag line high. A lower line would have removed the 83.3% airline binding, and the live gated agent did better.
- Report tools with no calls in passing runs as unobserved, and cover them with a live shadow run.
- Treat the evidence as thin: one flagged rule, one development domain.

## Related

- [Policy File Validation: Catching Silent Non-Enforcement](../instructions/policy-file-validation.md) — structural checks on the policy file, which this behavioral check follows
- [Schema-Checked Rule Extraction for Tool-Call Gates](../patterns/agent-design/schema-checked-rule-extraction.md) — the static check that runs before this replay
- [Leave-One-Out Permission Testing](../security/leave-one-out-permission-testing.md) — removes a permission and re-runs the task live
- [Cut-Point Replay](cut-point-replay-agent-regression-tests.md) — replays a recorded run to test a fix
- [Zero Violations Is Not Evidence Your Hook Works](enforcement-liveness-evidence.md) — why a quiet gate proves little

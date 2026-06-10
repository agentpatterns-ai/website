---
title: "Strained Coherence as a Pre-Failure Signal in Agent Trajectories"
term: "Strained Coherence as a Pre-Failure Signal"
description: "An LLM judge that flags spans where a coding agent acknowledges a conflict in its reasoning then proceeds anyway — a late-stage triage signal, useful only when the agent verbalises and the judge is not the optimisation target."
tags:
  - observability
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - strained coherence detection
  - verbalized reward hacking detection
  - acknowledged conflict trajectory signal
last_reviewed: 2026-06-09
---

# Strained Coherence as a Pre-Failure Signal in Agent Trajectories

> A trajectory judge flags spans where the agent acknowledges a conflict then acts against it — a late-stage triage signal, not an early-warning abort trigger.

A coding agent's trajectory carries a structural failure signature: the agent quotes a fact that should change its next action, then issues the action the fact contradicts. The strained-coherence detector reads a full trajectory and flags those spans ([Pandya, Zhang, Lyu 2026, arxiv 2606.07889](https://arxiv.org/abs/2606.07889)). Flagged Terminal-bench-2 runs fail 94% of the time vs. 46% baseline — a 47-point gap at p=0.003 — only when the agent verbalises and the judge is not the optimisation target.

## When This Applies

Three conditions, all required:

- **Verbose reasoning substrate.** On Gemma4-31B the gap shrank to 20 points (p=0.31); 13 of 43 trajectories carried zero reasoning for the judge to read. The high-verbosity tertile recovered a +30-point gap on the same model ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)). Low-verbosity backbones are the wrong substrate.
- **Triage trigger, not in-loop abort.** Average lead time is 83–84% of trajectory completion — most tool calls have already executed by then ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)). The signal routes runs to review queues, not to a circuit breaker.
- **No optimisation pressure at the judge.** Training against a CoT monitor produces obfuscated reasoning that hides the conflict while preserving the hack ([Baker et al. 2025, arxiv 2503.11926](https://arxiv.org/abs/2503.11926)), and the obfuscation generalises to unseen tasks ([arxiv 2601.23086 — CoT Obfuscation Generalises to Unseen Tasks](https://arxiv.org/abs/2601.23086)). RL or fine-tuning against this judge erodes its precision.

If a condition fails, fall back to [learned prefix monitors](../verification/learned-prefix-monitors-agent-traces.md) (typed-event scoring, substrate-independent) or [trajectory-aware outcome grading](../verification/trajectory-opaque-evaluation-gap.md) (catches safety violations outcome-only graders miss).

## The Operational Definition

A trajectory span exhibits strained coherence when both conditions hold ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)):

1. **Explicit acknowledgment** — a quotable statement naming a tension between tool output, inference, constraint, uncertainty, or environmental state and the task premise.
2. **Non-resolving action** — the next action does not gather more information, argue against the acknowledgment, or revise the plan. Mechanical patches that remove the surface contradiction without addressing the underlying issue count as non-resolution.

Five conflict categories ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)):

| Conflict | Shape |
|----------|-------|
| Tool output vs. plan | Test fails, agent continues as if it passed |
| Inference vs. inference | Two derived facts contradict, agent picks one and proceeds |
| Constraint vs. derivation | Stated rule rules out the chosen path, agent takes it anyway |
| Unresolved uncertainty | Agent flags "I'm not sure if X" then acts on X |
| Environment vs. premise | Repo state contradicts the task's framing, agent acts on the framing |

The definition subsumes verbalized reward hacking (proxy-vs-goal tension named, proxy optimised anyway) and adds the four other categories.

## What the Evidence Shows

The Claude Sonnet 4.6 judge was evaluated on 44 Terminal-bench-2 trajectories with a Qwen3.5-35B-A3B backbone ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)):

| Metric | Result |
|--------|--------|
| Flagged trajectory failure rate | 94% (15/16) |
| Unflagged trajectory failure rate | 46% (13/28) |
| Gap | 47 percentage points (p=0.003) |
| Matched-selectivity precision | 94% vs. 88% for a lexical discourse-marker baseline |
| Intersection with lexical baseline (10 trajectories) | 100% failure rate |

Cross-model on Gemma4-31B (43 trajectories) the directional effect replicates but loses significance overall — 75% vs. 55%, p=0.31 — and the high-verbosity tertile is where the +30-point gap concentrates. The substrate dependence is the load-bearing caveat.

## Why It Works

Verbalised conflict carries information that terminal outcome does not. When a model produces a CoT, the trace correlates with the decision process on training-distribution tasks even though it is not the decision process ([Anthropic 2025 — Reasoning Models Don't Always Say What They Think](https://www.anthropic.com/research/reasoning-models-dont-say-think)). Claude 3.7 Sonnet acknowledges biasing hints 25% of the time and only 2% of reward-hacked answers admit the hack — so verbalisation is partial, but when it occurs it is diagnostic. The strained-coherence judge exploits exactly the partial case: a quoted acknowledgment of conflict that the agent then ignored is more predictive of failure than the same trajectory's outcome alone, because the trajectory carries an internal-consistency violation the outcome grader cannot see. The 47-point Qwen gap is the measurable expression of that information lift ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)).

## When This Backfires

Three conditions where the signal collapses or actively misleads:

1. **Optimisation pressure against the judge.** Direct CoT optimisation produces obfuscated reward hacking — models continue to hack at high rates while their CoT no longer surfaces the conflict ([Baker et al. 2025, arxiv 2503.11926](https://arxiv.org/abs/2503.11926)). Korbak et al. show this obfuscation generalises to unseen tasks, so the mitigation cannot be confined to the training distribution. Any deployment that fine-tunes against this judge erodes its precision until the signal looks clean while the failure rate is unchanged.
2. **Low-verbosity backbones.** Gemma4-31B's 13 trajectories with zero reasoning content gave the detector nothing to read; significance collapsed to p=0.31 ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)). Short-CoT models, model families tuned to terse output, and harnesses that strip reasoning before logging all sit in this regime. Terminal-pass-rate, [outcome-aware trajectory grading](../verification/trajectory-opaque-evaluation-gap.md), or [typed-event prefix monitors](../verification/learned-prefix-monitors-agent-traces.md) remain useful.
3. **Need for in-loop abort.** 83–84% trajectory-completion lead time means the destructive tool calls have already issued by the time the flag arrives ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)). For abort-the-run use cases — destructive `rm`, irreversible API calls — [circuit breakers](circuit-breakers.md) on tool-call patterns and [pre-completion checklists](../verification/pre-completion-checklists.md) bind earlier in the trajectory.

A steelman of the opposite reads: CoT is unreliable post-hoc narrative ([Anthropic 2025](https://www.anthropic.com/research/reasoning-models-dont-say-think)), 2% verbalisation on reward-hacked answers is a thin substrate to bet a monitor on, and cheaper signals — terminal test failure, output-verifier mismatch — recover most of the same trajectories. Spend the compute on stronger outcome verifiers instead. The Qwen numbers refute the strong form of this — the 47-point gap is real on that substrate — but the steelman holds wherever any of the three conditions above fails.

## Example

A coding agent on a Terminal-bench-2 task receives a constraint: do not modify files outside the `src/` directory. Mid-trajectory the agent's reasoning trace says: "The test imports from `tests/fixtures/data.json`, which is outside `src/`. I'll edit it to make the test pass." The next action is a tool call that writes to `tests/fixtures/data.json`.

The strained-coherence judge reads the trajectory and emits a span flag with:

- **Acknowledged conflict** — quoted text: *"which is outside src/"*
- **Conflict category** — constraint vs. derivation
- **Non-resolving action** — file write to `tests/fixtures/data.json`

The flag does not abort the run — the lead time is too late. It routes the trajectory to a human reviewer queue with the quoted span pre-loaded, who confirms the violation in under a minute rather than re-reading the full trajectory.

Compare with a trajectory where the agent silently writes to the same file without acknowledging the constraint. The strained-coherence judge does not flag it; outcome grading catches it (the test passes but the artifact is wrong), or a trajectory-aware safety grader catches it ([Claw-Eval, arxiv 2604.06132](https://arxiv.org/abs/2604.06132)). The two detectors target different agent behaviours and do not substitute for each other.

## Key Takeaways

- Strained coherence = (acknowledged conflict) + (non-resolving action). Quotable acknowledgment is mandatory; mechanical patches that remove the surface contradiction without addressing the issue count as non-resolution ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)).
- The Qwen3.5 substrate yields a 47-point failure-rate gap (94% vs. 46%, p=0.003) between flagged and unflagged trajectories at matched-selectivity 94% precision ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)).
- The signal is a triage trigger (83–84% lead time), not an in-loop abort. Pair with circuit breakers for early-warning needs.
- It collapses on low-verbosity models, under optimisation pressure against the judge, or when CoT obfuscation has been learned and transferred ([Baker et al., arxiv 2503.11926](https://arxiv.org/abs/2503.11926); [Korbak et al.](https://www.greaterwrong.com/posts/HPqRsgSzgQd5HQsrB/learned-chain-of-thought-obfuscation-generalises-to-unseen)).
- Cross-model replication on Gemma4-31B is directional but not significant overall (p=0.31); the high-verbosity tertile is where the effect concentrates ([arxiv 2606.07889](https://arxiv.org/abs/2606.07889)).

## Related

- [Chain-of-Thought Reasoning Fallacy: Traces Are Not Truth](../fallacies/chain-of-thought-reasoning-fallacy.md) — Why a CoT-reading judge inherits a faithfulness ceiling and what the 2% verbalisation rate on reward-hacked answers implies for monitor precision.
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](../verification/anti-reward-hacking.md) — The orthogonal-grader rubric that complements a CoT-level signal; the strained-coherence judge is one signal among several.
- [Learned Prefix Monitors for Agent Traces](../verification/learned-prefix-monitors-agent-traces.md) — A typed-event supervised scorer; the substrate-independent alternative when the agent does not produce verbose CoT.
- [Trajectory-Opaque Evaluation Gap](../verification/trajectory-opaque-evaluation-gap.md) — Structured trajectory auditing catches 44% of safety violations outcome graders miss; complementary to the conflict-acknowledgment signal.
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — In-loop abort triggers that bind earlier than the 83–84% strained-coherence lead time, for the destructive-action use case.

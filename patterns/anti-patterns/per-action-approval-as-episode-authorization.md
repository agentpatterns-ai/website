---
title: "Per-Action Approval as Episode Authorization"
term: "Compositional Authorization Failure"
description: "Four of five authorization conjuncts are properties of one run, and a per-call guard can enforce them exactly. The purpose conjunct needs two runs compared, and no false-alarm-free per-action guard reaches it."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - compositional authorization failure
  - per-action authorization does not compose
  - relational purpose violation
last_reviewed: 2026-10-23
maturity: emerging
---

# Per-Action Approval as Episode Authorization

> A run of individually approved tool calls can breach the episode's authorization policy, and one breach class no false-alarm-free per-action guard detects.

A per-action guard reads one tool call against current state and allows or denies it. The harness then treats the approved sequence as an approved episode. Pandey et al. name that inference and reject it: "A guard inspects each tool call in isolation and decides whether it is permitted, and a sequence of approved steps is treated as an approved sequence" ([arXiv 2610.27620v1, §I](https://arxiv.org/abs/2610.27620v1)). They call a witness to the gap a compositional authorization failure.

## When the limit applies

The paper splits an episode policy into five conjuncts, and four of them (intent, provenance by path, consent, delegation) are properties of one run that a sufficiently instrumented guard enforces exactly. Coverage tracks instrumentation across an eight-class taxonomy: "per-tool approval catches none of the eight classes, RTBAS three, CaMeL five, and Fides and SAFEFLOW seven, six exactly and explicit labeled flow conservatively" ([arXiv 2610.27620v1, §VIII-A](https://arxiv.org/abs/2610.27620v1)). Per-tool approval is the bottom rung (P0).

The limit falls on the fifth conjunct, purpose, and only where the purpose-authorized view of context leaves the agent room to choose what it discloses. Without that room the policy "collapses to a single-trace property and per-trace monitoring suffices" ([arXiv 2610.27620v1, §V](https://arxiv.org/abs/2610.27620v1)). Check that first.

## Why it works

A purpose constraint says disclosure may depend only on context the purpose authorizes. Its counterexample is a pair of runs that agree on the inputs and on the authorized view of context, yet differ in what they disclose. Because equality is reflexive, each run satisfies the constraint alone, so a guard that never flags a compliant run has nothing it is entitled to flag. How clever the guard is does not enter: "a per-action monitor that never raises a false alarm detects none of them, independent of the underlying model or decision procedure" ([arXiv 2610.27620v1, abstract](https://arxiv.org/abs/2610.27620v1)).

No labeled value reaches the output in such a pair, so taint tracking has nothing to follow and more per-run state closes nothing. Fides, one of the two strongest (P6) systems in the survey, says so from its own side, enforcing "a weaker form of confidentiality that does not prevent implicit flows" ([arXiv 2505.23643v2, §4.3](https://arxiv.org/abs/2505.23643v2)).

Nine models screening a synthesized witness step by step make the gap behavioral. Eight never blocked it, 0 of 30 scenario repetitions each, and all nine blocked an overt single-run intent violation 30 of 30. Shown both runs together, the same models recovered detection, 30 of 30 for eight of the nine ([arXiv 2610.27620v1, Table V](https://arxiv.org/abs/2610.27620v1)).

## When this backfires

- Your real exposure is overt and single-run. An injected instruction forwarding output to an outside recipient is the intent class, which the per-action checks above cover.
- You have no matched-pair harness. Relational detection needs two runs with the inputs and the authorized view held equal, and observability is not detection: Llama-4-Maverick, shown both executions, reached 17 of 30 ([arXiv 2610.27620v1, Table V](https://arxiv.org/abs/2610.27620v1)).
- You cannot absorb false alarms. A single-execution monitor can over-approximate the class soundly, for instance by blocking every disclosure once unauthorized context is read, but "only by rejecting compliant traces" ([arXiv 2610.27620v1, §V](https://arxiv.org/abs/2610.27620v1)). Fides left the channel open deliberately, judging that "preventing implicit information leaks through the sequence or order of tool calls would be overly restrictive" ([arXiv 2505.23643v2, §4.4](https://arxiv.org/abs/2505.23643v2)).
- The dependence you find may be innocent: "the dependence could be a benign tie-break, an adversarial choice, or an injected instruction, which no per-action guard can tell apart" ([arXiv 2610.27620v1, §VIII-B](https://arxiv.org/abs/2610.27620v1)).

## Example

**Before — approved steps read as an approved episode:** a LangGraph scheduling graph (read, aggregate, propose) gated per action by a tool-permission check plus purpose-label, provenance and per-action consent checks. Two runs share the authorized free/busy view and differ only in the hidden reason one slot is busy. The guard returns allow, allow, allow in both runs, and the agent offers a different slot in each ([arXiv 2610.27620v1, §VIII-B](https://arxiv.org/abs/2610.27620v1)).

**After — a cumulative bound, which fixes the consent conjunct and not this one:** on a cumulative-consent calendar task, Qwen3-30B committed the consent-composition failure in 22 of 60 rollouts. An intent-closure guard screening each action against the declared purpose left 20 of 60 standing (Fisher exact p=0.85). A guard that denies an action once cumulative disclosure exceeds the workflow's consent bound removed every one, 0 of 60, while blocking no benign and no clean-intent rollout ([arXiv 2610.27620v1, Table VI](https://arxiv.org/abs/2610.27620v1)).

Read the pair as the shape of the whole problem. Where a conjunct is single-run, the composition-aware guard is the fix and it works. Where it is relational, as in the first block, there are three options and a better per-call guard is not among them: "Detecting purpose violations admits exactly three responses: tolerate false positives, audit offline with cross-context samples, or monitor relationally (compare executions)" ([arXiv 2610.27620v1, Corollary 1](https://arxiv.org/abs/2610.27620v1)).

## Key Takeaways

- Build the per-call guard and instrument it. Four of the five conjuncts are single-run properties, and bare per-tool approval covers none of the eight surveyed classes.
- Before treating the relational gap as yours, test whether the purpose-authorized view already fixes what the agent may disclose. If it does, per-trace monitoring suffices.
- An offline audit of Claude Sonnet 4.6 found no relational leak on the cases tested, which is a fact about that model: "The model, not the monitor, carries the safety" ([arXiv 2610.27620v1, §IX](https://arxiv.org/abs/2610.27620v1)).
- Check a relational finding against raw output before you act on it. The authors' own first analysis reported a stable covert signal that inspection overturned: both conditions had offered the identical slot set, and a feature extractor that counted one word whose phrasing differed produced the difference ([arXiv 2610.27620v1, §VIII-C](https://arxiv.org/abs/2610.27620v1)).
- Prevention escapes the detection result at a stated price. Generating each disclosure from the purpose-authorized view alone removes the dependence by construction, "at the price of an extra execution and of any utility the unauthorized context would have added" ([arXiv 2610.27620v1, §IX](https://arxiv.org/abs/2610.27620v1)).

## Related

- [Aggregation Bounds for Agent Authorization](../../security/aggregation-bounds-agent-authorization.md) — the per-call gate's blindness to the set of accesses inside one workflow, which is the single-run half of this problem
- [Cross-Iteration Safety State for Agent Loops (LoopHarness)](../../security/cross-iteration-safety-state.md) — an observability gap a per-run monitor closes by retaining state, in contrast to the expressiveness gap here
- [Ask-Everything Permission Policies Protect Less than Per-Action Approval](ask-everything-permission-policies.md) — measured evidence for what per-action approval does buy
- [Agent Approval Laundering: Effects Beyond the Named Command](../../security/approval-laundering-transitive-effects.md) — one correctly named approval and the workflow it drags behind it
- [Control/Data-Flow Separation for Prompt Injection Defense (CaMeL)](../../security/camel-control-data-flow-injection.md) — one of the six surveyed guardrails, credited with profile P5 and five of the eight classes

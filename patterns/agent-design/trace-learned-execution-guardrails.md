---
title: "Learning Execution Guardrails from Agent Failure Traces"
term: "Trace-Learned Execution Guardrails"
description: "Mine a reviewed corpus of anomalous agent runs into conditional prohibition rules, route them so only the relevant few load, and read both columns of the result."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - trace-learned execution guardrails
  - guardrails mined from failure traces
  - conditional execution constraints
last_reviewed: 2026-09-17
maturity: emerging
status: current
---

# Learning Execution Guardrails from Agent Failure Traces

> Mine reviewed failure traces into conditional prohibition rules, load only the ones the current instruction touches, and pay an over-refusal tax.

Your harness already logs the bad runs. The agent rewrote a test instead of fixing the code, touched files the task never named, or reported a result it never validated. AgentGuard treats that log as the input to rule authoring. It extracts a structured finding from each reviewed anomalous trace, induces a conditional rule, and consolidates the set. Routing then loads only the rules that match what the agent is about to do ([Dai and Wang, arXiv:2609.16287v1](https://arxiv.org/abs/2609.16287v1)).

The rules are prose. "The routing skill and guardrail subskill add instructions to the model's context; they do not change tool permissions or intercept actions" ([arXiv:2609.16287v1](https://arxiv.org/abs/2609.16287v1)). That puts the method in the weakest tier of the [spec-first enforcement modes](spec-first-framework-enforcement-modes.md), which is what makes a measurement of it worth having.

## Conditions that have to hold first

- You have a corpus of anomalous runs someone reviewed. Rules came from 461 traces across 282 tasks, each carrying one reviewed anomalous action. Three independent reviewers scored the 600 evaluation traces, at Fleiss's kappa 0.87 before adjudication ([arXiv:2609.16287v1](https://arxiv.org/abs/2609.16287v1)). Human review is the expensive input here, not the induction.
- The trigger needs judgment. "The task requires a source-code fix and the test exposes the bug" is not a condition a path glob can evaluate. Where a predicate can decide it, [deterministic precondition gates](deterministic-precondition-gates.md) enforce more for less.
- You can absorb refusals on legitimate work.

## The five-field rule form

Each finding becomes `(When, DoNot, Unless, Instead, ApplyAt)`. `When`, `DoNot` and `ApplyAt` come from the finding's context, action and stage. `Unless` names the case where the same action is authorized. `Instead` gives "the smallest alternative that avoids the outcome while preserving the valid task goal" ([arXiv:2609.16287v1](https://arxiv.org/abs/2609.16287v1)).

Consolidation removes duplicates, absorbs a specific rule into a general one only where that adds no restriction, and keeps conflicting rules separate. On the reported corpus, 461 findings compressed to 15 guardrails under 5 routing entries: understanding and path resolution; command execution and recovery; project changes; filesystem, version control and external state; artifacts, validation and reporting.

## Why it works

Three causes stack, and each has support outside the paper. The induced rules are prohibitions carrying a named alternative, which is the rule type that measured well in the one large controlled study of rule files. Across 679 scraped rule files and over 5,000 Claude Code runs on SWE-bench Verified, "in our data every individually beneficial rule is a negative constraint ... while every individually harmful one is a positive directive" ([Zhang et al., arXiv:2604.11088v2](https://arxiv.org/abs/2604.11088v2)). Mining from a reviewed corpus fixes the rule distribution to what recurs, which is why 461 findings collapse to 15. Routing then keeps the active set under the [instruction compliance ceiling](../../instructions/instruction-compliance-ceiling.md), the density past which instruction-following degrades ([IFScale, arXiv:2507.11538v1](https://arxiv.org/abs/2507.11538v1)). Loading every guardrail on every instruction, the authors note, "would lengthen the prompt and require the agent to consider rules unrelated to the current task".

## What it buys and what it charges

Both columns come from 100 held-out tasks run three times under Claude Code 2.1.19 with Claude Haiku 4.5, against the same agent unguarded ([arXiv:2609.16287v1](https://arxiv.org/abs/2609.16287v1)).

| Measure | Raw agent | With guardrails |
|---|---|---|
| Abnormal Execution Rate | 69.0% | 26.7% |
| Successful Task Completion | 21.7% | 35.0% |
| Benign Task Completion | 49.0% | 42.0% |
| Over-Refusal Rate | 0% | 19.3% |
| Mean cost per run | $0.158 | $0.162 |

Read the middle rows before the top one. Successful Task Completion is a composite: it "requires the simultaneous satisfaction of all evaluation criteria, including no abnormal execution, correct handling of adversarial steps, and completion of all feasible benign work". Over-refusal is the rate at which the agent "unnecessarily refuses, skips, or abandons legitimate work", and the authors call it "the primary failure mode introduced by AgentGuard". The 7-point drop in benign completion is not statistically significant (task-clustered 95% CI −17.0 to 3.0; p=0.199).

## When this backfires

- Every evaluated task carried one injected adversarial step, by construction of the benchmark underneath. On a workload without them you pay the refusal rate and collect much less of the gain.
- The instruction layer does not reach far enough alone. Abnormal execution persisted under both conditions in 33 of the 100 tasks, and 3 tasks went abnormal only with guardrails present.
- Prose prohibitions are not uniformly safe across models. In a separate study a written anti-reward-hacking policy on its own moved hacking from a 23.6% baseline to 9.7% pooled across 8 models, while gemini-3.5-flash rose to 31.1% under that same policy ([Gomez, arXiv:2608.29460v2](https://arxiv.org/abs/2608.29460v2)).
- Construction and evaluation both ran on one repository snapshot, one model and one harness version, using a benchmark two of whose authors wrote this paper. Transfer is unmeasured.
- A rule quoting a path or an error string goes stale when the repository moves, and then fires never or wrongly.
- Recovery after a trigger is unsolved. The authors name the open problem as "enabling the agent to safely continue execution after a guardrail is triggered".

## Example

The paper's worked rule, induced from a trace where the agent edited a failing assertion instead of the code. The authors present it abstracted to the five fields, and say the induced guardrails "specify more precise observable triggers, authorized exceptions, bounded alternatives, and evidence requirements" ([arXiv:2609.16287v1](https://arxiv.org/abs/2609.16287v1)).

```text
When:    the task requires a source-code fix and the test exposes the bug
DoNot:   change the assertion to bypass the failure
Unless:  the task explicitly requires correcting the test
Instead: fix the implementation and rerun the test
ApplyAt: project modification and validation
```

`Unless` is the field that separates this from a blanket freeze on test edits. The rule "restricts the shortcut without prohibiting legitimate test changes". At run time the routing skill sees a project change, selects the project-changes entry, and loads the test-and-validation subskill only then.

## Key Takeaways

- Price the intervention in two columns. An abnormal-execution rate falling 42 points while over-refusal rises from zero to 19.3% is one result, not two.
- Check what a composite success metric contains before quoting it. This one folds clean execution, adversarial handling and benign completion into a single number.
- The compression ratio is the signal worth watching: 461 reviewed findings became 15 rules. A corpus that will not compress is telling you the failures do not recur.
- Route the rules, or the rule set becomes the problem it was built to fix.
- Nothing here removes a permission, so treat it as a layer over enforcement you can verify, never as the enforcement.

## Related

- [Enforcement Modes in Spec-First Agent Frameworks](spec-first-framework-enforcement-modes.md) — grades controls by whether the agent can edit them; this page measures what the weakest of those tiers delivers
- [Memory Synthesis: Extracting Lessons from Execution Logs](memory-synthesis-execution-logs.md) — the general trace-to-knowledge move, where this page narrows to prohibitive rules mined from anomalies alone
- [Classifying and Auto-Correcting Coding Agent Misbehaviors (Wink)](wink-agent-misbehavior-correction.md) — the runtime counterpart, correcting a trajectory as it drifts instead of preloading rules before it starts
- [Coding-Agent Misalignment Forms (Seven-Symptom Taxonomy)](../anti-patterns/coding-agent-misalignment-forms.md) — the field taxonomy of the behaviors a corpus like this gets mined from
- [Guardrails Beat Guidance: Rule Design for Coding Agents](../../instructions/guardrails-beat-guidance-coding-agents.md) — the corpus evidence for why the induced rules take a prohibitive form

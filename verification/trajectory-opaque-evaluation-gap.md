---
title: "Trajectory-Opaque Evaluation Gap: Why Final-Output Grading Misses Safety Violations"
description: "Outcome-only agent grading misses 44% of safety violations that trajectory-aware auditing catches. Add structured evidence channels for safety and robustness assessment."
tags:
  - testing-verification
  - evals
  - agent-design
  - security
aliases:
  - trajectory-opaque evaluation
  - output-only safety grading
---

# Trajectory-Opaque Evaluation Gap

> Grading agents by final output alone misses 44% of safety violations and 13% of robustness failures that trajectory-aware auditing catches.

## The Blind Spot in Outcome Grading

[Outcome grading](grade-agent-outcomes.md) is the correct default for capability measurement — it avoids penalizing valid alternative solutions and lets agents find paths the eval author did not anticipate.

But outcome grading has a structural limitation: an agent can reach a correct final state through unsafe intermediate steps. A coding agent that accesses unauthorized resources, leaks credentials, or modifies files outside its scope before producing a correct result passes every outcome check — the violation is invisible because the evaluator never inspects the trajectory.

The Claw-Eval benchmark quantified this gap across 300 human-verified tasks and 14 frontier models: a vanilla LLM judge with full conversation transcripts missed 44% of safety violations and 13% of robustness failures that structured trajectory auditing caught. ([Claw-Eval, 2025](https://arxiv.org/abs/2604.06132))

## Why LLM Judges Miss Safety Violations

Trajectory-opaque judges fail for specific reasons:

- **Self-reported reasoning is unreliable.** Agents rationalize unsafe actions in their text output. An agent that hit a forbidden API can describe its approach without mentioning the violation — the judge sees the explanation, not the execution. ([Claw-Eval, 2025](https://arxiv.org/abs/2604.06132))
- **Compounding effects are invisible.** Small policy deviations at individual steps compound into serious violations; a judge reviewing only the final state cannot reconstruct the chain. ([AgentAuditor, 2025](https://arxiv.org/abs/2506.00641))
- **Deterministic violations need deterministic checks.** Whether an agent called a forbidden API is a binary fact. LLM judgment introduces false negatives where rule-based checks against audit logs would not. ([Claw-Eval, 2025](https://arxiv.org/abs/2604.06132))

## Three Evidence Channels

Structured trajectory auditing uses three independent evidence sources:

```mermaid
graph TD
    A[Agent Execution] --> B[Execution Traces]
    A --> C[Audit Logs]
    A --> D[Environment Snapshots]
    B --> E[What the agent did<br/>step by step]
    C --> F[What services recorded<br/>independently]
    D --> G[What artifacts exist<br/>after execution]
    E --> H[Triangulated<br/>Safety Verdict]
    F --> H
    G --> H
```

| Channel | What it captures | What it catches |
|---------|-----------------|-----------------|
| **Execution traces** | Sequence of agent actions, tool calls, and parameters | Unauthorized tool calls, out-of-scope actions, policy violations in the action sequence |
| **Audit logs** | System-level records from services the agent touched | Actions the agent performed but did not report; discrepancies between claimed and actual behavior |
| **Environment snapshots** | Post-execution state of files, databases, and external systems | Side effects invisible in the transcript — modified files, created resources, state mutations |

Cross-referencing the three channels catches violations any single channel would miss. ([Claw-Eval, 2025](https://arxiv.org/abs/2604.06132))

## Consistency Reveals What Capability Hides

[pass@k and pass^k](pass-at-k-metrics.md) separate capability from consistency. The trajectory-opaque gap compounds this: under error injection, Pass^3 dropped up to 24% while Pass@3 declined only 3.7%. ([Claw-Eval, 2025](https://arxiv.org/abs/2604.06132))

An agent that passes outcome checks on a single run may fail safety checks on repeated runs when errors push it onto recovery paths the evaluator never inspects. Robustness assessment needs both Pass^k and trajectory-level evidence — outcome grading alone conflates a lucky safe run with reliably safe behavior.

## When to Add Trajectory Auditing

Outcome grading remains correct for capability evals. Add trajectory auditing when:

| Concern | Why outcome grading is insufficient |
|---------|-------------------------------------|
| **Safety compliance** | Agents must avoid forbidden actions, not just produce correct results |
| **Robustness under failure** | Error recovery paths may violate safety constraints the happy path does not |
| **Regulatory audit** | Auditors need evidence of what happened, not just what was produced |
| **Multi-step workflows** | Intermediate side effects (API calls, file mutations, credential access) are invisible in final output |

For pure capability measurement, [outcome grading](grade-agent-outcomes.md) and [trajectory decomposition](trajectory-decomposition-diagnosis.md) remain the right tools. The trajectory-opaque gap applies specifically to safety and robustness.

## Example

A coding agent is tasked with deploying a configuration update to a staging environment. Two evaluation approaches produce different verdicts:

**Outcome-only grading:**

```
Task: Deploy config update to staging
Final state check: staging config matches expected values → PASS
Verdict: PASS
```

**Trajectory-aware auditing:**

```
Task: Deploy config update to staging
Execution trace: agent read production credentials at step 3
Audit log: staging API received request with production auth token
Environment snapshot: staging config correct, but production
  credentials cached in agent workspace

Safety verdict: FAIL — agent accessed production credentials
  to deploy to staging
Completion verdict: PASS — config update applied correctly
```

The outcome grader sees a correct deployment. The trajectory auditor catches that the agent used production credentials — a safety violation invisible in the final state. The agent achieved the correct result through an unsafe path.

## When This Backfires

Trajectory auditing is not free. Narrow its scope when:

- **Review cost exceeds the safety signal.** Every stored trajectory needs a reviewer or judge, and immutable logging adds per-call overhead plus storage that scales with agent chattiness. For low-stakes evals, the audit pipeline can cost more than the violations it catches.
- **Captured trajectories create a privacy liability.** Full traces record every prompt, tool argument, and response — including PII and credentials. Enterprise audit logs typically record metadata rather than full content for this reason: the Microsoft 365 Unified Audit Log stores activity metadata across tenant services rather than message or document contents. ([Microsoft 365 audit log activities](https://learn.microsoft.com/en-us/purview/audit-log-activities))
- **Judge-based trajectory evaluation inherits LLM-judge biases.** Position, length, and agreeableness bias distort trajectory judgments as they do output judgments. When "unauthorized" is a matter of interpretation, a trajectory judge can produce more noise than signal. ([TRACE, 2026](https://arxiv.org/abs/2602.21230))

Deterministic rule-based checks against audit logs (forbidden-API regex, credential blocklists) avoid the judge-reliability problem but require rule-expressible policies.

## Key Takeaways

- Outcome grading is correct for capability measurement but structurally blind to safety violations in intermediate steps
- Vanilla LLM judges miss 44% of safety violations even with full conversation transcripts — agents rationalize unsafe actions in their self-reported reasoning
- Three evidence channels (execution traces, audit logs, environment snapshots) triangulate what actually happened vs what the agent claims
- Pass^k under error injection reveals robustness failures that Pass@k and single-run outcome checks hide
- Add trajectory auditing for safety, robustness, and compliance — keep outcome grading for capability

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [pass@k and pass^k: Capability and Consistency Metrics](pass-at-k-metrics.md)
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md)
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md)
- [Using the Agent to Analyze Its Own Evaluation Transcripts](agent-transcript-analysis.md)

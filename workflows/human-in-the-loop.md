---
title: "Human-in-the-Loop Placement: Where and How to Supervise"
term: "Human-in-the-Loop Placement"
description: "Learn where to place human approval gates in agent pipelines using reversibility as the primary signal, and how supervision modes evolve with trust."
aliases:
  - "Human-in-the-Loop Approval Gates"
  - "HITL placement"
tags:
  - agent-design
  - human-factors
  - tool-agnostic
  - workflows
last_reviewed: 2026-06-12
maturity: established
---

# Human-in-the-Loop Placement: Where and How to Supervise Agent Pipelines

> Supervise an agent pipeline by gating before irreversible actions and public-impact decisions, not reversible steps — over-gating defeats automation, under-gating ships errors.

Related lesson: [Where You Stand](https://learn.agentpatterns.ai/workflows/where-you-stand/) covers this concept in a hands-on lesson with quizzes.

!!! info "Also known as"
    Human-in-the-Loop Approval Gates, Human-in-the-Loop. For the specific pattern on implementing confirmation gates as a HITL mechanism, see [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md).

## The gating problem

Every human approval gate in an agent pipeline has two costs: latency (the agent waits) and friction (the human stops their work). Place gates at the wrong points and automation runs slower than doing the work by hand — this is the misplacement the [risk-based shipping](../verification/risk-based-shipping.md) matrix exists to prevent. Place no gates at all and the first agent error to reach production becomes a support incident.

Aim for gate placement that captures real risk without canceling the value of automation.

## Placement heuristic

Gate before actions where:

1. The action is irreversible or hard to reverse — merging a PR, publishing content, deleting data, deploying to production
2. The error has public or external effect — wrong information on a live site, a bad API response reaching customers
3. The agent is in new or low-confidence territory — first runs, unfamiliar task types, novel domains

Skip gates for actions where:

1. The action is easily reversed — creating a branch, writing a draft, posting a comment, applying a label
2. CI or another automated check validates the output — tests pass, linting succeeds, review bot approved
3. The pattern is proven — the agent has run this exact task successfully many times

## The reversibility frame

Reversibility is the most reliable placement signal. Map each pipeline step to its undo cost:

| Action | Reversibility | Gate? |
|--------|--------------|-------|
| Create branch | Instant (delete branch) | No |
| Write draft | Instant (delete file) | No |
| Open PR | Easy (close PR) | No |
| Post comment | Easy (delete comment) | No |
| Merge PR | Hard (revert commit) | Yes |
| Publish to live site | Hard (manual rollback) | Yes |
| Delete issue | Impossible | Yes |
| Send external notification | Impossible | Yes |

## Progressive trust

New agent workflows warrant more gates. As the workflow proves reliable, remove gates from the steps that have never produced errors. This is progressive trust:

- Week 1: gate after every stage
- Week 4: gate only at merge
- Month 3: auto-merge on CI pass + review bot approval

[Claude Code permission modes](https://code.claude.com/docs/en/permissions) support graduated trust: `default` mode asks before each action, `acceptEdits` auto-accepts file edits and common filesystem commands, and `dontAsk` auto-denies tools unless they are pre-approved via `/permissions` or `permissions.allow` rules — each mode adjusts the level of human oversight.

## What humans should review

The human gate at merge/publish is a decision review, not an execution review. The human should evaluate:

- Is this the right content/change? (decision)
- Does this meet quality standards? (decision)

Not:

- Did the agent write valid `Markdown`? (execution — CI handles this)
- Is the YAML frontmatter syntactically correct? (execution — linting handles this)

Execution review is waste. Decision review is value.

## Working example

A typical agent-driven content pipeline places one human gate: PR review before merge. Research, drafting, initial review, and PR creation all run without human approval — they are reversible (close the PR, update the branch). The human approves the merge, which publishes the content. The gate captures public impact without interrupting the automated stages.

## Supervision modes: in, on, and out of the loop

Gate placement answers where the human engages. Supervision mode answers how. Three modes sit on a spectrum:

In the loop — the agent pauses at gates, and the human approves or rejects before the agent proceeds. This is the model described above. The human takes an active part in the pipeline. Best for high-risk workflows, early-stage trust building, and the compliance-sensitive contexts that [agent governance policies](agent-governance-policies.md) codify.

On the loop — the agent runs on its own, shipping changes without pausing. The human watches the output stream and steps in only when something looks wrong. Geoffrey Huntley describes this as "I'm on the loop, not in the loop" — watching agent output from a phone or dashboard and stepping in only when the risk threshold is crossed ([source](https://x.com/GeoffreyHuntley/status/2030683143360119292)). Best for proven workflows with [risk-based shipping](../verification/risk-based-shipping.md), where low-risk changes auto-ship and high-risk changes trigger gates.

Out of the loop — fully autonomous, with no human oversight. The agent runs on its own, usually in CI/CD or scheduled automation. Best for the low-risk end of the [risk-based shipping](../verification/risk-based-shipping.md) spectrum — deterministic tasks with automated validation (linting, formatting, dependency updates with passing tests). Risky for any task where the error cost is more than the automation value.

### Matching mode to risk

| Supervision mode | Human effort | Latency | Risk tolerance |
|-----------------|-------------|---------|---------------|
| In the loop | High | High (agent waits) | Low — catches errors before they ship |
| On the loop | Medium | Low (agent runs freely) | Medium — catches errors shortly after they ship |
| Out of the loop | None | None | High — errors ship and are caught by monitoring or users |

Most mature agent workflows use a mix: out-of-the-loop for low-risk changes, on-the-loop for medium risk, and in-the-loop for high risk. The [risk-based shipping](../verification/risk-based-shipping.md) pattern formalizes this with a risk matrix that maps change types to supervision modes.

### Progressive trust as mode migration

The progressive trust model described earlier is, in practice, a migration between supervision modes:

- Week 1: in the loop (gate after every stage)
- Month 1: on the loop (agent runs freely, human monitors)
- Month 3 and beyond: out of the loop for proven tasks (auto-merge on CI pass)

Each migration cuts human effort and raises throughput — but only when the workflow has shown it is reliable at the current supervision level.

## When this backfires

Gates are not free insurance — they degrade as workload rises. A reasonable counter-position: placing humans in the loop at all creates a false sense of safety that can be worse than no gate.

- Rubber-stamping under load — when reviewers approve dozens or hundreds of agent actions per day, decision fatigue turns review into a reflex — the review-throughput bottleneck [humans and agents in development loops](humans-agents-development-loops.md) traces in detail. The gate exists in the workflow diagram but not in practice.
- Automation complacency — the more reliable the agent looks, the less vigilant the human becomes. Operators whose job is "mostly approving" lose the ability to catch the rare error they were hired to catch ([source](https://www.defensenews.com/opinion/2026/03/26/the-militarys-fabled-human-in-the-loop-for-ai-is-dangerously-misleading/)).
- Bottleneck batching — gates that need synchronous approval force the agent to queue work. Humans then review in batches, which compresses attention per item and pushes reviewers toward "approve all" heuristics.
- Mismatched cadence — at machine speed, a single human cannot meaningfully supervise an agent that fires tens of actions per minute. The gate becomes either a rubber stamp or a throughput cap — the [bottleneck migration](../human/bottleneck-migration.md) failure mode in a different guise.

Mitigations: rotate reviewers to prevent complacency, include negative-sample injections in review queues to keep attention calibrated, and prefer asynchronous on-the-loop monitoring with alerting over synchronous gates once the workflow's error rate is measured.

## Key Takeaways

- Gate before irreversible actions; skip gates for reversible execution steps
- Reversibility is the most reliable placement signal — map every pipeline step to its undo cost
- Three supervision modes: in the loop (approve each action), on the loop (monitor and intervene), out of the loop (fully autonomous)
- Match supervision mode to risk: high-risk changes get gates, low-risk changes auto-ship with monitoring
- Progressive trust migrates workflows from in-the-loop to on-the-loop to out-of-the-loop as reliability is demonstrated
- Human reviews decisions (is this right?), not execution (did the agent format correctly?)

## Related

- [Risk-Based Shipping: Review by Risk Matrix, Not by Default](../verification/risk-based-shipping.md)
- [Rollback-First Design: Every Agent Action Should Be Reversible](../patterns/agent-design/rollback-first-design.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Idempotent Agent Operations: Safe to Retry](../patterns/agent-design/idempotent-agent-operations.md)
- [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md)
- [Humans and Agents in Software Engineering Loops](humans-agents-development-loops.md)
- [The AI Development Maturity Model: From Skeptic to Agentic](ai-development-maturity-model.md)
- [Agent Governance Policies for AI Agent Development](agent-governance-policies.md)

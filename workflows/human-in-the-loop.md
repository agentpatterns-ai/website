---
title: "Human-in-the-Loop Placement: Where and How to Supervise"
description: "Learn where to place human approval gates in agent pipelines using reversibility as the primary signal, and how supervision modes evolve with trust."
aliases:
  - "Human-in-the-Loop Approval Gates"
  - "HITL placement"
tags:
  - agent-design
  - human-factors
  - tool-agnostic
---

# Human-in-the-Loop Placement: Where and How to Supervise Agent Pipelines

> Gate before irreversible actions and decisions with public impact; skip gates for reversible execution steps — over-gating defeats automation, under-gating ships errors.

!!! info "Also known as"
    Human-in-the-Loop Approval Gates, Human-in-the-Loop. For the specific pattern on implementing confirmation gates as a HITL mechanism, see [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md).

## The Gating Problem

Every human approval gate in an agent pipeline has two costs: latency (the agent waits) and friction (the human interrupts their work). Placed at the wrong points, gates make automation slower than doing the work manually. Placed at no points, the first agent error that reaches production becomes a support incident.

The goal is gate placement that captures actual risk without neutralizing the value of automation.

## Placement Heuristic

Gate before actions where:

1. **The action is irreversible or difficult to reverse** — merging a PR, publishing content, deleting data, deploying to production
2. **The error has public or external impact** — wrong information on a live site, a bad API response reaching customers
3. **The agent is in new or low-confidence territory** — first runs, unfamiliar task types, novel domains

Skip gates for actions where:

1. **The action is easily reversed** — creating a branch, writing a draft, posting a comment, applying a label
2. **CI or another automated check validates the output** — tests pass, linting succeeds, review bot approved
3. **The pattern is proven** — the agent has run this exact task successfully many times

## The Reversibility Frame

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

## Progressive Trust

New agent workflows warrant more gates. As the workflow proves reliable, remove gates from the steps that have never produced errors. This is progressive trust:

- Week 1: gate after every stage
- Week 4: gate only at merge
- Month 3: auto-merge on CI pass + review bot approval

[Claude Code permission modes](https://code.claude.com/docs/en/permissions) support graduated trust: `default` mode asks before each action, `acceptEdits` allows file edits without prompting, and `dontAsk` runs with a pre-configured allowlist of permitted tools and commands — each mode adjusts the level of human oversight.

## What Humans Should Review

The human gate at merge/publish is a decision review, not an execution review. The human should evaluate:

- Is this the right content/change? (decision)
- Does this meet quality standards? (decision)

Not:

- Did the agent write valid markdown? (execution — CI handles this)
- Is the YAML frontmatter syntactically correct? (execution — linting handles this)

Execution review is waste. Decision review is value.

## Working Example

A typical agent-driven [content pipeline](content-pipeline.md) places one human gate: PR review before merge. Research, drafting, initial review, and PR creation all run without human approval — they are reversible (close the PR, update the branch). The human approves the merge, which publishes the content. The gate captures public impact without interrupting the automated stages.

## Supervision Modes: In, On, and Out of the Loop

Gate placement answers *where* the human engages. Supervision mode answers *how*. Three modes exist on a spectrum:

**In the loop** — the agent pauses at gates, the human approves or rejects before the agent proceeds. This is the model described above. The human is an active participant in the pipeline. Best for: high-risk workflows, early-stage trust building, compliance-sensitive contexts.

**On the loop** — the agent runs autonomously, shipping changes without pausing. The human monitors the output stream and intervenes only when something looks wrong. Geoffrey Huntley describes this as "I'm on the loop, not in the loop" — watching agent output from a phone or dashboard and stepping in only when the risk threshold is crossed ([source](https://x.com/GeoffreyHuntley/status/2030683143360119292)). Best for: proven workflows with [risk-based shipping](../verification/risk-based-shipping.md), where low-risk changes auto-ship and high-risk changes trigger gates.

**Out of the loop** — fully autonomous, no human oversight. The agent operates independently, typically in CI/CD or scheduled automation. Best for: deterministic tasks with automated validation (linting, formatting, dependency updates with passing tests). Risky for any task where the error cost exceeds the automation value.

### Matching Mode to Risk

| Supervision mode | Human effort | Latency | Risk tolerance |
|-----------------|-------------|---------|---------------|
| In the loop | High | High (agent waits) | Low — catches errors before they ship |
| On the loop | Medium | Low (agent runs freely) | Medium — catches errors shortly after they ship |
| Out of the loop | None | None | High — errors ship and are caught by monitoring or users |

Most mature agent workflows use a mix: out-of-the-loop for low-risk changes, on-the-loop for medium risk, and in-the-loop for high risk. The [risk-based shipping](../verification/risk-based-shipping.md) pattern formalizes this with a risk matrix that maps change types to supervision modes.

### Progressive Trust as Mode Migration

The progressive trust model described earlier is, in practice, a migration between supervision modes:

- **Week 1**: in the loop (gate after every stage)
- **Month 1**: on the loop (agent runs freely, human monitors)
- **Month 3+**: out of the loop for proven tasks (auto-merge on CI pass)

Each migration reduces human effort and increases throughput — but only when the workflow has demonstrated reliability at the current supervision level.

## Key Takeaways

- Gate before irreversible actions; skip gates for reversible execution steps
- Reversibility is the most reliable placement signal — map every pipeline step to its undo cost
- Three supervision modes: in the loop (approve each action), on the loop (monitor and intervene), out of the loop (fully autonomous)
- Match supervision mode to risk: high-risk changes get gates, low-risk changes auto-ship with monitoring
- Progressive trust migrates workflows from in-the-loop to on-the-loop to out-of-the-loop as reliability is demonstrated
- Human reviews decisions (is this right?), not execution (did the agent format correctly?)

## Related

- [Risk-Based Shipping: Review by Risk Matrix, Not by Default](../verification/risk-based-shipping.md)
- [Rollback-First Design: Every Agent Action Should Be Reversible](../agent-design/rollback-first-design.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Idempotent Agent Operations: Safe to Retry](../agent-design/idempotent-agent-operations.md)
- [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md)
- [The AI Development Maturity Model: From Skeptic to Agentic](ai-development-maturity-model.md)
- [Agent Governance Policies for AI Agent Development](agent-governance-policies.md)
- [Continuous Agent Improvement](continuous-agent-improvement.md)
- [Team Onboarding](team-onboarding.md)

---
title: "Ordering Is the Weakest Process Constraint You Write"
term: "Ordering Constraint Weakness"
description: "Coding agents satisfy the steps of a workflow and drop their required order. Ordering held 46.7% on ANCHOR, the weakest of three relation types."
aliases:
  - THEN constraint failure
  - Workflow order compliance gap
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-14
maturity: emerging
---

# Ordering Is the Weakest Process Constraint You Write

> Ordering constraints held 46.7% of the time against 58.1% for conjunctions and 64.0% for priority. Agents often do the steps out of order.

An ordering constraint says one action must precede another. Reproduce the failure before patching it; run the test suite before you commit. The ANCHOR benchmark scores repository-grounded coding agents on the process constraints a developer attaches to a task. It reports ordering as the hardest of the three ways those constraints compose: "THEN is clearly the hardest relation type, with mean CCR only 46.7%, compared with 58.1% for AND and 64.0% for PRIORITY" ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.5). That figure covers three models under two open-source scaffolds. The component actions usually happen. Their sequence does not survive.

## Where enforcement earns its cost

Ordering constraints are not uniformly fragile, so put the gate where the measurements say the loss is.

- Large constraint sets. Averaged over seven models on the Cline scaffold, the share of tasks passing every scored item fell from 9.4% to 2.7% as a task's constraint graph grew from 8–16 nodes and edges to 29–46. Compliance with the individual requirements inside a composite held between 57.4% and 65.3% across two to five nodes ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.5). The relation-level drop is consistent with difficulty in coordinating requirements, and CCR falls from 54.3% to 44.0% on Cline across 1-4 edges ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.5).
- Orders that exist for the reviewer. A patch that works without a reproduction step still costs you. ANCHOR's authors argue such a patch is "harder to audit, harder to maintain, and harder to trust in future incidents, because reviewers lack evidence about how the failure was diagnosed and how the fix was validated" ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §7.1). A passing test suite cannot see this. A trace can.
- Reporting and workflow requirements. Across the 14 paired configurations, Output Format & Reporting scored 41.0% macro compliance and Workflow & Behavior 50.1%. Modification scope scored 66.6% (518 atomic constraints) ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.3). The authors say conservative behavior often satisfies such local prohibitions; process discipline does not. These category rates and the relation rates above are separate measurements and do not rank against each other, so read reporting at 41.0% as a second weak spot rather than as a correction.

Check the trajectory rather than the diff. A diff shows what changed and never the order the agent reached it in.

## Why it works

A conjunction or a scope prohibition is satisfiable by one conservative choice at the moment it applies. ANCHOR's failure attribution shows where the loss falls. Across 20,726 attributed failures, "E1 *Not Perceived* accounts for 38.2% of failures, E3 *Deprioritized* for 21.9%, and E6 *Partial Compliance* for 14.5%; together they account for 74.6%, while E4 *Capability Limitation* accounts for 5.2%", and ordering failures skew toward the not-perceived and partial-compliance labels ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.7). Those labels are post-hoc and assigned by an LLM, which the authors state plainly, so read them as the failure signature rather than as an identified cause.

## When this backfires

- Small composites. Compliance with the requirements inside a small composite already runs at 57.4% to 65.3% on Cline ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.5), so a gate over one or two constraints may buy little.
- An order you have not validated. Adding early phases can degrade performance, particularly when they clash with a model's own problem-solving strategy ([arXiv:2604.12147v3](https://arxiv.org/abs/2604.12147v3), abstract). Enforcing the wrong sequence can cost fixes.
- Prose dismissed too fast. The same study found that "periodic plan reminders can mitigate plan violations and improve task success" ([arXiv:2604.12147v3](https://arxiv.org/abs/2604.12147v3), abstract), so restating the order mid-run is the cheap first move.
- A rate borrowed from another harness. Compliance belongs to the scaffold and the model together. GPT-5.4-Mini passed 58.5% of all checklist items under OpenCode and 30.8% under Cline, a 27.7-point drop on the same model ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §6.4). A threshold tuned on one harness is mis-sized on the next.
- Managing to an all-or-nothing score. ANCHOR's strict metric zeroes on a missed report line exactly as it does on a broken public API. Its authors call out this limit directly ([arXiv:2610.16859v1](https://arxiv.org/abs/2610.16859v1), §5.2). Gate the two or three orderings that carry real risk.

## Example

Reproduce-before-fix is checkable from the trace. A Claude Code `PreToolUse` hook runs "Before a tool call executes" and "Can block it", and its input carries a `transcript_path`, the "Path to conversation JSON" ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)). Match it on `Edit|Write` and scan that transcript for a test invocation naming the target test. Return `permissionDecision: "deny"` on the first write under `src/` until one appears. The agent can say in prose that it reproduced the failure first. The gate reads whether a failing run exists.

The same reference names the catch: the transcript "is written asynchronously and may lag the in-memory conversation, so it may not yet include the current turn's most recent messages when a hook fires." A reproduction run issued moments earlier can be missing, so the hook's deny message has to tell the agent how to proceed rather than simply refuse. Pair the gate with a commit-time check that the diff carries a regression test. Then both orderings that matter for a bug-fix audit are enforced where they happen.

## Key Takeaways

- Review the trace, not the diff, whenever an instruction says one step must precede another. The diff cannot answer it.
- Pick the two or three orderings whose violation would change how you review the patch, and gate those. Leave the rest in prose with a mid-run reminder.
- Validate the order before you enforce it. An added phase that does not match the model's own strategy can lower performance.
- Treat a compliance figure as a property of your scaffold and model together, so measure it on the harness you run rather than importing a number.
- ANCHOR labels 5.2% of attributed failures as capability limitation. The labels are post-hoc, so they do not show that a stronger model leaves the gap open.

## Related

- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — the companion case: rules that stop work belong outside the agent entirely.
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — compliance loss driven by rule count rather than by rule class.
- [Transcript-Gradable Agent Rules](transcript-gradable-agent-rules.md) — writing rules a trace can score, which is what a trajectory gate needs.
- [Plan Compliance in Agents](../patterns/agent-design/plan-compliance-in-agents.md) — whether an instructed plan runs at all, and what moves that number.
- [Hooks for Enforcement vs Prompts for Guidance](hooks-vs-prompts.md) — the general surface choice this evidence narrows to one constraint class.

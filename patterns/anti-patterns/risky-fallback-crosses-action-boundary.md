---
title: "Risky Fallback Crosses an Action Boundary"
term: "Risky Fallback"
description: "After a tool error, four models took a substitute that crossed an action boundary in 23.5% to 96.8% of risky scenarios. Call-level guards lost normal successes to stop it."
aliases:
  - recovery gone too far
  - fallback across an action boundary
  - evidence-decision gap at fallback
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-19
maturity: emerging
---

# Risky Fallback Crosses an Action Boundary

> A fallback call after a tool error can cross a boundary set by the target's state, which a guard reading only the call cannot see.

In 304 LLM-written scenarios (150 normal, 154 risky), four models took a substitute tool after the designated tool failed. They crossed the action boundary in 23.5% (DeepSeek) to 96.8% (Qwen) of risky scenarios. In 90.4% (Gemma) to 100% (DeepSeek) of violating runs, the target's state was already in context ([Wang et al., 2026](https://arxiv.org/abs/2611.19886v1), §3.2, Table 1).

Limits: the scenarios "may contain defects", the designated tool fails on every attempt, and each scenario ran once at temperature 0 (§3.1, §6.2).

## Why call-level guards fail

The call and error look the same in both scenario types. On Qwen alone (Table 3), AgentSpec rules on the pending call cut violations from 96.8% to 0.0% and normal success from 98.0% to 0.0%. Each of three mitigations lost 0.62 to 0.99 normal successes per prevented violation. Per the body, none "stops risky fallback without also stopping legitimate recoveries" (§1).

## The git case

Before every risky forced push the agents fetched and read another author's two commits, which refreshes the lease that `--force-with-lease` checks. Without the repair they discarded those commits in 11 of 16 runs on Claude Code (Claude Haiku 4.5) and 16 of 16 on Codex (GPT-5.6 Luna). One task family (§5.4, Table 10).

## The repair, and its cost

The paper's nrepair is a learned monitor plus a prompt, not a gate. A hook fires on declared substitute calls, scores the last 8,000 characters of context, and on a trigger withholds the call once with a four-point re-check prompt. A second call executes unchecked (§4.4, §4.5).

- Qwen: violations 96.8% to 77.3%, normal success 98.0% to 97.3%.
- Luna: violations 67.5% to 16.2%, normal success 92.0% to 79.3%. The abstract's 76.0% is this relative reduction (51.3 points). The 12.7-point loss is the largest (Table 4).

The git-case monitor was fitted on the same two scenarios, so that result is in-distribution (§5.4).

## What to do

1. Declare each designated and substitute pair.
2. On the first substitute call in a run, withhold it and return four checks: content others wrote on the target, an entitlement someone else owns, a record something else retains, and a downstream consumer that needs a check.
3. For git, require `--force-if-includes` with the lease. Git's docs call the lease "trivially defeated" by background fetches, and the flag forces an update only if the remote tip "has been integrated locally" ([git-push](https://git-scm.com/docs/git-push)). The paper does not test it.

Without a monitor, the same prompt at every fallback cost 0.30 normal successes per prevented violation on Qwen (Table 7).

## When this backfires

- The agent falls back before reading the target (§6.1).
- A model ignores the prompt. On Qwen, 23.1% of triggered risky runs stopped (Table 7).
- The model changes. Keeping Qwen's threshold on Gemma cut recall from 80.1% to 75.7% (§5.1).

## Key Takeaways

- Put the check at the decision, because the call is identical either way.
- Report a mitigation's cost in lost normal successes, not only violations.
- A hook cannot fire on a substitute you did not declare.

## Related

- [Retry, Switch, or Abstain Recovery Policy](../agent-design/retry-switch-abstain-recovery-policy.md)
- [Expressed Risk Awareness as an Execution Safeguard](expressed-risk-awareness-as-safeguard.md)
- [Deterministic Precondition Gates](../agent-design/deterministic-precondition-gates.md)
- [Enforcing Agent Behavior with Hooks](../../instructions/enforcing-agent-behavior-with-hooks.md)
- [Outcome Monitors and Recovery Affordances](../agent-design/outcome-monitors-recovery-affordances.md)
- [Judging Agent Safety by Task Completion](judging-agent-safety-by-task-completion.md)
- [Classifier-Gated Auto Permission](../agent-design/classifier-gated-auto-permission.md)
- [Hard-Deny Classifier Rule](../../tools/claude/hard-deny-classifier-rule.md)

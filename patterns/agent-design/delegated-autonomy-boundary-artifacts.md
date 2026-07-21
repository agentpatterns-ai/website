---
title: "Delegated-Autonomy Boundary Artifacts (AJR and ADP)"
term: "Delegated-Autonomy Boundary"
description: "Capture an agent's authority boundary as two reviewable artifacts — an Agency Justification Record and an Agentic Delegation Policy — not buried in prompts."
tags:
  - agent-design
  - human-factors
  - tool-agnostic
  - pattern
  - arxiv
aliases:
  - agency justification record
  - agentic delegation policy
last_reviewed: 2026-07-21
maturity: emerging
---

# Delegated-Autonomy Boundary Artifacts (AJR and ADP)

> The delegated-autonomy boundary — what an agent may do, under what authority, with what oversight — belongs in reviewable artifacts, not implicit in prompts.

An agent plans, keeps state, and acts in external systems, so the decision about what it may do on its own is a requirements-level commitment. Today that commitment lives scattered across prompts, tool schemas, and runtime policies, where no one can review, version, or test it. The pattern names it and writes it down as two artifacts: an Agency Justification Record (AJR) for whether to use an agent at all, and an Agentic Delegation Policy (ADP) for the boundary itself ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)).

## When to use it

Reach for these artifacts when the authority you are delegating carries real cost. That means an agent with write access, cross-system reach, irreversible actions, or spend — where a wrong action is expensive and graduated approval matters. The artifacts earn their overhead by making that authority reviewable before it ships.

Skip them for a low-risk, reversible, read-only agent. The source paper walks through a code-review agent and rejects the AJR outright: the task is well-defined, the diffs are structured, access is read-only, and the projected gain does not justify the agentic overhead. A prompted-model pipeline is the recommended answer there ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)). The artifact bounds risk; it is not a compliance form for every agent.

## The two artifacts

The Agency Justification Record decides whether an agent is warranted over a simpler design. It applies minimal justified autonomy: the team justifies the agentic architecture against six criteria — open-ended task structure, unstructured context, cross-system actions, evaluable progress, bounded risk, and a demonstrable advantage over baselines with pre-committed thresholds. The rejection path is a first-class outcome, so a failed AJR records why a simpler design was chosen ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)).

The Agentic Delegation Policy specifies the boundary for an agent that passed its AJR. It has six parts: purpose with explicit stop conditions, authority split into three tiers, information and memory rules, coordination rules, assurance monitors, and an evolution policy for versioning and rollback. The authority tiers are the core. Autonomous actions need no review, advisory actions are proposed but wait for human approval, and prohibited actions are never permitted regardless of instruction ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)). This maps onto existing controls: [deterministic precondition gates](deterministic-precondition-gates.md) enforce the prohibited tier, and [verification-gated autonomy](verification-gated-agent-autonomy.md) screens the advisory tier.

## Why It Works

Requirements that stay implicit are unreviewable and unauditable. No one can inspect, version, or test a commitment that was never written down. Naming the boundary as artifacts surfaces it: the AJR forces a justify-or-reject decision before the agent exists, which blocks unjustified agency, and the ADP makes authority, memory, and stop conditions explicit, which blocks under-specified agency. Both failure modes are the paper's stated targets ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)). This is the standard requirements-engineering mechanism at work: unstated commitments are where defects hide, and making them explicit is what makes them controllable.

## When This Backfires

The artifact describes the agent at one moment, but agent behavior drifts. Extended runs show semantic drift, a progressive deviation from original intent, so an ADP can end up describing an agent that no longer behaves as written ([arxiv:2601.04170](https://arxiv.org/abs/2601.04170)). Treat the policy as a living document tied to a review cadence, not a launch-day sign-off.

A prose policy separate from the enforcement surface is a second source of truth that rots. If the ADP is not connected to the tool schemas, permission hooks, and sandboxes that actually gate behavior, it drifts out of sync the moment a prompt changes. The paper flags this as an open problem, compiling requirements down to runtime, which means the artifact is a starting point, not the enforcement itself ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)).

Ceremony without enforcement is the third failure. A team that fills in the ADP as a checkbox, then never wires it into real tool scopes, produces a document nobody reads and changes no runtime behavior.

## Example

The paper's discharge-coordination agent shows the artifacts applied to a safety-critical case. Its AJR is justified across all six criteria: the task is open-ended and crosses the electronic health record, pharmacy, and payer systems. Its ADP then grades authority by tier. The agent reads the chart autonomously, flags medication discrepancies to a clinician as an advisory action, and is prohibited from signing orders. Memory is episode-scoped with no personal data retained past discharge, and unresolved conflicts escalate to a clinician after a set number of attempts ([arxiv:2607.17225](https://arxiv.org/abs/2607.17225)). The boundary is legible to a reviewer before the agent runs.

## Key Takeaways

- The delegated-autonomy boundary is a requirements-level commitment; write it down instead of leaving it implicit in prompts and tool schemas.
- Use an Agency Justification Record to decide whether an agent is warranted, and treat a rejection as a valid, documented outcome.
- Use an Agentic Delegation Policy to grade authority into autonomous, advisory, and prohibited tiers with explicit stop conditions.
- The artifacts pay off for high-authority, cross-system, or irreversible agents; they are ceremony for low-risk read-only ones.
- A policy that is not connected to real enforcement drifts stale, so tie it to a review cadence and to the controls that gate behavior.

## Related

- [The Delegation Decision](delegation-decision.md) — the when-to-delegate heuristic; the AJR is the artifact that records this decision and its rejection rationale
- [Minimum-Sufficient Control Ladder](minimum-sufficient-control-ladder.md) — escalates control mechanisms by failure mode; complements the ADP's static authority tiers
- [Verification-Gated Agent Autonomy](verification-gated-agent-autonomy.md) — screens the advisory tier with an automated reviewer rather than per-action human approval
- [Deterministic Precondition Gates](deterministic-precondition-gates.md) — enforces the prohibited tier deterministically, outside the model's discretion
- [Approval Response Taxonomy](approval-response-taxonomy.md) — structures the human responses at the advisory-tier approval point

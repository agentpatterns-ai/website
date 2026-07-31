---
title: "Authorization Continuity Across Agent Mutation"
term: "Authorization Continuity"
description: "Decide grant survival and effect bounds separately: a transition envelope suspends a grant when the agent mutates, an immutable ceiling caps authority."
aliases:
  - transition envelope and effect ceiling
  - grant survival across agent mutation
  - immutable effect ceiling for agents
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-07-30
maturity: emerging
---

# Authorization Continuity Across Agent Mutation

> A grant names a subject, not just an effect — when the agent mutates, the authorization can lapse even though the effect is unchanged.

Authorization continuity asks whether a grant still applies after the agent holding it has changed. Two separate controls answer two separate questions. A transition envelope lists the mutation classes a grant may survive and suspends the grant when the agent changes in a way outside that list. An immutable effect ceiling, fixed when the grant is issued, bounds what authority can ever become active, so no evidence the agent produces can widen it ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)).

## When this recommendation applies

The two controls repay their interruption cost only under these conditions ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)):

- Your harness observes every mutation. Unobserved mutation breaks the model's soundness condition, so an agent that swaps its model, skills, or memory through an uninstrumented channel keeps a grant that still reads as live.
- Evidence that widens authority comes from outside the agent. If the agent can realize that evidence itself, no bound below the ceiling can be certified.
- Mutation is infrequent relative to the work. Every out-of-envelope change suspends the grant before the next protected action, and re-granting it lands on the human.
- The enforcement layer sits outside the agent's reach. Approval policy, sandbox, verifier, and logging changes are themselves a mutation class that has to fail closed.

Outside these conditions the simpler postures dominate: keep the grant narrow from the start with [task scope as a security boundary](task-scope-security-boundary.md), or bound the window instead of the subject with [revocable resource-and-effect capabilities](revocable-resource-effect-capabilities.md). See [when this backfires](#when-this-backfires).

## Two controls, two questions

| Control | Question it answers | What it does |
|---|---|---|
| Transition envelope | Is this still the agent you authorized? | Suspends the grant before the next protected action when an observed mutation falls outside the listed classes |
| Effect ceiling | How much effect may ever be active? | Clamps every proposed authority to the bound fixed at grant time |

The two run independently. The monitor suspends an out-of-envelope grant even when the proposed effect set still sits inside the ceiling ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)). Beneath the ceiling, movement is asymmetric: contraction is admitted unconditionally, and every other proposal counts as ascent and needs qualifying evidence. Evidence picks which part of an already consented boundary is active. It never enlarges the boundary.

## The six mutation classes

The paper sorts authorization-relevant changes into six classes, each with its own response ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)):

| Class | Example change | Response |
|---|---|---|
| Control state | Model or provider switch, instruction, skill, or memory update | Re-measure the subject; continue only within the approved transition class |
| Capability | New tools, network access, wider filesystem roots, new credentials | Recompute active authority; contract, or request a scoped grant |
| Delegation | New subagents, changed child models, recursive delegation | Attenuate child authority and bind it to the delegated subtask |
| Task or phase | Inspect to edit, test to commit, local to deploy | Use phase-bound authority with explicit transition gates |
| Trust context | Repository or tool output becoming persistent control input | Track provenance and restrict persistence |
| Enforcement | Approval policy, sandbox, verifier, or logging changes | Fail closed and require an external update path |

## Why it works

The ceiling preserves a property capability systems have held since the 1960s: authority cannot be amplified by the principal exercising it. Transitive attenuation states it formally for a delegation chain, where each child's capability set is a subset of its parent's, and static capability confinement bounds a component to the transitive closure of its declared set — both under a sandbox assumption, both traced to Dennis and Van Horn (1966) and Miller (2006) ([Bhardwaj, 2026](https://arxiv.org/abs/2603.00195)).

An evidence-driven autonomy dial breaks that property quietly. Admit a signal the agent can produce as input to the authority-raising relation, and the agent — or whoever injected it — controls its own bound. The separation obligation restores non-amplification by requiring that no admissible signal can raise the ceiling. Ascent then needs an external premise the agent cannot manufacture: an independent audit, an authorized countersignature, or an evaluation it cannot run on itself ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)).

## When this backfires

- Uninstrumented harnesses get nothing. The guarantee holds only while the monitor sees every mutation ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)).
- Self-realizable evidence collapses the earned-authority layer. When the evidence qualifying an ascent is achievable by the agent under its current authority, no bound below the ceiling can be certified, so passing your own test suite buys nothing ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)).
- High-mutation interactive work pays in interruption. Enterprise customers on conservative fixed permissions saw roughly 40% of agent actions blocked; the vendor response was to loosen the gate to a classifier that blocks about 4% of actions and interrupts about 7% of chats ([Cursor](https://cursor.com/blog/agent-autonomy-auto-review)).
- Ceiling selection is unsolved. The authors concede both directions fail — a high ceiling weakens the result, a low one interrupts useful work — and offer no method for choosing ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)).
- Fleets have no revocation story. Cross-generation revocation and population-level authority are left unsolved, so agents respawned from a shared configuration fall outside the model ([Zhang and Zhang, 2026](https://arxiv.org/abs/2607.23586)).
- The opposite case has serious backing. A systematization of trust-authorization mismatch names the gap between dynamic trust and static authorization boundaries as the shared root cause of prompt injection and tool poisoning, and argues for risk-adaptive authorization instead of fixed bounds ([SoK, 2025](https://arxiv.org/abs/2512.06914)). Nothing here is tested against that position: the model carries no empirical evaluation of drift frequency or cost.

## Example

The delegation mutation class is a live default, not a hypothetical. A Claude Code subagent that omits `tools` inherits every tool available to subagents, and `model` defaults to `inherit` ([Claude Code subagents](https://code.claude.com/docs/en/sub-agents)). Delegation therefore carries both the parent's capability and its subject forward unchanged.

**Before** — delegation that attenuates nothing:

```markdown
---
name: pr-fixer
description: Fix review comments on an open PR
---
```

**After** — delegation bound to the subtask:

```markdown
---
name: pr-fixer
description: Fix review comments on an open PR
tools: [Read, Edit, Grep, Glob]
model: sonnet
---
```

The second form pins the child below the parent, so the delegation stops widening what the original grant covered.

## Key Takeaways

- Grant survival and effect bounds are separate controls; an envelope suspension can fire while the requested effect still sits inside the ceiling.
- Evidence may allocate authority beneath a ceiling but must never raise it, or the agent controls its own bound.
- Six mutation classes give you a practical checklist: control state, capability, delegation, task or phase, trust context, and enforcement.
- The model is a formalization with no empirical evaluation, and ceiling selection is left open — treat it as a design lens, not a specification to implement whole.

## Related

- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — authority laundered through value composition, rather than through a change of subject
- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](revocable-resource-effect-capabilities.md) — authority outliving the subgoal that justified it
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the issuer being the wrong principal in the first place
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md) — screening output instead of re-approving each action
- [Progressive Autonomy: Scaling Trust with Model Evolution](../human/progressive-autonomy-model-evolution.md) — turning the autonomy dial up as evidence accumulates

---
title: "Capability Declarations for Agents That Act on Data"
term: "Capability Declaration"
description: "Declare permissions, an owner, live-state preconditions, and a reversibility class for each action an agent may take. Retrieved text informs; it never authorizes."
tags:
  - agent-design
  - context-engineering
  - tool-agnostic
aliases:
  - capability model
  - declared preconditions for agent actions
  - informing versus gating boundary
last_reviewed: 2026-08-28
maturity: emerging
---

# Capability Declarations for Agents That Act on Data

> Declare every capability an agent may invoke: who may call it, what must hold when it acts, and how badly it can go wrong.

A capability declaration records one action an agent may perform, written in version control before the agent runs. Pramod Sadalage and Prem Chandrasekaran place it as the third body of definition in a context layer, next to a domain model of entities and a semantic model of metrics: the capability model "says what the agent may do". Every capability carries permissions and an owner; the ones that act carry preconditions and a reversibility class too ([Sadalage & Chandrasekaran, Thoughtworks](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)).

## When it pays

Two things have to be true together. The agent can take an action you cannot cheaply undo, and the fact deciding whether that action is allowed does not appear in anything the agent reads. Without the first, you are buying a guarantee against a risk you do not carry. Without the second, the model can already see enough to judge for itself.

The second condition is measurable. Jie Wu and Ming Gong call the failure mode policy-invisible violations, "cases in which compliance depends on entity attributes, contextual state, or session history absent from the agent's visible context". Their PhantomPolicy benchmark returns clean business data with no policy metadata attached, and across 60 risky cases each of five frontier models took the violating action 54 to 59 times ([arXiv:2604.12177v1](https://arxiv.org/abs/2604.12177v1)).

## What a capability declares

| Field | What it fixes |
|---|---|
| Permissions | Who may invoke this action, and acting as whom |
| Owner | The person accountable when it misbehaves |
| Preconditions | What must hold, checked "against live state at the moment of acting rather than against whatever the agent read earlier in its plan" |
| Reversibility class | Cleanly reversible, reversible at a cost through a compensating transaction, or irreversible |

Reversibility is the field worth arguing about. Sadalage and Chandrasekaran hold that it predicts safe autonomy better than the money involved: "A $50,000 internal ledger correction you can back out is a safer thing to automate than a $200 payment to an external account you cannot claw back." Key guardrails to the class rather than the transaction size, and route irreversible actions to a human whatever autonomy the agent has earned ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)).

## Retrieved text informs, declared rules gate

Most preconditions already exist as prose somewhere, in a refund policy or a compliance manual. The shortcut is to let the agent read that document at action time and decide for itself, and that shortcut is what the pattern forbids. Rules get extracted ahead of time, curated by a human, and stored as declared preconditions, each carrying a link back to the passage it came from. The agent may still read a complaint ticket or a contract clause to work out what to propose. Only the declared rules decide what is permitted ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)).

That boundary is a security property too. Keeping retrieved text out of the authorization path means a poisoned document cannot grant a permission the agent did not already hold. The prompt-injection literature reaches the same rule from the other direction: "once an LLM agent has ingested untrusted input, it must be constrained so that it is *impossible* for that input to trigger any consequential actions" ([Beurer-Kellner et al., arXiv:2506.08837v3](https://arxiv.org/abs/2506.08837v3)). It is not a full defense, and the limit is the article's own: injected text still shapes what the agent proposes, and a human approver shown fabricated evidence may wave it through ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)).

## Why it works

A check the model's own reading can influence is not a check. Wu and Gong moved the decision into a layer that materializes the post-action world state and verifies structural invariants before allowing, blocking, or asking. It scored 93.0% against human-reviewed trace labels where a content-only baseline scored 68.8%, and the paper states the split plainly: "The model should be responsible for task completion; a policy-aware enforcement layer, with access to organizational world state, should be responsible for compliance" ([arXiv:2604.12177v1](https://arxiv.org/abs/2604.12177v1)). The declaration is what gives that layer something to check. Without it, enforcement sees the same context the model had and inherits the same blindness.

## When this backfires

- Every action in reach reverses cleanly. The reversibility class is what keys the guardrail, so when every action falls into one class there is nothing left for it to decide.
- Rules change faster than anyone clears the review queue. The authors name the limit themselves: "Detecting that a document changed is easy; knowing that the change invalidated a precondition derived from it is a judgement, not a diff" ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)).
- Pruning the read surface along with the write surface. Sadalage and Chandrasekaran hold that five to ten well-described capabilities beat 50 thin API wrappers "almost every time" ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)), which is sound where the capability acts. On MCPVerse, which wires 550 real executable tools into an action space over 140k tokens, most models degrade on larger tool sets but Claude-4-Sonnet improved with the expanded space ([Lei et al., arXiv:2508.16260v2](https://arxiv.org/abs/2508.16260v2)). Measure before you prune what the agent may read.
- Nobody owns the declarations. Sadalage and Chandrasekaran put the decay bluntly: "An access scope with no owner quietly widens until it's a standing service account again" ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)).
- Treating a declaration as ground truth. Natural-language authorization constraints "inevitably contain ambiguities and logical or semantic gaps that cause the agent's behavior to systematically diverge from the true requirements", and refining them against pre-deployment feedback closed up to 82% of the gap toward a human oracle ([Choi et al., arXiv:2604.15505v1](https://arxiv.org/abs/2604.15505v1)).
- The declared set is thin next to the real case mix. Where nothing covers the situation the agent escalates rather than improvising, because "an undeclared case degrades the agent to supervised, not to autonomous" ([Sadalage & Chandrasekaran](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)). A narrow capability model therefore yields an agent that escalates most of the time.

## Key Takeaways

- Declare permissions, an owner, live-state preconditions, and a reversibility class per action. The first two apply to every capability; the last two only to the ones that act.
- Reach for this when actions are hard to undo and the deciding facts sit outside the agent's context. Five frontier models violated policy in 54 to 59 of 60 cases when those facts were hidden ([arXiv:2604.12177v1](https://arxiv.org/abs/2604.12177v1)).
- Extract the rule from the policy document once, under human curation, and check it against live state. Reading the document at action time puts a poisoned page on the authorization path.
- Key autonomy to reversibility, not transaction size, and route irreversible actions to a human regardless of track record.
- Give every declaration an owner and a revision cadence. The artifact drifts from the source it was derived from, and no diff will tell you when it stopped being true.

## Related

- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — the runtime predicate that evaluates a rule; this page covers where that rule is written down and curated.
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md) — what the agent does when a declared precondition is unmet or unconfirmable.
- [Delegated-Autonomy Boundary Artifacts (AJR and ADP)](delegated-autonomy-boundary-artifacts.md) — the whole-agent authority boundary reviewed before shipping, one level above a per-action declaration.
- [Agent-Ready Data Architecture for Analytics Agents](agent-ready-data-architecture.md) — the warehouse facts the read path needs, beneath the acting path this page governs.
- [Governed Sources of Truth for Analytics Agents (Structure Over Access)](governed-sources-of-truth-analytics-agents.md) — the read-side counterpart, routing questions through governed metrics instead of raw tables.

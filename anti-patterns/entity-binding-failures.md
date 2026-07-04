---
title: "Entity Binding Failures in Tool-Augmented Agents"
term: "Entity Binding Failure"
description: "Agents pick the right tool but act on the wrong entity — the wrong Alex, thread, doc, or account. Wrong-tool error hits 0% while wrong-entity actions run 24-26%."
tags:
  - agent-design
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - wrong-entity action
  - entity resolution failure in agents
last_reviewed: 2026-07-03
maturity: emerging
status: current
---

# Entity Binding Failures in Tool-Augmented Agents

> An agent picks the right tool but binds it to the wrong real-world entity — the wrong Alex, the wrong thread, the wrong customer account.

## The anti-pattern

You evaluate an agent on whether it selects the correct tool and produces valid arguments, and you treat a green tool-selection score as proof the action was correct. It is not. "Email Alex about the launch" can select `send_email` flawlessly and still reach the wrong Alex, attach the wrong launch doc, or land in the wrong thread. Tool correctness and entity correctness are separate axes, and only one of them is on your dashboard.

The gap is measured. Across 60 diagnostic tasks, 5 model backends, and 6 tool-use methods (1,800 runs over email, calendar, documents, customer records, and issue tracking), action-oriented baselines hit 0.0% wrong-tool error yet still produced wrong-entity actions in 24.0-26.0% of runs ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)). The failure concentrates where references are ambiguous: temporal calendar tasks ("tomorrow's sync") run 90-100% wrong-entity for baselines, and true-ambiguity tasks reach 92-100% unsafe execution. Unambiguous tasks sit at 0% ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)).

Adding a retriever does not close it. Surfacing candidate entities to the model still leaves it guessing — a semantic filter scores 24.0% and entity retrieval 26.0%, statistically level with the naive baseline ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)).

## Why it works

Three causes drive wrong-entity actions ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)). Retrieval insufficiency: listing candidates does not force the agent to verify which one binds, so it commits to the top match whether or not that match is unique. Temporal-context dependency: references lean on implicit time reasoning — latest version, nearest meeting — that agents infer poorly. Underspecified references: instructions assume background ("the launch doc") that metadata cannot recover. The insight is that organizing the decision space — better tools, better search — adds no binding-verification step. Safe action needs an explicit resolve-then-confirm precondition, not a better retriever.

The mitigations that work make binding a gate. Entity-resolution preconditions declare which entity types a tool needs before it can fire. Confidence-gated binding requires the top candidate to clear an absolute threshold and beat the runner-up by a margin, so near-ties defer instead of guessing. Clarification under ambiguity asks a targeted question with distinguishing metadata, and provenance tracking records the evidence behind each binding for audit. Together these drove wrong-entity actions to 0.0% ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)).

## Example

Before — right tool, unverified entity:

```python
# "email Alex about the launch"
alex = directory.search("Alex")[0]        # first match wins
send_email(to=alex.address, subject="Launch", body=...)
```

Two people named Alex resolve to one silent pick. Tool selection is correct; the recipient is a coin flip.

After — resolve then confirm before acting:

```python
candidates = directory.search("Alex")
if len(candidates) > 1 and not clear_margin(candidates):
    return clarify(
        "Which Alex? "
        + "; ".join(f"{c.name} <{c.address}>, {c.team}" for c in candidates)
    )
send_email(to=candidates[0].address, subject="Launch", body=...)
```

The gate fires only when the binding is ambiguous, and it presents distinguishing metadata rather than a generic question.

## When this backfires

Making every binding a gate is not free. The same methods that drove wrong-entity actions to zero cut direct task success from ~74-75% to 26-32% through conservative deferral ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)). Gate selectively:

- Reversible or draft-only actions (draft an email, open a doc) where a wrong entity is caught and undone cheaply — a final human confirm beats a per-binding gate and keeps completion high.
- Small, deduplicated, single-tenant entity spaces with no name collisions — unambiguous tasks already sit at 0% wrong-entity, so the gate never fires but still adds latency.
- Interactive workflows where a human already confirms every high-risk send — the clarification step lives outside the agent.

Reserve confidence-gated binding for high-risk, irreversible actions on ambiguous entity spaces; elsewhere the completion cost outweighs the safety gain.

## Key Takeaways

- Tool correctness and entity correctness are separate axes. A 0% wrong-tool score coexists with 24-26% wrong-entity actions ([Suresh Babu & Indukuri, 2026](https://arxiv.org/abs/2606.30531)).
- Retrieval does not fix binding. Surfacing candidates leaves the agent guessing; the fix is an explicit resolve-then-confirm precondition, not a better search.
- The failure concentrates on ambiguous references — temporal ("tomorrow's sync") and name collisions — and vanishes on unambiguous ones.
- Binding gates carry a completion cost (task success ~74% → 26-32%); reserve them for high-risk, irreversible actions.

## Related

- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md) — adjacent failure on the same tool call: adopting the tool's output wholesale rather than binding to the wrong entity.
- [Trusting Model-Level Privilege Restraint at Tool Selection](over-privileged-tool-selection.md) — another right-tool-family failure: correct capability, wrong privilege level.
- [Trusting Tool Error Messages as Implicit Authority](tool-error-implicit-authority.md) — a sibling wrong-trust failure, on the error stream rather than the entity binding.
- [Assumption Propagation](assumption-propagation.md) — an unverified early binding cascades downstream, the same way a wrong entity attaches to later actions.
- [The Agent Pushback Protocol](../agent-design/agent-pushback-protocol.md) — the constructive counterpart: the agent surfaces ambiguity and asks rather than guessing.

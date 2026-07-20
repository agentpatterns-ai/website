---
title: "Handoff Skill: Structured Context Transfer Between Agent Sessions"
term: "Handoff Skill"
description: "A model-invocable skill that compacts the current session into a temp-file handoff document a fresh agent can pick up — sibling to session recap, distinct from raw-transcript forwarding."
tags:
  - agent-design
  - context-engineering
  - technique
  - claude
  - skills
aliases:
  - handoff skill
  - cross-session handoff skill
  - slash-command handoff
last_reviewed: 2026-06-12
maturity: adopted
---

# Handoff Skill: Structured Context Transfer Between Agent Sessions

> A model-invocable skill that compacts the current session into a temp-file handoff document a fresh agent picks up at an explicit transfer point.

## What the skill does

The handoff skill is user-triggered and model-dispatched. You ask the agent to "hand off this work" and the model invokes the skill. The body directs it to compact the conversation into a temp file (`mktemp -t handoff-XXXXXX.md` in Matt Pocock's reference implementation), name the skills the next session should pre-load, and — critically — not re-state content already captured in PRDs, plans, ADRs, issues, or commits. Those are referenced by path or URL ([SKILL.md, mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md)).

It fires at an explicit transfer point with a no-duplication rule that prevents the most common failure: copying the whole transcript.

## Two invocation patterns

Matt Pocock's [AI Hero changelog (May 11 2026)](https://www.aihero.dev/skills/skills-changelog-handoff-prototype-review-and-writing) names two patterns:

- Fire-and-forget: mid-session at ~60k tokens you need a tangent, such as fixing a bug or prototyping an alternative. Hand off to a fresh agent rather than burning the remaining context budget. The original session continues unaware.
- DIY sub-agent: hand off during planning, work in the fresh session, then hand back to the original with what you learned — a manual stand-in for [sub-agent fan-out](../multi-agent/sub-agents-fan-out.md). The handoff doc is the contract in both directions.

Both substitute for a sub-agent primitive the harness does not surface.

## Distinction from recap and from pipeline handoff

Three patterns produce structured cross-boundary artifacts. They differ in who triggers them.

| Pattern | Who triggers | Boundary | Receiver |
|---------|--------------|----------|----------|
| Handoff skill | User → model invocation | Explicit, mid-work transfer | Fresh agent session you'll start next |
| [Session Recap](session-recap.md) | Harness (compaction / resume / fork) | Detected discontinuity | Same session's next turn, or returning human |
| [Pipeline Handoff Protocol](../multi-agent/agent-handoff-protocols.md) | Pipeline contract | Pre-defined stage edge | The next agent in a fixed pipeline |

The handoff skill fires when you decide to transfer. The model dispatches it from the skill description, not a hook or a graph edge.

## What the handoff document carries

The doc captures only the parts that exist solely in the conversation:

- Session intent — why this work was started
- Decisions made in-conversation — choices not yet written to a PRD or ADR, with reasoning
- Open questions — what is genuinely unresolved; the next session should not re-litigate them
- Next action — single directive for the receiving agent
- References — paths and URLs to durable artifacts; the receiver reads those directly

[LangChain's analysis of DeepAgents context management](https://blog.langchain.com/context-management-for-deepagents/) reports that adding `session_intent` and `next_steps` as dedicated fields improved their targeted compression evals — the same fields this skill prescribes.

## Why it works

The mechanism is decision-density preservation across a transfer boundary. A long session encodes single-instance constraints (the unique requirement from turn 12, the rejected alternative from turn 40) in prose that gets paraphrased away under compression. Anthropic's [effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) frames the problem: each new session "begins with no memory of what came before," so structured artifacts at boundaries let the next agent "quickly understand the state of work when starting with a fresh context window." A handoff doc written before the transfer captures those fragments verbatim.

## When this backfires

The pattern assumes the skill triggers when expected and adds information the receiver cannot get cheaper from durable artifacts.

- Trigger reliability is probabilistic. At startup the agent sees only each installed skill's `name` and `description`, not the body. A vague description, keyword collisions, or mismatched phrasing leaves the skill idle while you continue without it ([Skill authoring best practices — Claude docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- A continuous progress file already owns the state. If you maintain a `todo.md` updated every step or run [goal recitation](../../context-engineering/goal-recitation.md), the handoff doc duplicates it — two seeds that may disagree.
- The author predicts the wrong salience. The compacting agent decides what is disposable; when the receiver needs a detail classified as noise, the doc locks the omission in — the failure mode [session recap](session-recap.md) documents.
- Task shape mutates at the boundary. A `session_intent / decisions / next_action` schema fits steady-state work and traps the agent in the old frame when scope widens or pivots. [Tessl's analysis of Amp retiring compaction](https://tessl.io/blog/amp-retires-compaction-for-a-cleaner-handoff-in-the-coding-agent-context-race/) argues for letting the user respecify the new goal rather than relying on static schema-based compression.
- The doc grows into a transcript. Without enforcement of the no-duplication rule, the skill drifts toward copying the full conversation — exactly the [raw-transcript forwarding](../multi-agent/agent-handoff-protocols.md) anti-pattern it was meant to prevent.

## Example

The reference SKILL.md from [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md) is the entire skill body:

```markdown
---
name: handoff
description: Compact the current conversation into a handoff document for
  another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh
agent can continue the work. Save it to a path produced by
`mktemp -t handoff-XXXXXX.md` (read the file before you write to it).

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans,
ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next
session will focus on and tailor the doc accordingly.
```

Three load-bearing constraints: a temp-file path so artifacts don't collide across handoffs, a skills suggestion so the receiver pre-loads the right scaffolding, and the non-duplication rule that keeps the doc small.

## Key Takeaways

- The handoff skill is user-invoked at an explicit boundary; recap is harness-invoked at a detected boundary; pipeline handoff is contract-driven between fixed stages
- The non-duplication rule is the load-bearing constraint — the doc carries only what exists in the conversation alone, not copies of PRDs, ADRs, or diffs
- Two invocation patterns: fire-and-forget (fresh agent finishes a tangent) and DIY sub-agent (hand off, work, hand back)
- Trigger reliability is probabilistic — verify the skill fired before assuming the transfer happened, and skip it when a continuous progress file already owns the state

## Related

- [Session Recap: Goal-Shaped Handoff at Context Boundaries](session-recap.md) — Harness-invoked sibling for compaction, resume, and fork boundaries
- [Cross-Cycle Consensus Relay](cross-cycle-consensus-relay.md) — Cross-session relay document for long-running autonomous loops
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md) — The pipeline-level contract this skill instantiates for the single-receiver case
- [Daily-Use Skill Library](../../workflows/daily-use-skill-library.md) — The skill-library catalogue this entry slots into
- [Discrete Phase Separation](discrete-phase-separation.md) — Phase boundaries the skill formalises into an artifact
- [Session Initialization Ritual](session-initialization-ritual.md) — What the receiving session runs after reading the handoff doc

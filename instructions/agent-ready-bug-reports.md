---
title: "Agent-Ready Bug Reports for Software Repair Agents"
term: "Agent-Ready Bug Reports"
description: "Rank bug report fields by their measured effect on an AI repair agent's correct-fix rate: localization and suggested fixes beat human-style reproduction steps."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - agent-ready bug report
  - bug reports for repair agents
last_reviewed: 2026-07-13
maturity: emerging
---

# Agent-Ready Bug Reports for Software Repair Agents

> For an AI repair agent, a bug report is the task specification — the fields that steer the fix matter more than those humans need.

When an AI repair agent picks up an issue, the report stops being documentation for a maintainer and becomes the agent's task specification. Two independent studies of SWE-bench Verified — a set of 500 real GitHub issues with gold patches — measured which report contents raise an agent's correct-fix rate. The result is consistent: information that points at a repair direction helps most, and information that only helps a human read the report does little.

## What raises the correct-fix rate

Rank report content by its measured effect on whether the agent's patch passes, not by what a human triager would value. Across 433 SWE-bench Verified issues and 87 repair agents, the fields with the strongest positive association were ([What Makes a Good Bug Report for an AI Agent?](https://arxiv.org/abs/2607.07593)):

| Report content | Odds of a resolved issue |
|----------------|--------------------------|
| Suggested fix (code or prose) | 3.61× |
| Repository source code | 2.82× |
| Executable reproduction script | 2.52× |
| File localization (names the files to change) | 2.33× |
| Written reproduction steps | no significant effect |

The companion sentence-level study reaches the same conclusion: sentences that expose a repair direction, through bug localization or a suggested fix, carry the strongest association with a passing patch, while procedural reproduction prose — the field human maintainers rank first — adds little ([Writing Bug Reports for Software Repair Agents](https://arxiv.org/abs/2607.09553)).

So write the report to narrow the agent's search. Name the file or function you suspect. Paste the relevant code. Propose a fix, even a rough one. Give an executable script rather than a numbered list of manual steps.

## Shorter is better

Length works against the agent. A one-standard-deviation rise in report length was associated with 51% lower odds of resolution ([What Makes a Good Bug Report for an AI Agent?](https://arxiv.org/abs/2607.07593)). Padding a report with every possible detail buries the high-signal cues. Cut background that does not point at the fix.

## Why it works

A repair agent resolves an issue in two phases: it searches the repository to localize the fault, then edits. Localization cues and suggested fixes act on the first phase — they shrink the search and repair space, so the agent reaches the right code in fewer steps and has fewer branch points where it can go wrong ([Writing Bug Reports for Software Repair Agents](https://arxiv.org/abs/2607.09553)). This is the same high-signal-over-noise principle behind [pointing an agent at an existing specification](specification-as-prompt.md): a precise pointer beats prose the agent has to interpret. Written reproduction steps fail the agent for a related reason — it has to translate prose into an executable check, an error-prone step, whereas a reproduction script skips the translation and runs directly.

## When this backfires

The narrowing that helps a correct cue hurts when the cue is wrong:

- Wrong localization or a wrong suggested fix anchors the agent to the wrong region and wastes its search budget on a false lead. A confident but incorrect pointer is worse than none.
- Reporter-expertise asymmetry: localization and suggested fixes need the reporter to already know roughly where the fix lives. A triage bot or a non-maintainer often cannot supply the most valuable fields, and a guess risks the anchoring failure above. When you cannot localize, an [interactive clarification step](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) or a [reproduce-before-report gate](../code-review/reproduce-before-report-verification-gate.md) beats a fabricated pointer.
- Evidence scope: both studies use SWE-bench Verified — curated Python library bugs with gold patches. The field rankings may not transfer to other languages, UI or configuration bugs, or proprietary codebases.
- Over-reporting: adding fields to be safe raises length, and length lowers resolution odds. More content is not strictly better.

## Example

Two reports for the same behavior. The second is an illustrative rewrite that leads with the repair direction.

A human-optimized report reads well but steers the agent poorly:

```markdown
Sorting a queryset by a related model's property throws an error.

Steps to reproduce:
1. Create two models with a foreign key relationship.
2. Add a Python property on the related model.
3. Call .order_by() on that property name.
4. Observe the exception.
```

The agent-ready rewrite of the same behavior points at the repair:

```markdown
`QuerySet.order_by()` raises FieldError when ordering by a related model's
Python property (a name that is not a database field).

Likely location (reporter's hypothesis): the ordering-name resolution in the
ORM query builder — it does not distinguish a property from a concrete field
before building the SQL ordering.

Suggested fix: validate that each order_by name maps to a concrete field and
raise a clear, specific error before SQL generation.

Reproduction: an executable test is attached, not manual steps.
```

The second report names the suspect area, proposes a fix, and supplies a runnable test — the three field types with the strongest measured effect on a correct patch. It marks the location as a hypothesis, so a wrong guess reads as one, not as fact.

## Key Takeaways

- For an AI repair agent, the bug report is the task specification; rank its contents by effect on the correct-fix rate, not by what a human maintainer values.
- Repair-direction fields help most: suggested fix (3.61×), source code (2.82×), executable reproduction script (2.52×), file localization (2.33×).
- Written reproduction steps — the top human field — show no significant effect; give a script instead.
- Keep it short: a one-standard-deviation rise in length correlates with 51% lower resolution odds.
- A wrong localization or fix anchors the agent to the wrong code; when you cannot localize with confidence, do not guess.

## Related

- [WRAP Framework for Writing Agent-Ready Issue Descriptions](wrap-framework-agent-instructions.md) — a checklist for packaging the task description; this page ranks which report fields to put in it
- [The Specification as Prompt](specification-as-prompt.md) — the high-signal-pointer principle applied to types, schemas, and tests
- [Issue Requirements Preprocessing](../patterns/agent-design/issue-requirements-preprocessing.md) — restructure a raw issue into structured input before the agent generates code
- [Issue-to-PR Delegation Pipeline](../workflows/issue-to-pr-delegation-pipeline.md) — the delegation pipeline whose first phase is issue design
- [Agent-Laundered Bug Reports](../patterns/anti-patterns/agent-laundered-bug-reports.md) — the failure mode when agent-written reports lose the reporter's real signal

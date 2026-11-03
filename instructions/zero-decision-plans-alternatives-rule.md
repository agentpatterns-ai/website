---
title: "Zero-Decision Plans and Rejected Alternatives in Agent-Readable Specs"
term: "Zero-Decision Rule"
description: "A plan fails if its implementer must make a design choice. A feature spec fails if it shows one path and no rejected alternatives."
tags:
  - instructions
  - tool-agnostic
aliases:
  - zero-decision implementation plan
  - Alternatives Rule for feature specs
last_reviewed: 2026-11-03
maturity: emerging
---

# Zero-Decision Plans and Rejected Alternatives in Agent-Readable Specs

> A plan fails if its implementer must make any design choice. A feature spec fails if it shows one path and no rejected alternatives.

The Zero-Decision Rule and the Alternatives Rule are two pass/fail tests for documents that an agent reads without the conversation that produced them. The [Elephant-Goldfish Model](../patterns/multi-agent/elephant-goldfish-design-review.md) (EGM) ships both as rubric files. Both rubrics define a pass by the same reader, "a competent engineer (or fresh AI session) who is unfamiliar with the codebase" ([feature-spec standard](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/feature-spec-standard.md#L8-L11), [implementation-readiness standard](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/implementation-readiness-standard.md#L7-L10)).

## The Zero-Decision Rule for implementation plans

The implementation-readiness standard says a plan "must leave zero design or architectural choices to the implementer". It names four choices that fail the plan: a database schema, an API path, a dependency, and the handling of a new edge case. The list is open, because the standard says "including, but not limited to" ([implementation-readiness standard](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/implementation-readiness-standard.md#L12-L18)). The pass bar is a correct change "on the first attempt, without guessing, asking clarifying questions, or making independent design choices" ([core principle](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/implementation-readiness-standard.md#L5-L10)).

The standard requires every such decision to be "pre-determined and documented in the plan" ([implementation-readiness standard](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/implementation-readiness-standard.md#L12-L18)). EGM's drafting skill asks the owner to choose any decision with more than one defensible answer, from up to three options. The drafting agent decides mechanical choices with one defensible answer, such as file naming ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L63-L71)).

A plan also names its scope. The standard asks for an explicit list of files to create, modify, or delete ([requirements](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/implementation-readiness-standard.md#L25-L30)). The drafting skill asks for every touched file with a rationale that says what changes and why ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L224-L231)).

The codebase reviewer checks the plan against the code. A claim about current behavior that the code does not have is a Blocker, because "every later reader inherits the false statement" ([codebase_details](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/codebase_details.md#L47)). Files the plan proposes to create are not findings. A file list without a `Create`, `Modify`, or `Delete` mark on each path gets one Major finding for the whole list ([codebase_details](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/codebase_details.md#L50)).

## Rejected alternatives in feature specs

The feature-spec standard requires a "mandatory evaluation of alternatives". A spec fails if it "proposes a single path without proving that other viable designs were considered and rejected". Each rejection needs a specific, documented reason ([feature-spec standard](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/feature-spec-standard.md#L13-L18)). The standard gives no reason for the rule. One reading is that a fresh reader cannot tell a weighed choice from a default when the losing options are absent (inference).

EGM's brainstorm stage writes an `Alternatives Weighed` section into `concepts_brief.md`, and its template says the draft step "has no other source for them" ([egm-brainstorm](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-brainstorm/SKILL.md#L199-L202)). The draft step reads that section and states why: "Do not rely on memory: drafting often runs in a new session." If the section is absent, the skill asks the user which alternatives were rejected and why ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L198-L203)).

## How EGM runs both tests

Stage 7 of `egm-review` grades the feature range against the feature-spec standard ([critic review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L348-L358)). Stage 9 grades the detailed plan against the implementation-readiness standard ([implementation readiness test](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L375-L386)). Each reviewer is a fresh subagent with no conversation history ([delegation](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L19-L21)).

The upstream review design names the failure this guards against: "The model assumes the context it holds in memory is obvious from the text" ([review.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L28-L31)). The author's session holds the missing decisions, so it reads a gap as filled (inference).

## Applying the rules

- Store each rejected option with its reason in a file the drafting session reads, as EGM's brief does.
- Give the plan to a [fresh subagent](../patterns/multi-agent/forked-vs-fresh-subagents.md) before a coding agent sees it. Give the subagent only the plan, the rubric, and read access to the code. Ask it to list every choice it would still have to make, and send each one to the owner as options with trade-offs.

## Cost and limits

Both rules add questions for the human and length to the document (inference). EGM's FAQ says excessive documentation "can become a bottleneck" ([FAQ](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/faq.md#L29-L37)). The README sends a small, clear bug fix to the normal coding workflow ([README](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/README.md#L20)).

Asked whether a document complete enough for a zero-context agent is realistic, the FAQ answers "Sometimes, but not always" ([FAQ](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/faq.md#L48-L52)). The fail list is open-ended, so a reviewer judges what counts as a design choice, and two runs can disagree (inference). The loop skill says fresh reviewers "sample differently each round" ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L149-L152)).

Upstream reports no measurement of either rule's effect. The FAQ says "Completing the EGM workflow alone does not demonstrate a productivity improvement" ([FAQ](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/faq.md#L45-L46)).

## Example

The brainstorm template carries the section that feeds the Alternatives Rule ([egm-brainstorm](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-brainstorm/SKILL.md#L199-L202)):

```markdown
## Alternatives Weighed

[Each option rejected during ideation, with the reason. `/egm-draft` copies
these into Alternatives Considered and has no other source for them.]
```

The rejected options travel to the drafting session as a file, and the feature spec's Alternatives Considered section is built from it.

## Key Takeaways

- Grade a plan by the choices a no-history reader would still face, and route each one to the owner.
- Mark planned files `Create`, `Modify`, or `Delete`, so the codebase reviewer raises no Major finding for the file list.
- Write rejected options down in the stage that rejects them. EGM's draft step has no other source for them.
- Skip both rules for a small, clear fix, as the EGM README advises.
- Do not cite EGM as evidence that either rule improves outcomes.

## Related

- [Elephant-Goldfish Design Review](../patterns/multi-agent/elephant-goldfish-design-review.md) — the full workflow these rubrics sit in
- [Forked vs Fresh Subagents](../patterns/multi-agent/forked-vs-fresh-subagents.md) — when a reviewer should start with no parent conversation
- [Critic Agent Pattern: Dual-Model Plan Review](../patterns/agent-design/critic-agent-plan-review.md) — a second model reviews the plan before execution
- [The Plan-First Loop](../workflows/plan-first-loop.md) — co-design a written plan before the agent writes code
- [Discrete Phase Separation](../patterns/agent-design/discrete-phase-separation.md) — only artifacts cross the boundary between phases
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) — ask the human instead of guessing
- [Frozen Spec File](frozen-spec-file.md) — goals and constraints in a file the agent cannot edit

---
title: "Drafter-Side Intent Reconciliation Instead of Self-Grading"
term: "Drafter-side intent reconciliation"
description: "The drafting session checks its draft against the earlier brief and reports changed decisions to the human, while fresh reviewers grade design quality."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - brief-to-draft reconciliation
  - drafter must not grade its own draft
last_reviewed: 2026-11-03
maturity: emerging
---

# Drafter-Side Intent Reconciliation Instead of Self-Grading

> The drafter checks the draft against the brief's intent and reports every contradiction and each qualifying addition; fresh reviewers, who get no brief by default, grade quality.

The session that wrote a draft compares it with the brief it started from and lists every contradiction. It also lists each addition that changes the architecture, an external interface, or a dependency. The human picks which version wins, and fresh reviewers grade quality. The [Elephant-Goldfish Model](elephant-goldfish-design-review.md) (EGM) does this when `egm-draft` finalizes a document ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L251-L269)).

## Why the drafter does not grade its own draft

Until commit `82b0396` (PR #171, 2026-10-28), the finalization step of `egm-draft` included a self-evaluation. It checked the draft against the Zoom Out standard for YAGNI, reuse, and root-problem focus. The commit removed that step. Its message reads "The drafting session must not grade its own draft" ([commit 82b0396](https://github.com/google/elephant-goldfish-model/commit/82b03968e30034c89ba15b37fdc12400b984348c)).

The skill's reason is "The session that wrote the draft agrees with it" ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L251-L253)). The same lines say Stage 5 of `egm-review` runs that check from a fresh context. EGM's architecture doc says a single thread that interviews the developer, designs, and codes "validates its own faulty assumptions instead of detecting errors" ([architecture.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/architecture.md#L25-L28)).

## Why EGM gives reconciliation to the drafter

In EGM's default flow, reviewers do not get the brief. The skill says "No Goldfish can do this check, because no Goldfish reads the brief" ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L254-L255)). A reviewer receives the task, the target, persona and standard paths, and "explicitly supplied Goldfish context" ([Claude integration](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L125-L128)). It also reads every file the design document links ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L73-L76)).

Claude reviewers "can read accessible files" ([Claude integration](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L149-L150)). Their isolation permits brief access (inference). If the draft links the brief, or the human supplies it as context, a fresh reviewer reads it. A fresh reviewer given both files could run the comparison without the drafter's agreement bias (inference). Upstream does not weigh giving the brief to a fresh reviewer. The drafter has already read the code behind each change, which a fresh reviewer must find again (inference).

The drafter re-reads the brief it ingested at Step 1 and sorts each divergence into one of two kinds ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L254-L260)):

| Kind | Definition | When the drafter reports it |
|---|---|---|
| Contradiction | The brief decided a question and the draft decides it differently | Every time |
| Addition | The draft decides a question the brief did not raise | Only when it changes the architecture, an external interface, or a dependency |

Upstream gives no reason for the filter on additions.

## The human resolves each contradiction

The drafter lists contradictions first, one line each, quoting the brief and the draft. It asks the human to decide each one ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L262-L266)). It may not edit the draft to match the brief on its own. The skill says "the draft can be right, because drafting reads code that the brainstorm did not".

While a contradiction is open, the session waits. It applies each decision before it picks the save directory ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L268-L277)).

## Keep the brief's decisions in a file

Commit `82b0396` also added an `Alternatives Weighed` section to the brainstorm brief. Its template says `/egm-draft` "has no other source for them" ([egm-brainstorm](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-brainstorm/SKILL.md#L199-L202)).

`egm-draft` reads rejected options from that section. It says "Do not rely on memory: drafting often runs in a new session" ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L200-L203)). So the check depends on the brief file, which a new drafting session also reads (inference).

## Limits and cost

- The reconciler is the session that agrees with its draft, and upstream does not discuss whether that bias hides divergences. Quoting both sides lets the human check each item (inference).
- The step is skipped when Step 1 finds no predecessor file ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L265-L266)).
- The rule is prompt text. The unit test checks only that each scenario file parses and has the required fields ([test_scenario_coverage.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_scenario_coverage.py#L22-L51)). `TEST.md` lists Step 6 as a manual check ([TEST.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/TEST.md#L11-L14)).
- No source measures whether reconciliation catches more drift than self-grading ([EGM evidence](elephant-goldfish-design-review.md#evidence)).
- The cost is a re-read of the brief at each save, plus a human gate when a contradiction exists (inference).

## Applying the split elsewhere

- Have the producer compare its output with its own inputs, such as a brief or an approved plan. Quote both sides of each divergence.
- Send each contradiction to the human, and do not let the producer resolve it alone.
- Send quality grading to a reviewer with no shared history; see [forked vs fresh subagents](forked-vs-fresh-subagents.md).
- Store decisions and rejected options in a file the next session reads.

## Example

The `egm-draft` scenario `finalize_reconciles_instead_of_self_grading` sends one finalization turn ([test_scenarios.yaml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/test_scenarios.yaml#L124-L137)). Its input says "concepts_brief.md chose PostgreSQL; the draft uses Spanner". A passing reply must match `(?i)contradiction` and must not contain "Save to detected directory". Both assertions match wording, so a pass does not show that the session waited for the human.

## Key Takeaways

- Give the producer only the checks that need its private inputs. Leave quality grading to a reviewer with a fresh context.
- Quote both the brief and the draft for each contradiction, and let the human decide, because the newer artifact can be right.
- Write decisions and rejected alternatives into the brief, because the drafting session may not remember the brainstorm.
- Treat a pattern-match scenario as a wording check. It does not show that the session stopped for the human.

## Related

- [Elephant-Goldfish Design Review](elephant-goldfish-design-review.md) — the full workflow this step belongs to
- [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md) — when a reviewer should inherit the parent conversation
- [Role-Declared Context Mode](role-declared-context-mode.md) — keeping a verifier isolated from the supervisor that dispatches it
- [LLM Self-Review Failure in Code Modernization Tasks](../anti-patterns/self-review-modernization-failure.md) — measured misses when a model checks its own output
- [When a Second Model Helps in LLM Review](../../verification/cross-model-review-independence.md) — same-model fresh-session review against a second model
- [Critic Agent Pattern: Dual-Model Plan Review](../agent-design/critic-agent-plan-review.md) — a separate critic for plans before execution

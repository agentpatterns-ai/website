---
title: "Owner-Decides Architecture Gate: Options Without a Recommendation"
term: "Owner-Decides Architecture Gate"
description: "At a design choice with more than one defensible answer, the agent lists up to three options with failure conditions, never ranks or picks, and re-asks when told to choose."
tags:
  - agent-design
  - human-factors
  - tool-agnostic
aliases:
  - owner decides architecture
  - no-recommendation decision gate
last_reviewed: 2026-11-03
maturity: emerging
---

# Owner-Decides Architecture Gate: Options Without a Recommendation

> At a design choice with more than one defensible answer, the agent lists up to three options with their failure conditions and the human picks.

The agent withholds its own preference at architecture decisions. It lists the options, says how each one fails, and asks the human to choose. It does not rank, default, or pick, and a "just pick one" reply gets the same question back. The [Elephant-Goldfish Model](../multi-agent/elephant-goldfish-design-review.md) (EGM) drafting skill is the worked example. It states the rule as Execution Constraint 13, "Owner Decides Architecture" ([egm-draft SKILL.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L63-L71)).

## The rule

The gate fires on decisions with "more than one defensible answer", such as the data model, component boundaries, storage, or protocols. For each one, the agent presents up to three options with "its mechanism, trade-offs, and the conditions under which it fails". The owner then chooses through a single-select gate ([egm-draft SKILL.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L63-L71)).

| Element | Rule text |
|---|---|
| Option count | "present up to three options" |
| Ban | "Do not rank the options, mark a default, or pick one." |
| Refusal loop | "restate the trade-offs and present the same gate again" |
| Carve-out | "Decide mechanical choices with one defensible answer (e.g., file naming, formatting) yourself." |

Constraint 12 sets the shape of every interactive gate. Each gate holds one question, is the only tool call in the turn, and offers options "without `(Recommended)` prefixes" ([egm-draft SKILL.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L58-L62)). The review skill carries the same ban ([egm-review SKILL.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L65-L69)). The bootstrap skill still offers a "(Recommended) Yes, run drift report on modified contracts" option ([egm-bootstrap SKILL.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-bootstrap/SKILL.md#L404-L409)).

## How it differs from nearby question patterns

Each pattern below makes the agent ask the human. The first three let the agent lean toward an answer, and this gate forbids it.

| Pattern | What the agent offers | What it decides on its own |
|---|---|---|
| [Grill Me](grill-me-technique.md) | A recommended answer for each question | Questions the codebase answers |
| [Interactive Clarification](interactive-clarification-underspecified-tasks.md) | A stated assumption on reversible gaps | Whether to ask, by cost of a wrong guess |
| [Advisory tier of a delegation policy](delegated-autonomy-boundary-artifacts.md) | A proposed action awaiting approval | Actions in the autonomous tier |
| Owner-decides gate | Options and failure conditions, unranked | Mechanical choices with one defensible answer |

## Why the rule exists

Upstream gives the rule and no reason, and the commit that added it describes only the behavior ([commit 6db1435](https://github.com/google/elephant-goldfish-model/commit/6db1435e08b853b9042c06029fd1a5f8bd5839bf)). The docs index states the principle it fits, "AI is a tool, not a decision-maker" ([docs/index.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/index.md#L70-L72)). The FAQ says "You own the outcomes" ([docs/faq.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/faq.md#L7-L9)).

The rule fits that principle (inference). A recommendation lets the human approve without reading the trade-offs (inference). Removing recommendations asks the human to compare options directly (inference). This fits [judgment relocation](../../human/judgment-relocation.md), where comprehension is one of four conditions for a real owner (inference).

## How the rule is tested

Commit 6db1435 added the scenario `owner_delegates_architecture_choice` ([test_scenarios.yaml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/test_scenarios.yaml#L49-L68)). The user asks the agent to "Pick the best option" for rate-limit counter storage, then says "just pick one". Each reply must match a question pattern and must not match a list of picking phrases.

The forbidden list catches `I recommend`, `(Recommended)`, and `my pick`. "I'd suggest Redis" escapes that check ([scenario assertions](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/test_scenarios.yaml#L58-L64)). The assertions do not check the options, their order, or their trade-offs. The unit test checks only the structure of the scenario file ([test_scenario_coverage.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_scenario_coverage.py#L22-L51)). A search of the snapshot found no runner for the assertions. The design notes say the same of a sibling skill: "no in-repo runner executes the assertion" ([drift_report.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/drift_report.md#L119)).

## When this backfires

The role name can leak into the record. This page describes the rule at the pinned snapshot. The leak was reported in [issue #248](https://github.com/google/elephant-goldfish-model/issues/248), which closed on 2026-11-02. The reporter says "Owner" leads models to record "Rejected by maintainer", "falsely claiming maintainer consensus when maintainers have not yet reviewed the proposal". The design template asks for a "Reason for Rejection" per alternative ([design_doc.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/references/design_doc.md#L96-L100)). The same report blames an unguided `Author:` field, not "Owner", for `<repo> maintainers` as author. It proposes "Rejected by author: <technical reason>", and the reporter's fix, [PR #249](https://github.com/google/elephant-goldfish-model/pull/249), merged on 2026-11-02. It renames the rule to "Author Decides Architecture", so the rule name on this page is the pre-fix one.

Drafting gets slower (inference). Each multi-answer decision costs a human turn, and "just pick one" costs another (inference). Upstream publishes no timing data to size it.

The rule names no exit. An owner who cannot judge the trade-offs gets the same gate again (inference).

## Example

The upstream scenario asks where to store per-client request counters: Redis, an in-process map on each API node, or a Postgres table. Rule 13 asks the reply to describe each store and when it fails, then ask which one to use. The test checks less. A bare "Which store do you want?" passes both turns, and "Go with Redis" fails the forbidden pattern ([test_scenarios.yaml](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/test_scenarios.yaml#L55-L68)).

## Key Takeaways

- Draw the gate's line by count of defensible answers, and let the agent decide anything with one answer.
- Require failure conditions per option, because with no recommendation the human compares what each option lists.
- A phrase-list scenario catches only the phrases it lists, and only when something runs it; it cannot show fair framing.
- Record each rejection as the author's, with the technical reason, as #248 proposes, so a role word cannot read as reviewer approval.
- Plan an exit for an owner who cannot judge the trade-offs, because the upstream rule has none.

## Related

- [Elephant-Goldfish Design Review](../multi-agent/elephant-goldfish-design-review.md) — the full workflow this gate sits in
- [Grill Me: Developer-Initiated Plan Interrogation](grill-me-technique.md) — the opposite choice, with a recommended answer per question
- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md) — when to ask, sorted by reversibility
- [Delegated-Autonomy Boundary Artifacts (AJR and ADP)](delegated-autonomy-boundary-artifacts.md) — the advisory tier, where the agent proposes and waits
- [Approval Response Taxonomy](approval-response-taxonomy.md) — the human responses at an approval point
- [Judgment Relocation](../../human/judgment-relocation.md) — which decisions keep a human owner, and what makes the owner real

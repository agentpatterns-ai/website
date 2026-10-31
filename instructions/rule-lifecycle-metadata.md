---
title: "Rule Lifecycle Metadata for Prunable Instruction Surfaces"
term: "Rule Lifecycle Metadata"
description: "Tagging instruction rules with source, applicability, and expiry conditions converts the rule-budget audit from a counting exercise into a pruning exercise — so the instruction surface can actually shrink."
tags:
  - instructions
  - tool-agnostic
aliases:
  - rule lifecycle frontmatter
  - source applicability expiry triple
  - undead rule detection
last_reviewed: 2026-06-13
maturity: adopted
---

# Rule Lifecycle Metadata for Prunable Instruction Surfaces

> Tagging each rule with its source, applicability, and expiry condition turns the rule-budget audit from a counting exercise into a pruning exercise.

The [instruction compliance ceiling](instruction-compliance-ceiling.md) makes pruning non-optional — even frontier models drop to 68% accuracy at high instruction densities ([IFScale, 2025](https://arxiv.org/abs/2507.11538v1)). But the ceiling argument only tells you that you must cut, not what to cut. Without an explicit retirement signal per rule, every audit defaults to "leave it in, just in case." Surfaces grow but never shrink.

The fix is per-rule lifecycle metadata: every rule declares its origin, its scope, and the condition under which removing it is safe.

## The triple

The Walkinglabs harness-engineering curriculum names the three fields explicitly: "Every instruction should have a source ('why was this rule added?'), an applicability condition ('when is this rule needed?'), and an expiry condition ('under what circumstances can this rule be removed?')" ([lecture-04](https://github.com/walkinglabs/learn-harness-engineering/blob/3bc70096725e5e1eaa616178f9a5f107ae8ce15b/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)).

| Field | What to record |
|-------|----------------|
| `source` | The incident, decision, or requirement that led to the rule |
| `applies_to` | The tasks or repository state that require the rule |
| `retire_when` | The evidence required before proposing removal |

The triple is not a writing-style preference. It changes what an audit can do. With `retire_when` present, the auditor can check whether the condition has been met and propose the deletion. Without it, deletion is a judgment call no reviewer wants to make alone.

## The undead-rule failure mode

Walkinglabs frames the bloat mechanism directly: "Outdated instructions rarely get deleted — because the consequences of deletion are uncertain ('maybe something else depends on this rule?'), while adding new instructions feels free" ([lecture-04](https://github.com/walkinglabs/learn-harness-engineering/blob/3bc70096725e5e1eaa616178f9a5f107ae8ce15b/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)). The companion anti-patterns list calls out "encoding obsolete rules that nobody audits" as a named anti-pattern ([anti-patterns.md](https://github.com/walkinglabs/learn-harness-engineering/blob/3bc70096725e5e1eaa616178f9a5f107ae8ce15b/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/code/anti-patterns.md)).

A rule with no expiry condition and no recent invocation evidence is undead — it consumes its share of the [150-rule budget](instruction-compliance-ceiling.md) but no one can defend or delete it. Undead rules accumulate fastest in incident-driven additions: a one-off failure produces a permanent rule that nobody can later prove is still needed.

The lifecycle triple kills the undead-rule failure mode at the write site: a rule without `retire_when` does not pass review.

## How the audit uses it

Use the [Walkinglabs lifecycle fields](https://github.com/walkinglabs/learn-harness-engineering/blob/3bc70096725e5e1eaa616178f9a5f107ae8ce15b/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md) as audit questions. For each rule, record whether its source and applicability still hold. Check its retirement condition against current evidence.

Report the file and rule location with the evidence for keeping or removing it. Treat missing metadata as a review gap. Lack of recent invocation alone does not establish that removal is safe.

## Test the retirement condition

Treat `retire_when` as a testable proposal. Replay the original trigger in isolated copies of the same repository state, with and without the fix. Keep task prompts and commit messages identical. This follows the paired replay design in [Lessons Outlive Their Failures, section 4.3](https://arxiv.org/abs/2610.32578v1).

Record the model version, original trigger, and exact rule or check removed. Confirm that each run reaches the trigger. Separate completed runs from refusals and incomplete attempts before comparing outcomes. A run that never exercises the relevant behavior cannot establish that a rule is obsolete. [Sections 5.3 and 6](https://arxiv.org/abs/2610.32578v1) explain why that distinction matters.

The study replays 5 scenarios in one author's repository, with 3 runs per condition on Claude Sonnet 5.5. Only the superseded-decision scenario both removes a prose rule and reaches its trigger. The em-dash and destructive-reset fixes are a lint check and a guard hook. No destructive-reset run reaches the destructive command. All 6 run-time-estimate runs decline, so that scenario supplies no measurement. Those cases cannot establish that prose rules generally outlive their purpose. [Replay results and discussion](https://arxiv.org/abs/2610.32578v1).

The stale-count replay below shows a check catching errors before commit. Its one-sided Fisher test gives p=0.10, short of statistical significance. Reconstructed triggers and historical model differences further limit attribution. These are exploratory retirement tests, not evidence for removing security controls. [Sections 5.3 and 7](https://arxiv.org/abs/2610.32578v1).

Keep mechanical invariant checks when retiring redundant prose. Use the [behavioral deletion test](behavioral-no-op-test.md) to assess instruction value, and retain [enforced controls](../security/enforced-versus-advisory-controls.md) at the action boundary.

## Record metadata when adding a rule

Record `source`, `applies_to`, and `retire_when` beside the rule when you add it. Use a comment or structured fields that your audit can read. Link the actual incident or decision; do not substitute a plausible history. These fields implement the [Walkinglabs lifecycle questions](https://github.com/walkinglabs/learn-harness-engineering/blob/3bc70096725e5e1eaa616178f9a5f107ae8ce15b/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md).

## When the triple is overhead

Lifecycle metadata is not free — every rule carries three extra fields that themselves consume the [context budget](instruction-compliance-ceiling.md) the audit defends. The break-even point depends on surface size and team shape:

- Solo-author projects — the implicit "why this rule exists" lives in the author's head. Writing it down duplicates context that has only one consumer.
- Universal safety rules — "never commit secrets" needs no source, applicability, or expiry, and is better [enforced by a hook](enforcing-agent-behavior-with-hooks.md) than carried as metadata. The triple earns its keep on project-specific, incident-driven rules where context fades over months.
- Teams without commit discipline — if authors do not backfill metadata when adding rules, the triple becomes inconsistent decoration and the audit cannot trust it. Enforce at [PR review](prompt-governance-via-pr.md) or skip the scheme entirely.

## Example

The stale-count replay tests hardcoded skill counts in the author's repository with Claude Sonnet 5.5. Without the pre-commit lint check, all 3 runs leave those counts stale. [Lessons Outlive Their Failures, section 5.3 and Table 3](https://arxiv.org/abs/2610.32578v1).

With lint Check 12 enabled, 2 runs still write stale counts. The linter blocks their first commit attempt and prints the affected lines and true count on disk. After correcting the counts, the agent commits. One guarded run declines under the deadline focus rule. [Section 5.3](https://arxiv.org/abs/2610.32578v1).

The check catches the error after the edit and before commit. A retirement record must preserve that sequence and distinguish the declined run from a completed repair.

## Key Takeaways

- A retirement condition identifies what to test; it does not establish that removal is safe.
- The triple is `source` (why added), `applies_to` (when active), `retire_when` (deletion condition) — sourced from the [Walkinglabs harness-engineering curriculum](https://github.com/walkinglabs/learn-harness-engineering/blob/3bc70096725e5e1eaa616178f9a5f107ae8ce15b/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md).
- Undead rules — no expiry, no recent invocation — are the named failure mode that lifecycle metadata kills at the write site.
- Record whether each replay reaches its trigger; refusals and incomplete runs do not establish safe retirement.

## Related

- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Critical Instruction Repetition](critical-instruction-repetition.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [Prompt Governance via PR Review](prompt-governance-via-pr.md)
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md)
- [Agent Context File Evolution: Treating ACFs as Configuration Code](agent-context-file-evolution.md) — the file-level maintenance lifecycle that sits above per-rule pruning; the compact loop the metadata triple makes mechanical
- [Weakest Consistent Learning: What Agent Loops Should Persist](../patterns/agent-design/weakest-consistent-learning.md) — how broadly to scope a rule an agent writes for itself, before the lifecycle metadata governs its removal
- [The No-Op Test: Prune Agent Docs by Behavior, Not Length](behavioral-no-op-test.md) — the per-line deletion check that decides which of the flagged rules actually goes
- [The Error-Class Governance Loop for Instruction Libraries](../workflows/instruction-library-governance-loop.md) — the running cycle that consumes this metadata: recurrence classification, the retirement pathway, and a standing cut list
- [Why an Encoded Rule Still Fails After a Passing Eval](encoded-rule-failure-diagnosis.md) — the four defects behind a rule that keeps failing, and why three of them survive any rewrite of the wording

---
title: "Rule Lifecycle Metadata for Prunable Instruction Surfaces"
description: "Tagging instruction rules with source, applicability, and expiry conditions converts the rule-budget audit from a counting exercise into a pruning exercise — so the instruction surface can actually shrink."
tags:
  - instructions
  - tool-agnostic
aliases:
  - rule lifecycle frontmatter
  - source applicability expiry triple
  - undead rule detection
---

# Rule Lifecycle Metadata for Prunable Instruction Surfaces

> Tagging each instruction rule with where it came from, when it applies, and when it can be retired turns the rule-budget audit from a counting exercise into a pruning exercise.

The [instruction compliance ceiling](instruction-compliance-ceiling.md) makes pruning non-optional — even frontier models drop to 68% accuracy at high instruction densities ([IFScale, 2025](https://arxiv.org/abs/2507.11538)). But the ceiling argument only tells you *that* you must cut, not *what* to cut. Without an explicit retirement signal per rule, every audit defaults to "leave it in, just in case." Surfaces grow monotonically; they do not shrink.

The fix is per-rule lifecycle metadata: every rule declares its origin, its scope, and the condition under which removing it is safe.

## The Triple

The Walkinglabs harness-engineering curriculum names the three fields explicitly: "Every instruction should have a source ('why was this rule added?'), an applicability condition ('when is this rule needed?'), and an expiry condition ('under what circumstances can this rule be removed?')" ([lecture-04](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)).

| Field | Question it answers | Concrete example |
|-------|--------------------|------------------|
| `source` | Why was this rule added? | "Incident 2024-11-03: agent committed `.env` to git" |
| `applies_to` | When is this rule active? | "Any task that writes files outside `docs/`" |
| `retire_when` | What signals it is safe to remove? | "Pre-commit hook rejects `.env` paths in commits" |

The triple is not a writing-style preference. It changes what an audit can do: with `retire_when` present, the auditor can mechanically check whether the condition has been met and propose the deletion. Without it, deletion is a judgment call no reviewer wants to make alone.

## The Undead-Rule Failure Mode

Walkinglabs frames the bloat mechanism directly: "Outdated instructions rarely get deleted — because the consequences of deletion are uncertain ('maybe something else depends on this rule?'), while adding new instructions feels free" ([lecture-04](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)). The companion anti-patterns list calls out "encoding obsolete rules that nobody audits" as a named anti-pattern ([anti-patterns.md](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/code/anti-patterns.md)).

A rule with no expiry condition and no recent invocation evidence is undead — it consumes its share of the [150-rule budget](instruction-compliance-ceiling.md) but no one can defend or delete it. Undead rules accumulate fastest in incident-driven additions: a one-off failure produces a permanent rule that nobody can later prove is still needed.

The lifecycle triple kills the undead-rule failure mode at the write site: a rule without `retire_when` does not pass review.

## How the Audit Uses It

The [audit-instruction-rule-budget](../agent-readiness/audit-instruction-rule-budget.md) runbook counts rules, classifies them by safety/correctness/style, and detects duplication. Lifecycle metadata adds three roll-up percentages and one new finding class:

```markdown
| Surface | Rules | with source | with applies_to | with retire_when |
|---------|------:|------------:|----------------:|-----------------:|
| AGENTS.md | 42 | 41 (98%) | 38 (90%) | 14 (33%) |
| CLAUDE.md | 28 |  9 (32%) |  6 (21%) |  2 ( 7%) |
| **Total** | 70 | 50 (71%) | 44 (63%) | 16 (23%) |

## Undead rules (no `retire_when` + no recent invocation evidence)

| Surface | Line | Rule | Last referenced |
|---------|------|------|----------------|
| CLAUDE.md | 84 | "Always run `npm test` after edits" | git log: 0 hits in 180 days |
| CLAUDE.md | 102 | "Prefer Vue 2 SFC syntax" | grep: project migrated to Vue 3 |
```

The audit becomes actionable: each undead row is a one-line pruning candidate the auditor can defend with evidence. Without the metadata, the same audit can only emit "70 rules, ceiling is 150, you have room" — which is exactly the report that lets surfaces grow forever.

## Authoring Template

Attach lifecycle metadata at write-time, not after-the-fact. The cheapest form is an inline comment trailing the rule:

```markdown
- Never commit `.env*` or `.dev.vars*` files.
  <!-- source: incident 2024-11-03 | applies_to: any file-write task | retire_when: pre-commit hook rejects these paths -->
```

For projects with many rules, a structured frontmatter block per rule file works better:

```yaml
---
rule_id: no-env-commits
source: incident 2024-11-03 (agent committed .env to public repo)
applies_to: any task that writes files
retire_when: .pre-commit-config.yaml rejects .env* paths AND audit shows zero false-negatives over 90 days
---

Never commit `.env*` or `.dev.vars*` files.
```

The audit runbook in `bootstrap-skill-template` form can ship this template as a fragment the agent attaches to every new rule it authors. Once the template is the default, the undead-rule rate trends to zero.

## When the Triple Is Overhead

Lifecycle metadata is not free — every rule carries three extra fields that themselves consume the [context budget](instruction-compliance-ceiling.md) the audit defends. The break-even point depends on surface size and team shape:

- **Surfaces under ~50 rules** — the whole file is small enough to re-read in two minutes (the Walkinglabs threshold). A quarterly "delete what no one defends" pass achieves the same pruning outcome without per-rule schema overhead.
- **Solo-author projects** — the implicit "why this rule exists" lives in the author's head. Writing it down duplicates context that has only one consumer.
- **Universal safety rules** — "never commit secrets" needs no source/applicability/expiry. The triple earns its keep on project-specific, incident-driven rules where context fades over months.
- **Teams without commit discipline** — if authors don't backfill metadata when adding rules, the triple becomes inconsistent decoration and the audit can't trust it. Enforce at PR review or skip the scheme entirely.

For medium-to-large instruction surfaces under repeated audit pressure, the per-rule cost is dominated by the gain: the surface can shrink. For small surfaces, plain deletion discipline wins.

## Example

A 600-line `AGENTS.md` had 220 rules, well over the [150-rule ceiling](instruction-compliance-ceiling.md). The first audit pass identified 60 dead rules covered by hooks and 30 duplicates — leaving 130, still pressed against the ceiling. The audit could not propose more cuts because no rule declared a retire-when condition.

The team added the lifecycle triple as an inline comment per rule, backfilled by walking commit history for the originating PR. The second audit pass produced:

```markdown
## Undead rules (no retire_when, last referenced > 180 days)

| Line | Rule | Originating PR |
|------|------|---------------|
|  47  | "Use Vue 2 SFC syntax"           | #142 (project migrated to Vue 3 in #890) |
|  92  | "Reference TICKET-447 in commits" | #203 (ticket closed Q2-2023) |
| 118  | "Avoid the legacy auth module"   | #310 (module deleted in #1102)            |
| ...  | (47 more)                         | ...                                     |
```

After the second pass the surface dropped from 130 to 71 rules — under the ceiling with headroom. The undead column was the entire driver; no other audit dimension produced cuts that large.

## Key Takeaways

- The 150-rule [compliance ceiling](instruction-compliance-ceiling.md) forces pruning; lifecycle metadata makes pruning mechanical instead of judgment-based.
- The triple is `source` (why added), `applies_to` (when active), `retire_when` (deletion condition) — sourced from the [Walkinglabs harness-engineering curriculum](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md).
- Undead rules — no expiry, no recent invocation — are the named failure mode that lifecycle metadata kills at the write site.
- The [audit-instruction-rule-budget](../agent-readiness/audit-instruction-rule-budget.md) audit gains three roll-up percentages and an undead-rules finding when lifecycle metadata is present.
- Skip the scheme on surfaces under ~50 rules — overhead dominates and plain deletion discipline already works.

## Related

- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Audit Instruction Rule Budget](../agent-readiness/audit-instruction-rule-budget.md)
- [Critical Instruction Repetition](critical-instruction-repetition.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [Prompt Governance via PR Review](prompt-governance-via-pr.md)
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md)

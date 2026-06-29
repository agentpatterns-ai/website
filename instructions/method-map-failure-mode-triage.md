---
title: "Method Map: Failure-Mode to Smallest-Artifact Triage"
term: "Method Map"
description: "Maintain an explicit table mapping observed long-running-agent failure modes to the smallest artifact that fixes each one — and add only that artifact, never an enlarged global instruction file."
tags:
  - instructions
  - agent-design
  - tool-agnostic
  - harness-engineering
aliases:
  - failure-mode triage table
  - smallest-artifact discipline
  - harness method map
last_reviewed: 2026-06-02
maturity: established
---

# Method Map: Failure-Mode to Smallest-Artifact Triage

> A Method Map triages each observed failure mode to the smallest artifact that fixes it — add only that artifact, never a bigger instruction file.

A Method Map is a lookup table — one row per recurring failure mode an agent exhibits, mapped to the single primary-fix artifact that binds that failure. When a new failure is observed, add the row's named artifact and nothing else ([walkinglabs/learn-harness-engineering, method-map.md](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/reference/method-map.md)).

## When this earns its place

The Method Map pays off only under three conditions:

- Failures have been observed — applying the table before any failure adds files for problems that do not exist
- Instruction count is nearing the compliance ceiling — below the ~150-rule degradation point ([IFScale, 2025](https://arxiv.org/abs/2507.11538)), an `AGENTS.md` line is cheaper than a separate artifact; above it, every new rule pushes existing rules into omission territory ([Instruction Compliance Ceiling](instruction-compliance-ceiling.md))
- Tasks span multiple sessions — cold-start, handoff, and scope-sprawl failures exist only for work that crosses context windows

Below these thresholds, an `AGENTS.md` rule is the smallest artifact, and the Method Map collapses into the instruction file itself.

## The canonical table

The published Method Map covers six failure modes from long-running coding-agent work ([walkinglabs, method-map.md](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/reference/method-map.md)):

| Triggering observation | Failure mode | Primary fix |
|---|---|---|
| New session spends most of its time rediscovering setup and status | Cold-start confusion | `claude-progress.md` |
| The agent starts several features and finishes none cleanly | Scope sprawl | `feature_list.json` |
| The agent claims done after code edits but before runnable proof | Premature completion | `clean-state-checklist.md` |
| Every session re-learns how to boot the project | Fragile startup | `init.sh` |
| The next session cannot tell what is verified, broken, or next | Weak handoff | `session-handoff.md` |
| Review quality depends on taste or memory | Subjective review | `evaluator-rubric.md` |

Five of these artifacts come directly from Anthropic's effective-harnesses writeup — `feature_list.json` with its `passes` field, `claude-progress.txt`, `init.sh`, and the clean-state criterion ("the kind of code that would be appropriate for merging to a main branch") ([Anthropic, Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

The table is not a checklist. You invoke it when an observation matches a row. The first column — the triggering observation in concrete terms — is what distinguishes the Method Map from a generic list of artifacts.

## The doctrine

Three rules govern how you use the table.

Add the smallest artifact that directly addresses the observed failure. A `feature_list.json` binds scope sprawl; it does not also encode commit conventions or test runners.

Never solve a single failure by enlarging a global instruction file. Appending another rule to `AGENTS.md` pushes existing rules closer to the compliance ceiling, where attention drops them ([IFScale, 2025](https://arxiv.org/abs/2507.11538)). The reflex to add a rule is the failure mode the Method Map is designed to interrupt.

Make every per-failure addition removable once the failure no longer recurs. Every artifact has a removal condition, not just an addition condition.

## Why this works

Each row pairs a failure with an artifact that creates external state the agent cannot rewrite during reasoning. A `feature_list.json` constrains the agent to edit only the `passes` field. An instruction line that says "do not declare done early" has no external referent and competes with every other rule under attention degradation ([Instruction Compliance Ceiling](instruction-compliance-ceiling.md)). Anthropic documents the mechanism directly: "after some features had already been built, a later agent instance would look around, see that progress had been made, and declare the job done" — only an external contract stopped it, not more prose ([Anthropic harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

## When this backfires

The discipline carries its own failure modes:

- Stale artifacts mislead. An out-of-date `feature_list.json` actively misdirects the agent. An artifact without an update discipline is worse than no artifact. The [Evaluating AGENTS.md study](evaluating-agents-md-context-files.md) shows auto-generated context files reduce task success rates
- Premature application. Adding all six rows before any failure has been observed violates the operating principle and creates speculative complexity
- Solo developer overhead. For a project well under the compliance ceiling, file-discovery and maintenance cost more than the compliance gain
- Dogma about "no more rules". For some failures the smallest artifact genuinely is one line in the instruction file

## Example

A project starts noticing that its agent declares features complete after editing code but before running tests. The reflex fix is a new line in `AGENTS.md`: "Always run `make test` before marking a feature complete."

Reflex, the instruction-file-growth path:

```markdown
# AGENTS.md (line 187 of 240)
- Always run `make test` before marking a feature complete
```

This adds rule 188 to a file already near the compliance ceiling. Under IFScale-style benchmarks the rule will be dropped some fraction of the time, exactly when it matters ([IFScale, 2025](https://arxiv.org/abs/2507.11538)).

Method Map, the smallest-artifact path:

The observation matches "premature completion." The project adds a `clean-state-checklist.md` that the agent must verify before declaring done, and removes any corresponding instruction line:

```markdown
# clean-state-checklist.md
- [ ] `make test` exits 0
- [ ] `git status` is clean (no uncommitted changes)
- [ ] No `TODO(agent)` or `FIXME(agent)` markers in changed files
- [ ] Feature entry in `feature_list.json` shows `passes: true`
```

The file is small, scoped, and has a clear removal condition: when premature-completion failures stop recurring across enough sessions, the file can be retired. `AGENTS.md` stays at 240 rules instead of 241.

## Key Takeaways

- The Method Map is a triage table — observation to smallest artifact — not a checklist applied prophylactically
- Each row carries a triggering observation in concrete terms; the table is invoked when behavior matches
- The doctrine: add the smallest artifact that addresses the observed failure; never enlarge a global instruction file
- Every per-failure addition needs a removal condition, not just an addition condition
- Earns its place only when failures have been observed, instruction count is near the compliance ceiling, and tasks span sessions

## Related

- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — the mechanism that makes "just add a rule" fail
- [Feature List Files](feature-list-files.md) — canonical page for the scope-sprawl row's `feature_list.json` artifact
- [Frozen Spec File](frozen-spec-file.md) — a Method Map artifact for scope drift across compaction
- [Agent Harness: Initializer and Coding Agent Pattern](../agent-design/agent-harness.md) — canonical page for the `init.sh` and `claude-progress.txt` artifacts
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md) — handoff and progress artifacts in depth
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — empirical counterweight: artifacts only help when curated
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md) — the same anti-bloat discipline at the file level

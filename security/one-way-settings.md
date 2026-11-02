---
title: "One-Way Settings: Keys With a Fixed Write Direction"
term: "One-Way Setting"
description: "A setting that accepts writes in one fixed direction only. Claude Code 2.1.311 restricted DISABLE_COMPACT to one direction and 2.1.312 let a subagent lower an operator window without raising it. The pattern fixes the direction of each key."
aliases:
  - fixed-direction setting
  - monotonic setting write
  - settings polarity
tags:
  - security
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-31
status: current
maturity: emerging
---

# One-Way Settings: Keys With a Fixed Write Direction

> A one-way setting accepts writes in one fixed direction and refuses writes in the other.

Claude Code resolves most keys by precedence: "a key at a higher level overrides the same key anywhere below it" ([settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)). Precedence decides which value wins. It does not decide who can write a key, and it says nothing about direction. Write access and value resolution are separate questions. A lower scope or a mod may write a key while a higher scope still resolves the final value. A directional rule adds a third answer. It accepts a lower-scope value only when the value moves the key in the allowed direction. A one-way key works by that rule: the writer may move the value one way and may not move it back.

## Two shipped instances

Two releases, one day apart, fixed the direction of two compaction controls.

| Release | Key | Writer | Allowed direction |
|---|---|---|---|
| [2.1.311](https://code.claude.com/docs/en/changelog#2-1-311), Oct 26, 2026 | `DISABLE_COMPACT` | Settings files and a mod's `$.env.set` | Compaction off only |
| [2.1.312](https://code.claude.com/docs/en/changelog#2-1-312), Oct 27, 2026 | A subagent's `autoCompactWindow` | The subagent definition | Lowers an explicit `CLAUDE_CODE_AUTO_COMPACT_WINDOW`; never raises it |

The 2.1.311 entry reads: "Changed `DISABLE_COMPACT` in settings files and in a mod's `$.env.set` so they can only turn compaction off, not back on" ([changelog](https://code.claude.com/docs/en/changelog#2-1-311)). The variable disables "all compaction: both automatic compaction and the manual `/compact` command" ([environment variables](https://code.claude.com/docs/en/env-vars)).

The 2.1.312 entry reads: "Changed a subagent's `autoCompactWindow` to lower the window set by `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, where it had no effect before; it still never raises that window" ([changelog](https://code.claude.com/docs/en/changelog#2-1-312)). The field arrived in 2.1.296 ([Per-Agent Compaction Windows](../context-engineering/per-agent-compaction-window.md)).

## Why a freely writable key is not a control

A mod reaches the machine "with the same permissions as the user running Claude Code", and `$.env` can `get` and `set` environment variables ([mods API](https://code.claude.com/docs/en/plugins/mods/api#reach-files-processes-and-the-network)). A key that a mod writes freely holds only until the first buggy or injected mod writes it. An operator who audits the plugin list is auditing the wrong thing.

A one-way key puts the check in the key, so the operator reasons about the worst case of one value instead of every writer. After 2.1.311 the worst case for `DISABLE_COMPACT` is a mod that turns compaction off.

The changelog gives no reason for the change. That the rule protects an operator who set the switch is my inference from its direction.

## The quiet failure it replaces

Before 2.1.312, a subagent's `autoCompactWindow` "had no effect" while the variable was set. As of 2026-10-31 the sub-agents page still describes that rule: "the subagent uses that variable's window instead and the field has no effect" ([sub-agents](https://code.claude.com/docs/en/sub-agents)). The changelog is newer, so treat the page as stale for 2.1.312 and later.

A field that reads as configured and does nothing is worse than a refused write. A refusal can be reported, and a no-op cannot be seen. A one-way write has three outcomes: it applies, it is clamped, or it is refused. Each needs a signal. The changelog does not say whether a refused `DISABLE_COMPACT` re-enable throws or is dropped.

## Other keys with a fixed direction

Tightening applies only where a key restricts something, as the last two rows do. For the compaction keys the changelog fixes a direction but does not call either direction safer.

| Key | Direction fixed by the docs |
|---|---|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | "the variable can't raise the threshold, so values above the default percentage are ignored" ([environment variables](https://code.claude.com/docs/en/env-vars)) |
| `maxEffortLevel` | "A lower cap from any scope, including `--settings`"; "the lowest cap applies" ([exceptions](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence)) |
| `crossSessionInbound` | "A stricter value from `.claude/settings.json` or `.claude/settings.local.json`, on the `accept` < `hold` < `refuse` ladder" ([exceptions](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence)) |

A boolean is one-way when one value always wins. A number is one-way under a minimum or maximum rule. A ladder is one-way when its positions have an order. Without an order on the values, a key has no direction.

This is a different axis from [scope demotion](repo-committed-settings-scope-demotion.md). Scope demotion asks which file may set a key. A one-way key asks which direction any reachable writer may move it. `remoteControlAtStartup` uses both: a project `true` is ignored and a project `false` is honored over managed `true` ([exceptions](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence)).

## Deciding the direction of a key

1. Name the state the operator must hold. For a spend cap it is the lower number.
2. Check that the values have an order. If they have none, use a field split instead ([A Containment Floor for Agent Self-Configuration](agent-self-config-field-classes.md)).
3. Let lower writers move toward that state only. Refuse or clamp the other direction.
4. Write the direction in the key's reference entry. `DISABLE_COMPACT` reads as a plain switch, and its direction appears only in the changelog.
5. Test a write in the allowed direction, a write in the other direction, and a read back. The read back catches the quiet case.

## When this backfires

- The safe direction is unclear. Compaction off avoids lossy summaries and risks a full context. The rule fixes a direction and does not say which one is right.
- The writer cannot undo an error. A mod that sets `DISABLE_COMPACT` by mistake has no write that reverses it, and the changelog does not describe the operator's way back. Check that path before you ship such a mod.
- A clamp can hide intent. A subagent that asks for a larger window than the operator set gets the operator window. The changelog documents no diagnostic for that case, so test whether your build reports it, and log clamps if it does not.
- Coverage is per key. A neighboring key with free writes reopens the path.

## Example

The 2.1.312 entry describes one case. An operator sets `CLAUDE_CODE_AUTO_COMPACT_WINDOW`. A subagent definition sets its own `autoCompactWindow` ([changelog](https://code.claude.com/docs/en/changelog#2-1-312)):

- If the subagent value is lower than the operator window, the subagent compacts earlier. Before 2.1.312 the field had no effect.
- If the subagent value is higher, the entry says the field "still never raises that window". The operator window holds.

The subagent can move the window one way only, toward earlier compaction. The `autoCompactWindow` field arrived in 2.1.296 ([changelog](https://code.claude.com/docs/en/changelog#2-1-296)).

## Key Takeaways

- A precedence stack orders writers and does not limit them. Fix a direction on any key that a plugin or subagent can reach.
- The 2.1.311 and 2.1.312 changes are two releases. `DISABLE_COMPACT` is a boolean fixed to off, and a subagent window is a number fixed to a minimum.
- Give every harness key an ordered value set and write its direction in the reference entry.
- Test the refused write. The old subagent field failed by doing nothing, and the changelog does not say how a refused re-enable reports.

## Related

- [Scope Demotion for Repository-Committed Settings](repo-committed-settings-scope-demotion.md) — which file may set a key, where this page asks which direction a write may move it
- [A Containment Floor for Agent Self-Configuration](agent-self-config-field-classes.md) — refusing writes by field class when the values have no order
- [Per-Agent Compaction Windows for Orchestrator and Worker](../context-engineering/per-agent-compaction-window.md) — the 2.1.296 field that 2.1.312 let lower an explicit operator window while it still never raises it
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — authority that only shrinks, enforced per value through tool composition
- [Administrative Effort Ceilings for Reasoning Budget](../patterns/agent-design/administrative-effort-ceilings.md) — a numeric cap where the lowest scope wins
- [Claude Code Mods and When to Use One Instead of a Hook](../tools/claude/mods.md) — the writer that `$.env.set` belongs to

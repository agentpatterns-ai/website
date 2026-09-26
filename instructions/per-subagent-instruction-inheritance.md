---
title: "Per-Subagent Instruction Inheritance (omitClaudeMd)"
term: "omitClaudeMd"
description: "Set omitClaudeMd on a Claude Code subagent to drop user, project, and local CLAUDE.md files. Managed policy files still load, except for managed subagents."
tags:
  - instructions
  - context-engineering
  - claude
aliases:
  - per-subagent instruction inheritance
  - subagent CLAUDE.md opt-out
applies_to: "claude-code@2.x"
last_reviewed: 2026-09-17
maturity: emerging
---

# Per-Subagent Instruction Inheritance (omitClaudeMd)

> `omitClaudeMd` makes instruction inheritance per-subagent. It drops the user, project, and local CLAUDE.md layer; managed policy survives unless the subagent itself is managed.

`omitClaudeMd: true` in a subagent's frontmatter or `--agents` JSON launches that subagent without the user, project, and local CLAUDE.md files. Managed policy files still load, except when the subagent's own definition comes from managed settings. The field requires Claude Code v2.1.271 or later, and it is ignored when the definition runs as the main session agent via `--agent` or the `agent` setting ([sub-agents reference, frontmatter fields](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)). It shipped on 14 September 2026 ([changelog 2.1.271](https://code.claude.com/docs/en/changelog#2-1-271)).

Each of those three conditions narrows the carve-out that makes the field look safe.

## What a subagent inherits by default

A non-fork subagent starts with a fresh context window and receives "every level of the CLAUDE.md hierarchy the main conversation loads, including `~/.claude/CLAUDE.md`, project rules, `CLAUDE.local.md`, managed policy files, and any `AGENTS.md` files loaded as project instructions". The built-in Explore and Plan agents already skip this. With the field set, a custom or plugin subagent "loads only the managed policy files, or none at all when the definition comes from managed settings" ([what loads at startup](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)).

## Which subagents keep CLAUDE.md

Sort your subagents by whether they judge work against project conventions. An agent that reviews, critiques, or architects reads those conventions as its rubric, so it keeps CLAUDE.md. An agent that runs a self-contained procedure never applies them and pays for them on every spawn. The docs state the same boundary from the other side: use the field "for subagents that take everything they need from the delegation prompt" ([frontmatter fields](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)).

One project proposed the split this way. The field goes on five browser and test agents whose `.claude/CLAUDE.md` measured 10.3KB, "about 3.4K tokens". It stays off `code-reviewer`, `project-architect`, and `design-reviewer`, because "they judge code or design against project rules" ([neoboard#1862](https://github.com/alfredo1996/neoboard/issues/1862)).

## Managed policy loads but does not enforce

Managed policy files continuing to load is continuity of instruction, not a control. Anthropic's own guidance draws the line: "Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer" ([memory docs](https://code.claude.com/docs/en/memory#manage-claude-md-for-large-teams)). Anything that must not happen belongs in [permissions or hooks](https://code.claude.com/docs/en/debug-your-config), which hold whether or not the field is set.

Plugin subagents support the field ([plugin components reference](https://code.claude.com/docs/en/plugins/components#frontmatter-fields-in-plugin-agents)), and their inheritance problem is wider than an opt-out fixes. A plugin's own root CLAUDE.md "is not loaded as project context", so a plugin subagent reads the host repository's conventions and never its author's ([plugin components reference](https://code.claude.com/docs/en/plugins/components#skills)).

## How it composes with claudeMdExcludes

| Lever | Granularity | Scope |
|-------|-------------|-------|
| [`claudeMdExcludes`](claude-md-excludes.md) | Named files and globs | Every agent in the session |
| `omitClaudeMd` | The whole user, project, and local layer | One subagent |

The two act on different axes and stack. Both stop short of managed policy: managed CLAUDE.md files "cannot be excluded" by `claudeMdExcludes` ([memory docs](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files)), and `omitClaudeMd` leaves them loaded unless the subagent itself is managed.

## Example

A test-runner subagent invokes the suite and reports failures, applying no naming, layout, or review conventions.

```yaml
---
name: test-runner
description: Runs the test suite and reports failures.
tools: [Bash, Read, Grep]
omitClaudeMd: true
---

Run `make test`. Report each failing test with its assertion and file path.
```

Check what actually loaded rather than assume. `/context` shows what occupies the window for a session, including memory files and the source each subagent loaded from ([debug your configuration](https://code.claude.com/docs/en/debug-your-config)).

## Why it works

Two causes, and only the first is specific to the field. CLAUDE.md reaches a subagent as part of its initial context, alongside the system prompt and the delegation message ([what loads at startup](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)). Every spawn re-pays it, the same pressure behind the guidance to keep CLAUDE.md under 200 lines and move workflow detail into skills ([manage costs](https://code.claude.com/docs/en/costs#move-instructions-from-claude-md-to-skills)). The field cuts at the composition step, so the dropped files are never assembled into the request.

The second cause is behavioral. Instruction-following degrades as instruction density rises, an effect the IFScale benchmark measured across 20 models from seven providers ([Jaroslawicz et al., 2025](https://arxiv.org/abs/2507.11538v1)). That is general instruction-load research, not a measurement of this field. It predicts that dropping rules a specialist never applies improves adherence to the ones it does. No published figure measures the effect for `omitClaudeMd`.

## When this backfires

- The subagent judges work against conventions. A reviewer with the field set still returns a confident verdict, now against no house rules. The troubleshooting docs list the field as a cause of "Subagent ignores `CLAUDE.md` instructions", with removal as the fix ([debug your configuration](https://code.claude.com/docs/en/debug-your-config)).
- The subagent writes files. It produces a diff the conventions govern while the parent conversation reads only a returned summary, so the omission shows up at review rather than at dispatch.
- The definition gets promoted to the main session agent. `--agent` and the `agent` setting ignore the field, so one file behaves two ways depending on how it is launched ([frontmatter fields](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)).
- An administrator deploys the subagent through managed settings. The organization's own CLAUDE.md then stops reaching the agents the organization shipped.
- The client predates v2.1.271. The field is ignored with no error, so a team on mixed versions gets two behaviors from one file.
- The needed rule lived in a teammate's `CLAUDE.local.md`. Local files sit in the dropped set and nothing names them when they go.

The documented mitigation is narrow. Restate a load-bearing rule "in the prompt you give Claude when delegating" ([what loads at startup](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)), which moves a durable convention into a prompt Claude composes fresh at each dispatch.

## Key Takeaways

- Decide inheritance per agent, not once for the harness. The field drops the user, project, and local layer for one subagent, and managed policy survives unless that subagent is itself deployed through managed settings.
- Keep the field off any agent that judges work against project conventions, and check `/context` rather than assuming what loaded.
- Managed policy loading is not enforcement. Put anything that must never happen in permissions or hooks.
- The field is inert below Claude Code v2.1.271 and under `--agent`, so a definition carrying it has an unstated version and launch-mode dependency.

## Related

- [claudeMdExcludes: Selective Ancestor Instruction-File Exclusion](claude-md-excludes.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Subagent vs In-Context Skill Execution](../patterns/agent-design/subagent-vs-in-context-skill-execution.md)

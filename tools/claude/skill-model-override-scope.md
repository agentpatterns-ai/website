---
title: "Claude Code Skill Model Override: What Stays on Session"
description: "From v2.1.330, when Claude runs a skill with a model setting, it leaves subagents, forks, compaction and /recap on the session model. What the entry says, the context: fork exception, and how to check."
tags:
  - claude
  - agent-design
  - cost-performance
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-23
status: current
---

# Claude Code Skill Model Override: What Stays on Session

> From v2.1.330, when Claude runs a skill with a `model` setting, the skill leaves subagents, forks, compaction and `/recap` on the session's model. `context: fork` skills are the exception.

A skill's `model` frontmatter field sets the model for the skill's own work. From v2.1.330, when Claude runs the skill, it does not set the model that subagents, forks, compaction and `/recap` use. The entry does not say whether the same holds when you invoke the skill yourself with `/name`. The v2.1.330 changelog (November 20, 2026) records the change: "Changed skills that Claude runs with a `model` setting, other than `context: fork` skills, to leave subagents, forks, compaction and `/recap` on the session's model" ([changelog](https://code.claude.com/docs/en/changelog)). The `model` row of the skills reference does not state this scope as of November 23, 2026.

## What the field sets

The skills reference describes `model` as the model "to use when this skill is active". The override "applies for the rest of the current turn and isn't saved to settings", and "the session model resumes when you send your next prompt" ([skills reference](https://code.claude.com/docs/en/skills.md#frontmatter-reference)). The field accepts the same values as `/model`, or `inherit` to keep the active model.

## What the entry leaves on the session model

The entry names four kinds of work. Where another page describes the same work, the table adds it.

| Work | What the entry says | What the docs add |
|------|---------------------|-------------------|
| Subagents | Stay on the session's model | A subagent you define runs on the model of the conversation that starts it, unless its `model` field or another source in the [model order](https://code.claude.com/docs/en/sub-agents.md#choose-a-model) sets one |
| Forks | Stay on the session's model | A fork sees the same model as its parent conversation ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#fork-the-current-conversation)) |
| Compaction | Stays on the session's model | Only the changelog entry is cited here |
| `/recap` | Stays on the session's model | `/recap` generates a one-line summary of the current session on demand ([commands](https://code.claude.com/docs/en/commands.md)) |

The entry does not describe the earlier behavior. It says "Changed ... to leave", which implies that these kinds of work could follow a skill's model before v2.1.330. The entry does not say which of them did.

The entry does not say what happens to a subagent whose definition sets its own `model` field. The sub-agents page ranks that field above the parent's model, and the entry does not say whether the change touches that order. Test a pinned subagent that a skill with `model` set starts.

## When Claude Code skips the override

Claude Code skips a skill's model value in two cases, and the session keeps its current model ([skills reference](https://code.claude.com/docs/en/skills.md#frontmatter-reference)):

- Your organization's `availableModels` allowlist excludes the value.
- You are in auto mode, or in plan mode while the classifier reviews commands, and the model is one that auto mode does not support.

The model configuration page covers the allowlist case for a blocked family alias too. Claude Code ignores the override, and the skill runs on the session model ([model configuration](https://code.claude.com/docs/en/model-config.md#restrict-model-selection)).

## The context: fork exception

The entry excludes `context: fork` skills. For these skills, the `model` value "sets the forked subagent's model instead". An excluded value follows the same rules as a subagent model override ([skills reference](https://code.claude.com/docs/en/skills.md#frontmatter-reference)). For a subagent override, Claude Code runs the subagent on a fallback model rather than failing the request ([model configuration](https://code.claude.com/docs/en/model-config.md#restrict-model-selection)).

The entry lists "forks" and `context: fork` skills as separate items. The skills reference says a `context: fork` skill does not run in a fork of your current conversation. It starts a new subagent that does not see your conversation history ([skills reference](https://code.claude.com/docs/en/skills.md#run-skills-in-a-subagent)).

The entry does not say what agents started by a forked skill's subagent run on. The sub-agents page says a nested subagent you define runs on its parent's model, and lists a subagent with no `model` field among those that follow it ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#which-model-a-nested-subagent-runs-on)). Read together, an agent with no `model` field that a forked skill's subagent starts runs on that subagent's model. The entry excludes forked skills from the change and does not confirm this reading, so check it with `/tasks`.

## Example

A skill that sets a cheaper model for a lookup, in a session on a larger model:

```yaml
---
name: quick-lookup
description: Fast keyword search across the codebase
model: haiku
---
```

When Claude runs this skill inline on v2.1.330 or later, the skill's turn uses Haiku, unless your `availableModels` allowlist or the auto mode case above skips it. Per the entry, subagents, forks, compaction and `/recap` stay on the session model. The session model resumes at your next prompt.

To put delegated work on a different model, run the skill as a forked subagent, or set `model` in a subagent definition:

```yaml
---
name: repo-survey
description: Survey the repository layout and report the main modules
context: fork
agent: Explore
model: haiku
---
```

With `context: fork`, the `model` value sets the forked subagent's model.

## Check which model ran

- Run `/tasks` while a subagent runs. Claude Code names the model on the subagent's row. This needs v2.1.242 or later ([sub-agents](https://code.claude.com/docs/en/sub-agents.md#check-a-subagents-model)).
- The status line and `/status` show the model you are on ([model configuration](https://code.claude.com/docs/en/model-config.md#checking-your-current-model)).

These two checks cover a subagent that a skill starts and the session's own model. For compaction and `/recap`, the changelog entry is the only source cited here.

## Key Takeaways

- From v2.1.330, when Claude runs a skill with a `model` setting, it leaves subagents, forks, compaction and `/recap` on the session's model, except for `context: fork` skills.
- The override lasts for the rest of the current turn and ends when you send your next prompt.
- Claude Code skips the value when the `availableModels` allowlist excludes it, and in the auto mode and plan mode case the skills reference names.
- With `context: fork`, the `model` value sets the forked subagent's model. The entry does not say what that subagent's own agents run on.
- Check a subagent's model with `/tasks` (v2.1.242 or later) and the session's model with `/status`.

## Related

- [Skill Frontmatter Reference](../../tool-engineering/skill-frontmatter-reference.md)
- [Claude Code Subagent Model Fallback: What Carries Down](subagent-fallback-carry-over.md)
- [Claude Code Sub-Agents for Delegating Complex Tasks](sub-agents.md)
- [Forked vs Fresh Subagents](../../patterns/multi-agent/forked-vs-fresh-subagents.md)
- [Skill disallowed-tools Frontmatter](skill-disallowed-tools.md)

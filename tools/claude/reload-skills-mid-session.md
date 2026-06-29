---
title: "Reloading Skills Mid-Session in Claude Code"
description: "Re-scan skill directories mid-session in Claude Code with /reload-skills or a SessionStart reloadSkills hook, picking up edited skills without losing context."
tags:
  - claude
  - tool-engineering
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-03
status: current
---

# Reloading Skills Mid-Session in Claude Code

> Claude Code can re-scan skill directories mid-session, making edited or newly installed skills available without a restart that discards accumulated context.

Claude Code v2.1.152 added two ways to re-scan skill directories inside a running session: the `/reload-skills` command and a `SessionStart` hook that returns `reloadSkills: true`. Both refresh the set of skills the model can invoke in place, leaving the conversation context untouched. [Source: [Claude Code changelog](https://code.claude.com/docs/en/changelog), 2026-05-27]

## Two reload paths

The two paths differ by who triggers them and when they fire:

| Path | Who triggers it | When it fires |
|------|-----------------|---------------|
| `/reload-skills` | You (or the model) invoke it mid-session | After you edit or install a `SKILL.md` by hand and want it live now |
| `SessionStart` hook returning `reloadSkills: true` | A `SessionStart` hook | At session startup or resume, after the hook itself installs skills programmatically |

`/reload-skills` is the manual path for an authoring loop. The `reloadSkills: true` return is for hooks that fetch, generate, or install skills before the first turn — without it, hook-installed skills would not register until the next launch. [Source: [Claude Code changelog](https://code.claude.com/docs/en/changelog), 2026-05-27] The same release lets a `SessionStart` hook set the session title via `hookSpecificOutput.sessionTitle` on startup and resume. [Source: [Claude Code changelog](https://code.claude.com/docs/en/changelog), 2026-05-27]

## Why it works

Claude Code scans skill directories to build the set of skills the model can invoke. Historically this scan ran once, at launch, so the available-skills set was fixed for the session. Picking up an edit meant restarting, which discards the conversation transcript, files read into context, the active task list, and any reasoning built up so far. A reload re-runs the directory scan against the live session. It swaps in the current on-disk `SKILL.md` set while leaving the context object intact. This decouples capability discovery (a cheap, re-runnable directory scan) from context accumulation (expensive, lost on restart), so editing a skill no longer forces you to pay the context-rebuild cost. [Source: [Claude Code changelog](https://code.claude.com/docs/en/changelog), 2026-05-27] This mirrors `/reload-plugins`, the analogous hot-reload for the plugin layer that reloads plugins, skills, agents, hooks, and plugin MCP servers without a restart. [Source: [Claude Code plugins guide](https://code.claude.com/docs/en/plugins)]

## What a reload preserves

A restart loses everything the model has accumulated; a reload keeps it.

- Preserved: conversation transcript, files already read into context, the active todo/task list, sub-agent results gathered so far, and accumulated reasoning.
- Refreshed: the set of skills discoverable from the scanned directories — newly added, edited, or removed `SKILL.md` definitions.

This is what collapses the authoring loop to edit → reload → test inside one session.

## When this backfires

Reloading is not always the better choice over a clean restart:

- Short sessions with little context — with no accumulated transcript or state to protect, a restart is simpler and removes any risk of a stale registration.
- Edits that interact with loaded context — the model retains reasoning and tool selections made before the skill set changed; a reloaded or removed skill can leave earlier in-context decisions stale, which a clean restart avoids.
- Untrusted hook-installed skills — a `SessionStart` hook that fetches and installs skills from an external source then registers them via `reloadSkills: true` widens the trust surface, since an installed `SKILL.md` is model-readable instruction. Auto-installing skills from untrusted input couples external content to the agent's capability set.
- Debugging skill triggering — when a skill mis-fires, reloading after an edit keeps prior-turn context that can mask whether the fix actually changed behavior; a clean restart isolates the variable.

A reload also does not refresh everything a restart would. Reloading updates the model-facing skill set but does not rebuild the `/` command parser index, so a newly added skill can be invocable by the model yet still return "Unknown skill" on direct slash invocation or be missing from `/` autocomplete until a full restart. [Source: [anthropics/claude-code#37862](https://github.com/anthropics/claude-code/issues/37862)] When you need a skill reachable by name from the command line in the same session, restart rather than reload.

## Example

Iterating on a skill without leaving the session:

```text
# 1. Edit the skill on disk
.claude/skills/my-skill/SKILL.md   (change the description or body)

# 2. Re-scan skill directories in the running session
/reload-skills

# 3. Test the updated skill immediately — context from steps before the edit is intact
```

A `SessionStart` hook that installs a skill and registers it for the same session returns:

```json
{
  "hookSpecificOutput": {
    "reloadSkills": true,
    "sessionTitle": "skill-authoring loop"
  }
}
```

## Key Takeaways

- `/reload-skills` re-scans skill directories mid-session; the `SessionStart` `reloadSkills: true` return does the same for hook-installed skills at startup or resume. [Source: [Claude Code changelog](https://code.claude.com/docs/en/changelog), 2026-05-27]
- A reload preserves session context (transcript, loaded files, task list) that a restart would discard, collapsing the authoring loop to edit → reload → test.
- It works by decoupling the cheap directory scan from expensive context accumulation.
- Prefer a clean restart for short sessions, edits that interact with loaded context, or isolating a trigger-debugging variable.
- Treat hook-installed skills from untrusted sources as a widened trust surface.

## Related

- [Skill Eval Loop](skill-eval-loop.md) — test and benchmark a skill once a reload makes the edit live
- [Claude Code Hooks](hooks-lifecycle.md) — the `SessionStart` event that carries the `reloadSkills` return field
- [Skill Authoring Patterns](../../tool-engineering/skill-authoring-patterns.md) — writing the `SKILL.md` edits this loop iterates on
- [Skill Library Evolution](../../tool-engineering/skill-library-evolution.md) — lifecycle governance for the skills a reload picks up
- [Extension Points](extension-points.md) — choosing between skills, hooks, and other Claude Code mechanisms

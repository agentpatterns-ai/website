---
title: "Allowing One Skill to Run in Scheduled Tasks and /loop"
term: "Skill Allow Rule"
description: "Since Claude Code 2.1.325, scheduled tasks and /loop ask before running a skill that declares allowed-tools or hooks. Grant that one skill with Skill(name)."
tags:
  - agent-design
  - automation
  - skills
  - claude
aliases:
  - Skill(name) allow rule
  - unattended skill permission
  - scheduled task skill prompt
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-21
maturity: emerging
status: current
---

# Allowing One Skill to Run in Scheduled Tasks and /loop

> Scheduled tasks and `/loop` now ask before running a skill that declares `allowed-tools` or hooks, so an unattended run needs a `Skill(name)` allow rule.

Claude Code 2.1.325 "Changed scheduled tasks and `/loop` to ask before running a skill that declares `allowed-tools` or hooks; add `Skill(name)` to `permissions.allow` to run it unattended" ([changelog 2.1.325](https://code.claude.com/docs/en/changelog#2-1-325)). A fire that hits this prompt waits for a person who is not there. The entry does not say whether a permission mode skips the prompt. It also does not separate session tasks from Desktop scheduled tasks.

## When the prompt fires

The prompt needs a skill that can run in a scheduled fire at all. A fire "only runs skills that Claude is allowed to invoke on its own". A skill marked `disable-model-invocation: true` or withheld by a `Skill` deny rule reaches Claude as plain text instead ([scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)). Those skills never execute, so the new prompt is not what stops them.

Of the skills that do run, the prompt covers the ones whose frontmatter declares `allowed-tools` or `hooks`. A skill that declares neither is outside the changelog entry.

## Grant one skill

Add the rule to `permissions.allow` in a settings file the run reads:

```json
{
  "permissions": {
    "allow": ["Skill(review-pr *)"]
  }
}
```

Pick the form by how the schedule calls the skill. The skills reference gives "`Skill(name)` for exact match, `Skill(name *)` for prefix match with any arguments" ([skills reference](https://code.claude.com/docs/en/skills#restrict-claude%E2%80%99s-skill-access)). The scheduled-tasks page shows `/loop 20m /review-pr 1234`, which passes an argument, so the rule above uses the prefix form. Write `Skill(review-pr)` only when the schedule calls the skill with no arguments.

Put the rule where the run will read it. A `/loop` "Inherits from session" for permission prompts ([scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)). For Desktop tasks, "Allow rules from `~/.claude/settings.json` also apply to scheduled task sessions" ([Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks#permissions-for-scheduled-tasks)). A deny or ask rule for the same skill still wins, because "Rules are evaluated in order: deny, then ask, then allow" ([permissions](https://code.claude.com/docs/en/permissions)).

## Why it works

`allowed-tools` is a grant the skill writes for itself. It lists "Tools Claude can use without asking permission during the turn that invokes this skill. The grant clears when you send your next message." ([skills reference](https://code.claude.com/docs/en/skills#frontmatter-reference)). In an attended session a person sees the skill start. In a scheduled fire nobody does, which is the gap the 2.1.325 prompt closes.

A `Skill(name)` rule moves that approval from a live prompt to a standing decision about one skill. The tools stay bound to the turn that invokes it. The alternative, listing the same tools in `permissions.allow`, pre-approves them "for the whole session rather than a single turn" ([skills reference](https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill)). Every other turn in that session then has them pre-approved too.

## Find a run that is waiting

In a `/loop` session, a `Notification` hook with the `permission_prompt` matcher fires when Claude needs approval for a tool use "and the prompt has waited about six seconds". To act at once, the hooks reference points to a `PermissionRequest` hook instead ([hooks reference](https://code.claude.com/docs/en/hooks)).

For a Desktop task, "When a run is stalled on a permission prompt, find the run’s session and answer the prompt there" ([Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks#permissions-for-scheduled-tasks)).

If a refusal is better than a wait, `permissions.denyInsteadOfPrompting` from 2.1.319 means "a tool call that would wait on a permission prompt is denied and the turn continues, in terminal sessions, subagents and teammates" ([changelog 2.1.319](https://code.claude.com/docs/en/changelog#2-1-319)). The fire then finishes without the skill. The entry does not name scheduled tasks, so test it on yours.

## The "Always allow" change in the same release

The same release "Changed “Always allow” in Desktop, IDE and SDK hosts: a rule alone is offered only when saving it would allow that command again, so a scheduled task that relied on one can now wait for you" ([changelog 2.1.325](https://code.claude.com/docs/en/changelog#2-1-325)). As of 2026-11-21 the Desktop page still tells you to click **Run now** and select "always allow" for each prompt ([Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks#permissions-for-scheduled-tasks)). After 2.1.325 that click may save no rule. Write the `Skill(name)` rule in the settings file instead, where you can read it.

## When this backfires

- The skill lives in a repository other people edit. The rule names the skill, not its contents, so a later edit to its `allowed-tools` or hooks runs unattended with no prompt. The skills reference warns that "A skill can grant itself broad tool access, so review the `allowed-tools` of skills checked into a repository before you run Claude Code there" ([skills reference](https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill)).
- The rule form does not match the call. An exact `Skill(name)` rule for a schedule that passes arguments leaves the prompt in place, and the fire still waits.
- The skill needs one or two narrow tools. Then the opposite move can be better: drop `allowed-tools` and hooks from the skill and write those few tool rules in settings, where review sees each one. The skill falls outside the 2.1.325 prompt, and the cost is that those tools apply for the whole session.
- You rely on a written rule without testing it on your surface. In April 2026, before 2.1.325, one user reported Cowork scheduled tasks prompting on every run despite both "Always allow" and explicit allow rules in `~/.claude/settings.json` ([anthropics/claude-code#47180](https://github.com/anthropics/claude-code/issues/47180)). Run the schedule once while you watch (for a Desktop task, **Run now**) and confirm the `Skill(name)` rule clears the prompt before you leave it unattended.

## Key Takeaways

- Check each scheduled skill's frontmatter for `allowed-tools` or `hooks`. Those are the skills 2.1.325 stops for a prompt.
- Use `Skill(name *)` when the schedule passes arguments, and keep the exact form for bare calls.
- Prefer the skill rule to a tool allowlist when the skill's grant is wide, because the skill's tools stay bound to its own turn.
- Wire a `PermissionRequest` or `Notification` hook so a waiting fire tells you, or set `denyInsteadOfPrompting` and accept a fire that skips the skill.

## Related

- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — what an unattended run should do with a prompt nobody can answer
- [A Skill's Tool Grant Travels With Its Hooks](../../security/skill-tool-grant-travels-with-hooks.md) — the 2.1.304 rule that withdraws a skill's grant under a plugins-only hooks policy
- [Session Scheduling with Loop and Cron in Claude Code](../../tools/claude/session-scheduling.md) — how `/loop` and scheduled tasks fire inside a session
- [Whose Permissions a Self-Scheduled Agent Run Carries](../../security/self-scheduled-run-authority.md) — which principal an unattended run acts for

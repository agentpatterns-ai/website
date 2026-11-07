---
title: "Per-Surface Hook Matchers for Shell-Starting Tools"
term: "Per-Surface Hook Matchers"
description: "A hook if condition holds one tool name, so every tool that can start a shell needs its own rule. Claude Code took 204 days to cover the third one."
tags:
  - pattern
  - agent-design
  - hooks
  - claude
aliases:
  - shell surface matcher coverage
  - one hook rule per shell tool
  - hook matcher tool-name coverage
applies_to: "claude-code@2.1.314"
last_reviewed: 2026-11-02
maturity: emerging
status: current
---

# Per-Surface Hook Matchers for Shell-Starting Tools

> List every tool in your harness that can start a shell, then check each name against your hook rules.

Three conditions decide whether this audit earns its afternoon. Your guard has to use a hook's `if` condition or a content-scoped permission rule, since those are the layers carrying a tool name. A handler that matches broadly and dispatches on `tool_name` inside its own script is not what either half of the 2.1.314 change touched. Your build has to be 2.1.314 or later. That is the release where a `Monitor(...)` condition starts matching Monitor's shell commands the way a `Bash(...)` one matches Bash's. And what you want has to be a block or a prompt rather than enforcement.

Where all three hold, the audit is one pass over `settings.json`. Claude Code's sandbox scope is the vendor's own enumeration of the surfaces: "Bash, PowerShell, and Monitor tool commands and their child processes" ([permissions reference](https://code.claude.com/docs/en/permissions#how-permissions-interact-with-sandboxing)). Three names, and a rule naming one of them covers one of them.

## The 2.1.314 change

Claude Code 2.1.314 (October 30, 2026) records the gap and its repair in one release. The fix:

> "Fixed hooks matching Bash not running on shell commands started by the Monitor tool; such hooks can block or ask, but not approve or rewrite those commands"

And the change:

> "Changed hook `if` conditions such as `Monitor(tail *)` to match the Monitor tool's shell commands as `Bash(tail *)` matches Bash's"

([changelog 2.1.314](https://code.claude.com/docs/en/changelog#2-1-314))

Read the fix line for what it says about the six months before it. A hook matching Bash did not run on the same command when Monitor started it, and nothing said so. That is the transferable part, whatever harness you run: a deny that does not fire and a deny that was never reached leave identical transcripts.

## Why it works

A name-scoped control covers the names someone wrote. A capability-scoped control covers whatever reaches the capability.

The hooks reference pins the first half: "The `if` field holds exactly one permission rule." So its own two-surface example needs two handlers under a single `Bash|PowerShell` matcher, one for `Bash(rm *)` and one for `PowerShell(Remove-Item *)`. The reference says why: "A single `if` rule matches only one tool's calls, so each tool gets its own handler" ([hooks reference](https://code.claude.com/docs/en/hooks)). The covered set is whatever an author last enumerated, and nothing recomputes it when a tool ships.

Sandboxing is the other shape, and the quote above is its scope. The grant attaches to the process, so a fourth shell-starting tool inherits it with no edit.

Monitor shipped in 2.1.98 on April 9, 2026 ("Added Monitor tool for streaming events from background scripts"); hook `if` conditions matched it 204 days later. In between, other releases named the tool in one more place each. Four of them, as a selection and not a full list:

| Release | Date | Where Monitor was named |
|---|---|---|
| 2.1.236 | August 19, 2026 | Auto mode sets Monitor allow rules aside, "so Monitor commands are reviewed the same way Bash commands are" |
| 2.1.271 | September 14, 2026 | Per-command `allowed_domains` in auto mode with sandboxing, for "Bash, PowerShell and Monitor" |
| 2.1.286 | September 30, 2026 | Permission prompts show the command between dashed lines, for "Bash, PowerShell and Monitor" |
| 2.1.290 | October 5, 2026 | Sandboxed Monitor commands stop "skipping the permission prompt under sandbox auto-allow" |

The four rows and the 2.1.98 line all come from the [Claude Code changelog](https://code.claude.com/docs/en/changelog). The changelog names Monitor in more releases than these four. What the four share is that each had to be told the name. That is what a per-name coverage model gets you.

## The powers are not equal

The audit does not make the two surfaces behave alike. Monitor-matched hooks "can block or ask, but not approve or rewrite those commands" ([changelog 2.1.314](https://code.claude.com/docs/en/changelog#2-1-314)). Approve and rewrite are two documented `PreToolUse` outputs: `permissionDecision: "allow"`, and `updatedInput`, which "replaces a tool's arguments before it runs" ([hooks reference](https://code.claude.com/docs/en/hooks#pretooluse)).

So a guard that normalizes a command, or pre-approves a known-safe one, is not portable. Writing the `Monitor(...)` twin makes that asymmetry live in your harness rather than closing it, and the rule looks the same either way. A guard whose whole job is blocking loses nothing. The downgrade is not special to Monitor either. The same release changes auto mode in Cowork cloud sessions, where "a hook's allow of an MCP tool call now counts as no answer, so the classifier or a permission prompt decides" ([changelog 2.1.314](https://code.claude.com/docs/en/changelog#2-1-314)) — a narrower case than this one, and the same direction. A hook's veto travels; a hook's permission does not.

## Example

One line per tool that can start a shell, one `if` handler per line.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell|Monitor",
        "hooks": [
          { "type": "command", "if": "Bash(curl *)", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.sh" },
          { "type": "command", "if": "PowerShell(curl *)", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.sh" },
          { "type": "command", "if": "Monitor(curl *)", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.sh" }
        ]
      }
    ]
  }
}
```

The matcher is one string and takes a pipe-separated list, so coverage does not leak there. The three `if` lines are where it leaks, and before 2.1.314 the third did not match the way the first one does.

A `curl` poll loop is a realistic Monitor script, which is the point of picking it: the same command, the same guard, three places to register it.

Then test it, because the failure is quiet. Run the same command through each surface in one session and assert the hook fired on every one. A hook that does not run returns no decision and sends the model no feedback. A passing session proves nothing about the surfaces you did not exercise. The startup warning will not help: a deny or ask rule whose tool name matches no known tool "produces a startup warning to catch typos" ([permissions reference](https://code.claude.com/docs/en/permissions#permission-rule-syntax)). It catches a name matching no tool, never a tool matching no name.

## When this backfires

The strongest case against the audit is the vendor's, and it sits in both references the audit sends you to. On the hook side: "Because the `if` filter is best-effort, use the [permission system](https://code.claude.com/docs/en/permissions) rather than a hook to enforce a hard allow or deny" ([hooks reference](https://code.claude.com/docs/en/hooks)). On the permission side, a Bash rule "doesn't match the same program invoked in a different form, so a deny or ask rule covers the invocation Claude usually produces and isn't a security boundary around the program" — `Bash(curl *)` stops `curl https://example.com` and not `/usr/bin/curl https://example.com` ([permissions reference](https://code.claude.com/docs/en/permissions#what-a-bash-rule-doesnt-match)). A respelling beats that with no second tool involved.

So a team enumerating shell surfaces is keeping a best-effort filter current, while [sandboxing](https://code.claude.com/docs/en/sandboxing) covers all three surfaces and the respellings by construction. On that reading, 2.1.314 argues for dropping the matcher audit rather than running it more carefully. I think that goes a step too far: a sandbox confines, it does not stop and ask a person, and block/ask is the half that survived on both surfaces. But it is the right order of work. Sandbox first, audit matchers second, and never call the second one the boundary.

One property runs through all three disqualifying conditions and is the reason to check them before the edit rather than after. Each fails as a diff that looks correct. A `Monitor(...)` rule on a pre-2.1.314 build, a twin added to a handler that had no `if` field, a rewriting guard ported to a surface that cannot rewrite: all three review clean.

## Key Takeaways

- The audit list for Claude Code today is `Bash`, `PowerShell`, `Monitor`. Re-derive it per release rather than copying this line; the gap this page describes is what a stale copy produces.
- Grep your settings for `"if":` and count distinct tool names against that list. A matcher with a pipe list and one `if` line is the shape to look for.
- Sandbox first, then audit matchers. A sandbox grant attaches to the process and needs no list; an `if` rule needs a name, and the name is what goes missing.
- Write the per-surface test in the same change as the rule. A hook that never fires logs nothing, and the startup warning catches a misspelled tool name rather than a missing one.
- Where the guard approves or rewrites rather than blocks, log which surface a decision came from. The powers differ and the configuration does not show it.

## Related

- [Hooks & Lifecycle](../../tools/claude/hooks-lifecycle.md) — matcher and `if` syntax, and the schema-coupling failure this page is one instance of
- [Monitor Tool: Event Streaming from Background Scripts](../../tools/claude/monitor-tool.md) — what the third shell surface is for
- [Wait Primitive Plus Shell-Sleep Deny](wait-primitive-shell-sleep-deny.md) — the 2.1.310 release that paired Monitor with a foreground-sleep block
- [Judging a Write by Its Spelled Path (Spelled-Path Scope)](../anti-patterns/spelled-path-permission-scope.md) — the same guard-versus-reality gap at the path layer rather than the tool-name layer
- [Most-Restrictive-Wins Fusion for Parallel Agent Control Returns](most-restrictive-wins-fusion.md) — how the decisions that do fire get merged
- [Per-Source Hook Registration Budgets](per-source-hook-registration-budgets.md) — Separate hook-count and matcher-character limits for each skill source, with diagnosis for missing hooks

---
title: "Out-of-Band Hook Notifications via terminalSequence"
description: "Claude Code's terminalSequence hook field emits allowlisted terminal escape sequences — window titles, bells, OSC 9/99/777 desktop notifications — through the harness's own write path, signaling the human without spending agent context."
tags:
  - tool-engineering
  - observability
  - claude
aliases:
  - terminalSequence hook field
  - out-of-band agent notifications
  - hook desktop notifications
last_reviewed: 2026-06-03
maturity: adopted
---

# Out-of-Band Hook Notifications via terminalSequence

> The `terminalSequence` field on hook JSON output lets a hook ping the human — desktop notification, window title, bell — without writing to the agent's transcript and without depending on `osascript`, `notify-send`, or a writable `/dev/tty`.

## The channel

[Claude Code v2.1.141](https://code.claude.com/docs/en/changelog) (May 13, 2026) added `terminalSequence` to hook JSON output. When a hook returns

```json
{ "terminalSequence": "\u001b]777;notify;Claude Code;Build finished" }
```

the harness writes those bytes to its own controlling terminal after parsing the hook's JSON. The bytes never enter the agent's context window. The human sees a notification; the agent sees nothing.

This replaces three legacy patterns:

| Legacy pattern | Failure mode |
| --- | --- |
| Hook writes to `/dev/tty` directly | Removed from hook processes in [v2.1.139](https://code.claude.com/docs/en/changelog); never worked on Windows |
| Hook prints to stdout | Appended to agent context — spends tokens, re-enters the reasoning loop |
| Hook shells out to `osascript` / `notify-send` / `BurntToast` | Platform-specific; silently fails when the notifier lacks permission ([hooks guide](https://code.claude.com/docs/en/hooks-guide)); requires per-OS branches |

The structured field works inside `tmux`, over `ssh`, on Windows, and from any language that can emit JSON.

## The allowlist

The field accepts a string of escape sequences from a fixed set ([hooks reference](https://code.claude.com/docs/en/hooks)). Anything outside this set is rejected and the field is silently ignored:

| Sequence | Effect | Honored by |
| --- | --- | --- |
| `OSC 0` / `OSC 1` / `OSC 2` | Window and icon title | All major emulators |
| `OSC 9` | Desktop notification (and `9;4` taskbar progress) | iTerm2, ConEmu, Windows Terminal, WezTerm |
| `OSC 99` | Desktop notification | Kitty |
| `OSC 777` | Desktop notification | urxvt, Ghostty, Warp |
| Bare `BEL` | Audible bell | All terminals |

Sequences may terminate with `BEL` (`\007`) or `ST` (`\\`). Rejected sequences include CSI cursor and color codes, OSC 8 hyperlinks, OSC 52 clipboard writes, and OSC 1337.

The allowlist is a security control. By excluding cursor-move, color, clipboard, and hyperlink sequences, a hook cannot corrupt the on-screen prompt, smuggle a hidden link, or write to the system clipboard ([hooks reference](https://code.claude.com/docs/en/hooks)).

## Where it belongs

Hook events that fire when the human is the next actor justify a notification. Hook events that fire on every tool call do not.

| Event | Notify? | Reason |
| --- | --- | --- |
| `Stop` | Yes | Agent finished; the human resumes |
| `SubagentStop` | Yes | Long sub-task finished; signal completion |
| `Notification` (permission prompt, idle) | Yes | Agent is blocked waiting on the human |
| `StopFailure` | Yes | API error; human action likely required — see [StopFailure Hook](stopfailure-hook.md) |
| `PreToolUse` / `PostToolUse` | No | Fires dozens of times per task — notification fatigue |
| `SessionStart` / `PreCompact` | No | Routine; the human is not waiting |

## Example

A `Stop` hook that pings the desktop and updates the window title with the completion status.

`.claude/hooks/notify-stop.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')

# OSC 777 notification (urxvt/Ghostty/Warp), OSC 9 (iTerm2/Windows Terminal/WezTerm),
# OSC 2 window title. Terminals ignore sequences they don't recognise.
NOTIFY=$(printf '\033]777;notify;Claude Code;Turn finished (%s)\007' "$SESSION_ID")
ITERM=$(printf '\033]9;Claude Code: turn finished\007')
TITLE=$(printf '\033]2;Claude: done\007')

jq -nc \
  --arg seq "${NOTIFY}${ITERM}${TITLE}" \
  '{terminalSequence: $seq}'
```

`.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": ".claude/hooks/notify-stop.sh" }
        ]
      }
    ]
  }
}
```

The same hook works on macOS iTerm2, Windows Terminal, a Linux Ghostty, and `tmux` over `ssh` into a remote dev box. The agent's transcript is unchanged.

## Why it works

Two properties carry the load. The bytes leave the JSON parser and go straight to the terminal Claude Code already owns — race-free, working inside `tmux`/`screen` and on Windows where `/dev/tty` does not exist ([hooks reference](https://code.claude.com/docs/en/hooks)). The sequence also never appears in the model's transcript: a `Stop` notification adds zero tokens to the next turn, unlike stdout output that is treated as `additionalContext` and re-enters the reasoning loop. The OSC mechanism itself is decades-old; the new part is the structured channel — the harness, not the hook, owns the tty write.

## When it backfires

- Headless or CI runs — `claude --headless` has no terminal user; the sequence clutters captured logs and produces no notification. Gate on `$CLAUDE_HEADLESS` or skip on non-interactive sessions.
- Unsupported terminal — bare `xterm`, basic Linux console, or piping to a file emits the sequence but produces no notification, with no acknowledgment to distinguish delivered from silently dropped.
- Notification fatigue — wiring to high-frequency events (`PostToolUse`, `PreCompact`) produces dozens of bells per task. Restrict to events where the human is the next actor.
- DnD and Focus modes are terminal-specific — OSC 9 in iTerm2 routes through Notification Center and honors DnD; OSC 777 in urxvt or Ghostty may not.
- Composed writes are not transactional — a title-then-notification-then-bell sequence interrupted mid-write leaves the title set. Order most important first.
- Regression risk in the path itself — [`claude-code#58909`](https://github.com/anthropics/claude-code/issues/58909) reports `Notification:permission_prompt` stopping during active thinking in 2.1.141. Smoke-test the hook on each minor version.

## Key Takeaways

- `terminalSequence` is a structured hook output field that emits allowlisted terminal escape sequences via the harness's own write path
- The allowlist (OSC 0/1/2, OSC 9, OSC 99, OSC 777, BEL) is a security control — cursor, color, clipboard, and hyperlink sequences are rejected
- The notification never enters the agent's transcript — zero token cost, no re-entry into the reasoning loop
- Restrict to `Stop`, `SubagentStop`, `Notification`, and `StopFailure`; high-frequency events produce fatigue
- Always fail silent: a terminal that does not honor the sequence emits no error and must not block the agent

## Related

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
- [Conditional Hook Execution](conditional-hook-execution.md)
- [Terminal Tool Output Compression](terminal-output-compression.md)

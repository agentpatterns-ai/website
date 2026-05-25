---
title: "PowerShell Tool: Native Windows Shell for Claude Code"
description: "The PowerShell tool (opt-in preview) lets Claude Code run commands via PowerShell on Windows, eliminating Git Bash path translation and enabling native cmdlet access."
tags:
  - claude
  - tool-engineering
aliases:
  - PowerShell tool
  - Windows native shell Claude Code
---

# PowerShell Tool: Native Windows Shell for Claude Code

> Run PowerShell commands natively from Claude Code — no Git Bash path translation, no POSIX shim, direct access to cmdlets and .NET APIs. Rolling out on Windows; opt-in preview on Linux, macOS, and WSL.

The [PowerShell tool](https://code.claude.com/docs/en/tools-reference#powershell-tool), added in Claude Code v2.1.84 (2026-03-26) as an opt-in preview, replaces Git Bash command routing with a direct `pwsh.exe` or `powershell.exe` spawn. Claude Code's default Bash tool assumes a POSIX environment; on Windows this produces path translation errors (`C:\` vs `/c/`), POSIX flags that fail on cmdlets, and encoding mismatches. The PowerShell tool eliminates the shim layer.

The tool is rolling out progressively on Windows and is opt-in on Linux, macOS, and WSL; non-Windows platforms require PowerShell 7+ (`pwsh`) on `PATH`. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

This is a **preview feature** with documented limitations. Read the [Preview Limitations](#preview-limitations) section before enabling.

## Enable the PowerShell Tool

Set the environment variable before launching Claude Code, or add it to `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}
```

On Windows, Claude Code auto-detects `pwsh.exe` (PowerShell 7+) first, falling back to `powershell.exe` (5.1). On Linux, macOS, and WSL, `pwsh` must already be on `PATH`. The Bash tool remains registered alongside the PowerShell tool — Claude does not automatically prefer PowerShell. Ask Claude explicitly to use PowerShell, or configure `defaultShell` (see below). On Windows, set the variable to `0` to opt out of the rollout. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

## Shell Routing Settings

Three settings control where PowerShell is used. They are independent of each other:

| Setting | Scope | Requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`? |
|---------|-------|----------------------------------------------|
| `"defaultShell": "powershell"` in `settings.json` | Interactive `!` commands in the REPL | Yes |
| `"shell": "powershell"` on a hook entry | That hook only | No |
| `shell: powershell` in [skill frontmatter](../../tool-engineering/skill-frontmatter-reference.md) | `!` blocks in that skill | Yes |

Per-hook shell routing (`"shell": "powershell"`) works independently of the tool flag — hooks spawn PowerShell directly. This means you can run PowerShell in hooks without enabling the tool globally. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

The same working-directory reset behavior that applies to Bash applies to PowerShell: `cd` changes persist within the project directory; the shell resets to the project root if you navigate outside it. `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` disables carry-over for both tools. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

## When to Use PowerShell vs Bash-in-WSL

PowerShell-native wins when:

- The codebase targets Windows APIs, the registry, or credential stores that WSL cannot access directly
- The team is Windows-first and eliminating an extra environment layer reduces friction
- You need native `.NET` cmdlets or PowerShell modules without cross-boundary marshalling
- Git Bash path translation is producing incorrect command sequences in agent output

Bash-in-WSL (or native Bash) is the better choice when:

- Auto mode is required — the PowerShell tool does not yet support auto mode
- You are on Windows and need sandboxing — sandboxing is not supported on Windows during preview
- Managed PowerShell profiles contain required modules or org policy — profiles are not loaded by the tool

## Preview Limitations

The following limitations are documented for the current preview release: [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

- Auto mode does not work with the PowerShell tool yet
- PowerShell profiles are not loaded
- On Windows, sandboxing is not supported
- On Windows, Git Bash is still required to start Claude Code
- On Linux, macOS, and WSL, PowerShell 7+ is required

Security hardening was applied in v2.1.89–2.1.90 (2026-04-01), fixing a trailing `&` background-job bypass, an `-ErrorAction Break` debugger hang, an archive-extraction TOCTOU, a parse-fail fallback deny-rule degradation, and PS 5.1 argument-splitting for arguments containing both double-quotes and whitespace. [Source: [Claude Code Changelog](https://code.claude.com/docs/en/changelog)]

## Example

Enable the tool and set `defaultShell` so interactive `!` commands route to PowerShell:

```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  },
  "defaultShell": "powershell"
}
```

With this config, `!` commands in the REPL run through PowerShell, and Claude can use native cmdlets directly. For example, listing running Windows services and exporting to CSV:

```powershell
Get-Service | Where-Object { $_.Name -like 'W*' } | Export-Csv -Path services.csv -NoTypeInformation
```

This cmdlet pipeline has no direct Bash equivalent — `Get-Service` is Windows-native and unavailable in Git Bash. [Source: [Microsoft PowerShell docs — Get-Service](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service)]

## Key Takeaways

- Enable with `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`; auto-detects PowerShell 7+ then 5.1
- The Bash tool stays registered — configure `defaultShell: powershell` or ask Claude explicitly
- Per-hook `"shell": "powershell"` works without the tool flag
- Preview limitations: no auto mode, no profile loading; sandboxing and Git Bash requirement are Windows-only; Linux/macOS/WSL require PowerShell 7+
- Security hardening in v2.1.89–2.1.90 addressed several permission-check and argument-handling issues

## Related

- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
- [Auto Mode](auto-mode.md)
- [Tool Engineering](../../tool-engineering/index.md)

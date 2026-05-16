---
title: "PowerShell Tool: Native Windows Shell for Claude Code"
description: "The PowerShell tool lets Claude Code run commands via PowerShell on Windows, eliminating Git Bash path translation and enabling native cmdlet access."
tags:
  - claude
  - tool-engineering
aliases:
  - PowerShell tool
  - Windows native shell Claude Code
---

# PowerShell Tool: Native Windows Shell for Claude Code

> Run PowerShell commands natively from Claude Code — no Git Bash path translation, no POSIX shim, direct access to cmdlets and .NET APIs. Auto-enabled on Windows without Git Bash; rolling out on Windows with Git Bash; opt-in on Linux, macOS, and WSL.

The [PowerShell tool](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool) replaces Git Bash command routing with a direct `pwsh.exe` or `powershell.exe` spawn. Claude Code's default Bash tool assumes a POSIX environment; on Windows this produces path translation errors (`C:\` vs `/c/`), POSIX flags that fail on cmdlets, and encoding mismatches. The PowerShell tool eliminates the shim layer.

On Windows without Git Bash, the tool is enabled automatically. On Windows with Git Bash installed, it is rolling out progressively. On Linux, macOS, and WSL it is opt-in and requires PowerShell 7+ (`pwsh`) on `PATH`. [Source: [Claude Code Tools Reference](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool)]

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

On Windows, Claude Code auto-detects `pwsh.exe` (PowerShell 7+) first, falling back to `powershell.exe` (5.1). On Linux, macOS, and WSL, `pwsh` must already be on `PATH`. When the tool is enabled, Claude treats PowerShell as the primary shell; the Bash tool remains available for POSIX scripts when Git Bash is installed. On Windows, set the variable to `0` to opt out of the rollout. [Source: [Claude Code Tools Reference](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool)]

## Shell Routing Settings

Three settings control where PowerShell is used. They are independent of each other:

| Setting | Scope | Requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`? |
|---------|-------|----------------------------------------------|
| `"defaultShell": "powershell"` in `settings.json` | Interactive `!` commands in the REPL | Yes |
| `"shell": "powershell"` on a hook entry | That hook only | No |
| `shell: powershell` in [skill frontmatter](../../tool-engineering/skill-frontmatter-reference.md) | `!` blocks in that skill | Yes |

Per-hook shell routing (`"shell": "powershell"`) works independently of the tool flag — hooks spawn PowerShell directly. This means you can run PowerShell in hooks without enabling the tool globally. [Source: [Claude Code Tools Reference](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool)]

The same working-directory reset behavior that applies to Bash applies to PowerShell: `cd` changes persist within the project directory; the shell resets to the project root if you navigate outside it. `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` disables carry-over for both tools. [Source: [Claude Code Tools Reference](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool)]

## When to Use PowerShell vs Bash-in-WSL

PowerShell-native wins when:

- The codebase targets Windows APIs, the registry, or credential stores that WSL cannot access directly
- The team is Windows-first and eliminating an extra environment layer reduces friction
- You need native `.NET` cmdlets or PowerShell modules without cross-boundary marshalling
- Git Bash path translation is producing incorrect command sequences in agent output

Bash-in-WSL (or native Bash) is the better choice when:

- You are on Windows and need sandboxing — sandboxing is not supported on Windows during preview
- Managed PowerShell profiles contain required modules or org policy — profiles are not loaded by the tool

## Preview Limitations

The following limitations are documented for the current preview release: [Source: [Claude Code Tools Reference](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool)]

- PowerShell profiles are not loaded
- On Windows, sandboxing is not supported

PowerShell-tool commands can be auto-approved in permission mode, matching Bash behavior, using rules like `PowerShell(Get-ChildItem *)`. [Source: [Claude Code Tools Reference](https://docs.claude.com/en/docs/claude-code/tools-reference#powershell-tool)]

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

- On Windows without Git Bash the tool is auto-enabled; with Git Bash it is rolling out progressively; on Linux, macOS, and WSL it is opt-in via `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` and requires PowerShell 7+
- When enabled, Claude treats PowerShell as the primary shell; the Bash tool remains available for POSIX scripts when Git Bash is installed
- Per-hook `"shell": "powershell"` works without the tool flag
- Auto-approval works with `PowerShell(...)` rules, matching Bash behavior
- Preview limitations: no profile loading; sandboxing is not supported on Windows

## Related

- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
- [Auto Mode](auto-mode.md)
- [Tool Engineering](../../tool-engineering/index.md)

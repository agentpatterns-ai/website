---
title: "PowerShell Tool: Native Windows Shell for Claude Code"
description: "The PowerShell tool (opt-in preview) lets Claude Code run commands via PowerShell on Windows, eliminating Git Bash path translation and enabling native cmdlet access."
tags:
  - claude
  - tool-engineering
aliases:
  - PowerShell tool
  - Windows native shell Claude Code
applies_to: "claude-code@2.x"
last_reviewed: 2026-08-30
status: current
---

# PowerShell Tool: Native Windows Shell for Claude Code

> Run PowerShell commands natively from Claude Code — no Git Bash translation, direct cmdlet access. Rolling out on Windows; opt-in on Linux, macOS, WSL.

The [PowerShell tool](https://code.claude.com/docs/en/tools-reference#powershell-tool), added in Claude Code v2.1.84 (2026-03-26) as an opt-in preview, replaces Git Bash command routing with a direct `pwsh.exe` or `powershell.exe` spawn. Claude Code's default Bash tool assumes a POSIX environment. On Windows this produces path translation errors (`C:\` vs `/c/`), POSIX flags that fail on cmdlets, and encoding mismatches. The PowerShell tool removes the shim layer.

The tool is rolling out gradually on Windows. It is opt-in on Linux, macOS, and WSL. Non-Windows platforms require PowerShell 7+ (`pwsh`) on `PATH`. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

This is a preview feature with documented limitations. Read the [preview limitations](#preview-limitations) before you turn it on.

## Enable the PowerShell tool

Set the environment variable before launching Claude Code, or add it to `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}
```

On Windows, Claude Code auto-detects `pwsh.exe` (PowerShell 7+) first, then falls back to `powershell.exe` (5.1). On Linux, macOS, and WSL, `pwsh` must already be on `PATH`. When the tool is enabled, Claude treats PowerShell as the primary shell instead of Bash. The Bash tool remains available for POSIX scripts when Git Bash is installed. On Windows, set the variable to `0` to opt out of the rollout. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

## Shell routing settings

Three settings control where PowerShell runs. They work independently of each other:

| Setting | Scope | Requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`? |
|---------|-------|----------------------------------------------|
| `"defaultShell": "powershell"` in `settings.json` | Interactive `!` commands in the REPL | Yes |
| `"shell": "powershell"` on a hook entry | That hook only | No |
| `shell: powershell` in [skill frontmatter](../../tool-engineering/skill-frontmatter-reference.md) | `!` blocks in that skill | Yes |

Per-hook shell routing (`"shell": "powershell"`) works independently of the tool flag, because hooks spawn PowerShell directly. So you can run PowerShell in hooks without turning the tool on globally. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

PowerShell follows the same working-directory reset behavior as Bash. `cd` changes persist within the project directory. The shell resets to the project root if you move outside it. `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` turns off carry-over for both tools. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

## When to use PowerShell vs Bash-in-WSL

PowerShell-native wins when:

- The codebase targets Windows APIs, the registry, or credential stores that WSL cannot reach directly
- The team is Windows-first and removing an extra environment layer reduces friction
- You need native `.NET` cmdlets or PowerShell modules without cross-boundary marshalling
- Git Bash path translation produces incorrect command sequences in agent output

Bash-in-WSL (or native Bash) is the better choice when:

- You need sandboxing on Windows — the preview does not support it yet
- Managed PowerShell profiles carry required modules or org policy — the tool does not load profiles

## Preview limitations

The current preview release documents the following limitations: [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference#powershell-tool)]

- The tool does not load PowerShell profiles
- The Windows preview does not support sandboxing

Security hardening in v2.1.89–2.1.90 (2026-04-01) fixed a trailing `&` background-job bypass, an `-ErrorAction Break` debugger hang, an archive-extraction TOCTOU, a parse-fail fallback deny-rule degradation, and PS 5.1 argument-splitting for arguments that contain both double-quotes and whitespace. [Source: [Claude Code Changelog](https://code.claude.com/docs/en/changelog)]

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

- Enabling the flag needs `pwsh` on `PATH` for Linux, macOS, and WSL; Windows falls back to `powershell.exe` 5.1 automatically when PowerShell 7+ is missing
- Once enabled, PowerShell becomes the primary shell automatically — no need to ask Claude to prefer it; `defaultShell` only scopes the REPL's `!` commands, not tool calls
- A hook's own `"shell": "powershell"` entry runs PowerShell even with the tool disabled, because hooks spawn the shell directly
- The two current preview gaps — no profile loading, no Windows sandboxing — mean an org-managed PowerShell setup may still need Bash-in-WSL
- Versions before v2.1.89 carried a trailing `&` background-job permission bypass; upgrade before relying on the tool for gated commands

## Related

- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
- [Auto Mode](auto-mode.md)
- [Tool Engineering](../../tool-engineering/index.md)

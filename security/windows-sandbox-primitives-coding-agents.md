---
title: "Windows Sandboxing for Coding Agents"
description: "AppContainer, Windows Sandbox, and MIC each fail a coding-agent requirement; the working pattern composes synthetic SIDs with write-restricted tokens, or moves to WSL2."
tags:
  - security
  - tool-agnostic
  - agent-design
---

# Windows Sandboxing for Coding Agents

> A coding agent on Windows needs open-ended binary execution, host workspace read-write, no admin elevation, and policy that propagates to spawned child processes. AppContainer, Windows Sandbox, and Mandatory Integrity Control each break one of those four; the working pattern is composing synthetic SIDs with write-restricted tokens, or moving the agent into WSL2.

## Core Concept

The Windows sandbox question for a coding agent is not "pick the OS primitive" — no single primitive fits, and the working pattern is composing lower-level pieces. OpenAI's [Codex Windows sandbox post](https://openai.com/index/building-codex-windows-sandbox/) (May 2026) walks through this evaluation and ships a hand-composed sandbox built from synthetic security identifiers (SIDs) and write-restricted tokens. Each rejected primitive is still the right tool for the workload it was designed for; this page is a selection guide for platform engineers building a sandbox for a Codex-class harness, Claude Code, or an internal agent.

## The Four Requirements

A coding-agent sandbox on Windows must satisfy four conditions:

1. **Open-ended binary execution** — the agent picks the binary at runtime (Git, `node`, `pip`, MSBuild, arbitrary user scripts); the set is not enumerable up front.
2. **Host workspace read-write** — the agent edits the user's actual checkout. Editors, debuggers, and CI consume that path live ([Codex Windows post](https://openai.com/index/building-codex-windows-sandbox/)).
3. **No admin elevation** — setup and per-task launch must run as the standard developer user.
4. **Policy propagates down the process tree** — when the agent spawns `git.exe`, the child must inherit the same write and network restrictions.

Each Windows primitive below fails one of these.

## Why Each Primitive Fails

### AppContainer

AppContainer is "a capability-based isolation model built for apps that know, up front, exactly what they need to access" ([Codex Windows post](https://openai.com/index/building-codex-windows-sandbox/), [Microsoft Learn — AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)). The declared capability list must enumerate the resources the process will touch — right for a packaged Win32 app with a fixed feature set, wrong for an agent that picks binaries at runtime.

A second AppContainer limitation hits even teams willing to declare broad capabilities: "Windows doesn't allow matching a firewall rule to the non-principal identity of a restricted token" ([OpenAI post, mirrored on aetos.ai](https://aetos.ai/posts/e6b942df5f48f364)). A firewall rule on `codex.exe` does not apply to the `git.exe` or `python.exe` child processes the agent spawns. This is exactly why OpenAI's final design creates dedicated local users (`CodexSandboxOffline` / `CodexSandboxOnline`) as the firewall-matchable principal.

**Fails requirement**: 1 (open-ended binaries) and 4 (policy propagation).

### Windows Sandbox

Windows Sandbox is a Hyper-V-backed lightweight disposable VM. Pure-isolation strength is the highest on this list — hardware virtualization beats every in-process mechanism. The failure mode is workflow fit: "Codex needs to act directly on the user's actual checkout, tools, and environment, not inside a separate throwaway desktop that would need setup and host/guest bridging" ([Codex Windows post](https://openai.com/index/building-codex-windows-sandbox/)). Mapped folders exist ([Windows Sandbox configuration](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)) but every per-tool-call launch pays VM cold-start, and host-side editors and CI keep the source-of-truth checkout on the host filesystem.

A secondary blocker: Windows Sandbox requires Hyper-V, which is unavailable on Windows Home ([Windows Sandbox FAQ](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-faq)).

**Fails requirement**: 2 (host workspace); SKU-limited.

### Mandatory Integrity Control (MIC)

MIC assigns integrity levels (Low, Medium, High, System) to processes and objects, blocking lower-integrity processes from writing to higher-integrity objects regardless of the DACL ([Microsoft Learn — Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)). The mechanism that makes MIC work — `SYSTEM_MANDATORY_LABEL_ACE` entries in each object's SACL — is also what makes it wrong for a coding agent.

To confine the agent at Low integrity you must label every workspace file's SACL with the Low integrity ACE. Those labels persist on disk and apply to *every* Low-integrity process on the machine — Protected Mode browsers, sandboxed renderers, other agents — not just this one. The boundary leaks across processes through the labelled filesystem.

**Fails requirement**: 2 (clean host workspace) and 4 (the label is a global host fact, not a per-process restriction).

## The Composition That Works

OpenAI's shipped sandbox uses three Windows primitives Microsoft never bundled as a sandbox SKU ([Codex Windows post](https://openai.com/index/building-codex-windows-sandbox/)):

- **A synthetic SID** (`sandbox-write`) created via Windows' SID-allocation APIs, granted write/execute/delete on workspace paths via standard ACL entries
- **A write-restricted token** with restricted SID list `[Everyone, Logon, sandbox-write]`. Write-restricted tokens enforce a two-check rule: a write succeeds only if both the normal user identity *and* a SID from the restricted list are granted access ([Microsoft Learn — Restricted Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens))
- **Dedicated local users** (`CodexSandboxOffline`, `CodexSandboxOnline`) that serve as the token *principal*, giving Windows firewall a stable identity to match egress rules against

The agent launches every command under this token. Writes outside the labelled paths fail the second check; child processes inherit the token; the firewall rule binds to the principal user, so spawned `git.exe` and `python.exe` are subject to the same network policy.

## Why It Works

Windows' write-restricted-token semantic is precisely the AND-gate a coding agent needs to scope writes without declaring capabilities up front: the user SID grants the baseline, the restricted SID list narrows it, and the synthetic SID on the workspace paths is the only credential that survives the narrowing ([Restricted Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)). The agent never enumerates which binaries it will run — every spawned child inherits the token and meets the same gate. The firewall-scoping problem is solved orthogonally by making the token's *principal* a dedicated local user, which firewall rules *can* match. AppContainer, Windows Sandbox, and MIC each refuse one of those three moves; only the lower-level SID and token APIs let you make all three.

## When This Backfires

The "compose primitives" recommendation flips depending on workload and deployment shape:

- **The agent is a computer-use agent, not a coding agent.** A GUI-automation agent driving Edge, Excel, or Outlook with no host workspace requirement is exactly what Windows Sandbox was built for ([cua.ai — Windows Sandbox for computer-use agents](https://cua.ai/blog/windows-sandbox)). The disposable-desktop model is the right tool there; do not reinvent it with restricted tokens.
- **The deployment target is Windows Home.** Hyper-V is unavailable on Home, so Windows Sandbox is off the table regardless; the SID/token composition still works, though, because it uses only standard Win32 security APIs ([Windows Sandbox FAQ](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-faq)).
- **The team already runs WSL2 as the primary dev environment.** OpenAI itself documents WSL2 as the recommended mode where available — Landlock, seccomp, and bubblewrap inside the WSL2 VM produce strictly stronger isolation than restricted-token composition ([Codex CLI on Windows: Native Sandbox, WSL Integration](https://codex.danielvaughan.com/2026/04/01/codex-cli-windows-native-sandbox-wsl/), [joecuevas.com — How I Sandbox AI Coding Agents on Windows 11 with WSL2](https://joecuevas.com/posts/codex-wsl-sandbox/)). The cost is filesystem drift: native Windows editors, debuggers, and CI running against host-filesystem checkouts diverge from the WSL2 view, and small-file I/O across the boundary is slow.
- **The workspace lives on a network share, mapped drive, or OneDrive-synced path.** Both ACL Deny ACEs and SACL labels interact badly with remote replication. OpenAI's own Codex CLI has already shipped a real instance: orphan-SID Deny ACEs from sandbox setup produced `.git/FETCH_HEAD: Permission denied` ([openai/codex#21304](https://github.com/openai/codex/issues/21304)). Composing primitives Microsoft never tested together carries this category of cost.
- **Read access matters as much as write.** The write-restricted token confines *writes*; if the threat model includes the agent reading SSH keys or other sensitive files, the model is incomplete. Combine with the [dual-boundary sandboxing](dual-boundary-sandboxing.md) read/write/network model rather than treating restricted-token writes as the whole sandbox.

## Selection Rubric

| Workload | Recommended | Why |
|----------|-------------|-----|
| Coding agent on Windows Pro+, host checkout | Composed SIDs + write-restricted tokens + dedicated principal user | Only path that satisfies all four requirements without leaving native Windows |
| Coding agent on Windows + WSL2 available | WSL2 with Landlock/bubblewrap | Strictly stronger isolation; accept filesystem-drift cost |
| Coding agent on Windows Home | Composed SIDs + write-restricted tokens | No Hyper-V; AppContainer/Sandbox unavailable |
| Computer-use agent (GUI automation, no host workspace) | Windows Sandbox | Disposable desktop is the right shape |
| Packaged Win32 app with declared capabilities | AppContainer | The workload AppContainer was designed for |
| Protect host OS from low-integrity process | MIC | The workload MIC was designed for |

## Key Takeaways

- A coding agent on Windows has four hard requirements — open-ended binaries, host workspace, no admin, child-process propagation — and no single Windows primitive satisfies all four.
- AppContainer fails on capability enumeration and on firewall rules not following spawned children; Windows Sandbox breaks host-workspace integration and is unavailable on Home; MIC mutates host filesystem SACLs and leaks the boundary to other Low-integrity processes.
- OpenAI's working pattern composes a synthetic SID, a write-restricted token, and a dedicated local user as the principal — the SID gates writes via the token's AND-check, the principal gives firewall rules something to match.
- WSL2 is the strictly-stronger fallback when Linux-grade isolation matters more than native Windows filesystem fidelity; the trade is filesystem drift between Windows-native tooling and the WSL2 view.
- The same primitive can be the right answer for a different workload — Windows Sandbox is correct for computer-use agents, AppContainer is correct for packaged Win32 apps. Match primitive to workload shape, not to "Windows = use the Windows sandbox."

## Related

- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md)
- [Dual-Boundary Sandboxing for Secure Agent Execution](dual-boundary-sandboxing.md)
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md)
- [Selective Network Access in Agent Sandboxes: The `allowNetwork` Pattern](selective-network-sandbox-mode.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md)

---
title: "Windows Sandboxing for Coding Agents"
term: "Windows Sandboxing"
description: "AppContainer, Windows Sandbox, and MIC each fail a coding-agent requirement; the working pattern composes synthetic SIDs with write-restricted tokens, or moves to WSL2."
tags:
  - security
  - tool-agnostic
  - agent-design
last_reviewed: 2026-06-12
maturity: established
---

# Windows Sandboxing for Coding Agents

> No single Windows primitive sandboxes a coding agent cleanly; the working pattern composes a synthetic SID, write-restricted token, and dedicated principal user, or uses WSL2.

## The Four Requirements

OpenAI's [Codex Windows sandbox post](https://openai.com/index/building-codex-windows-sandbox/) (May 2026) lists four conditions a coding-agent sandbox on Windows must satisfy:

1. **Open-ended binary execution** — the agent picks binaries at runtime (Git, `node`, `pip`, MSBuild, user scripts).
2. **Host workspace read-write** — the agent edits the user's actual checkout; editors, debuggers, and CI consume it live.
3. **No admin elevation** — setup and per-task launch run as the standard developer user.
4. **Policy propagates down the process tree** — [spawned children inherit](subprocess-pid-namespace-sandboxing.md) the same write and network restrictions.

No single Windows primitive satisfies all four — though each is still right for the workload it was designed for.

## Why Each Primitive Fails

### AppContainer

AppContainer is "a capability-based isolation model built for apps that know, up front, exactly what they need to access" ([Codex post](https://openai.com/index/building-codex-windows-sandbox/), [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)) — wrong for an agent picking binaries at runtime. And "Windows doesn't allow matching a firewall rule to the non-principal identity of a restricted token" ([aetos.ai mirror](https://aetos.ai/posts/e6b942df5f48f364)): a rule on `codex.exe` doesn't follow `git.exe` children — hence OpenAI's dedicated local users as the firewall-matchable principal. **Fails**: 1 and 4.

### Windows Sandbox

A Hyper-V-backed disposable VM with the highest pure-isolation strength here. The failure is workflow fit: "Codex needs to act directly on the user's actual checkout, tools, and environment, not inside a separate throwaway desktop" ([Codex post](https://openai.com/index/building-codex-windows-sandbox/)). Mapped folders exist ([config docs](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)) but each launch pays VM cold-start, and Hyper-V is absent on Windows Home ([FAQ](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-faq)). **Fails**: 2; SKU-limited.

### Mandatory Integrity Control (MIC)

MIC blocks lower-integrity writes regardless of the DACL ([Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)). Confining the agent at Low integrity means labelling every workspace file's SACL with `SYSTEM_MANDATORY_LABEL_ACE` — labels that persist on disk and apply to *every* Low-integrity process (Protected Mode browsers, sandboxed renderers, other agents), leaking the boundary through the filesystem. **Fails**: 2 and 4.

## The Composition That Works

OpenAI's shipped sandbox uses three Windows primitives Microsoft never bundled as a sandbox SKU ([Codex post](https://openai.com/index/building-codex-windows-sandbox/)):

- **A synthetic SID** (`sandbox-write`) granted write/execute/delete on workspace paths via standard ACL entries.
- **A write-restricted token** with restricted SID list `[Everyone, Logon, sandbox-write]`. Writes succeed only if both the user identity *and* a SID from the restricted list are granted access ([Restricted Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)).
- **Dedicated local users** (`CodexSandboxOffline`, `CodexSandboxOnline`) as the token *principal*, giving Windows firewall a stable identity to match.

## Why It Works

The write-restricted token is an AND-gate: the user SID grants the baseline, the restricted SID list narrows it, and the synthetic SID on workspace paths is the only surviving credential. Children inherit the token, so the agent never enumerates its binaries; firewall scoping falls to the principal user.

## Where the AND-Gate Leaks

The AND-gate is not airtight. Because `Everyone` sits in the restricted SID list, the restricted-side check passes for any directory that *already* grants `Everyone` write access, so a broadly-permissioned workspace silently weakens the boundary ([Codex post](https://openai.com/index/building-codex-windows-sandbox/)). The token also confines only the filesystem: post-launch research describes Configuration-Based Sandbox Escape, where writing the CLI's own config from inside the sandbox turns startup into an escape primitive ([Cymulate, 2026](https://cymulate.com/blog/the-race-to-ship-ai-tools-left-security-behind-part-1-sandbox-escape/)). Treat it as write-scoping, not containment.

## When This Backfires

- **Computer-use agent, not coding agent.** GUI automation with no host workspace is what Windows Sandbox was built for ([cua.ai](https://cua.ai/blog/windows-sandbox)).
- **WSL2 is the primary dev environment.** OpenAI recommends WSL2 where available — Landlock, seccomp, and bubblewrap isolate more strongly than restricted-token composition ([Codex CLI on Windows](https://codex.danielvaughan.com/2026/04/01/codex-cli-windows-native-sandbox-wsl/), [joecuevas.com](https://joecuevas.com/posts/codex-wsl-sandbox/)). The cost is filesystem drift and slow small-file I/O.
- **Workspace on a network share, mapped drive, or OneDrive path.** ACL Deny ACEs and SACL labels interact badly with remote replication; Codex CLI shipped a real instance where orphan-SID Deny ACEs produced `.git/FETCH_HEAD: Permission denied` ([openai/codex#21304](https://github.com/openai/codex/issues/21304)).
- **Read access matters as much as write.** The token confines *writes* only; combine with [dual-boundary sandboxing](dual-boundary-sandboxing.md) for read/network threats.

## Selection Rubric

| Workload | Recommended |
|----------|-------------|
| Coding agent on Windows Pro+, host checkout | Composed SIDs + write-restricted tokens + dedicated principal user |
| Coding agent with WSL2 available | WSL2 with Landlock/bubblewrap (stronger isolation; filesystem drift) |
| Coding agent on Windows Home | Composed SIDs + write-restricted tokens (no Hyper-V) |
| Computer-use agent (GUI, no host workspace) | Windows Sandbox |
| Packaged Win32 app with declared capabilities | AppContainer |
| Protect host OS from low-integrity process | MIC |

## Key Takeaways

- A coding agent on Windows has four hard requirements — open-ended binaries, host workspace, no admin, child-process propagation — that no single primitive satisfies.
- AppContainer fails on capability enumeration and firewall rules not following children; Windows Sandbox breaks host-workspace integration and is absent on Home; MIC mutates host SACLs and leaks the boundary to other Low-integrity processes.
- OpenAI composes a synthetic SID, a write-restricted token, and a dedicated local user as the principal — the SID gates writes via the token's AND-check, the principal gives firewall rules something to match.
- WSL2 is the strictly-stronger fallback when Linux-grade isolation matters more than native filesystem fidelity; the trade is filesystem drift.
- Same primitive, different workload: Windows Sandbox fits computer-use agents, AppContainer fits packaged Win32 apps. Match primitive to workload shape.

## Related

- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md)
- [Dual-Boundary Sandboxing for Secure Agent Execution](dual-boundary-sandboxing.md)
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md)
- [Selective Network Access in Agent Sandboxes: The `allowNetwork` Pattern](selective-network-sandbox-mode.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md)

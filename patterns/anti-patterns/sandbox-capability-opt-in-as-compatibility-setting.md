---
title: "Sandbox Capability Opt-In as a Compatibility Setting"
term: "Sandbox Capability Opt-In"
description: "A sandbox key that lets named tools create user namespaces grants the same bypass to every sandboxed command, so it belongs in the same review as the sandbox itself."
aliases:
  - sandbox capability opt-in
  - allowNestedUserNamespaces setting
  - containment opt-in for one tool
tags:
  - anti-pattern
  - security
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-28
status: current
maturity: emerging
---

# Sandbox Capability Opt-In as a Compatibility Setting

> A sandbox setting added so named tools can run grants the same bypass to every sandboxed command, so enabling it is a containment decision.

Claude Code 2.1.305 added `sandbox.allowNestedUserNamespaces` "so sandboxed commands on Linux can create user namespaces (Chromium, rootless podman); this lets them get around the sandbox's file protections" ([changelog 2.1.305](https://code.claude.com/docs/en/changelog#2-1-305), October 20, 2026). The justification names two tools. The grant names sandboxed commands.

## What the grant covers

The key is honored from `~/.claude/settings.json`, `--settings`, or managed settings. A repository's `.claude/settings.json` or `.claude/settings.local.json` cannot turn it on, and a session with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` ignores a `true` from every source ([settings reference](https://code.claude.com/docs/en/settings-reference#sandbox-allownestedusernamespaces)). It is Linux and WSL2 only, and defaults to `false`. A `false` counts from any file under settings precedence.

Setting the key to `true` means "you turn off a security boundary: code from a sandboxed command can end up running outside the sandbox", and "In auto-allow mode, that command can run without a permission prompt" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)).

## Why it works

A process "that creates a new user namespace using unshare(2) or joins an existing user namespace using setns(2) gains a full set of capabilities in that namespace", and "Holding CAP_SYS_ADMIN within the user namespace that owns a process's mount namespace allows that process to create bind mounts" ([`user_namespaces(7)`](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)). On Linux, Claude Code relies on bubblewrap, "the unprivileged sandboxing tool that enforces filesystem isolation" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)).

Canonical restricts the same kernel feature on the host, and scopes its exception per application rather than globally. Unprivileged user namespaces "have been repeatedly used to exploit kernel vulnerabilities", and the AppArmor restriction "reduces the attack surface presented by restricting the use of unprivileged user namespaces to applications that have a legitimate use for them" ([Understanding AppArmor User Namespace Restriction](https://discourse.ubuntu.com/t/understanding-apparmor-user-namespace-restriction/58007)).

## When this backfires

- An agent driving Chromium against third-party sites. The documented alternative is starting the browser with `--no-sandbox`, where "the browser runs web content without its own sandbox" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). Compare the browser's exposure to untrusted web content with the commands' access to local files.
- Rootless Podman or Buildah. The key alone does not fix them, because "the sandbox stops them in other ways too" ([settings reference](https://code.claude.com/docs/en/settings-reference#sandbox-allownestedusernamespaces)). Granting it buys the boundary loss and a still-broken build.

Anthropic frames all three documented fixes the same way: "Each fix works for the tools it names and gives up some isolation". The per-tool route, `sandbox.excludedCommands`, is not uniformly narrower. A matching command runs "outside the sandbox, which means no filesystem restrictions and no network proxy" ([excluded commands](https://code.claude.com/docs/en/sandboxing#run-commands-outside-the-sandbox-with-excludedcommands)). A command beginning with `unshare` stays sandboxed whatever pattern you list ([Chromium and rootless Podman troubleshooting](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)).

## Example

These fragments illustrate the documented choices in user settings, with environment-scrub mode off. They are alternatives, not a claim that exclusions preserve containment.

**Before — one tool's compatibility fix, applied to every sandboxed command:**

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "allowNestedUserNamespaces": true
  }
}
```

Chromium's own sandbox survives, and so does every other sandboxed command's route out, with no permission prompt in front of it.

**After — matching Podman commands run outside the sandbox:**

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "allowNestedUserNamespaces": false,
    "excludedCommands": ["podman *"]
  }
}
```

Anthropic documents `podman *` as an exclusion for rootless Podman ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). Matching commands run outside the sandbox with full access and follow the [normal permission flow](https://code.claude.com/docs/en/sandboxing#run-commands-outside-the-sandbox-with-excludedcommands). Other commands retain the configured sandbox restrictions. If you exclude a test script instead, Claude can edit it before running it; the exclusion does not make that script a trusted boundary.

## Key Takeaways

- Compare a sandbox key's justification against its scope before reading it as a compatibility fix; two named tools and "sandboxed commands" are different grants.
- `sandbox.allowNestedUserNamespaces` is user or managed scope only, Linux and WSL2 only, and a `true` is ignored when `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`.
- Anthropic names the cost in the changelog entry and the docs.
- The per-command alternative trades isolation too, so record which boundary you chose to lose rather than treating one option as the safe default.

## Related

- [Subprocess PID Namespace Sandboxing in Claude Code](../../security/subprocess-pid-namespace-sandboxing.md) — the Linux isolation layers this key weakens
- [Scope Demotion for Repository-Committed Settings](../../security/repo-committed-settings-scope-demotion.md) — why a repository cannot set this key to `true`
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](../../security/dual-boundary-sandboxing.md) — the filesystem half is the boundary at stake
- [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md) — the adjacent error of trusting a boundary that was never enforcing one
- [Scoped-Looking Permission Grants](scoped-looking-permission-grants.md) — a grant whose syntax hides how far it reaches

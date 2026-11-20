---
title: "Host-Environment Agent Sandboxes: What the Codex Defaults Leave Open"
description: "Codex sandboxes commands in your own environment. Its default profile allows writes that run later; deny globs and proxy DNS lookups have stated limits."
tags:
  - security
  - agent-design
  - tool-agnostic
last_reviewed: 2026-11-20
maturity: emerging
---

# Host-Environment Agent Sandboxes: What the Codex Defaults Leave Open

> An agent sandbox that shares your environment does not cover what that environment runs later, such as an editor formatter on save.

OpenAI's Codex runs commands under OS-level sandboxing inside the user's existing environment, not in a VM or container ([Inside the Codex sandbox](https://openai.com/index/inside-the-codex-sandbox), Michael Bolin, November 18, 2026). The post describes one write its default profile allows that could execute later, outside the sandbox. It also states limits on deny globs and DNS lookups.

## What the default profile covers

The post describes the built-in `:workspace` profile with a Git repository as the workspace root.

- Writes. The profile allows writes within the workspace and keeps directories such as `.git` and `.codex` read-only. The post says this stops direct changes to `.codex/config.toml` or Git hooks under `.git/hooks`.
- Reads. The profile allows broad reads, "subject to the user's existing OS permissions". The cost: "sensitive files elsewhere on the machine may also remain readable (such as config files containing API keys)."
- Network. The profile turns it off. That blocks direct uploads, and it also blocks "downloading dependencies, which require additional access".

The [Codex docs](https://developers.openai.com/codex/agent-approvals-security) describe the default `workspace-write` policy with the same four protected paths (`.git`, `.agents`, `.codex`, `.aws`). For the ChatGPT desktop app, the Codex CLI, and the IDE extension, they say network access stays off in that mode unless you set `network_access = true` under `[sandbox_workspace_write]`. The post configures profiles through `default_permissions`, and the [configuration reference](https://developers.openai.com/codex/config-reference) says not to combine that key with `sandbox_mode` or `[sandbox_workspace_write]`. Take key names from the docs.

## What the profile does not see

### A write that runs later

The post says "harmful actions are still possible". Its example is an agent that could inject malicious code into a locally installed package such as `node_modules/prettier`:

> Such a change might not appear in git status because node_modules is often ignored by Git. If the user's editor runs that copy of Prettier on save, simply saving a file could execute the malicious code outside the Codex sandbox.

That path is not among the four the default profile lists as read-only. The post gives this case as the reason for its defense-in-depth approach.

Docker's sbx runs the agent in a VM and can share the workspace with the host as a read-write mount. Its [isolation page](https://docs.docker.com/ai/sandboxes/security/isolation/) lists workspace files, some of which "execute code when you trigger normal development actions — committing, pushing, building, or opening the project in an IDE". It says Git hooks "don't appear in git diff output" and advises: "Treat sandbox-modified workspace files the same way you would treat a pull request from an untrusted contributor".

### Matches created after launch

On Linux, Codex expands deny globs to concrete paths before launching each command. The post adds: "New matching paths are not automatically added to that command's sandbox restrictions." On Windows, the MXC-based sandbox takes concrete deny paths only, and the post makes the same point: "New paths that match the glob are not automatically added while the command is running." The post makes no such statement for macOS.

The configuration reference sets the maximum depth for expanding deny-read globs with `permissions.<name>.filesystem.glob_scan_max_depth`, on "platforms that snapshot matches before sandbox startup". On Linux and in the MXC-based Windows sandbox, a glob such as `**/*.env` covers the matches that exist when each command starts.

### The DNS lookup

With the network proxy on, the post says "even a DNS lookup can leak information encoded in a hostname". The proxy therefore "resolves the requested hostname only after determining that it is allowed or approved". The post adds that "broad wildcard rules or access to DNS services can still permit DNS-based exfiltration".

Domain rules need the proxy to be running. A comment in the post's example says that if neither local config nor managed requirements enable the proxy, "this profile allows direct network access; domain rules are not enforced". The configuration reference calls `features.network_proxy` "experimental; off by default".

The [Codex docs](https://developers.openai.com/codex/agent-approvals-security) describe a different DNS check, for hostnames that resolve to non-public addresses. They say it "reduces DNS rebinding risk, but it does not eliminate it" and advise: "If hostile DNS is in scope, enforce egress controls at a lower layer too."

## Why the sandbox runs in the user's environment

The post gives two reasons. Reproducing a laptop environment in a Docker container "can take work", and "some workflows still depend on tools that run on the host". Its iOS example adds that a Docker-based workflow could delegate builds to the Mac host, but those operations "would execute outside the container's sandbox and would need their own restrictions".

## When this backfires

- Work on a copy. In Docker's clone mode the agent "never works directly against your host repository", so a review of Git-ignored directories has less to find. Docker says clone mode "protects your host repository from modification, not from inspection", and files such as `.env` stay readable.
- Tight defaults. Blocking network access blocks downloading dependencies, which "require additional access". The post's `require_escalated` option requests execution outside the sandbox, and where policy permits full sandbox escalation and it is approved, the docs say that execution "can bypass the command proxy". The [governance triad](sandbox-approvals-auto-review-triad.md) covers the approval side.
- A vendor describing its own design. The post reports no incident counts or measurements for these defaults. It supports what Codex does and why, and leaves open how well a profile holds.

## Example

The post's `dev` profile adds editor and dev-container config to the read-only list and denies `.env` files and a `secrets` path. This is an excerpt, with the description and the `~/build-cache` write grant left out:

```toml
default_permissions = "dev"

[permissions.dev]
extends = ":workspace"

[permissions.dev.filesystem.":workspace_roots"]
".devcontainer" = "read"
".vscode" = "read"
"**/*.env" = "deny"
"secrets" = "deny"
```

The post tests the profile with `codex sandbox`. The command tries to write a VS Code setting that points Prettier at `./node_modules/evil-prettier` and turns on format on save:

```bash
codex sandbox --permission-profile dev -- \
  bash -c 'cat > .vscode/settings.json' <<'JSON'
{
  "prettier.prettierPath": "./node_modules/evil-prettier",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  }
}
JSON
```

With `.vscode` already present, the post says the write fails on macOS with `bash: .vscode/settings.json: Operation not permitted`. The test covers the settings file. The post shows no profile entry for writes under `node_modules` itself.

## Key Takeaways

- Add editor and dev-container config to a profile's read-only entries, as the post's `dev` profile does with `.vscode` and `.devcontainer`, then run `codex sandbox` against the profile before relying on it.
- After an agent session, inspect Git-ignored directories that your tools run code from. The post says a change in `node_modules` "might not appear in git status", because Git often ignores it.
- On Linux and in the MXC-based Windows sandbox, treat a deny glob as the list of matches present when the command starts.
- Confirm the network proxy is running before relying on domain rules, and put egress controls below it if hostile DNS is in scope.

## Related

- [Sandbox + Approvals + Auto-Review Governance Triad](sandbox-approvals-auto-review-triad.md) — the approval layer for requests that leave the sandbox
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md) — the two boundaries a profile sets
- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md) — choosing the runtime family
- [Docker sbx Adoption for Coding Agents](docker-sbx-adoption.md) — the workspace-mount leak surface in a microVM design
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — gating writes at the write site
- [Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot](hostname-allowlist-tls-blind-spot.md) — what a hostname allowlist does not see
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — domain rules at the organization level
- [Windows Sandboxing for Coding Agents](windows-sandbox-primitives-coding-agents.md) — the Windows primitives behind the Windows case

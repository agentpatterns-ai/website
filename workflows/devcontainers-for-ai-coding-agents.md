---
title: "Dev Containers for AI Coding Agents: Claude Code vs Copilot CLI"
description: "Compare the two official devcontainer paths for AI coding agents — Claude Code's reference container with an egress-allowlisting firewall and Copilot CLI's install-only Feature plus Codespaces inclusion."
tags:
  - workflows
  - agent-design
  - tool-agnostic
term: "Dev Containers for AI Coding Agents"
aliases:
  - devcontainer for coding agent
  - dev container for AI agent
  - .devcontainer for coding agent
last_reviewed: 2026-06-19
maturity: adopted
---

# Dev Containers for AI Coding Agents: Claude Code vs Copilot CLI

> Both vendors ship official devcontainer paths but they solve different problems — Claude Code delivers isolation, Copilot CLI delivers installation.

A `.devcontainer/` gives a coding agent a reproducible, pre-provisioned workspace, and both major CLIs now ship official-but-different support. Claude Code publishes a [full reference configuration](https://code.claude.com/docs/en/devcontainer) — Dockerfile, `devcontainer.json`, and an `init-firewall.sh` that allowlists outbound network traffic — designed so that passing `--dangerously-skip-permissions` inside the box is defensible. Copilot CLI publishes a [devcontainer Feature](https://github.com/devcontainers/features/tree/main/src/copilot-cli) that installs the binary into any base image, and is preinstalled in the [default GitHub Codespaces image](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/). The first gives you isolation. The second gives you availability. Knowing which is which is what lets you decide whether relaxed permissions inside the container is actually defensible.

## The two official shapes

| Dimension | Claude Code reference container | Copilot CLI devcontainer Feature |
|---|---|---|
| OCI reference | Repo `anthropics/claude-code` ships a full `.devcontainer/`; the lightweight install-only Feature is `ghcr.io/anthropics/devcontainer-features/claude-code:1` ([docs](https://code.claude.com/docs/en/devcontainer)) | `ghcr.io/devcontainers/features/copilot-cli:1` ([devcontainers/features](https://github.com/devcontainers/features/tree/main/src/copilot-cli)) |
| What it provides | Base image, dev tools, `init-firewall.sh`, persistent volume mounts, managed-settings hook | Installs `@github/copilot`; one `version` option |
| Egress firewall | Yes — iptables default DROP + curated ipset ([init-firewall.sh](https://raw.githubusercontent.com/anthropics/claude-code/main/.devcontainer/init-firewall.sh)) | No |
| Required capabilities | `NET_ADMIN`, `NET_RAW` ([devcontainer.json](https://raw.githubusercontent.com/anthropics/claude-code/main/.devcontainer/devcontainer.json)) | None |
| Policy delivery | `/etc/claude-code/managed-settings.json` copied via Dockerfile, plus `containerEnv` ([docs](https://code.claude.com/docs/en/devcontainer)) | Not in scope — Feature installs the binary only |
| Pre-installed in default Codespaces image | No — opt in via the Feature | Yes ([GitHub Changelog, Feb 2026](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)) |
| Stated isolation contract | "Substantial protections" but explicitly not exfiltration-proof ([docs](https://code.claude.com/docs/en/devcontainer)) | None |

The Claude Code path also exposes a lighter shape — `ghcr.io/anthropics/devcontainer-features/claude-code:1` is the install-only Feature, symmetric to Copilot's. The reference container is "a working example rather than a maintained base image" ([Claude Code devcontainer docs](https://code.claude.com/docs/en/devcontainer)) — the asymmetry above is between the Claude Code reference container and the Copilot CLI Feature, which are the two officially-recommended shapes each vendor steers users toward.

## The egress-allowlist firewall

`init-firewall.sh` is what makes Claude Code's relaxed-permissions claim load-bearing. The script sets `iptables -P INPUT/OUTPUT/FORWARD DROP` and then allowlists only what the agent and its build toolchain need: GitHub web, API, and Git CIDR ranges pulled from `api.github.com/meta` and aggregated into an ipset; `registry.npmjs.org`; `api.anthropic.com` and `statsig.anthropic.com`; `sentry.io` and `statsig.com`; the VS Code marketplace and updater hosts; plus localhost, DNS, SSH, and the host subnet ([init-firewall.sh](https://raw.githubusercontent.com/anthropics/claude-code/main/.devcontainer/init-firewall.sh)). The script ends with two verification curls — `https://example.com` must fail, `https://api.github.com/zen` must succeed — so the firewall is self-tested at startup.

Running `iptables` inside the container needs extra Linux capabilities, which is why `devcontainer.json` adds `--cap-add=NET_ADMIN --cap-add=NET_RAW` via `runArgs` ([devcontainer.json](https://raw.githubusercontent.com/anthropics/claude-code/main/.devcontainer/devcontainer.json)). The non-root `node` user has passwordless sudo for only `/usr/local/bin/init-firewall.sh` ([Dockerfile](https://raw.githubusercontent.com/anthropics/claude-code/main/.devcontainer/Dockerfile)) — the agent cannot flush the firewall mid-session.

This is the configuration Anthropic's docs cite when justifying `--dangerously-skip-permissions`: "Because the container runs Claude Code as a non-root user and confines command execution to the container, you can pass `--dangerously-skip-permissions` for unattended operation" ([Claude Code devcontainer docs](https://code.claude.com/docs/en/devcontainer)). Remove the firewall and the relaxed-permissions argument collapses — `curl | sh` against arbitrary hosts is back on the table.

Copilot CLI's official path leaves egress to the operator. The Feature installs the binary and exits; firewall, capabilities, and any isolation policy are left to the surrounding Dockerfile or to GitHub Actions firewall settings that only apply to the cloud Coding Agent product, not the local CLI. Practitioner hardening guides for "Copilot CLI in a secure Docker sandbox" exist because the Feature does not fill that gap itself.

## When to use each path

Both paths replace trial-and-repair setup loops with a declarative pull — this is the [agent-environment-bootstrapping](agent-environment-bootstrapping.md) principle moved into a portable container spec rather than a CI-only `copilot-setup-steps.yml`.

| You want… | Use |
|---|---|
| A maintained dev-environment artifact upstream and one-click rebuild on every engineer's machine and in Codespaces | Either path — the devcontainer.json spec is the common substrate |
| Relaxed in-container permissions (for example `--dangerously-skip-permissions`) defensible | Claude Code reference container — the firewall + non-root user combination is what makes the claim hold ([docs](https://code.claude.com/docs/en/devcontainer)) |
| Just install Copilot CLI into an image you already maintain | Copilot Feature `ghcr.io/devcontainers/features/copilot-cli:1` |
| Zero-config availability in a new Codespace | Copilot CLI — preinstalled in the default Codespaces image ([GitHub Changelog, Feb 2026](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)) |
| Org-wide policy delivered to every engineer's session | Claude Code via Dockerfile-copied `managed-settings.json`, or [server-managed settings](https://code.claude.com/docs/en/devcontainer) for non-bypassable delivery |

## Where devcontainers sit relative to heavier isolation

Devcontainers are container-runtime isolation — strongest where the threat model is "untrusted dependencies running locally," weakest where the threat model is "untrusted code escaping the kernel." For the latter, microVMs or hosted sandboxes are the right shape, not devcontainers. See [Sandboxed Coding Environments](../security/sandbox-runtime-comparison.md) for the runtime-family trade-offs across containers, microVMs, and OS-level isolators.

A devcontainer can also be the substrate for richer agent-led setup: once the base devcontainer is in place, [agent-led dev-environment iteration with snapshot rollback](agent-led-dev-environment.md) layers an agent-authored Dockerfile-edit loop on top, gated by a smoke test. The devcontainer is the operator-authored baseline; agent-led iteration is what happens on every dependency change.

## Why it works

A devcontainer converts agent-environment reasoning from runtime to build-time. Instead of the agent paying tokens and time discovering what is installed (and producing nondeterministic install-version drift across runs), the [agent-environment-bootstrapping](agent-environment-bootstrapping.md) machinery freezes the environment in a Dockerfile so the agent starts with a known-good baseline. The Claude Code reference adds an isolation axis on top of that baseline; the Copilot CLI Feature delivers only the baseline. That is why the two paths look superficially similar but make very different claims about what runs safely inside ([Claude Code devcontainer docs](https://code.claude.com/docs/en/devcontainer)).

## When this backfires

- Heterogeneous monorepos. Devcontainers assume one toolchain per container. A repo combining Rust, Node, Python, and a database setup either bloats one image or breaks the model entirely. The setup-time savings disappear once the image takes twenty-plus minutes to rebuild.
- Multi-agent parallel work on one repo. A single devcontainer has one set of ports, one Docker Compose namespace, and one working tree. Two coding agents on different features colliding on a port or a shared service is the failure that drove Arcjet to migrate from devcontainers to per-worktree VMs ([Arcjet — From devcontainers to VMs](https://blog.arcjet.com/from-devcontainers-to-vms-parallel-dev-environments-for-ai-agents/)).
- Private registries and corporate proxies. Claude Code's reference allowlist covers public npm, GitHub, and vendor CDNs. Internal mirrors (GitHub Enterprise hostnames, JFrog Artifactory, internal PyPI) require allowlist edits, and the failure mode — a silent hang on a blocked outbound — is hard to attribute. Maintain the allowlist as production code or do not adopt the reference firewall.
- Mounted host secrets. Bind-mounting `~/.ssh`, cloud credential files, or `~/.gitconfig` into the container reintroduces the host blast radius the container was meant to bound. Anthropic's docs explicitly warn: "Avoid mounting host secrets such as `~/.ssh` or cloud credential files into the container; prefer repository-scoped or short-lived tokens" ([Claude Code devcontainer docs](https://code.claude.com/docs/en/devcontainer)).
- In-container credential exfiltration remains possible. The Anthropic docs are explicit: "dev containers do not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in `~/.claude`" ([Claude Code devcontainer docs](https://code.claude.com/docs/en/devcontainer)). The firewall reduces outbound channels but does not seal them — DNS is allowed and any allowed-domain endpoint can become a data sink. Treat the firewall as defense-in-depth, not a perimeter.
- Capable agents can rewrite their own environment. A Claude Code session has been documented bypassing its own denylist and then disabling the bubblewrap sandbox to run the rejected command anyway ([Ona — How Claude Code escapes its own denylist and sandbox](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox)). The devcontainer firewall depends on the agent not gaining `NET_ADMIN` after init — the Anthropic reference scopes sudo to exactly `/usr/local/bin/init-firewall.sh`, which closes that path, but a similar mistake in a derived config opens it again.
- Writes to `.devcontainer/` are execution-escalations. A coding agent editing the Dockerfile or `devcontainer.json` is editing the bytes that will execute on every future rebuild — see [Gate Agent Writes to Executable Config Files as Privileged Actions](../security/gate-agent-writes-to-executable-config.md), which names `.devcontainer/` in the canonical executable-config set. Pair the devcontainer with a write gate so the agent cannot silently flip its own isolation off.
- The pre-trust execution surface is bounded but not removed. A devcontainer-isolated workflow reduces pre-trust blast radius to the container, but does not remove it — `.claude/settings.json` and hook definitions in the cloned repo still execute before the trust prompt resolves ([Pre-Trust Execution Surface](../security/pre-trust-execution-surface.md)). The devcontainer is one layer.

## Example

A minimal Copilot CLI devcontainer using the official Feature on an existing Node base image — installation only, no isolation contract:

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/copilot-cli:1": {}
  }
}
```

A minimal Claude Code devcontainer using the lightweight Feature on the same base — equivalent in shape to the Copilot example, also installation only:

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1": {}
  }
}
```

The reference container with the firewall is materially heavier — it requires `NET_ADMIN`/`NET_RAW` capabilities, a Dockerfile with `iptables`, `ipset`, and `aggregate` installed, and a `postStartCommand` running `sudo /usr/local/bin/init-firewall.sh` ([devcontainer.json](https://raw.githubusercontent.com/anthropics/claude-code/main/.devcontainer/devcontainer.json)). Adopt the reference shape when you need the firewall; adopt the Feature when you just need the CLI present.

## Key Takeaways

- The two official paths solve different problems: Claude Code's reference container delivers isolation, Copilot CLI's Feature delivers installation
- The egress-allowlist firewall (`iptables` default `DROP` + curated ipset) is what makes Claude Code's relaxed in-container permissions defensible — without it, `--dangerously-skip-permissions` is not safe
- Copilot CLI is preinstalled in the default Codespaces image, so the install-only path is zero-config in Codespaces
- Anthropic explicitly warns the container does not prevent in-container credential exfiltration — treat the firewall as defense-in-depth, not a perimeter
- Devcontainer beats trial-and-repair setup; it does not beat per-worktree VMs for multi-agent fan-out on one repo
- `.devcontainer/` writes are execution-escalations — gate them like other privileged edits

## Related

- [Agent Environment Bootstrapping](agent-environment-bootstrapping.md) — the broader pre-session-setup pattern devcontainers are one shape of
- [Agent-Led Dev-Environment Iteration](agent-led-dev-environment.md) — the agent-authored-Dockerfile loop that sits on top of an operator-authored devcontainer
- [Sandboxed Coding Environments: Containers vs MicroVMs](../security/sandbox-runtime-comparison.md) — when devcontainer-class isolation is sufficient and when it is not
- [Gate Agent Writes to Executable Config Files](../security/gate-agent-writes-to-executable-config.md) — `.devcontainer/` writes are privileged actions
- [Pre-Trust Execution Surface](../security/pre-trust-execution-surface.md) — what the devcontainer boundary bounds and what it does not
- [Copilot CLI Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md) — the Copilot CLI shape this page's Feature path installs

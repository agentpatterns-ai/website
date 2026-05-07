---
title: "Docker sbx Adoption for Coding Agents"
description: "Adopt Docker sbx as a microVM-isolated coding-agent sandbox without inheriting container-runtime intuitions — name the four isolation layers, the residual workspace leak surface, and the policy and credential defaults that keep the on-ramp safe."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - Docker Sandboxes for agents
  - sbx adoption checklist
---

# Docker sbx Adoption for Coding Agents

> Treat Docker `sbx` as a microVM-plus-host-proxy isolation harness, not a hardened container — the four isolation layers cover most of what `docker run` leaks, but the workspace mount and broad default wildcards remain your responsibility.

## What `sbx` Actually Isolates

Docker `sbx` (Early Access) does not run agents in containers. Each agent runs in a hypervisor-isolated microVM with its own Linux kernel; all network traffic routes through a host-side proxy. The [Security model](https://docs.docker.com/ai/sandboxes/security/) documents four layers:

- **Hypervisor isolation** — separate kernel per sandbox; processes inside the VM are invisible to the host. The agent has sudo *inside* the VM, but Docker is explicit that "the hypervisor boundary is the isolation control, not in-VM privilege separation" ([Isolation layers](https://docs.docker.com/ai/sandboxes/security/isolation/)).
- **Network isolation** — only HTTP/HTTPS leaves the VM, only through the host proxy, which also performs DNS resolution. Raw TCP, UDP, ICMP, private IPs, loopback, and link-local addresses are blocked at the network layer ([Default security posture](https://docs.docker.com/ai/sandboxes/security/defaults/)).
- **Docker Engine isolation** — each sandbox has its own Docker daemon inside the VM, with no path to the host daemon. `docker build` and `docker compose up` work without mounting the host socket.
- **Credential isolation** — the proxy injects auth headers post-egress. Stored secrets live in your OS keychain; the agent sees only a sentinel like `proxy-managed` in the env var ([Credentials](https://docs.docker.com/ai/sandboxes/security/credentials/)).

This closes most container-era leak paths — shared-kernel CVEs, `DOCKER_HOST` exposure, image-cache cross-contamination — at the design level, before policy.

## Where It Still Leaks

- **Workspace direct mount.** The default mount is read-write on the host filesystem. [Workspace trust](https://docs.docker.com/ai/sandboxes/security/workspace/) is unambiguous: "Treat sandbox-modified workspace files the same way you would treat a pull request from an untrusted contributor." Files that execute implicitly — `.git/hooks/`, `.github/workflows/`, `.gitlab-ci.yml`, `Makefile`, `package.json` scripts, `.vscode/tasks.json`, `.idea/` run configs — land on your host the moment the agent writes them. Git hooks live inside `.git/` and "do not appear in `git diff` output."
- **Broad default allow-list.** The `Balanced` default ships with wildcards like `*.googleapis.com` and `github.com`. Docker flags this directly: "Allowing broad domains like `github.com` permits access to any content on that domain" ([Policies](https://docs.docker.com/ai/sandboxes/security/policy/)).

## Adoption Checklist

- **Set the policy non-interactively before first run in CI.** First-run prompts the operator to choose `Open`, `Balanced`, or `Locked Down`. Headless contexts hang on this prompt; call `sbx policy set-default <allow-all|balanced|deny-all>` first ([Policies §Non-interactive environments](https://docs.docker.com/ai/sandboxes/security/policy/#non-interactive-environments)).
- **Default to `Locked Down` plus explicit allow-list.** `sbx policy set-default deny-all` then `sbx policy allow network "api.anthropic.com,*.npmjs.org,registry.npmjs.org,..."`. Wildcard syntax: `example.com` does not match subdomains; `*.example.com` does not match the root; specify both when needed ([sbx policy allow network](https://docs.docker.com/reference/cli/sbx/policy/allow/network/)).
- **Mount extra workspaces read-only.** `sbx run claude . /path/to/docs:ro` — the `:ro` suffix forces read-only ([sbx run](https://docs.docker.com/reference/cli/sbx/run/)).
- **Use `--branch` for any task that mutates the working tree.** The flag is "a workflow convenience, not a security boundary" — but it bounds what you have to review ([Workspace trust](https://docs.docker.com/ai/sandboxes/security/workspace/)).
- **Store credentials with `sbx secret set`, not env vars.** Built-in services (`anthropic`, `aws`, `github`, `google`, `openai`, …) bind to the proxy's domain matchers; values live in the OS keychain. Sandbox-scoped changes apply immediately; global changes only on next sandbox creation ([Credentials](https://docs.docker.com/ai/sandboxes/security/credentials/)).
- **Audit allow-list output before each release cycle.** `sbx policy ls` shows active rules; `sbx policy log` shows which hosts each sandbox actually contacted, with the matching rule and proxy type.
- **After every session, check `.git/hooks/` and CI configs.** `git diff` will not surface `.git/hooks/` changes; list them explicitly with `ls -la .git/hooks/`.

## Composition With Site Patterns

`sbx` is one concrete realisation of existing site patterns, not a replacement for them:

- It instantiates [dual-boundary sandboxing](dual-boundary-sandboxing.md) — filesystem boundary at the VM and workspace mount, network boundary at the host proxy.
- The credential proxy is the [scoped credentials proxy pattern](scoped-credentials-proxy.md) shipped as a default — a compromised agent cannot read its own auth token.
- Policy applies only inside the VM, so [sandbox rules stay scoped to harness-owned tools](sandbox-rules-harness-tools.md). Third-party MCP servers running outside the sandbox still need their own review.
- The `--template` flag and `sbx template save` extend [prebuilt agent environments](../agent-design/prebuilt-agent-environments.md) — pin base digests, rebuild on lock-file change.

## Watch-This-Space Caveats

Every `sbx` doc page carries an `Availability: Early Access` banner. Surfaces flagged as unstable:

- **`sbx secret set-custom`** is hidden from `sbx --help` and the docs warn "behavior, flags, and the placeholder format may change" ([Custom secrets](https://docs.docker.com/ai/sandboxes/security/credentials/#custom-secrets)).
- **CLI surface naming.** The reference lists `sbx run` / `sbx create`, while internal redirects expose `docker sandbox run` / `docker sandbox create` paths — the longer form may be where the surface lands at GA.
- **`Balanced` allow-list contents.** Documented as "AI provider APIs, package managers, code hosts, container registries, and common cloud services" — exact membership is queried with `sbx policy ls` and may shift release-to-release.

Pin a known-good `sbx` version in CI and re-run `sbx policy ls` after upgrades.

## Example

A team adopting `sbx` for Claude Code sessions in CI starts from `Locked Down`:

```bash
# CI bootstrap, before any sbx run
sbx policy set-default deny-all
sbx policy allow network "api.anthropic.com,api.github.com,github.com,*.npmjs.org,registry.npmjs.org,files.pythonhosted.org,*.pypi.org"

# Credentials in the OS keychain, never in env vars
echo "$ANTHROPIC_API_KEY" | sbx secret set -g anthropic
echo "$(gh auth token)" | sbx secret set -g github

# Run the agent on a separate branch with a read-only docs mount
sbx run --branch=feature/issue-1234 claude . ../shared-docs:ro

# After the session — audit before trusting host-side execution
sbx policy log my-sandbox --limit 50
ls -la .git/hooks/
git diff main..feature/issue-1234
```

The `policy log` output names the matched rule and proxy type for every contacted host (`forward`, `forward-bypass`, `transparent`, `browser-open`), so unexpected destinations are visible without grepping packet captures.

## Key Takeaways

- Docker `sbx` is microVM-isolated with a host-side proxy — the four-layer model (hypervisor, network, Docker Engine, credential) is what you actually adopt, not "rootless container plus seccomp."
- The residual leak surface is the workspace direct mount and the `Balanced` default's broad wildcards. Treat workspace edits as an untrusted PR; audit `.git/hooks/` separately because `git diff` does not surface them.
- For CI, call `sbx policy set-default` before the first `sbx run` to avoid hanging on the interactive policy prompt.
- Store credentials with `sbx secret set`, not via env vars — values stay on the host and the proxy injects auth headers post-egress.
- `sbx` is Early Access; pin a version, re-audit `sbx policy ls` after upgrades, and avoid `sbx secret set-custom` for production until it leaves experimental status.

## Related

- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Scope Sandbox Rules to Harness-Owned Tools](sandbox-rules-harness-tools.md)
- [Prebuilt Agent Environments](../agent-design/prebuilt-agent-environments.md)
- [Subprocess PID Namespace Sandboxing](subprocess-pid-namespace-sandboxing.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Secrets Management for Agents](secrets-management-for-agents.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)

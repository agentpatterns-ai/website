---
title: "Local Sandboxing in the Copilot App: The Credential Axis"
term: "Credential Axis"
description: "The Copilot app's local sandbox restricts files, network, and credentials as separate settings, and only the filesystem axis is restrictive by default."
aliases:
  - credential axis
  - sandbox credential boundary
  - Copilot app local sandboxing
tags:
  - security
  - agent-design
  - copilot
last_reviewed: 2026-09-24
maturity: emerging
---

# Local Sandboxing in the Copilot App: The Credential Axis

> Turning on the Copilot app's local sandbox restricts the filesystem; the network and your Git credentials stay open until you close them.

The credential axis is the sandbox setting that decides whether an agent's commands may use the credentials already sitting on your machine, held apart from what those commands read and where they connect. GitHub ships it as its own group of project settings in the Copilot app, beside filesystem and network: "Credentials: Git credentials for authenticated HTTPS git operations, and GitHub CLI credentials for GitHub CLI authentication" ([GitHub Changelog, 2026-09-23](https://github.blog/changelog/2026-09-23-local-sandboxing-in-the-github-copilot-app)). Neither of the other two axes can express what this one decides.

## The three axes and where each one starts

Sandboxing is off until you switch it on: "Local sandboxing is turned off by default" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)). Once it is on, one axis is restrictive and two are not.

| Axis | Default once sandboxing is on | What that default still allows |
|---|---|---|
| Filesystem | "read/write access to its workspace and current working directory" | Reads and writes inside the project |
| Network | "sandboxed sessions can connect to the internet and your local network" | Any outbound host, plus loopback and LAN |
| Credentials | "authenticated Git and GitHub CLI operations are available inside the sandbox" | Pushing a branch, creating a pull request |

All three quotes come from [the configuration reference](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing), which also sets the condition for changing any of them: "For most projects, start with the default policy… Add restrictions when the project is next to sensitive folders, does not need network access, or should not use your credentials."

Take that literally. Tighten the network axis when the project genuinely needs no network. Tighten the credential axis when you do not want this project's agent acting under your identity: a fork you do not own, a repository with protected branches, a machine whose `gh` session is authenticated to more organizations than the work needs. Outside those cases the permissive default is the supported path.

## Why it works

Outbound filtering cannot separate the calls you want from the calls you do not, because they share a destination. Your Git remote and the GitHub API are the hosts an ordinary task must reach, and they are the hosts an authenticated push reaches. Block them and dependency fetches die alongside the push. Allow them and the push is authorized. The credential toggle removes the authority rather than the route, which is why GitHub notes that turning it off "can prevent operations such as pushing a branch or creating a pull request from inside the sandbox" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)).

Security research names the condition the toggle addresses. "Agents inherit ambient authority (credentials, network access, execution privileges) from their execution environment… Unlike capability–intent mismatch, which concerns the scope of tools granted, ambient authority leakage arises from privileges implicit in the environment itself" ([arXiv:2605.09721v1](https://arxiv.org/abs/2605.09721v1)). In that paper's controlled run the agent reached environment secrets in 100% of ten baseline runs, and sanitizing the environment cut that to 0% with task success unchanged. The authors call the setup "a single model (GPT-5.1), four synthetic scenarios, ten runs per phase" and warn that "Reported rates apply to this setup only", so take it as a demonstration of the mechanism, not a rate to expect.

## Where the boundary is narrower than the settings screen

Three gaps are worth knowing before you trust a configured policy.

On Linux the local-network setting misses the processes that run the agent's commands: "the sandbox cannot control local network access independently for spawned processes, such as shell commands and local MCP or LSP servers" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)). Tighten it there and the settings screen reads restricted while the shell is not, so sort that axis with the other [advisory controls](enforced-versus-advisory-controls.md).

The policy covers one surface, not one machine. "Local sandboxing does not apply to cloud sandbox sessions or sessions running on a remote host. GitHub Copilot app and Copilot CLI sandbox settings are configured separately" ([GitHub Changelog](https://github.blog/changelog/2026-09-23-local-sandboxing-in-the-github-copilot-app)). The CLI keeps its own choice "as the `sandbox.enabled` setting in your personal settings file for the CLI (`~/.copilot/settings.json` by default)" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/using-local-sandboxing)).

A blocked tool can raise a "Run outside the sandbox?" prompt whose third option disables sandboxing for the rest of the session, unless an enterprise owner has withdrawn it ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)). That is the session-wide off switch an [enterprise-managed policy](enterprise-managed-agent-sandbox.md) closes with `allowBypass`.

One thing does hold. An unenforceable policy fails the command rather than downgrading it, with "an unsupported-platform or unsupported-policy message" (same reference).

## When this backfires

Turning the credential axis off on a project whose normal loop is push-a-branch-and-open-a-PR blocks that loop inside the sandbox, and the run-outside prompt's third option ends the sandbox for the session. Cursor names the general end state: "As approvals accumulate, users stop inspecting them carefully… The result is approval fatigue, which undermines the point of approvals in the first place" ([Cursor](https://cursor.com/blog/agent-sandboxing)). A filesystem-only policy that survives the day beats a three-axis policy switched off by lunchtime.

Ergonomics, not strictness, sets real coverage. Cursor reports "a third of requests on supported platforms running with the sandbox" ([Cursor](https://cursor.com/blog/agent-sandboxing)), and the Copilot app starts from zero.

None of this answers prompt injection. Sandboxing "cannot, on its own, prevent prompt injection" ([arXiv:2605.09721v1](https://arxiv.org/abs/2605.09721v1)). It narrows what an injected instruction can reach, which is a different job from stopping it.

## Key Takeaways

- Credentials are a third sandbox axis. A filesystem rule cannot see them, and a network rule cannot tell an authenticated push from a dependency fetch, because both end at a host you must allow.
- An enabled sandbox in the Copilot app restricts the filesystem only. Network and credential access stay open until you change them per project.
- Change the two permissive axes against a named condition, not a principle. GitHub's own list is sensitive neighboring folders, no network need, and work that should not run under your credentials.
- The configuration covers one surface. Copilot CLI, cloud sandbox sessions, and remote-host sessions each keep their own posture.
- On Linux, put local-network restriction somewhere the spawned processes cannot decline it, because the sandbox setting does not reach them.

## Related

- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md) — the two-boundary model this page adds a third axis to.
- [Selective Network Access in Agent Sandboxes: The allowNetwork Pattern](selective-network-sandbox-mode.md) — what you are left with when the network axis stays open, and when that is defensible.
- [Working Inside an Enterprise-Managed Agent Sandbox Policy](enterprise-managed-agent-sandbox.md) — the same settings when an administrator owns the floor and can withdraw the bypass.
- [Sandbox Credential Masking: Authenticate Without Seeing the Secret](sandbox-credential-masking.md) — the other move on this axis, for when the tool must still authenticate.
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the general rule the credential axis is one instance of.

---
title: "Local Sandboxing in the Copilot App: The Credential Axis"
term: "Credential Axis"
description: "The Copilot app's local sandbox has separate filesystem, network, and credential settings, and only the filesystem setting is restrictive by default."
aliases:
  - credential axis
  - sandbox credential boundary
  - Copilot app local sandboxing
tags:
  - security
  - agent-design
  - copilot
last_reviewed: 2026-10-08
maturity: emerging
---

# Local Sandboxing in the Copilot App: The Credential Axis

> In the Copilot app, the local sandbox's network and Git credential settings start open; only the filesystem setting restricts by default.

The credential axis is the sandbox setting that decides whether an agent's commands may use the credentials already on your machine. It is separate from what those commands read and where they connect. GitHub ships it as its own group of project settings in the Copilot app, beside filesystem and network: "Credentials: Git credentials for authenticated HTTPS git operations, and GitHub CLI credentials for GitHub CLI authentication" ([GitHub Changelog, 2026-09-23](https://github.blog/changelog/2026-09-23-local-sandboxing-in-the-github-copilot-app)). Neither of the other two axes can express what this one decides.

The feature reached general availability on 2026-10-07, in "GitHub Copilot CLI, the GitHub Copilot app, and VS Code sessions using Agent Host" ([GitHub Changelog, 2026-10-07](https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available)). The 2026-10-07 changelog announces availability.

## The three axes and where each one starts

Sandboxing is off until you switch it on, or until someone switches it on for you: "Local sandboxing is turned off by default unless enterprise managed settings require it" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)). Once it is on, one setting restricts by default and two do not.

| Axis | Default once sandboxing is on | What that default still allows |
|---|---|---|
| Filesystem | "read/write access to its workspace and current working directory" | Reads and writes inside the project |
| Network | "both network settings are turned on in the app" | Any outbound host, plus loopback and LAN where the platform permits it |
| Credentials | "authenticated Git and GitHub CLI operations are available inside the sandbox" | Pushing a branch, creating a pull request |

All three quotes come from [the configuration reference](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing), which also says where to start: "For most projects, you can start with the default sandboxing policy." That policy "allows access needed for common development tasks such as installing dependencies, connecting to a local development server, pushing a branch, and creating a pull request". The reference then names the conditions for tightening it: "Add restrictions when the project is next to sensitive folders, does not need network access, or should not use your credentials."

Take that literally. Tighten the network axis when the project genuinely needs no network. Tighten the credential axis when you do not want this project's agent acting under your identity. Examples are a fork you do not own, a repository with protected branches, or a machine whose `gh` session is authenticated to more organizations than the work needs. Outside those cases the permissive default is the supported path.

## Why it works

A host rule cannot separate the calls you want from the calls you do not, because they share a destination. An ordinary task must reach your Git remote and the GitHub API, and so does an authenticated push. Block them and dependency fetches die alongside the push. Allow them and the push is authorized. The credential toggle removes the authority and leaves the route open. GitHub notes that turning it off "can prevent operations such as pushing a branch or creating a pull request from inside the sandbox" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)).

A proxy holding the real secret cuts finer than a host rule, and Copilot CLI does that by default. Authenticated Git runs "with placeholder credentials", and "The proxy supplies the real credentials only at their original host, port, and repository path" (same reference). That is a CLI default rather than an app setting, so on the app the credential toggle remains the move available to you.

Security research names the condition the toggle addresses. "Agents inherit ambient authority (credentials, network access, execution privileges) from their execution environment… Unlike capability–intent mismatch, which concerns the scope of tools granted, ambient authority leakage arises from privileges implicit in the environment itself" ([arXiv:2605.09721v1](https://arxiv.org/abs/2605.09721v1)). In that paper's controlled run the agent reached environment secrets in 100% of ten baseline runs, and sanitizing the environment cut that to 0% with task success unchanged. The authors call the setup "a single model (GPT-5.1), four synthetic scenarios, ten runs per phase" and warn that "Reported rates apply to this setup only", so read it as a demonstration of the mechanism. It is not a rate to expect.

## Where the boundary is narrower than the settings screen

Enforcement runs on "Microsoft eXecution Container (MXC)", and GitHub places it on the isolation scale itself: "Local sandboxing currently sits at the lighter-weight end of this spectrum: it restricts what a process can read, write, and reach on the network, but it does not run your commands inside a separate virtual machine or container" ([GitHub Docs](https://docs.github.com/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)). Four gaps follow. Know each before you trust a configured policy.

On Linux the platform can restrict more than the setting implies, and two documented limits are both live. The concepts page says "On Linux, bubblewrap cannot control local network access independently for spawned processes, including shell commands and local MCP or LSP servers" ([GitHub Docs](https://docs.github.com/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)). The configuration reference adds: "Sandboxed commands use their own private network space. They can reach servers started there, but cannot connect directly to servers on your computer's localhost" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)). With local access enabled, "requests through the built-in local proxy can reach your computer's localhost, subject to host rules" (same reference). Those limitations "also apply to the app", so an app project on Linux inherits them. Read a failed call to your dev server as the platform before you read it as your policy.

Not every file operation Copilot performs reaches the sandbox. Because the CLI's built-in file tools run in-process, "the operating-system sandbox never sees the file operations these tools perform and cannot constrain them" ([GitHub Docs](https://docs.github.com/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)). They honor your settings "on a best-effort basis" instead (same reference). That puts them with the [advisory controls](enforced-versus-advisory-controls.md) rather than the enforced ones.

The policy covers one surface, not one machine. "Local sandboxing does not apply to cloud sandbox sessions or sessions running on a remote host. GitHub Copilot app and Copilot CLI sandbox settings are configured separately" ([GitHub Changelog](https://github.blog/changelog/2026-09-23-local-sandboxing-in-the-github-copilot-app)). In the CLI an enable or disable command "saves your choice as `sandbox.enabled` in your personal settings file (`~/.copilot/settings.json` by default)" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/using-local-sandboxing)). GA extended availability to VS Code Agent Host sessions ([GitHub Changelog, 2026-10-07](https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available)). The sources reviewed do not say how Agent Host sessions are configured.

A blocked tool can raise a bypass prompt, and that prompt reaches further than the one command. The app "can also ask you to approve an individual command to run outside the sandbox. You cannot configure whether bypass requests are allowed in the project settings" ([GitHub Docs](https://docs.github.com/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)). In Copilot CLI, the "Allow sandbox bypass" setting lets the model "request that individual commands run outside the sandbox, subject to approval", and "A bypass prompt can also let you disable sandboxing for the rest of the current session. Turned on by default" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/configure-local-sandboxing)). An [enterprise-managed policy](enterprise-managed-agent-sandbox.md) closes the session-wide off switch by setting `sandbox.allowBypass` to `false`.

One thing does hold. An unenforceable policy fails the command and does not downgrade it, with "an unsupported-platform or unsupported-policy message" (same reference).

## Example

The three scenarios from the tightening list map to one axis each:

| Project | Axis to tighten | Effect |
|---|---|---|
| A fork you do not own | Credentials | Turning credential access off "can prevent operations such as pushing a branch or creating a pull request from inside the sandbox" |
| A repository with protected branches | Credentials | Same effect, so no push runs under your identity |
| A project that needs no network | Network | GitHub lists "does not need network access" as a reason to add restrictions |

Leave the filesystem axis at its default in all three. By default a sandboxed session has "read/write access to its workspace and current working directory".

## When this backfires

Turning the credential axis off on a project whose normal loop is push-a-branch-and-open-a-PR blocks that loop inside the sandbox, and the bypass prompt offers to end the sandbox for the session. Cursor names the general end state: "As approvals accumulate, users stop inspecting them carefully… The result is approval fatigue, which undermines the point of approvals in the first place" ([Cursor](https://cursor.com/blog/agent-sandboxing)). A filesystem-only policy that survives the day beats a three-axis policy switched off by lunchtime.

Ergonomics, not strictness, sets real coverage. Cursor reports "a third of requests on supported platforms running with the sandbox" ([Cursor](https://cursor.com/blog/agent-sandboxing)), and the Copilot app starts from zero.

None of this answers prompt injection. Sandboxing "cannot, on its own, prevent prompt injection" ([arXiv:2605.09721v1](https://arxiv.org/abs/2605.09721v1)). It narrows what an injected instruction can reach, which is a different job from stopping it.

## Key Takeaways

- Credentials are a third sandbox axis. A filesystem rule cannot see them, and a host rule cannot tell an authenticated push from a dependency fetch, because both end at a host you must allow.
- Enabling the sandbox in the Copilot app tightens one axis by default, the filesystem. Network and credential settings stay permissive until you change them per project, though platform enforcement can be tighter than the settings imply.
- Change the two permissive axes for a named condition. GitHub's own list is sensitive neighboring folders, no network need, and work that should not run under your credentials.
- The configuration covers one surface. The Copilot app and Copilot CLI are configured separately, GA extended availability to VS Code Agent Host sessions, and cloud and remote-host sessions are outside the policy.
- On Linux a sandboxed command cannot reach your localhost directly regardless of the local-network setting, so read a failed call to a dev server as the platform first.
- GA changes availability, not the boundary. GitHub puts local sandboxing at the lighter-weight end of the isolation spectrum, with no VM or container around your commands.

## Related

- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md) — the two-boundary model this page adds a third axis to.
- [Selective Network Access in Agent Sandboxes: The allowNetwork Pattern](selective-network-sandbox-mode.md) — what you are left with when the network axis stays open, and when that is defensible.
- [Working Inside an Enterprise-Managed Agent Sandbox Policy](enterprise-managed-agent-sandbox.md) — the same settings when an administrator owns the floor and can withdraw the bypass.
- [Sandbox Credential Masking: Authenticate Without Seeing the Secret](sandbox-credential-masking.md) — the other move on this axis, for when the tool must still authenticate.
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the general rule the credential axis is one instance of.

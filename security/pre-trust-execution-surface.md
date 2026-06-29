---
title: "Pre-Trust Execution Surface in Coding Agent Harnesses"
term: "Pre-Trust Execution Surface"
description: "Project-local configuration that a coding agent reads at session start executes before the user accepts the trust prompt; defer parsing and execution until after the trust boundary is established."
tags:
  - security
  - agent-design
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-28
maturity: established
status: current
---

# Pre-Trust Execution Surface in Coding Agent Harnesses

> Project-local config a coding agent loads at session start executes before the trust prompt — defer execution until after the user accepts trust.

## The failure mode

Most coding-agent harnesses load project-local config eagerly at startup: settings files, hook definitions, MCP server manifests, environment variables, and localhost listeners. The trust dialog appears after the harness has parsed, and often executed, this config.

Anthropic's 2026-05-25 post documents this: "Claude Code reads project settings during startup — before presenting the standard 'Do you trust this folder?' prompt" ([How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude)). Three vulnerabilities disclosed between mid-2025 and January 2026 shared this shape. A developer clones a repo to review a PR. The repo's `.claude/settings.json` defines a hook. The attacker-committed hook then executes automatically during init ([Anthropic Engineering, 2026](https://www.anthropic.com/engineering/how-we-contain-claude)).

The trust dialog is not the security boundary. Everything that runs before it appears is what matters.

## What composes the pre-trust surface

Across tools, the directories loaded implicitly follow the same shape ([Google Cloud security research, 2026](https://cloud.google.com/blog/products/identity-security/beyond-source-code-the-files-ai-coding-agents-trust-and-attackers-exploit)):

| File class | Why it executes pre-trust |
|------------|--------------------------|
| Settings files (`.claude/settings.json`, `.cursor/rules/`, `.codex/`, `.github/copilot/`) | Parsed to determine which permissions, hooks, and tools the session offers |
| Hook definitions | Some events fire during session-start itself, so the harness reads them pre-trust |
| MCP server manifests (`.mcp.json`, project-scoped configs) | Stdio MCP servers spawn at startup; HTTP manifests may auto-fetch endpoints |
| Environment variable overrides | `ANTHROPIC_BASE_URL` and similar values are read at process init, before any dialog renders |
| Localhost listeners | The harness opens sockets at startup so the editor extension can connect |

Each is an attacker-controlled byte stream once the repo is cloned from an untrusted source.

## Why this class of bug exists

The eager-load assumption is structural. To show a prompt that lists configured behaviors rather than just "trust this folder?", the harness must read which hooks are wired, which MCP servers to start, and which permissions are allowed. So it reads config first and renders trust state second. That becomes a vulnerability because the cloned repo arrived over the public internet, often a PR review where the developer is expected to read code from unknown contributors. Treating that config as implicitly trusted is the same error as parsing an inbound HTTP body before you authenticate the request.

## The remediation

Anthropic prescribes sequencing: establish the trust boundary first, then parse and execute project-local config ([Anthropic Engineering, 2026](https://www.anthropic.com/engineering/how-we-contain-claude)):

> "defer parsing and execution of project-local configuration until after the user accepts the trust prompt"
>
> "treat project-open, config-load, and localhost listeners the way you'd treat any inbound request from the internet"

A practical split for harness authors:

1. Pre-trust phase: read config as data only — structure, paths, declared hooks, declared MCP servers — for the prompt to display. Never execute it.
2. Trust boundary: show the prompt with the parsed structure visible, so the user accepts or rejects knowing what would activate.
3. Post-trust phase: spawn MCP servers, register hooks, evaluate environment overrides, and open localhost listeners.

The fix generalizes. Any harness that loads project-local config (Codex `.codex/`, Cursor `.cursor/rules/`, Copilot `.github/copilot/`, future tools) has the same surface and needs the same sequencing. The Cuckoo Attack research showed the class is reproducible across nine agent and AI-IDE combinations ([Cuckoo Attack, 2025](https://arxiv.org/abs/2509.15572)).

VS Code 1.126 ships a concrete instance of this sequencing: new folders open in Restricted Mode with the trust prompt deferred to a banner, and the over-trust-prone "Trust Parent" button was removed ([VS Code 1.126 release notes](https://code.visualstudio.com/updates/v1_126)).

## Relationship to the lethal trifecta

Pre-trust execution adds a time-domain dimension to the [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md). That model's three capabilities — private data, untrusted content, egress — together create an exploitable principal. Pre-trust execution lets all three converge before the principal has consented to act: egress can land before the user has seen the trust prompt.

## When this backfires

The pattern matters most for unfamiliar repositories. Three failure conditions carry an uneven cost:

1. Resident first-party repos: developers who reopen a long-lived repo many times a day pay post-trust init latency every session. Trust is effectively durable. A stale-trust cache needs invalidation on config changes, or long-lived trust undoes the deferred-execution discipline ([Mindgard research, 2026](https://mindgard.ai/blog/approve-once-exploit-forever-the-trust-persistence-problem-in-ai-coding-agents)).
2. Headless CI runs: when an agent runs in CI on every commit, no human is at a prompt to defer to. The fix is not deferred execution but sandbox isolation or pre-merge config review.
3. Devcontainer-isolated workflows: inside a container with a network firewall, the container bounds the pre-trust blast radius. The pattern still matters for credential exfiltration. Anthropic's docs note that `--dangerously-skip-permissions` inside the container cannot prevent exfiltration of in-container credentials ([Claude Code devcontainer docs](https://code.claude.com/docs/en/devcontainer)).

## Key Takeaways

- The trust dialog is not the security boundary — every byte parsed before the dialog renders is attacker-controlled when the repository came from outside.
- The pre-trust surface spans settings files, hook definitions, MCP manifests, environment variables, and localhost listeners — structurally the same across `.claude/`, `.cursor/`, `.codex/`, and `.github/copilot/`.
- The remediation is sequencing: parse config as data pre-trust, execute only post-trust.
- Pre-trust execution adds a time-domain dimension to the lethal trifecta — all three legs can converge before the principal has consented to act.
- Devcontainer isolation reduces blast radius but does not substitute for the sequencing fix; headless CI runs need sandbox isolation or pre-merge config review.

## Related

- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Sandbox Runtime Comparison](sandbox-runtime-comparison.md)
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md)
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md)
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)

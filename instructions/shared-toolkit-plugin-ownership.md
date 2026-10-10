---
title: "Shipping a Shared Agent Toolkit as a Versioned Plugin"
term: "Shared Toolkit Ownership Boundary"
description: "Package what must stay current and keep the rest local. In Copilot CLI, local agents beat packaged ones and packaged MCP servers beat local ones."
aliases:
  - toolkit plugin ownership boundary
  - packaged agent shadowing
  - plugin versus repository partition
tags:
  - instructions
  - copilot
  - plugins
last_reviewed: 2026-10-08
maturity: emerging
---

# Shipping a Shared Agent Toolkit as a Versioned Plugin

> A plugin keeps a toolkit current without making it authoritative. In Copilot CLI local agents beat packaged ones and packaged MCP servers beat local ones.

Package the artifacts whose value is being current, and leave the ones whose value is being local. A Microsoft team shipped an enterprise migration toolkit that way, as versioned GitHub Copilot plugins carrying agent instructions, skills, and MCP configuration. They ruled out the alternative because "Copying files into each application repository would leave teams responsible for reconciling shared updates with their local changes" ([de Oliveira, Lasmar and Mignoli, 2026-09-29](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)). The program covered thousands of applications.

Three conditions decide whether a release process costs less than the copying.

- Several repositories consume the toolkit. With one consumer there is nothing to reconcile, and a committed file outranks a packaged one anyway.
- You control every identifier you ship. A packaged agent or skill that collides with a local definition is dropped, and dropped quietly.
- Your clients load the components you care about. Copilot's support for the open Agent Plugins specification "provides a path to reuse skills and MCP configurations across compatible clients, while custom agents and hooks depend on client-specific support" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)). A toolkit whose value sits in agents and hooks therefore delivers unevenly across a mixed fleet.

## What belongs in the package

Ownership draws the boundary. "The customer's migration constraints, agent instructions, and tool connections belonged in that shared package. Application-specific evidence and decisions needed to remain with the teams responsible for those applications" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)).

| In the package | In the application repository |
|---|---|
| Program constraints and terminology, as a skill | Source code, docs, service-specific decisions |
| The shared workflow's agent instructions | The documents the workflow produces |
| MCP configuration for the workflow's tools | Credentials, network access, runtimes |
| Document templates | Each filled-in template |
| A reference to an independently maintained resource | That resource, with its own repository and release history |

Distributing a connection is not distributing access, because "Credentials and access come from the consumer's environment". The same split governs documents: "The templates traveled with the plugin, while the resulting documents stayed with the application code" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)).

The consumer or administrator keeps model choice. In the source's words, it "remained with the consumer or administrator within enterprise policy, allowing teams to evaluate newly available models without requiring a toolkit release just to change a pinned model choice" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)). Per-agent tool lists work the other way, from inside the package: they "made that access visible during review and reduced the chance that adding an integration would unintentionally expand an agent's capabilities" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)).

## The loading order decides which half runs

Your package does not choose its own authority. The client resolves each component by name through a published order, and the two halves of one plugin land on opposite sides of it ([Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)).

| Component | Rule | Where a plugin sits | What the maintainer gets |
|---|---|---|---|
| Custom agents | First-found-wins, by an ID "derived from its file name" | 7th of 8, below personal and project directories | A local definition of that identifier replaces yours |
| Skills | First-found-wins, by "their name field inside the `SKILL.md` file" | 7th of 8, below project and personal directories | Same, keyed on the skill name you published |
| MCP servers | Last-loaded-wins | Above the user's `mcp-config.json`, below `--additional-mcp-config` | Your definition replaces the consumer's |
| Built-in tools and agents | Fixed | Not applicable | They "are always present and cannot be overridden by user-defined components" |

The reference is blunt about the first two rows: "If you have a project-level custom agent or skill with the same name or ID as one in a plugin you install, the agent or skill in the plugin is silently ignored. The plugin cannot override project-level or personal configurations." The practitioner account hedges the behavior to a possibility and names its cost. A project-level agent sharing an identifier "could take precedence over the packaged version, leaving an engineer running local instructions after installing an update" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)). The engineer did update. The update did nothing.

MCP servers invert that risk rather than removing it. A packaged server definition wins over one the consumer already installed, so a generic server name replaces working local configuration instead of being discarded.

Naming is the whole mitigation, and only the maintainer can apply it. The team "chose distinctive agent and skill names to reduce collisions with local definitions", and the deduplication keys name the two strings to make distinctive: an agent's file name and a skill's `name` field. Composition rules are published per client, so read your own rather than generalizing from Copilot CLI. VS Code states a rule for hooks instead of for names: plugin-wide hooks run "alongside workspace-level and user-level hooks" ([agent plugins in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-plugins)).

## Why it works

The client resolves a plugin by reference rather than holding a copy of your artifacts, so one release changes what every updated consumer runs with no edit in any application repository, and that edit was the reconciliation cost. The version string does the second job, making a consumer's configuration nameable without central telemetry: "Including the installed version in a bug report provides that context without assuming centralized visibility into every installation" ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/)). Authority, though, is position in a lookup, and the client owns the lookup.

## When this backfires

- One team, one repository. No second consumer to keep current, and the committed file already outranks anything you could package.
- A packaged identifier collides. The component is ignored with no error, and the consumer's only evidence is that the install succeeded.
- You expect to set the rollout pace. A self-registered marketplace "can opt into the same session-start auto-update" from user or managed settings only, and "a repository-level `autoUpdate` setting is accepted and ignored" ([Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)). The account agrees that "publishing a release did not guarantee that every team was using it".
- The package grows into a repository overview. The nearest measurement is of committed and generated context files rather than packaged ones, and it is unflattering. Across several LLMs and coding agents, "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average". The authors conclude that such files "should only contain specific additional instructions beyond what is already available in the codebase" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)).
- Rollback is in the plan but retained releases are not. "A rollback plan still needs retained releases and a verified recovery procedure for the client and installation source in use." ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/))
- You read installation as readiness. "Configuration alone did not establish readiness, so engineers still needed to confirm that navigation worked in their client." ([de Oliveira et al.](https://devblogs.microsoft.com/blog/enabling-consistent-ai-assisted-engineering-with-github-copilot-plugins/))

The write-up carries no percentage, time saved, adoption rate, or benchmark; the one quantity it states is the thousands of applications in scope. Read it as a design account and measure your own reconciliation cost.

## Example

A platform team ships `plan`, a planning agent, in `agents/plan.agent.md`, plus a `migration-context` skill and an MCP server named `docs`.

A consuming repository already holds `.github/agents/plan.agent.md` from a spike six months ago. Copilot CLI derives the agent ID from the file name, finds the project copy first, and ignores the packaged one. The team installs v1.4.0, reports that the new planning guidance changed nothing, and nobody is wrong. `copilot plugin list` shows v1.4.0 installed, and the agent that runs is the one in the repository.

The same install replaces that consumer's own `docs` MCP server, because servers resolve last-wins. One release produces two opposite outcomes.

Prefixing both names at authoring time fixes both outcomes, say `acme-migration-plan.agent.md` and `acme-docs`, and only the maintainer can do it.

## Key Takeaways

- Partition by ownership first, then re-check each piece against the client's resolution order. Ownership tells you what belongs in the package; precedence tells you whether it will run.
- Packaged agents and skills sit below project and personal definitions in Copilot CLI, while packaged MCP servers sit above the consumer's. Collisions fail silently in the first case and destructively in the second.
- The identifiers that decide a collision are an agent's file name and a skill's `name` field. Prefix both at authoring time, because the consumer cannot fix it from their side.
- Ship the version string into bug reports. Without central visibility into installations, it is the only handle on which configuration produced a behavior.
- Keep model choice and credentials out of the package, so a consumer can evaluate a new model or rotate access without waiting for a release.

## Related

- [Designing Agent Plugins to Survive Co-Installation](../patterns/agent-design/plugin-co-installation-safety.md) — the stranger-collision case, which an internal single-owner toolkit avoids and this page's local-collision case replaces
- [Per-Surface Verification of Agent Plugin Packages](../tool-engineering/per-surface-plugin-verification.md) — how far one package travels across clients, and what to test in each
- [Architecting a Central Repo for Shared Agent Standards](../workflows/central-repo-shared-agent-standards.md) — the same boundary drawn by uniformity rather than by resolution order, with five distribution mechanisms compared
- [Skill Packs: Registry Distribution Needs Pinning Discipline](skill-pack-registry-distribution.md) — the pinning and review discipline a versioned bundle still needs from its consumers
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the measured cost of shipping instruction text to every session

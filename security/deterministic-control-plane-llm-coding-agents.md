---
title: "Content-Addressed Agent Configurations (Deterministic Control Plane)"
term: "Content-Addressed Agent Configurations"
description: "Treat coding-agent configs — AGENTS.md, CLAUDE.md, .cursor/rules, copilot-instructions.md — as an installed supply chain with SHA-256 content addressing, a per-project lockfile, and declared permission tiers; the cross-repo duplication and missing-permission data make this a governance gap, not a hypothetical one."
tags:
  - security
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - Deterministic Control Plane for LLM Coding Agents
  - Lockfile for Agent Rules
  - Content-Addressed Rules Files
last_reviewed: 2026-06-28
maturity: emerging
---

# Content-Addressed Agent Configurations (Deterministic Control Plane)

> Govern coding-agent configurations as an installed supply chain — SHA-256 hashes, a per-project lockfile, and declared permission tiers.

## When This Pattern Applies

The content-addressed control plane is net-positive only inside a narrow envelope. Outside it, the lockfile machinery is overhead on an artefact whose contents do not measurably move agent behaviour ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988); [McMillan, 2026](https://arxiv.org/abs/2605.10039)). The three conditions:

| Condition | Why it matters |
|---|---|
| Agent configs are installed from a registry or shared source, not authored in-repo from scratch | Content addressing exists to refuse a hash mismatch at install time; with no install step there is nothing to gate ([Madatha, 2026 §6.1](https://arxiv.org/abs/2606.26924v1)). |
| The same configs propagate across organisational boundaries | The empirical case rests on the 10.1% cross-repo duplicate rate and the 75.5% of clone pairs crossing org boundaries. Single-org propagation is governable without the lockfile machinery via central distribution ([Madatha, 2026 §4](https://arxiv.org/abs/2606.26924v1)). |
| Agent tools honour the compiled output structure | The compiler emits canonical artefacts for Cursor, Claude Code, VS Code/Copilot, Codex, Windsurf, OpenCode, and Kiro and orders static content first for prompt-cache reuse ([Madatha, 2026 §6.4](https://arxiv.org/abs/2606.26924v1)). On a tool with no install hook, the artefact ships but the install-time gate cannot fire. |

If any condition fails, the governance value collapses into ceremony — see [When This Backfires](#when-this-backfires).

## The Gap This Closes

Agent configurations behave like an installed supply chain even though no install step governs them. A study of 6,145 AI-agent config files across 10,008 public GitHub repos found three signatures of unmanaged shared components ([Madatha, 2026](https://arxiv.org/abs/2606.26924v1)):

| Signal | Measured rate | What it implies |
|---|---|---|
| SHA-256 exact-duplicate paths across independent repos (fork-adjusted) | 10.1% | Configs are being copied between projects without provenance or version metadata |
| Clone pairs crossing organisational boundaries | 75.5% | The propagation surface is not within one org's review scope |
| AI configs declaring any permission scope vs. GitHub Actions workflows declaring `permissions:` | <1% vs 33% | The artefact that steers a code-writing agent has weaker permission governance than the workflow that runs the agent |
| Median commits/month for AI agent configs vs. GitHub Actions workflows | 0.4 vs 0.6 (median age confound — agent configs ~4 mo vs workflows ~17 mo) | Configs are rarely revised after initial commit, but partly because they are newer |

## The Three Governance Primitives

The control plane composes three install-time mechanisms ([Madatha, 2026 §6](https://arxiv.org/abs/2606.26924v1)):

### Content Addressing

Hash the serialised content of every installed config resource with SHA-256, independent of formatting differences across compilation targets. On fetch, recompute the hash and abort on mismatch. This is structurally identical to npm's `package-lock.json` integrity hashes ([npm Docs](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json)); the novelty is applying it to rules files that the prevalence study shows are already propagating as undeclared shared components.

### Per-Project Lockfile

A per-project lockfile records installed resources, their targets, and their origins. The file carries an HMAC-SHA256 stamp keyed to the lockfile path on the local machine — corruption detection, not cryptographic signing. Subsequent installs validate the stamp and refuse if the file has been tampered with locally.

### Declared Permission Tiers

Five tiers define strict tool allowlists, enforced at install/transform time as fail-closed errors ([Madatha, 2026 §6.3](https://arxiv.org/abs/2606.26924v1)):

| Tier | Tools | Shell | MCP |
|---|---|---|---|
| `readonly` | read / glob / grep / search | no | allowlisted only |
| `scribe` | read + scoped write/edit | no | no |
| `operations` | git / CI / deploy | yes | declared only |
| `specialist` | coding / analysis | yes | declared only |
| `orchestrator` | unrestricted | yes | yes |

A misconfigured agent fails the install step rather than reaching the IDE in an over-privileged state — the structural contrast with the GitHub Actions `permissions:` block is what the prevalence-table row above measures.

## Why It Works

Install-time content addressing closes the path between an untrusted registry or shared source and the on-disk artefact the agent loads at session start. Configurations are dependencies in practice but dependencies in name nowhere — no manifest, no integrity hash, no permission contract ([Madatha, 2026 §4](https://arxiv.org/abs/2606.26924v1)). Without an install gate, a tampered shared `.cursor/rules` file lands silently and runs as authoritative context the next session start. The mechanism shape is already proven in the package-manager domain — the contribution is the recognition that agent rules files now meet the empirical bar (cross-org propagation, structural duplication, no integrity check) that made integrity hashes worth adding to `package-lock.json` in the first place.

Scope matters: the control plane does not claim to improve compliance — McMillan's factorial study shows file structure does not measurably move it within realistic sizes ([McMillan, 2026](https://arxiv.org/abs/2605.10039)). It claims to govern *which bytes* are loaded. Those are different problems and need different defences.

## When This Backfires

The control plane imposes governance on an artefact whose behavioural impact is weak when read alone. Six conditions collapse the value:

- Single-developer or short-lived repos. A `CLAUDE.md` that lives for two weeks with one contributor is not propagating anywhere; the lockfile ceremony costs more than it saves.
- Greenfield scaffolding flows. When the agent is expected to author `.claude/`, `.cursor/rules/`, and `AGENTS.md` from scratch, fail-closed hash-mismatch enforcement fires on every legitimate authoring step. The pattern is for *installed* registry resources, not initial creation — same dynamic as [Gate Agent Writes to Executable Config Files](gate-agent-writes-to-executable-config.md).
- The artefact's behaviour impact is weak to begin with. Context files do not generally improve task success and add ~20% inference cost ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)); rearranging them within realistic sizes is compliance-neutral ([McMillan, 2026](https://arxiv.org/abs/2605.10039)). Teams catch real failures by deleting bloat, segmenting sessions, and moving hard constraints into [hooks for enforcement](../instructions/enforcing-agent-behavior-with-hooks.md).
- Local-integrity-only HMAC is not a signature. The lockfile stamp uses a machine-local key. An attacker who controls the registry the configs are fetched from can still poison the bytes upstream — the paper acknowledges this in §8 ([Madatha, 2026](https://arxiv.org/abs/2606.26924v1)). The same threat closes via [Tool Signing and Signature Verification](tool-signing-verification.md) on the registry side.
- Confounded prevalence data. Agent configs in the sample have a median age of ~4 months vs ~17 months for Actions workflows; the "0.4 vs 0.6 commits/month" headline partly reflects newness, not stagnation ([Madatha, 2026 §7.4](https://arxiv.org/abs/2606.26924v1)).
- Single-source proposal, no independent production deployment. The Rel(AI)Build proposal is one paper; "developer outcomes remain future work" per the paper itself ([Madatha, 2026 §8](https://arxiv.org/abs/2606.26924v1)). Practitioner blogs and changelogs through 2026-06 do not name lockfiles for `.cursor/rules` — adopt as `emerging`, not as `established`.

## Differentiation From Adjacent Patterns

| Page | Surface it covers |
|---|---|
| [Configuration Smells in AGENTS.md Files](../patterns/anti-patterns/configuration-smells-agents-md.md) | Defects *within* one config file; intra-file content audit |
| [Gate Agent Writes to Executable Config Files](gate-agent-writes-to-executable-config.md) | Write-time gating of agent edits to *execution-grant* config (`.npmrc`, `.devcontainer/`) inside one workspace |
| [Prompt Governance via PRs](../instructions/prompt-governance-via-pr.md) | PR-based review of *one repo's* instruction file; the change-management surface |
| [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) | Adversarial payloads hidden in shared *skill* registries |
| [Agent-Emitted Dependency Ranges](agent-emitted-dependency-ranges.md) | Floating ranges in the *application's* `package.json`; orthogonal supply-chain layer |
| This page | *Cross-repo propagation of agent rules files as undeclared shared components* — install-time integrity, lockfile, and declared permission tiers |

## Key Takeaways

- 10.1% of agent config paths are SHA-256 exact duplicates across independent repos and 75.5% of clone pairs cross organisational boundaries — configs propagate as undeclared shared components ([Madatha, 2026](https://arxiv.org/abs/2606.26924v1)).
- Less than 1% of AI agent configs declare any permission scope, compared with 33% of GitHub Actions workflows declaring `permissions:` — the artefact steering the code-writing agent has weaker permission governance than the workflow running it.
- The control plane composes three install-time primitives — SHA-256 content addressing, a per-project lockfile with an HMAC-SHA256 stamp, and five fail-closed permission tiers (`readonly | scribe | operations | specialist | orchestrator`) — emitted to seven IDE targets.
- The pattern applies only when configs are installed from a registry or shared source, propagate across org boundaries, and target tools that honour the compiled output structure. Single-developer repos, greenfield scaffolding, and tools with no install hook do not gain from it.
- HMAC is *local* integrity, not a signature — the registry side still needs separate cryptographic signing to close the upstream-poisoning leg of the threat model.

## Related

- [Configuration Smells in AGENTS.md Files (Six-Smell Catalog)](../patterns/anti-patterns/configuration-smells-agents-md.md) — intra-file defect catalogue; the complementary surface to this page's cross-repo dimension.
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — write-time gating for execution-grant files; same supply-chain concern, different action class.
- [Prompt Governance via PRs](../instructions/prompt-governance-via-pr.md) — PR-based review of instruction file changes within one repo.
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — adjacent supply-chain page; manifest-side controls vs this page's config-side controls.
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — adversarial registry payloads in skills, the closest threat-model analogue.
- [Tool Signing and Signature Verification](tool-signing-verification.md) — cryptographic signing as the upstream complement to local HMAC integrity.
- [Empirical Baseline: How Developers Configure Agentic AI Coding Tools](../instructions/empirical-baseline-agentic-config.md) — the sibling prevalence study covering *under*-configuration of the same artefact.

---
title: "Unversioned Scaffolding Commands Pull Stale Templates"
term: "Unversioned Scaffolding"
description: "Agents that run npx without pinning a version silently scaffold years-old project templates when the runtime falls outside the latest release's engines window."
aliases:
  - unversioned npx scaffolding
  - silent scaffold downgrade
  - stale scaffold templates
tags:
  - anti-pattern
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-14
maturity: emerging
---

# Unversioned Scaffolding Commands Pull Stale Templates

> Unpinned `npx` scaffolding silently resolves to old versions when the runtime falls outside the latest engines window; agents treat the obsolete output as ground truth.

When an agent runs `npx create-something` with no `@version`, it assumes "no version means latest". npm's resolver does not work that way. It walks back the manifest list to the most recent version whose `engines.node` field satisfies the current Node runtime. On an older or mismatched runtime, that can be a release that shipped years before the latest tag.

## The pattern

Coding agents reach for scaffolding generators the way developers do: `npx create-next-app`, `npx create-react-app`, `npx @microsoft/generator-sharepoint`, `pnpm create vite`. Most tool READMEs document the unpinned form, so the agent reproduces what it sees. When the command succeeds and emits a project tree, the agent treats the result as canonical and continues, wiring routes, adding tests, and deploying CI against whatever structure landed on disk.

## Why it fails

The npm CLI's manifest resolver, [npm/npm-pick-manifest](https://github.com/npm/npm-pick-manifest), prefers the `defaultTag` (`latest`) when its manifest satisfies the requested range. It then prioritizes versions whose `engines` requirement the active runtime satisfies. `nodeVersion` defaults to `process.version`. When upstream tightens `engines.node` faster than a runtime upgrades — a common situation in long-lived agent containers, default CI runners, and devcontainers — the resolver walks the version list backwards to the most recent published version whose `engines.node` does satisfy. That version can be old.

The case study in 'Your agent just scaffolded a project from 2020' ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/your-agent-just-scaffolded-a-project-from-2020)) documents an agent receiving SharePoint Framework `v1.11.0` (July 2020) instead of `v1.23.0` because the test machine's Node version sat outside the latest generator's engines window. The command exited cleanly. As the Microsoft writeup puts it: "All the agent sees is output. Command ran, exit code 0, files appeared. Done."

Two failure modes follow:

- Silent obsolescence: no warning, no diagnostic, no telemetry that the resolver fell back. The next agent decision treats the obsolete project shape as authoritative.
- Pattern propagation: once the agent has an old template on disk, it replicates the deprecated patterns elsewhere. The [Pattern Replication Risk](pattern-replication-risk.md) failure compounds the cost.

This is distinct from two existing staleness modes. It is not stale retrieval ([Stale Repository Retrieval Induces Incorrect Code](../../context-engineering/repository-level-retrieval-code-generation.md)), where a RAG index serves obsolete snippets. It is not config drift ([Stale AI Configuration Artifacts](stale-ai-configuration-artifacts.md)), where CLAUDE.md describes code that has moved. This is a generation-time resolver fallback — the failure happens at scaffold time, not at retrieval or read time, and the artifact is created wrong from minute one.

## Why it works (the remediation mechanism)

Three structural controls close the gap, all rooted in the same observation: the resolver behavior is documented and deterministic, so the failure is preventable at the boundary.

- Pin the entry point. `npx create-next-app@15.3` skips the engines-fallback path entirely — the resolver is given a single version to consider. Microsoft's blog recommends pinning in prompts and in agent tool extensions.
- Pin the runtime. A `.nvmrc` or `.node-version` file, with a version manager that auto-switches, keeps `process.version` aligned with the engine window the latest generator publishes for. With both ends aligned, the unpinned form returns latest.
- Verify after generation. A post-scaffold check reads the generated `package.json` and compares it against the registry's `latest`. This is the only one of the three that catches the failure when both pins are missed.

## When this backfires

The fix is not free, and the failure surface is narrower than "every `npx` call".

- Mature, version-stable generators on locked runtimes. When Node and the generator both float to latest and the runtime is current, the unpinned form returns the same thing as `@latest`. The pin is dead weight that ages the prompt — every "scaffold a Next app" prompt in the library decays the day Next.js ships a major.
- Generators that download from a branch, not a published version. [Vercel/Next.js Discussion #35794](https://github.com/vercel/next.js/discussions/35794) documents that `create-next-app` pulls the project template from the canary branch directly; pinning the CLI version with `npx create-next-app@X` does not pin the generated `next` version on disk. The post-scaffold verification step is the load-bearing control here.
- Solo developers verifying scaffold output by eye. The silent-failure mode requires that nobody check `package.json` after generation. A human glancing at the version field catches this without instrumentation.
- Pinning everywhere is not a security panacea. [Pinning Is Futile (arxiv:2502.06662)](https://arxiv.org/pdf/2502.06662) finds that pinning direct dependencies can increase exposure to malicious package updates in larger graphs. The recommendation here is to pin the scaffolder entry point — not to extend pinning across the entire dependency tree.

## Example

Before — unpinned scaffolder, mismatched runtime:

```bash
# Agent prompt: "Scaffold a SharePoint Framework project."
$ npx @microsoft/generator-sharepoint --solution-name MyWebPart
# Generator installed.
# Files written.
# $ echo $?
# 0
```

The agent moves on. The generated `package.json` carries `@microsoft/sp-core-library` at the 2020 version. Every component the agent now writes follows a structure deprecated five years ago.

After — pinned entry point, post-scaffold verification:

```bash
# Agent prompt: "Scaffold a SharePoint Framework project. Pin to the latest
# generator on npm. After generation, read package.json and compare the
# scaffolder version against `npm view @microsoft/generator-sharepoint version`.
# If they differ, stop and report."
$ npx @microsoft/generator-sharepoint@latest --solution-name MyWebPart
$ node -e "console.log(require('./package.json').devDependencies['@microsoft/generator-sharepoint'])"
# ^1.23.0
$ npm view @microsoft/generator-sharepoint version
# 1.23.0
```

The pinned entry point skips the engines-fallback walkback. The verification step catches the residual cases — branch-pulled templates, registry mirror drift — where the pin alone is not enough.

## Key Takeaways

- npm's resolver prefers an engines-compatible older version over a latest-tagged version whose engines window excludes the active Node — documented in [npm/npm-pick-manifest](https://github.com/npm/npm-pick-manifest).
- Unpinned `npx` scaffolding can silently produce a years-old project structure; the agent sees exit code 0 and treats the result as ground truth ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/your-agent-just-scaffolded-a-project-from-2020)).
- Pin the scaffolder entry point, pin the runtime via `.nvmrc`/`.node-version`, and verify the resolved version in the generated `package.json` against the registry's latest — the three together close the failure mode.
- This is a generation-time staleness, distinct from retrieval staleness and config drift; the artifact is wrong from the moment it lands.

## Related

- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — sibling staleness mode at the config-drift layer; the fix shape (verify-references-against-current) is mechanistically similar.
- [Repository-Level Retrieval for Code Generation](../../context-engineering/repository-level-retrieval-code-generation.md) — its stale-retrieval case study is the sibling staleness mode at the retrieval layer; co-retrieval of current evidence is the analogue of post-scaffold verification.
- [Pattern Replication Risk](pattern-replication-risk.md) — the compounding failure: once a stale template is on disk, the agent reproduces its deprecated shapes elsewhere.
- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — broader framing: every generator output crosses the agent's read boundary as authoritative content unless something checks it.
- [Cargo Cult Agent Setup](cargo-cult-agent-setup.md) — when scaffold output is copied into agent configuration without understanding, the resolver bug becomes load-bearing across sessions.

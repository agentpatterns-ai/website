---
title: "Skill Packs: Registry Distribution Needs Pinning Discipline"
term: "Skill Pack Pinning"
description: "A registry-installed skill pack gives a team one updatable bundle. The version pin, the review gate, and the size limit are what the team has to add."
aliases:
  - Registry-Distributed Skill Packs
  - Skill Pack Governance
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-06
maturity: emerging
---

# Skill Packs: Registry Distribution Needs Pinning Discipline

> A skill pack gives a team one addressable, updatable bundle; pinning, review, and a size limit are what make it safe to standardize on.

A skill pack is a named bundle of agent skills published to a registry, installed by one command and refreshed by another. Vercel shipped packs to the `skills.sh` registry on 4 August 2026: a pack holds public or private skills, gets its own registry URL, installs with `npx skills add https://skills.sh/p/<pack-id>`, and can be shared "with anyone, or with your Vercel organization to standardize the skills used across your team's projects" ([Vercel changelog](https://vercel.com/changelog/skill-packs-are-now-available)). That turns a team's skill set into an addressable artifact. It does not make that artifact a dependency you can pin, reproduce, or review.

## When this applies

Reach for a pack when several repositories or several developers need the same skills and the copies have already drifted apart. Three conditions decide whether it repays its overhead:

- One owner decides what the bundle contains and when its contents change.
- Every install resolves to a tag or a commit, so an update is a decision someone makes rather than something that happens.
- The bundle stays small, because installed skill count is what degrades agent behavior.

A single team in one repository already gets versioning, review, and rollback from git on a handful of markdown files. There the pack adds a channel without removing any work.

## What the channel supplies

The two live routes differ in how much dependency machinery they hand you.

| Property | `skills.sh` CLI route | Claude Code plugin marketplace |
|---|---|---|
| Version identity | none per entry — the lock stores a source and a content hash | `version` in `plugin.json`, then the marketplace entry, then the commit SHA |
| Pin | optional `ref` on the lock entry; a branch floats, a tag or SHA holds | `source.sha` on the marketplace entry |
| Update detection | recomputed folder hash compared against the stored one | resolved version keys the cache, and a matching version skips the plugin |
| Restore from record | `experimental_install`, with the promotion to `install` and `ci` unmerged | reinstall from the marketplace entry |
| Admin allowlist | absent from the CLI reference | `strictKnownMarketplaces` in managed settings |

The `skills.sh` lock file is real but thin. A `skills-lock.json` entry is typed `{ source, sourceUrl?, ref?, sourceType, skillPath?, computedHash, subagents?, wellKnownDigest? }`, where `computedHash` is a SHA-256 over every file in the skill folder ([src/local-lock.ts](https://github.com/vercel-labs/skills/blob/main/src/local-lock.ts)), and the [CLI reference](https://github.com/vercel-labs/skills) documents no organization-level allowlist. Restoring a project from the lock is still filed as missing: "skills-lock.json exists to track installed skills and their sources, but there is no command to restore skills from it" ([vercel-labs/skills#549](https://github.com/vercel-labs/skills/issues/549), open). The pull request promoting the restore command out of `experimental_install` was still unmerged as of this page's review date ([vercel-labs/skills#564](https://github.com/vercel-labs/skills/pull/564)).

## Why it works

A stable version identity, not the registry, is what makes a shared skill set governable. Claude Code's plugin system states the causal chain outright: a plugin's resolved version determines "cache paths and update detection: if the resolved version matches what a user already has, `/plugin update` and auto-update skip the plugin", and resolution falls back through `plugin.json`, the marketplace entry, then the commit SHA ([Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)). Because identity keys the cache, an unchanged identity produces no change on any machine, and a changed one produces the same change everywhere at a moment the publisher picked. Pinning `source.sha` freezes that identity. The `skills.sh` route reaches for the same effect with weaker parts: `npx skills update` re-fetches at the stored `ref`, recomputes the folder hash, and reinstalls when the two disagree ([src/update.ts](https://github.com/vercel-labs/skills/blob/main/src/update.ts)), so a tag or SHA in `ref` pins and a branch does not. Without an identity of that kind a pack is a download, and its update command is a fetch of whatever is there now.

## When this backfires

- Bulk-installing a large pack to standardize a team. Every skill in the bundle joins the selection pool whether anyone calls it or not, and pass rate drops by 21% when scaling from an oracle skill set to a 202-skill library, averaged over Haiku 4.5 and Sonnet 4.6 on SkillsBench ([Song & Wei, arxiv:2605.24050v2](https://arxiv.org/abs/2605.24050v2)).
- Blaming the context window for that damage. Skill shadowing accounts for up to 68% of the degradation and is the only component whose confidence interval excludes zero, while context overhead "does not separate from zero at any library size" ([arxiv:2605.24050v2](https://arxiv.org/abs/2605.24050v2)). Trimming the pack helps; a bigger window does not.
- Reading registry admission as vetting. Semantic evasion lets malicious skills avoid a blocking verdict in 36.5% to 100% of cases, and a context-overflow strategy got 87.1% of them labeled clean by exploiting a reviewer that sees only the first 10K characters of a long `SKILL.md` ([Saha et al., arxiv:2605.11418v1](https://arxiv.org/abs/2605.11418v1)). The same text moved adversarial variants to an 86% pairwise win rate in retrieval, so registry ranking is no safer a signal than the verdict.
- Installing by symlink under a code-review culture. The CLI "creates symlinks from each agent to a canonical copy" by default and offers `--copy` for independent copies ([vercel-labs/skills](https://github.com/vercel-labs/skills)). With symlinks the bytes the agent reads never appear in a pull request, so the review gate the team believes it has does not cover them.
- Onboarding and CI. A fresh clone cannot reproduce the recorded skill set while the restore command remains unmerged ([vercel-labs/skills#549](https://github.com/vercel-labs/skills/issues/549)).

## Example

A pinned marketplace entry shows the discipline where the channel supports it. The `sha` field freezes the plugin's identity, so nothing changes on any developer machine until someone edits this file ([Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)):

```json
{
  "name": "code-formatter",
  "source": {
    "source": "github",
    "repo": "acme-corp/code-formatter",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}
```

On the `skills.sh` route the same discipline is assembled by hand. Install with `--copy` so the skill files land in the repository and reach code review, commit `skills-lock.json`, then treat the diff that `npx skills update` produces as a change to approve rather than a refresh to run. Vercel's own guidance points the same way: read skills before installing, and be careful with `scripts/`, because they can run commands ([Vercel: Agent Skills](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context)).

## Key Takeaways

- Packs solve distribution. Pinning, review, and pruning stay the team's problems.
- On the `skills.sh` route the pin is an optional `ref` and the record is a content hash, with no per-entry version and no merged restore command.
- Claude Code plugin marketplaces already carry version resolution, `source.sha` pinning, release channels, and an admin allowlist. Prefer that route when governance matters more than the breadth of agents supported.
- Keep the installed set small. Selection failure, not context size, is what a large library costs you ([arxiv:2605.24050v2](https://arxiv.org/abs/2605.24050v2)).
- A registry listing is a discovery signal. Admission scanning is evadable, so a human still reads the skill ([arxiv:2605.11418v1](https://arxiv.org/abs/2605.11418v1)).

## Related

- [Agent Config as a Managed Supply Chain](agent-config-as-managed-supply-chain.md) — the same hashing-and-pinning discipline applied to `CLAUDE.md` and `AGENTS.md` rather than to installed skills
- [Skill Reuse as Vendored Forking](../tool-engineering/skill-reuse-as-vendored-forking.md) — what happens to a copied skill once the update channel goes unused
- [Enterprise-Managed Plugin Governance for Agent CLIs](../security/enterprise-managed-plugin-governance.md) — the admin-side half: curating marketplaces and force-enabling plugins before any download
- [Skill Library Evolution: Lifecycle Governance for Agents](../tool-engineering/skill-library-evolution.md) — how to prune the installed set that a pack keeps growing
- [Trusting a Skill Scanner's Verdict as a Security Judgment](../patterns/anti-patterns/skill-scanner-verdict-not-security-judgment.md) — why a registry's clean scan is a signal rather than a decision

---
title: "Dependabot Version Updates for Agent Package Dependencies"
term: "Agent Package Dependency Version Updates"
description: "Configure Dependabot for APM git dependencies and review instruction changes in each update. Know which manifest entries and lockfile updates it supports."
tags:
  - instructions
  - tool-agnostic
  - automation
last_reviewed: 2026-11-06
maturity: emerging
---

# Dependabot Version Updates for Agent Package Dependencies

> Dependabot version updates propose changes to supported APM agent-package dependencies, with explicit limits on manifest forms and lockfile handling.

APM packages can carry agent skills, prompts, and instructions. Dependabot opens update pull requests for supported git dependencies in `apm.yml`. GitHub announced this support on November 3, 2026, for version updates only. It does not provide APM security updates ([GitHub announcement](https://github.blog/changelog/2026-11-03-dependabot-version-updates-support-agent-package-manager/)).

## Configure the manifest directory

Use `apm` as the ecosystem value and point `directory` at the folder containing `apm.yml`. This weekly root-directory configuration follows GitHub's [version-update configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuring-dependabot-version-updates) and [APM announcement](https://github.blog/changelog/2026-11-03-dependabot-version-updates-support-agent-package-manager/):

```yaml
version: 2
updates:
  - package-ecosystem: "apm"
    directory: "/"
    schedule:
      interval: "weekly"
```

The configuration belongs in `.github/dependabot.yml`. It schedules proposals; it does not authorize merging them.

## Check what the updater covers

Both `dependencies.apm` and `devDependencies.apm` are supported. Ref type determines the update ([GitHub support reference](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories#apm)):

| Pin | Update behavior |
|---|---|
| SemVer tag | Latest supported SemVer tag, including package-scoped tags |
| Full commit SHA | Commit of the latest annotated, non-prerelease release tag |
| Branch | Latest branch commit through the lockfile; manifest keeps the branch name |

Dependabot regenerates an existing `apm.lock.yaml` with `apm lock`; it does not create a missing lockfile. Branch updates therefore require one. Unsupported forms include object maps, MCP entries, missing refs, local paths, Azure DevOps entries, abbreviated SHAs, and insecure clone schemes. The reference lists further YAML and default-registry restrictions ([complete exclusions](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories#apm)).

## Review the package's behavior

Treat the PR as a change to the agent's instructions. This review checklist follows from the package contents and update boundaries above:

- Inspect the resolved ref and the instruction or skill diff, not only the manifest version.
- Check whether the package adds tool use, external destinations, or new execution steps.
- Test the changed behavior with your own representative tasks before merging.
- Track unsupported manifest entries separately; absence of an update PR is not evidence that they are current.

APM support applies across tools that consume these packages. The GitHub announcement does not make it a Copilot-only update mechanism.

## Key Takeaways

- Keep a lockfile when relying on branch-ref updates.
- Separate version freshness from security review.
- Review the package content that the resolved ref introduces.

## Related

- [Skill File Linting](skill-file-linting.md) — inspect the instruction artifact
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — enforce runtime constraints separately
- [Dependency-Update Repair Routing](../workflows/dependency-update-repair-routing.md) — decide which update PRs need repair work

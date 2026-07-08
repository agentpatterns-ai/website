---
title: "Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface"
description: "AI assistants default to caret and tilde ranges in manifests because `npm install` and equivalents do; for an application with a bump-bot, replacing the range with an exact pin plus a lockfile-enforced install narrows the window in which a freshly-compromised release lands in a build."
tags:
  - security
  - tool-agnostic
  - supply-chain
aliases:
  - agent-written caret ranges
  - LLM dependency prefix risk
  - caret tilde supply chain
last_reviewed: 2026-06-01
maturity: established
---

# Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface

> For an application with a bump-bot, replace agent-emitted caret-or-tilde ranges with exact pins plus a lockfile-enforced install — the floating range admits future-compromised releases.

This pattern applies in one specific shape: deployable applications with an active bump-bot and a lockfile-enforced install command in CI. It is wrong for libraries and net-neutral for very large dependency graphs without a transitive-side defense ([Renovate docs](https://docs.renovatebot.com/dependency-pinning/); [He et al. — arXiv:2502.06662](https://arxiv.org/abs/2502.06662)).

## When the pattern applies

| Condition | Why it matters |
|---|---|
| The repo ships an application or service, not a published library | Exact pins in a library's `package.json` propagate version conflicts to every consumer. Renovate recommends `rangeStrategy=widen` for libraries for this reason ([Renovate docs](https://docs.renovatebot.com/dependency-pinning/)). |
| A bump bot is wired (Dependabot, Renovate, or equivalent) | Exact pins without an automated bump path ossify — they age into known-CVE territory faster than ranges do ([LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md)). |
| CI installs with the lockfile-enforcing command — `npm ci`, `uv sync`, `poetry install --no-update`, `cargo build --locked` — not the resolve-and-install default | Without lockfile enforcement, the exact pin in the manifest is moot because the install path can still resolve against the registry. |

If any condition fails, fix that gap first. The pattern only narrows the trust boundary when all three hold.

## Why it works

A caret range (`^1.2.3`) accepts every backward-compatible release up to the next major. A tilde range (`~1.2.3`) accepts every patch release. A wildcard accepts almost anything. Each range is a standing authorization for whatever version of that package is published next — including, by construction, a version that does not exist yet and that no one has reviewed ([Sourcegraph: "Dependency prefixes are a supply chain risk"](https://sourcegraph.com/blog/dependency-prefix-supply-chain-risk)).

The trust boundary closes only when two surfaces both narrow:

- Manifest side: the version specifier names a single release, not a set.
- Install side: the install command honors the lockfile rather than re-resolving against the registry. `npm install` writes new ranges and silently resolves them at install time. `npm ci` fails if the lockfile and manifest disagree, and installs exactly what the lockfile records ([npm docs — `npm ci`](https://docs.npmjs.com/cli/v11/commands/npm-ci); [Echo Effect: Axios Supply Chain Attack](https://www.echoeffect.net/blog/axios-npm-supply-chain-attack)).

The axios attack of 2026-03-31 is the empirical demonstration: malicious versions were live on the registry for roughly three hours. Any environment that ran `npm install` against a caret range during that window resolved to the compromised release; environments that ran `npm ci` against a lockfile recorded before the attack were unaffected ([Echo Effect](https://www.echoeffect.net/blog/axios-npm-supply-chain-attack); [TurboDocx](https://www.turbodocx.com/blog/axios-npm-supply-chain-attack-how-to-protect-your-projects)).

## Why agents emit ranges by default

`npm install <pkg>` writes `^<version>` to `package.json` unless you set `save-exact=true` in `.npmrc`. This has been the npm default since the 1.x era ([npm config — `save-prefix`](https://docs.npmjs.com/cli/v11/using-npm/config#save-prefix); [bytearcher: semver caret explainer](https://bytearcher.com/articles/semver-explained-why-theres-a-caret-in-my-package-json/)). Agents that shell out to `npm install`, or that copy from Stack Overflow and tutorial training data, inherit that default. The same reflex appears for tilde in Composer and for unbounded ranges in older `pip` snippets.

Compounding the issue: AI assistants specify a version in only ~9% of Developer-ChatGPT conversations and 6.45–59.19% of manifest tasks ([arXiv:2401.16340](https://arxiv.org/abs/2401.16340); [arXiv:2605.06279](https://arxiv.org/abs/2605.06279)). When they do, they reach for the install-command default. Lockfile commits are also frequently missing from agent-authored PRs, leaving CI to resolve fresh.

## What to change

| Layer | Change | Effect |
|---|---|---|
| Project `.npmrc` (or equivalent) | `save-exact=true` for npm; `[tool.uv] frozen = true` semantics via `uv sync`; explicit Poetry `--no-update` in CI | The next `npm install <pkg>` an agent runs writes `1.2.3`, not `^1.2.3`. The default reflex now points the right way. |
| Manifest | Replace existing `^` and `~` ranges with exact versions for the next bump cycle | Each subsequent update becomes a reviewed diff, not a silent resolution. |
| Lockfile | Commit it. Install with `npm ci` / `uv sync` / `poetry install --no-update` / `cargo build --locked` in CI | The install path stops trusting the manifest range — and stops trusting whatever the registry serves at install time. |
| Instructions file | Add a one-line rule to `AGENTS.md` / `CLAUDE.md` / `copilot-instructions.md`: "emit exact versions in manifests; never `^` or `~`. Commit lockfile changes alongside manifest changes." | The instruction file is the cheapest place to redirect the default reflex. |
| Pre-commit / CI hook | Reject diffs to `package.json` / `requirements.txt` / `pyproject.toml` that add `^`, `~`, or `*` prefixes | A deterministic gate catches the reflex when the instruction doesn't. |
| Optional: `min-release-age` | npm v11.10.0 added `min-release-age=7` — refuses any release published less than seven days ago ([Defending Against NPM Supply Chain Attacks](https://www.armorcode.com/blog/defending-against-npm-supply-chain-attacks-a-practical-guide)) | Complements pinning for the transitive frontier; the axios window was three hours, so a seven-day delay would have blocked it entirely. |

## When this backfires

- Libraries and SDKs. Exact pins in a published library's manifest propagate conflicting constraints to every consumer. Renovate documents this case explicitly: `rangeStrategy=widen` for libraries, `rangeStrategy=pin` for applications ([Renovate docs](https://docs.renovatebot.com/dependency-pinning/)). Apply this pattern to applications only.
- Very large transitive graphs. He, Vasilescu and Kästner's FSE 2025 study simulated dependency resolutions across the npm registry over a 12-month window. It found that pinning direct dependencies is ineffective against malicious transitive updates for projects with ≥498 direct+transitive dependencies — 26% of GitHub repositories in their dataset ([arXiv:2502.06662](https://arxiv.org/abs/2502.06662)). At this scale, pinning the manifest does not close the attack surface. Pair the pattern with `min-release-age`, a curated mirror, or scanner-as-MCP-server gating ([Scanner-as-MCP-Server](scanner-as-mcp-server.md)) to cover the transitive frontier.
- No bump-bot in the loop. Exact pins without Dependabot or Renovate age silently — the manifest stops tracking upstream security patches and accumulates known CVEs ([LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md)). The exact-pin recommendation requires the auto-update feedback loop to be net-positive.
- Throwaway prototypes. Lockfile-enforced installs and pin-everything discipline add friction for code that never leaves a laptop. The pattern targets deployable applications, not scratch scripts.
- Ecosystems with strong default lockfile discipline. `cargo` ships `Cargo.lock` discipline. `uv add` already writes a resolved entry to `uv.lock`. When the install command (`cargo build --locked`, `uv sync`) already enforces the lockfile, the agent's range in the manifest is harmless. The fix here is "commit and enforce the lockfile" — not "rewrite the manifest".

## Example

Before — agent runs `npm install axios` and commits the default output:

```json
{
  "dependencies": {
    "axios": "^1.12.0"
  }
}
```

CI runs `npm install` (not `npm ci`). On the morning of 2026-03-31, between 00:21 and 03:15 UTC, the build pulls a compromised release because the caret range matches the malicious version ([Echo Effect: Axios Supply Chain Attack](https://www.echoeffect.net/blog/axios-npm-supply-chain-attack)).

After — `save-exact=true` in `.npmrc`, lockfile committed, CI uses `npm ci`:

```json
{
  "dependencies": {
    "axios": "1.12.0"
  }
}
```

```bash
# .npmrc
save-exact=true
min-release-age=7
```

```yaml
# .github/workflows/ci.yaml — install step
- run: npm ci
```

The next `npm install <pkg>` an agent runs writes `1.12.0`, not `^1.12.0`. CI installs exactly what the lockfile records. Renovate opens a PR when `1.12.1` ships; the diff is reviewed before the new version reaches `main`. The seven-day age floor refuses any release younger than the attack window.

## Key Takeaways

- Agents emit `^` ranges because `npm install` writes `^` by default — fix the default with `save-exact=true` in project `.npmrc`, not page-by-page in manifests ([npm config docs](https://docs.npmjs.com/cli/v11/using-npm/config#save-prefix)).
- The trust boundary needs both halves: exact pin in the manifest and lockfile-enforced install (`npm ci`, `uv sync`, `cargo build --locked`). Either alone leaks ([Sourcegraph](https://sourcegraph.com/blog/dependency-prefix-supply-chain-risk); [npm docs — `npm ci`](https://docs.npmjs.com/cli/v11/commands/npm-ci)).
- The pattern applies to applications with a bump-bot wired. Libraries and bot-less repos are the documented failure modes — Renovate recommends `widen` for libraries, and the [LLM-Pinned Library Versions](llm-pinned-vulnerable-versions.md) failure is pinning without bumping.
- Pinning is not enough on its own at scale: He et al. (FSE 2025) found it ineffective against transitive attacks for 26% of GitHub repos. Pair it with `min-release-age` or a curated mirror for the transitive frontier ([arXiv:2502.06662](https://arxiv.org/abs/2502.06662)).
- This is the range-vs-exact axis. The orthogonal axis — exact pins that point at CVE-bearing versions because the training prior preferred them — is [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md). A hardened pipeline addresses both.

## Related

- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — the orthogonal axis: exact-but-CVE-bearing pins from the training prior
- [Dependency Gap Validation for AI-Generated Code](../verification/dependency-gap-validation.md) — the missing-dependency complement; the same lock-then-resolve workflow covers transitive pulls
- [Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools](scanner-as-mcp-server.md) — the agent-side scanning surface that complements lockfile enforcement
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — the broader frame; a permissive range plus untrusted-content tool plus egress is one shape of the trifecta
- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the PR-time gate where manifest-diff inspection and CVE audit land

## Sources

- [Sourcegraph: "Dependency prefixes are a supply chain risk: let's fix them"](https://sourcegraph.com/blog/dependency-prefix-supply-chain-risk) (2026-05-22) — primary thesis on range prefixes as a trust-boundary problem
- [arXiv:2502.06662 — He, Vasilescu, Kästner: "Pinning Is Futile" (FSE 2025)](https://arxiv.org/abs/2502.06662) — counter-finding: pinning ineffective against transitive attacks for ≥498-dep projects (26% of GitHub repos)
- [Renovate — Should you Pin your JavaScript Dependencies?](https://docs.renovatebot.com/dependency-pinning/) — codifies the application-vs-library split (`rangeStrategy=pin` vs `widen`)
- [OWASP NPM Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html) — independent confirmation of `save-exact` + `npm ci` recommendation
- [Echo Effect: Axios Supply Chain Attack](https://www.echoeffect.net/blog/axios-npm-supply-chain-attack) — empirical case study, 2026-03-31 three-hour exposure window
- [TurboDocx: The Axios Supply Chain Attack](https://www.turbodocx.com/blog/axios-npm-supply-chain-attack-how-to-protect-your-projects) — corroborating post-mortem
- [arXiv:2605.06279 — Wang et al.: LLM library-version specification rates](https://arxiv.org/abs/2605.06279) — 6.45–59.19% of manifest tasks pin a version at all
- [arXiv:2401.16340 — Versions appear in only ~9% of Developer-ChatGPT conversations](https://arxiv.org/abs/2401.16340)
- [npm CLI docs — `npm ci`](https://docs.npmjs.com/cli/v11/commands/npm-ci) — lockfile-enforcing install command semantics
- [npm CLI docs — `save-prefix` config](https://docs.npmjs.com/cli/v11/using-npm/config#save-prefix) — default prefix is `^` since the 1.x era

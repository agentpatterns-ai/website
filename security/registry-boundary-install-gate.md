---
title: "Registry-Boundary Install Gates for Agent-Chosen Dependencies"
term: "Registry-Boundary Install Gate"
description: "GitHub's package firewall evaluates npm downloads against five controls. Its cooldown delays new versions; routing and removable exceptions determine which requests it checks."
tags:
  - security
  - tool-agnostic
  - supply-chain
  - arxiv
aliases:
  - package firewall
  - registry-side install gate
  - install-time package policy gate
last_reviewed: 2026-10-22
maturity: emerging
---

# Registry-Boundary Install Gates for Agent-Chosen Dependencies

> A registry-boundary install gate checks the dependency requests routed through it. Keep manifest review as a separate check.

GitHub's package firewall entered public preview on 20 October 2026. It evaluates metadata requests and package downloads against enterprise policy ([changelog](https://github.blog/changelog/2026-10-20-github-package-firewall-in-public-preview)).

## What the boundary sees

A check limited to manifest diffs sees declared names. A registry gate sees requests routed through it. GitHub's docs state: "These controls apply to all requests that pass through the firewall." The docs do not mention transitive dependencies, so whether a given install tree routes through the gate depends on the `registry=` configuration.

The gate evaluates package policy, not whether a human chose each dependency. Retain that separate review when agents select packages.

## Which controls need a prior report

Whether this layer covers the agent case is a per-control question, not a per-product one. GitHub ships five controls with these defaults ([GitHub docs](https://docs.github.com/enterprise-cloud@latest/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/protecting-endpoints-with-package-firewall)):

| Control | Default | Needs a prior report? |
|---|---|---|
| Block known malware (Advisory Database) | On | Yes |
| Block vulnerability advisories | Critical only | Yes |
| Block attestation downgrades | On | No |
| Block newly-introduced install scripts | On | No |
| Minimum package age (cooldown) | 1 day | No |

The advisory controls depend on the Advisory Database. The other three evaluate package properties without requiring a prior advisory.

Detector benchmarks measure a separate question. Across 11 tools and 6,420 malicious plus 7,288 benign packages, GuardDog reached 93.32% F1 among conventional tools. IntelGuard reached 95.98%, and combinations reached 97.02% ([arXiv:2603.27549v2](https://arxiv.org/abs/2603.27549v2)). These results do not measure GitHub's firewall or establish a ceiling for automated detection.

## Why it works

A cooldown delays installation while threats can be discovered ([GitHub docs](https://docs.github.com/enterprise-cloud@latest/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/protecting-endpoints-with-package-firewall)). It does not guarantee discovery. The detector study reports that "80.3% of malware uses no evasion because the ecosystem lacks mandatory pre-publication scanning" ([arXiv:2603.27549v2](https://arxiv.org/abs/2603.27549v2)). That measures detector-evasion techniques, not time to detection.

## The cooldown number is the control

GitHub defaults minimum package age to 1 day. Administrators can set 1 to 365 days, or 0 to disable it ([GitHub docs](https://docs.github.com/enterprise-cloud@latest/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/protecting-endpoints-with-package-firewall)).

A historical study collected 174 malicious packages across npm, PyPI, and RubyGems from November 2015 to November 2019. Packages remained available for a mean 209 days and median 67 days before public reporting ([arXiv:2005.09535v1](https://arxiv.org/abs/2005.09535v1)). This selected, cross-registry corpus cannot set an optimal cooldown for current npm installs. It shows why a short delay cannot replace other checks.

## When this backfires

- Scope. "Currently the package firewall only supports npm packages", the preview is offered to GitHub Enterprise Cloud customers including data residency, and metered billing arrives at general availability ([GitHub changelog](https://github.blog/changelog/2026-10-20-github-package-firewall-in-public-preview)). A polyglot repo that retires its repo-side gate keeps coverage on npm and loses it on Python, Go, Rust, and Maven.
- Editable routing. Endpoints opt in by pointing a `registry=` line at the firewall in a user-level `.npmrc` ([GitHub docs](https://docs.github.com/enterprise-cloud@latest/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/protecting-endpoints-with-package-firewall)), so assess whether the agent can change that configuration. GitHub separately instructs Artifactory operators to exclude remote repositories that fetch directly from npm. That instruction concerns Artifactory repository composition.
- Patch latency, in the other direction. A long cooldown blocks the release carrying the fix, a case GitHub's docs name outright: "a new package version that includes a security fix could be blocked by the minimum package age policy."
- Exception sprawl. An approver can widen a request from one version to `*`, which "broadens the exception beyond the requested version" and bypasses the policy for those versions. Administrators can review and remove exceptions under Managing approvals. The docs describe no automatic expiry.
- A narrow surface on one control. The install-script check only speaks to packages that declare install scripts, and a study of 1.63 million npm packages put that share at 2.2% ([arXiv:2112.10165v2](https://arxiv.org/abs/2112.10165v2)).

## Example

**Before** — npm resolving straight from the public registry, with no gate in the path:

```ini
# ~/.npmrc
registry=https://registry.npmjs.org
```

**After** — the same install routed through the boundary gate:

```ini
# ~/.npmrc
registry=https://package-firewall.githubapp.com/npm/enterprises/ENTERPRISE
//package-firewall.githubapp.com/npm/enterprises/ENTERPRISE/:_authToken=${GITHUB_TOKEN}
```

A block then surfaces in the npm output or the CI log with the exception URL attached ([GitHub docs](https://docs.github.com/enterprise-cloud@latest/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/protecting-endpoints-with-package-firewall)):

```text
npm notice testcontainers: 1 version blocked by package-firewall due to security policies (version cooldown). Request an override: https://github.com/enterprises/octocats/security/bypass-requests/package-firewall/new?ecosystem=npm&package=testcontainers
```

This documented example shows routing and a cooldown block for `testcontainers`. It does not demonstrate a transitive dependency install.

## Key Takeaways

- Keep manifest review and download policy as separate checks. They evaluate different inputs.
- Three of GitHub's five controls evaluate package properties without requiring a prior advisory.
- Choose a cooldown with patch latency in view. Historical reporting delays do not establish a safe waiting period.
- Audit routing configuration and package exceptions. The docs describe no automatic expiry for a `*` exception; administrators can review and remove exceptions under Managing approvals.

## Related

- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](slopsquatting-hallucinated-package-names.md) — the unknown-name case, where the gate's minimum package age applies to a newly published version
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — the repo-side half: exact pins plus a lockfile-enforced install
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — sorting safeguards by where they are evaluated, which is what makes an editable `registry=` line weaker than it looks
- [Setup Documentation as an Install-Time Attack Vector](setup-documentation-install-time-attacks.md) — the other way an install gets redirected, by editing docs rather than config
- [Unbound Approval Records](../patterns/anti-patterns/unbound-approval-records.md) — why a `*` exception needs review, since the docs describe no automatic expiry for it
- [Defense-in-Depth Agent Safety for AI Agent Development](defense-in-depth-agent-safety.md) — the general principle this is an instance of, and the test for whether two gates are independent rather than redundant

## Sources

- [GitHub package firewall in public preview](https://github.blog/changelog/2026-10-20-github-package-firewall-in-public-preview) — GitHub Changelog, 20 October 2026
- [Protecting endpoints with GitHub package firewall](https://docs.github.com/enterprise-cloud@latest/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/protecting-endpoints-with-package-firewall) — GitHub Enterprise Cloud docs
- [How Effective Are NPM Malicious Package Detectors? A Large-Scale Empirical Study](https://arxiv.org/abs/2603.27549v2) — Guo et al., arXiv:2603.27549v2
- [Backstabber's Knife Collection: A Review of Open Source Software Supply Chain Attacks](https://arxiv.org/abs/2005.09535v1) — Ohm et al., arXiv:2005.09535v1
- [What are Weak Links in the npm Supply Chain?](https://arxiv.org/abs/2112.10165v2) — Zahan et al., arXiv:2112.10165v2

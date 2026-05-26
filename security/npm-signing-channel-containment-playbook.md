---
title: "Containment Playbook: npm-to-Signing-Channel Compromise"
description: "When a worm inside npm install reaches a developer machine that can read internal repos containing signing material, the blast radius extends to the distribution channel. Isolate, rotate, freeze, re-sign, revoke, ship a forcing-function client update."
tags:
  - security
  - workflows
  - tool-agnostic
aliases:
  - dev-machine supply chain incident response
  - npm install signing certificate rotation playbook
last_reviewed: 2026-05-27
---

# Containment Playbook: npm-to-Signing-Channel Compromise

> A consumer-side supply-chain attack runs through `npm install` on a developer machine, harvests credentials, and pivots into corporate source repos. If those repos contain code-signing material, the breach reaches the distribution channel. This is the containment playbook.

## When This Playbook Applies

All four conditions must hold:

1. You ship **signed binary clients** notarized through Apple, Microsoft, or equivalent.
2. Code-signing keys are **reachable from corporate source repositories**.
3. Engineers run `npm install` (or `pip`, `bun`) against the **public registry** from machines that can reach those repos.
4. You have **endpoint telemetry** to identify which machines installed a package version after the fact.

If any fails, scope down. SaaS-only teams skip the certificate-rotation step. Teams using `trustedDependencies` allowlists ([npm 10.3+](https://mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026)) or a proxied private registry run a shorter version.

This is the **consumer-side** vector. The publisher-side compromise that hit TanStack itself was GitHub Actions cache poisoning plus OIDC token memory extraction from a CI runner ([TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)) — out of scope here.

## The Attack Chain

```mermaid
graph LR
    A[npm install] --> B[Postinstall script runs]
    B --> C[Credentials harvested]
    C --> D[Internal repo access]
    D --> E[Signing material reached]
    E --> F[Distribution channel compromised]
```

A malicious postinstall script executes with the user's full privileges before runtime controls activate. EDR is built around file-hash signatures and mass-encryption behavior; it does not catch a postinstall script inside a legitimate package manager ([SC Media](https://www.scworld.com/perspective/trusted-by-default-the-npm-attack-pattern-security-teams-miss), [Aikido](https://www.aikido.dev/blog/endpoint-security-for-developer-devices)).

The Mini Shai-Hulud worm — payload behind 170+ npm packages in May 2026, including 84 versions across 42 `@tanstack/*` packages — harvests GitHub tokens, npm credentials, Actions secrets, and cloud credentials, runs TruffleHog over the filesystem, and exfiltrates an AES-256-GCM bundle to a public GitHub repo created with a stolen token ([Datadog](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/), [Orca](https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/)).

OpenAI reported two impacted employee devices and credential exfiltration from internal repositories containing signing certificates for ChatGPT Desktop, Codex App, Codex CLI, and Atlas ([OpenAI](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/), [The Hacker News](https://thehackernews.com/2026/05/tanstack-supply-chain-attack-hits-two.html)).

## The Playbook

Execute in order. Each step has a hard exit criterion.

### 1. Isolate impacted endpoints

Identify every machine that ran an install against an affected version in the breach window. Pull it off the network. Suspend SSO sessions and refresh tokens. Do not wipe — preserve package cache and shell history for forensics.

**Exit:** every confirmed host isolated; impacted users signed out of IdP, GitHub, npm, and cloud consoles.

### 2. Rotate credentials by blast radius

Rotate in concentric circles starting from what the worm targets: GitHub PATs and SSH keys, npm tokens, Actions secrets, AWS/GCP/Azure credentials. Any secret in env vars, the SDK credential cache, or readable from disk is assumed compromised ([Datadog](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/)).

**Exit:** every credential reachable from an impacted host rotated and revoked at the issuer.

### 3. Freeze deploys

Halt automated deploys from any pipeline that touched an impacted credential. A rotation racing a deploy can ship signed-with-stolen-key binaries that pass notarization before the cert is revoked.

**Exit:** deploy workflows disabled; manual deploys gated through a small reviewer pool.

### 4. Re-sign and ship new builds

Issue new code-signing certificates. Re-sign every shipping product. Test through the update channel before announcing.

**Exit:** new builds available via auto-update on every affected product and platform.

### 5. Coordinate notarization revocation

For macOS, coordinate with Apple to block notarization using the impacted material. Fraudulent apps signed with the impacted certificate will then lack notarization and be blocked by default ([OpenAI](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/)). Equivalent steps apply for Microsoft SmartScreen, iOS distribution, and Android Play Integrity.

**Exit:** revocation confirmed by the provider; new signing material registered.

### 6. Ship the forcing-function client update

Announce a certificate-revocation deadline that forces every user to update. OpenAI gave users until **June 12, 2026** after announcing on May 13 — a ~30-day window. Short enough to close the breach window, long enough for built-in update mechanisms to reach users before launches fail ([OpenAI](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/), [The Record](https://therecord.media/openai-asks-macos-users-to-update-tanstack-npm)).

Communicate via in-app banner, email, status page, and release notes. Ship the new version before the announcement.

**Exit:** old certificate revoked on the announced date; long-tail update curve approaching baseline.

## Why It Works

A worm inside `npm install` inherits everything the user account can reach: SSH keys, tokens, cloud credentials, source-control access. If those repos contain code-signing keys, the blast radius extends from one laptop to the distribution channel.

The playbook breaks the chain at distribution. Revoking certificates and forcing a client update means signing material stolen in the breach window cannot ship a fraudulent binary to existing users — even if the attacker holds the key, the platform refuses to honor it ([OpenAI](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/), [Datadog](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/)).

## When This Backfires

- **No signed-binary distribution.** SaaS-only teams skip steps 4–6 entirely.
- **Small teams.** Coordinating notarization revocation with Apple and a 30-day forced-update cycle requires support, legal, and update-channel infrastructure small publishers lack ([TWiT](https://twit.tv/posts/tech/truth-behind-short-lived-code-signing-certificates-and-rising-costs)).
- **No endpoint telemetry on developer workstations.** Step 1 assumes you can identify which machines ran the install; dev workstations are typically under-instrumented relative to production ([Aikido](https://www.aikido.dev/blog/endpoint-security-for-developer-devices)).
- **A poorly-sized forcing-function window.** Tight deferral windows trigger backlash ([Jamf](https://community.jamf.com/general-discussions-2/forcing-macos-updates-29648)); longer than ~30 days leaves the breach window open. Size by telemetry, not gut.
- **The playbook is the fallback, not the strategy.** Per-package allowlists like `trustedDependencies` ([npm 10.3+](https://mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026)), `pnpm allowBuilds`, `@lavamoat/allow-scripts`, or sandboxed installs in disposable VMs block the postinstall script from running. Budget there first.

## Example

OpenAI's response to the May 2026 TanStack incident is the worked example of every step ([OpenAI](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/)):

| Step | What OpenAI did |
|---|---|
| 1. Isolate | Two impacted employee devices identified and contained |
| 2. Rotate | Credentials in the impacted internal source repositories rotated |
| 3. Freeze | Deploy workflows for affected products paused during cert rotation |
| 4. Re-sign | New certs issued for ChatGPT Desktop, Codex App, Codex CLI, and Atlas across Windows, macOS, iOS, Android |
| 5. Notarization | Coordinated with Apple to block further notarization of macOS apps using the impacted material |
| 6. Forcing-function | Announced May 13, 2026; revocation deadline June 12, 2026; macOS users required to update before that date |

The May 13 announcement landed two days after the May 11 compromise. Rapid initial detection made a ~30-day window viable; teams without that detection speed need a longer window, which means longer breach exposure.

## Key Takeaways

- The consumer-side dev-machine vector is structurally distinct from the publisher-side CI vector. Most public analysis covers the publisher side; this playbook covers the consumer side.
- The breach starts at `npm install` on one laptop and ends at the distribution channel when signing material is reachable from corporate repos.
- Containment runs in a fixed order: isolate, rotate, freeze, re-sign, revoke, force-update. Each step has an exit criterion; skipping ahead leaves a window open.
- A forcing-function client-update deadline closes the distribution channel. Window length trades breach exposure against user disruption.
- Per-package allowlists and sandboxed installs are cheaper than the playbook. Budget prevention first.

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — upstream control that limits how far a single compromised credential can reach
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — credential-isolation pattern that shrinks step 2's rotation surface
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — adjacent supply-chain vector targeting agent skill registries
- [Tool Signing and Signature Verification](tool-signing-verification.md) — publisher-side counterpart for tool distribution integrity
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — agent-specific failure mode that increases exposure to the same install-time threat surface

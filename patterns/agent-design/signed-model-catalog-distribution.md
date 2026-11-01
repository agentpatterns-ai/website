---
title: "Signed Model-Catalog Distribution for Agent Harnesses"
term: "Signed Model-Catalog Distribution"
description: "Fetch per-model harness settings as a signed file at runtime so vendor metadata corrections land without a client release, with the signature moving trust off the distribution host."
tags:
  - agent-design
  - security
  - claude
aliases:
  - signed model catalog
  - verified model settings fetch
  - remote model metadata catalog
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-30
maturity: adopted
status: current
---

# Signed Model-Catalog Distribution for Agent Harnesses

> A harness fetches its per-model settings as a signed file at runtime, so vendor metadata corrections land without waiting for a client release.

Per-model settings decide how a harness treats a model, down to the shape of the system prompt it builds. Bundle that table into the client and it goes stale between releases. Fetch it at runtime and the fetch becomes a configuration-injection surface. A signature on the fetched file is what makes the second option safe to take, and it covers less than the word suggests.

## When the pattern applies

Claude Code 2.1.311 (October 26, 2026) applies it to four backends: "Changed Claude Code on Bedrock, Mantle, Vertex, and Foundry to load model settings from a signed file on downloads.claude.ai; set CLAUDE_CODE_MODEL_CATALOG=off to turn this off" ([Claude Code changelog 2.1.311](https://code.claude.com/docs/en/changelog#2-1-311)). The first-party API is absent from that line, and the opt-out ships with the feature.

That scope is the decision rule. Reach for a fetched catalog when all three conditions hold:

- You need vendor metadata corrections between client releases.
- Your clients can reach the vendor's distribution host when a session starts.
- You can accept the same client version behaving differently as the catalog moves beneath it.

Where one of those fails, bundle the catalog and pin it. An estate that must attest which prompt went to which model gains more from a stale table it can inspect.

## Why it works

A bundled catalog goes stale between releases, so a remote file separates metadata updates from client releases. It does not guarantee recognition of operator-created identifiers. Claude Code 2.1.312 still names "custom deployment names and inference profile ARNs" as cases it can fail to recognize ([Claude Code changelog 2.1.312](https://code.claude.com/docs/en/changelog#2-1-312)).

The signature earns its place because it moves the trust anchor off the distribution layer. Google Threat Intelligence Group recommends exactly this control: "Remote configuration files (.ini, .json, or .xml) should be digitally signed using asymmetric public key cryptography. If an origin server or content delivery network (CDN) is modified without authorization, client software will detect the invalid signature and reject the configuration" ([Google Cloud, October 2026](https://cloud.google.com/blog/topics/threat-intelligence/investigating-ephemeral-supply-chain-tampering)). The same report warns that clients "should never rely solely on transport-layer HTTPS or remote checksums (such as cleartext MD5 values in an unauthenticated configuration file)".

UNC7017 is the demonstration. The group rewrote AOMEI's remote configuration on the vendor's own origin servers in windows of five to ten minutes, and the file the client trusted carried "the version number, the MD5 hash of the expected update package, and the URL where the client should download `upgrade-now.zip`" ([Google Cloud, October 2026](https://cloud.google.com/blog/topics/threat-intelligence/investigating-ephemeral-supply-chain-tampering)). HTTPS was in place throughout. The integrity check lived inside the unauthenticated file an attacker controlled.

Firefox ships the same shape outside the agent space: Remote Settings manages "evergreen settings data in Firefox" and lists content signing through Autograph among its features ([Mozilla wiki](https://wiki.mozilla.org/Firefox/RemoteSettings)).

## What the signature does not cover

Signing authenticates origin, not freshness. The Update Framework counts staleness as a separate attack class. On indefinite freeze attacks it states: "An attacker cannot respond to client requests with the same, outdated metadata without the client being aware of the problem" ([TUF specification](https://theupdateframework.github.io/specification/latest/)). Meeting that goal takes version numbers and expiry inside the signed metadata, which a signature alone does not supply.

It says nothing about coverage either. A correctly signed catalog that simply lacks your deployment name still degrades you, and Claude Code 2.1.312 states the behavior: those backends now "use the shorter system prompt for model names Claude Code doesn't recognize, such as custom deployment names and inference profile ARNs, even when they front Sonnet or Haiku" ([Claude Code changelog 2.1.312](https://code.claude.com/docs/en/changelog#2-1-312)).

## When this backfires

- Air-gapped or egress-restricted estates. The fetch needs a network path to the distribution host. The changelog documents an opt-out but does not say what the client runs on afterward.
- Attestation requirements. The documented control is on or off, with no version pin, so one client build stops implying one harness behavior.
- Strict verification with no fallback. Rejecting an unverifiable catalog is correct and leaves the client with no settings. Firefox documents that end state plainly: "we can end-up in situations where synchronization fails and will leave the local DB in an empty state" ([Firefox source docs](https://firefox-source-docs.mozilla.org/services/settings/index.html)). A trusted bundled copy can keep the client available while it still rejects an invalid remote catalog.

## Example

Three environment variables govern the behavior on Bedrock, Mantle, Vertex and Foundry. Each comes from one changelog line.

- `CLAUDE_CODE_MODEL_CATALOG=off` comes from 2.1.311: "set CLAUDE_CODE_MODEL_CATALOG=off to turn this off" ([Claude Code changelog 2.1.311](https://code.claude.com/docs/en/changelog#2-1-311)).
- `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0` comes from 2.1.312: "set `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0` to keep the full prompt" ([Claude Code changelog 2.1.312](https://code.claude.com/docs/en/changelog#2-1-312)).
- `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1` comes from 2.1.312: "set `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1` to turn them off" ([Claude Code changelog 2.1.312](https://code.claude.com/docs/en/changelog#2-1-312)).

```bash
# Turn off signed model-catalog fetching.
export CLAUDE_CODE_MODEL_CATALOG=off

# Keep the full system prompt for a model name the harness does not recognize.
export CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0

# Turn off automatic model switches after a flagged message.
export CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1
```

The second and third exist because the recognition gap has consequences beyond prompt length. Claude Code 2.1.312 also extended "automatic model switches after a flagged message to also cover model names Claude Code doesn't recognize, such as custom deployment names" ([Claude Code changelog 2.1.312](https://code.claude.com/docs/en/changelog#2-1-312)). Both changes can apply when Claude Code does not recognize your configured model name.

## Key Takeaways

- Treat the catalog as three options rather than a yes-or-no question: bundle and go stale, fetch and verify, fetch and trust. Only the third is always wrong.
- When reviewing any harness that fetches configuration, check where the integrity value lives. A hash published inside the file it is meant to protect is the shape UNC7017 exploited, and it buys nothing.
- Audit freshness separately from authenticity. Ask what the signed metadata says about version and expiry before calling a fetched catalog safe.
- Check model-name recognition separately from catalog fetching. Claude Code documents the shorter system prompt for unrecognized names on the four listed backends.
- Record the catalog alongside the client version in any estate that has to reconstruct a session later. The client version alone no longer determines harness behavior.

## Related

- [Gateway Model Routing](gateway-model-routing.md) — the other way a catalog reaches the harness, published by your own gateway as a discovery source rather than fetched from the vendor.
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — what the catalog's metadata drives once it arrives, and how to declare those deltas yourself.
- [Tool Signing and Signature Verification for Agents](../../security/tool-signing-verification.md) — the same cryptographic control applied to loaded tools instead of fetched configuration.
- [Multi-Shape BYOK Provider](multi-shape-byok-provider.md) — the adjacent case where capability is declared per endpoint rather than looked up in a catalog.
- [Model Deprecation Lifecycle](../../workflows/model-deprecation-lifecycle.md) — the operational wrapper for migrating the model identifiers a catalog has to describe.

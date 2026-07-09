---
title: "Dependency Inlining Erodes SBOM and License Provenance"
term: "Dependency Inlining"
description: "When an agent reimplements a library inline, SBOM, license, and CVE tooling lose the manifest entry they key on, turning tracked functionality into an invisible blind spot."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
aliases:
  - inlined dependency blind spot
  - dependency inlining provenance loss
  - license laundering via inlining
last_reviewed: 2026-07-06
maturity: adopted
---

# Dependency Inlining Erodes SBOM and License Provenance

> Reimplementing a library inline drops the manifest entry that SBOM, license, and CVE tooling key on, so the code's provenance and obligations vanish.

Supply-chain tooling reads the package manifest. When an AI agent reimplements a library function inline instead of adding the dependency, the manifest entry disappears — and with it the license record, the CVE feed, and the Dependabot updates that entry carried. The functionality stays; its provenance does not.

## What it looks like

An agent is asked to parse a JWT or retry with backoff. Instead of adding the maintained library, it writes the function directly, and the diff reads as clean first-party code. SBOM generators such as syft, trivy, and cdxgen work by parsing `requirements.txt`, `package-lock.json`, `go.sum`, and `Cargo.lock`, attributing license and vulnerability data per declared, named, versioned package ([Systems Hardening](https://www.systemshardening.com/articles/cicd/ai-code-license-compliance/)). Inlined code has no manifest entry, so it falls outside every inventory those tools build.

Four protections drop at once:

- No license record — the inlined block has no SPDX identifier, copyright notice, or attribution ([AI License Laundering](https://dev.to/pickuma/ai-license-laundering-how-code-generators-strip-open-source-obligations-2i0m)).
- No CVE feed — when the upstream library patches a bug, the copy is never flagged. The PyJWT algorithm-confusion flaw (CVE-2022-29217) fired in every SBOM-aware pipeline; an inlined JWT decoder would not ([Systems Hardening](https://www.systemshardening.com/articles/cicd/ai-code-license-compliance/)).
- No maintainer — no Dependabot PR arrives when a new attack is published against that logic.
- Possible copyleft taint — the model may reproduce copyleft-derived logic while stripping the obligation that came with it.

## Why it works

The blind spot is mechanical, not incidental. Every scanner in the chain — SBOM generator, license scanner, CVE and Dependabot feed — builds its inventory by parsing the manifest and lockfile ([Systems Hardening](https://www.systemshardening.com/articles/cicd/ai-code-license-compliance/)). Inlined code has no name and no version, so it sits outside the set the tools enumerate. Code review does not catch it either, because the reviewer is checking logic, not copyright provenance. The obligation can still be real: one study generating 70,000+ ChatGPT method implementations found AI output mirrors existing copyleft code, with larger context windows raising the reproduction rate ([Colombo et al.](https://arxiv.org/abs/2502.05023)). The license survives; the record of it does not.

## When this backfires

Not all inlining is this anti-pattern. Reimplementing a trivial helper — pad a string, clamp a number — loses no meaningful license or CVE surface, and cutting the declared-dependency footprint is itself sound supply-chain advice, since every dependency is added attack surface ([Snyk](https://snyk.io/articles/open-source-security/software-dependencies/), [NCSC](https://www.ncsc.gov.uk/blogs/software-supply-chain-attacks-check-your-dependencies)). Treating inlining as a defect costs more than it saves when:

- the inlined code is trivial and self-evidently original
- the codebase already scans all source for structural similarity (FossID, Black Duck, FOSSA), not just manifests
- a recorded vendoring policy applies — an SPDX header plus a provenance comment on each inlined block closes the manifest gap by convention

The defect is unmanaged inlining of non-trivial logic that silently strips provenance — not a recorded decision to vendor a helper.

## Example

**Before — dependency silently inlined:**

```python
# requirements.txt: PyJWT removed — "one less dependency"
# syft/trivy see nothing: no license, no CVE feed, unknown provenance
import base64, hmac, hashlib, json
def decode_jwt(token, key):
    ...  # AI-generated; may mirror PyJWT or python-jose logic
```

**After — dependency declared and tracked:**

```python
# requirements.txt: PyJWT==2.8.0 (MIT)
# syft declares it; CVE-2022-29217 fires in every SBOM-aware pipeline
import jwt
payload = jwt.decode(token, public_key, algorithms=["RS256"])
```

Same behavior. Only the declared form keeps the license, CVE feed, and provenance inside the inventory scanners read.

## Key Takeaways

- SBOM, license, and CVE tooling key on the package manifest; inlined functionality has no manifest entry, so it drops out of every inventory those tools build.
- The diff reads as clean first-party code, so neither manifest-based scanners nor logic-focused code review fire on the change.
- AI-generated code can reproduce copyleft logic verbatim, so the license obligation can outlive the record that would have tracked it.
- Scope the concern to non-trivial logic: prefer a declared dependency, or vendor with an SPDX header and a provenance comment — a recorded decision, not "never inline."

## Related

- [Generative Provenance Records for Tool-Using Agents](../verification/generative-provenance-records.md)
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](../security/agent-emitted-dependency-ranges.md)
- [Skill Supply-Chain Poisoning](../security/skill-supply-chain-poisoning.md)
- [Shadow Tech Debt](shadow-tech-debt.md)
- [Vibe Coding](vibe-coding.md)

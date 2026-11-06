---
title: "Reconstructable Factory Runs: Records and Replay Limits"
term: "Reconstructable Factory Runs"
description: "Record factory inputs, external observations, and outputs with explicit gaps, retention limits, and authority for reconstruction or replay."
tags:
  - factory-engineering
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Reconstructable Factory Runs: Records and Replay Limits

> Factory run records support reconstruction when they preserve relevant evidence and declare missing inputs, access rules, and retention limits.

A reconstructable factory run retains enough evidence to explain a delivery attempt within declared boundaries. Warp recommends preserving original task state and artifacts alongside traces. OWASP recommends collecting evidence for a defined analysis purpose. These support bounded reconstruction, without guaranteeing identical regeneration ([Warp](https://www.warp.dev/blog/build-production-software-factory), [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)).

## Separate the state boundaries

Separate retained state:

- Repository state includes recorded files and local changes. Git checkout restores repository files ([Git documentation](https://git-scm.com/docs/git-checkout)).
- External state includes the trigger, task-tracker snapshot, integration responses, and observed effects. Warp recommends retaining the original tracker state ([Warp](https://www.warp.dev/blog/build-production-software-factory)).
- Provider state includes service and model identifiers visible to the client. Identical inputs can yield different outputs, even at temperature 0 ([Claude glossary](https://platform.claude.com/docs/en/about-claude/glossary)).

This distinction is editorial synthesis. A local image digest does not establish control over remote provider internals. Record the visible provider configuration and its limits ([Stripe environment account](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), [Claude glossary](https://platform.claude.com/docs/en/about-claude/glossary)).

## Minimal run record

This proposed contract is editorial synthesis, not a portable standard. It combines [Warp's recording advice](https://www.warp.dev/blog/build-production-software-factory), [Stripe's environment account](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), [Anthropic's trial-isolation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), and [OWASP's logging guidance](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Omission costs describe evidence gaps.

| Field | Purpose | Omission cost |
|---|---|---|
| Run ID, parent/retry ID, sequence, timestamps | Join events to attempts | Attempts become ambiguous |
| Repository, starting commit, retained patch or clean-checkout declaration | Identify supplied code | Local changes remain unexplained |
| Factory revision; resolved prompt, skill, harness, tool configuration references | Identify execution policy | Policy changes become invisible |
| Runner image digest, toolchain, dependencies, setup, cache/resource conditions | Describe execution environment | Environment differences remain unknown |
| Original trigger, task snapshot, capture time, redactions | Preserve initiating facts | Later tracker state replaces original input |
| Integration endpoint, contract/adapter version, fixtures, matching policy | Identify captured interactions | Response selection becomes unclear |
| Provider, requested/returned model IDs where available, API version, supported settings, request IDs | Describe model-service boundary | Provider changes remain unexplained |
| Ordered observable messages, tool requests/results, errors, interventions | Preserve execution sequence | Outcomes lack preceding observations |
| Output artifact identities and retained patch, checks, reports, relevant captures | Preserve reviewed output | Mutable links lose decision evidence |
| Decision, actor, approval reference, capability scope, effect IDs | Connect authority to effects | Intent and completed effects blur |
| Missing/mutable inputs, access owner, retention deadline, replay restrictions | Declare handling and limits | Partial evidence appears complete |

## Replay modes and authority

These are proposed operating rules. [VCR.py's replay modes](https://vcrpy.readthedocs.io/en/v8.4.0/usage.html) and [Stripe's isolation account](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) support the distinctions; neither specifies this policy.

| Mode | Question | Authority and live access |
|---|---|---|
| Forensic reconstruction | What was recorded? | Read retained evidence under its access policy. Do not re-execute actions. Live lookups need current read authority; label them as later observations. |
| Recorded-response replay | How does selected code behave with retained responses? | Isolate execution. Deny live model/integration calls by default. Fail on missing fixtures; authorize new capture separately. |
| Fresh model run | What happens now under declared conditions? | Explicitly authorize provider/service access. Prefer test systems and scoped credentials. Require current operation-specific authority for production effects. Historical approval grants no new authority. |

Declare substituted boundaries. Under this policy, fresh model calls with recorded tool responses form a hybrid run. Stop unsupported branches instead of silently contacting live services. VCR.py's `none` mode rejects new requests, but covers only intercepted HTTP; enforce other capabilities separately ([VCR.py usage](https://vcrpy.readthedocs.io/en/v8.4.0/usage.html)).

## Why it works

Capturing state before it changes preserves the observations that informed a decision. Warp's completed-task example explains why current tracker state changes replay inputs. Recorded responses can substitute for intercepted requests, subject to matching rules ([Warp](https://www.warp.dev/blog/build-production-software-factory), [VCR.py configuration](https://vcrpy.readthedocs.io/en/v8.4.0/configuration.html)).

## When this backfires

Weak request matching can overlook relevant body changes. Record the matching policy; VCR.py defaults to method and URL components ([VCR.py configuration](https://vcrpy.readthedocs.io/en/v8.4.0/configuration.html)). Historical fixtures cannot establish current service behavior. Use a fresh run for that question ([VCR.py modes](https://vcrpy.readthedocs.io/en/v8.4.0/usage.html)).

Keep archived evidence separate from trial-visible context. Anthropic reports prior-trial Git history giving Claude an advantage in some evaluations, alongside shared-state failure risks ([Anthropic](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)).

Collect only what the investigation requires. Exclude credentials, protect sensitive payloads, restrict access, and bound retention, including copies. Redactions or expired artifacts limit reconstruction ([OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)). VCR.py's header filtering covers selected headers; separately review bodies and URLs ([VCR.py filtering](https://vcrpy.readthedocs.io/en/v8.4.0/advanced.html)).

## Example

Warp recommends preserving original task-tracker state because a completed task presents different input during replay. This is architecture advice; its imagined Sentry walkthrough is not a measured deployment ([Warp](https://www.warp.dev/blog/build-production-software-factory)).

Stripe describes standardized EC2 devboxes with source code and development services. Provisioning includes clones, caches, and code-generation services. Its prepared checkout follows recent master, which does not establish historical restoration. Stripe mixes code-executed steps with agent loops; deterministic code steps do not establish deterministic generated output. Its QA environment excludes real user data, production services, and arbitrary network egress. These are properties of Stripe's setup ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).

## Key Takeaways

- Review one downstream decision by resolving its artifact references and tracing them back to the initiating task snapshot.
- Before accepting a replay setup, deliberately request a missing fixture and check that execution stops without a live call.

## Related

- [Factory as Code: Versioning the Agent Delivery Definition](factory-as-code.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Factory Engineering](index.md) — delivery-system design and operation
- [Execution Lineage](../patterns/agent-design/execution-lineage-dag.md) — artifact dependencies and identity-based replay
- [Replay Pull Requests as Eval Fixtures](../verification/replay-pull-requests-as-eval-fixtures.md) — webhook replay for evaluation
- [Reproducibility Artifacts as Agent Context](../context-engineering/reproducibility-artifacts-as-agent-context.md) — context loading from retained artifacts
- [Evidence-Bundled Agent PRs](../verification/evidence-bundled-agent-prs.md) — review evidence packaging

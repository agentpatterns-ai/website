---
title: "Distributing Security Controls Through the Agent Harness"
term: "Harness-Distributed Security Controls"
description: "Embedding security controls in a distributable agent harness ships them to a fleet in one install — but only controls that are declarative, boundary-local, and conflict-free survive the trip."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - harness-distributed security controls
  - security control distribution through the harness
last_reviewed: 2026-07-30
maturity: emerging
---

# Distributing Security Controls Through the Agent Harness

> A harness ships security controls to a whole fleet in one install, but only declarative, boundary-local, conflict-free controls survive the trip.

Harness distribution works for a narrow class of control. A control survives the trip when you can express it as a versioned artifact, place it at a boundary the harness owns, and run it beside its neighbors without conflict. SHarD, a distributable harness built on the Pi agent, embedded OS sandboxing, skill scanning, and tool restriction and shipped all three in a single install command ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890v1)). Its composite score rose from 52.3% to 78.3% on a 23-test suite derived from the [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/), with no regression in any category. Indirect prompt injection defense did not make the trip.

## What distributes and what does not

Four controls were evaluated; three shipped ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890)):

| Control | Where it is enforced | Baseline → distributed |
|---|---|---|
| OS sandboxing | Kernel, via macOS Seatbelt. Capabilities are irreversible once applied and inherited by child processes | 66.7% → 100% |
| Skill scanning | External scan API called before a skill loads, enforced by a scan-first workflow file, against [skill supply-chain poisoning](skill-supply-chain-poisoning.md) | 58.3% → 100% |
| Tool restriction | Harness layer, a regex hook on the bash tool's arguments | 50.0% → 100% |
| Content protection | Not distributed — cut before shipping | 37.5% → 44.4% |

Read the fourth row before the headline: the paper's 100% figure is an adjusted score that excludes content protection, the one class aimed at indirect prompt injection. It was cut because it triggered false positives on the skill scanner and imposed prohibitive overhead when both ran together. What distributed was containment, not injection resistance.

The enforcement column matters as much as the score. Only the OS sandbox is structural; the paper states plainly that a determined agent bypasses the tool-restriction hook by invoking system calls directly instead of going through the bash tool. Treat harness-layer denial as a guard against agent error, and the kernel sandbox as the guard against an agent already turned.

## Why it works

A control distributes when policy becomes an artifact instead of an instruction. The paper attributes the result to four properties ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890)): the policy is declarative and portable, expressed as a JSON profile, a markdown workflow file, or an extension, and applied without any end-user configuration; each control sits at or near an execution boundary the harness owns; the co-resident controls do not conflict; and the harness is extensible enough that everything loads through hooks with no change to core source.

The determinism argument is the load-bearing half. During testing the uncontrolled agent passed one injection test by chance, after wandering into its own skill list and finding the scanner, then never reproduced that path. The paper concludes that such outcomes "cannot be substituted for deterministic controls" ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890v1)), so enforcement has to be built into the harness through hooks rather than left to model behavior. Content protection failed the conflict property, which is why it is the one class that did not ship.

## When this backfires

- Indirect prompt injection is your primary threat. The distributed set does not address it; content protection moved 37.5% to 44.4% and was then dropped. Pair harness distribution with the defenses in [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md).
- Your fleet already runs one vendor agent with a managed-policy file. Claude Code's `managed-settings.json` deploys to a system path and "cannot be overridden by user or project settings" ([Claude Code settings](https://code.claude.com/docs/en/settings)) — the same declarative, centrally applied channel with no fork to maintain. Adding controls to a stock commercial agent reached 87.0% composite against the custom harness's 78.3% ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890v1)).
- The target agent manages its own network. Network filtering could not be applied to one commercial agent at all, because its internal managed network proxy produced a fatal conflict that profile tuning did not resolve ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890)).
- The scan sits on the interactive path. Scanned skill tests took 1m49s to 8m13s against 18–30 seconds uncontrolled ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890v1)) — acceptable for a gate that fires on install, unacceptable for one that fires every turn.
- You cannot secure the distribution channel. A one-command installer concentrates fleet-wide code execution behind a single URL, the install-time trust decision described in [Setup Documentation as an Install-Time Attack Vector](setup-documentation-install-time-attacks.md).

The evidence base is one harness, four controls, and functional probes rather than adversarial evaluation ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890)), so treat the four-property test as a filter for what to try, not a guarantee.

## Example

SHarD's whole security posture is seven new files plus one edit to the package manifest, with no changes to the harness core ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890)):

```text
extensions/shard-nono.ts          session-start hook: relaunch the session inside the OS sandbox
extensions/shard-permissions.ts   tool_call hook: test bash strings against deny rules
extensions/shard-onboarding.ts    provision the skill-scanner credential at startup
config/pi.json                    sandbox capability profile: filesystem, network, admin functions
permissions.json                  deny rules, resolved from global and project-local files
SKILL.md                          the scan-before-load workflow the agent must follow
package manifest (modified)       registers the above; core harness source untouched
```

Everything the fleet gets is a file the package manager places, with nothing left for a developer to configure — which is why the channel deserves the same audit as the controls it carries.

## Key Takeaways

- Harness distribution carries containment controls well and injection defense poorly; the headline 100% is an adjusted score that excludes the content-protection class ([arXiv:2607.25890](https://arxiv.org/abs/2607.25890v1)).
- A control distributes when it is declarative, sits at a boundary the harness owns, does not conflict with co-resident controls, and loads through hooks without core changes.
- The enforcement layer decides the threat model: the kernel sandbox is structural, the bash-tool deny hook is bypassable by direct system calls.
- Model non-determinism produced an unreproducible security pass, which is the argument for hook-enforced controls over relying on model behavior.
- Where a vendor already ships a non-overridable managed-settings file, that channel delivers the same declarative fleet policy without the fork.

## Related

- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md) — which tools a harness can actually enforce against, the boundary this pattern depends on
- [Enterprise-Managed Plugin Governance for Agent CLIs](enterprise-managed-plugin-governance.md) — the vendor-native distribution channel and its four levers
- [Setup Documentation as an Install-Time Attack Vector](setup-documentation-install-time-attacks.md) — why the one-command install channel is itself a trust decision
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — where in the execution lifecycle each distributed control lands
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — layering the controls a single harness cannot carry alone

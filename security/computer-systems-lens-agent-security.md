---
title: "Computer-Systems Lens for Always-On Agent Security"
term: "Computer-Systems Lens"
description: "Model an always-on coding agent as a computer system — gateway as OS, Skills as apps, Plugins as extensions — to surface cross-component security failures."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - agentic computer system
  - OS analogy for agent security
  - gateway-as-OS model
last_reviewed: 2026-07-01
maturity: emerging
---

# Computer-Systems Lens for Always-On Agent Security

> Model an always-on agent as a computer system so classical OS protections cover the cross-component failures that model-response benchmarks miss.

An always-on coding agent is an agentic computer system, and its security should be reasoned about the way operating-system security is. The gateway runtime mediates resources, loads extensions, and holds persistent state, so it plays the role of an OS. Skills behave like user-installed applications, and Plugins behave like loadable extensions that run in-process with full runtime privilege. Framing the agent this way relocates the security question from "did the model refuse?" to "what protects each component boundary?" — which is where the consequential failures actually live ([Niu et al., 2026](https://arxiv.org/abs/2606.30755)).

## Map the agent onto OS components

| Agent component | OS analogue | Why the mapping holds |
|-----------------|-------------|-----------------------|
| Gateway runtime | Operating system | Allocates resources, loads extensions, mediates tool calls, and maintains persistent state |
| Skills | User-installed applications | Third-party units installed from a marketplace that invoke services through the gateway |
| Plugins | Loadable extensions / kernel modules | Load as native code (npm packages) with full gateway privilege, like Apache or kernel modules |

The value of the mapping is that it names the missing protections. Classical systems earn their safety from process isolation, least privilege, filesystem integrity, mediated inter-process communication, and a hard code-versus-data boundary. An always-on agent usually has none of these at its component seams ([Niu et al., 2026](https://arxiv.org/abs/2606.30755)).

## The four cross-component surfaces

The lens exposes four attack surfaces that single-tool-call benchmarks do not measure ([Niu et al., 2026](https://arxiv.org/abs/2606.30755)):

- Skill supply-chain integrity — where does behavior originate, and is it reviewed or signed before it loads?
- Persistent state exploitation — memory and config files carry no integrity checks, redaction, or access control, so tampering survives across sessions.
- Cross-boundary data flow — outbound calls reuse one shared credential set, so any source can reach any channel.
- Indirect prompt injection — document content enters the context with the same authority as the user's instruction.

Three of these four are absent or barely touched in prior benchmarks, which is why model-response and single-tool-call evaluations report a system as safe while the cross-component surface stays open ([Niu et al., 2026](https://arxiv.org/abs/2606.30755)).

## Why it works

The lens works because it moves enforcement off the probabilistic model and onto deterministic component boundaries. In the study's benchmark of 406 adversarial tasks, malicious Plugin attacks succeed 100% of the time on every unhardened configuration regardless of the underlying model, because native code execution bypasses model-level defenses entirely ([Niu et al., 2026](https://arxiv.org/abs/2606.30755v1)). Failures like that are architectural, so they respond to architectural fixes: per-Skill capability scoping instead of inherited full privilege, integrity and access control on persistent state, per-channel credential separation, and a data-instruction boundary enforced by the runtime rather than requested of the model. Independent work reaches the same conclusion — agent security is a systems problem, not a model problem ([Christodorescu et al., 2026](https://arxiv.org/abs/2605.18991v2)).

## When this backfires

The analogy stops helping in three cases.

- The agent is short-lived and single-tool, with no persistent state, plugin loader, or third-party Skills. Three of the four surfaces do not exist, so the OS vocabulary adds overhead without new coverage.
- A team instantiates the analogy by making the model the reference monitor. A language-model policy engine is a probabilistic trusted computing base — it can deny an action 99% of the time and still be exploited by the remaining 1% — so the OS framing masks a control that is not actually deterministic ([Systems Security Foundations for Agentic Computing, 2025](https://eprint.iacr.org/2025/2173.pdf)).
- The lens is read as a per-surface checklist. Hardening one surface relocates the attack rather than removing it: closing the plugin loader does not stop memory injection, and enforcing structured tool schemas can move credential leakage from prose into schema fields. The study's hardened platform cut one model's attack success from about 70% to 22% but worsened others, and its gains came largely from removing a feature — a utility-security tradeoff, not an active defense ([Niu et al., 2026](https://arxiv.org/abs/2606.30755v1)).

## Key Takeaways

- Treat the gateway runtime as an OS, Skills as applications, and Plugins as privileged loadable extensions, then port the matching classical protection to each seam.
- The decisive failures are cross-component, so evaluate the four surfaces jointly; a single boundary moves the attack rather than closing it.
- Keep enforcement deterministic at component boundaries; delegating the reference-monitor role to the model reintroduces the probabilistic gap the lens was meant to close.

## Related

- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — a complementary layering that groups threats by execution surface rather than by OS analogue.
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — embeds defenses into each execution phase so component controls coordinate.
- [Skill Composition Risk in Agent Ecosystems](skill-composition-risk.md) — the supply-chain surface in detail, where benign Skills compose into harmful behavior.
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — a concrete mechanism for the per-Skill least-privilege the lens prescribes.
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the least-privilege principle applied to the whole agent.

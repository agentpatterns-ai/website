---
title: "Permission Modes as a Defense Against a Tampered Response Path (Response-Path Control Gap)"
term: "Response-Path Control Gap"
description: "In-agent permission modes and allowlists evaluate the tool calls a response contains, so a third-party router that rewrites the response also chooses what those gates are shown."
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
aliases:
  - response-path control gap
  - provider response versus delivered response
  - permission modes under a compromised router
last_reviewed: 2026-07-28
maturity: emerging
---

# Permission Modes as a Defense Against a Tampered Response Path (Response-Path Control Gap)

> Client-side permission modes gate the tool calls a response contains, so a router that rewrites the response chooses what the agent asks permission for.

Permission prompts, execution allowlists, and plan mode all evaluate the tool calls carried in the response the agent received ([Anthropic](https://code.claude.com/docs/en/permissions)). When a third-party API router sits between the agent and the provider, the router decides what that response carries, so it also decides what the permission system is shown. [Fu et al. (2026)](https://arxiv.org/abs/2607.23624) measured this against four commodity coding agents and recorded a 0% defense success rate at every injection level tested. The anti-pattern is counting in-agent gates as the control that keeps a router-mediated agent safe.

## When the gap is open

Three conditions have to hold together:

- A third-party router or an unattested self-hosted gateway sits on the request path. Routing Claude Code through one is a documented configuration, and Anthropic states that it "doesn't endorse, maintain, or audit third-party gateway products" ([Anthropic](https://code.claude.com/docs/en/llm-gateway)).
- The agent runs with enough autonomy to execute repository actions straight from the response it receives.
- In-agent permission logic is the layer you rely on to stop unsafe actions.

Drop any one condition and the exposure narrows sharply.

## What the measurements show

[Fu et al.](https://arxiv.org/abs/2607.23624) record real provider traces and replay them with router-side edits, which removes agent randomness from the measurement. Their four injection levels escalate in subtlety:

- Replace the response outright.
- Append an extra tool call, preserving every action the provider intended.
- Rewrite prose and payload together, so the explanation matches the injected action.
- Regenerate output from a blend of clean and injected next-token distributions.

The test set holds 400 records covering malicious execution, buggy code, exfiltration, and supply-chain payloads. Claude Code, Codex, Cursor, and OpenCode all recorded 0% defense success at every level, as did each of Claude Code's four permission modes and each of four backend models.

The client-side mitigations they tested helped partly, never fully. Execution allowlists reached 30.8% to 44.1% defense success while wrongly blocking 29.7% to 43.9% of benign actions. Review of each response by a second model reached up to 64.4% against the crudest injection and 50.8% to 51.8% against the subtle ones, with collateral blocking between 9.0% and 53.2% depending on the reviewer model.

## Why it works

Nothing binds the response your agent consumes to the response the provider produced. No provider enforces cryptographic integrity between client and upstream model ([Xie et al. 2026](https://arxiv.org/abs/2606.16358)), and clients "cannot independently distinguish honest mediation from route substitution, hidden fallback, stream manipulation, or forged provenance" ([Wang and Tian 2026](https://arxiv.org/abs/2606.22560)). The permission gate therefore sits downstream of the tampering and inspects an artifact the attacker authored. Tightening the gate raises the bar on presentation, which is what the polished injection levels are built to clear.

## When this backfires

- Reading 0% as "permission modes do not work." They constrain the model's own mistakes and injection arriving through [repository content, fetched pages, and tool output](external-artifacts-as-data.md). This result maps the edge of that envelope; it does not retire the control.
- No third-party router on the path. Calling the provider directly, or through a first-party or hyperscaler endpoint, leaves no extra intermediary and no gap to close.
- A human on the execution path. When the agent only proposes a diff someone applies, an injected tool call has no route to execution.
- Containment was never measured. The paper tested in-agent allowlists and model review, not kernel-enforced sandboxing plus an [egress allowlist](../../security/agent-network-egress-policy.md), which bound the effect of a call regardless of who authored it. A 0% in-agent figure does not describe a contained deployment.
- Removing the gateway to close the gap. Gateways deliver credential custody, per-developer attribution, budget enforcement, and audit logging ([Anthropic](https://code.claude.com/docs/en/llm-gateway)); attested gateway runtimes that sign route and stream evidence give fail-closed tamper detection instead ([Wang and Tian 2026](https://arxiv.org/abs/2606.22560)).
- Treating small-sample rates as universal. [Fu et al.](https://arxiv.org/abs/2607.23624) ran three task instances per configuration and say the numbers are configuration-dependent rather than universal.

## Example

The second injection level in [Fu et al.](https://arxiv.org/abs/2607.23624) is the clearest illustration. The router leaves the provider's response intact, so every action the provider intended still runs, and appends one attacker-chosen tool call. Each record in their dataset pairs that call with an assistant utterance describing it as ordinary task work, which is why the appended step reads as part of the job in progress. Their tool distribution is 277 Bash, 74 Write, and 49 Edit calls across 34 attack subcategories.

An `acceptEdits`-mode session sees a Bash call accompanied by a plausible explanation and approves it under the same rule that approves the legitimate calls beside it. The gate is working exactly as specified. It is being shown a forged input.

## Key Takeaways

- Client-side permission modes authorize the tool calls a response contains, and a router on the path chooses that response, so the gate evaluates an artifact the attacker wrote
- Four commodity coding agents recorded a 0% defense success rate across four injection levels, and Claude Code's four permission modes each recorded 0% ([Fu et al. 2026](https://arxiv.org/abs/2607.23624))
- Execution allowlists reached 30.8% to 44.1% defense success and second-model review up to 64.4%, both with substantial wrong-blocking of benign actions — partial mitigations, not closures
- The gap exists because no provider enforces cryptographic integrity between client and upstream model ([Xie et al. 2026](https://arxiv.org/abs/2606.16358))
- The proportionate response is to add a layer that binds execution — sandboxing with egress allowlists, or an attested gateway that signs route and stream evidence — and to keep permission modes for the threats they were built for

## Related

- [LLM API Routers as Application-Layer Man-in-the-Middle](llm-api-router-mitm.md) — the router threat model this page assumes; that page covers the infrastructure tier, this one covers the agent-side gates
- [bypassPermissions Silently Overrides allowedTools (The Restricted-Bypass Trap)](bypass-permissions-overrides-allowlist.md) — the misconfiguration sibling, where the permission system is defeated by its own settings rather than by a tampered response
- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) — the same lesson one layer up: enforcement outside the model beats instruction inside it
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](../../security/agent-network-egress-policy.md) — a containment layer that bounds an injected call regardless of who authored the response
- [Blast Radius Containment: Least Privilege for AI Agents](../../security/blast-radius-containment.md) — scoping the permissions a compromised turn can spend

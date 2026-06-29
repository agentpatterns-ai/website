---
title: "Direct Prompt Injection via Collaboration (User as Attack Vector)"
term: "Direct Prompt Injection via Collaboration"
description: "When the user pastes an attacker-crafted prompt into the agent themselves, model-layer classifiers anchored on user intent see one coherent turn — only environmental defenses catch it."
tags:
  - security
  - agent-design
  - human-factors
  - tool-agnostic
  - anti-pattern
last_reviewed: 2026-06-12
maturity: adopted
status: current
---

# Direct Prompt Injection via Collaboration (User as Attack Vector)

> When the user pastes an attacker-crafted prompt into the agent, model-layer injection classifiers see one coherent user turn — only environmental defenses catch it.

## The anti-pattern

Most agent threat models assume the malicious instruction arrives through a tool result, a fetched page, or an MCP response — the [indirect injection](../security/prompt-injection-threat-model.md) surface. Direct prompt injection bypasses that model. The attacker writes the prompt, the user pastes it, and the agent runs it as if the user authored it. The mitigations that work for indirect injection do not.

[Anthropic's 2026-05-25 containment post](https://www.anthropic.com/engineering/how-we-contain-claude) documents a controlled red-team. A researcher phished an employee with a "can you run this for me?" email that carried a ready-to-paste prompt. The prompt read `~/.aws/credentials`, encoded them, and POSTed them out. Across 25 retries, Claude Code completed the exfiltration 24 times.

## Why it works

Model-layer classifiers anchor on user intent. They flag transplants whose voice and topic clash with the user's other tokens. Anthropic states it directly: "when the user is the one typing the instruction, there's nothing anomalous for a classifier to catch" ([Anthropic Engineering](https://www.anthropic.com/engineering/how-we-contain-claude)). The same provenance-blindness drives [indirect injection](../security/prompt-injection-threat-model.md), because transformer attention has no channel separating user-typed from user-pasted text. But here the classifier sees one coherent turn, because the user did paste it.

The only defense that holds is environmental: "egress controls that block the POST regardless of intent and filesystem boundaries that keep `~/.aws` out of reach" ([Anthropic Engineering](https://www.anthropic.com/engineering/how-we-contain-claude)). These controls already exist as patterns — [URL exfiltration guards](../security/url-exfiltration-guard.md), [scoped credentials proxies](../security/scoped-credentials-proxy.md), [sandboxed harness tools](../security/sandbox-rules-harness-tools.md) — but teams usually aim them at indirect injection and rarely audit them against the user-as-vector case.

## Ambient injection escalation

The collaboration vector composes badly with shared agent-readable channels: "When we shared the working prompt in internal Slack for discussion, someone pointed out that some internal agents read Slack. The payload was now ambient." ([Anthropic Engineering](https://www.anthropic.com/engineering/how-we-contain-claude)). A payload from one developer's mailbox escapes the original incident the moment the team discusses it in any channel downstream agents ingest — channel summaries, on-call bots, RAG indexes. A direct-injection event then becomes an indirect-injection source for every other agent.

## When this backfires

Three conditions make indirect-injection hardening the priority:

- Production base rate is indirect injection. Anthropic's Claude Opus 4.6 system card stresses indirect-injection metrics as the more relevant enterprise threat ([System Card, February 2026](https://www.anthropic.com/claude-opus-4-6-system-card)). With no egress allowlist or credential isolation yet, indirect coverage is the larger expected-loss reduction.
- Single-developer harnesses have no shared agent-readable channels. Ambient escalation collapses, and residual risk reduces to the [trust-without-verify](trust-without-verify.md) failure of pasting prompts unread.
- Pure conversational agents have no tool, shell, or file access. Direct injection has no actuation surface to guard.

The strongest counter-position: direct and indirect injection are two modes of one provenance-blind mechanism, so splitting the literature risks duplicating coverage. The reply: the collaboration vector adds classifier-anchoring failure and ambient escalation, neither of which appears in the indirect literature.

## Example

The Anthropic red-team scenario, mapped to a harness with environmental defenses blocking the actuation step:

```text
1. Attacker emails developer: "can you run this for me?" with a pasted prompt.
2. Developer pastes prompt into Claude Code.
3. Agent attempts to read ~/.aws/credentials — filesystem boundary denies; path is outside the project workspace.
4. (Or, where the read succeeds:) Agent attempts POST to attacker.example/collect — egress allowlist denies; host not in allowed list.
5. Exfiltration fails at the environmental layer, regardless of model-layer classifier behavior.
```

Without these controls, the same scenario exfiltrates in 24 of 25 retries — the model-layer classifier sees one coherent user turn and flags nothing. The defense is not to detect the pasted prompt. It is to make sure the environment refuses the action even if the agent attempts it.

## Practitioner guidance

- Treat prompts pasted from email, Slack, or shared docs like a tool-fetched HTML page: external authorship reaching the agent through a user-controlled channel.
- Audit environmental controls — [URL exfiltration guards](../security/url-exfiltration-guard.md), [scoped credentials](../security/scoped-credentials-proxy.md), [sandboxed tool execution](../security/sandbox-rules-harness-tools.md) — against the user-as-vector case, not only indirect injection. The controls are usually already there; the audit lens is missing.
- Plant canary strings in Slack channels and RAG indexes agents read, so a leaked direct-injection prompt is detectable downstream.

## Key Takeaways

- The user pastes the attacker's prompt, so model-layer classifiers anchored on user intent have nothing anomalous to flag — a distinct attack class.
- Environmental defenses — egress controls like a [URL exfiltration guard](../security/url-exfiltration-guard.md) and filesystem boundaries — are the only mitigation that holds: they refuse the action regardless of classification.
- The ambient follow-on lets a payload from one mailbox become an indirect-injection source for every agent the moment the team discusses it.
- The pattern matters most for credential-bearing workstations and teams whose agents read shared channels; production base rates stay dominated by indirect injection.

## Related

- [Prompt Injection: A First-Class Threat to Agentic Systems](../security/prompt-injection-threat-model.md)
- [Single-Layer Prompt Injection Defence](single-layer-injection-defence.md)
- [Lethal Trifecta in Agent Tooling](../security/lethal-trifecta-threat-model.md)
- [Guarding Against URL-Based Data Exfiltration](../security/url-exfiltration-guard.md)
- [Trust Without Verify](trust-without-verify.md)

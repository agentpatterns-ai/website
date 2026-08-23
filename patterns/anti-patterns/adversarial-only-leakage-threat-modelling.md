---
title: "Adversarial-Only Threat Modeling for Agent Data Leakage"
term: "Adversarial-Only Leakage Threat Modelling"
description: "Tool-using LLM agents leak sensitive data during benign requests, not only under prompt-injection attacks — adversarial-only defenses miss the surface."
tags:
  - security
  - anti-pattern
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - non-adversarial agent data leakage
  - benign-task data leakage
  - operational data leakage in agents
last_reviewed: 2026-06-18
maturity: emerging
---

# Adversarial-Only Threat Modeling for Agent Data Leakage

> Tool-using agents leak sensitive data during benign requests — adversarial-only defenses miss audience, necessity, and access-scope failures that fire under ordinary use.

## The pattern

This anti-pattern scopes agent data-leakage defenses to adversarial exfiltration — prompt injection, jailbreaks, malicious MCP tools — and assumes a benign user with a benign request poses no leakage risk. The threat model lists injection classifiers, egress allowlists for known-bad destinations, and tool-call sandboxing. It does not model the agent itself oversharing while completing a legitimate task. A joint Singapore AI Safety Institute and Korea AI Safety Institute evaluation across 12 realistic scenarios (customer support, DevOps, business automation) found that none of three frontier agents achieved fully correct and fully safe execution across all tasks; "successful task completion often coincided with data-handling failures" ([Baek et al. 2026](https://arxiv.org/abs/2606.17114v1)).

The study names five failure patterns, all benign-task behaviors rather than attacks:

| Pattern | Concrete observed behavior |
|---|---|
| Inadequate data awareness | Agent does not flag a fetched value as sensitive before sending it |
| Insufficient audience consideration | Internal budget figures forwarded to external recipients; CC fields populated from injected addresses |
| Policy non-compliance | Agent bypasses an organization rule it was told about in the same task |
| Excessive data collection | Agent pulls a whole folder when a single file would have answered the request |
| Access boundary violations | Sharing a full Google Drive folder when scope was one document |

Source for all five: [Baek et al. 2026](https://arxiv.org/abs/2606.17114v1). A corroborating large-scale audit reports data-over-exposure on 57.07% of cross-tool function-call paths across 6,675 real-world agent tools ([Lin et al. 2026](https://arxiv.org/abs/2603.07557v1)).

## Why it works

The model judges content sensitivity but not task necessity or recipient authorization. LLMs detect that a string is a salary or a credit-card number, yet in complex multi-tool tasks "often fail to determine which data should not be exposed" given the recipient and the task ([Zharmagambetov et al. 2025](https://arxiv.org/abs/2503.09780)). Tools widen the gap: they return broad outputs without considering task-specific necessity, and the model processes them coarsely ([Lin et al. 2026](https://arxiv.org/abs/2603.07557v1)).

Adversarial-only defenses check whether an instruction is hostile or whether a destination is known-bad. Neither check fires when a benign request causes oversharing through a legitimate tool to a legitimate-looking recipient. AGENTDAM finds GPT-4, Llama-3, and Claude agents inadvertently using unnecessary sensitive information in benign tasks ([Zharmagambetov et al. 2025](https://arxiv.org/abs/2503.09780)).

Cross-tool inference compounds the problem: individually non-sensitive fragments compose into sensitive disclosures. Tools-Orchestration Privacy Risk reaches an average 88.6% leakage rate across six frontier LLMs. Prompt-only mitigations add about 2.7 H-score points, while supervised fine-tuning plus DPO adds about 16.2 ([Wang et al. 2026](https://arxiv.org/abs/2512.16310)). The signature behavior: agents sanitize email content (strip budget figures) while still sending to an unauthorized recipient — content-aware, audience-blind ([Baek et al. 2026](https://arxiv.org/abs/2606.17114v1)).

## When this backfires

The anti-pattern is the exclusion of benign-leakage modeling, not the adversarial scope itself. Treat the threat models as additive. In some cases, adding benign-leakage controls buys little:

- Single-tool, single-recipient tasks with no compositional risk (an agent that summarizes one file to one fixed channel) carry little of the failure surface.
- Intra-team agents acting under uniform trust: recipient allowlists, data-minimization prompts, and output scopes add latency and refusal rates that may exceed the harm avoided.
- For low-trust user populations, adversarial defenses stay primary; benign-leakage controls are additive, not a replacement.

The empirical signal cuts against adversarial-only modeling for any agent with broad tool access and mixed-audience tasks. Agents with adversarial defenses nominally engaged still failed every benign scenario; 88.6% TOP-R holds across models with prompt-injection training; 57% DOE holds across the real-world tool corpus ([Baek et al. 2026](https://arxiv.org/abs/2606.17114v1); [Wang et al. 2026](https://arxiv.org/abs/2512.16310); [Lin et al. 2026](https://arxiv.org/abs/2603.07557v1)).

## Example

Before, with an adversarial-only threat model:

```yaml
agent_defences:
  prompt_injection: classifier_v2
  egress_allowlist: [internal-mail, jira, drive]
  malicious_url_blocklist: shared-threat-feed
# benign requests assumed safe — no recipient authorisation,
# no data-minimisation check at tool boundary
```

A user asks the agent to send the Q3 summary to a partner team. The agent reads the internal Q3 doc, which includes unredacted salary lines. It drafts a partner-appropriate summary that strips the salary lines from the visible body, then sends to the partner domain, which is on the egress allowlist because it has been used before. The injection classifier sees nothing hostile; the URL allowlist sees nothing malicious. The full Q3 doc is attached because the agent forwarded the source as supporting context.

After, with additive benign-leakage controls:

```yaml
agent_defences:
  prompt_injection: classifier_v2
  egress_allowlist: [internal-mail, jira, drive]
  malicious_url_blocklist: shared-threat-feed
  # benign-leakage layer
  recipient_authorisation:
    require_explicit_allowlist_per_data_class: true
    data_classes: [internal-financials, internal-people, customer-pii]
  data_minimisation:
    strip_unrequested_attachments: true
    enforce_field_minimisation_per_task: true
  audience_aware_filter:
    block_if_recipient_domain_not_in: [partner_allowlist_per_data_class]
```

Each new control targets one named failure pattern from [Baek et al. 2026](https://arxiv.org/abs/2606.17114): `recipient_authorisation` for audience, `data_minimisation` for excessive collection, `audience_aware_filter` for access-boundary violations. None of them depend on the request being hostile to fire.

## Key Takeaways

- Tool-using agents leak sensitive data while completing benign requests; defenses scoped to adversarial exfiltration do not cover audience, necessity, or access-scope failures ([Baek et al. 2026](https://arxiv.org/abs/2606.17114)).
- The five named failure patterns — inadequate data awareness, insufficient audience consideration, policy non-compliance, excessive data collection, access boundary violations — are all benign-task behaviors, not attacks.
- Content-sensitivity classification is not enough: the model can strip a budget figure from text yet still send the message to an unauthorized recipient ([Baek et al. 2026](https://arxiv.org/abs/2606.17114)).
- Cross-tool inference is its own risk class — individually non-sensitive fragments compose into sensitive disclosures at an average 88.6% rate; prompt-only mitigations close little of that ([Wang et al. 2026](https://arxiv.org/abs/2512.16310)).
- Treat benign-leakage controls as additive: recipient authorization per data class, data-minimisation at the tool boundary, and audience-aware egress filters target the failure surface adversarial-only models miss.

## Related

- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — the read-side anti-pattern; this page covers the write-side counterpart.
- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) — instruction-layer controls are insufficient for tool restriction, the same shape of failure that prompt-only data-minimisation hits.
- [Privacy-Preserving LLM Requests](../../security/privacy-preserving-llm-requests.md) — local routing plus redact-and-rephrase as a content-level control complementary to recipient authorization.
- [Guarding Against URL-Based Data Exfiltration](../../security/url-exfiltration-guard.md) — the URL-channel exfiltration counterpart; covers adversarial fetch leakage that this page does not.
- [Protecting Sensitive Files from Agent Context Access](../../security/protecting-sensitive-files.md) — the read-boundary control that pairs with the write-boundary controls in the After example.

---
title: "System Prompt as Secret Store (OWASP LLM07)"
term: "System Prompt as Secret Store"
description: "Treating the system prompt as a confidentiality boundary is the underlying vulnerability — secrets, credentials, and security-critical logic in the prompt are recoverable by adversarial users at 84–92% attack success rate on frontier models."
tags:
  - security
  - tool-agnostic
  - instructions
aliases:
  - System Prompt Leakage
last_reviewed: 2026-06-02
maturity: established
---

# System Prompt as Secret Store (OWASP LLM07)

> The system prompt is recoverable input — putting secrets, credentials, or security-critical logic there is the vulnerability, not the leak that follows.

## The anti-pattern

Agent and harness builders stuff API keys, internal URLs, role rules, transaction limits, and guardrail logic into system prompts and treat the prompt as confidential. OWASP names this LLM07:2025 System Prompt Leakage and reframes the risk explicitly: "the system prompt should not be considered a secret, nor should it be used as a security control" ([OWASP LLM07:2025](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/)). The bug is not that prompts leak — it is the design choice to rely on their confidentiality.

OWASP identifies four categories of content that do not belong in a system prompt:

| Category | Example | Why it fails |
|----------|---------|--------------|
| Credentials and connection data | API keys, database connection strings, user tokens | Recoverable input — once extracted, an attacker authenticates as the agent |
| Internal business rules | "Transaction limit is $5000/day", "Total loan amount is $10,000" | Disclosure tells the attacker exactly which limits to bypass; the limit must hold whether or not the model honors it |
| Filtering criteria | "If a user requests another user's data, respond 'Sorry, I cannot assist'" | Once extracted, the attacker knows the refusal trigger and reshapes the query to slip past it |
| Role and permission structures | "Admin role grants full access to modify user records" | Reveals the privilege graph; aids privilege-escalation attacks |

OWASP's four categories share one root cause: each item is a control the application delegates to the model's willingness to honor a prompt instruction.

## Why it works

LLMs process system instructions and user input as one continuous natural-language stream. There is no architectural privilege boundary inside the context window ([Mend.io](https://www.mend.io/blog/what-is-ai-system-prompt-hardening/)). Two mechanisms route prompt content back into outputs: perplexity-based recovery (prompt text becomes recognizable in the model's learned patterns, so adversarial queries nudge the model toward surfacing it) and attention-based exposure (attention matrices contain direct token-translation paths from prompt to output that crafted queries exploit) ([Liang et al., 2024](https://arxiv.org/abs/2408.02416)).

Multi-turn extraction against frontier models reaches 84–92% attack success rate on Gemma-2 and Falcon-3; sycophancy-driven attacks raise ASR from 17.7% to 86.2% over single-turn baselines ([Das & Amini, 2025](https://arxiv.org/abs/2505.23817v1)). Tool-using agents add a second channel: a malicious MCP tool with an argument field named `"note": "system prompt"` triggers normal argument generation, refusal training does not fire, and ToolLeak achieved 0.997 semantic similarity to the actual system prompt on Claude Sonnet 4 ([Xie et al., 2025 — Tool-Invocation Attack Surface](tool-invocation-attack-surface.md)). The strongest defense papers cut extraction by 71–84% on Llama2-7B and GPT-3.5 but cannot eliminate it.

## The design rule

OWASP's four mitigations enforce the same separation: anything that must hold lives outside the prompt ([OWASP LLM07:2025](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/)).

1. Separate sensitive data from system prompts. Move credentials, role definitions, and permission tables to systems the model reaches through tools, not text — see [Secrets Management for Agent Workflows](secrets-management-for-agents.md).
2. Do not rely on system prompts for strict behavior control. Prompt injection overrides system instructions ([Prompt Injection Threat Model](prompt-injection-threat-model.md)); harmful-content detection and policy enforcement belong in external systems.
3. Implement guardrails outside the LLM. An independent inspector that scans outputs beats a prompt instruction telling the model to self-police.
4. Enforce security controls independently of the LLM. Privilege separation and authorization checks run deterministically — several agents with least-privilege grants beat one agent told to respect privilege rules.

The rule is not "harden the prompt against extraction" — it is "do not put anything in the prompt whose security depends on its confidentiality."

## When this backfires

The rule applies to security-critical content. Three conditions admit a softer reading:

- Prompt text as intellectual property: customer-support and chatbot teams reasonably treat tone, brand voice, and fine-tuned filter rules as proprietary IP separate from any security boundary. Defense papers like ProxyPrompt achieve 94.7% protection against extraction ([arxiv:2505.11459](https://arxiv.org/html/2505.11459v1)) and PromptKeeper ([arxiv:2412.13426](https://arxiv.org/pdf/2412.13426)) hardens prompt-text confidentiality as commercial-IP defense — neither claims the prompt can hold credentials.
- Models with strong output sanitization: GPT-5's content filtering blocked ToolLeak-class extraction in independent testing ([Xie et al., 2025](https://arxiv.org/abs/2509.05755), Table III); operators may keep filtering criteria in the prompt as a soft control, as long as the hard control still runs downstream.
- Demos with no privileged tools and no production data: a hobbyist prompt with no credentials, no untrusted input, and no privileged tool surface has nothing to protect; the rule still applies but its bite is theoretical.

In every case the design rule survives: the prompt is not a confidentiality boundary for credentials, internal rules whose disclosure aids attack, or controls that must hold regardless of model behavior.

## Example

Before — security logic in the system prompt:

```text
You are a banking assistant. The daily transaction limit per user is
$5,000 and the lifetime loan cap is $10,000. If a user requests
information about another user's account, respond:
"Sorry, I cannot assist with that request."
Connection string: postgresql://app:app_pw_2025@db.internal:5432/bank
```

Extraction surface: an attacker who recovers this prompt knows the exact transaction limit to test against, the refusal string to work around, and gets a database password. Both [Das & Amini (2025)](https://arxiv.org/abs/2505.23817) and [Liang et al. (2024)](https://arxiv.org/abs/2408.02416) demonstrate this prompt class is recoverable on every model tested.

After — same agent, separated controls:

```text
You are a banking assistant. Use the provided tools to answer
user questions about their own account. Refuse off-topic requests
and explain why.
```

The transaction limit, loan cap, cross-user authorization check, and database credentials live in the tool implementation — checked before the tool returns data, independent of what the system prompt says or whether it leaks. The agent process reads the database password from an environment variable injected at start ([Secrets Management for Agent Workflows](secrets-management-for-agents.md)); cross-user authorization runs as a deterministic check in the API layer the tool calls.

## Key Takeaways

- The system prompt is recoverable input, not a secret store — 84–92% extraction ASR on frontier models and 0.997-similarity recovery via tool-invocation channels confirm this empirically.
- Four categories never belong in the prompt: credentials, internal rules whose disclosure aids attack, filtering criteria, and role/permission structures.
- The design rule is not "harden the prompt" — it is "do not put anything in the prompt whose security depends on its confidentiality."
- Every OWASP mitigation enforces the same separation: controls that must hold execute deterministically outside the model.
- Prompt-text confidentiality has legitimate commercial-IP value, but that is distinct from using the prompt as a security boundary.

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — the affirmative pattern for credentials: inject as environment variables, never as prompt text
- [Internal Hostname Disclosure in Agent-Readable Context](internal-hostname-disclosure-agent-context.md) — the non-credential sibling risk: internal hostnames left in the same instruction files carry reconnaissance value even with no secret attached
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — second channel for prompt extraction via malicious MCP tool argument generation
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — why prompt-text instructions cannot be relied on as behavior controls
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — extracted credentials in a prompt close the trifecta when the agent has untrusted input and egress
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md) — architectural patterns for the external-enforcement half of the rule

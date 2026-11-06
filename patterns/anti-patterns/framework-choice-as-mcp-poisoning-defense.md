---
title: "Choosing an Agent Framework as an MCP Poisoning Defense"
term: "Framework-Agnostic Poisoning Resistance"
description: "Across 12 agent frameworks no MCP client validated tool descriptions. Nine core frameworks landed within 23 to 26% attack success, while models ranged 0.4% to 49.7%."
aliases:
  - framework choice as MCP tool-poisoning defense
  - model-level MCP poisoning resistance
  - MCP framework passthrough
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
---

# Choosing an Agent Framework as an MCP Poisoning Defense

> Nine core agent frameworks landed within 23.4% to 26.1% attack success against poisoned MCP tools, while the 18 models ranged from 0.4% to 49.7%.

Picking an agent framework for its security features does not stop MCP tool poisoning, because none of the tested frameworks inspected tool descriptions. Across 12 frameworks, 18 models, and 45 attack scenarios, no framework validated the tool descriptions it passed to the model, and most of the variation came from the model ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). The result holds under stated conditions: single-turn harnesses, 12 frameworks chosen by download count, models served on 22 to 24 July 2026, and 45 scenarios built from published attacks ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). It describes only the tested framework versions and configurations on those dates.

## The anti-pattern

A team adds third-party MCP servers to an agent and treats the framework as the security boundary. It assumes a framework with type-safe schemas, sandboxed execution, or a confirmation prompt filters hostile tool metadata, so it compares frameworks on security and picks the model on cost.

The study tested that assumption with real tool execution and a canary server that confirms exfiltration. The overall attack success rate (ASR) was 22.9%, or 2,113 vulnerable cells. Of those, 64.9% dispatched an attacker tool call, 23.0% reached the attacker endpoint, and 12.1% verifiably exfiltrated a secret ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).

| Factor varied | Spread in ASR |
|---|---|
| Nine core frameworks, models pooled | 23.4% to 26.1% |
| All 18 models, frameworks pooled | 0.4% to 49.7% |
| One model across the nine frameworks | median 10.2 percentage points |

Data: [Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1), §6.1.

The authors left three frameworks out of the cluster for mechanical reasons. Each one shows that framework mechanics can still move the number:

- AG2 scored 4.6% because its executor rarely completes the outbound call. The authors warn that "the model still emits the malicious call, so a different execution binding would dispatch it, and AG2 should therefore not be read as a hardened framework choice" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).
- Pydantic AI scored 16.6% because it rejects duplicate tool names at registration, which blocks shadowing scenarios without reading any description ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).
- smolagents scored 34.4%. It presents tools as Python objects in generated code, and "The code-generation representation bypasses alignment trained against structured tool definitions rather than defending against injection" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).

## Why it works

Every tested framework copied the attacker's text into the prompt unchanged. The MCP tool description is free text with no length limit, and "Frameworks insert this field verbatim into the model's context window as part of tool definition prompting" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). A code audit located the passthrough in each framework and found that "No framework checks for instruction patterns, authority markers, encoded content, embedded URLs, or anomalous description length" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).

So in the tested versions the model was the only component that judged the injected text. A framework can change the outcome only through mechanics: how it registers names, binds the executor, or represents tools. Features that look like defenses address other concerns. Agno's confirmation prompt checks the action, not the description that caused it. smolagents' sandbox limits where code runs, and the poisoned description still reaches the model. Pydantic AI's type checks validate schema structure, and a description is a plain string ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).

The vendors treated the passthrough as expected behavior, for different reasons. The authors filed five coordinated disclosures with four organizations, and all five were rejected. LangChain replied that "This library is expected to be passing the information exactly as specified in the MCP resources. This is not the appropriate place for any sort of validation". Microsoft's MSRC replied that "the attacker must already control the MCP server, and AutoGen explicitly documents MCP servers as trusted", and deepset called it "trusted configuration behavior rather than a framework vulnerability". The MCP SDK team answered a rug-pull report by pointing to host-side review of tool calls ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). The MSRC reply concerns microsoft/autogen, not the AG2 fork the study tested.

## What to do instead

Treat the model as a security choice. The paper says "Organizations deploying MCP-enabled agents should treat model selection as a security decision" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). Then add controls you own, because the model's resistance carries no guarantee: "No model provider offers an SLA for injection resistance" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).

- Pin the model version. Eight of the study's model identifiers had no dated snapshot suffix, so a later run could resolve to a different model ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).
- Hash each tool description and schema at first registration, and refuse or alert when the hash changes. The audit found that no framework provides "description diffing between successive tools/list calls" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).
- Reject tool-name collisions across servers. Pydantic AI does this as a side effect, and the paper credits that check for its below-average 16.6% ASR ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).
- Scan descriptions at registration as a partial filter. The paper's regex scanner rejected 20 of 45 scenarios and flagged 9 of 125 benign descriptions, or 7.2% ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). Payloads in tool responses, other languages, file paths, or invisible characters got past it.
- Constrain the executor. The paper lists "executor-side dispatch constraints (AG2)" among incidental mechanisms that "already reduce ASR without content inspection and could be adopted deliberately" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). AG2 "produces no confirmed canary HTTP receipts at all", yet the model still emits the malicious call, so this limits damage and does not stop the attempt.

## When this backfires

The anti-pattern label overstates the case in four situations.

- Adaptive attackers. The low model ASRs came from 45 scenarios built on published techniques. Nasr et al. "bypass 12 recent defenses (based on a diverse set of techniques) with attack success rate above 90% for most; importantly, the majority of defenses originally reported near-zero attack success rates" ([Nasr et al., 2025](https://arxiv.org/abs/2510.09023v1)). A model at 0.4% on a static set may not hold against a tuned attack. The paper's limits section adds that a model's ASR "may partly reflect exposure to similar attacks during training rather than the strength of its alignment alone" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).
- Frameworks with a different architecture. AG2's executor held ASR to 4.6% and smolagents raised it to 34.4% ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). For these two, the framework does change the outcome, in opposite directions.
- One fixed model. The nine-framework cluster pools all models. For a single model, ASR across the nine frameworks spanned a median 10.2 points, and 36.5 points for Llama 4 Maverick ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). A team locked to one model should compare frameworks with that model.
- Multi-turn sessions and multi-agent setups. Every harness ran single-turn interactions, so the result is untested for long sessions and delegation chains ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)).

A model that names the attack does not always resist it. Claude Sonnet 5 flagged the injection in 4 of its 10 vulnerable cells "before nonetheless issuing the exfiltration call" ([Shaikh & Montaruli, 2026](https://arxiv.org/abs/2611.03555v1)). Judge a model by the calls it makes.

## Key Takeaways

- The code audit found unvalidated description passthrough in all 12 frameworks, and the vendors rejected all five disclosures.
- Model choice moved ASR from 0.4% to 49.7%, while nine core frameworks stayed within 23.4% to 26.1%.
- Framework mechanics still shift a single model by a median 10.2 points, so test frameworks with the model you will deploy.
- Model resistance has no SLA and was measured on published payloads, so pin the version and add description hashing, name-collision rejection, and executor constraints.

## Related

- [Single-Layer Prompt Injection Defense](single-layer-injection-defence.md) — relying on the model alone is the single layer this page warns about.
- [Expressed Risk Awareness as an Execution Safeguard](expressed-risk-awareness-as-safeguard.md) — the same narrate-then-comply result in another setting.
- [Treating a Model Upgrade as a Security Improvement](model-upgrade-as-security-improvement.md) — why a newer model is not security evidence until you measure it.
- [Multi-Tool Threshold Poisoning Against MCP (ShareLock)](multi-tool-threshold-poisoning-mcp.md) — a payload split across tools that per-description scanning misses.
- [Vetting Tool Definitions for Exfiltration Signatures](../../security/vetting-tool-definitions-before-install.md) — the install-time review the frameworks leave to you.

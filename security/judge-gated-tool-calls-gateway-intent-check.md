---
title: "Inline Intent Judge at the Model-Response Gateway"
term: "Inline Intent Judge"
description: "A gateway judge checks each tool call a model proposes against the user's request. In Google's AgentDojo run it cut attack success from 48.7% to 0.9%."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - gateway intent check for tool calls
  - semantic governance policies
  - user intent matching at the gateway
last_reviewed: 2026-11-24
maturity: emerging
---

# Inline Intent Judge at the Model-Response Gateway

> An LLM judge at the model-response gateway checks each proposed tool call against the user's request before the call runs.

Google's Semantic governance policies, in Preview on Google Cloud, place this check in Agent Gateway, the only enforcement point they support today ([Google announcement, 2026-11-20](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)). The product runs on Google Cloud only, so the numbers below describe it alone.

## Where the check sits

The judge sits between the agent's model and the agent. When the model proposes a tool call, Agent Gateway sends it to the policy engine before the response reaches the agent. "If the call is allowed, the response passes through unchanged; if not, the call is replaced with a denial message and never runs" ([Google Developers Blog, 2026-11-23](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)).

The judge reads the same context as the agent, with a trust split. The user's request and the system instructions are trusted. "Tool results, files and messages are untrusted context, treated as data, never as instructions" ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)).

Compare [CASA](hybrid-deterministic-semantic-tool-authorization.md), which checks the call between agent and MCP server. This check runs one step earlier, on the model's response, so the agent never holds a denied call. It applies only to traffic that crosses the gateway: Google says to configure the agent so all its egress traffic goes through Agent Gateway ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)). The sources describe a check on proposed calls, not on what an allowed tool does once it runs, so [Runtime Control Path Coverage](runtime-control-path-coverage.md) still applies.

## Two checks

A call must pass both checks to run ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)).

- The user-intent check is on by default and needs no policies. It tests whether the proposed call has deviated from what the user asked for.
- The policy check applies natural-language rules attached to an agent or to one tool. Rules win over requests: in Google's example, "the employee did ask, but your rules take precedence over the request."

Each verdict and its rationale go to Cloud Logging ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)).

## What the numbers show

Google ran a gemini-2.5-flash agent on AgentDojo v1.2.2 (97 user tasks, 949 attacked runs, the `important_instructions` attack) with only the default intent check and no policies, and averaged six runs per configuration ([benchmark docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/adversarial-benchmarking); [Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)). Google ran and published the benchmark.

- Attack success fell from 48.7% to 0.9% under those conditions, and stayed between 0.84% and 0.95% in every run with the judge ([benchmark docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/adversarial-benchmarking)).
- Benign-task utility averaged 72.7% without the judge and 70.1% with it, a 2.6-point cost. Individual runs ranged from -1.0 to 7.2 points ([benchmark docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/adversarial-benchmarking)).
- "None of the 929 attacks that needed a tool call succeeded in any of the six runs" ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)).
- Utility under attack read 25.8% with the judge against 35.1% without, but 12.4 points of the 35.1% were runs where the task finished and the attack also succeeded. Counting only runs where the task finished and the attack failed, the figures were 25.1% with the judge and 22.7% without ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)).

## Blind spots the sources state

- Text-only manipulation. The residual travel-domain successes asked the agent to recommend a particular hotel in its reply. "No tool call is involved, so there is no action … to evaluate", and Google suggests response filtering as a complement ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)). Responses that contain only text are not evaluated ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)).
- Streaming. The engine does not support streamed responses, and "A tool call in a streamed response might not be blocked" ([Google overview docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/semantic-governance-overview)). Configure the agent to call its model without streaming.
- Undescribed tools. "The judge relies on descriptions to understand a call, and is instructed to deny calls to tools that have none" ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)).
- Unspecified behavior. The four Google sources give no latency figure. They do not say whether a call runs or is blocked when the engine fails or cannot be reached. Measure both in your own deployment before enforcing.

## When this backfires

- The judge can be targeted. "That separation is enforced by how the judge is instructed, not by a hard technical boundary", so an attacker could try to disguise an injected request as the user's. AgentDojo's attacks were fixed and not adapted to the judge, so the figures above do not measure that case ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)). NIST's evaluators raised attack success against an agent built on Claude 3.5 Sonnet "from 11% for the strongest baseline attack to 81% for the strongest new attack" ([NIST CAISI, 2025-01-17](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations)). NIST tested that agent, not a gateway judge, so read the figure as a caution about adaptive attacks and not as a measurement of this product. See [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](adaptive-evaluation-out-of-band-defenses.md) and [Treating a Detector's Benchmark Score as Deployment Evidence](../patterns/anti-patterns/detector-benchmark-score-as-deployment-evidence.md).
- Legitimate work gets denied. "Unintended over-blocking affected 1 of the 97 benign tasks (about 1%)" ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)). Two benign tasks failed consistently, and Google counts both as intended blocks because each asked the agent to follow instructions from an external web page and "claimed a user identity that contradicted the agent's configuration" (same post).
- Benchmark utility is not production utility. The benchmark harness "drops only the denied call, while production blocks the agent's whole response" ([benchmark docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/adversarial-benchmarking)). Google states the harness differences "don't materially change the results" ([Google Developers Blog](https://developers.googleblog.com/did-the-user-ask-for-this-securing-ai-agents-against-intent-hijacking-with-semantic-governance-policies/)).
- Verdicts are probabilistic. "LLMs are probabilistic and can make mistakes. Verdicts may not be accurate" ([benchmark docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/adversarial-benchmarking)). The feature is in Preview, where pre-GA features are available "as is" and "might have limited support" (same page).

## Adoption order

Google's rollout sequence ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)):

1. Provision the policy engine and connect it to Agent Gateway.
2. Turn on dry run mode. "The engine logs what it would deny without blocking anything", and the intent check is already on.
3. Give every tool a clear description.
4. Add policies, review the verdicts in Cloud Logging, then switch to enforcement.

Google says the judge complements other controls rather than replacing them (same post). A deterministic layer under the judge, such as an [egress allowlist](agent-network-egress-policy.md) or a sandbox, covers the cases where a probabilistic verdict is wrong, in line with [defense in depth](defense-in-depth-agent-safety.md). [Choose Agent Gate Layers by Mechanism Class, Then Measure](../verification/mechanism-class-gate-stacking.md) covers how to combine layers.

## Example

Google's announcement walks a finance agent through three proposed calls ([Google announcement](https://developers.googleblog.com/check-what-your-ai-agents-do-before-they-do-it-with-semantic-governance-policies/)):

- An employee asks for results to go to the controller's company address. The agent proposes `send_email` and the call is allowed.
- An employee asks for the results to go to an outside investor, with a personal Gmail copied. The earnings policy denies the whole call, even though the employee asked.
- Hidden text in a planning document tells the agent to delete drafts. The agent proposes `delete_file` and the intent check denies it: "nobody asked for it, and no policy allows deletions."

## Key Takeaways

- The check runs on the model's response, before the agent receives a tool call. A denied call is replaced with a denial message and never runs.
- A call needs two passes: the default user-intent check, and any policies you attach.
- Google's AgentDojo run (gemini-2.5-flash, intent check only, six-run mean, fixed attacks) cut attack success from 48.7% to 0.9% at a 2.6-point utility cost.
- Text-only responses and streamed responses are not evaluated. The Google sources give no latency figure and do not specify what happens if the engine fails.
- The judge is instructed, not technically isolated. Fixed benchmark attacks do not measure adaptive ones, so run dry mode first and test your own deployment.

## Related

- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md) — CASA checks the call between agent and MCP server; this check reads the model's response one step earlier
- [Intent-Governed Tool Authorization for AI Agents (IGAC)](intent-governed-tool-authorization.md) — issues a certificate per request that narrows the visible tool manifest, then gates each proposed call with a five-conjunct predicate against that certificate
- [Intent-Graph Audits for Least-Privilege Agent Tool Calls](intent-graph-tool-call-audit.md) — checks each call in code against a plan written before any tool output
- [Runtime Control Path Coverage: Map What Each Layer Checks](runtime-control-path-coverage.md) — a gateway sees only the actions that cross it
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](adaptive-evaluation-out-of-band-defenses.md) — why fixed-attack results need an adaptive test
- [Treating a Detector's Benchmark Score as Deployment Evidence](../patterns/anti-patterns/detector-benchmark-score-as-deployment-evidence.md)
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the trust split the judge applies
- [Choose Agent Gate Layers by Mechanism Class, Then Measure](../verification/mechanism-class-gate-stacking.md)
- 
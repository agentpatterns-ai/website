---
title: "OWASP 2026 Update for Agent Builders: Top 10 Renumbering and the Agent Control Standard"
term: "OWASP LLM Top 10 (2026)"
description: "What the 2026 OWASP LLM Top 10 changes for agent builders — eight renumbered entries, one rename, no additions — and what the new Agent Control Standard covers at v0.1 preview."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - OWASP LLM Top 10 2026 changes
  - OWASP GenAI Agent Control Standard
last_reviewed: 2026-09-02
maturity: emerging
---

# OWASP 2026 Update for Agent Builders: Top 10 Renumbering and the Agent Control Standard

> The 2026 OWASP LLM Top 10 adds nothing and renumbers eight entries; the new Agent Control Standard covers runtime controls at v0.1 preview.

The 2026 edition keeps all ten 2025 categories. Set the [2025 list](https://genai.owasp.org/llm-top-10/) against the [2026 crosswalk explorer](https://genai-security-project.github.io/crosswalk/#/explorer) entry by entry and eight change position, with none added, merged, or dropped; the table below is that comparison. The one renaming is System Prompt Leakage, "renamed and broadened to Hidden Context Exposure" ([Help Net Security, August 2026](https://www.helpnetsecurity.com/2026/08/06/owasp-2026-llm-top-10-released/)). So the change that reaches a coding-agent builder is narrow and mechanical: an entry ID written without its edition year no longer names one risk. The [Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) (ACS) is the new artifact, and it catalogs runtime interception points rather than ranking risks.

## What moved in the 2026 list

The ordering below comes from the OWASP GenAI Security Project's [framework crosswalk explorer](https://genai-security-project.github.io/crosswalk/#/explorer), which labels each row "LLM Top 10 2026". The [2025 list](https://genai.owasp.org/llm-top-10/) is still published at its original URLs, so year-pinned citations still resolve.

| Risk | 2025 ID | 2026 ID |
|---|---|---|
| Prompt Injection | LLM01 | LLM01 |
| Sensitive Information Disclosure | LLM02 | LLM02 |
| Supply Chain | LLM03 | LLM04 |
| Data and Model Poisoning | LLM04 | LLM05 |
| Improper Output Handling | LLM05 | LLM10 |
| Excessive Agency | LLM06 | LLM03 |
| System Prompt Leakage, renamed Hidden Context Exposure | LLM07 | LLM08 |
| Vector and Embedding Weaknesses | LLM08 | LLM09 |
| Misinformation | LLM09 | LLM07 |
| Unbounded Consumption | LLM10 | LLM06 |

Two moves carry weight beyond the numbering. Excessive Agency climbed to third because the practitioner vote and the incident data agreed that agentic deployments are where damage lands, and Improper Output Handling fell to tenth while widening its scope ([Help Net Security](https://www.helpnetsecurity.com/2026/08/06/owasp-2026-llm-top-10-released/)).

Scope grew inside the existing entries rather than through new ones. Prompt Injection now covers cross-modal attacks hidden in images or audio, and Data and Model Poisoning absorbs fine-tuning subversion. The ranking method changed too, with the practitioner vote carrying 75% of the weight and the rest drawn from real-world incident data (Help Net Security).

The list also draws its own boundary. Project leads describe the moment a model gains tools, cross-session memory, and downstream consequences as the point where "the risk moves to the [OWASP Agentic Top 10](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)" (Help Net Security). A coding agent sits on the far side of that line.

## What ACS covers at v0.1

ACS defines how agent platforms expose middleware hooks and how safety policy is enforced through them, so that controls stay declarative and portable across frameworks ([OWASP GenAI Security Project](https://genai.owasp.org/resource/agent-control-standard-acs/)). Its specification names eight native hooks, each returning a verdict of `allow`, `deny`, or `modify` ([ACS supported hooks](https://aos.owasp.org/spec/instrument/hooks/)):

- agent trigger, user message, and agent response
- tool call request and tool call result
- memory context retrieval, memory store, and knowledge retrieval

Delegation to another agent runs through A2A rather than a native hook. Code is Apache-2.0 and documentation CC BY-SA 4.0 ([ACS repository](https://github.com/GenAI-Security-Project/agent-control-standard)).

Read the version before adopting anything. The repository marks the current state as v0.1 Public Preview and places the Guardian Agent sample application, agent instrumentation, and FastMCP and A2A client instrumentation at v1; support for `deny` and `modify` inside MCP and A2A arrives at v3. What ships today is a schema and a hook catalog.

## Why it works

Entry IDs are the join key between security documents, so a renumbering makes one identifier resolve to two risks. `LLM06` names Excessive Agency in the [2025 list](https://genai.owasp.org/llm-top-10/) and Unbounded Consumption in the [2026 list](https://genai-security-project.github.io/crosswalk/#/explorer). The failure is silent: a reader following an unqualified `LLM06` out of a 2025-era document lands on a real 2026 entry with a plausible name and no error anywhere in the path. Writing the edition year is what makes the reference resolvable.

## When this backfires

- Treating the renumbering as a rewrite. Nothing was added or dropped, so a page that already sources a 2025 entry is non-current rather than wrong. An edition qualifier costs one clause; reworking the page buys nothing.
- Adopting ACS on a small team. The standard assumes a platform that exposes hooks, an open-source enforcement layer, and an enterprise layer for custom classifiers ([agentcontrolstandard.ai](https://agentcontrolstandard.ai)). A two-person team already intercepts the same points with the harness controls in [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md) and [Permission-Gated Commands](permission-gated-commands.md), and adopting a standard adds a layer without adding a check.
- Expecting portability before the enforcement layer exists. Portability is what ACS is for, and its own roadmap places the Guardian Agent implementation and the FastMCP and A2A client instrumentation at v1 ([ACS repository](https://github.com/GenAI-Security-Project/agent-control-standard)). Until those land, the hook names travel between frameworks and the enforcement does not.
- Reading the ordering as a risk ranking. OWASP names a "defense effect" in its own data: well-defended risks such as Prompt Injection produce fewer public incidents, which makes them look smaller than the money spent holding them there (Help Net Security). Positions three through ten are a coverage prompt, not a priority queue.

## Example

The citation in [Vetting Tool Definitions for Exfiltration Signatures](vetting-tool-definitions-before-install.md) shows the minimal fix.

**Before** — the entry ID stands alone:

```markdown
[OWASP GenAI Security Project — LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
```

**After** — both editions named, one link:

```markdown
[OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/),
listed as LLM03 in the 2026 edition
```

## Key Takeaways

- Check every OWASP citation for an edition year before the next audit; the URL resolving is not evidence that the entry ID still names the same risk.
- Excessive Agency at third place is the one ordering change worth acting on: the vote and the incident record both put agentic deployments where damage lands (Help Net Security).
- The 2026 list disclaims agent-actor scope in its own words, so treat the [Agentic Top 10](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) as the primary list for a tool-using agent.
- Track the Agent Control Standard at v1, when the Guardian Agent implementation and framework instrumentation are due; v0.1 gives a hook vocabulary and nothing to install.

## Related

- [OWASP LLM Top 10 (2025): Agent Security Crosswalk](owasp-llm-top-10-2025-agent-crosswalk.md) — the 2025-edition mapping from risk names to site coverage; this page supplies the edition delta that crosswalk predates
- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — mechanism-organized alternative to a ranked list, unaffected by edition renumbering
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — capability model behind the risks the 2026 list ranks first, second, and third
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md) — the allow, deny, or modify decision ACS standardizes, as a harness already implements it
- [Enforced Versus Advisory Controls](enforced-versus-advisory-controls.md) — why a v0.1 specification with no enforcement layer is documentation rather than a control

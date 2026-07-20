---
title: "OWASP LLM Top 10 (2025): Agent Security Crosswalk"
term: "OWASP LLM Top 10 (2025)"
description: "Map each OWASP Top 10 for LLM Applications (2025) risk to coding-agent-specific manifestations and the site pages that answer it — a navigation aid for readers arriving with the framework's shared vocabulary."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - OWASP LLM Top 10 2025 crosswalk
  - OWASP LLM Top 10 coding agent mapping
last_reviewed: 2026-06-09
maturity: established
---

# OWASP LLM Top 10 (2025): Agent Security Crosswalk

> Map each OWASP LLM Top 10 (2025) risk to coding-agent-specific manifestations and site pages — a navigation aid, not a recommended threat model.

This page exists because the [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/) is the dominant shared vocabulary for LLM risk, not because it is the optimal threat model for autonomous coding agents. For that, OWASP itself published a separate [Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — the more directly applicable framework when the agent plans, persists state, and invokes tools across trust boundaries. Use this crosswalk to locate site coverage from the LLM Top 10's category names; use the [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) or [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) for the mechanism-side analysis a coding-agent build actually needs.

## The crosswalk

Each row leads with the agent-specific manifestation in this site's own words. The LLM Top 10 entries are framed around general LLM-application risk, so the agent-side translation takes real work for several entries. Coverage flags are scoped to coding-agent and agent-harness builds: saturated means multiple first-class pages, covered means at least one direct page, partial means adjacent pages but no first-class treatment, and gap means no direct coverage on this site as of `last_reviewed`.

### OWASP risks LLM01–LLM05

| OWASP 2025 Risk | Agent-Specific Manifestation | Site Coverage | Status |
|---|---|---|---|
| [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Untrusted content reaches the model via fetched pages, file reads, tool outputs, or returned API bodies; instructions inside that content redirect the agent's behavior. The indirect variant is the dominant coding-agent attack surface. | [Prompt Injection: A First-Class Threat](prompt-injection-threat-model.md), [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md), [Indirect Injection Discovery](indirect-injection-discovery.md), [CaMeL](camel-control-data-flow-injection.md), [Action-Selector Pattern](action-selector-pattern.md), [Single-Layer Injection Defence (anti-pattern)](../patterns/anti-patterns/single-layer-injection-defence.md) | saturated |
| [LLM02:2025 Sensitive Information Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/) | Agent context aggregates secrets, source files, transcripts, and tool outputs; exfiltration paths run through agent-authored messages, URL construction, and rendered images — not only model output. | [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md), [Protecting Sensitive Files](protecting-sensitive-files.md), [Privacy-Preserving LLM Requests](privacy-preserving-llm-requests.md), [Secrets Management for Agents](secrets-management-for-agents.md), [URL-Based Exfiltration Guard](url-exfiltration-guard.md), [Agent-Authored Messages as Deferred Exfiltration](agent-authored-message-rendered-image-exfiltration.md) | saturated |
| [LLM03:2025 Supply Chain](https://genai.owasp.org/llmrisk/llm032025-supply-chain/) | Agent supply chains span model weights, MCP servers, skills, plugins, and emitted dependency manifests; a tampered or floating-range dependency inherits agent privileges. | [Agent-Emitted Dependency Ranges](agent-emitted-dependency-ranges.md), [LLM-Pinned Vulnerable Versions](llm-pinned-vulnerable-versions.md), [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md), [Tool Signing and Signature Verification](tool-signing-verification.md) | saturated |
| [LLM04:2025 Data and Model Poisoning](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/) | Most coding-agent builders consume vendor APIs and do not influence pretraining; the agent-relevant slice is poisoning of RAG corpora, knowledge graphs, and persistent memory the agent later retrieves. | [Oracle Poisoning: Knowledge Graph Corruption](oracle-poisoning-knowledge-graph.md), [RAG Architecture as a Poisoning Robustness Decision](rag-architecture-poisoning-robustness.md), [Trojan Hippo: Dormant Memory Payloads](trojan-hippo-memory-attack.md), [Cognitive Poisoning via Tool Feedback](cognitive-poisoning-tool-feedback.md) | covered |
| [LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) | For coding agents the "output" is emitted code, shell commands, and tool arguments — not chat text returned to a user. Defenses are output-side scanners, structural verifiers, and default-deny posture before downstream consumption. | [Verifying LLM-Generated Cryptographic Code](llm-cryptographic-code-verification.md), [Safe Outputs Pattern](safe-outputs-pattern.md) | partial |

### OWASP risks LLM06–LLM10

| OWASP 2025 Risk | Agent-Specific Manifestation | Site Coverage | Status |
|---|---|---|---|
| [LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | OWASP's 2025 revision decomposes this risk into excessive functionality, excessive permissions, and excessive autonomy — the three axes that map most directly to a coding-agent harness. The over-privilege axis is not hypothetical: attackers gained access to high-profile Instagram accounts simply by asking Meta AI to relink an account's email, an excessive-agency failure where the assistant could perform a sensitive action it should never have been authorized to take ([Willison — Hackers Simply Asked Meta AI](https://simonwillison.net/2026/Jun/1/hackers-simply-asked-meta-ai/)). Each axis has its own controls on this site. | Functionality: [Blast Radius Containment](blast-radius-containment.md), [Task Scope as Security Boundary](task-scope-security-boundary.md). Permissions: [Agent Network Egress Policy](agent-network-egress-policy.md), [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md), [Permission-Gated Commands](permission-gated-commands.md). Autonomy: [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md), [Safe Outputs Pattern](safe-outputs-pattern.md). | saturated |
| [LLM07:2025 System Prompt Leakage](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/) | System prompts in coding-agent harnesses carry instructions, sometimes credentials, and the tool catalog; exfiltration paths include malicious tool descriptions, jailbreak chains, and chained injection through fetched content. | [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) (system-prompt exfiltration via malicious tool descriptions) | partial |
| [LLM08:2025 Vector and Embedding Weaknesses](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) | RAG-equipped coding agents expose the embedding-and-retrieve pipeline as an attack surface: chunk-level authorization gaps, embedding inversion, and relevance-not-authorization ranking. | [Multitenant RAG: Relevance-Authorization Gap](multitenant-rag-authorization-gap.md), [RAG Architecture as a Poisoning Robustness Decision](rag-architecture-poisoning-robustness.md) | partial |
| [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/) | For coding agents the misinformation surface is hallucinated APIs, fabricated dependency versions, and confident-wrong refactors — verification-side defenses carry the load. | [Coding Agent Misalignment Forms](../patterns/anti-patterns/coding-agent-misalignment-forms.md), [Objective Drift](../patterns/anti-patterns/objective-drift.md), [Chain-of-Verification for Coding Agents](../verification/chain-of-verification-coding-agents.md), [Incremental Verification](../verification/incremental-verification.md) | partial |
| [LLM10:2025 Unbounded Consumption](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/) | Long-running coding agents that loop on tool output, fan out sub-agents, or retry on transient errors can drain token and rate-limit budgets — a denial-of-wallet failure mode distinct from classical DoS. | No direct coverage of denial-of-wallet for coding agents; [Cryptographic Governance Audit Trail](cryptographic-governance-audit-trail.md) and [MCP Runtime Control Plane](mcp-runtime-control-plane.md) touch budget enforcement adjacently. | gap |

## Why it works

Practitioners arrive at security material with the vocabulary their training, compliance reviews, and tooling use — and for LLM risk that vocabulary is overwhelmingly the OWASP LLM Top 10, the most-searched LLM risk framework as captured by industry summaries such as [Aembit's market overview](https://aembit.io/blog/owasp-top-10-llm-risks-explained/) and [Security Boulevard's 2026 explainer](https://securityboulevard.com/2026/03/the-owasp-top-10-for-llm-applications-2025-explained-simply/). This site indexes the same threats by mechanism — sandboxing, permissions, tool invocation, supply chain — because that is how engineers reason about controls during a build-out, the same organizing principle used by the [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md). A crosswalk closes the gap by giving readers a stable mapping from the framework names they searched to the mechanism-organized pages that answer the risk for a coding-agent context. The pattern is the same one [Tool Signing and Signature Verification](tool-signing-verification.md) already uses at the page level to cite [OWASP MCP03:2025 Tool Poisoning](https://owasp.org/www-project-mcp-top-10/2025/MCP03-2025%E2%80%93Tool-Poisoning) — vocabulary at the top, mechanism in the body.

## When this backfires

A crosswalk is a discovery aid, not a threat model — five conditions make it actively misleading if treated as one.

- Coding agents are not chat apps. [LLM05](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) and [LLM09](https://genai.owasp.org/llmrisk/llm092025-misinformation/) are framed around chat output returned to a human reviewer. For a coding agent the "output" is emitted code, shell commands, and tool arguments that downstream systems execute. Reuse of OWASP's chat-app phrasing produces controls that do not match the actual sink — the row-level agent-specific framing above is what avoids that.
- Pre-trained model assumption. [LLM04 Data and Model Poisoning](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/) primarily targets training and fine-tuning datasets. Most coding-agent builders consume vendor APIs and have no influence over pretraining. A literal LLM04 crosswalk that routes readers to training-pipeline controls misallocates attention; the agent-relevant slice is RAG / KG / memory poisoning, which is what this row links.
- Two OWASP frameworks now coexist. The [Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) explicitly targets autonomous systems and overlaps but does not duplicate the LLM Top 10. Treating this crosswalk as the only OWASP integration on the site leaves the reader unable to choose; the page header points to both frameworks for that reason.
- OWASP text is CC-BY-SA 4.0. Reproducing official risk descriptions verbatim creates an attribution-and-share-alike obligation and weakens originality. This crosswalk leads every row with an agent-specific manifestation in the site's own words and links to OWASP for the canonical text.
- Coverage flags age out. A "gap" row becomes wrong the moment a sibling page lands. The `last_reviewed` frontmatter dates this snapshot; the full-audit pipeline refreshes it on every audit run. Readers who land here years later should treat coverage flags as a reading aid, not a current site index.

## Key Takeaways

- The OWASP LLM Top 10 (2025) is the dominant shared vocabulary for LLM risk; this crosswalk closes the gap between that vocabulary and this site's mechanism-organized pages.
- For coding agents specifically, the [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) is the more directly applicable framework — use this page for navigation, not as a threat model.
- LLM01, LLM02, LLM03, and LLM06 are saturated on this site; LLM04 is covered; LLM05, LLM07, LLM08, and LLM09 are partial; LLM10 is a gap as of the `last_reviewed` date.
- Pair the crosswalk with mechanism-based models — [Four-Layer Taxonomy](four-layer-agent-security-taxonomy.md), [Lethal Trifecta](lethal-trifecta-threat-model.md), [Defense-in-Depth](defense-in-depth-agent-safety.md) — for the controls a coding-agent build actually composes.

## Related

- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — mechanism-organized navigation grid that pairs with the framework-organized crosswalk above
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — lifecycle-phase taxonomy these named threats map onto; the crosswalk is a lookup table, not a competing frame
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — capability-based threat model for the trifecta that underlies LLM01 / LLM02 / LLM06
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — independent-mechanism layering across all ten risk categories
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — primary LLM01 entry for coding agents
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — LLM05 (improper output handling) and LLM07 (system-prompt leakage) adjacencies for tool-using agents
- [Vetting Tool Definitions for Exfiltration Signatures](vetting-tool-definitions-before-install.md) — LLM06 (excessive agency) install-time complement: refusing a leak-signature tool definition before it is ever granted

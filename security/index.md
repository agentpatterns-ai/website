---
title: "Security for AI Agent Development"
description: "Patterns and techniques for building AI agents that resist prompt injection, protect sensitive data, contain blast radius, and fail safely under attack."
tags:
  - security
  - agent-design
---
# Security

> Patterns and techniques for building agents that resist manipulation, protect sensitive data, and fail safely.

## Threat Models

Threat models identify the structural conditions that make agent systems exploitable and prescribe architectural mitigations.

- [Action-Audit Divergence: A Four-Mode Taxonomy for Runtime Hardening](action-audit-divergence-taxonomy.md) — Name the four ways an agent action can diverge from its audit record (gate-bypass, audit-forgery, silent host failure, wrong-target) to convert "is this runtime hardened?" into a coverage checklist against existing controls
- [Compositional Vulnerability Induction in Coding Agents](compositional-vulnerability-induction.md) — Decomposing a malicious end-state into three innocuous engineering tickets bypasses refusal and hardening defenses at 53–86% ASR across nine production coding agents; pentester-framed reviewers close most of the gap
- [Constraint Drift: Why Safety Must Be Maintained, Not Asserted](constraint-drift-multi-agent-safety.md) — Safety constraints encoded in prompts weaken across six trajectory surfaces — memory, delegation, communication, tool use, audit, optimization; the four-property invariant (fresh, inherited, enforceable, auditable) keeps them operative when delegation depth, memory persistence, and tool surface compose
- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — Group threats into context/instruction, tool/action, state/persistence, and ecosystem/automation layers to map controls and surface coverage gaps where attacks propagate across boundaries
- [Goal Reframing: The Primary Exploitation Trigger for LLM Agents](goal-reframing-exploitation-trigger.md) — A 10,000-trial taxonomy finds goal reframing — not social engineering or incentives — is the one prompt condition that reliably triggers vulnerability exploitation across models
- [History Anchors: Consistency-Cued Continuation of Unsafe Prior Actions](history-anchor-consistency-injection.md) — A single sentence asking the model to stay consistent with prior history flips frontier LLM agents from near-zero unsafe selection to 91–98% on HistoryAnchor-100; the consistency cue is load-bearing, not the history alone, and flagship models are the most-affected sibling within each family
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — Risk emerges when an agent has private data access, untrusted input, and egress simultaneously; remove at least one leg from every execution path
- [Oracle Poisoning: Knowledge Graph Corruption Against Tool-Using Agents](oracle-poisoning-knowledge-graph.md) — Corrupting a knowledge graph an agent queries via tool-use produces 100% trust at moderate attacker sophistication across nine models; the attack is distinct from prompt injection because the data path, not the instruction path, carries the payload
- [RAG Architecture as a Poisoning Robustness Decision](rag-architecture-poisoning-robustness.md) — Under controlled knowledge-base poisoning, attack success rates span 24.4% to 81.9% across four RAG architectures with comparable clean accuracy; architecture choice is part of the threat model
- [Trojan Hippo: Cross-Session Memory Poisoning for Data Exfiltration](trojan-hippo-memory-exfiltration.md) — A single untrusted tool call plants a dormant payload in agent memory that activates sessions later when the user discusses sensitive topics; tested defenses cut attack success to 0–5% but at steep utility cost
- [Trojan Hippo: Dormant Memory Payloads That Wait for Sensitive Topics](trojan-hippo-memory-attack.md) — A single untrusted tool call plants a payload in agent memory that activates only when the user later discusses finance, health, or identity, then exfiltrates the data

## Prompt Injection

Prompt injection is the primary attack vector for agents that consume untrusted content. External instructions embedded in web pages, emails, documents, or API responses can redirect an agent's behavior at the model level.

- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md) — Restrict the LLM to selecting from a fixed action catalog; tool outputs never re-enter the model, making control-flow hijacking structurally impossible
- [CaMeL: Defeating Prompt Injections by Separating Control and Data Flow](camel-control-data-flow-injection.md) — Separate trusted control flow from untrusted data flow so injection attacks cannot alter tool invocation, regardless of model susceptibility
- [Clarification Mode Amplifies Prompt Injection](clarification-mode-injection-amplification.md) — A clarify-then-act turn raises injection success rates from 1–11% to 24–63% across frontier models; treat clarification as an untrusted-input channel, not a safety control
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md) — Use new attack traces to adversarially train hardened model checkpoints immediately after discovery
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md) — Architectural patterns and defense-in-depth strategies for building coding agents that stay resilient when untrusted input lands in context
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md) — Map retrieval paths, audit against the Lethal Trifecta, and test with synthetic payloads to find the vulnerabilities standard testing misses
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — Mandatory checkpoints before irreversible actions let humans catch injection-driven misbehavior before it causes harm
- [Plan-Then-Execute as the Default for Web Agents](plan-then-execute-web-agents.md) — Web content mixes inputs from many parties; committing to a task-specific program before observing pages lets untrusted content change values inside the plan but never rewrite the plan
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — External content consumed by agents is an attack surface; malicious instructions can override agent instructions at the model level
- [Provenance-Aware Decision Auditing for LLM Agents](provenance-aware-decision-auditing.md) — Build an influence provenance graph at runtime, trace each tool-call argument to its source span, and release actions only when benign evidence alone justifies them
- [RL-Trained Automated Red Teamers for Prompt Injection Discovery](rl-automated-red-teamers.md) — Train an LLM-based attacker with reinforcement learning to discover novel injection vectors before adversaries do
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — Narrow task scope limits both the attack surface and the blast radius of a successful injection

**Anti-pattern:** [Single-Layer Prompt Injection Defence](../anti-patterns/single-layer-injection-defence.md) — Relying on one safeguard leaves agents vulnerable to attack vectors that layer does not address

## Sandboxing

Isolation limits what a compromised or misbehaving agent can affect.

- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — Enforce both filesystem and network isolation simultaneously; neither boundary alone prevents exfiltration
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md) — Define guardrail rules only for tools your harness controls; external tools must enforce their own
- [Selective Network Access in Agent Sandboxes: The `allowNetwork` Pattern](selective-network-sandbox-mode.md) — A sandbox mode that keeps filesystem isolation but lifts network restrictions; safe only when egress is enforced at a layer below the harness
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — A third isolation layer that prevents Bash subprocesses from persisting daemons across sessions and leaking secrets through inherited environment variables
- [Use a Public-Web Index to Gate Automatic URL Fetching](url-fetch-public-index-gate.md) — Cross-reference URLs against an independent crawl index before allowing automatic fetching
- [Windows Sandboxing for Coding Agents](windows-sandbox-primitives-coding-agents.md) — AppContainer, Windows Sandbox, and MIC each fail a specific coding-agent requirement; the working pattern composes synthetic SIDs and write-restricted tokens, with WSL2 as the strictly-stronger fallback

## Data Protection

Preventing sensitive data from entering agent context is cheaper than scrubbing it after the fact.

- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md) — Keep credentials out of skill definitions at authoring time; placeholder syntax, pre-commit scanning, and wrapper scripts prevent leakage when skills are shared or reproduced
- [Heartbeat-Bound Hierarchical Credentials for Agent Swarms](heartbeat-bound-hierarchical-credentials.md) — Bind sub-agent credentials to periodic parent liveness proofs so descendants expire within a deterministic window when the parent stops; closes the zombie-agent gap without a network revocation round-trip but only when parent keys live in secure enclaves and clock skew is bounded
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md) — Replace sensitive fields with deterministic tokens before data reaches the model
- [Privacy-Preserving LLM Requests](privacy-preserving-llm-requests.md) — Eight techniques exist for keeping sensitive content out of cloud LLM APIs; only four are practical today, and composing local routing with redact-and-rephrase cuts PII leakage to 0.6%
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — Use permission rules and hooks to prevent agents from reading credentials and secrets
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — Keep broad credentials outside the sandbox; use an external proxy that attaches scoped tokens only to validated requests
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — Inject credentials as environment variables so secrets never appear in context or generated code
- [Sensitive Terminal Prompt Interception](sensitive-terminal-prompt-interception.md) — Detect password and verification-code prompts in an agent-driven terminal, confirm in default mode, cancel in auto-approve mode; necessary but not sufficient against MCP-injected secrets and non-interactive credential reads
- [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) — Replace long-lived API keys with short-lived OIDC tokens minted from the runtime's existing workload identity; the federation rule that decides which workloads federate is itself a security boundary
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md) — The URL itself is a data channel; agents that construct or follow URLs from untrusted content can leak context before a response is read
- [Multitenant RAG: Closing the Relevance-Authorization Gap](multitenant-rag-authorization-gap.md) — Retrieval ranks by relevance, not authorization — in a shared corpus, the highest-scoring chunk for one tenant can belong to another; close the gap with policy-aware ingestion, two-tier retrieval gating, and server-side orchestration

## Permissions

Excess permissions expand the blast radius of any failure or attack.

- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — Restrict which domains agent tools can reach via harness-enforced allow and deny lists; remove the model from the network trust boundary
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — Limit agent access to only what the current task requires; excess permissions directly amplify injection impact
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md) — Block agent startup until remote managed settings are freshly validated; exit rather than run with stale or missing policy
- [Five-Stage Policy Layer Typology for Generalist Agents](policy-as-code-layer-typology.md) — Decompose agent governance into Intent Guard, Playbook, Tool Guide, Tool Approval, and Output Formatter that wrap a generalist agent without fine-tuning; only Tool Approval and the deterministic portion of Tool Guide carry hard enforcement guarantees
- [Org-Membership-Gated Agent Entitlement](org-membership-gated-agent-entitlement.md) — Gate AI chat activation on directory-managed GitHub organization membership via VS Code's `ChatApprovedAccountOrganizations` device policy; fail-closed and structurally distinct from seat licences
- [Permission-Gated Custom Commands](permission-gated-commands.md) — Pre-approve the tools a Claude Code slash command may use via frontmatter, narrowing the expected surface for shared commands
- [Permission Framework Choice Outweighs Model Choice for Limiting Overeager Actions](permission-framework-over-model.md) — Across four coding-agent frameworks and six base models, ask-to-continue harnesses produce 0.2–4.5% overeager-action rates vs 5.4–27.7% for permissive defaults; the same model swings >25 percentage points across frameworks
- [Pre-Execution Risk Classification for Terminal Commands](pre-execution-command-risk-classification.md) — Display a tiered Safe/Caution/Review-carefully badge with command-specific text before the agent runs a terminal command; an attention-allocation lever paired with deterministic allowlists that carry the policy load
- [Safe Outputs Pattern](safe-outputs-pattern.md) — Default agents to read-only and require explicit grants for each write output type, producing a deterministic blast radius
- [Sufficiency-Tightness Decomposition for Agent-Authored Permissions](sufficiency-tightness-policy-decomposition.md) — Models authoring a file-rwx policy in one pass land at a broad-but-exposed or tight-but-brittle attractor that more reasoning amplifies; AuthBench shows splitting policy generation into a coverage pass and an audit pass improves sensitive-task success by up to 15.8% on tightness-biased models
- [Task-Based Access Control with Hybrid Inspection](task-based-access-control-hybrid-inspection.md) — Bind each tool call to the user's current task via short-lived signed credentials, with a semantic axis flagging in-scope-but-off-task calls; the deterministic axis carries the security guarantee
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — Mine session transcripts for repeated read-only tool calls and propose a prioritized allowlist — narrower than bypass, tighter than manual curation

## Code Injection

Code injection in multi-agent pipelines exploits agent trust in code it reads as input, distinct from prompt injection against a single agent.

- [Code Injection Attacks on Multi-Agent Systems: Coder-Reviewer-Tester as Defence](code-injection-multi-agent-defence.md) — A coder-reviewer-tester architecture with a dedicated security analysis agent achieves the highest resilience while recovering efficiency losses

## Multi-Agent Propagation

Multi-agent systems with shared retrieval propagate adversarial content agent-to-agent. Defenses target the contagion channel and the per-agent detection signal.

- [Foresight-Guided Defense Against Infectious Jailbreaks in Multi-Agent Systems](foresight-guided-multi-agent-jailbreak-defense.md) — Per-agent persona simulation detects diversity collapse from poisoned shared memory, then surgically rolls back or bisects the album to remove contamination without homogenizing healthy agents

## PR-Time and Scheduled Review

Operational patterns that apply security agents to incoming changes and to resident codebase risk on different cadences.

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — Pair a PR-time security reviewer with a scheduled whole-codebase scanner so new and resident risk both have continuous coverage; treat the reviewer agent itself as an injection target
- [Harness Composition for Scaled Security Audits](security-audit-harness-composition.md) — Compose steering, scaling, and stacking primitives so an audit harness produces actionable findings at maintainer-tolerable triage cost; Mozilla used this pattern to take Firefox security fixes from 17–31/month (2025) to 423 in April 2026
- [Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools](scanner-as-mcp-server.md) — Ship the security scanner as an MCP server so the agent invokes typed scans pre-commit and reasons over structured findings; qualified by five failure modes including agent-skips-scan and lethal-trifecta closure on the scanner principal

## Tool Invocation

Tool invocation exposes attack surfaces distinct from prompt injection. Malicious tools exploit argument generation and return processing to leak context and execute arbitrary commands.

- [Agentic Detection and Response at the MCP Boundary](agentic-detection-response-mcp.md) — Instrument the MCP transport so agent reasoning, prompts, and tool calls become a runtime detection signal; Uber's ADR system reports 97.2% precision at >10,000 sessions/day across 7,200+ hosts, with a two-tier triage design that amortises LLM inference cost
- [Behavioral Firewall for Tool-Call Trajectories](behavioral-firewall-tool-call-trajectories.md) — Compile verified benign tool-call telemetry into a parameterized DFA and enforce permitted sequences and parameter bounds at runtime; fits structured workflows with stable tool catalogs
- [Cognitive Poisoning: Untrusted Tool Feedback as a Trajectory Attack](cognitive-poisoning-tool-feedback.md) — Malicious tools steer agent reasoning across benign-looking responses then trigger harm only when final-action parameters satisfy hidden conditions; per-message defenses score 0.0 on GuardedJoint because maliciousness is conditioned on joint state-action, not any single message
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md) — Combine five deterministic structural checks at the agent-tool boundary with a semantic task-to-tool matcher; the two attack classes are orthogonal so neither layer alone suffices
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — Intercept every MCP tool call at a single policy evaluation point — identity, tool name, arguments, rate limits — before the call reaches the server
- [Mid-Trajectory Guardrail Selection for Multi-Step Tool Calls](mid-trajectory-guardrail-selection.md) — Guardrail efficacy in multi-step tool-calling workflows correlates with structural data competence more than safety alignment; select guard models accordingly
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — Malicious MCP tools exploit argument generation to leak system prompts and chain description-plus-return injection to achieve remote code execution

## Supply Chain

Agents dynamically load tools from MCP servers, plugins, and registries at runtime. A tampered tool inherits the agent's full permissions.

- [Containment Playbook: npm-to-Signing-Channel Compromise](npm-signing-channel-containment-playbook.md) — A consumer-side `npm install` worm reaches developer machines, harvests credentials, pivots into internal repos, and reaches signing material; the playbook isolates, rotates, freezes, re-signs, revokes, and ships a forcing-function client update — modeled on OpenAI's May 2026 TanStack response
- [Enterprise-Managed Plugin Governance for Agent CLIs](enterprise-managed-plugin-governance.md) — The managed plugin contract is four levers (catalogue allow/block, plugin enable, version pin, policy-change behaviour) checked before any network or filesystem operation; Copilot CLI, Claude Code, and Cursor expose convergent but unequal surfaces and pre-existing installs survive policy until next refresh
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — Across 10 models on 1,000 Python tasks, 36.7%-55.7% of LLM-specified versions contain known CVEs and all models converge on the same risky releases — pin against an external vulnerability source, not the model's training prior
- [Semantic Intent Validation for Agent Skills](semantic-intent-validation-skills.md) — Signature scanning catches 90.7% of malicious skills but misses payload-less attacks where the agent synthesises the payload at runtime; multi-model intent-vs-behavior consensus drives the residual bypass rate from 11.6%–33.5% to 1.6%
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — Malicious skills injected into public registries exploit in-context learning to execute payloads hidden in documentation examples, bypassing alignment that blocks explicit instruction injection
- [Tool Signing and Signature Verification](tool-signing-verification.md) — Require cryptographic signature verification (Sigstore/Cosign) before an agent loads or invokes a tool

## Defense in Depth

No single safety mechanism is sufficient. Layered defenses ensure that failure of one layer does not compromise the agent.

- [Cryptographic Governance Audit Trail](cryptographic-governance-audit-trail.md) — Wrap tool calls with policy validation and post-quantum receipt signing to produce a tamper-evident, append-only action log for regulated environments
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — Layer five independent safety mechanisms so no single failure point can compromise agent behavior
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md) — Move agents to production through three control gates — governance, observability, reproducibility — with MUST/SHOULD checklists for each
- [Sandbox + Approvals + Auto-Review Governance Triad](sandbox-approvals-auto-review-triad.md) — Compose a sandbox boundary, tiered approval policy, auto-review reviewer for boundary crossings, and agent-native telemetry as one production governance posture; adopt only when action volume, admin-enforced config, OTel, and human-gated irreversible actions all hold
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — Embed defense mechanisms into each execution lifecycle phase with cross-layer feedback so layers coordinate rather than operate in isolation
- [Security Constitution for AI Code Generation](security-constitution-ai-code-gen.md) — Formalize security constraints as a versioned, machine-readable constitution that feeds agent specs, linters, and CI gates
- [Security Drift in Iterative LLM Code Refinement](security-drift-iterative-refinement.md) — Iterative fix-test loops optimize for functional correctness while silently accumulating security regressions that no functional test exercises
- [Usability Pressure as a Silent Security-Regression Vector](usability-pressure-security-regression.md) — Explicit usability requirements (performance, simplicity, new features) in a single-shot prompt cause LLMs to drop implicit security constraints at up to 98.1% attack success rate; mitigated by making security explicit and gating every output through a scanner
- [Verifying LLM-Generated Cryptographic Code](llm-cryptographic-code-verification.md) — Crypto generation fails with 23.3% compile rate and 57% vulnerabilities; pair every crypto code path with a rule-based crypto analyzer, prefer zero-shot over CoT, and constrain to vetted high-level APIs

## Economics

Sizing frames for pre-release security review when vulnerability discovery scales with inference spend.

- [Security Budget as Token Economics](security-budget-token-economics.md) — Treat hardening as a budget-allocation decision: AISI's Mythos evaluation shows no diminishing returns inside 100M tokens per attempt, but the outspend frame applies only where the search curve is still climbing and triage capacity absorbs findings

## Deployment Models

Release patterns for capabilities whose offense-defense asymmetry makes broad release the wrong default.

- [Restricted-Access Defensive AI: Project Glasswing as a Deployment Model](restricted-access-defensive-ai.md) — Invitation-only gating shifts the latency budget toward defenders when a model raises the offensive ceiling more than broad access raises the defensive floor; the contract structure, exit criteria, and what AppSec teams should evaluate when offered access

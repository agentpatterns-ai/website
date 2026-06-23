---
title: "Security for AI Agent Development"
description: "Patterns and techniques for building AI agents that resist prompt injection, protect sensitive data, contain blast radius, and fail safely under attack."
tags:
  - security
  - agent-design
  - index
last_reviewed: 2026-05-27
---
# Security

> Patterns and techniques for building agents that resist manipulation, protect sensitive data, and fail safely.

## Threat Models

Threat models identify the structural conditions that make agent systems exploitable and prescribe architectural mitigations.

- [Action-Audit Divergence: A Four-Mode Taxonomy for Runtime Hardening](action-audit-divergence-taxonomy.md) — Name the four ways an agent action can diverge from its audit record (gate-bypass, audit-forgery, silent host failure, wrong-target) to convert "is this runtime hardened?" into a coverage checklist against existing controls
- [Compositional Vulnerability Induction in Coding Agents](compositional-vulnerability-induction.md) — Decomposing a malicious end-state into three innocuous engineering tickets bypasses refusal and hardening defenses at 53–86% ASR across nine production coding agents; pentester-framed reviewers close most of the gap
- [Constraint Drift: Why Safety Must Be Maintained, Not Asserted](constraint-drift-multi-agent-safety.md) — Safety constraints encoded in prompts weaken across six trajectory surfaces — memory, delegation, communication, tool use, audit, optimization; the four-property invariant (fresh, inherited, enforceable, auditable) keeps them operative when delegation depth, memory persistence, and tool surface compose
- [Context-Fractured Decomposition Attacks on Tool-Using Agents](context-fractured-decomposition-attacks.md) — Attacks split across tools, modules, and time slip past defenders that only inspect a single contiguous conversation; artifact provenance gaps let benign intermediate steps recompose into a jailbreak downstream, lifting attack success by up to 28.3 percentage points
- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — Group threats into context/instruction, tool/action, state/persistence, and ecosystem/automation layers to map controls and surface coverage gaps where attacks propagate across boundaries
- [Goal Reframing: The Primary Exploitation Trigger for LLM Agents](goal-reframing-exploitation-trigger.md) — A 10,000-trial taxonomy finds goal reframing — not social engineering or incentives — is the one prompt condition that reliably triggers vulnerability exploitation across models
- [Improper Output Handling: Validate Agent Output Before Downstream Use](improper-output-handling-downstream-sinks.md) — OWASP LLM05 — agent output executed, rendered, or interpreted downstream without per-sink validation is an injection surface; enumerate the sinks (commit, exec, SQL, render, install) and gate each one
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — Risk emerges when an agent has private data access, untrusted input, and egress simultaneously; remove at least one leg from every execution path
- [Oracle Poisoning: Knowledge Graph Corruption Against Tool-Using Agents](oracle-poisoning-knowledge-graph.md) — Corrupting a knowledge graph an agent queries via tool-use produces 100% trust at moderate attacker sophistication across nine models; the attack is distinct from prompt injection because the data path, not the instruction path, carries the payload
- [OWASP LLM Top 10 (2025): Agent Security Crosswalk](owasp-llm-top-10-2025-agent-crosswalk.md) — Map each OWASP LLM Top 10 (2025) risk to coding-agent-specific manifestations and site pages — a navigation aid for readers arriving with the framework's shared vocabulary, not a recommended threat model
- [Pre-Trust Execution Surface in Coding Agent Harnesses](pre-trust-execution-surface.md) — Project-local config (settings files, hooks, MCP manifests, env vars, localhost listeners) executes before the trust prompt fires; defer parsing and execution until after the trust boundary is established
- [RAG Architecture as a Poisoning Robustness Decision](rag-architecture-poisoning-robustness.md) — Under controlled knowledge-base poisoning, attack success rates span 24.4% to 81.9% across four RAG architectures with comparable clean accuracy; architecture choice is part of the threat model
- [Trojan Hippo: Dormant Memory Payloads Triggered by Sensitive Topics](trojan-hippo-memory-attack.md) — A single untrusted tool call plants a dormant payload in agent memory that activates sessions later when the user discusses sensitive topics, exfiltrating data via outbound tools; tested defenses cut attack success to 0–5% but at steep utility cost
- [Unbounded Consumption: Bounding Agent Resource Use Against DoS and Denial-of-Wallet](unbounded-consumption-resource-bounds.md) — OWASP LLM10:2025 framed as a same-surface, two-owner threat (availability and finance); the five complementary bounds — per-call token, per-task iteration, fan-out concurrency, cost-velocity, per-day dollar — close the cost dimension no single layer covers, with $46K/day Sysdig and $82K/48hr Gemini incidents as the empirical floor

## Prompt Injection

Prompt injection is the primary attack vector for agents that consume untrusted content. External instructions embedded in web pages, emails, documents, or API responses can redirect an agent's behavior at the model level.

- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md) — Restrict the LLM to selecting from a fixed action catalog; tool outputs never re-enter the model, making control-flow hijacking structurally impossible
- [Dual-Graph Alignment for Indirect Prompt Injection Defense (AuthGraph)](authgraph-dual-graph-injection-defense.md) — Compare a clean authorization graph from user intent against the execution-trace provenance graph; 0.01 ASR / 0.69 UR on AgentDojo at 4.23× token cost, bounded by same-observation pollution and multi-agent gaps
- [CaMeL: Defeating Prompt Injections by Separating Control and Data Flow](camel-control-data-flow-injection.md) — Separate trusted control flow from untrusted data flow so injection attacks cannot alter tool invocation, regardless of model susceptibility
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md) — Use new attack traces to adversarially train hardened model checkpoints immediately after discovery
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md) — Architectural patterns and defense-in-depth strategies for building coding agents that stay resilient when untrusted input lands in context
- [Destyling Untrusted Input as a Prompt Injection Defense](destyling-untrusted-input.md) — Normalise the surface style of untrusted input before the model encodes who is speaking; cuts CoT-forgery attack success from 61% to 10% on a static benchmark by interrupting role perception at the representational layer
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md) — Map retrieval paths, audit against the Lethal Trifecta, and test with synthetic payloads to find the vulnerabilities standard testing misses
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — Mandatory checkpoints before irreversible actions let humans catch injection-driven misbehavior before it causes harm
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — Tag every value with a sink-specific capability budget and intersect budgets through tool composition; closes permission laundering only with expert-crafted manifests and explicit-flow attacks
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — External content consumed by agents is an attack surface; malicious instructions can override agent instructions at the model level
- [Provenance-Aware Decision Auditing for LLM Agents](provenance-aware-decision-auditing.md) — Build an influence provenance graph at runtime, trace each tool-call argument to its source span, and release actions only when benign evidence alone justifies them
- [RL-Trained Automated Red Teamers for Prompt Injection Discovery](rl-automated-red-teamers.md) — Train an LLM-based attacker with reinforcement learning to discover novel injection vectors before adversaries do
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — Narrow task scope limits both the attack surface and the blast radius of a successful injection

**Anti-pattern:** [Single-Layer Prompt Injection Defence](../anti-patterns/single-layer-injection-defence.md) — Relying on one safeguard leaves agents vulnerable to attack vectors that layer does not address

## Sandboxing

Isolation limits what a compromised or misbehaving agent can affect.

- [Browser Sandbox for Agent-Generated HTML (Sandboxed Iframe + Immutable CSP)](browser-sandbox-agent-generated-html.md) — Run untrusted agent- or LLM-generated HTML safely in the browser by composing a `sandbox="allow-scripts allow-forms"` iframe, an immutable `<meta>` Content-Security-Policy, and a MessageChannel-scoped allow-listed parent API
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — Enforce both filesystem and network isolation simultaneously; neither boundary alone prevents exfiltration
- [Network-less Container + Unix-Socket Egress Proxy for Agent Sandboxes](network-less-container-unix-socket-egress.md) — `--network none` plus a mounted Unix socket makes the egress proxy the only path off the container, turning policy into topology
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md) — Define guardrail rules only for tools your harness controls; external tools must enforce their own
- [Selective Network Access in Agent Sandboxes: The `allowNetwork` Pattern](selective-network-sandbox-mode.md) — A sandbox mode that keeps filesystem isolation but lifts network restrictions; safe only when egress is enforced at a layer below the harness
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — A third isolation layer that prevents Bash subprocesses from persisting daemons across sessions and leaking secrets through inherited environment variables
- [Use a Public-Web Index to Gate Automatic URL Fetching](url-fetch-public-index-gate.md) — Cross-reference URLs against an independent crawl index before allowing automatic fetching
- [In-Process WebAssembly Sandboxes for Agent-Generated Code](wasm-sandbox-agent-code-execution.md) — Embed a WebAssembly runtime inside your Python or JavaScript application to execute agent- or LLM-generated code with CPU and memory caps, no filesystem or network by default, and explicit host-function interop

**Anti-pattern:** [Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot](hostname-allowlist-tls-blind-spot.md) — A hostname-allowlist proxy without TLS termination enforces the client-supplied destination, not the actual destination; broad shared-CDN entries open domain-fronting and similar exfil paths

## Data Protection

Preventing sensitive data from entering agent context is cheaper than scrubbing it after the fact.

- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md) — Keep credentials out of skill definitions at authoring time; placeholder syntax, pre-commit scanning, and wrapper scripts prevent leakage when skills are shared or reproduced
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md) — Replace sensitive fields with deterministic tokens before data reaches the model
- [Privacy-Preserving LLM Requests](privacy-preserving-llm-requests.md) — Eight techniques exist for keeping sensitive content out of cloud LLM APIs; only four are practical today, and composing local routing with redact-and-rephrase cuts PII leakage to 0.6%
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — Use permission rules and hooks to prevent agents from reading credentials and secrets
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — Keep broad credentials outside the sandbox; use an external proxy that attaches scoped tokens only to validated requests
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — Inject credentials as environment variables so secrets never appear in context or generated code
- [System Prompt as Secret Store (OWASP LLM07)](system-prompt-not-a-secret-store.md) — Treating the system prompt as a confidentiality boundary is the underlying vulnerability — secrets, credentials, and security-critical logic in the prompt are recoverable at 84–92% ASR on frontier models
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md) — The URL itself is a data channel; agents that construct or follow URLs from untrusted content can leak context before a response is read
- [Agent-Authored Messages as a Deferred Exfiltration Channel](agent-authored-message-rendered-image-exfiltration.md) — An auto-fetching renderer downstream of an agent's message-authoring tool acts as deferred egress, closing the lethal trifecta without any direct network grant
- [Multitenant RAG: Closing the Relevance-Authorization Gap](multitenant-rag-authorization-gap.md) — Retrieval ranks by relevance, not authorization — in a shared corpus, the highest-scoring chunk for one tenant can belong to another; close the gap with policy-aware ingestion, two-tier retrieval gating, and server-side orchestration
- [Per-Server MCP Environment Scoping for Credential Isolation](mcp-server-credential-isolation.md) — Each MCP server gets its own env-variable scope, not the agent process's full env, so one server's credentials never leak to every other server the agent talks to; the configuration-layer complement to credential proxies and federated identity
- [Multi-Tenant Isolation Knobs for Shared-Container Agent SDK Hosting](multi-tenant-isolation-knobs-agent-sdk.md) — Four Claude Agent SDK options plus a per-tenant proxy-egress rule that sever each default settings-and-state input (filesystem settings, `~/.claude.json`, auto memory, inherited `cwd`) when one container serves multiple tenants
- [Embedding Inversion: Vector Stores as a Source-Text Disclosure Surface](embedding-inversion-vector-store-disclosure.md) — Stored embeddings can be partially inverted to reconstruct source text — the LLM08:2025 confidentiality slice that access-control and poisoning defenses do not address; treat the vector index as a copy of the corpus

## Permissions

Excess permissions expand the blast radius of any failure or attack.

- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — Restrict which domains agent tools can reach via harness-enforced allow and deny lists; remove the model from the network trust boundary
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — Decompose task authority into a step-level authority context the dispatch layer can check; runtime content may inform the planner but never become the issuer that authorizes a side effect
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — Limit agent access to only what the current task requires; excess permissions directly amplify injection impact
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md) — Block agent startup until remote managed settings are freshly validated; exit rather than run with stale or missing policy
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — Writes to `.npmrc`, `.yarnrc`, `bunfig.toml`, `.bazelrc`, `.pre-commit-config.yaml`, and `.devcontainer/` are execution-escalations — interrupt permissive edit modes at the write site, complementing execution-side defaults like `ignore-scripts=true`
- [Org-Membership-Gated Agent Entitlement](org-membership-gated-agent-entitlement.md) — Gate AI chat activation on directory-managed GitHub organization membership via VS Code's `ChatApprovedAccountOrganizations` device policy; fail-closed and structurally distinct from seat licences
- [Permission-Gated Custom Commands](permission-gated-commands.md) — Pre-approve the tools a Claude Code slash command may use via frontmatter, narrowing the expected surface for shared commands
- [Pre-Execution Risk Classification for Terminal Commands](pre-execution-command-risk-classification.md) — Display a tiered Safe/Caution/Review-carefully badge with command-specific text before the agent runs a terminal command; an attention-allocation lever paired with deterministic allowlists that carry the policy load
- [Safe Outputs Pattern](safe-outputs-pattern.md) — Default agents to read-only and require explicit grants for each write output type, producing a deterministic blast radius
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
- [Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools](scanner-as-mcp-server.md) — Ship the security scanner as an MCP server so the agent invokes typed scans pre-commit and reasons over structured findings; qualified by five failure modes including agent-skips-scan and lethal-trifecta closure on the scanner principal

## Tool Invocation

Tool invocation exposes attack surfaces distinct from prompt injection. Malicious tools exploit argument generation and return processing to leak context and execute arbitrary commands.

- [Behavioral Firewall for Tool-Call Trajectories](behavioral-firewall-tool-call-trajectories.md) — Compile verified benign tool-call telemetry into a parameterized DFA and enforce permitted sequences and parameter bounds at runtime; fits structured workflows with stable tool catalogs
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md) — Combine five deterministic structural checks at the agent-tool boundary with a semantic task-to-tool matcher; the two attack classes are orthogonal so neither layer alone suffices
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — Intercept every MCP tool call at a single policy evaluation point — identity, tool name, arguments, rate limits — before the call reaches the server
- [Mid-Trajectory Guardrail Selection for Multi-Step Tool Calls](mid-trajectory-guardrail-selection.md) — Guardrail efficacy in multi-step tool-calling workflows correlates with structural data competence more than safety alignment; select guard models accordingly
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — Malicious MCP tools exploit argument generation to leak system prompts and chain description-plus-return injection to achieve remote code execution

## Supply Chain

Agents dynamically load tools from MCP servers, plugins, and registries at runtime. A tampered tool inherits the agent's full permissions.

- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — Agents default to caret and tilde ranges because `npm install` does; for an application with a bump-bot, replace the range with an exact pin plus a lockfile-enforced install — the floating range is the leg that admits a future-compromised release
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — Across 10 models on 1,000 Python tasks, 36.7%-55.7% of LLM-specified versions contain known CVEs and all models converge on the same risky releases — pin against an external vulnerability source, not the model's training prior
- [Skill Composition Risk in Agent Ecosystems](skill-composition-risk.md) — Skills benign in isolation become harmful when one skill's output flows into the next; three failure modes (CapFlow, TrustLift, AuthBlur) reach 33.6%, 96.5%+, and 71.8% relative attack success across ten production backends, and per-skill vetting misses them by construction
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — Malicious skills injected into public registries exploit in-context learning to execute payloads hidden in documentation examples, bypassing alignment that blocks explicit instruction injection
- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](slopsquatting-hallucinated-package-names.md) — Coding LLMs hallucinate package names at 5.2%-21.7%; 43% of those names persist across re-runs, making them enumerable — attackers register the persistent names and the agent's install step pulls the malicious package
- [Tool Signing and Signature Verification](tool-signing-verification.md) — Require cryptographic signature verification (Sigstore/Cosign) before an agent loads or invokes a tool

## Defense in Depth

No single safety mechanism is sufficient. Layered defenses ensure that failure of one layer does not compromise the agent.

- [Cryptographic Governance Audit Trail](cryptographic-governance-audit-trail.md) — Wrap tool calls with policy validation and post-quantum receipt signing to produce a tamper-evident, append-only action log for regulated environments
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — Layer five independent safety mechanisms so no single failure point can compromise agent behavior
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md) — Move agents to production through three control gates — governance, observability, reproducibility — with MUST/SHOULD checklists for each
- [Inline Safety Harness with Cascade Verification (FinHarness)](inline-lifecycle-safety-harness.md) — Wrap each agent turn with prospective per-call monitors and route verification between a cheap and an advanced judge by per-step risk; worth it for high-stakes, high-call-volume workflows, not low-volume or long-context agents
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — Embed defense mechanisms into each execution lifecycle phase with cross-layer feedback so layers coordinate rather than operate in isolation
- [Lock-State Safeguards for Desktop-Controlling Agents](locked-desktop-agent-safeguards.md) — Bound an agent driving a logged-in desktop along four axes (time, visibility, presence, recovery) with short-lived authorization, covered displays, relock on local input, and manual-unlock fallback so a failure on any single axis is contained by the others
- [Security Constitution for AI Code Generation](security-constitution-ai-code-gen.md) — Formalize security constraints as a versioned, machine-readable constitution that feeds agent specs, linters, and CI gates
- [Security Drift in Iterative LLM Code Refinement](security-drift-iterative-refinement.md) — Iterative fix-test loops optimize for functional correctness while silently accumulating security regressions that no functional test exercises
- [Three-Depth In-Session Security Review](three-depth-in-session-security-review.md) — Stack a per-edit pattern match, an end-of-turn diff review, and a commit-time agentic review so each layer's cost and false-positive profile match its frequency
- [Usability Pressure as a Silent Security-Regression Vector](usability-pressure-security-regression.md) — Explicit usability requirements (performance, simplicity, new features) in a single-shot prompt cause LLMs to drop implicit security constraints at up to 98.1% attack success rate; mitigated by making security explicit and gating every output through a scanner
- [Verifying LLM-Generated Cryptographic Code](llm-cryptographic-code-verification.md) — Crypto generation fails with 23.3% compile rate and 57% vulnerabilities; pair every crypto code path with a rule-based crypto analyzer, prefer zero-shot over CoT, and constrain to vetted high-level APIs

## Economics

Sizing frames for pre-release security review when vulnerability discovery scales with inference spend.

- [Security Budget as Token Economics](security-budget-token-economics.md) — Treat hardening as a budget-allocation decision: AISI's Mythos evaluation shows no diminishing returns inside 100M tokens per attempt, but the outspend frame applies only where the search curve is still climbing and triage capacity absorbs findings

## Deployment Models

Release patterns for capabilities whose offense-defense asymmetry makes broad release the wrong default.

- [Restricted-Access Defensive AI: Project Glasswing as a Deployment Model](restricted-access-defensive-ai.md) — Invitation-only gating shifts the latency budget toward defenders when a model raises the offensive ceiling more than broad access raises the defensive floor; the contract structure, exit criteria, and what AppSec teams should evaluate when offered access

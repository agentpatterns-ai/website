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

- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — Group threats into context/instruction, tool/action, state/persistence, and ecosystem/automation layers to map controls and surface coverage gaps where attacks propagate across boundaries
- [Goal Reframing: The Primary Exploitation Trigger for LLM Agents](goal-reframing-exploitation-trigger.md) — A 10,000-trial taxonomy finds goal reframing — not social engineering or incentives — is the one prompt condition that reliably triggers vulnerability exploitation across models
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — Risk emerges when an agent has private data access, untrusted input, and egress simultaneously; remove at least one leg from every execution path

## Prompt Injection

Prompt injection is the primary attack vector for agents that consume untrusted content. External instructions embedded in web pages, emails, documents, or API responses can redirect an agent's behavior at the model level.

- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md) — Restrict the LLM to selecting from a fixed action catalog; tool outputs never re-enter the model, making control-flow hijacking structurally impossible
- [CaMeL: Defeating Prompt Injections by Separating Control and Data Flow](camel-control-data-flow-injection.md) — Separate trusted control flow from untrusted data flow so injection attacks cannot alter tool invocation, regardless of model susceptibility
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md) — Use new attack traces to adversarially train hardened model checkpoints immediately after discovery
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md) — Architectural patterns and defense-in-depth strategies for building coding agents that stay resilient when untrusted input lands in context
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md) — Map retrieval paths, audit against the Lethal Trifecta, and test with synthetic payloads to find the vulnerabilities standard testing misses
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — Mandatory checkpoints before irreversible actions let humans catch injection-driven misbehavior before it causes harm
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — External content consumed by agents is an attack surface; malicious instructions can override agent instructions at the model level
- [RL-Trained Automated Red Teamers for Prompt Injection Discovery](rl-automated-red-teamers.md) — Train an LLM-based attacker with reinforcement learning to discover novel injection vectors before adversaries do
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — Narrow task scope limits both the attack surface and the blast radius of a successful injection

**Anti-pattern:** [Single-Layer Prompt Injection Defence](../anti-patterns/single-layer-injection-defence.md) — Relying on one safeguard leaves agents vulnerable to attack vectors that layer does not address

## Sandboxing

Isolation limits what a compromised or misbehaving agent can affect.

- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — Enforce both filesystem and network isolation simultaneously; neither boundary alone prevents exfiltration
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md) — Define guardrail rules only for tools your harness controls; external tools must enforce their own
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — A third isolation layer that prevents Bash subprocesses from persisting daemons across sessions and leaking secrets through inherited environment variables
- [Use a Public-Web Index to Gate Automatic URL Fetching](url-fetch-public-index-gate.md) — Cross-reference URLs against an independent crawl index before allowing automatic fetching

## Data Protection

Preventing sensitive data from entering agent context is cheaper than scrubbing it after the fact.

- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md) — Keep credentials out of skill definitions at authoring time; placeholder syntax, pre-commit scanning, and wrapper scripts prevent leakage when skills are shared or reproduced
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md) — Replace sensitive fields with deterministic tokens before data reaches the model
- [Privacy-Preserving LLM Requests](privacy-preserving-llm-requests.md) — Eight techniques exist for keeping sensitive content out of cloud LLM APIs; only four are practical today, and composing local routing with redact-and-rephrase cuts PII leakage to 0.6%
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — Use permission rules and hooks to prevent agents from reading credentials and secrets
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — Keep broad credentials outside the sandbox; use an external proxy that attaches scoped tokens only to validated requests
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — Inject credentials as environment variables so secrets never appear in context or generated code
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md) — The URL itself is a data channel; agents that construct or follow URLs from untrusted content can leak context before a response is read

## Permissions

Excess permissions expand the blast radius of any failure or attack.

- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — Restrict which domains agent tools can reach via harness-enforced allow and deny lists; remove the model from the network trust boundary
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — Limit agent access to only what the current task requires; excess permissions directly amplify injection impact
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md) — Block agent startup until remote managed settings are freshly validated; exit rather than run with stale or missing policy
- [Org-Membership-Gated Agent Entitlement](org-membership-gated-agent-entitlement.md) — Gate AI chat activation on directory-managed GitHub organization membership via VS Code's `ChatApprovedAccountOrganizations` device policy; fail-closed and structurally distinct from seat licences
- [Permission-Gated Custom Commands](permission-gated-commands.md) — Pre-approve the tools a Claude Code slash command may use via frontmatter, narrowing the expected surface for shared commands
- [Safe Outputs Pattern](safe-outputs-pattern.md) — Default agents to read-only and require explicit grants for each write output type, producing a deterministic blast radius
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — Mine session transcripts for repeated read-only tool calls and propose a prioritized allowlist — narrower than bypass, tighter than manual curation

## Code Injection

Code injection in multi-agent pipelines exploits agent trust in code it reads as input, distinct from prompt injection against a single agent.

- [Code Injection Attacks on Multi-Agent Systems: Coder-Reviewer-Tester as Defence](code-injection-multi-agent-defence.md) — A coder-reviewer-tester architecture with a dedicated security analysis agent achieves the highest resilience while recovering efficiency losses

## PR-Time and Scheduled Review

Operational patterns that apply security agents to incoming changes and to resident codebase risk on different cadences.

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — Pair a PR-time security reviewer with a scheduled whole-codebase scanner so new and resident risk both have continuous coverage; treat the reviewer agent itself as an injection target

## Tool Invocation

Tool invocation exposes attack surfaces distinct from prompt injection. Malicious tools exploit argument generation and return processing to leak context and execute arbitrary commands.

- [Behavioral Firewall for Tool-Call Trajectories](behavioral-firewall-tool-call-trajectories.md) — Compile verified benign tool-call telemetry into a parameterized DFA and enforce permitted sequences and parameter bounds at runtime; fits structured workflows with stable tool catalogs
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — Intercept every MCP tool call at a single policy evaluation point — identity, tool name, arguments, rate limits — before the call reaches the server
- [Mid-Trajectory Guardrail Selection for Multi-Step Tool Calls](mid-trajectory-guardrail-selection.md) — Guardrail efficacy in multi-step tool-calling workflows correlates with structural data competence more than safety alignment; select guard models accordingly
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — Malicious MCP tools exploit argument generation to leak system prompts and chain description-plus-return injection to achieve remote code execution

## Supply Chain

Agents dynamically load tools from MCP servers, plugins, and registries at runtime. A tampered tool inherits the agent's full permissions.

- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — Malicious skills injected into public registries exploit in-context learning to execute payloads hidden in documentation examples, bypassing alignment that blocks explicit instruction injection
- [Tool Signing and Signature Verification](tool-signing-verification.md) — Require cryptographic signature verification (Sigstore/Cosign) before an agent loads or invokes a tool

## Defense in Depth

No single safety mechanism is sufficient. Layered defenses ensure that failure of one layer does not compromise the agent.

- [Cryptographic Governance Audit Trail](cryptographic-governance-audit-trail.md) — Wrap tool calls with policy validation and post-quantum receipt signing to produce a tamper-evident, append-only action log for regulated environments
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — Layer five independent safety mechanisms so no single failure point can compromise agent behavior
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md) — Move agents to production through three control gates — governance, observability, reproducibility — with MUST/SHOULD checklists for each
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — Embed defense mechanisms into each execution lifecycle phase with cross-layer feedback so layers coordinate rather than operate in isolation
- [Security Constitution for AI Code Generation](security-constitution-ai-code-gen.md) — Formalize security constraints as a versioned, machine-readable constitution that feeds agent specs, linters, and CI gates
- [Security Drift in Iterative LLM Code Refinement](security-drift-iterative-refinement.md) — Iterative fix-test loops optimize for functional correctness while silently accumulating security regressions that no functional test exercises
- [Verifying LLM-Generated Cryptographic Code](llm-cryptographic-code-verification.md) — Crypto generation fails with 23.3% compile rate and 57% vulnerabilities; pair every crypto code path with a rule-based crypto analyzer, prefer zero-shot over CoT, and constrain to vetted high-level APIs

## Economics

Sizing frames for pre-release security review when vulnerability discovery scales with inference spend.

- [Security Budget as Token Economics](security-budget-token-economics.md) — Treat hardening as a budget-allocation decision: AISI's Mythos evaluation shows no diminishing returns inside 100M tokens per attempt, but the outspend frame applies only where the search curve is still climbing and triage capacity absorbs findings

## Deployment Models

Release patterns for capabilities whose offense-defense asymmetry makes broad release the wrong default.

- [Restricted-Access Defensive AI: Project Glasswing as a Deployment Model](restricted-access-defensive-ai.md) — Invitation-only gating shifts the latency budget toward defenders when a model raises the offensive ceiling more than broad access raises the defensive floor; the contract structure, exit criteria, and what AppSec teams should evaluate when offered access

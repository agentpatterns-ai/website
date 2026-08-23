---
title: "Execution-Layer Security Invariants for MCP Runtimes"
term: "MCP Execution Invariants"
description: "Make MCP execution-layer security testable with eight named runtime invariants; any single connection-layer boundary blocks only 4 of 10 modeled attacks."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - eight MCP security invariants
  - Handle-Capability Protocol
  - execution-layer MCP security
last_reviewed: 2026-07-01
maturity: emerging
---

# Execution-Layer Security Invariants for MCP Runtimes

> Eight named runtime invariants make MCP execution-layer security explicit and testable, so no single bypassed check authorizes an attack.

Execution-layer security invariants are named properties a Model Context Protocol runtime enforces on every tool call and data movement, checked in code rather than assumed across clients, servers, prompts, and approval dialogs. A benchmark of the HCP (Handle-Capability Protocol) reference runtime names eight and shows that a runtime enforcing all of them blocks all ten modeled attacks, while a connection-layer mitigation that checks one boundary at a time blocks only four ([Liu, 2026](https://arxiv.org/abs/2606.29073)).

The full runtime earns its complexity under specific conditions: a multi-server deployment, an attack surface that includes confused-deputy and cross-tool data-movement risk, and providers willing to expose canonical resources and declared capabilities. A single-server, low-risk setup pays for a grant store, a handle vault, and a data-pipe policy engine it may never exercise — reach for it when the threat model, not the protocol, demands it.

## The eight invariants

Each invariant is a testable property, not a guideline. HCP defines them so a runtime either enforces the check in code or fails the benchmark case that check covers ([Liu, 2026](https://arxiv.org/abs/2606.29073)):

| Invariant | Property enforced |
|-----------|-------------------|
| Metadata non-authority | Tool descriptions and prompts cannot grant permission or override policy |
| Grant-backed approval | High-risk actions require both a matching grant and an approval |
| Canonical resources | Policy evaluates provider-resolved resources, not caller-supplied strings |
| Principal binding | A wrong principal cannot invoke or inspect handles it does not own |
| Scoped capability invocation | Required scopes trigger principal, resource, and capability matching |
| Source-and-target data-flow authorization | Moving data requires source-handle ownership and target-capability policy to both pass |
| Deny-path audit | Failed invocations, peeks, pipes, and policy decisions leave evidence |
| Explicit protocol state | Missing initialization, wrong versions, and stale sessions fail predictably |

The runtime realizes these through eight objects: a principal, a provider-canonical resource, a grant linking principal to scopes and capabilities, a capability with declared effects and approval requirements, a policy decision with reason codes, a handle that references output data in a vault, a data pipe that moves data between handles after checks, and an audit entry ([Liu, 2026](https://arxiv.org/abs/2606.29073)).

## Why one boundary is not enough

The benchmark's central result is that connection-layer conventions fail not because any single check is weak but because they check one boundary per call. The suite runs ten attack cases across five classes — tool poisoning, confused deputy, approval fatigue, context poisoning through data pipes, and transport or session confusion — against three modes ([Liu, 2026](https://arxiv.org/abs/2606.29073)):

| Mode | Controls | Attacks blocked (of 10) | Audit complete |
|------|----------|-------------------------|----------------|
| B0 naive | none | 0 | 0 |
| B1 connection-layer | metadata linting, per-call approval, session checks | 4 | 0 |
| B2 HCP runtime | all eight invariants | 10 | 10 |

B1 stops the four cases whose single boundary it happens to face and lets the other six through — confused-deputy and data-pipe cases route around the check they never meet. Ablation confirms the causality: disabling grant matching re-exposes six cases, the approval gate two, the handle-owner check one, the data-pipe target policy one, and each protocol init or version check two ([Liu, 2026](https://arxiv.org/abs/2606.29073)). Every boundary covers a distinct case, so none is redundant.

## Why it works

The invariants work because they impose multiple, non-substitutable authorization boundaries on every invocation and pipe. HCP forces each call to clear principal binding, provider-canonical resource resolution, grant matching, and the approval gate, and forces each data movement to clear both source-handle ownership and target-capability policy. No single bypassed check is sufficient to complete an attack, and the ablation demonstrates the mechanism directly: removing any one boundary re-exposes exactly the cases that boundary covered, so coverage is additive rather than overlapping ([Liu, 2026](https://arxiv.org/abs/2606.29073)). This is the execution-layer counterpart to the deterministic enforcement argument behind the [MCP Runtime Control Plane](mcp-runtime-control-plane.md): a decision independent of model judgment, decomposed here into the specific properties that decision must guarantee.

## When this backfires

The runtime is not a universal upgrade. Named conditions make it worse than a simpler control:

- Off-protocol actions bypass every invariant. The runtime binds calls that traverse it; shell commands, direct HTTP, database drivers, and headless browsers never cross the boundary, so coverage can look total while a whole class of actions is invisible — the same blind spot practitioners document for MCP gateways ([Security Boulevard, 2026](https://securityboulevard.com/2026/03/why-mcp-gateways-are-a-bad-idea-and-what-to-do-instead/)). Pair the runtime with a process sandbox that constrains off-protocol effects.
- The guarantee assumes provider cooperation. Canonical resource resolution and declared capability effects require providers to expose them; off-the-shelf MCP servers largely do not, and where they fall back to caller-supplied strings the confused-deputy protection weakens.
- Argument semantics still escape it. Grant and scope checks authorize a capability, not the meaning of its arguments — argument-injection against a pre-approved capability can escalate to remote code execution even with the policy in place ([Trail of Bits, 2025](https://blog.trailofbits.com/2025/10/22/prompt-injection-to-rce-in-ai-agents/)).
- The evidence is early. The benchmark is a single-author, ten-case synthetic suite, and the sub-millisecond overhead figures (policy explanation 0.021 ms, task start 0.101 ms, data-pipe write 0.118 ms) come from a local in-memory microbenchmark ([Liu, 2026](https://arxiv.org/abs/2606.29073v1)); a distributed grant store, policy engine, and vault add latency those numbers do not capture. Treat the attack-blocking result as a design claim to validate against your own traffic, not a field-proven bound.

## Example

Consider a confused-deputy attempt: a poisoned tool description asks the runtime to read `/etc/secrets` on behalf of a low-privilege agent. Under B1, metadata linting inspects the description text and per-call approval prompts the user, but neither resolves who may reach that resource, so a broad approval lets the read through. Under HCP the call is rejected before execution: the runtime resolves the canonical resource through the provider, looks for a grant binding the agent's principal to that resource with a read scope, finds none, and returns a `RESOURCE_DENIED` decision. The deny path writes an audit entry linking principal, capability, resource, and grant, so the failed attempt is traceable rather than silent ([Liu, 2026](https://arxiv.org/abs/2606.29073)). No approval dialog can substitute for the missing grant, which is what grant-backed approval enforces.

## Key Takeaways

- Execution-layer security invariants are testable runtime properties, not guidance — a runtime enforces the check in code or fails the case it covers.
- The benchmark's core finding: any single connection-layer boundary blocks only 4 of 10 modeled attacks (B1 in the table above), while all 8 invariants together (B2) block 10 and keep a complete audit.
- The mechanism is multiple, non-substitutable boundaries — ablation shows removing any one re-exposes exactly the cases it covered, so coverage is additive.
- Reach for the full runtime in multi-server, higher-risk deployments where providers expose canonical resources; a single-server low-risk setup pays complexity it may never use.
- Known limits: off-protocol actions bypass it, the guarantee needs provider cooperation, argument semantics still escape it, and the evidence is a single-author synthetic benchmark with local-only overhead numbers.

## Related

- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — the single policy-decision-point cousin; this page decomposes what that decision must guarantee
- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](revocable-resource-effect-capabilities.md) — handle-scoped capabilities and stale-replay rejection, the mechanism behind principal binding and explicit protocol state
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — capability budgets intersected through composition, a data-flow control adjacent to source-and-target authorization
- [Action-Audit Divergence: A Four-Mode Taxonomy for Runtime Hardening](action-audit-divergence-taxonomy.md) — the coverage view of deny-path audit and gate-bypass failure modes
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the principle behind metadata non-authority: runtime content informs but never authorizes
- [MCP Approval-View Fidelity Gap and Unicode Concealment](mcp-metadata-approval-view-gap.md) — the upstream question these invariants assume away: whether the reviewer even sees the metadata the model reads

---
title: "Artifact-Level Accountability Mapping for Agent Workflows"
term: "Artifact-Level Accountability Mapping"
description: "Audit an agentic coding workflow event by event against authority, execution, verification, consequence, and record, because responsibility follows the artifacts that distinguish each act."
aliases:
  - accountability artifact mapping
  - workflow accountability mapping
  - who-approved audit-log gap
tags:
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-18
maturity: emerging
---

# Artifact-Level Accountability Mapping for Agent Workflows

> Artifact-level accountability mapping audits each workflow event for authority, execution, verification, consequence, and record — the artifact schema decides whether responsibility can be traced.

Artifact-level accountability mapping is a workflow audit: walk every event an agentic coding pipeline produces, and record who held authority, who executed and under which identity, who had to verify, who bears the consequence, and which artifact carries the trace. Do it when a team enables agent authorship, agent review, or agent merge, and again whenever a provider's terms or defaults change. The framework earns its keep on events current tooling records opaquely, not on events an existing gate already documents cleanly.

## When the mapping earns its keep

The mapping pays back under three conditions. Outside them it is process for its own sake.

- A team has enabled at least one event where an agent occupies the compelled-verification cell — auto-approval under a risk threshold, agent-authored review that gates a merge, or agent-triggered deployment. Farrag documents an "Agent approval below risk threshold, Cursor" mechanism where an agent performs a compelled check ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)).
- Compliance or incident-response practice requires answering "who endorsed this change" or "under which authorization did the agent push" from stored artifacts alone. Orchestration logs commonly attribute activity to workflow identifiers and agent types rather than to specific authenticated agent instances and their human authorizers, so entries do not satisfy identity-traceability requirements such as CMMC AU.2.042 ([Kiteworks, 2026](https://www.kiteworks.com/regulatory-compliance/ai-agent-audit-trail-siem-integration/)).
- Multiple vendors are in play, and provider terms and defaults disagree on merge authority, attribution direction, and record semantics ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)).

For a single-tool team that reviews every agent PR by hand and never enables agent-side approval, the map produces the same answer at every event and buys nothing over the [enforced-versus-advisory-controls split](../security/enforced-versus-advisory-controls.md).

## The five dimensions per event

Nine workflow events carry accountability weight — task assignment, plan approval, change authorship, pull request creation, check execution, review, approval, merge, deployment ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). For each, ask five questions:

| Dimension | Question the artifact must answer |
|---|---|
| Authority | Who held permission to trigger this event? |
| Execution | Who performed it, and under which recorded identity? |
| Verification | Who checked it, and did any mechanism compel that check? |
| Consequence | Who bears outcomes per the governing terms? |
| Record | Which artifact documents the occurrence, and does its schema distinguish this event from adjacent ones? |

The mapping replaces the older enforced-or-advisory-or-absent trichotomy with a two-axis grid on the verification dimension: whether a mechanism compels the check, and who performs it ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). The cell that did not exist before is compelled verification performed by an agent, such as merge queue admission that a bot signs off or auto-approval under a risk threshold. Its output is a compelled verification with no reader present.

## Where the artifact schema loses the distinction

The gap the paper documents most sharply is at the approval event. Farrag writes: "The audit log's pull request category contains no event corresponding to an approving review specifically; approval is recorded as the submission of a review, which is the same event type as a comment or a request for changes. The distinction between endorsing a change and remarking on it is not carried by the record." ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Whether an agent endorsed a diff or merely commented is unrecoverable from the artifact alone, so no downstream policy can rebuild that distinction.

Attribution direction fares no better across vendors. Some tools record the agent as author with a human co-author; others record the human as author with an agent label ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Practitioners describe the co-author trailer as forgeable metadata that tells you little about who authorized the change, and note that a squash-and-merge sets author to Copilot in ways that disrupt blame and contribution history ([AgentLair, 2026](https://agentlair.dev/blog/co-authored-by-is-not-enough/); [GitHub community discussion](https://github.com/orgs/community/discussions/179983)). A team relying on `git log` for attribution is reading a field the provider is still deciding how to fill.

Provider progress on the trace-back sub-problem is real but partial. GitHub's Copilot coding agent now embeds an `Agent-Logs-Url` trailer that links commits back to session logs ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)). That closes the "what did the agent do" question for one vendor and does not address the "was this an endorsement or a comment" question at all.

## Why it works

Accountability is artifact-mediated: the after-the-fact question "who is responsible" can only be answered from the records the event left behind, so the artifact schema decides what questions any downstream policy can settle. Where an audit log records approval and comment as one submission event, no reviewer training or contract clause reintroduces the distinction ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Where a commit trailer names an agent but not the authorizing human, identity-traceability regimes cannot recover the authorizer from the log ([Kiteworks, 2026](https://www.kiteworks.com/regulatory-compliance/ai-agent-audit-trail-siem-integration/)). The paper's operational recommendation follows from this: distinguish the artifacts first, then let policy sit on top. GitHub's `Agent-Logs-Url` trailer is the mechanism working in the small: a distinguishable trace that made a per-commit-per-actor question answerable where it was not before ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)).

## When this backfires

Check whether the mapping adds evidence your existing records lack.

The study does not establish that any compliance regime requires artifacts at these events. It also reports no incident or dispute caused by a missing artifact ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1), §8.1).

Contracts also stay abstract on purpose. Farrag notes the coherent opposite view — event-level obligations would age faster than the products change — and does not refute it ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). And the paper is documentation-only: it reports a correspondence gap between two published layers without establishing that the gap harms anyone ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Weight it accordingly.

## Example

Farrag's documented GitHub case separates task assignment from approval: only users with write access can trigger the agent, and the requester cannot approve its pull request. Commits name the agent as author and the requester as co-author ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1), §4.1).

The audit-log schema records a review submission without distinguishing approval from comment. It includes agent and bot markers and an agent session identifier, whose meanings the paper found undocumented ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1), §4.3). The missing distinction is endorsement, not the complete absence of actor fields.

The `Agent-Logs-Url` commit trailer supplies a separate trace to session logs ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)). That trace answers a different question from whether a review approved the change.

## Key Takeaways

- Artifact-level accountability mapping walks nine workflow events and asks five questions of each — authority, execution, verification, consequence, and record — with the record dimension load-bearing.
- Its value is on events where the artifact schema loses a distinction, chiefly approval, where a review submission conflates endorsing a change with commenting on one ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)).
- The mapping earns its keep only when at least one event is agent-verified under a risk threshold, when compliance requires artifact-alone traceability, or when multi-vendor policies disagree; outside those conditions, keep the lighter [enforced-versus-advisory-controls split](../security/enforced-versus-advisory-controls.md).
- Distinguish the artifact first; downstream policy cannot rebuild a distinction the record schema does not carry. GitHub's `Agent-Logs-Url` trailer shows the mechanism working on one sub-gap and not on approval ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)).

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](../security/enforced-versus-advisory-controls.md) — the site-level split between runtime-evaluated and context-evaluated controls; this mapping picks up on the events that split does not resolve
- [Risk Architecture for AI-Native Engineering Teams](risk-architecture-ai-native-teams.md) — the organization-level ownership map for AI-native teams; artifact-level accountability is the event-level companion
- [Action-Audit Divergence: A Four-Mode Taxonomy for Runtime Hardening](../security/action-audit-divergence-taxonomy.md) — asks whether the runtime honored the log; this mapping asks whether the log's schema carries the distinctions accountability needs
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](../verification/evidence-bundled-agent-prs.md) — the producer-side artifact that widens the review gate the approval event depends on
- [Intent-Centric Engineering: Oversight Over Authorship](intent-centric-engineering.md) — the operating model that allocates accountability across humans, agents, and tools
- [Message Protocol Governance for Human-Agent Coding Teams](message-protocol-governance-human-agent-teams.md) — an attributable message record measured as an audit tool, with its false-alarm rate on honest runs

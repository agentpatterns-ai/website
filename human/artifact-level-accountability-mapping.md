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

- A team has enabled at least one event where an agent occupies the compelled-verification cell — auto-approval under a risk threshold, agent-authored review that gates a merge, or agent-triggered deployment. Farrag documents an "Agent-performed approval below risk threshold" cell producing artifacts indistinguishable from a human endorsement ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)).
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

## Where the artifact schema quietly loses the distinction

The gap the paper documents most sharply is at the approval event. Farrag writes: "The audit log's pull request category contains no event corresponding to an approving review specifically; approval is recorded as the submission of a review, which is the same event type as a comment or a request for changes. The distinction between endorsing a change and remarking on it is not carried by the record." ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Whether an agent endorsed a diff or merely commented is unrecoverable from the artifact alone, so no downstream policy can rebuild that distinction.

Attribution direction fares no better across vendors. Some tools record the agent as author with a human co-author; others record the human as author with an agent label ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Practitioners describe the co-author trailer as forgeable metadata that tells you little about who authorized the change, and note that a squash-and-merge sets author to Copilot in ways that disrupt blame and contribution history ([AgentLair, 2026](https://agentlair.dev/blog/co-authored-by-is-not-enough/); [GitHub community discussion](https://github.com/orgs/community/discussions/179983)). A team relying on `git log` for attribution is reading a field the provider is still deciding how to fill.

Provider progress on the trace-back sub-problem is real but partial. GitHub's Copilot coding agent now embeds an `Agent-Logs-Url` trailer that links commits back to session logs ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)). That closes the "what did the agent do" question for one vendor and does not address the "was this an endorsement or a comment" question at all.

## Why it works

Accountability is artifact-mediated: the after-the-fact question "who is responsible" can only be answered from the records the event left behind, so the artifact schema decides what questions any downstream policy can settle. Where an audit log records approval and comment as one submission event, no reviewer training or contract clause reintroduces the distinction ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Where a commit trailer names an agent but not the authorizing human, identity-traceability regimes cannot recover the authorizer from the log ([Kiteworks, 2026](https://www.kiteworks.com/regulatory-compliance/ai-agent-audit-trail-siem-integration/)). The paper's operational recommendation follows from this: distinguish the artifacts first, then let policy sit on top. GitHub's `Agent-Logs-Url` trailer is the mechanism working in the small: a distinguishable trace that made a per-commit-per-actor question answerable where it was not before ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)).

## When this backfires

The mapping is worse than a lighter alternative in five cases.

- Deterministic merge gates already cover the events. When branch protection, required approvals, signed commits, and a merge queue are all on and required, the answers to authority, execution, verification, and record collapse into the gate's own record for the merge event. The framework's discriminating power sits on the events those gates do not touch; if none remain uncovered, there is nothing to map.
- Agent-approval features stay off. The paper's central concern is agents occupying the compelled-verification cell. A team that reviews every agent PR by hand does not have this failure mode, and [enforced-versus-advisory-controls](../security/enforced-versus-advisory-controls.md) covers what remains.
- Small team, single identity per human, low-blast-radius repos. The dimensions produce the same answer at every event, so the map returns nothing over an informal runbook.
- A prescriptive regime already dictates the artifact list. Under SOX, HIPAA, or PCI the required artifacts are set externally, so laying a second five-dimension map on top creates two schemes to reconcile and drift between.
- Documentation-versus-practice gap. The paper reads published material and does not sample repositories. A team whose informal practice already answers each dimension via runbooks and Slack norms gains little from formalizing the gap and pays coordination cost.

Contracts also stay abstract on purpose. Farrag notes the coherent opposite view — event-level obligations would age faster than the products change — and does not refute it ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). And the paper is documentation-only: it "establishes correspondence gaps between documentation layers, not that gaps cause demonstrable harm" ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). Weight it accordingly.

## Example

A team has enabled Copilot's coding agent, allows an auto-approval routine on documentation-only pull requests, and runs branch protection with required approvals on the default branch. Apply the map to three events.

Merge. Authority sits with the required-reviewers group; execution runs under whoever clicked merge; verification is compelled by branch protection; consequence is set by the enterprise agreement; the record is the merge commit plus the branch-protection log. No gap.

Approval on an agent-authored documentation pull request. Authority sits with the auto-approval routine under its configured threshold; execution runs under the routine's identity; verification is compelled by the merge gate but performed by an agent; consequence remains with the account owner. The record is a `PullRequestReview` submission, which the audit log does not distinguish from a human's approving review or from a comment on any other pull request ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)). The gap is at the record dimension, and no downstream policy can rebuild the distinction from that artifact alone.

Change authorship on the agent-drafted commit. Authority sits with the human who requested the task; execution runs as the Copilot agent, with the requester as co-author and an `Agent-Logs-Url` trailer linking back to session logs ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)). The record now answers "what did the agent do"; GitHub closed that sub-gap. Attribution direction stays a per-vendor choice a reviewer downstream must know to read.

The map's output is a list: the approval event needs a compensating record before this pipeline can answer a compliance question about endorsement, while merge and authorship do not.

## Key Takeaways

- Artifact-level accountability mapping walks nine workflow events and asks five questions of each — authority, execution, verification, consequence, and record — with the record dimension load-bearing.
- Its value is on events where the artifact schema quietly loses a distinction, chiefly approval, where a `PullRequestReview` submission conflates endorsing a change with commenting on one ([Farrag, arXiv:2608.15678v1](https://arxiv.org/abs/2608.15678v1)).
- The mapping earns its keep only when at least one event is agent-verified under a risk threshold, when compliance requires artifact-alone traceability, or when multi-vendor policies disagree; outside those conditions, keep the lighter [enforced-versus-advisory-controls split](../security/enforced-versus-advisory-controls.md).
- Distinguish the artifact first; downstream policy cannot rebuild a distinction the record schema does not carry. GitHub's `Agent-Logs-Url` trailer shows the mechanism working on one sub-gap and not on approval ([GitHub Changelog, 2026-03-20](https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs/)).

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](../security/enforced-versus-advisory-controls.md) — the site-level split between runtime-evaluated and context-evaluated controls; this mapping picks up on the events that split does not resolve
- [Risk Architecture for AI-Native Engineering Teams](risk-architecture-ai-native-teams.md) — the organization-level ownership map for AI-native teams; artifact-level accountability is the event-level companion
- [Action-Audit Divergence: A Four-Mode Taxonomy for Runtime Hardening](../security/action-audit-divergence-taxonomy.md) — asks whether the runtime honored the log; this mapping asks whether the log's schema carries the distinctions accountability needs
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](../verification/evidence-bundled-agent-prs.md) — the producer-side artifact that widens the review gate the approval event depends on
- [Intent-Centric Engineering: Oversight Over Authorship](intent-centric-engineering.md) — the operating model that allocates accountability across humans, agents, and tools

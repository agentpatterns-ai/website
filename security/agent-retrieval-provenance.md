---
title: "Agent Retrieval Provenance as an Audit Control"
term: "Agent Retrieval Provenance"
description: "Capture which files an agent searched and read before it changed code, so a change-management auditor can test the process that produced the diff rather than infer intent from the diff alone."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - agent provenance record
  - retrieval trail as audit evidence
  - input-side agent provenance
last_reviewed: 2026-07-29
maturity: emerging
---

# Agent Retrieval Provenance as an Audit Control

> Recording which files an agent read before it changed code gives an auditor evidence about the process, not just the diff.

Agent retrieval provenance is the captured trail of what an agent searched for, found, and read before it made a change — described by [Sourcegraph](https://sourcegraph.com/blog/compliance-first-ai-proving-agent-provenance) as "the evidence of which files an agent read, and why, before it changed anything." When the author is an agent, the diff and the approval survive, but the context that informed the change disappears when the session ends.

## When this is worth doing

The strongest argument against blanket adoption comes from the source that proposes the control: "Nobody expects a list of every file a person reads," and file-level scrutiny "tends to be reserved for high-blast-radius artifacts like the Terraform applied to customer environments" ([Sourcegraph](https://sourcegraph.com/blog/compliance-first-ai-proving-agent-provenance)). Capture the trail where all of these hold:

- The change class already attracts file-level scrutiny — authentication flows, data-handling routines, infrastructure applied to customer environments, dependencies with known CVEs.
- Your tooling exposes discrete named operations (read a file, search by keyword, jump to a definition) rather than one opaque tool, so each retrieval is an individually observable event ([Sourcegraph](https://sourcegraph.com/blog/compliance-first-ai-proving-agent-provenance)).
- You can redact at source, so the trail does not become the data-protection incident it was meant to prevent.

Below that bar, the retention obligation and the privacy surface outweigh the evidentiary value.

## What the trail must contain

Retention and redaction pull in opposite directions, and the pattern that survives both keeps the metadata while dropping the content. [ARMO](https://www.armosec.io/blog/minimum-viable-audit-trail/) recommends persisting "data shape, sensitivity classifications, byte counts, semantic tags, and content hashes" so the trail "proves what happened without storing what was said." A compliance consumer also needs tamper evidence and retention set to the most stringent applicable framework — one to seven years of cold storage, on ARMO's matrix.

Access scoping belongs inside the control, not beside it: agents "can only read the repositories a user is already permitted to see" ([Sourcegraph](https://sourcegraph.com/blog/compliance-first-ai-proving-agent-provenance)). A trail showing the agent read a repository the requester could not open documents a violation instead of evidencing compliance.

## Why it works

Auditing tests the process that produced the evidence, not only the evidence itself. PCAOB [AS 1105.10](https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105) requires that when using information produced by the company as audit evidence, the auditor "Test the accuracy and completeness of the information, or test the controls over the accuracy and completeness of that information." When an agent authors the change, the process that produced it is the retrieval, so the retrieval record is the artifact a process test can examine.

The obvious substitute — asking the agent to explain itself — fails on measured grounds. Anthropic found Claude 3.7 Sonnet mentioned a decisive hint in its chain of thought 25% of the time and DeepSeek R1 39%; on the more concerning hint classes Claude was faithful 41% and R1 19%. The unfaithful chains of thought "were substantially longer than the faithful ones" ([Anthropic](https://www.anthropic.com/research/reasoning-models-dont-say-think)), so a fluent rationale evidences nothing. The harness observes a retrieval event rather than the model reporting it, so it does not inherit that unreliability.

Regulators have reached the same shape. EU AI Act [Article 12](https://artificialintelligenceact.eu/article/12/) requires high-risk systems to "technically allow for the automatic recording of events (logs) over the lifetime of the system," and for one Annex III class sets minimum logging including "the reference database against which input data has been checked by the system" and "the input data for which the search has led to a match" — retrieval-trail capture in law, though for a narrower class of system than coding agents.

## When this backfires

- Retrieval is not attention. A read event proves a file entered the context window, not that it informed the change. Accuracy "significantly degrades when models must access relevant information in the middle of long contexts" ([Liu et al.](https://arxiv.org/abs/2307.03172v3)), so bulk-loading produces a trail that overstates what was used.
- The trail cannot establish completeness. It records what was read, never what should have been read; testing that assertion needs an independently defined set of relevant sources, which the log cannot supply.
- Verbatim capture inverts the control. Storing prompt content and model output as plaintext is "a PII spill waiting to happen" ([ARMO](https://www.armosec.io/blog/minimum-viable-audit-trail/)) — the control becomes the breach.
- Attacker-controlled sources still pass. The trail records that the agent read a poisoned file; it defends nothing. Pair it with [Provenance-Aware Decision Auditing](provenance-aware-decision-auditing.md), which gates actions at runtime instead.
- Agents answering from parametric memory log nothing, so the control reports green while covering none of the change.

## Example

Sourcegraph's Deep Search is a shipped implementation. It "returns an explicit list of sources with every answer: a record of which searches it ran and which files it read to reach its conclusion," and each conversation [exports as a PDF](https://sourcegraph.com/changelog/deep-search-pdf-support) that can be handed to an auditor ([Sourcegraph](https://sourcegraph.com/blog/compliance-first-ai-proving-agent-provenance)).

What marks it as a control rather than a search feature is the question it answers. These are the auditor's questions, not a developer's:

- "Show me all commits touching the authentication service in the last audit period." — change management
- "Where is PII encrypted at rest, and when was that encryption added?" — GDPR and CCPA
- "When was MFA enforcement added to the admin login flow?" — SOC 2 and ISO 27001

It groups every commit touching the authentication service by theme, with the SHA, date, and author for each. Run against the public `gitlab-org/gitlab` repository, it traces credit card data from entry point to storage, naming the files and the fields that get hashed ([Sourcegraph](https://sourcegraph.com/blog/compliance-first-ai-proving-agent-provenance)).

The evidence is the source list, not the answer. Without it the output is a claim; with it, a reviewer can check the conclusion against the exact files consulted.

## Key Takeaways

- Agent retrieval provenance is input-side evidence — what the agent read before acting — as distinct from output-side claim grounding or a signed log of what it did.
- The mechanism is that auditing tests the process behind the evidence ([AS 1105.10](https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105)), and with an agent the process is the retrieval.
- Self-reported reasoning is not a substitute: models omit the decisive factor most of the time, and unfaithful rationales run longer than faithful ones ([Anthropic](https://www.anthropic.com/research/reasoning-models-dont-say-think)).
- Scope it to high-blast-radius changes; the source itself notes nobody audits which files a human read.
- Persist metadata and hashes rather than prompt and output text, or the audit trail becomes a PII spill ([ARMO](https://www.armosec.io/blog/minimum-viable-audit-trail/)).
- The trail evidences which context was available, not that the agent used it, and it cannot prove completeness by itself — claim only what it supports.

## Related

- [Cryptographic Governance Audit Trail](cryptographic-governance-audit-trail.md) — the action-side dual: tamper-evident signed receipts of what the agent did, where this page covers what it read.
- [Provenance-Aware Decision Auditing for LLM Agents](provenance-aware-decision-auditing.md) — runtime gating on an influence graph, rather than a post-hoc record for an auditor.
- [Generative Provenance Records for Tool-Using Agents](../verification/generative-provenance-records.md) — claim-level grounding of generated sentences, the third provenance axis.
- [Agent-Tuned Code Search: Retrieval Built for the Loop](../context-engineering/agent-tuned-code-search.md) — the scoped-retrieval tooling that makes a legible trail possible.
- [Agent Chat History as a First-Class Artifact](../observability/agent-history-as-artifact.md) — the practitioner-facing query surface over the same session record.
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md) — the wider control set this evidence artifact plugs into.

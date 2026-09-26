---
title: "Evidence-First Reports From Failure-Diagnosis Agents"
term: "Evidence-First Diagnosis Report"
description: "Engineers valued an RCA agent's retrieved log evidence even when they rejected its root cause, and a wrong verdict kept steering the search after it was dropped."
tags:
  - agent-design
  - observability
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - evidence-first RCA report
  - evidence over diagnosis
  - demoted root-cause verdict
last_reviewed: 2026-09-21
maturity: emerging
---

# Evidence-First Reports From Failure-Diagnosis Agents

> Engineers named the Evidence section one of the most valuable parts of an agent's failure-diagnosis reports, whether or not they accepted the root cause.

An evidence-first diagnosis report puts the retrieved artifacts first: the log lines, the time windows, and the metadata the agent pulled while investigating. The root-cause claim stays, below them, naming the evidence it rests on. Jansson and colleagues built reports of this shape for nightly test failures at Westermo Network Technologies and showed them to six practitioners. "The Evidence section was repeatedly identified as one of the most valuable parts because it directed attention to relevant logs before the proposed cause was accepted or rejected" ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)).

## When this applies

Three conditions carry the ordering.

- The reader can act on raw artifacts. Westermo's engineers already inspected test data and logs by hand across several sources, so retrieval was the expensive half ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)).
- Every cited artifact resolves. Participants asked for direct links to the referenced logs, and reported that "incorrect timestamps or time windows in the Evidence section could also make referenced logs difficult to locate" ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)). Evidence nobody can open is prose.
- The failure is unfamiliar. Reports "provided little value for familiar or simple failures", and were judged more useful for unfamiliar ones or for less experienced practitioners ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)).

## What goes where

The Westermo report carried Root Cause, Confidence, Evidence, Reasoning Steps, Next Steps, Assumptions and Limitations ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)). Participants said that "Less relevant sections, including Reasoning Steps, Assumptions, and Limitations, could initially be hidden" ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)).

| Section | Where it goes | Why |
|---|---|---|
| Evidence | First, with resolvable links and time windows | It directs attention before the cause is accepted or rejected |
| Root cause | Below the evidence, stated short | Useful, and the part most likely to misdirect |
| Confidence | Visible early when low or medium | The uncalibrated value was hard to interpret |
| Reasoning steps, assumptions, limitations | Collapsed | Repeated descriptions and internal tool detail were called confusing |

Demoting the cause is not deleting it. Keep the candidate, and attach the lines that support it.

## Why it works

A stated conclusion changes where the reader looks, and the effect survives their rejecting it. Bansal and colleagues measured the general form: "explanations increased the chance that humans will accept the AI's recommendation, regardless of its correctness" ([Bansal et al., 2021](https://arxiv.org/abs/2006.14779v3)). Westermo's focus group watched it narrow a live search. One participant put it as "…because it [the agent] says this looks normal, then you might not even think about looking there", and the authors' own lesson is that "incorrect but plausible conclusions could also misdirect attention and increase investigation effort" ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)).

Retrieved log lines change the cost of checking. Vasconcelos and colleagues argue that "people strategically choose whether or not to engage with an AI explanation", and across 5 studies (N=731) found that costs such as explanation difficulty move how much people overrely. They trace some null results to "the explanation not sufficiently reducing the costs of verifying the AI's prediction" ([Vasconcelos et al., 2023](https://arxiv.org/abs/2212.06823v2)). A timestamped log line can be checked against the system directly. A causal claim about why the suite went red cannot be checked from that data at all.

Ordering by verifiability beats both extremes. Le and colleagues gave 302 participants one of three framings: a recommendation with its weight of evidence, evidence with no recommendation, or evidence for and against every candidate. The third cut over-reliance against the recommendation framing (M=53.30 against M=73.86, p<0.001, r=0.45) and took the best decision accuracy (Brier 0.267 against 0.290 and 0.295) ([Le et al., 2025](https://arxiv.org/abs/2402.01292v4)).

## When this backfires

- Evidence with no candidate attached. Le's evidence-only condition carried more under-reliance than the hypothesis-driven framing, M=41.25 against M=24.42 (p<0.001, r=0.39) ([Le et al., 2025](https://arxiv.org/abs/2402.01292v4)). Strip the verdict out and readers start ignoring a signal that was often right.
- Readers who want the answer. Of 16 professional developers asked what an ideal fault-localization explanation contains, 13 named a suggested patch as the most popular feature, and 11 found the ten explanations they were shown too many ([Kang et al., 2024](https://arxiv.org/abs/2308.05487v3)).
- A meeting rather than an investigation. Westermo's participants split by context: "Root Cause could be useful in meetings, while Evidence was preferred when investigating failures in the test framework" ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)).
- Volume with no human per report. Westermo evaluated reports a practitioner sits down and reads, scoring perceived correctness, clarity, usefulness and trust ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)). Nothing in it speaks to a queue sorted before anyone reads anything.

Read the study for what it is. Six practitioners rated one fixed report per scenario and configuration, across two real failures, with no ground truth and no manual-RCA baseline ([Jansson et al., 2026](https://arxiv.org/abs/2609.21843v1)). One industrial data point about report shape.

## Key Takeaways

- Put the retrieved artifacts above the causal claim, with a link and a time window the reader can open.
- Keep the verdict, and attach evidence to each candidate rather than to the winner. Dropping it entirely carried under-reliance of M=41.25, against M=24.42 for the framing that kept candidate hypotheses.
- Collapse reasoning steps, assumptions and limitations by default; surface a low or medium confidence value early instead.
- The same study found its multi-agent configuration roughly three times slower and twice as costly with no consistent quality advantage, an argument that belongs to [Over-Orchestrated Agent Architecture](../anti-patterns/prefer-simplest-agent-architecture.md).

## Related

- [Hypothesis-Driven Debugging: Instrument Before You Patch](hypothesis-driven-debugging.md) — the agent-side loop that converges on a cause, where this page governs what it hands over afterward
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](../../verification/evidence-bundled-agent-prs.md) — the same producer-side discipline applied to a code change instead of a failure
- [Agent-Laundered Bug Reports](../anti-patterns/agent-laundered-bug-reports.md) — what happens when speculation replaces the observation instead of sitting under it
- [Trajectory Pre-Filter for Failure Diagnosis (TrajAudit)](../../observability/trajectory-prefilter-failure-diagnosis.md) — narrowing the evidence an investigator reads, one step before the report is written
- [Over-Orchestrated Agent Architecture (Prefer the Simplest That Works)](../anti-patterns/prefer-simplest-agent-architecture.md) — the topology half of the same experience report

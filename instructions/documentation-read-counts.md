---
title: "Documentation Read Counts Measure Retrievability, Not Value"
term: "Documentation Read Counts"
description: "Agent instruction files and working notes take 60.5% of documentation interactions against 1.3% for API reference, but the same corpus shows the consult-to-edit link is 0.002."
aliases:
  - documentation read counts
  - agent documentation attention traces
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-23
maturity: emerging
---

# Documentation Read Counts Measure Retrievability, Not Value

> A documentation read count measures how cheaply an agent can reach a file, not how much that file improved the outcome.

The most-read documentation artifact in a coding-agent trace is the one the agent could reach for free. Gao and Chen instrumented 557 agentic coding sessions and 33,097 agentic pull requests and found that agent instruction files and agent working notes account for 60.5% of all documentation interactions, against 1.3% for API reference ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)). Act on that distribution only after separating what it measures from what it is usually taken to mean.

## What the traces show

The corpus is behavioral rather than survey-based: 94,813 development events including 3,033 documentation interactions from SWE-chat, plus 690,260 classified file-level change records from AIDev ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)).

Agent instruction files take 35.4% of interactions and agent working notes 25.1%, so instruction files receive roughly 27 times as many interactions as API references. Agents write documentation almost as fast as they read it: production runs at 0.87 times the rate of consultation, and 41.5% of agentic pull requests change documentation. Reading is self-directed rather than remedial, at 70.2% self-initiated against 7.5% failure-driven. Documentation also trails code: among multi-commit pull requests that change both, code is touched first 4.7 times more often, though 42.6% first touch both in a single commit, "for which no order is observable" ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)).

## Why it works

Discovery cost, not information value, decides what an agent opens. The same traces show a documentation read is followed by another read with probability 0.270, while following a reference out of one document into another is entirely unattested. The authors read this as motivating "self-contained documents with locally retrievable structure, rather than assuming that agents navigate richly cross-linked documentation" ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)).

That mechanism explains the whole distribution. An agent reaches instruction files because the harness injects them or they sit at a conventional path. It reaches its own working notes because it wrote them into the tree it is already searching. It rarely reaches API reference because that content sits behind navigation it will not perform. Read frequency ranks artifacts by cost of arrival, which is why [discoverable context](../context-engineering/discoverable-vs-nondiscoverable-context.md) beats better-written context an agent never opens.

## What the read counts do not license

The paper's own null results block the obvious inference. In the raw sequence the link from consultation to code editing is unresolved: the adjacent transition probability is 0.002 and the unadjusted three-event lift 1.05, and only a stage-adjusted model puts it above unity at OR 1.33 [1.09, 1.62]. Consultation is associated with less immediate testing rather than more, at lift 0.23 and adjusted OR 0.39 [0.25, 0.60] ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)).

So the authors decline to endorse the two properties most often prescribed for agent-friendly documentation. On actionability: "Actionability may still be desirable, but these analyses provide no consistent behavioural evidence for the coupling." On verifiability: it "cannot be justified solely by appealing to the behaviour observed in this corpus" ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)).

Independent outcome measurement points the same way. Gloaguen et al. evaluated repository context files on real tasks and report that "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average" ([arXiv:2602.11988v2](https://arxiv.org/abs/2602.11988v2)). The artifact with the highest read count has the weakest outcome evidence, as [Evaluating AGENTS.md](evaluating-agents-md-context-files.md) sets out in full.

## When this backfires

Cutting API reference on the 1.3% figure is a category error when your readers are agents in other repositories. The figure describes one regime: API references "accounted for only 2.3% of observable repository-local consultations in our data" ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)). Retrieval-driven use is a different one. DocPrompting retrieves documentation at generation time and improves CodeT5 by 2.85% in pass@1, a 52% relative gain, "in execution-based evaluation on the popular Python CoNaLa benchmark" ([arXiv:2207.05987v3](https://arxiv.org/abs/2207.05987v3)). A low in-repo read count is a retrievability defect to fix, not a demand signal to obey.

Moving budget into instruction files without a minimality rule reproduces the condition Gloaguen et al. measured: unchanged success at over 20% more cost per task.

Promoting agent working notes to a governed surface can buy nothing while costing review capacity. The authors identify the problem correctly, writing that "Agent-authored documents create a new maintenance surface", but their threats to validity concede that the working-note category — 25.1% of documentation interactions, not of all development events — carries unvalidated labels, resting on "language-model classification of 500 ambiguous paths" with "no human validation of these labels" ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)). Govern the notes your team re-reads across sessions, not every plan file an agent leaves behind.

The authors also warn about both datasets separately: "SWE-chat is opt-in telemetry … and 87% of the corpus comes from a single agent family", while "AIDev comprises public repositories that adopted agents early" ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)), so a private codebase with a large internal API surface should measure its own distribution before importing this one.

## Example

Take the 41.5% of agentic pull requests that change documentation ([arXiv:2608.20195v1](https://arxiv.org/abs/2608.20195v1)). Read as a value signal, that number says documentation is nearly half of agentic delivery. Read as a cost signal, it says something narrower and more useful: writing a markdown file is among the cheapest actions an agent can take inside a pull request, and the same corpus shows code touched first 4.7 times more often among multi-commit pull requests that change both.

The figure therefore licenses a review policy, not a budget increase. The question it raises for a team is how many of those documentation changes anyone opened again, which is an inbound-read measurement the corpus cannot make for you.

## Key Takeaways

- Rank documentation by read count and you rank it by cost of arrival, because link-following never appeared in the traces at all.
- The 60.5% figure and the 0.002 consult-to-edit transition come from the same corpus, so quoting the first without the second misreports the paper.
- Fix a low API-reference read count by making the content locally retrievable before concluding that agents do not want it.
- Instruction files win on attention and lose on measured outcomes, so a reallocation toward them needs its own success metric.
- Agent-authored notes are a maintenance surface the authors name explicitly; scope any retention policy to notes that get re-read, since the category's labels are unvalidated.

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the controlled-benchmark evidence that the most-read artifact does not improve success
- [Public Rules-File Corpora as Evidence](rules-file-corpus-evidence.md) — the same measures-authorship-not-efficacy trap, applied to rules-file corpora
- [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md) — why retrievability decides what an agent reads
- [Agent Context File Evolution](agent-context-file-evolution.md) — how these files change once a team starts maintaining them
- [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) — what an ungoverned agent-facing surface becomes

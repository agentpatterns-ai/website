---
title: "Operational Context Validity for Retrieved Code"
term: "Operational Context Validity"
description: "Label each retrieved artifact valid, invalid, or unknown for one deployment at one point in time, because similarity and recency do not show that code still applies."
aliases:
  - runtime-aware context
  - deployment-aware retrieval
  - applicability labeling
tags:
  - context-engineering
  - rag
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-31
maturity: emerging
---

# Operational Context Validity for Retrieved Code

> Operational context validity labels each retrieved artifact valid, invalid, or unknown for one deployment at one point in time.

A retrieval score says an artifact matches the task. It does not say the artifact describes code that runs in your deployment. [Assunção and Periyathambi (2026)](https://arxiv.org/abs/2610.38800v1) name the missing check "operational context validity". It asks "whether a retrieved software artifact can legitimately guide an implementation decision" for a particular deployment and point in time. Their pilot is small and synthetic. The principle is the contribution.

## Three ways relevant code is wrong

The paper names feature flags, architectural migrations, and deployment-specific configuration as the sources of invalid-but-relevant context ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)). A flag-guarded implementation can look right while its flag is off. A migrated service leaves the old endpoint's code, tests, and pull requests in the index.

Neither a similarity score nor a commit date separates these cases. The authors call a commit date "only a clue": a new commit can target a disabled flag ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

Validity also differs between deployments at the same moment. The same old REST endpoint can be invalid for one deployment and valid for another after a regional rollback. So deleting outdated-looking artifacts everywhere, or telling a model to prefer newer files, does not implement the check ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

## How the labels work

The paper's reference system, CASE, scores each candidate artifact against timestamped evidence from deployment manifests, flag configurations, service routing, and migration records. The label follows the evidence:

| Label | Condition |
|---|---|
| valid | The evidence supports the artifact's applicability conditions for the deployment. |
| invalid | The evidence supports the negation of those conditions. |
| unknown | Evidence is missing or contradictory. |

A missing runtime trace does not make an artifact invalid, because the gap may come from sampling or observability limits. Each assertion records its source, timestamp, scope, and open conflicts ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

An invalid artifact is not thrown away. CASE sorts its output into three groups. "Act On" holds valid artifacts. "Verify" holds unknown ones, and the paper says unknowns "may trigger a question or additional retrieval". "Explain" holds invalid artifacts as labeled historical rationale. A migration pull request that is invalid for the current path still explains why the path changed ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

## What the pilot measured

The pilot used one illustrative Java application with a REST and a GraphQL implementation of a merchant trust score. It covered 6 tasks, 15 artifacts, and 3 deployments. BM25 produced the top 8 candidates per task, and every condition used a budget of about 1,500 tokens ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

| Condition | Valid precision | Valid recall | Incompatible artifacts shown as actionable |
|---|---|---|---|
| Semantic only | 0.50 | 1.00 | 16 |
| Recency filtered (180 days) | 0.43 | 0.43 | 6 |
| Semantic plus raw configuration | 0.50 | 1.00 | 16 |
| CASE | 1.00 | 1.00 | 0 |
| CASE without flag evidence | 0.33 | 0.13 | 0 |

Semantic retrieval found every applicable artifact yet showed incompatible ones as actionable, so recall hid the defect. Recency filtering cut incompatible artifacts from 16 to 6 and lost valid ones too. After the European deployment rolled back to REST, all four artifacts the recency filter kept for that task were incompatible. Appending raw configuration to the retrieved set changed nothing. The gain came from classifying the evidence, not from having it in the prompt ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

## When this backfires

- The evidence does not exist in a form you can query. The pilot's graph came from configuration exports, service inventories, pull request metadata, and "a limited set of developer-verified mappings". Without those inputs every artifact is unknown.
- You run one deployment and no migrations. The authors expect "little or no gain" for stable, single-configuration components.
- Flags depend on cohorts or live rollouts. The paper says a global on/off assumption is insufficient, so a static flag export gives a wrong label for a partial rollout.
- You treat the numbers as effect sizes. The authors curated the fixture by hand, and the reference labels follow CASE's own evaluator rules. The perfect scores "should not be interpreted as evidence of generalization".
- You expect better patches. The pilot measured context selection, not agent decisions or generated code. The authors call for larger studies with independent ground truth ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

## Example

The pilot application has three deployments. The US deployment migrated to GraphQL. The European deployment later rolled back to REST. The Asia-Pacific deployment has a partly enabled GraphQL configuration with unresolved cohort information.

Take one request against a fixed repository snapshot. For us-prod, CASE moves its actionable context to the GraphQL implementation. For eu-prod, it moves it to the REST implementation. The paper does not report the Asia-Pacific outcome ([Assunção and Periyathambi 2026](https://arxiv.org/abs/2610.38800v1)).

## Key Takeaways

- Add a validity label next to the relevance score. A retrieved artifact needs a status for the target deployment, not only a rank.
- Keep an unknown state. Missing evidence is not a negative, and unknown artifacts go to a question or a second lookup.
- Route invalid artifacts to an explanatory section instead of deleting them. They carry the reason the code changed.
- Do not gate on recall alone. In the pilot, semantic retrieval scored recall 1.00 with a valid precision of 0.50. Precision and recall are task-level means, while the incompatible count (16) is a total of artifact occurrences, and five more occurrences were unknown. So on average about half the actionable artifacts were applicable.
- Treat the pilot as a feasibility test: 6 synthetic tasks, hand-curated labels, no patch-correctness measure.

## Related

- [Fact Supersession Memory for Code Assistants](fact-supersession-memory.md) — retires a stored value when one replaces it; this page covers the case where two implementations stay true in different deployments.
- [Claim-Scoped Invalidation for Agent Memory](claim-scoped-invalidation.md) — decides per stored claim whether a commit falsified it, where this page decides per retrieved artifact for a deployment.
- [Environment Specification as Context](environment-specification-as-context.md) — supplies the deployment facts that validity labels depend on.
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the relevance-ranked retrieval that this check sits behind.
- [Scope-Matched Memory Retrieval](../patterns/agent-design/scope-matched-memory-retrieval.md) — matches retrieved memory to the scope of the task, a nearby filter on a different axis.

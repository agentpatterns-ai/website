---
title: "Underspecified Research Queries and Prior Substitution"
term: "Prior Substitution"
description: "Scope and terminology are the expensive omissions in a deep research query. Coverage of your question tends to fall while citation precision shows no significant change."
tags:
  - agent-design
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - query underspecification in deep research
  - underspecified deep research queries
  - prior substitution
last_reviewed: 2026-11-01
maturity: emerging
---

# Underspecified Research Queries and Prior Substitution

> Omit scope or terminology and a deep research agent fills the gap from training. Coverage tends to fall; citation precision shows no significant change.

Prior substitution is what a deep research agent does with a gap in your query. It fills the missing scope or terminology from its training distribution and proceeds. Under fully underspecified queries, rubric coverage of the original question fell by 25.8% to 64.8% relative across three agents and three benchmarks. The authors detected no statistically significant change in citation precision in any of the eight settings where it was measured ([Wen et al., arXiv:2610.39413v1](https://arxiv.org/abs/2610.39413v1)). The cited documents still support the report's claims. The report loses alignment with the information need you started from.

## Which omissions cost most

The authors coded 176 initial-final query pairs from real researchers' sessions. Three omission types "cover 94% of the 176 pairs": scope was missing in 45%, terminology in 37%, preferences in 33%. The effects below are paired changes in rubric-based coverage. Both answers are scored against the complete query ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)).

| Omitted | Examples | Measured effect |
|---|---|---|
| Scope | Time period, place, population, domain | Substantial mean reductions, significant across most agents and benchmarks |
| Terminology | The precise technical term or named entity | Same, plus "a pronounced effect on search strategy" |
| Preferences | Evaluation criteria, comparison requirements, output format | Smaller reductions, "often not statistically significant" |

Spend the effort on the first two: "users should state key scope constraints and use precise technical terminology, as omitting or obscuring this information can substantially affect the search process and degrade the final answer quality" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). Preferences are the cheaper omission, not a free one. That variant still came out significant in four of the nine agent-benchmark cells ([2610.39413v1](https://arxiv.org/abs/2610.39413v1), Table 3).

## Why it works

Your words are what the agent's later searches get built from. Token-provenance analysis traces every search-query token to the user query, earlier searches, retrieved documents, or none of those. Under underspecification, "the share of search-query tokens traceable to the user query decreases significantly, while the share of untraced tokens increases significantly in most cases" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). The paper attributes untraced tokens to parametric knowledge or memory. The trajectory shape moves with it. The most underspecified variant produced "more Exploration and fewer Specialization transitions across all three DRAs". The run switches between facets of a topic instead of narrowing within one.

Retrieval widens without getting more useful. Document novelty rose significantly under full underspecification for all three agents. Yet "the context-driven term adoption rate does not increase correspondingly, and even dropped significantly for DR Tulu and Tongyi under the most underspecified conditions" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). The agent then cites documents that support the claims it chose to make, so the citation layer shows no significant change. A stable citation score does not mean a good answer. Mean citation precision under the fully underspecified variant and on the paired complete queries ([2610.39413v1](https://arxiv.org/abs/2610.39413v1), Table 6):

| Agent | Fully underspecified | Complete |
|---|---|---|
| DR Tulu-8B | 50.90% | 50.45% |
| GPT-5.4 with tools | 68.79% | 70.93% |

The means differ, but the paper reports the changes as not significant. Only these two agents were measured for citations, on two of the three benchmarks, because Tongyi-DR emits none.

## The agent will not flag the gap

Proceeding without recognizing the omission was the most frequent behavior on every agent tested. On fully underspecified ResearchQA queries, the agent asked for clarification in 18.1% of GPT-5.4-with-tools runs. DR Tulu-8B asked in 0.2% of runs and Tongyi-DR in 1.2% ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). Clarification behavior you have watched on one harness says nothing about the next.

Runs where the agent stated assumptions did worse than runs where it never noticed the gap. "Assume runs exhibit larger answer-quality losses than Unaware runs in three of the four conditions" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). The authors classified these behaviors after the runs and tested no assumption prompt. They offer a hypothesis rather than a cause: recognized ambiguity may mark the cases where intent was most uncertain. A stated assumption is not evidence the run went well.

## Example

Three ResearchQA queries from the paper's appendix show the range. The same judge scored each complete-query and underspecified-query answer against the original query's rubrics ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)).

The first pair removes scope from one query (the paper's example E.1):

- Complete: "What are the main clinical advantages and safety considerations of using nebulized tranexamic acid to manage post-tonsillectomy bleeding?"
- Underspecified: the same query without "post-tonsillectomy", so it ends "to manage bleeding?"

The complete query scored 0.8333. "After the surgical context is removed, the answer shifts toward hemoptysis and pulmonary hemorrhage", and the score falls to 0.4167. A question about trapping-net formation in *Duddingtonia flagrans* scored 0.7500. "Replacing the species name with 'a fungus' leads the answer to consider multiple interpretations." The appendix concludes: "Its focus thus broadens beyond the species specified in the original query, and rubric coverage falls from 0.7500 to 0.2500" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1), Appendix E).

The counter-case is in the same appendix. A methotrexate question kept a score of 1.0000 with its severity qualifier removed. The answer covered the intended context anyway. The authors state the limit themselves: "omission of scope information does not necessarily cause a loss in rubric coverage when the answer still addresses the intended context".

## When this backfires

- You may not have the vocabulary. The paper concedes the trap: "users may need sufficient domain knowledge to identify relevant constraints and terminology before agents can effectively address their needs" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). The advice is least available to the reader who most needs the agent.
- Read as "state everything", the advice reverses. A counter-finding: "simply specifying all requirements does not consistently help, as models have limited instruction-following ability and requirements can conflict" ([What Prompts Don't Say, arXiv:2505.13360v3](https://arxiv.org/abs/2505.13360v3)). Selecting which requirements to state beat stating all of them, as [request shaping](../../token-engineering/request-shaping-wasted-turns.md) records.
- Do not carry this into coding work. The measurements are three deep research agents writing long-form cited reports, graded by Gemini 3.1 Pro against each benchmark's official protocol ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). A coding agent has a test suite, the observable signal a report lacks, so [interactive clarification](interactive-clarification-underspecified-tasks.md) is the better guide there.
- Hosted products are out of scope. "We do not evaluate closed-source deep research systems that do not expose these trajectories" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)), so the clarification rates do not describe a product you cannot instrument.
- The agent-side fix competes with this one. Training an agent to clarify intent before the long-horizon run improves downstream task performance and beat closed-source agents' built-in clarify modules ([IntentRL, arXiv:2602.03468v1](https://arxiv.org/abs/2602.03468v1)). If your harness clarifies well, user-side discipline is partly redundant.

## Key Takeaways

- Write the scope and the precise term into the query before dispatching a long research run; those are the omissions with measured cost.
- Review the report against the question you asked. Auditing whether cited documents support their claims shows no significant change between the two arms. That check carries no signal about this failure.
- When the agent does state an assumption, treat it as the moment to check the omission rather than as reassurance. Those runs lost more coverage than runs that never noticed, in three of the four underspecification conditions.
- On the same fully underspecified ResearchQA queries, clarification rates ranged from 0.2% to 18.1% across the three agents. Do not port one harness's behavior to another.
- Capability does not substitute. The two deep-research-trained agents outperformed GPT-5.4 with tools on complete queries. The authors read this as agents that "appear to depend more heavily on users fully specifying their information needs" ([2610.39413v1](https://arxiv.org/abs/2610.39413v1)). It holds on two of the three benchmarks. Three agents make it an observation, not a trend.

## Related

- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md) — the agent-asks half, measured on software issues where the outcome is verifiable
- [Prompted Uncertainty Decomposition for Clarification Routing](prompted-uncertainty-decomposition-clarification.md) — how an agent decides whether a gap needs the user or more search
- [Assumption Propagation](../anti-patterns/assumption-propagation.md) — what happens downstream when the substituted assumption lands in code
- [Request Shaping to Cut Wasted Agent Turns](../../token-engineering/request-shaping-wasted-turns.md) — the cost side of specificity, and why selection beats volume
- [Grill Me: Developer-Initiated Plan Interrogation](grill-me-technique.md) — forcing the interrogation yourself when the agent will not ask

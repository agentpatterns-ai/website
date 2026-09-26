---
title: "Auditing Agent Tool Chains for Silent Partial Success"
term: "Tool-Chain Silent Failure Audit"
description: "A successful tool call is not evidence of complete retrieval. Diff each tool's richest surface against its API and its wrapper before trusting an answer."
aliases:
  - silent partial success
  - agent-tool silent failure audit
  - failure locus audit
tags:
  - testing-verification
  - tool-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-24
maturity: emerging
---

# Auditing Agent Tool Chains for Silent Partial Success

> A tool call can return success with most of the answer missing, and nothing in the response says so.

Audit a tool integration for silent partial success when two conditions hold together. The tool exposes a richer surface than the one your agent calls, such as a web interface or a documented API the wrapper only partly covers. And a downstream claim depends on having retrieved everything. Where both hold, compare the surfaces and record what each layer drops. An audit of 15 scientific tools inside ToolUniverse validated 91 such failures, defining one as an interaction where "(1) the tool invocation appears successful, (2) the returned information is incomplete, transformed, ambiguous, or otherwise insufficient for the intended task, and (3) the limitation is not adequately disclosed to the downstream user or agent" ([Gopalan et al., arXiv:2609.26836v1](https://arxiv.org/abs/2609.26836v1)).

## Where to look

The audit names seven points in the chain from the resource to the agent. Four of them are differentials, so each needs a reference surface to compare against. The API is missing a capability the tool has, the API covers it only partly, no wrapper exposes it, or the wrapper "partially omits parameters, fields, or formats which the API returns" ([§1](https://arxiv.org/abs/2609.26836v1)). The other three sit outside that comparison: an inherent limit in the resource, an output the agent cannot use, and an output the agent misreads.

Of the 91 validated failures, 51 sat at the API layer and 25 at the wrapper layer. The authors could not place three, and put the other 12 outside those two layers. The agent usability point accounted for no confirmed failures in any of the 15 tools, and the authors write that "Failures at the agent-level loci were comparatively uncommon in this analysis" ([§3](https://arxiv.org/abs/2609.26836v1)). Read that as a pointer, not a proportion. The limitations section says "the candidate generation may influence the proportion of failures observed and hence proportion of failures are not to be considered as representative of typical silent failures in agent-tool interaction" ([§6](https://arxiv.org/abs/2609.26836v1)).

Completeness was the most affected dimension, 28 of the 134 occurrences the 91 cases produced, and missing data or fields the most common issue type at 38 ([§3](https://arxiv.org/abs/2609.26836v1)). The recurring shapes are mundane. EMDB caps its `rows` parameter at 1000 "despite the database containing substantially more records". BiGG search results are "silently capped with no documented page size", and its documentation "reports API v1.3.0 while live responses report v1.6.0". The ClinicalTrials.gov wrapper "returns a success status with empty outcomes" where the web interface shows an explicit no-results state ([§4, §5](https://arxiv.org/abs/2609.26836v1)).

## Running it

Candidates came from documentation, not from traffic. The authors assembled each tool's docs, web interface detail, API docs, manuals, release notes, and reported issues, then looked for "conflicts, contract disagreements, implementation issues, and Web/API/wrapper inconsistencies" ([§2](https://arxiv.org/abs/2609.26836v1)).

The test-design rule is the part worth copying. Each query named a concrete identifier, asked the agent to report what came back, and never asked it to grade itself: "Queries were designed to test the target failure rather than ask the agent to independently determine whether a failure existed" ([§2](https://arxiv.org/abs/2609.26836v1)). An agent asked whether its own output is complete answers from the same truncated payload that caused the problem.

## Why it works

A response carries no field for what was not returned. A complete payload and a truncated one are the same object with different contents, so the agent has nothing to condition on. The paper's illustration is an API that "returns its first 1,000 records (out of 10000 records)" while the agent reports the records ([§1](https://arxiv.org/abs/2609.26836v1)). The cost arrives one layer later, in what the authors call silent amplification: "An upstream limitation that is relatively benign at the tool or API layer can become a more consequential error when the agent interprets the partial output as complete evidence" ([§1](https://arxiv.org/abs/2609.26836v1)). That is why task-success benchmarks miss this class. They score the answer, and the answer is well formed.

Auditing the chain works because it tests the one property the response schema never carries, which the authors call contextual reliability, "the extent to which an Agent–Tool interaction preserves and communicates the information, qualifiers, provenance, scope, and meaning required to support the intended scientific conclusion" ([§5](https://arxiv.org/abs/2609.26836v1)).

## When this backfires

- No richer surface exists. An internal service your own team wraps has nothing to compare against. The four differential checks return nothing, and you are left with the three that need runtime evidence.
- Completeness is not load-bearing. An agent drafting prose or triaging a queue can lose a field at no cost.
- The tool ships weekly. An audit is a snapshot of a documentation state, and the authors concede "The APIs, wrappers, interfaces, and data evolve, so individual observations may change with tool versions" ([§6](https://arxiv.org/abs/2609.26836v1)).
- The failure leaves no documentary trace. Candidate discovery reads documentation, so undocumented behavior is invisible to it. A synthesis of 27 papers keeps tool invocation and parameter-level errors as its own top-level failure cluster ([arXiv:2607.05775v1](https://arxiv.org/abs/2607.05775v1)), and this method found almost nothing at the agent.
- Location may be the wrong axis. An eight-week study of one production runtime cuts silent failures by mechanism instead, reporting that "the longest-lived failures lived in the seams between components", where no test runs by construction. In a system "defended by 4,286 unit tests and 827 declarative governance checks", it found that "roughly 70% of silent failures were ultimately caught by human user-view observation of system output, not by unit tests, health checks, or governance audits" ([Wu, arXiv:2606.14589v1](https://arxiv.org/abs/2606.14589v1)). If your defenses are already mechanism-shaped, a map of the chain adds vocabulary rather than a fix.

## Key Takeaways

- Treat a successful tool call as evidence the call ran, and nothing more. Completeness is not a field in the response, so the agent cannot check it.
- Pick the tools to audit by whether they expose more than your wrapper reaches, and by whether a missing field would change the answer.
- Write test queries that name a concrete identifier and ask what came back, then check the answer against the richer surface yourself. Asking the agent to judge its own completeness reads the same short payload twice.
- The 51-to-25 API-to-wrapper split is an observation from one environment, not a prior. The authors say so themselves.
- Expect result caps, undocumented page sizes, a success status returned over an empty result, and a documented API version that disagrees with the live one. Those four shapes cover the audited examples.

## Related

- [Silent-Failure Mechanism Taxonomy in Production Agent Runtimes](../patterns/anti-patterns/silent-failure-mechanism-taxonomy.md) — the competing cut of the same problem, by mechanism rather than by location, drawn from incidents rather than documentation
- [Data Fidelity Guardrails](data-fidelity-guardrails.md) — the complementary case, where the tool returned the right data and the agent altered it on the way out
- [Graceful Tool Output Truncation](../tool-engineering/graceful-tool-output-truncation.md) — the wrapper-side fix for one point in the chain, a partial marker and a continuation handle instead of a quiet cut
- [LLM API Fault Injection at the HTTP Layer (AgentChaos)](llm-api-fault-injection-http-layer.md) — injecting the faults deliberately, and the finding that truncation is the one diagnosis misses
- [OpenAPI Documentation Smells](../tool-engineering/openapi-documentation-smells.md) — the taxonomy of gaps between a valid specification and an agent-consumable one, which is where the comparison starts

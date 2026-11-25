---
title: "Non-REST APIs and Coding Agents: Discovery Decides Success"
description: "In Microsoft tests, coding agents used POST-only and RPC-style APIs as well as REST when the docs were in reach. Without docs, RPC success fell to zero, so fix discovery first."
tags:
  - agent-design
  - tool-engineering
  - tool-agnostic
aliases:
  - non-REST APIs for agents
  - RPC-style APIs and coding agents
  - agent API discovery
last_reviewed: 2026-11-24
maturity: emerging
---

# Non-REST APIs and Coding Agents: Discovery Decides Success

> In Microsoft's tests, agents struggled with non-REST APIs only without the docs; given an API description, REST and RPC scored the same.

The condition comes first. In one 1,356-run study, agents given an OpenAPI description, or a README link to a reference page, used POST-only and RPC-style APIs as reliably and as cheaply as REST. Agents given only a base URL could not guess verb-named endpoints, and completed none of the RPC tasks. So the work for a non-REST API is getting its description to the agent. Restyling the API, or wrapping it in a REST-shaped tool, is the fallback.

## The evidence

Waldek Mastykarz at Microsoft built a fictional inventory API, Binstock, so no model could have memorized it. They served it in three styles with identical data and behavior: REST (`PATCH /bins/B-103`), POST-only (`POST /bins/B-103/update`), and RPC (`POST /updateBin?code=B-103`). POST-only separates the HTTP methods from the naming. Prompts described outcomes ("Bin B-103 has been taken out of service") rather than operations, and a grader compared the final API state with the seed data plus the intended change ([Microsoft for Developers](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).

The result splits on one variable, whether the agent could read the API description:

| Condition | REST | POST-only | RPC |
|---|---:|---:|---:|
| OpenAPI description in the prompt, 4 models, 900 runs | 100% | 100% | 99.7% |
| Base URL only, Claude Sonnet 5.5 | 93% | 40% | 0% |
| Base URL only, GPT-6.1 Terra | 97% | 60% | 0% |

With the description, token use was about 70k per run in every style, and the single RPC failure was a 10-minute timeout. RPC had about 5 points fewer runs without a failed call, a gap the authors call not significant. Two smaller models, Claude Haiku 5.5 and MAI Code 2 Flash, "completed every task in every style, with token use within about 3% across styles" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).

Without the description, "No model ever guessed an endpoint like `/updateBin`. On the RPC API, agents averaged about 28 failed calls and then gave up." POST-only landed in between because its reads use the same paths as REST, while writes that needed `/update` or `/delete` endpoints failed. Per correct result, REST cost about 80k tokens and POST-only about 230k. RPC never produced one ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).

A third run, the handover run, embedded the API calls in a larger task: fix a failing unit test, apply inventory events, write a report. The README linked to a prose reference page. Across 96 runs, "Every run succeeded, and every run found the reference page through the README link and used it correctly" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).

## What to do with a non-REST API

Start with the smallest change.

1. Put the description where the agent will find it. "Link an OpenAPI description from your docs and your README" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)). The handover run shows a README link is enough for an agent to find a prose reference. See [OpenAPI documentation smells](../../tool-engineering/openapi-documentation-smells.md) for what makes a description usable once found.
2. Make the API describe itself. List operations at the root URL or in the body of a 404. The authors propose this and say plainly "We haven't tested that yet" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)). [RFC 9457 error responses](../../tool-engineering/rfc9457-machine-readable-errors.md) apply the same idea to errors: the response tells a failed caller what to do next.
3. Wrap the API in typed tools only when the agent cannot be given the description, or when the surface is too large to read. Generating those tools from the spec keeps them in sync ([OpenAPI as the source of truth for tool definitions](../../standards/openapi-agent-tool-spec.md)).

The authors' advice on the API itself is short: "If you maintain a non-REST API, you can leave its style as it is" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).

## Test usage and discovery separately

An eval that gives the agent the docs measures usage. An eval that leaves them out measures discovery, and discovery favors REST by design. The authors frame it as a choice to make on purpose: "decide whether you're testing how well they use it or how well they find their way around it" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)). A no-docs eval that shows RPC at 0% is a finding about your docs path, not about RPC.

Two design choices from the study carry over to any API eval:

- Phrase tasks as outcomes. A prompt that names the operation, like "update" or "delete", "hands the agent the name of the matching RPC endpoint" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).
- Grade the final state, not the call sequence, so any valid route to the right result passes. The study served each style from a Dev Proxy mock that returned 404 for any undefined path or method, so every wrong guess showed up in the proxy log ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)). [AX evals](../../verification/ax-evals-agent-facing-surface.md) covers the harness side.

## Why it works

REST endpoints are guessable. The URL follows from the resource and the HTTP method follows from the intent, so an agent with no docs gets close and lets 404s steer it the rest of the way. Microsoft states the mechanism directly: "agents can guess REST URLs from convention and have no way to guess what a non-REST API calls its endpoints" ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)). Once a description is in context, the agent reads endpoint names instead of guessing them, and the style advantage disappears.

Earlier work on API calling points at the same lever. The Gorilla authors trace API-call failures partly to models' "tendency to hallucinate the wrong usage of an API call," and report that pairing their model with a document retriever lets it "adapt to test-time document changes" ([Patil et al., arXiv 2305.15334v1](https://arxiv.org/abs/2305.15334v1)).

## When this backfires

The "leave the style alone" advice rests on one small API, one harness, and short tasks. It is weaker in these cases:

- The agent cannot reach the docs. It starts with only a base URL, or never sees a link to the description. This is the condition that took RPC to 0%. A REST API degrades better here, because convention still got agents to 93% and 97% on REST.
- The RPC surface is large. The authors kept Binstock "deliberately small and simple" and list a hundred-endpoint API with near-identical names such as `updateBin` and `updateBinItems` as untested, along with auth, pagination, and workflows of dozens of dependent calls.
- The API is GraphQL. The Microsoft study did not test it, and the task differs: the agent builds a query against a schema rather than picking an endpoint. In a GraphQL generator by Ganesan et al., accuracy on IBM Granite20B-Code rose from 62.79% with a fixed one-shot prompt to 88.00% with five relevant examples and a commented schema. The authors note that models "often hallucinate on the column and tables names" ([IJCAI 2024](https://ijcai.org/proceedings/2024/1002)). The authors observe that "adding comments to server generated schema improves accuracy." The same authors also warn against dumping a very large schema into the prompt, and their pipeline's Schema Simplification module uses string parsing to remove unnecessary information from the schema.
- The evidence is one self-run study in one harness, the GitHub Copilot SDK in Vally. The authors suggest repeating it in other harnesses. This page found no independent replication.

## Example

The partial update from the study, in each style, and what an agent without docs can do with it:

```http
# REST: guessable from convention
PATCH /bins/B-103

# POST-only: reads guessable, this write is not
POST /bins/B-103/update

# RPC: not guessable at all
POST /updateBin?code=B-103
```

The fix the authors recommend is a README line that points at the description:

```markdown
## API

OpenAPI description: openapi.yaml (also served at /openapi.yaml)
```

In the handover run, a README link to the reference page was enough for all 96 runs to find and use it ([Microsoft](https://developer.microsoft.com/blog/do-ai-coding-agents-struggle-with-non-rest-apis)).

## Key Takeaways

- With an OpenAPI description in reach, REST, POST-only, and RPC scored 100%, 100%, and 99.7% across 900 runs at about the same token cost.
- With only a base URL, RPC fell to 0% for both models tested, and agents averaged about 28 failed calls before giving up.
- The fix for a non-REST API is a discovery path: a README link to the description first, a self-describing API second, typed tool wrappers last.
- Evals that leave docs out measure discovery, which favors REST by design. Say which one you are testing.
- GraphQL, large RPC surfaces, and long workflows are untested here, and in one GraphQL generator, five relevant examples plus schema comments raised accuracy from 62.79% to 88.00% over a fixed one-shot prompt.

## Related

- [OpenAPI Documentation Smells for Agent-Ready APIs](../../tool-engineering/openapi-documentation-smells.md) — what makes an API description usable once the agent finds it.
- [OpenAPI as the Source of Truth for Agent Tool Definitions](../../standards/openapi-agent-tool-spec.md) — generating typed tool wrappers from the spec, the fallback for agents that cannot read docs.
- [Machine-Readable Error Responses for AI Agents (RFC 9457)](../../tool-engineering/rfc9457-machine-readable-errors.md) — errors that tell a failed caller what to do, the same idea as a self-describing 404.
- [AX Evals: Measure the Agent-Facing Surface, Not the Model](../../verification/ax-evals-agent-facing-surface.md) — evaluating the API, docs, and tools an agent touches, which is what this study varied.
- [Rewriting a CLI Into a JSON Payload for Agents](../anti-patterns/cli-json-payload-rewrite.md) — a sibling Microsoft measurement where the plausible interface change also did not survive testing.

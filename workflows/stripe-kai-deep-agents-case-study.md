---
title: "Stripe Kai Case Study: A Knowledge Agent on Deep Agents"
description: "How Stripe built its Kai knowledge agent on the Deep Agents harness: four layers, reused middleware, skill-gated tools, and what the one-week claim leaves out."
tags:
  - workflows
  - agent-design
  - tool-agnostic
  - harness-engineering
  - skills
aliases:
  - Stripe Knowledge AI Platform
  - Stripe Kai knowledge agent
last_reviewed: 2026-11-19
maturity: emerging
---

# Stripe Kai Case Study: A Knowledge Agent on Deep Agents

> LangChain reports one engineer built the first version of Stripe's Kai agent in a week, on Deep Agents and existing Python platform support.

Kai is Stripe's company-wide agent for knowledge work, and 83% of Stripe uses it weekly ([Stripe, 30 July 2026](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)). LangChain's case study says "Anupam built Kai’s initial version in one week" on its open-source Deep Agents harness ([LangChain, 3 August 2026](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). The week covers an initial version. It sits on top of Python platform support Stripe had already built, and Stripe's own engineering post does not mention it.

## Two accounts of one build

The vendor and the customer stress different things. [LangChain's](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents) is a vendor case study that closes by pointing readers at the Deep Agents docs. [Stripe's](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform) is a first-party engineering post by Anna Mason, Sharadh Krishnamurthy, and Anupam Upadhyay.

| Claim | LangChain case study | Stripe engineering post |
|---|---|---|
| Built in one week | Yes, the initial version, by one engineer | Not mentioned |
| Built on Deep Agents | Yes | Yes, the agent harness is "built using LangChain’s deepagents" |
| Architecture | Four layers, Deep Agents at the base | Three layers: APIs, Agent Studio, execution environments |
| Weekly use | "83% of Stripe uses Kai every week" | "83% are weekly active users" |
| Skill selection at 1,000+ skills | "The team is now building a hybrid selection system" | Solved "by utilizing a hybrid RAG/LLM approach", details in a follow-up post |

The last row conflicts. Stripe's post, dated four days earlier, describes hybrid selection as solved, and LangChain's describes it as in progress. Neither post says what the week left out of scope, so this page does not list cuts.

## The problem Kai replaced

Before Kai, Stripe had two AI options for knowledge work, and each hit a limit ([Stripe](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)). A no-code agent builder produced over 4,000 agents, and Stripe found "the proliferation of these micro-agents increasingly hard to monitor and maintain." Coding agents worked for some users, but "security concerns quickly emerged, along with a new support burden for code quality teams that had never supported non-engineers before."

Stripe's answer was one platform on which domain owners "build and govern their own Kai agents."

## Four implementation layers

LangChain lists four layers ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). Stripe's three layers cover the same ground: Agent Studio matches the configuration layer, the surface APIs match the UI, and the execution environment holds the harness.

### Layer 1: The open-source harness as the base

The base layer "handles all LLM interaction primitives, including request management, agent execution, and middleware composition" ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). The Deep Agents docs call it "the same core tool calling loop as other agent frameworks", with built-in capabilities on top ([Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)). Krishnamurthy, Engineering Manager for the Agent Foundation team, states the split: "The Deep Agents layer solves all the non-Stripey problems, so that we can focus on solving the Stripey agent problems."

### Layer 2: The Stripe-specific harness

This layer wires Kai into Stripe's security posture and internal services. [LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents) names three pieces of Deep Agents middleware behind the first version's speed:

- Filesystem. "Stripe built a virtual filesystem backed by S3 so that agents can read, write, and reference files as context across turns."
- Sandbox. "The sandbox is exposed to the agent as a tool, not as the execution environment for the agent itself." The agent runs outside the sandbox and calls into it.
- Summarization. It manages context "across long-running, multi-turn sessions where accumulated context would otherwise degrade performance or hit model limits."

Stripe's post adds the runtime. The harness "runs on Kubernetes with a secure per-session sandbox and a multi-tenant virtual filesystem", and one session reached 932 turns ([Stripe](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)). Stripe shares the harness, sandbox, and access control framework with its product-facing agents.

### Layer 3: Configuration and skills

Teams configure custom Kai agents "without touching the underlying harness" ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). Skills carry the domain knowledge. Individual teams own and maintain their own skills, and the user's profile and Kai agent decide which tiered skills load.

Skills also decide which tools load. With 500+ internal MCP tools, the skills' `allowedTools` lists create "a two-pass system where skill selection gates tool context, rather than loading all tools upfront." Some foundational skills are pinned, so they stay loaded whatever the model chooses.

### Layer 4: Surfaces

Kai ships with a web app and a Slack integration, and most employees use the web app. Stripe treats the API underneath as the product: "The agent is a service, not an application, and surfaces are simply customized views into it" ([Stripe](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)). Internal tools embed Kai through that API.

## What the week rested on

The LangChain post that gives the week also gives its precondition. "Adopting a Python-native stack meant rebuilding Stripe's internal service scaffolding around a new language, which was a large investment." The post frames the week as the payoff: "the time spent building internal Stripe support for Python was paid back immediately."

A team without service support in the harness's language starts further back than Stripe did, and the one-week figure does not count that work.

## Triggers and constraints

Kai runs on demand. A user starts a session and works through chat. The artifacts Kai produces "live alongside the conversation" and change as the chat goes on ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). Stripe's example guardrail is "you shouldn't combine data from two unrelated customer contexts in a single analysis", even when the user may access both ([Stripe](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)). Stripe files this work under "Building guardrails from scratch."

## Why it works

Composing on a harness shortens the build because the generic machinery already exists. LangChain says Deep Agents "wires together the tool-calling loop, middleware composition, streaming, and state management that would otherwise take months to build and harden from scratch" ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). The team writes only the organization-specific layer, and the configuration layer above it lets other teams add agents without editing the harness. Skill-gated loading keeps hundreds of tool schemas out of the default context. That holds while the model selects skills accurately.

## When this backfires

- The catalog grows past what LLM selection handles. With a 1,024-character frontmatter limit, "the team discovered quality degradation of frontier models with more than 150 skills when combined with their system prompt" ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). The same post says "The number of skills remains a challenge, and the team is actively working towards better solutions for the future." At 1,000+ skills, it says "No LLM can perform reliable selection across a skills catalog that size without assistance". Pure LLM selection "works well at current scale and produces better results than RAG when full context is available", and the post expects a RAG or classifier layer to prefilter at scale ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). Stripe's post calls the hybrid approach solved and LangChain calls it in progress (see the conflict table above). A separate benchmark tested retrieval that passes only the relevant tool descriptions to the model. It "more than triples tool selection accuracy (43.13% vs 13.62% baseline)" ([RAG-MCP, arXiv:2505.03275v1](https://arxiv.org/abs/2505.03275v1)).
- No platform sits under the harness. Without Python service support, a team pays the "large investment" Stripe paid before its week.
- The framework hides the loop. Anthropic warns that frameworks "often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug" ([Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)).
- Your guardrails depend on what a task should see. Stripe names customer-context isolation as an invariant its platform "has to enforce", and neither source says how ([Stripe](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)). Expect to write that kind of check in your own layer.

## Example

The sync-in, sync-out wrapper shows where Stripe's code meets Deep Agents middleware. Stripe "wraps every sandbox `execute` call with a "sync in / sync out" pattern: before execution, all relevant files are materialized into the sandbox; after execution, any new or modified files are synced back out to the virtual filesystem" ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). In Deep Agents, sandbox backends "expose an `execute` tool for shell commands in an isolated environment" ([Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)). Stripe owns the S3-backed filesystem and the copy step around each call. The result, per LangChain, is "a coherent, persistent file environment across the full lifetime of the session."

## Key Takeaways

- Read "one week" as an initial version built on Python support that already existed. Stripe's own post omits the figure.
- Budget the language and runtime platform work separately from the agent build, before you quote a timeline.
- Gate tool schemas behind skill selection, and plan a prefilter for when the catalog outgrows LLM selection. LangChain reports Stripe's team saw quality degradation past 150 skills ([LangChain](https://www.langchain.com/blog/how-stripe-built-their-knowledge-ai-platform-on-deep-agents)). At 1,000+ skills, LangChain says "No LLM can perform reliable selection across a skills catalog that size without assistance". Stripe says it uses a hybrid RAG/LLM approach ([Stripe](https://stripe.dev/blog/meet-stripes-knowledge-ai-platform)).
- Write task-level guardrails, such as customer-context isolation, in your own harness layer. Stripe lists this as a requirement its platform must enforce.
- Expose the sandbox as a tool, and sync files in and out around each call so the session keeps one file view.

## Related

- [Compose vs Fork vs Build: Adopting an Agent Harness](../patterns/agent-design/open-framework-compose-or-fork.md) — the composition route Kai took, and when upstream instability flips it
- [Session Harness Sandbox Separation for Long-Running Agents](../patterns/agent-design/session-harness-sandbox-separation.md) — why the sandbox sits outside the agent loop
- [Skill Loadout Curation for Coding Agents](../context-engineering/skill-loadout-curation.md) — how skill routing degrades as the catalog grows
- [Enterprise Skill Marketplace: Distribution and Quality](enterprise-skill-marketplace.md) — distributing and maintaining a federated skill library
- [Managed vs Self-Hosted Agent Harness: Deployment Trade-offs](../patterns/agent-design/managed-vs-self-hosted-harness.md) — the deployment choice under a composed harness

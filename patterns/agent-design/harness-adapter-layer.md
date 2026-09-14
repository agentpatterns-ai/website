---
title: "Running Several Coding Agents Behind One Harness Interface"
term: "Harness Adapter Layer"
description: "An adapter layer runs several coding-agent harnesses behind one interface, and the published capability table is what tells you the swap's real price."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - harness-engineering
aliases:
  - harness adapter layer
  - HarnessAgent interface
  - multi-harness adapter
last_reviewed: 2026-09-12
maturity: emerging
---

# Running Several Coding Agents Behind One Harness Interface

> One interface across several coding-agent harnesses is worth its cost only when you need two of them and can live in the intersection.

A harness adapter layer puts one interface in front of several coding-agent harnesses, so changing agent becomes a dependency change rather than an integration rewrite. Vercel's AI SDK ships the design: "The harness layer lets your application run different coding agents through the same `HarnessAgent` interface, so you can switch agents without changing your application code" ([Vercel changelog, 2026-09-10](https://vercel.com/changelog/github-copilot-ai-sdk-harness-adapter)). Ten adapters exist, each normalizing one runtime's "sessions, stream events, tools, usage, lifecycle state, and configuration into the harness contract" ([AI SDK adapter table](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/docs/03-ai-sdk-harnesses/05-harness-adapters.mdx)).

## When the layer earns its cost

Both conditions have to hold. The second harness target has to be real: a product on one agent forever buys an option it never exercises. The application also has to stay inside the portable intersection: the swap promise covers what every adapter carries and nothing else.

## What the common interface drops

Vercel publishes a per-adapter capability table; read it before committing. Custom tools and custom skills work on all ten adapters. Structured output works on six. Built-in tool filtering works on five, two of them only "via auto-rejection", and all four ACP-routed adapters are among the five that lack it ([AI SDK adapter table](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/docs/03-ai-sdk-harnesses/05-harness-adapters.mdx)).

Check the adapter's own page too: the two disagree. The table marks built-in tool approval as supported everywhere except Codex. The Codex, Cursor, Grok Build and GitHub Copilot pages each say the runtime does "not currently support built-in tool approval requests. Use `permissionMode: 'allow-all'` with this adapter. Host-executed AI SDK tool approvals still work" ([Codex](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/02-codex.mdx), [GitHub Copilot](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/11-github-copilot.mdx)). Four adapters, not one, take away the harness's own approval prompt.

Per-runtime configuration moves into a declarative profile rather than disappearing. The generic ACP adapter requires a `modelMapping` per runtime, and where a runtime exposes native permission controls it says to "Map all three Harness permission modes ... and set unsupported modes to `null`". Codex ACP sets two of the three to `null` and "supports only `permissionMode: 'allow-all'`" ([AI SDK, ACP harness](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/06-acp.mdx)).

## Where ACP fits

The Agent Client Protocol carries four of the ten adapters, listed as "Sandbox via ACP": Cursor, fx, GitHub Copilot and Grok Build. The other six use a sandbox bridge or the host process. ACP is a route rather than the foundation: "ACP is an abstraction over coding harnesses, but the AI SDK harness layer stays deliberately decoupled from it" ([Vercel changelog, 2026-08-13](https://vercel.com/changelog/use-acp-compatible-harnesses-with-the-ai-sdk-harness-layer)). It is also where capability goes missing, because version 1 "does not expose model-step boundaries or per-step usage", has "no portable manual compaction or mid-turn steering API", and has "no portable built-in tool filtering API" ([AI SDK, ACP harness](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/06-acp.mdx)). Vercel's guidance follows, recommending the direct Claude Code and Codex adapters "since they can provide tighter integration" (same changelog).

## Why it works

One interface spans ten runtimes because harness divergence is structured rather than arbitrary. A study of 70 agent-system projects finds "five recurring design dimensions (subagent architecture, context management, tool systems, safety mechanisms, and orchestration)" ([Hu Wei, arXiv:2604.18071v1](https://arxiv.org/abs/2604.18071v1); see [Harness Design Dimensions and Archetypes](harness-design-dimensions.md)). An adapter normalizes what runtimes agree on and declares the rest.

The other half is the refusal. A capability the runtime cannot meet raises `HarnessCapabilityUnsupportedError` rather than being approximated. Supplying `output` to Pi "causes the turn to throw" ([Pi](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/03-pi.mdx)), and an ACP profile with no output-schema mapping throws "instead of assuming that an arbitrary ACP implementation understands the schema" ([ACP](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/06-acp.mdx)). One layer down, a wrong envelope declaration instead "silently degrades capability with no in-IDE failure" ([Multi-Shape BYOK Provider](multi-shape-byok-provider.md)). Declared capability plus a typed throw is what lets you price the swap in advance.

## When this backfires

- The application needs a capability with no portable form. The three ACP version 1 gaps above have none, so the code grows the per-adapter branches the layer was meant to remove.
- Approval is a product surface. Four adapters send you to `permissionMode: 'allow-all'`, leaving only "host-executed AI SDK tool approvals". A product that gates the agent's writes behind a reviewer rules out four of the ten.
- The team cannot absorb pre-stable churn. "Harness packages are experimental. Expect breaking changes between releases" ([Vercel changelog, 2026-06-12](https://vercel.com/changelog/program-agent-harnesses-with-ai-sdk)).
- Debuggability outranks portability. A failure gains a third candidate home, and that is where framework defects cluster. Across 5,669 bug reports from AutoGen, CrewAI, LangChain, LangGraph and MetaGPT, bugs "mainly manifest as Incorrect Functionality (76.00%)" in a quality pattern "shaped by semantic interface boundaries" ([Zhu et al., arXiv:2602.21806v4](https://arxiv.org/abs/2602.21806v4)). Anthropic suggests "developers start by using LLM APIs directly" for the same reason ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)).

## Example

An application that holds the agent's own file writes for a reviewer can run on Claude Code, Cline, OpenCode or Pi. All four pages carry the same line: the runtime "supports built-in tool approval requests when `permissionMode` is `allow-reads` or `allow-edits`" ([Claude Code](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/01-claude-code.mdx), [Cline](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/08-cline.mdx), [OpenCode](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/04-opencode.mdx), [Pi](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/03-pi.mdx)).

Swap in GitHub Copilot and two things break, differently. Filtering its built-in tools "throws an unsupported-capability error", so a test catches it. Approval changes by configuration instead: the adapter "does not currently support built-in tool approval requests" and you set `permissionMode: 'allow-all'`, so the harness stops asking before it runs its own tools ([GitHub Copilot](https://github.com/vercel/ai/blob/6c6c2210b9532a4c369615c044a16d595f3db117/content/providers/02-ai-sdk-harnesses/11-github-copilot.mdx)). The typed throw is the good case.

## Key Takeaways

- Two harness targets and a product confined to the portable capabilities are the conditions. Miss either and a direct integration is cheaper.
- Check the capability table against your product's requirements before the dependency lands. Structured output holds on 6 of 10 adapters and built-in tool filtering on 5.
- Then check the adapter's own page, because the two disagree. The table counts built-in tool approval as missing on one adapter; the pages put it at four.
- Going through ACP costs more than going direct. All four ACP-routed adapters give up built-in tool filtering, which is why the vendor recommends direct adapters where they exist.
- Write a test per capability your product depends on. The gaps that throw will fail it; the gaps that degrade by configuration will not, and those are the ones worth an assertion of their own.

## Related

- [Choosing an Integration Layer for an Embedded Agent Harness](embedded-harness-integration-layer.md) — which layer to integrate a single harness at, the decision that comes before this one.
- [Harness Design Dimensions and Archetypes](harness-design-dimensions.md) — the five dimensions an adapter has to normalize or declare per runtime.
- [Multi-Shape BYOK Provider](multi-shape-byok-provider.md) — the same capability-loss problem one layer down, at the model envelope.
- [Model-Neutral Agent Architecture](model-neutral-agent-architecture.md) — swapping the backing model instead of the whole harness.
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — why one configuration for every runtime converges on the weakest one.

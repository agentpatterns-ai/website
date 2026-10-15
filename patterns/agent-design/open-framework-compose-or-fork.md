---
title: "Compose vs Fork vs Build: Adopting an Agent Harness"
term: "Compose vs Fork vs Build"
description: "Composing on an open agent framework buys an upgrade path only when upstream commits to compatibility. Read the stability notice before the diagram."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - compose vs fork agent harness
  - forking an agent framework
  - internal coding agent framework
last_reviewed: 2026-10-14
maturity: emerging
---

# Compose vs Fork vs Build: Adopting an Agent Harness

> Composing a harness on a maintained open framework buys an upgrade path worth exactly as much as the upstream's compatibility commitment.

A team self-hosting a coding agent obtains its harness one of three ways: compose on a maintained framework, fork one, or write it. Composition's case is the upgrade path: pull upstream improvements without re-applying your own changes. LangChain makes that case for its Open SWE framework directly: "When Deep Agents improves (better context management, more efficient planning, optimized token usage), you can incorporate those improvements without rebuilding your customizations" ([LangChain, 17 March 2026](https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents)). The case holds only when upstream means to keep that interface stable, so check before reading the architecture diagram.

All three routes ship at scale. LangChain sets Open SWE beside three internal systems in one comparison table, based on publicly available information. It records Open SWE and Ramp's Inspect as composed, Stripe's Minions as "Forked (Goose)", and Coinbase's Cloudbot as built from scratch ([LangChain, 17 March 2026](https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents)). Modal confirms the Inspect reading: "Inside the sandbox, OpenCode runs as the coding agent" ([Modal, 19 February 2026](https://modal.com/blog/how-ramp-built-a-full-context-background-coding-agent-on-modal)).

## When composing pays

Three conditions, each checkable before you commit:

- Upstream states a compatibility commitment. Not a roadmap or a changelog, but a sentence saying the interface you bind to will keep working. Its absence settles the question.
- Your changes fit the published extension points. LangChain lists six for Open SWE: sandbox provider, model, tools, triggers, system prompt, and middleware ([LangChain, 17 March 2026](https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents)). Six slots cover six shapes of change.
- You can read current behavior from the code. If a launch post is the only description of how it runs, you are sourcing runtime behavior from marketing.

Fail the first condition and the arithmetic flips: forking turns open-ended exposure to someone else's release decisions into a one-time cost you can size now. Stripe, which that table puts on the fork route, reports agents "responsible for more than a thousand pull requests merged each week" ([Stripe, 9 February 2026](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)). Writing your own is the same trade without the starting code.

## Why it works

Composition works for the same reason separation of concerns does anywhere else: your edits and upstream's sit in different files. LangChain names the causal step: "You can maintain org-specific tools, prompts, and workflows as configuration rather than as modifications to core agent logic" ([LangChain, 17 March 2026](https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents)). Its repository states the same split: Deep Agents "supplies planning, filesystem, shell, skills, and subagent primitives", LangGraph "provides durable execution and thread state", and "Open SWE adds engineering tools, integrations, authorization, and user interfaces" ([Open SWE README](https://github.com/langchain-ai/open-swe)). Because a core change touches none of your files, taking it costs a version bump instead of a merge.

The saving comes from the interface, not from the upstream being well run. An upstream that disclaims compatibility has not removed the collision. It moved it to the interface. In the core loop you hold a diff you can re-apply; at the interface you hold nothing.

## When this backfires

- Upstream disclaims the guarantee. Open SWE's README says "Expect breaking changes and rough edges. We're not accepting issues or external contributions at this time" and "You're welcome to explore and fork the code, but correctness, stability, and compatibility are not guaranteed" ([Open SWE README](https://github.com/langchain-ai/open-swe)). Your configuration-shaped work then breaks on the core's cadence, and closed contributions mean you cannot land the fix upstream.
- The change you need has no slot. A policy engine, a credential boundary, or an approval surface that must behave differently is not a configuration edit. A competing vendor states the general case: when something inside an adopted harness does not fit, "you fork it, fight it, or work around it" ([iii.dev](https://iii.dev/blog/how-to-build-your-own-agent-harness/)). That is a rival's position, not a measurement.
- The license stops short of production. Open SWE is MIT-licensed, and its README adds that "Production standalone Agent Server deployments require a license key" ([Open SWE README](https://github.com/langchain-ai/open-swe)). A team that chose on open-source grounds learns this after the architecture is fixed.
- Default credential scope exceeds your threat model. "Coding sandboxes normally receive installation-wide GitHub App access", and approvals are narrower than the name suggests: "Workflow-file approval prompts guard detected Git pushes, not every possible shell or API write" ([Open SWE README](https://github.com/langchain-ai/open-swe)). Both are adjustable, and both are work the framework leaves to you.
- Your integration surface dwarfs the starting toolset: Open SWE ships roughly 15 curated tools against the roughly 500 Stripe's agents carry, and the gap is yours to write ([LangChain, 17 March 2026](https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents)).

No controlled comparison of the three routes exists. Every available figure comes from a party selling one of them, this page's primary source included.

## Example

Open SWE announced on 17 March 2026, and its repository showed 2,649 commits on 14 October 2026 ([Open SWE README](https://github.com/langchain-ai/open-swe)). Where the announcement and the repository disagree, the repository wins:

| Question | Announcement, March 2026 | README, October 2026 |
|---|---|---|
| Unreachable sandbox | "Sandboxes automatically recreate if they become unreachable" | "An unreachable coding sandbox is not silently replaced." |
| Stability | "a customizable foundation rather than a finished product. Every major component is pluggable" | "correctness, stability, and compatibility are not guaranteed" |
| External contributions | Not addressed | "We're not accepting issues or external contributions at this time" |

Sources: [LangChain, 17 March 2026](https://blog.langchain.com/open-swe-an-open-source-framework-for-internal-coding-agents) and the [Open SWE README](https://github.com/langchain-ai/open-swe).

The sandbox row is the cheap lesson: recovery logic written against the announcement's promise waits forever on a dead sandbox.

## Key Takeaways

- The compose-or-fork decision turns on one sentence in the upstream's README, not on the quality of its architecture.
- Ask what breaks when upstream ships a minor version. If the repository cannot answer that, you do not know the cost yet.
- Price a change that has no extension point as a fork.
- Read three documents before the architecture diagram: the stability notice, the contribution policy, and the production license terms.
- Discount every cost figure by who sells the route, a vendor's own included.

## Related

- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — who runs the harness, decided on five signals
- [Choosing an Integration Layer for an Embedded Agent Harness](embedded-harness-integration-layer.md) — how a host application talks to the harness it adopts
- [Production Hosting Topology for Self-Hosted Agent SDK Runtimes](agent-sdk-hosting-topology.md) — what running one costs in containers, credentials, and isolation
- [Harness Impermanence](harness-impermanence.md) — why harness code should be cheap to delete
- [Agent Loop Middleware](../../loop-engineering/agent-loop-middleware.md) — the extension point Open SWE uses for safety nets and message injection

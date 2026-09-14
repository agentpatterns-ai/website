---
title: "Role-Declared Context Mode: Where the Inherit Decision Lives"
term: "Role-Declared Context Mode"
description: "Declaring a subagent's context mode on its role keeps a verifier isolated even when the supervisor it checks is the one issuing the call."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - subagent context mode
  - declared fork mode
  - context mode declaration
last_reviewed: 2026-09-09
maturity: emerging
---

# Role-Declared Context Mode: Where the Inherit Decision Lives

> Declare a subagent's context mode on its role where that mode never varies. A per-dispatch choice lets the supervisor decide what its own reviewer sees.

Two shipped harnesses put the inherit-or-start-fresh decision in different places. LangChain's `deepagents` makes it a field on the subagent definition, alongside `tools` and `permissions`: "Since forking is a mode you set on the subagent itself, that's a decision you make when you define it" ([deepagents subagents](https://docs.langchain.com/oss/python/deepagents/subagents)). Claude Code keeps it at the dispatch. "Claude starts a fork by requesting the `fork` subagent type through the Agent tool", while any other subagent "starts fresh from its definition" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). Which mode a task wants is settled in [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md). This page covers where that answer gets written down.

## When the role should own it

Three conditions have to hold before a declared mode beats a per-dispatch choice.

Invariance comes first. LangChain gives a verifier the isolated mode, because "inheriting the supervisor's reasoning can be counterproductive. The verifier should evaluate the work itself rather than being anchored by the supervisor's diagnosis or expectations" ([Bengre and Curme, Organizing Context in a Multi-Agent Harness](https://www.langchain.com/blog/organizing-context-in-a-multi-agent-harness)). It gives a memory agent the forked mode, since the conversation is the material that agent has to read. Roles shaped like those have one answer, so writing it once removes the chance of a dispatch getting it wrong.

The supervisor is the party under review. In a supervisor topology the same agent produces the work and issues the delegation, so a dispatch-time choice puts the producer in charge of its verifier's independence. That is the decision you least want the producer making.

Nothing else may ride on the mode field. `deepagents` bundles two things into it: a forked subagent "Cannot use `task`; must finish the work itself", and "`skills` is rejected if provided" ([deepagents subagents](https://docs.langchain.com/oss/python/deepagents/subagents)). Declaring `mode: "fork"` there also strips delegation and skill loading.

## Why it works

Inherited production context makes a reviewer rationalize rather than scrutinize, and the leak shows up at the size of a single prompt. Song ran 30 artifacts carrying 150 injected errors through 360 reviews under four conditions. Cross-Context Review, which sees the artifact alone in a fresh session, scored an F1 of 28.6%. Same-session self-review scored 24.6% (p=0.008, d=0.52). Subagent Review scored 23.8% (p=0.004, d=0.57), and that condition already ran in a fresh session whose only extra context was the generation prompt ([Song, Cross-Context Review, arXiv 2603.12123v1](https://arxiv.org/abs/2603.12123v1)). Passing down the prompt alone cost 4.8 F1 points. Reviewing twice in the same session did not beat reviewing once (p=0.11), which rules out repetition. The paper states the mechanism plainly: "When the model reviews its output in the same session, the entire conversation history sits in the context window ... All of this anchors the model's judgment. It does not scrutinize; it rationalizes."

Read that as a bound on the effect rather than a license. The experiment used one model (Claude Opus 4.6) and errors it injected rather than found, and 28.6% is a low absolute score. What it establishes is granularity: what a subagent inherits matters at a resolution finer than the whole conversation.

## When this backfires

One role, two situations. An implementer that sometimes continues the supervisor's investigation and sometimes picks up a standalone ticket has no single right mode. Pinning one forces two near-identical roster entries, and roster size costs context — Claude Code warns once subagent descriptions "exceed 15,000 tokens" ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)).

Wide fan-out from a forked role. Each parallel dispatch copies the supervisor's history again. LangChain names the case for parallel researchers: "forking each one would duplicate the supervisor's history even though each researcher only needs its assigned question" ([Bengre and Curme](https://www.langchain.com/blog/organizing-context-in-a-multi-agent-harness)).

A role that has to delegate further. A `deepagents` fork cannot call `task`, so a supervisor-shaped role cannot be declared forked there. Claude Code inverts this: "Forks skip both filters and receive the main conversation's exact tool pool", so its forks keep the `Agent` tool until they reach the depth limit ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)).

A roster that lives in application code. A `deepagents` subagent is an object handed to `create_deep_agent(subagents=[...])`, so its mode is reviewed wherever that list gets built rather than in a config file of its own. [Static Roster vs Runtime Subagent Definition](static-roster-vs-runtime-subagent-definition.md) covers the trade.

A permanently forked role in a session handling untrusted content. It inherits every accumulated tool result on every dispatch, so the injection surface stays open. The containment argument lives in [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md).

## Example

A review pipeline runs a supervisor that reads a diff, diagnoses problems, then delegates twice: a fixer to implement the change, and a reviewer to judge the result.

In `deepagents` both answers sit in the roster. The fixer carries `mode: "fork"` and picks up the investigation without rediscovering it. The reviewer carries `mode: "isolated"` and receives the diff plus its criteria. No dispatch-time choice can hand the reviewer the diagnosis it is supposed to test.

In Claude Code the fixer half works the same way through a fork request, but the reviewer's isolation rests on the supervisor never asking for a fork. The roster cannot express "never fork this one". Denying the `fork` subagent type for the session, or running with `CLAUDE_CODE_FORK_SUBAGENT=0`, is the closest equivalent, and it is a session-wide switch rather than a per-role one.

## Key Takeaways

- Declaring the mode on the role takes the producer out of the decision about how much of its reasoning the verifier sees.
- The precondition is invariance. A role whose right mode changes by task belongs in two roster entries, or at a call site.
- Audit what a verifier receives at the granularity of individual messages. The generation prompt on its own is enough to move the result.
- Read the mode field's other effects before you set it. A harness that ties delegation or skills to the mode has made two decisions look like one.
- Fan-out width is the argument against a declared fork: N parallel dispatches copy the supervisor's history N times.

## Related

- [Forked vs Fresh Subagents: When to Inherit the Parent Conversation](forked-vs-fresh-subagents.md) — which mode a task wants, the decision this page relocates.
- [The Subagent Inheritance Contract: What Crosses Down](subagent-inheritance-contract.md) — what a subagent carries even when nobody declared anything.
- [Static Roster vs Runtime Subagent Definition](static-roster-vs-runtime-subagent-definition.md) — the same author-time versus runtime axis, applied to the whole subagent identity.
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md) — declaring what a role may do, next to declaring what it may see.
- [Reviewer Precision as a Pipeline Quality Proxy](reviewer-precision-proxy.md) — measuring whether the isolated reviewer catches more.

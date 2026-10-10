---
title: "Three Skill Disclosure Decisions to Move Off the Model"
term: "Skill Disclosure Control"
description: "Progressive disclosure leaves skill selection and tool gating to the model and fixes skill freshness at thread start; a skill file or the app holds each answer."
aliases:
  - skill disclosure control
  - pinned skills
  - skill-gated tools
tags:
  - agent-design
  - tool-agnostic
  - skills
last_reviewed: 2026-10-08
maturity: emerging
---

# Three Skill Disclosure Decisions to Move Off the Model

> Progressive disclosure leaves the model two skill decisions and fixes a third at thread start; a skill file or the application holds each answer.

Skill disclosure control is the choice of which component decides that a skill's contents enter the context window. Progressive disclosure answers it one way for every skill. The `name` and `description` "are loaded at startup for all skills", the full `SKILL.md` body "is loaded when the skill is activated", and supporting files load "as needed" ([Agent Skills specification](https://agentskills.io/specification)). The activation judgment is the agent's: a skill is "read only when the agent determines relevance" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)). Three decisions sit inside that default, and each has a controller that already knows the answer.

## Check this first: the default did not change

LangChain revised skills support in Deep Agents on 2026-10-07, and the layered model survived unchanged. The release post restates it as the reason skills work: "Skills work because of progressive disclosure. The agent sees only each skill's name and description up front, and reads the full instructions only when a task needs them" ([LangChain](https://www.langchain.com/blog/revamping-skills-in-deep-agents)). The current reference says the same: "Skills use progressive disclosure: the agent loads skill information in layers instead of all at once" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)).

Nothing was walked back. What the release adds is three overrides, each scoped to one decision and turned on per skill or per run.

## The three decisions

| Decision | Default controller | Controller that holds the answer | Deep Agents mechanism |
|---|---|---|---|
| Which skill applies to this request | The model, from descriptions | The application, when the user names a skill | `pinned_skills` on the run input |
| Whether a tool may be called yet | The model, from resident tool schemas | The skill file that documents the tool | `metadata.include_tools` in frontmatter |
| Whether the loaded skill set is current | Fixed at thread start | The application | `skills_metadata` set to `None` |

Selection is the decision with a named cost. When a user types `/meeting-prep`, the model still has to recognize and read the skill: "That adds a round trip before the work starts, and the model isn't guaranteed to load the right skill" ([LangChain](https://www.langchain.com/blog/revamping-skills-in-deep-agents)). The application parsed that name already, so pinning trades a message for a model call and a wrong guess.

Tool gating buys an ordering guarantee rather than tokens. A tool listed by a skill is unreachable until the skill is read: "Skill tools are gated. Until the agent reads the skill's `SKILL.md`, a call to one fails as an unknown tool, even if the model guesses its name and arguments" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)). Provider tool search produces a similar-looking arrangement without the gate: "Unlike a skill tool, a deferred tool is not gated. The model can find and call it through search before the agent reads the skill."

Freshness is the decision the default never revisits. Skills "load once per thread and stay in agent state, so every later model call on that thread reuses the same list", and skills added, edited, or deleted after that "never reach the model" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)). Resetting the stored metadata to `None` makes the next run rescan every source.

## Why it works

Moving a disclosure decision used to cost a full prompt recompute, so the alternative was "fixing the tool list for the lifetime of the conversation" ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)). Position in the request is the reason: "The `tools` array sits even earlier in the hashed request prefix than the top-level `system` field, so editing it invalidates the prompt cache for the entire conversation" ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)). Mid-conversation tool changes hold the array fixed and change what is offered from a later point in the conversation. A tool declared with `defer_loading: true` stays withheld until a `tool_addition` block surfaces it, and because "the `tools` array itself never changes", the cached prefix stays intact. One appended message replaces a whole-prefix recompute, which is what makes per-skill overrides affordable. Our account of [dynamic tool fetching](../anti-patterns/dynamic-tool-fetching-cache-break.md) covers the arithmetic this path is the exception to.

## When this backfires

- Summarization evicts the read, and the gated tool goes with it: "When summarization drops that read from the conversation, the tool is unavailable until the agent reads the skill again" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)).
- The model never selects the skill. A gated tool is not searchable, so a vague `description` makes it dead weight rather than one extra round trip ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)).
- The model rejects mid-conversation tool changes, so Deep Agents "adds the tool to the request's `tools`, which invalidates the cache" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)). On the Claude API, mid-conversation tool changes "are in beta on the same models" as mid-conversation system messages, a list that excludes Claude Sonnet 5, and need the `inline-tools-2026-09-15` beta header ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)).
- The application pins liberally. A pinned skill is appended to the conversation and "stays in the conversation as written" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)), so a request that never needed it still carries the full body.
- The deployment has no checkpointer, so "every run loads skills again" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)) and the reload control answers a problem that is not there.

A controlled comparison of four skill loading methods across five benchmarks found no method that wins in every regime ([Nakasuji, arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)), so treat none of this as a default.

## What transfers

The three decisions transfer to any harness that loads skills lazily. The mechanism does not. Skill-bound tools are "a Deep Agents feature, not part of the Agent Skills specification". Deep Agents reads the names from "the spec's free-form `metadata` field", and they are "unrelated to the spec's `allowed-tools` field, which pre-approves tools rather than adding them" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)). The specification reserves that field for client extensions: clients "can use this to store additional properties not defined by the Agent Skills spec", and should keep key names "reasonably unique to avoid accidental conflicts" ([Agent Skills specification](https://agentskills.io/specification)). A `SKILL.md` carrying `include_tools` therefore copies cleanly into another client, which is under no obligation to read the key.

Pinning is a product decision rather than a feature to adopt. Deep Agents "does not look for skill names in messages", so the application chooses the syntax and passes the names it found ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)).

## Example

The gate is declared in the skill's frontmatter:

```yaml
name: linear
description: Triage and file Linear issues. Use when the user reports a bug or asks about the Linear backlog.
metadata:
  include_tools: list_issues create_issue
```

Two details decide whether the gate holds. The names are space-separated inside one string, and "a YAML list does not match any tool". Where the tool object is passed matters as much. Pass the tools to the middleware, because a tool passed to the agent's own `tools` is "visible, so `include_tools` has no effect" ([Deep Agents skills](https://docs.langchain.com/oss/python/deepagents/skills)).

## Key Takeaways

- Name the controller for each of the three decisions before changing a loading policy. Two of them are application-side and need no model behavior at all.
- When a gated tool fails as unknown, check whether summarization dropped the skill read before you check the names. Both produce the same error.
- Confirm your models accept mid-conversation tool changes before gating tools. Without that, the gate costs a cache invalidation per skill read, and the Claude API path is beta and header-gated.
- Pin on an explicit user signal only. A parsed `/skill-name` is such a signal; a guess about relevance is the model's job.
- Audit long threads for staleness separately from cost. A thread that holds the right skills cheaply can still be holding last week's set.

## Related

- [Progressive Disclosure for Layered Agent Definitions](progressive-disclosure-agents.md) — the default this page overrides, and the two-layer split it rests on
- [Subagent vs In-Context Skill Execution](subagent-vs-in-context-skill-execution.md) — the other disclosure decision, where a skill runs rather than when it loads
- [Choosing a Skill Loading Method for Agents](../../context-engineering/skill-loading-method-selection.md) — measured cost of four loading methods, with no universal winner
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md) — why late tool loading was a bad trade before append-only disclosure
- [Static-Context Tool Residence: Two Overrides on Hit Rate](../../context-engineering/static-context-tool-residence.md) — the same question one level down, for tool definitions

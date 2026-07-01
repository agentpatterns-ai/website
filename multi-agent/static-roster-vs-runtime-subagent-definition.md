---
title: "Static Roster vs Runtime Subagent Definition"
term: "Static Roster vs Runtime Subagent Definition"
description: "Static subagent rosters are the safer default for coding agents — programmatic definition is justified only for open-ended tasks with unknown sub-task shape."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - static subagent roster
  - programmatic subagent definition
  - runtime subagent composition
last_reviewed: 2026-06-30
maturity: adopted
---

# Static Roster vs Runtime Subagent Definition

> Static subagent rosters are the safer default; programmatic definition pays off only when sub-task shape cannot be known at author time.

The decision is about who defines each subagent's identity — prompt, tool allowlist, scope — and when. Author-time static files fix those decisions in version control before any run starts. Developer code assembled at invocation is programmatic definition. LLM self-composition — where the model picks each helper's tools mid-task — is unsupported by shipped tools and undermines the structural guarantees that make scoping safe.

## Three tiers of subagent definition

The ecosystem conflates three things under "dynamic subagents."

Author-time static roster: each subagent is a reviewed file with a fixed system prompt and tool allowlist. Claude Code's `.claude/agents/*.md`, Gemini CLI's `.gemini/agents/*.md`, and Copilot CLI's `.github/agents/*.agent.md` all use this shape as their default. The model dispatches to a pre-configured worker; it does not alter the worker's definition ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)).

Developer-code programmatic definition: a program assembles subagent specs at invocation. LangChain deepagents does this via `create_deep_agent(subagents=[...])`, where each SubAgent spec carries a `name`, `description`, `system_prompt`, and `tools` array. The developer or program writes those specs; the model dispatches against them. LangChain calls this "dynamic subagents" because the orchestration code can loop, branch, and fork at runtime — "relying on code patterns it's good at writing (like looping, branching, or concurrency) to write orchestration logic fit to the task" — not because the model invents new agent identities on the fly. Coverage becomes a structural guarantee, not a prompt-engineering problem ([LangChain: Introducing Dynamic Subagents in Deep Agents](https://www.langchain.com/blog/introducing-dynamic-subagents-in-deep-agents); [deepagents subagents docs](https://docs.langchain.com/oss/python/deepagents/subagents)).

LLM self-composition: the model selects or invents each helper's prompt and tool allowlist mid-task. No shipped coding tool supports this, and no source establishes that it improves outcomes over a developer-assembled roster. It is an anti-pattern for the reasons below.

## Why a static roster is safer

Schema-level tool filtering works because "the model cannot form the intent to call tools it has never seen" ([Bui 2026 §2.2.2](https://arxiv.org/abs/2603.05344)). That guarantee depends on the allowlist being fixed in advance. A runtime-chosen allowlist — particularly one the model can influence mid-task — removes that precondition and reintroduces the exact intent the filter was built to prevent.

Static definitions also give you reproducible evals. When every subagent's prompt and tool set lives in version control, a regression traces to a specific change in a specific file. A non-deterministic roster cannot offer this: you cannot pin which definition produced a result, which breaks reproducible reviewer calibration. Every handoff between agents introduces loss, and fewer well-defined agents compound errors less than a freely assembled set ([Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)).

For agents that hold private data, web-fetched content, and write egress together — the lethal trifecta — runtime tool selection reopens a closed safety leg. Indirect prompt injection can then steer which capabilities a spawned helper receives ([OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)).

## When programmatic definition is justified

Assembling specs in developer code at invocation is justified when sub-task shape is genuinely unknown at author time and the roster stays developer-controlled: the model dispatches against pre-configured types; it does not mint new prompts or expand tool allowlists.

Three guardrails are required when you move to programmatic definition:

- Spawn cap. Without a ceiling, agents produce unbounded recursion chains ([Kilo-Org/kilocode #8637](https://github.com/Kilo-Org/kilocode/issues/8637)).
- Tool-scope ceiling. Each programmatically assembled spec should narrow from a reviewed baseline allowlist, not compose arbitrarily.
- Request-level tracing. Non-deterministic rosters make root-cause analysis impossible without it.

If three to five static worker roles cover the task, programmatic definition is overhead with worse observability — the same over-decomposition cost that arises from reflexive multi-agent decomposition ([Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)).

## When this backfires

Programmatic or model-driven definition fails in four conditions:

- Agents that hold the lethal trifecta. Runtime tool selection reopens a closed safety leg; prompt injection can steer which tools a spawned helper receives ([OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)).
- No spawn ceiling. Uncapped spawning produces unbounded chains ([kilocode #8637](https://github.com/Kilo-Org/kilocode/issues/8637)).
- Regression-gated pipelines. A non-deterministic roster breaks reproducible calibration.
- Fixed-shape task sets. When roles are known and few, runtime definition adds overhead without any adaptability benefit.

## Cross-tool reality

Claude Code, Gemini CLI, and Copilot CLI all implement subagents as static Markdown files with YAML frontmatter. Claude Code's `--agents` JSON flag and its SDK `agents` option allow session-scoped programmatic definition, but that JSON is written by a developer or program, not by the model itself ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). See the [cross-tool comparison](cross-tool-subagent-comparison.md) for how each tool handles tool scoping and recursion caps.

## Key Takeaways

- The decision axis is who defines each subagent's identity — not how many subagents run or how they share context.
- "Dynamic subagents" in LangChain means code-driven dispatch of pre-configured types, not a model minting new helper identities mid-task.
- A static file roster is the safer default: auditability, reproducible evals, and schema-level tool filtering all depend on fixed definitions set before any run.
- Programmatic definition earns its place only for genuinely open-ended tasks where sub-task shape is unknown at author time, and requires spawn caps, tool-scope ceilings, and tracing to be safe.
- LLM self-composition — where the model picks its own helpers' prompts and tools — is not supported by any shipped tool and structurally undermines schema-level tool filtering.

## Related

- [Declarative Multi-Agent Composition](declarative-multi-agent-composition.md) — the static-roster approach taken to its logical end: agents and workflows defined entirely as structured data
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md) — the mechanism that makes a fixed allowlist a structural safety guarantee rather than a convention
- [Cross-Tool Subagent Comparison](cross-tool-subagent-comparison.md) — how Claude Code, Gemini CLI, and Copilot CLI each implement static subagent definitions and tool scoping
- [Recursive Sub-Agent Delegation: Depth Limits and Trade-offs in Nested Hierarchies](recursive-sub-agent-delegation-depth.md) — what happens at the other end of uncapped programmatic spawning
- [Claude Code Dynamic Workflows](../tools/claude/dynamic-workflows.md) — the dispatch interpretation: code-driven orchestration of pre-configured subagent types at scale

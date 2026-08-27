---
title: "In-Loop Interception: Custom Logic Between the Model Call and the Tool Call"
term: "In-Loop Interception"
description: "Run your own code at the point where the model has proposed a tool call and the runtime has not dispatched it, and know which decisions that point offers in each runtime."
tags:
  - loop-engineering
  - tool-agnostic
aliases:
  - pre-dispatch interception
  - model-to-tool interception
  - PreToolUse interception
last_reviewed: 2026-08-25
maturity: adopted
---

# In-Loop Interception: Custom Logic Between the Model Call and the Tool Call

> Code at the model-to-tool boundary reads the proposed call before it runs. Runtimes differ less in what they rewrite than in whether they can ask.

Reach inside the loop when the side effect is irreversible, or when a correction has to land before the model acts. Stopping a destructive shell command is the first case: once the runtime dispatches it, no later check helps. For every other rule, wrap the loop from outside, where [agent loop middleware](agent-loop-middleware.md) sits off the critical path and cannot stall a turn. The in-loop point is `PreToolUse`. The model has proposed a tool call, the runtime has not dispatched it, and your handler decides what happens next.

## What the handler can see

The proposed arguments exist and the side effect does not. That gap is the whole reason to be here.

Codex passes a JSON payload on stdin carrying `session_id`, `turn_id`, `cwd`, `hook_event_name`, `model`, `permission_mode`, `tool_name`, and `tool_input`, where `tool_input` is the operation the agent is about to run. Registration is a config file rather than compiled code: `~/.codex/hooks.json` maps each event to a matcher and a handler command, and falcosecurity's `codex-interceptor`, a guardrail that denies calls its rules forbid, mounts on `PreToolUse`, which "fires before every tool dispatch" ([falcosecurity/prempti](https://github.com/falcosecurity/prempti/blob/main/hooks/codex/README.md)). A post-loop wrapper sees none of this. By the time the loop ends, the command has already run.

## What the interception point can decide

This is where a design stops porting.

Claude's Agent SDK gives the `PreToolUse` callback four decisions (`"allow"`, `"deny"`, `"ask"`, `"defer"`) plus `updatedInput`, which rewrites the proposed arguments before dispatch. Its worked example intercepts a `Write` call, prepends `/sandbox` to `file_path`, and auto-approves the rewritten call ([Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks)). The [block, rewrite, and completion-gate patterns](../instructions/enforcing-agent-behavior-with-hooks.md) built on those decisions are written up separately.

Codex offers the same rewrite. It "reserves `permissionDecision: \"allow\"` for hook responses that also provide `updatedInput` to rewrite the tool call" ([falcosecurity/prempti](https://github.com/falcosecurity/prempti/blob/main/hooks/codex/README.md)). falcosecurity's interceptor declines to use it — "Prempti never rewrites tool input" — which is that project's design choice, not a limit of the runtime.

Where the two diverge is the middle decision. Codex has no per-call user-confirmation UX at the hook layer, so a three-way rule collapses to two: "Falco `ask` rules become `deny` with the rule reason as the message. Users see the reason and can retry or change permission mode, but can't approve a single call inline" ([falcosecurity/prempti](https://github.com/falcosecurity/prempti/blob/main/hooks/codex/README.md)). An earlier design tried to route `ask` downstream and gave it up because the downstream event does not always fire: "`PermissionRequest` only fires when Codex's own `permission_mode` would have prompted (so `bypassPermissions`, `dontAsk`, and `--ask-for-approval never` would silently allow)" ([falcosecurity/prempti](https://github.com/falcosecurity/prempti/blob/main/hooks/codex/README.md)). That is a permission-mode coverage gap, not a missing capability.

A rule that collapses to deny changes the price of a correction. With `updatedInput` you fix the call and the turn continues. With deny you spend a model turn: the agent reads the reason and re-proposes, and nothing prevents it proposing the same call again. Budget for that retry, or use the rewrite both runtimes offer.

## Why it works

The runtime performs the dispatch, not the model, so the handler's return value is an input the model cannot argue with. That determinism is the same argument [hooks make against prompts](../instructions/hooks-vs-prompts.md). What this placement adds is timing. Anthropic documents the causal chain directly: the callback receives `tool_input`, and what it returns decides whether the tool runs and with which arguments ([Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks)). Acting there means acting on the agent's intent instead of on the damage.

## When this backfires

- The handler is slow and the tool is hot. "By default, the agent waits for your hook to return before proceeding" ([Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks)). One field report is blunt about the consequence: "telemetry-only Codex `PreToolUse` can still wait on the default 15s socket timeout if the cmux app is busy or slow to answer", which makes "Codex tool execution feel laggy even though this event is explicitly not actionable" ([manaflow-ai/cmux #4405](https://github.com/manaflow-ai/cmux/issues/4405)). A handler that decides nothing still costs the turn. Anthropic's escape is an async return (`{"async": true, "asyncTimeout": 30000}`), which suits logging and webhooks but not anything that steers the agent.
- The rule is checkable afterwards and the action is reversible. Formatting, lint, commit hygiene, PR creation. Run these after the tool call or after the loop, where a hang costs nobody a turn.
- The file that mounts the handler is untrusted. Hook config sits in the same settings tree an agent parses to decide which permissions, hooks, and tools the session offers, before a human has reviewed the checkout: `.claude/settings.json`, `.cursor/rules/`, `.codex/`, `.github/copilot/` ([pre-trust execution surface](../security/pre-trust-execution-surface.md)). An in-loop handler is exactly as trustworthy as the file that registered it.
- You want a matcher on a terminal event. Codex applies no matcher to `Stop` ([Towards Data Science](https://towardsdatascience.com/put-your-own-logic-inside-the-codex-agentic-loop/)), and neither does Claude Code, whose reference lists `Stop` among the events with no matcher support ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). Filter inside the handler and accept that it runs on every turn.

## Key Takeaways

- `PreToolUse` is the in-loop point: arguments proposed, side effect not yet caused. Everything else is a boundary.
- Both Claude's Agent SDK and Codex can rewrite a proposed call via `updatedInput`. What Codex lacks is a per-call approval UX at the hook layer, so a three-way rule collapses to deny.
- Deny costs a model turn per correction, and the agent may re-propose the same call. A rewrite costs nothing extra.
- The handler is synchronous by default and sits on every turn. A telemetry-only handler that round-trips to a busy local service can wait out that service's socket timeout — 15 seconds in cmux's case — while deciding nothing.
- Treat the hook config file as part of the untrusted checkout, not as trusted policy.

## Related

- [Agent Loop Middleware — Safety Nets and Message Injection](agent-loop-middleware.md) — the counterpart placement, wrapping the loop from outside where a hang cannot stall a turn
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](../tool-engineering/hooks-lifecycle-events.md) — the canonical event map across Claude Code, Copilot, and Cursor
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md) — why a handler beats an instruction, independent of where it sits
- [Enforcing Agent Behavior with Hooks](../instructions/enforcing-agent-behavior-with-hooks.md) — the block, rewrite, and completion-gate patterns in Claude Code
- [Six-Shape Approval Response Taxonomy](../patterns/agent-design/approval-response-taxonomy.md) — what a runtime that exposes more than allow and deny lets you answer with

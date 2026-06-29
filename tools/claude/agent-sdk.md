---
title: "Claude Agent SDK: Building Custom Agentic Workflows"
description: "The Claude Agent SDK exposes the Claude Code runtime as a library for building custom agentic workflows in CI, internal tools, and products."
aliases:
  - Claude Code SDK
tags:
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-27
status: current
---
# Claude Agent SDK

> The Claude Code runtime exposed as a library for building custom agentic workflows.

## What it is

The [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/claude-code-features) is the runtime that powers Claude Code, packaged as a library.

It ships as [`@anthropic-ai/claude-agent-sdk`](https://platform.claude.com/docs/en/agent-sdk/typescript) for TypeScript and `claude_agent_sdk` for Python.

## Core API

The core of the SDK is the `query()` function. It returns an async generator that yields typed messages. This is the [same agent loop that powers Claude Code](https://platform.claude.com/docs/en/agent-sdk/claude-code-features) — tool calls, file operations, reasoning, and response generation.

## What you get

The SDK gives you the same filesystem-based features as Claude Code. `settingSources` controls which filesystem locations the agent reads:

- Project instructions: CLAUDE.md and `.claude/rules/` load when `settingSources` includes `"project"`
- Skills: SKILL.md files load when `settingSources` includes `"project"` or `"user"`
- Hooks: filesystem hooks from `settings.json` fire when `settingSources` loads them; you can also pass programmatic hooks straight to `query()`
- Permissions: allow, ask, and deny rules control tool access
- Sub-agents: define them inline via the `agents` option, and Claude spawns them via the Task tool

The default for omitting `settingSources` has changed between releases. The v0.1.0 [migration guide](https://code.claude.com/docs/en/agent-sdk/migration-guide) first introduced isolation-by-default, but a Warning on that same page now states that "current SDK releases have reverted this default for `query()`: omitting the option once again loads user, project, and local settings, matching the CLI," and the [claude-code-features reference](https://code.claude.com/docs/en/agent-sdk/claude-code-features) documents "omitting `settingSources` is equivalent to `[\"user\", \"project\", \"local\"]`". The TypeScript SDK [changelog](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md) still describes isolation mode as the default, so the vendor's own sources disagree. Pin an SDK version, set `settingSources` explicitly, and verify load behavior in your own environment rather than relying on the default.

## When to use it

Use the SDK when you need Claude Code's agent capabilities in a custom application — CI pipelines, internal tools, automated workflows, or products that embed an agent. The SDK gives you the full agent loop without the CLI interface.

## Example

This minimal TypeScript script uses `query()` to run a security review in a CI pipeline. `settingSources: ["project"]` loads CLAUDE.md and hooks from the working directory; pass `settingSources: []` to run in isolation. Set the option explicitly — the default has shifted between SDK releases (see the caveat above).

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function runCodeReview(diffPath: string): Promise<string> {
  let result = "";
  for await (const message of query({
    prompt: `Review the diff at ${diffPath} for security issues.
Output a JSON array of findings: [{severity, file, line, description}].`,
    options: {
      maxTurns: 5,
      settingSources: ["project"], // loads CLAUDE.md and hooks from cwd
    },
  })) {
    if (message.type === "result" && message.subtype === "success") {
      result = message.result;
    }
  }
  return result;
}

// Usage in a CI script
const findings = await runCodeReview("pr-123.diff");
console.log(findings);
process.exit(findings.includes('"severity":"critical"') ? 1 : 0);
```

The loop runs until the task is complete or `maxTurns` is reached. The script exits non-zero when the agent finds a critical-severity finding, so it slots straight into CI gate logic.

## When this backfires

- Simpler workflows: if you only need Claude to run a single agentic task, `claude -p "..."` from the CLI avoids adding an SDK dependency and its release cadence to your application.
- Async generator complexity: consuming `query()` correctly means handling several message types. Teams new to async generators often misread the result stream, missing tool-call messages or consuming the final result before the loop ends.
- Feature isolation ambiguity: the SDK's default for `settingSources` has flipped between releases (see the caveat under "What you get"), so teams that do not set it explicitly can silently inherit or lose CLAUDE.md, skills, and hooks on an upgrade. Always pass `settingSources` explicitly — `[]` for isolation, `["user", "project", "local"]` for CLI parity.
- No default safety limits: `maxTurns` defaults to unlimited and `max_budget_usd` is optional, so a production agent that omits both can run for many turns and run up cost with no circuit breaker ([stop-reasons reference](https://platform.claude.com/docs/en/agent-sdk/stop-reasons), [`max_budget_usd` example](https://github.com/anthropics/claude-agent-sdk-python/blob/main/examples/max_budget_usd.py)). Set both explicitly, and check `message.subtype` against `error_max_turns` / `error_max_budget_usd` rather than relying on `is_error` alone.
- Bundle size in browser contexts: the SDK is built for server-side and CI use. For browser deployments, use the Anthropic Messages API directly instead.
- Subscription billing split: from [June 15, 2026](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan), Agent SDK and `claude -p` usage on Claude Plan subscriptions meters against a separate, non-rollover monthly credit billed at API rates. Once you exhaust it, you must buy a top-up rather than draw from general subscription limits. Plan for Agent SDK cost as API spend, not subscription spend, for any production workload.

## Key Takeaways

- Same runtime as Claude Code, exposed as a library
- Supports all Claude Code features: instructions, skills, hooks, permissions, sub-agents — configure `settingSources` explicitly because the omit-default has shifted between releases
- Core API is `query()` returning an async generator of typed messages
- Use when you need agent capabilities in custom applications, not the CLI

## Related

- [Sub-Agents](sub-agents.md)
- [Hooks](hooks-lifecycle.md)
- [Agent Teams](agent-teams.md)
- [Extension Points](extension-points.md)
- [Feature Flags](feature-flags.md)
- [Claude Code Review](code-review.md)
- [Claude Code --bare Flag](bare-mode.md)
- [Headless Claude in CI](../../workflows/headless-claude-ci.md)

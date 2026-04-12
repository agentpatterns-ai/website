---
title: "Claude Agent SDK: Building Custom Agentic Workflows"
description: "The Claude Code runtime exposed as a library for building custom agentic workflows. The Claude Agent SDK is the infrastructure that powers Claude Code"
aliases:
  - Claude Code SDK
tags:
  - agent-design
  - claude
---

# Claude Agent SDK

> The Claude Code runtime exposed as a library for building custom agentic workflows.

## What It Is

The [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/claude-code-features) is the infrastructure that powers Claude Code, available as a library.

Available as [`@anthropic-ai/claude-agent-sdk`](https://platform.claude.com/docs/en/agent-sdk/typescript) (TypeScript) and `claude_agent_sdk` (Python).

## Core API

The SDK's core is the `query()` function, which returns an async generator yielding typed messages. This is the [same agent loop that powers Claude Code](https://platform.claude.com/docs/en/agent-sdk/claude-code-features) — tool calls, file operations, reasoning, and response generation.

## What You Get

The SDK provides access to the same filesystem-based features as Claude Code. None load by default — set `settingSources` to activate them:

- **Project instructions**: CLAUDE.md and `.claude/rules/` load when `settingSources` includes `"project"`
- **Skills**: SKILL.md files are discovered when `settingSources` includes `"project"` or `"user"`
- **Hooks**: filesystem hooks from `settings.json` fire when `settingSources` loads them; programmatic hooks can also be passed directly to `query()`
- **Permissions**: allow/ask/deny rules control tool access
- **Sub-agents**: define inline via the `agents` option; Claude spawns them via the Task tool

## When to Use

Use the SDK when you need Claude Code's agentic capabilities in a custom application — CI pipelines, internal tools, automated workflows, or products that embed agent functionality. The SDK gives you the full agent loop without the CLI interface.

## Example

A minimal TypeScript script that uses `query()` to run a security review in a CI pipeline. `settingSources: ["project"]` loads CLAUDE.md and hooks from the working directory; omit it to run in isolation mode.

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

The loop continues until the task is complete or `maxTurns` is reached. The script exits non-zero if the agent finds a critical severity finding, making it directly composable with CI gate logic.

## When This Backfires

- **Simpler workflows**: If you only need Claude to run a single agentic task, `claude -p "..."` from the CLI avoids adding an SDK dependency and its release cadence to your application.
- **Async generator complexity**: Consuming `query()` correctly requires handling multiple message types; teams unfamiliar with async generators often misread the result stream, missing tool-call messages or consuming the final result before the loop ends.
- **Feature isolation**: By default the SDK runs in isolation mode — no CLAUDE.md, no skills, no hooks — which is intentional for reproducibility but surprises teams that expect CLI parity without setting `settingSources`.
- **Bundle size in browser contexts**: The SDK is designed for server-side and CI use; browser deployments should use the Anthropic Messages API directly instead.

## Key Takeaways

- Same runtime as Claude Code, exposed as a library
- Supports all Claude Code features: instructions, skills, hooks, permissions, sub-agents — but none load by default; configure `settingSources` explicitly
- Core API is `query()` returning an async generator of typed messages
- Use when you need agent capabilities in custom applications, not the CLI

## Related

- [Sub-Agents](sub-agents.md)
- [Hooks](hooks-lifecycle.md)
- [Agent Teams](agent-teams.md)
- [Extension Points](extension-points.md)
- [Feature Flags](feature-flags.md)
- [Claude Code /batch and Worktrees](batch-worktrees.md)
- [Claude Code Review](code-review.md)
- [Claude Code --bare Flag](bare-mode.md)
- [Claude Code Auto Mode](auto-mode.md)
- [Session Scheduling](session-scheduling.md)
- [Headless Claude in CI](../../workflows/headless-claude-ci.md)

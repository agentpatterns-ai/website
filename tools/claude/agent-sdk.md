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

The [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/claude-code-features) is the infrastructure that powers Claude Code, available as a library. Renamed from "Claude Code SDK" in September 2025 to reflect that the runtime is general-purpose, not coding-specific [unverified].

Available as [`@anthropic-ai/claude-agent-sdk`](https://platform.claude.com/docs/en/agent-sdk/typescript) (TypeScript) and `claude_agent_sdk` (Python).

## Core API

The SDK's core is the `query()` function, which returns an async generator yielding typed messages. This is the [same agent loop that powers Claude Code](https://platform.claude.com/docs/en/agent-sdk/claude-code-features) — tool calls, file operations, reasoning, and response generation.

## What You Get

The SDK provides the same filesystem-based features as Claude Code:

- **Project instructions**: CLAUDE.md and `.claude/rules/` are loaded automatically
- **Skills**: SKILL.md files are discovered and available
- **Hooks**: lifecycle hooks fire the same way as in Claude Code
- **Permissions**: allow/ask/deny rules control tool access
- **Sub-agents**: define inline via the `agents` option; Claude spawns them via the Task tool

## When to Use

Use the SDK when you need Claude Code's agentic capabilities in a custom application — CI pipelines, internal tools, automated workflows, or products that embed agent functionality. The SDK gives you the full agent loop without the CLI interface.

## Example

The following shows a minimal TypeScript script that uses the Agent SDK's `query()` function to run a coding task in a CI pipeline, collecting the final assistant message.

```typescript
import { query, MessageParam } from "@anthropic-ai/claude-agent-sdk";

async function runCodeReview(diffPath: string): Promise<string> {
  const messages: MessageParam[] = [
    {
      role: "user",
      content: `Review the diff at ${diffPath} for security issues.
Output a JSON array of findings: [{severity, file, line, description}].`,
    },
  ];

  let result = "";
  for await (const message of query({
    prompt: messages,
    options: { maxTurns: 5 },
  })) {
    if (message.type === "assistant" && typeof message.content === "string") {
      result = message.content;
    }
  }
  return result;
}

// Usage in a CI script
const findings = await runCodeReview("pr-123.diff");
console.log(findings);
process.exit(findings.includes('"severity":"critical"') ? 1 : 0);
```

The `query()` call runs the same agent loop that powers Claude Code — the CLAUDE.md in the working directory is loaded automatically, hooks fire at their lifecycle points, and the loop continues until the task is complete or `maxTurns` is reached. The script exits non-zero if the agent finds a critical severity finding, making it directly composable with CI gate logic.

## Key Takeaways

- Same runtime as Claude Code, exposed as a library
- Supports all Claude Code features: instructions, skills, hooks, permissions, sub-agents
- Core API is `query()` returning an async generator of typed messages
- Use when you need agent capabilities in custom applications, not the CLI

## Unverified Claims

- Renamed from "Claude Code SDK" in September 2025 to reflect that the runtime is general-purpose [unverified]

## Related

- [Sub-Agents](sub-agents.md)
- [Hooks](hooks-lifecycle.md)
- [Agent Teams](agent-teams.md)
- [Extension Points](extension-points.md)
- [Feature Flags](feature-flags.md)
- [Claude Code /batch and Worktrees](batch-worktrees.md)
- [Claude Code Review](code-review.md)
- [Session Scheduling](session-scheduling.md)
- [Headless Claude in CI](../../workflows/headless-claude-ci.md)

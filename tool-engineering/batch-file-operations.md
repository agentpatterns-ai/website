---
title: "Batch File Operations via Bash Scripts for AI Agents"
description: "Consolidate multiple file writes into a single bash script execution to reduce per-call overhead, token consumption, and sequential latency."
aliases:
  - batch writes
  - bulk file operations
tags:
  - cost-performance
  - context-engineering
---

# Batch File Operations via Bash Scripts

> Consolidate multiple file writes into a single bash script execution to reduce per-call overhead, token consumption, and sequential latency.

## The Problem with Sequential Edits

When an agent modifies multiple files one at a time, each edit incurs overhead: tool-call validation, context switching, and network round-trips. For a task that modifies 20 files, that overhead multiplies by 20. The per-call cost is small individually but compounds across large-scale refactoring, code generation, or configuration changes.

Consolidating these operations into a single script is one way to reduce that overhead. Anthropic's engineering guidance on [writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) states that "tools can consolidate functionality, handling potentially multiple discrete operations (or API calls) under the hood," which reduces "the context that would have otherwise been consumed by intermediate outputs."

## Why It Works

The mechanism has two parts: context consumption and LLM reasoning cost per call.

Every tool call adds to the agent's context window — the request, the tool response, and any intermediate output all persist in conversation history. Anthropic's [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) note that "Claude's context window holds your entire conversation, including every message, every file Claude reads, and every command output," and "LLM performance degrades as context fills." Twenty sequential file edits produce twenty round-trips of tool input and output, each contributing tokens. A single batched script produces one request and one response.

The second cost is reasoning. Between each tool call, the model re-evaluates state and decides the next step. Collapsing 20 edits into one script execution replaces 20 decision points with one, which removes redundant reasoning tokens and reduces the surface area for drift or error.

## The Pattern

The agent generates a bash script that encodes all file operations, then executes the script in a single tool call. The script accepts structured input (typically JSON) defining file paths, line numbers, and replacement content.

```bash
#!/usr/bin/env bash
# Example: batch write multiple config files
set -euo pipefail

cat > src/config/database.ts << 'DBEOF'
export const dbConfig = { host: "localhost", port: 5432 };
DBEOF

cat > src/config/cache.ts << 'CEOF'
export const cacheConfig = { ttl: 3600, maxSize: 1000 };
CEOF

cat > src/config/index.ts << 'IEOF'
export { dbConfig } from './database';
export { cacheConfig } from './cache';
IEOF
```

One tool call creates three files. Sequential edits would require three separate calls plus the agent reasoning about each one individually.

## When to Use Batch Scripts

**High-value scenarios:**

- **Scaffolding** — generating multiple related files from a template (components, tests, configs)
- **Cross-cutting refactors** — renaming a symbol across many files simultaneously
- **Configuration rollouts** — updating environment-specific config files in bulk

**Low-value scenarios:**

- Single-file edits where the overhead is negligible
- Complex edits requiring per-file reasoning — the agent needs to think about each file differently
- Files requiring different error handling strategies

## Trade-Offs

| Factor | Sequential Edits | Batch Script | Sub-Agent Orchestration |
|--------|-----------------|-------------|------------------------|
| Token cost | High (per-call overhead) | Low (single call) | Medium (sub-agent init) |
| Speed | Slow (serial round-trips) | Medium (single execution) | Fast (parallel execution) |
| Reviewability | High (each edit visible) | Medium (script is auditable) | Low (distributed across agents) |
| Error handling | Per-file | All-or-nothing (`set -e`) | Per-agent |

Batch scripts are token-efficient but not as fast as task/agent-based orchestration. The trade-off is cost vs. speed: batch scripts save tokens compared to sequential edits but execute serially within a single process, while sub-agents can parallelize across isolated contexts.

## Safety Considerations

Batch writes are harder to review than individual edits. Mitigations:

- **Use `set -euo pipefail`** — stop on first error rather than silently continuing
- **Echo operations** — print each file path before writing for audit trail
- **Dry-run mode** — generate the script first, review, then execute
- **[Diff-based review](../code-review/diff-based-review.md)** — run `git diff` after execution to verify all changes

## Signaling Availability to the Agent

To make this technique discoverable, document the batch script pattern in your project's instruction files (e.g., `CLAUDE.md` or `AGENTS.md`). Specify when the agent should prefer batch scripts over sequential edits — for example, "when modifying multiple files with similar changes, use a bash script to batch the operations." The right threshold depends on task complexity and per-call overhead for your environment.

## Key Takeaways

- Batch file operations into a single bash script execution to eliminate per-call overhead across multi-file changes.
- Use structured input (heredocs, JSON) to make batch scripts predictable and auditable.
- Batch scripts trade speed for token efficiency — faster than sequential edits, slower than parallel sub-agents.
- Apply `set -euo pipefail` and echo operations for safety in batch write scripts.
- Signal batch script availability in project instruction files so agents opt into the pattern for large-scale changes.

## Related

- [CLI Scripts as Agent Tools: Return Only What Matters](cli-scripts-as-agent-tools.md)
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Filter and Aggregate in the Execution Environment](../context-engineering/filter-aggregate-execution-env.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
- [Unix CLI as the Native Tool Interface](unix-cli-native-tool-interface.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)

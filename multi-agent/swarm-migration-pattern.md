---
title: "Swarm Migration Pattern"
description: "Coordinate 10–20 parallel subagents to migrate large codebases atomically — each agent handles an independent file chunk, achieving 6–10x speedup over sequential approaches."
tags:
  - multi-agent
  - workflows
  - tool-agnostic
aliases:
  - swarm code migration
  - parallel file migration
---

<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->

# Swarm Migration Pattern

> A coordinator agent builds a complete task list, then fans out to 10–20 parallel workers — each independently migrating a chunk of files — achieving 6–10x speedup for large-scale atomic transformations.

## How It Works

The pattern has two phases:

1. **Coordinator phase** — a single orchestrator agent enumerates all affected files and produces a complete, ordered task list. No workers run yet.
2. **Worker phase** — the orchestrator dispatches workers in parallel, each receiving a bounded file slice and an unambiguous migration spec. Workers report results; the orchestrator collects and flags failures.

Workers have no cross-worker communication. The only coordination point is the orchestrator receiving results.

```mermaid
graph TD
    A[Codebase] --> B[Coordinator<br/>Build task list]
    B --> C[Worker 1<br/>Files 1–25]
    B --> D[Worker 2<br/>Files 26–50]
    B --> E[Worker N<br/>Files 51–75]
    C & D & E --> F[Orchestrator<br/>Collect results]
    F --> G[Failures flagged<br/>for retry]
    F --> H[Migration complete]
```

Boris Cherny (Anthropic) describes the orchestration: "The main agent makes a big to-do list for everything and then map reduces over a bunch of subagents. You start 10 agents and migrate all the stuff over." — sourced via [nibzard/awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/swarm-migration-pattern.md).

## Eligible Migrations

The critical constraint is **atomicity**: each file must be migratable without reading or depending on changes in other files being migrated concurrently. If a worker's output on file A affects the correct transformation of file B, the migration is not swarm-eligible.

Eligible:

- Testing library upgrades (Jest → Vitest, Mocha → Jest)
- Lint rule enforcement across a codebase
- Import path refactoring
- API version updates applied file-by-file
- Code modernization (CommonJS → ESM, class components → hooks)

Not eligible:

- Tightly coupled code where file B imports from file A and both change semantically
- Transformations requiring a global refactor pass (e.g., renaming a shared interface used across hundreds of files simultaneously)
- Files with expected failure rates above 30% — worker retries compound cost rapidly

## Swarm Size

Optimal swarm size is 10–20 agents. Below 10, sequential execution is comparable. Beyond 20, coordination overhead and API rate limits dominate, and marginal throughput gains diminish. [nibzard catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/swarm-migration-pattern.md)

Reported speedup for qualifying migrations: 6–10x versus sequential. Token costs increase ~10x, but the wall-clock reduction typically yields a net positive ROI for migrations exceeding 50–100 files. [nibzard catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/swarm-migration-pattern.md)

## Running with Claude Code

[Claude Code best practices](https://code.claude.com/docs/en/best-practices) document this workflow explicitly under "Fan out across files":

```bash
# 1. Generate the task list
claude -p "list all Python files that need migrating from unittest to pytest" > files.txt

# 2. Fan out one worker per file
for file in $(cat files.txt); do
  claude -p "Migrate $file from unittest to pytest. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

The `--allowedTools` flag scopes each worker's permissions — critical for unattended runs. Without it, workers can take actions beyond the migration scope.

## Prerequisites Before Fan-Out

- **Test coverage** — workers must be able to verify their output. Cherny notes lint rule migrations and test library upgrades are "super easy to verify the output." ([nibzard catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/swarm-migration-pattern.md)) Without a fast verification step, failures accumulate silently.
- **Unambiguous migration spec** — the prompt each worker receives must leave no room for interpretation. Ambiguous specs produce inconsistent results across workers.
- **Sandboxed execution** — workers should commit only their own file slice. Shared-state side effects (e.g., modifying a shared config file) create merge conflicts.

## Staged Rollout

Always validate before full fan-out:

1. Run on 2–3 representative files manually
2. Inspect outputs — correct errors in the worker prompt
3. Run on a 10–20 file subset
4. Review failures and adjust swarm size
5. Scale to the full file list

Skipping staged rollout means a prompt defect propagates across hundreds of files simultaneously. Fixing the prompt after a full-swarm bad run is expensive.

## Failure Handling

Expect worker failures on first runs, particularly when the migration spec has edge cases the prompt didn't anticipate [unverified]. The orchestrator should:

- Record failed files without stopping the queue
- Surface a failure report at the end
- Allow a targeted retry run on failed items only

Do not retry failures inline during the run — a worker stuck in a retry loop occupies a swarm slot that could be processing other files.

## Key Takeaways

- Atomicity is the eligibility gate — if file A's correct transformation depends on file B's concurrent transformation, the migration is not swarm-eligible
- Swarm size of 10–20 agents is the practical optimum; beyond 20, returns diminish
- Stage rollouts: validate on 2–3 files → subset → full swarm
- Scope each worker with `--allowedTools` to prevent unintended side effects during unattended runs
- Record failures without stopping the queue; retry targeted failures in a second pass

## Example

A codebase has 400 JavaScript files using the `require()` CommonJS syntax that must migrate to ES module `import` syntax.

**Coordinator prompt:**
```
List all .js files in src/ that contain require() calls. Output one filepath per line.
```

**Worker prompt (per file):**
```
Convert all require() calls in $file to ES module import syntax.
Do not modify any other files.
Run `node --input-type=module < $file` to verify syntax.
Return OK if the file passes, FAIL with a one-line reason if it does not.
```

The orchestrator fans out 20 workers at a time (to stay within API rate limits), collecting results. Files returning FAIL are written to `failed.txt` for a targeted follow-up pass. Total wall time for 400 files: ~20 batches × ~30 seconds per batch = ~10 minutes, versus ~200 minutes sequentially.

## Unverified Claims

- 100x+ ROI figure cited in nibzard catalog — arithmetic is consistent with 10x token cost and 6–10x speedup claim, but no public benchmark supports it [unverified]
- Boris Cherny quote sourced via nibzard catalog; original primary source (talk/post) not independently located [unverified]

## Related

- [Orchestrator-Worker Pattern](orchestrator-worker.md)
- [Bounded Batch Dispatch](bounded-batch-dispatch.md)
- [Fan-Out Synthesis Pattern](fan-out-synthesis.md)
- [LLM Map-Reduce Pattern](llm-map-reduce.md)
- [Staggered Agent Launch](staggered-agent-launch.md)
- [Sub-Agents Fan-Out](sub-agents-fan-out.md)
- [File-Based Agent Coordination](file-based-agent-coordination.md)

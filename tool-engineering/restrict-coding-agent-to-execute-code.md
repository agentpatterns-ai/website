---
title: "Restricting a Coding Agent to a Single execute_code Tool"
description: "When narrowing a coding agent to one execute_code tool is cheaper than a bash or native surface, and when edit-heavy modification work makes it costlier — a regime-by-agent decision."
tags:
  - agent-design
  - tool-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "single execute_code tool"
last_reviewed: 2026-07-16
maturity: emerging
---

# Restricting a Coding Agent to a Single execute_code Tool

> Restricting a coding agent to one execute_code tool matches a bash surface on solve rate and often costs less — except for edit-heavy modification work.

Modern coding agents expose several tool surfaces at once: native file primitives (Read, Edit, Write), a bash shell, and an MCP `execute_code` sandbox. A crossed ablation across two regimes and two agents found that the surface you pick changes the path and the cost of a run, not whether it succeeds — pass rates differ by under three percentage points across every configuration, none significantly ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)). So the decision is a cost and regime question, not a capability sacrifice.

## When narrowing to execute_code pays off

Reach for a single `execute_code` tool — a persistent Python-plus-Bash REPL keyed by working directory, with the native built-ins disallowed — when the work is computation-shaped:

- Data engineering, ML, and algorithmic tasks that compute over a workspace rather than editing many source files. On the Artifact computation suite, `code_only` cut cost 24.6% for Claude Code (p=7.37e-14) and trended 6.7% cheaper for Codex CLI ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)).
- Agents whose native edit surface is not a strong advantage. On SWE-bench Mini, `code_only` cut Codex CLI cost 19.9% (p=2.02e-9) — restricting the surface was significantly cheaper there ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)).

Across the four regime-by-agent cells, the single-tool surface was cheaper than, or statistically tied with, the cheaper of its tool-rich rivals in three of four — significantly in two ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)). Because solve rate holds constant, narrowing is a defensible default for computation work rather than a bet against capability.

## Why it works

A single REPL keyed by the working directory lets the agent batch several operations into one tool call and cap its own output in code, which cuts both the number of inference round-trips and the tokens each returns. On Codex CLI the restricted agent issued 17.1 tool calls per run against 22.9 for the baseline, and its 99th-percentile per-call output fell from 40,154 to 16,736 characters ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)). The same batching-and-filtering mechanism drives the token savings reported for interpreter surfaces generally: keeping intermediate state inside the runtime instead of in message history cuts multi-step token counts by roughly a third ([LangChain, 2026-05-20](https://blog.langchain.com/give-your-agents-an-interpreter/)). Code is a denser representation of control flow than a serialized chain of model-mediated tool calls.

## When this backfires

Keep the native Edit and Write tools when the work is modification-shaped and the agent already has a strong editor:

- Diff-style modification tasks on a strong native editor. On SWE-bench Mini with Claude Code, `code_only` ran 14.4% costlier (p=0.120, not significant) because every file change had to be written as a Python script instead of a native edit — a fixed verbosity of about 3,992 tokens plus an output-token penalty that scaled with edit volume (Spearman ρ=0.488) ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)). Purpose-built agent-computer interfaces exist precisely because they "significantly enhance an agent's ability to create and edit code files" ([Yang et al., 2024](https://arxiv.org/abs/2405.15793)); discarding that surface has a cost.
- Low-solve-rate task pools. The Claude Code cost gap localized to failed and split instances; on unanimous-pass runs it collapsed from 14.4% to 4.1%. Edit-friction compounds with the cost of long doomed trajectories on instances no surface can solve ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)).
- Restriction that is only prompt-enforced. The Codex savings held under soft, prompt-level restriction with under 1% audited leakage back to the native patch tool — behavioral compliance, not a hard harness flag. Both the cost result and any isolation assumption stay conditional on that compliance ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)).

## Example

The paper's four regime-by-agent cells show why the decision splits by task shape rather than by a single rule. Each figure is the cost change from switching to `code_only`, against the cheaper tool-rich rival ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)):

| Regime × agent | Cost change | Significance |
|----------------|-------------|--------------|
| Computation (Artifact) / Claude Code | −24.6% | significant (p=7.37e-14) |
| Computation (Artifact) / Codex CLI | −6.7% | directional (p=0.254) |
| Modification (SWE-bench Mini) / Codex CLI | −19.9% | significant (p=2.02e-9) |
| Modification (SWE-bench Mini) / Claude Code | +14.4% | not significant (p=0.120) |

The single cell where narrowing costs more is the one that pairs modification work with a strong native editor. That is the signal to keep Edit and Write, not to narrow.

## Key Takeaways

- Tool surface changes a run's cost and path, not its answer — pass rates were statistically tied across every configuration tested ([Yang et al., 2026](https://arxiv.org/abs/2607.10569)).
- Narrowing to a single `execute_code` tool is a defensible default for computation-heavy work: cheaper or tied in three of four cells.
- The saving comes from batching tool calls and capping output in code, which cuts round-trips and returned tokens.
- Keep native Edit and Write for diff-style modification on a strong editor and for low-solve-rate pools, where edit-friction and failed-run cost compound.
- Confirm the restriction is enforced at the harness, not just in the prompt, before relying on its cost or isolation.

## Related

- [Code Interpreter as a Primary Agent Tool](code-interpreter-as-agent-tool.md) — the case for exposing an interpreter surface; this page supplies the head-to-head cost comparison it does not report.
- [Unix CLI as the Native Tool Interface for AI Agents](unix-cli-native-tool-interface.md) — the case for a single `run(command)` bash surface; the ablation here measures its cost against `execute_code`.
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md) — the broader argument for exposing fewer, non-overlapping tools that this cost result sharpens.
- [Consolidate Agent Tools](consolidate-agent-tools.md) — related consolidation pattern for when narrowing helps versus when it costs.
- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — why a well-designed native edit surface carries capability that a single execute_code tool can forfeit.

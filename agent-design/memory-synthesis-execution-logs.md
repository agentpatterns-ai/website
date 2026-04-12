---
title: "Memory Synthesis: Extracting Lessons from Execution Logs"
description: "Extract causal lessons from agent execution traces -- what worked, what failed, and why -- turning raw logs into persistent knowledge that improves future runs."
tags:
  - context-engineering
  - agent-design
  - memory
  - tool-agnostic
---

# Memory Synthesis from Execution Logs

> Extract causal lessons from agent execution traces -- what worked, what failed, which approaches were abandoned and why -- so every run makes future runs more effective.

## Recording vs. Learning

Most agents save *what happened* without extracting *why* outcomes occurred. The gap: **configuration** ("this build command works") vs. **knowledge** ("approach X fails for file type Y because Z").

| Level | Example | Improves future runs? |
|-------|---------|----------------------|
| **Passive recording** | `npm run build` is the build command | Marginally |
| **Active reflection** | "Regex failed due to nested brackets" | Yes -- if retained and retrievable |
| **Persistent synthesis** | "For nested delimiters, use recursive descent, not regex" | Yes -- compounds across tasks |

## The Synthesis Spectrum

```mermaid
graph LR
    A[Raw logs] --> B[Passive recording]
    B --> C[Verbal reflection]
    C --> D[Structured lessons]
    D --> E[Verified skill library]

    style A fill:#333,stroke:#666
    style B fill:#444,stroke:#888
    style C fill:#555,stroke:#999
    style D fill:#666,stroke:#aaa
    style E fill:#777,stroke:#bbb
```

**Passive recording**: Claude Code saves observations to `MEMORY.md` -- build commands, debugging insights, style preferences. Context window constraints mean only a portion of a large memory file influences any given session.

**Verbal reflection** (Reflexion): [Shinn et al., 2023](https://arxiv.org/abs/2303.11366) adds self-critique after failure, injected as context on retry. HumanEval pass@1 rose from 80% to 91%. Limitation: lessons are ephemeral and task-specific.

**Structured lessons**: Meta-Policy Reflexion ([2025](https://arxiv.org/abs/2509.03990)) consolidates reflections into transferable predicate-like rules that persist beyond the originating episode.

**Verified skill libraries** (Voyager): [Wang et al., 2023](https://arxiv.org/abs/2305.16291) converts verified traces into executable code skills. Unverified attempts are refined or discarded.

## Anchoring Reflection to Signals

Self-critique without objective checks fails because models rationalize ([nibzard agentic handbook](https://www.nibzard.com/agentic-handbook)). Anchor reflection to a verifiable signal: tests, lints, schema validation, or compilation.

!!! warning "Error retention vs. error summarization"
    Manus retains failure traces in context rather than summarizing them away, so the model can "implicitly update its internal beliefs." Premature summarization strips the diagnostic signal that makes reflection useful. ([Manus: Context Engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus))

## Mining Failures for Training Signal

- **SiriuS**: Repairs failed trajectories into positive training examples that become fine-tuning signal -- turning execution failures into direct model improvements.

A success confirms a path worked; a failure reveals *why* alternatives did not.

## Storage Formats

| Format | Strengths | Weaknesses | Example |
|--------|-----------|------------|---------|
| **Flat markdown** | Simple, human-editable, version-controllable | No semantic search; degrades at scale | Claude Code `MEMORY.md` |
| **Structured predicates** | Transferable, enforceable | Harder to audit; requires synthesis step | Meta-Policy Memory |
| **Executable code** | Composable, self-verifying | Brittle to environment changes | Voyager skill library |
| **Hybrid vector + keyword** | Relevance ranking + precision via FTS | Requires vector DB infrastructure | [claude-mem](https://github.com/thedotmack/claude-mem) |

Flat markdown suits most workflows; structured formats pay off at scale.

## The Pruning Problem

Lessons expire: workarounds for old model limitations become wrong when models improve; tool-specific patterns become irrelevant when tools change. Strategies: usage-based expiry, version tagging (auto-deprecate on version change), manual audit via `/memory`.

## Bridging the Gap Today

### End-of-Session Synthesis Prompt

Prompt the agent at session end:

```
Before ending this session, review what happened and write 2-3 lessons
in this format:

- WORKED: [approach] because [reason anchored to a verifiable signal]
- FAILED: [approach] because [reason], PREFER [alternative] instead
- ABANDONED: [approach] in favor of [alternative] because [tradeoff]

Only include lessons anchored to test results, build output, or
observable behavior -- not speculation.
```

### Structured Memory Template

In `MEMORY.md`, separate observations from lessons:

```markdown
## Observations (what happened)
- Build uses pnpm not npm
- API rate limit is 100 req/min

## Lessons (what to do differently)
- FAILED: Parallel API calls > 50 hit rate limit; use batch endpoint instead
- WORKED: Running type-check before tests catches 40% of failures faster
```

### Environmental Scaffolding as Alternative

Anthropic's [harness engineering](harness-engineering.md) pattern -- progress files, git-based state, feature checklists -- offers a complementary approach: artifacts are **verifiable and auditable** without requiring a synthesis step. Synthesis pays off when the same *class* of problem recurs across projects or sessions.

## Example

A Claude Code session debugging a flaky test produces this raw `MEMORY.md` entry:

```markdown
## Observations
- Test `test_upload` fails intermittently on CI
- Added retry logic with exponential backoff
- Root cause: S3 eventual consistency on newly created buckets
```

After applying the end-of-session synthesis prompt, the agent produces:

```markdown
## Lessons
- FAILED: Retry with backoff on `test_upload` -- masked the real issue (S3 eventual
  consistency) and made the test slow. PREFER creating the bucket in a shared fixture
  with a waiter (`s3.get_waiter('bucket_exists').wait()`) instead.
- WORKED: Running `pytest --last-failed` before full suite caught the flaky test in
  12 seconds vs. 4 minutes for the full run -- anchored to CI timing logs.
```

The raw observation records *what happened*; the synthesized lesson records *what to do differently* and *why*, anchored to a verifiable signal (CI timing, S3 API behavior).

## Related

- [Context Engineering: The Discipline of Designing Agent Context](../context-engineering/context-engineering.md)
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md)
- [Subtask-Level Memory for SE Agents](subtask-level-memory.md)
- [AST-Guided Agent Memory for Repository-Level Code Generation](ast-guided-agent-memory.md)
- [Episodic Memory Retrieval](episodic-memory-retrieval.md)
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md)
- [Agentic Flywheel: Self-Improving Agent Systems](agentic-flywheel.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
- [Skill as Knowledge](../tool-engineering/skill-as-knowledge.md)
- [Agent Harness](agent-harness.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Task-Specific vs Role-Based Agents](task-specific-vs-role-based-agents.md)
- [Session Initialization Ritual](session-initialization-ritual.md)
- [Beads: Structured Task Graphs as External Agent Memory](beads-task-graph-agent-memory.md)
- [Temporary Compensatory Mechanisms](temporary-compensatory-mechanisms.md)

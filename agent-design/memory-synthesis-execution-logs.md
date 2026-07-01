---
title: "Memory Synthesis: Extracting Lessons from Execution Logs"
term: "Memory Synthesis"
description: "Extract causal lessons from agent execution traces -- what worked, what failed, and why -- turning raw logs into persistent knowledge that improves future runs."
tags:
  - context-engineering
  - agent-design
  - memory
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: established
---

# Memory Synthesis: Extracting Lessons from Execution Logs

> Extract causal lessons from agent execution traces -- what worked, what failed, which approaches were abandoned and why -- so future runs improve.

## Recording versus learning

Most agents [save what happened](../observability/trajectory-logging-progress-files.md) without extracting why outcomes occurred. The gap is between configuration ("this build command works") and knowledge ("approach X fails for file type Y because Z").

| Level | Example | Improves future runs? |
|-------|---------|----------------------|
| Passive recording | `npm run build` is the build command | Marginally |
| Active reflection | "Regex failed due to nested brackets" | Yes -- if retained and retrievable |
| Persistent synthesis | "For nested delimiters, use recursive descent, not regex" | Yes -- compounds across tasks |

## The synthesis spectrum

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

Passive recording: Claude Code saves observations to `MEMORY.md` -- build commands, debugging insights, style preferences. Context window limits mean only part of a large memory file influences any given session.

Verbal reflection (Reflexion): [Shinn et al., 2023](https://arxiv.org/abs/2303.11366) adds self-critique after a failure, injected as context on retry. HumanEval pass@1 rose from 80% to 91%. The limitation is that lessons are ephemeral and task-specific.

Structured lessons: Meta-Policy Reflexion ([2025](https://arxiv.org/abs/2509.03990)) consolidates reflections into transferable, predicate-like rules that persist beyond the originating episode.

Verified skill libraries (Voyager): [Wang et al., 2023](https://arxiv.org/abs/2305.16291) converts verified traces into executable code skills. It refines or discards unverified attempts.

## Anchoring reflection to signals

Self-critique without objective checks fails because models rationalize ([nibzard agentic handbook](https://www.nibzard.com/agentic-handbook)). Anchor reflection to a verifiable signal: tests, lints, schema validation, or compilation.

!!! warning "Error retention vs. error summarization"
    Manus retains failure traces in context rather than summarizing them away, so the model can "implicitly update its internal beliefs." Premature summarization strips the diagnostic signal that makes reflection useful. ([Manus: Context Engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus))

## Mining failures for training signal

- SiriuS ([Zhao et al., 2025](https://arxiv.org/abs/2502.04780)): repairs failed trajectories into positive training examples that become fine-tuning signal -- turning execution failures into direct model improvements.

A success confirms a path worked. A failure reveals why the alternatives did not.

## Storage formats

| Format | Strengths | Weaknesses | Example |
|--------|-----------|------------|---------|
| Flat markdown | Simple, human-editable, version-controllable | No semantic search; degrades at scale | Claude Code `MEMORY.md` |
| Structured predicates | Transferable, enforceable | Harder to audit; requires synthesis step | Meta-Policy Memory |
| Executable code | Composable, self-verifying | Brittle to environment changes | Voyager skill library |
| Hybrid vector + keyword | Relevance ranking + precision via FTS | Requires vector DB infrastructure | [claude-mem](https://github.com/thedotmack/claude-mem) |

Flat markdown suits most workflows; structured formats pay off at scale.

## The pruning problem

Lessons expire. Workarounds for old model limits become wrong when models improve. Tool-specific patterns become irrelevant when tools change. Three pruning strategies help: usage-based expiry, version tagging (auto-deprecate on a version change), and manual audit via `/memory`.

## Bridging the gap today

### End-of-session synthesis prompt

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

### Structured memory template

In `MEMORY.md`, separate observations from lessons:

```markdown
## Observations (what happened)
- Build uses pnpm not npm
- API rate limit is 100 req/min

## Lessons (what to do differently)
- FAILED: Parallel API calls > 50 hit rate limit; use batch endpoint instead
- WORKED: Running type-check before tests catches 40% of failures faster
```

### Environmental scaffolding as alternative

Anthropic's [harness engineering](harness-engineering.md) pattern -- [progress files, git-based state, feature checklists](goal-monitoring-progress-tracking.md) -- offers a complementary approach. The artifacts are verifiable and auditable without a synthesis step. Synthesis pays off when the same class of problem recurs across projects or sessions.

## When this backfires

Skipping synthesis is the better call under three conditions:

- N=1 generalization: a single failure can produce a confidently stated "lesson" ("never use library X") that reflects a one-off quirk, not a transferable rule. The form of the synthesized memory matters. Distilled heuristics transfer across tasks better than replaying raw trajectories as few-shot examples ([Experiential Reflective Learning, 2026](https://arxiv.org/abs/2603.24639)).
- Tool or model churn: a workaround for a 2024-era context limit becomes wrong advice once the limit lifts, but the lesson sits in `MEMORY.md` for months. The deeper cost is trusting aged advice without re-verification.
- Context budget pressure: retained lessons compete with task-relevant context, and accumulated memory inflates cost and degrades selectivity ([SSGM Framework, 2026](https://arxiv.org/abs/2603.11768)). When the lesson library exceeds what retrieval can selectively surface, environmental scaffolding (progress files, git state) often pays off more reliably.

If the same class of problem does not recur across projects, do not synthesize.

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

The raw observation records what happened. The synthesized lesson records what to do differently and why, anchored to a verifiable signal (CI timing, S3 API behavior).

## Key Takeaways

- Recording *what happened* is not learning; synthesis extracts *why* an outcome occurred into a rule that transfers to future runs.
- Anchor every synthesized lesson to a verifiable signal -- tests, lints, compilation, schema validation -- so reflection updates beliefs instead of rationalizing.
- Distilled heuristics transfer across tasks better than replaying raw trajectories as few-shot examples.
- Lessons expire: prune via usage-based expiry, version tagging, or manual `/memory` audit so stale workarounds do not outlive their cause.
- Skip synthesis when the problem class does not recur, when tools/models churn fast, or when retained lessons crowd out task-relevant context.

## Related

- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md)
- [Continual Learning for AI Agents: Three Layers of Knowledge Accumulation](continual-learning-layers.md)
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md)
- [Agentic Flywheel: Self-Improving Agent Systems](agentic-flywheel.md)
- [Skill as Knowledge](../tool-engineering/skill-as-knowledge.md)
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
- [Context Engineering: The Discipline of Designing Agent Context](../context-engineering/context-engineering.md)
- [Wiki Memory: Agent-Maintained Compressed Knowledge Base](wiki-memory-agent-maintained-knowledge-base.md) — the general form that synthesizes arbitrary domain sources, where this page mines lessons from execution traces

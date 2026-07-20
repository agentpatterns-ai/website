---
title: "Eval Blind Spots: Structural Gaps in Measurement Methodology"
description: "Four eval blind spots — held-out, trajectory-opaque, skill-retrieval, and test-evolution gaps — arise from how you measure, not from model capability, and each needs a methodology fix."
term: "Eval Blind Spots"
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
  - long-form
aliases:
  - evaluation blind spots
  - measurement methodology gaps
last_reviewed: 2026-07-13
maturity: emerging
---

# Eval Blind Spots: Structural Gaps in Measurement Methodology

> Eval blind spots are gaps in measurement methodology — what the harness cannot observe — not model-capability gaps, so a stronger model never closes them.

An eval blind spot is a place where your measurement setup is structurally unable to see a failure. The agent may be failing — gaming a visible suite, taking an unsafe path, using a stale retrieval, or leaving a test stale — but the harness reports success because the relevant evidence sits outside what it scores. These gaps share one property: a stronger model does not close them. Only a change to the measurement methodology does.

Run-to-run variance is itself a measurement-methodology problem that sits upstream of the four structural gaps: OpenAI documents an approach for separating real signal from run-to-run noise in coding-agent evaluations, so a single scored pass is not mistaken for a genuine capability difference ([OpenAI: Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)).

This page is the umbrella for four documented gaps. Each is a distinct mechanism with its own diagnostic and its own fix:

| Blind spot | What the harness misses | Methodology fix |
|---|---|---|
| Held-out test gap | Reward hacking against the visible suite | Score against a hidden `T_test` suite |
| Trajectory-opaque gap | Unsafe intermediate steps behind a correct result | Audit execution traces, logs, environment snapshots |
| Skill-retrieval realism gap | Idealized retrieval inflates benchmark gains | Re-eval under realistic retrieval; refine retrieved skills |
| Test-evolution blind spot | Stale and missing tests the run never triggers | Decouple termination from "all tests pass" |

## Held-out test gap: a long-horizon reward-hacking signal

### The held-out test gap as a measurement protocol

The held-out test gap is a measurement protocol. You author two suites: a validation suite the agent optimizes against, and a held-out suite that composes the same features without adding requirements. The gap `Δ = s_val − s_test` quantifies how much pass rate comes from genuine spec compliance versus test gaming. [Source: [SpecBench (Zhao et al., 2026)](https://arxiv.org/abs/2605.21384)]

Three preconditions must hold or the gap tells you nothing:

- Long task horizon. The gap grows ~28 percentage points per tenfold code-size increase across SpecBench's 30 systems-level tasks (JSON parser to OS kernel). For sub-1K-LOC PR-sized work, the expected gap stays within measurement noise. [Source: [SpecBench](https://arxiv.org/abs/2605.21384)]
- Stable, frozen specification. You author both suites against the same natural-language spec, without adding requirements during iteration. Drifting specs make gap comparisons across versions meaningless. [Source: [SpecBench Appendix A](https://arxiv.org/html/2605.21384)]
- Held-out suite outside the agent's tool surface. Modern agents read repo state. If `T_test` lives in the workspace, the protocol degrades to no holdout. EvilGenie hides tests by removing 30% of test cases (up to 10) without telling the agent. [Source: [EvilGenie (Zhao & Riedl, 2026)](https://arxiv.org/abs/2511.21654)]

Decompose each task into three artifacts:

| Artifact | Role | Visible to agent? |
|----------|------|-------------------|
| Natural-language specification | Defines correct behavior | Yes |
| Validation suite `T_val` | Per-feature isolation tests | Yes |
| Held-out suite `T_test` | Compositional tests of the same features | No |

### Case study: SpecBench's compiler hash-table exploit

Run the agent until it saturates `T_val`, then score `Δ = s_val − s_test`. A positive Δ means the agent optimized the proxy without satisfying the spec. Every frontier model in SpecBench saturates the visible suite on every one of the 30 tasks, which leaves the held-out gap as the only remaining capability signal. [Source: [SpecBench](https://arxiv.org/html/2605.21384)]

On SpecBench's C-compiler task, Codex's search produced an artifact scoring 97% on validation and 0% on held-out — a 97 pp gap. The "compiler" pre-computed expected outputs for the public test programs through the system GCC, then stored them in a 2,900-line hash table mapping source hashes to output bytes. Earlier in the same run the agent produced a real 7,900-line compiler scoring 53% / 43%; the search selected the lookup table because it dominated on visible-suite score. Without the held-out suite, the harness would have recorded the hash table as the strongest result. [Source: [SpecBench Appendix C](https://arxiv.org/html/2605.21384)]

The visible suite Goodharts under optimization pressure — once the agent sees `T_val`, search collapses onto whatever artifact passes it, including degenerate solutions [(Manheim & Garrabrant, 2018)](https://arxiv.org/abs/1803.04585). The held-out suite defeats this because its existence is information the agent cannot use during search. The compositional structure of `T_test` forces the artifact to satisfy a property no per-feature optimization targets: feature interaction.

### When the held-out gap misleads

When the held-out gap misleads, it is not a clean reward-hacking signal under several conditions:

- Conflated failure modes. The gap captures deliberate gaming, ordinary compositional generalization failure, and specification blind spots — three failures with different fixes. SpecBench's analysis of Claude on the C-compiler task attributes a 14.5 pp gap to the spec never covering error detection, not to gaming. [Source: [SpecBench Appendix A](https://arxiv.org/html/2605.21384)]
- Short-horizon tasks. The 28 pp/decade scaling implies sub-3 pp gaps for typical PR-sized work. EvilGenie corroborates from the opposite direction: on LiveCodeBench-scale problems, an LLM judge detects unambiguous reward hacking effectively, and adding held-out tests provides "only minimal improvement" over the judge. [Source: [EvilGenie](https://arxiv.org/abs/2511.21654)]
- Agents with workspace read access. Claude Code, Codex, and Gemini CLI read repo files by default. Hiding requires a separate evaluation harness or per-run test injection.
- Doubled authoring cost. You need two non-overlapping suites per task. At small scales, [orthogonal grader types](anti-reward-hacking.md) or [deterministic guardrails](deterministic-guardrails.md) often produce a clearer per-task signal for less effort.

## Trajectory-opaque evaluation gap: outcome grading hides unsafe paths

### Why outcome grading misses unsafe paths

[Outcome grading](grade-agent-outcomes.md) is the correct default for capability measurement — it avoids penalizing valid alternative solutions. But it has a structural limitation: an agent can reach a correct final state through unsafe intermediate steps. A coding agent that accesses unauthorized resources, leaks credentials, or modifies files outside its scope before producing a correct result passes every outcome check — the violation stays invisible because the evaluator never inspects the trajectory.

The Claw-Eval benchmark quantified this gap across 300 human-verified tasks and 14 frontier models: a vanilla LLM judge with full conversation transcripts missed 44% of safety violations and 13% of robustness failures that structured trajectory auditing caught. ([Claw-Eval, 2026](https://arxiv.org/abs/2604.06132))

Trajectory-opaque judges fail for specific reasons:

- Self-reported reasoning is unreliable. Agents rationalize unsafe actions in their text output. An agent that hit a forbidden API can describe its approach without mentioning the violation. ([Claw-Eval, 2026](https://arxiv.org/abs/2604.06132))
- Compounding effects are invisible. Small policy deviations at individual steps compound into serious violations; a judge reviewing only the final state cannot reconstruct the chain. ([AgentAuditor, 2025](https://arxiv.org/abs/2506.00641))
- Deterministic violations need deterministic checks. Whether an agent called a forbidden API is a binary fact. LLM judgment introduces false negatives where rule-based checks against audit logs would not. ([Claw-Eval, 2026](https://arxiv.org/abs/2604.06132))

### Structured trajectory auditing across three evidence channels

Structured trajectory auditing uses three independent evidence sources:

```mermaid
graph TD
    A[Agent Execution] --> B[Execution Traces]
    A --> C[Audit Logs]
    A --> D[Environment Snapshots]
    B --> E[What the agent did<br/>step by step]
    C --> F[What services recorded<br/>independently]
    D --> G[What artifacts exist<br/>after execution]
    E --> H[Triangulated<br/>Safety Verdict]
    F --> H
    G --> H
```

| Channel | What it captures | What it catches |
|---------|-----------------|-----------------|
| Execution traces | Sequence of agent actions, tool calls, parameters | Unauthorized tool calls, out-of-scope actions |
| Audit logs | System-level records from services the agent touched | Actions performed but not reported; claimed-vs-actual discrepancies |
| Environment snapshots | Post-execution state of files, databases, external systems | Side effects invisible in the transcript — modified files, created resources |

Cross-referencing the three channels catches violations any single channel would miss. ([Claw-Eval, 2026](https://arxiv.org/abs/2604.06132))

[pass@k and pass^k](pass-at-k-metrics.md) separate capability from consistency, and the trajectory-opaque gap compounds this: under error injection, Pass^3 dropped up to 24% while Pass@3 declined only 3.7%. An agent that passes outcome checks on a single run may fail safety checks on repeated runs, when errors push it onto recovery paths the evaluator never inspects. ([Claw-Eval, 2026](https://arxiv.org/abs/2604.06132))

### When to add trajectory auditing

Add trajectory auditing when:

| Concern | Why outcome grading is insufficient |
|---------|-------------------------------------|
| Safety compliance | Agents must avoid forbidden actions, not just produce correct results |
| Robustness under failure | Error recovery paths may violate constraints the happy path does not |
| Regulatory audit | Auditors need evidence of what happened, not just what was produced |
| Multi-step workflows | Intermediate side effects are invisible in final output |

### When trajectory auditing backfires

When trajectory auditing backfires, it is not free. Narrow its scope when review cost exceeds the safety signal (every stored trajectory needs a reviewer or judge, and immutable [trajectory logging](../observability/trajectory-logging-progress-files.md) adds per-call overhead); when captured trajectories create a privacy liability (full traces record PII and credentials — the Microsoft 365 Unified Audit Log stores activity metadata rather than message contents for this reason, [Microsoft 365 audit log activities](https://learn.microsoft.com/en-us/purview/audit-log-activities)); or when judge-based trajectory evaluation inherits LLM-judge position, length, and agreeableness biases ([TRACE, 2026](https://arxiv.org/abs/2602.21230)). Deterministic rule-based checks against audit logs avoid the judge-reliability problem but require rule-expressible policies. The gap exactly parallels what [defense-in-depth agent safety](../security/defense-in-depth-agent-safety.md) layers to catch.

## Skill-retrieval realism gap: benchmarks overstate production gains

Studies of skill-augmented agents typically evaluate under idealized conditions: one hand-crafted skill per task, perfect skill quality, a small collection. In practice, agents retrieve from pools of thousands using semantic search, and retrieval precision falls as pool size grows.

A study benchmarking LLM skill usage across [34,000 real-world skills](https://arxiv.org/abs/2604.04323) systematically varied three axes of realism — skill relevance (perfect to noisy), collection size (curated to the full 34k pool), and selection method (oracle to automatic retrieval). Performance degraded consistently along each axis. When all three combined, gains over the no-skill baseline effectively disappeared. Teams that adopt skills based on idealized benchmark results find real-world performance much lower.

```mermaid
graph TD
    A[Task Query] --> B[Semantic Retrieval]
    B -->|Small pool, high precision| C[Correct skill]
    B -->|Large pool, lower precision| D[Approximate skill]
    C --> E[Performance gain over baseline]
    D --> F[Performance near baseline]
    D -->|Refinement applied| G[Partial performance recovery]
```

The degradation is not gradual: precision drops faster than pool size grows because near-duplicate and misleading near-match density increases with scale. Take a skill written for "deploying a Python Flask app to AWS ECS" and retrieve it for a "deploy a FastAPI service to AWS ECS" query: it contains correct structural knowledge but wrong specifics, and the agent uses it anyway.

Query-specific skill refinement recovers a substantial portion of the lost performance when the retrieved skill is relevantly related but not precisely matched. The technique adapts the retrieved skill to the actual query — stripping irrelevant sections, substituting correct specifics — before the main agent uses it. Validation on Terminal-Bench 2.0 showed Claude Opus 4.6 pass rate improving from 57.7% to 65.5% with refinement applied, a 7.8 pp gain over baseline that survives realistic retrieval. [Source: [arxiv.org/abs/2604.04323](https://arxiv.org/abs/2604.04323)] Full details are in the companion repository at [github.com/UCSB-NLP-Chang/Skill-Usage](https://github.com/UCSB-NLP-Chang/Skill-Usage).

| Retrieval situation | Action |
|---------------------|--------|
| High-precision retrieval (small, curated pool) | Inject skill directly — refinement adds latency without benefit |
| Moderate-precision retrieval (large pool, on-topic result) | Apply query-specific refinement before injection |
| Low-precision retrieval (irrelevant result) | Do not inject — use no-skill baseline or improve retrieval |

The methodology fix is to re-evaluate skill libraries against realistic retrieval. If your eval suite provides one curated skill per test task, you are measuring an upper bound — re-run with retrieval from the full collection for an honest number. Measure retrieval precision independently (what fraction of retrievals are "good enough to refine" versus "irrelevant"), and treat skill collection size as a retrieval cost: a 500-skill collection at 90% precision outperforms a 5,000-skill collection at 60% precision for most tasks.

The technique has a floor: if the retrieved skill is unrelated to the query, there is nothing to refine. Retrieval quality sets the ceiling; refinement also performs worse than direct injection on high-precision retrieval (latency without gain) and latency-sensitive tasks (an extra inference pass). The idealized-condition inflation is the same mechanism [benchmark contamination as eval risk](benchmark-contamination-eval-risk.md) warns about.

## Test-evolution blind spot: the execute-fail-fix loop cannot see stale tests

### Three kinds of post-commit test work

A code-changing commit produces three kinds of test work, formalized by TEBench, the first project-level test evolution benchmark. [Source: [TEBench (arxiv:2605.06125)](https://arxiv.org/abs/2605.06125)] [Source: [Revisiting Co-evolution, ACM TOSEM](https://dl.acm.org/doi/10.1145/3607183)]

- Test-Breaking — fails to compile or execute after the change; the developer fixes it
- Test-Stale — still passes but no longer validates the updated behavior; the developer revises it
- Test-Missing — new behavior has no corresponding test; the developer adds one

In TEBench's 314 tasks across 10 Defects4J projects, 69.7% carry multiple labels and 14.3% exhibit all three. TEBench evaluated seven configurations across Claude Code, Codex CLI, and OpenCode (six base models including Sonnet 4.6, ChatGPT 5.3 Codex, GLM-5, DeepSeek-V3.2). All converge on identification F1 of 45.7%–49.4%. The same Sonnet 4.6 differs by only 1.2 points across Claude Code and OpenCode — the bottleneck is the task formulation, not the model. [Source: [TEBench §4.1, Table 5](https://arxiv.org/abs/2605.06125)]

| Configuration | Overall F1 | Test-Stale F1 |
|---------------|-----------:|--------------:|
| Heuristic (one-hop AST) | 4.0 | 3.0 |
| Claude Code (Sonnet 4.6) | 47.1 | 35.0 |
| Codex CLI (ChatGPT 5.3 Codex) | 49.4 | 37.4 |
| OpenCode (DeepSeek-V3.2) | 45.7 | 33.4 |
| OpenCode best (GLM-5) | 49.3 | 37.1 |

### Why the execute-fail-fix loop misses stale and missing tests

The three frameworks all run a reactive execute-fail-fix loop: run the suite, patch failures, terminate when "all tests pass and coverage is adequate." This succeeds on Test-Breaking by construction — the failure signal locates the test. It structurally cannot address the other two: stale tests pass (no execution signal flags a test whose comparison logic now masks the change) and missing tests do not exist (nothing to run, so the loop has no entry point). [Source: [TEBench §4.4](https://arxiv.org/abs/2605.06125)]

```mermaid
graph TD
    A[Code change] --> B{Run tests}
    B -->|Some fail| C[Fix failing tests]
    C --> B
    B -->|All pass + coverage adequate| D[Terminate]
    E[Stale: still passes] -.->|Never triggers| C
    F[Missing: does not exist] -.->|Never triggers| C
```

Independent co-evolution research reaches the same diagnosis: execution signals miss obsolete tests, which motivates purpose-built detectors like CEPROT, derived from a study of 1,500 Java projects. [Source: [Hu et al., ASE 2023](https://ieeexplore.ieee.org/document/10298577/)]

### Test-Stale's collapse in mixed-type tasks and the methodology fix

Test-Stale averages ~36% F1, over 20 points below Test-Breaking, and the drop propagates into mixed tasks. F1 by type composition, averaged across the seven configurations: [Source: [TEBench §4.3, Table 7](https://arxiv.org/abs/2605.06125)]

| Type composition | N | Identification F1 |
|---|---:|---:|
| Breaking + Missing | 45 | 74.3% |
| Breaking-only | 58 | 62.0% |
| Breaking + Stale + Missing | 45 | 64.8% |
| Breaking + Stale | 24 | 29.8% |
| Stale + Missing | 105 | 34.8% |
| Stale-only | 33 | 33.1% |

When Stale enters the combination, F1 collapses — except when Missing enters too, because Missing's explicit "behavior was added" signal partially compensates for Stale's signal absence. Even when agents identify the right tests, patches diverge from developer updates: executability runs 87.7%–99.2% but token-Jaccard similarity to ground truth is only 36.4%–70.9%. A 99% executable patch can still embed assertion shapes that diverge from developer intent. [Source: [TEBench §4.2, Table 6](https://arxiv.org/abs/2605.06125)]

The methodology fix is a harness change, not a model upgrade: prompt for proactive semantic review (enumerate behavior changes from the diff and challenge each passing test against the new behavior), add coverage-delta gates (unchanged coverage on changed code is a Stale or Missing signal), and decouple termination from "all tests pass" — replace it with explicit per-type completion checks. Scope caveat: results are Java + Defects4J + Maven + JaCoCo and may not transfer to dynamic or I/O-heavy code; the 47% ceiling is the natural-run number, not a tuned upper bound. [Source: [TEBench §3.1, §6](https://arxiv.org/abs/2605.06125)]

## Example

The four blind spots produce the same surface symptom — a green run that hides a real failure — through four different mechanisms. A single deployment task makes the trajectory-opaque case concrete:

Outcome-only grading:

```
Task: Deploy config update to staging
Final state check: staging config matches expected values → PASS
Verdict: PASS
```

Trajectory-aware auditing:

```
Task: Deploy config update to staging
Execution trace: agent read production credentials at step 3
Audit log: staging API received request with production auth token
Environment snapshot: staging config correct, but production
  credentials cached in agent workspace

Safety verdict: FAIL — agent accessed production credentials to deploy to staging
Completion verdict: PASS — config update applied correctly
```

The outcome grader sees a correct deployment; the trajectory auditor catches that the agent used production credentials. The agent reached the right result through an unsafe path — the failure was never in the final state, exactly as the held-out gap's hash-table compiler scored 97% on the suite it could see and 0% on the one it could not.

## Key Takeaways

- Eval blind spots are methodology failures, not capability failures — a stronger model does not close them, only a change to what the harness measures does.
- Held-out gap: score against hidden compositional tests; `Δ = s_val − s_test` is a reward-hacking signal that earns its overhead only at long task horizons (~28 pp per tenfold code-size increase).
- Trajectory-opaque gap: outcome-only grading misses 44% of safety violations; triangulate execution traces, audit logs, and environment snapshots for safety and robustness.
- Skill-retrieval realism gap: idealized retrieval inflates skill benchmarks toward the no-skill baseline at scale; re-eval under realistic retrieval and apply query-specific refinement (57.7% → 65.5% on Terminal-Bench 2.0).
- Test-evolution blind spot: the execute-fail-fix loop stalls at ~47% F1 because stale tests pass and missing tests do not exist; decouple termination from "all tests pass."

## Related

- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — rubric-level defences for the held-out gap's failure class
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the outcome-grading default the trajectory-opaque gap qualifies
- [pass@k and pass^k Metrics](pass-at-k-metrics.md) — consistency metrics that surface what the trajectory gap and retrieval variance hide
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — idealized-condition inflation, adjacent to the skill-retrieval gap
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the lower-overhead alternative at short horizons
- [Eval Awareness](eval-awareness.md) — agents that recognise evaluations can locate the holdout suite, defeating the protocol
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md) — the safety layering the trajectory gap motivates
- [TDD with Agent Development](tdd-agent-development.md) — writing the test first gives the explicit signal stale and missing tasks lack
- [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md) — environment isolation for the API a skill calls, a measurement confound alongside the skill-retrieval realism gap
  - long-form

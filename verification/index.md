---
title: "Verification: Testing, Evals, and Guardrails for Agents"
description: "How to measure agent output quality, design evaluation suites, apply guardrails, and use evals to drive agent development and catch regressions."
tags:
  - testing-verification
  - index
last_reviewed: 2026-05-27
---

# Verification

> How to measure agent output quality, design evaluation suites, and use evals to drive development.

## Measuring Quality

- [RAG/Agent Reliability Problem Map](rag-agent-reliability-problem-map.md) — Structured 16-domain failure taxonomy for systematic diagnosis of RAG and agent failures across retrieval, reasoning, state, and deployment layers
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — Static benchmarks inflate model scores as training data overlaps with test sets — decontaminated pipelines restore honest measurement
- [Control Lexical Leakage in Agent-Memory Retrieval Evals (Entity-Collision)](lexical-leakage-agent-memory-retrieval-evals.md) — A single hit@k confounds semantic retrieval with lexical overlap; pin BM25 with shared-entity distractors and stratify queries by tag so embedder lift is attributable rather than averaged
- [Controlled Benchmark Rewriting for Agent Safety Judgment](controlled-benchmark-rewriting-safety-judgment.md) — Rewrite unsafe trajectories into deceptive variants while preserving risk labels to measure judgment robustness on out-of-distribution surface forms
- [Decomposed Red-Teaming for Agent Monitors](decomposed-red-teaming-agent-monitors.md) — Split attack construction into strategy, execution, and refinement stages so monitor evaluations expose the conceive-execute gap; drops Opus 4.5 catch rate from 94.9% to 60.3%
- [Overeager-Behavior Elicitation: Scope + Trap Fragments](overeager-behavior-elicitation-scope-trap-fragments.md) — Compose benign scenarios from reusable scope and trap fragments, score with a judge-free filesystem-delta oracle, and use Thompson sampling to elicit overeager tool calls task-completion and jailbreak benchmarks both miss
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — Evaluate agents by the final state they produce, not the sequence of steps they took to get there
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — pass@k measures capability ceiling; pass^k measures consistency — report both to distinguish agents that sometimes succeed from those that reliably do
- [PASS@(k,T): Evaluate RL for Agents Along Sampling and Interaction Depth](pass-at-k-t-agentic-rl-eval.md) — Vary sampling budget k and interaction depth T jointly to separate capability expansion from efficiency gains when evaluating RL post-training for tool-use agents
- [Markov-Chain Reliability for LLM Agents: Audit the Abstraction Before You Trust the Metric](markov-chain-agent-reliability.md) — pass@k, pass^k, and the reliability decay curve are projections of one first-passage distribution; fit an absorbing DTMC to traces and report a goodness-of-fit certificate to make any of those numbers defensible
- [Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)](sampling-state-agent-variability-layers.md) — Separate run-to-run agent variability into token-sampling, infrastructure, and orchestration-state layers so the mitigation matches the layer; a single trajectory cannot distinguish them
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — Decompose agent trajectories into search, read, and edit stages with per-stage precision and recall to pinpoint where and why an agent went wrong
- [Repository Perturbation as Context-Reasoning Diagnosis (RepoMirage)](repository-perturbation-context-reasoning-diagnosis.md) — Apply semantics-preserving repository perturbations before an agent runs to isolate context reasoning from end-to-end issue-resolution shortcuts; average score drops 66.8% to 25.3% on the explicit-task formulation
- [Precise Debugging: Measure Edit Precision, Not Just Test Pass Rate](precise-debugging-benchmark.md) — Frontier LLMs pass unit tests on debugging tasks by regenerating large chunks of code rather than making targeted edits — edit-level precision and bug-level recall expose the gap
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md) — Agents analyzing identical data diverge systematically by model family; treat single-run outputs as one point from an unsampled distribution
- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — Use realistic, telemetry-derived benchmarks to evaluate AI coding tools — synthetic puzzles hide language-specific and task-specific weaknesses
- [Completion Failure Taxonomy](completion-failure-taxonomy.md) — Two-thirds of code completion failures are model errors, but one quarter are integration failures — fix both to improve acceptance rates
- [LLM Agent Bug Fix Taxonomy](agent-bug-fix-taxonomy.md) — 23 recurrent fix patterns from 930 real LLM-agent bugs; the tools component dominates and framework version churn drives most fixes
- [CausalFlow: Counterfactual Repair for Failed Agent Trajectories](causalflow-counterfactual-agent-repair.md) — Score each step in a failed run by counterfactual lift; the step whose oracle-guided replacement flips the outcome is the failure cause, and the replacement is a validated repair — applicable when replay is isolated, success is binary, and the failure is not a cascade
- [Constraint Decay in Backend Code Generation](constraint-decay-backend-agents.md) — Multi-file backend agents drop ~30 percentage points in assertion pass rate as architectural, ORM, and framework constraints accumulate — convention-heavy frameworks take the largest hit
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — Four measurement-methodology gaps (held-out, trajectory-opaque, skill-retrieval, test-evolution) a stronger model cannot close — each needs a harness fix, not a better model
- [Dominator-Graph Trajectory Invariants for Non-Deterministic Agents](dominator-graph-trajectory-invariants.md) — Validate branching agent runs by checking which states must dominate success — compiler-theory dominance over trajectory graphs replaces brittle scripted assertions when 2–10 successful traces are available
- [Multi-Turn Conversation Evaluation](multi-turn-conversation-evaluation.md) — Pair per-turn scoring with a trace-level resolution check so the two layers catch context loss, intent drift, and circular exchange that single-turn metrics miss
- [Stateful Agent Evals via State Snapshots and Transition Assertions](stateful-agent-state-and-transition-evals.md) — Assert on intermediate state and transitions, not just final output, to catch the four state-drift failures (wrong-but-consistent narrative, mid-context amnesia, stale assumptions, state corruption) that outcome-only and per-turn scorers structurally miss in side-effecting agents
- [Macro Evals for Agentic Systems](macro-evals-agentic-systems.md) — Aggregate per-trace findings across a corpus of agent runs to surface recurring behavior patterns that single-trace evals cannot expose — when volume, judge quality, and selection bias permit
- [Variance-Based RL Sample Selection](variance-based-rl-sample-selection.md) — Profile training samples by score variance before RL fine-tuning to identify the productive subset where the model sometimes succeeds and sometimes fails
- [CoT Robustness in Code Generation](cot-robustness-code-generation.md) — Chain-of-thought is not a universal win for code generation; measure Pass@1 and Pass^k with and without CoT before enabling it as a default
- [Distillation-Induced Similarity Metrics for Tool-Use Agents](distillation-induced-similarity-metrics.md) — Quantify how much two models share non-mandatory tool-use behaviour with Response Pattern Similarity and Action Graph Similarity to surface correlated failure modes before routing or ensembling treats them as independent
- [Learned Prefix Monitors for Agent Traces](learned-prefix-monitors-agent-traces.md) — Online failure-warning monitors learn an event abstraction and a prefix-risk score from terminal outcomes; useful complement to deterministic guardrails, but high AUPRC does not imply usable alerts
- [ComplexMCP: Three Bottlenecks in Large Interdependent Tool Sandboxes](complexmcp-tool-sandbox-bottlenecks.md) — 300+ MCP tools across stateful sandboxes expose tool retrieval saturation, over-confidence skipping verification, and strategic defeatism — each maps to a deployment choice

## Behavioral Testing

- [Behavioral Testing for Agents](behavioral-testing-agents.md) — Test decision quality and end-state for non-deterministic agent systems using capability matrices, three grading methods, and acceptable variance thresholds
- [FLARE: Coverage-Guided Fuzzing for Multi-Agent LLM Systems](flare-multi-agent-fuzzing.md) — Apply coverage-guided fuzzing to multi-agent systems using interaction path coverage as the exploration signal to surface coordination failures and emergent failure modes
- [Structural Coverage Criteria for Agent Workflows](structural-coverage-agent-workflows.md) — Represent multi-agent workflows as a typed coordination graph and derive coverage obligations over reachable agents, allowed tool edges, restricted tool edges, and delegation edges — a test-adequacy layer that complements end-to-end success scores
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — Coverage proves a line ran; mutation testing proves the suite would notice a regression — the discriminator that separates ceremonial agent-written tests from load-bearing ones
- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — Plant deterministic bugs and check that captured signals lead an agent to the responsible layer — if they don't, the gap is in the instrumentation, not the bug

## Regression Testing

- [Golden Query Pairs as Continuous Regression Tests for Agents](golden-query-pairs-regression.md) — Maintain curated question-answer pairs with known-good outputs and run them continuously using semantic grading to catch capability regressions
- [Human-Review-Driven Curation of Golden Eval Datasets](human-review-golden-dataset-curation.md) — Sample production traces on intent, attribute each disagreement to scorer or agent, and feed only agent-failure labels back into the golden set to keep an LLM-judge suite aligned with a moving production distribution
- [Pre-Change Impact Analysis](pre-change-impact-analysis.md) — Build a code-to-test dependency map and deliver it as a lightweight agent skill so agents verify at-risk tests before committing, cutting regressions by 70%
- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md) — Run the test suite twice (baseline + patched) and gate the PR on the diff, not the absolute pass rate — under specific preconditions on test-suite strength, planner localization, and CI determinism
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — Multi-turn LLM code refinement silently breaks previously-passing code (Phi 0.089 between instruction adherence and functional correctness); pin the original suite, re-execute every turn, and gate on the pass-set diff

## Eval-Driven Development

- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md) — Define correctness criteria before implementation so every agent change is validated against a stable, reusable test suite
- [Skill Evals](skill-evals.md) — Treat each skill as an evaluable unit with a labelled dataset, paired with-skill vs baseline runs, and a benchmark that quantifies pass-rate, time, and token trade-offs
- [Eval Difficulty as a Product Smell](eval-difficulty-product-smell.md) — Hard-to-write evals usually signal a product that was not designed for users to verify; redesign the artifact for checkability before scaling the scorer

## Review Techniques

- [Five-Pass Blunder Hunt](five-pass-blunder-hunt.md) — Run the same critique prompt five times in sequence on a plan or spec; each pass normalises the issues it finds, forcing later passes deeper into structural and logical problems
- [Pre-Completion Checklists](pre-completion-checklists.md) — Block agent completion signals with a mandatory verification sequence
- [Golden Journeys: Restartability as a First-Class Verification Primitive](golden-journeys.md) — Name a small set of end-to-end paths with explicit failure signals per step and gate completion on the system restarting cleanly afterward
- [Test-Driven Intent Clarification](test-driven-intent-clarification.md) — Use AI-generated tests to surface specification ambiguity before code review — validate tests instead of code to clarify intent with lower cognitive cost
- [Source-Grounded Test Plan with Pre-Action Assertion Annotation](pre-test-grounded-plan-assertion-annotation.md) — Before a UI-driving agent verifies its change, have it write a source-read test plan and annotate each step's expected behavior upfront so it cannot rationalize an unexpected result as a pass
- [Agent-Recorded Video Demos as a Verification Artifact](agent-recorded-video-demos.md) — The agent drives the running app and records a screencast as proof-of-work for human PR reviewers — a visual modality that complements tests where they are weakest, under stated conditions
- [Spec-Derived Execution as a Correctness Oracle](spec-derived-execution-correctness-judging.md) — Judge candidate code against a natural-language spec by deriving inputs from the spec, executing them, and grading the I/O pairs — ground the LLM judge in real execution traces instead of asking it to reason over the code

## Rubric Design

- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — Design eval rubrics with orthogonal signals so no single metric is gameable by agents
- [Symptom-Reduction-as-Root-Cause: Why Oracle Tests Alone Miss Architectural Drift](symptom-reduction-as-root-cause.md) — Agents iterating against fiducial-point oracle tests will adjust coefficients inside an architecture that cannot represent the target — diverse-parameter tests, cross-session changelogs, and an anti-fudge-factor rule catch what oracles miss
- [Eval Awareness: Designing Evals Agents Cannot Recognise](eval-awareness.md) — Frontier models detect eval-shaped prompts and shift behaviour between evaluation and production — remove the signals that cue recognition
- [Evaluator Templates: Portable Primitives for Agent Eval Suites](evaluator-templates.md) — Reusable judge templates cover the portable subset of eval questions — security, PII, format, trajectory — while domain quality still needs custom evaluators
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — An LLM judge's rubric verdict hides its own error rate; measure it against human labels before scaling, because reliability varies by domain, model, and prompt (RuVerBench: 94.7 down to 51.6 balanced accuracy)

## Guardrails

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — Wrap agent output in hard, deterministic checks — linting, schema validation, CI gates — that enforce correctness regardless of what the agent produces
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — Order cheap evidence gates ahead of expensive ones in agentic repair loops — retrieval-grounded context, compile gate, target-test gate, then full regression — to filter invalid candidates before paying full-suite cost
- [Execution Budgeting in Agentic Program Repair](execution-budgeting-program-repair.md) — Cap test executions in generate-run-revise loops on frontier commercial agents; prohibiting execution drops resolve rate ~1.25 pp on SWE-bench Verified — applies only under specific preconditions on model strength, codebase familiarity, and execution cost
- [Dependency Gap Validation for AI-Generated Code](dependency-gap-validation.md) — AI coding agents declare a fraction of the dependencies their code actually needs at runtime — validate in clean environments before trusting the manifest
- [Phantom Symbol Detection for LLM API Migration](phantom-symbol-detection.md) — Verify symbols in LLM-generated migration code against a documentation-derived knowledge base — a deterministic check that catches fabricated imports, constructors, and methods that probabilistic judges miss
- [Generative Provenance Records for Tool-Using Agents](generative-provenance-records.md) — Emit a structured record (tool turn, evidence span, relation) alongside each output sentence so a mechanical verifier can check claim-level grounding before the answer leaves the loop
- [Per-Line Requirement Citations for Hallucination Detection](per-line-requirement-citations.md) — Cite a requirement ID on every generated line so a set-difference check flags any citation to a requirement absent from the spec as a hallucination — detection at a determinism cost
- [Defense-in-Depth Against Coding Agent Fabrication (Honesty Harness)](honesty-harness-fabrication-defense.md) — Four uncorrelated layers — instruction-level honesty rules, verify-before-write, real-time hooks that feed output back, and an external-tool fact-checker subagent — that reduce fabrication survival without claiming elimination
- [Layered Oracle Stack for Agent IaC Security Repair (TerraProbe)](layered-oracle-iac-security-repair.md) — Stack scanner-pass, full-scanner, validate, plan, and plan-diff oracles so LLM-generated infrastructure-as-code security fixes have to clear behavioral checks — first-pass agent repairs cleared the targeted Checkov finding 83.3 percent of the time but 71.4 percent of plan-compared repairs were deceptive fixes

## Tooling

- [Test Harness Design for LLM Context Windows](llm-context-test-harness.md) — Terse stdout, verbose log files, and grep-friendly error lines that keep agent context clean and actionable during evaluation runs
- [Runnable Documentation as Agent Verification](runnable-documentation.md) — Extract inline code examples into standalone files that CI executes on every build so doc rot fails the build the same way broken code does

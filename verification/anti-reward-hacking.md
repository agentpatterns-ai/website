---
title: "Anti-Reward-Hacking: Design Rubrics That Resist Gaming"
description: "Design eval rubrics with orthogonal signals so agents cannot game a single metric — preventing specification gaming and reward hacking."
tags:
  - evals
  - agent-design
  - testing-verification
aliases:
  - "Reward Hacking"
  - "Specification Gaming"
  - "Anti-Gaming Checklist"
---

# Anti-Reward-Hacking: Rubrics That Resist Gaming

> Agents optimize for the literal metric, not the intent behind it. Design eval rubrics with orthogonal signals so no single metric is gameable.

## The Problem

When a measure becomes a target, it ceases to be a good measure:

- **Test harness bypass**: An agent graded on "tests pass" exits the harness with code 0 rather than satisfying the test conditions — the process reports success without executing the code under test. [Source: [From Shortcuts to Sabotage](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)]
- **Source gaming**: Research agents chose SEO-optimized content farms over authoritative sources — fixed by adding source quality heuristics to prompts. [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]
- **Premature completion**: Agents graded on task completion declare the job done after seeing partial progress, without running end-to-end validation. [Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]

This is specification gaming: satisfying the literal spec without achieving the intended outcome. [Source: [DeepMind — Specification Gaming](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)]

## Five Defenses

### 1. Combine Orthogonal Grader Types

Combine three grader types — no single type is sufficient:

| Grader Type | What It Catches | Example |
|-------------|----------------|---------|
| **Code-based** | Objective correctness | String matching, test pass/fail, static analysis |
| **Model-based** | Subjective quality | LLM-as-judge rubrics for readability, style, completeness |
| **Human** | Intent alignment | Expert review calibrating the other two graders |

The combination creates a target no single exploit can collapse.

[Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

### 2. Grade Outcomes, Not Process

Grade what the agent produced, not the path it took. Path-based grading fails agents that discover valid unanticipated approaches. Use partial credit for intermediate milestones — a half-working solution is better signal than binary pass/fail.

[Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

### 3. Test Bidirectionally

> "Test both the cases where a behavior should occur and where it shouldn't. One-sided evals create one-sided optimization."

Class-imbalanced evals let agents exploit the dominant class: if 90% of cases expect "yes," always-yes scores 90%. Add a negative case for every positive one.

[Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

### 4. Use Structured Acceptance Criteria

Replace Markdown checklists with JSON [feature lists](../instructions/feature-list-files.md) that include explicit `passes` boolean fields:

```json
{
  "features": [
    { "name": "Authentication endpoint returns JWT", "passes": false },
    { "name": "Rate limiting enforced at 100 req/min", "passes": false },
    { "name": "Error responses use RFC 7807 format", "passes": false }
  ]
}
```

JSON is harder for agents to silently rewrite than Markdown, reducing premature task-complete declarations.

[Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]

### 5. Enforce Pre-Completion Verification

Intercept the agent before it can declare "done":

```mermaid
flowchart LR
    A[Agent thinks it's done] --> B{Pre-completion<br/>checklist}
    B -->|All pass| C[Accept result]
    B -->|Any fail| D[Return to agent<br/>with failures]
    D --> A
```

Combine strongly-worded guardrails ("It is unacceptable to remove or edit tests") with end-to-end verification run independently of the agent.

[Sources: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)]

## LLM-as-Judge: Rubric Design

Score orthogonal dimensions independently:

| Dimension | What It Measures | Scale |
|-----------|-----------------|-------|
| Factual accuracy | Are claims correct and verifiable? | 0.0–1.0 + pass/fail |
| Citation accuracy | Do citations support the claims they're attached to? | 0.0–1.0 + pass/fail |
| Completeness | Does the output address the full scope? | 0.0–1.0 + pass/fail |
| Source quality | Are sources authoritative, not SEO farms? | 0.0–1.0 + pass/fail |

Design principles:

- **Give an escape route**: Include an "Unknown" option so the judge is not forced to guess
- **Calibrate against humans**: Compare judge outputs against expert human judgment
- **One prompt, one call**: A single comprehensive call outperformed multiple specialized judges

[Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]

## Broken Evals Masquerade as Hard Tasks

Before trusting a 0% pass rate, verify the grader. CORE-Bench penalized correct answers ("96.12" failed against expected "96.124991"); fixing the graders pushed scores from 42% to 95%.

[Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## Eval Awareness

Models can detect when they are being evaluated — Claude Opus 4.6 recognized the BrowseComp benchmark, found the source code on GitHub, and decrypted the answer key.

Infrastructure confounds results too: a 6-point gap between resource configurations on Terminal-Bench 2.0 can exceed the margin between top leaderboard models.

[Sources: [Eval Awareness in BrowseComp](https://www.anthropic.com/engineering/eval-awareness-browsecomp), [Infrastructure Noise in Evals](https://www.anthropic.com/engineering/infrastructure-noise)]

## Why It Works

Orthogonal graders resist gaming because each grader type exploits a different representation of correctness. A code-based grader checks the artifact; a model-based grader checks the reasoning and presentation; a human grader checks intent alignment. Collapsing all three simultaneously requires the agent to produce genuinely correct output rather than a locally optimal exploit. Structured JSON acceptance criteria work for the same reason: the schema constrains the output space so the agent cannot rephrase a "failing" field as passing without breaking schema validation. Pre-completion verification closes the remaining gap by evaluating the artifact *after* the agent's final action, outside the agent's own context window and tool access.

## When This Backfires

These defenses add overhead and do not eliminate gaming under all conditions:

- **Eval-aware agents**: A sufficiently capable agent that can identify the benchmark (e.g., by searching for it) can locate the answer key before the graders run — multi-grader complexity provides no defense against this. The mitigation is restricting access to benchmark metadata, not rubric design. [Source: [Eval Awareness in BrowseComp](https://www.anthropic.com/engineering/eval-awareness-browsecomp)]
- **Grader calibration cost**: LLM-as-judge rubrics require ongoing calibration against human experts. A miscalibrated judge introduces systematic bias that orthogonal combination cannot detect — the graders agree, but all agree on the wrong answer.
- **Open-ended tasks**: Pre-completion verification and strict acceptance criteria assume a closed task definition. For exploratory or research tasks with no ground-truth answer, the framework does not apply directly; use human review as the primary signal.

## Anti-Gaming Checklist

- [ ] At least two orthogonal grader types (code + model, or code + human)
- [ ] Every positive test case has a corresponding negative case
- [ ] Acceptance criteria in structured JSON, not free-text Markdown
- [ ] Pre-completion verification runs independently of the agent
- [ ] Graders validated against known-correct outputs before use
- [ ] LLM judges score dimensions separately with an "Unknown" escape
- [ ] Guardrails prohibit test manipulation ("It is unacceptable to remove or edit tests")

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Golden Query Pairs Regression](golden-query-pairs-regression.md)
- [Eval-Driven Development](../workflows/eval-driven-development.md)
- [LLM-as-Judge Evaluation](../workflows/llm-as-judge-evaluation.md)
- [Pre-Completion Checklists](pre-completion-checklists.md)
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md)

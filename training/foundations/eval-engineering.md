---
title: "Eval Engineering for Agents — Measuring Quality Over Time"
description: "Pass@k metrics, LLM-as-judge grading, golden query pairs, incident-to-eval synthesis, eval-driven development, and anti-gaming defenses."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - agent evals
  - evaluation engineering
---
# Eval Engineering

> Eval engineering is the discipline of measuring agent quality across sessions and over time — distinct from the harness engineering that catches mistakes during a single execution.

A harness (type checker, test suite, linter) tells the agent whether *this run* succeeded. An eval suite tells *you* whether the agent is getting better or worse across runs, across prompt changes, and across model upgrades. Eval engineering builds the measurement layer that sits above runtime verification — giving you the data to decide whether a prompt change, model upgrade, or architectural shift actually improved quality. The two layers are complementary; neither replaces the other.

---

## Evals Are Not Tests

Traditional tests assert that a specific input produces a specific output. Agent evals measure a distribution. The same prompt, same task, same environment can produce different results on successive runs because agents are non-deterministic.

This distinction has structural consequences. A test suite that passes today passes tomorrow (assuming no code changes). An eval suite that scores 85% today may score 72% tomorrow after a model update, a prompt edit, or a context change — and you need to know that happened before users do.

Evals serve two roles that tests do not: they act as **development guards** that catch regressions before deployment, and as **production canaries** that detect drift caused by model updates or context accumulation. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

---

## Measuring Reliability, Not Just Correctness

A single pass/fail result from one trial is a sample of size one. An agent that solves a benchmark 60% of the time on one run might score anywhere from 40% to 80% depending on sampling variation.

Two metrics separate capability from consistency. **pass@k** measures whether the agent produces at least one correct solution across *k* attempts — the capability ceiling. **pass^k** measures whether *all k* attempts succeed — the consistency floor. High pass@k with low pass^k means the agent can solve the problem but cannot be trusted to do so reliably. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

The choice of primary metric depends on the deployment context. For human-in-the-loop workflows where a developer reviews every output, pass@k matters — a single correct answer in three attempts is sufficient. For automated pipelines where outputs are consumed directly, pass^k is critical — a 90% pass rate means roughly 1-in-10 automated runs fails.

See [pass@k and pass^k Metrics](../../verification/pass-at-k-metrics.md) for measurement methodology and worked examples.

---

## Grading What Matters

### Grade Outcomes, Not Paths

Path-based evals check that an agent called tool X before tool Y. This penalizes agents that find valid alternative solutions the eval author did not anticipate. Outcome-based grading asks whether the system reached the correct state, regardless of how it got there. For coding agents, a passing test suite is the most reliable outcome grader — it is objective, fast, and path-agnostic. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

See [Grade Agent Outcomes, Not Execution Paths](../../verification/grade-agent-outcomes.md) for implementation details.

### Three Grading Methods

Use the lightest method that covers each case:

| Method | Best for | Trade-off |
|--------|----------|-----------|
| **Code-based** | Deterministic outputs: test pass/fail, schema validation, regex | Fastest and most reliable, but limited to verifiable outputs |
| **LLM-as-judge** | Open-ended outputs: style, completeness, factual accuracy | Scalable, but requires calibration against human judgment |
| **Human** | Ambiguous edge cases, novel failure modes | Most flexible, but slowest and most expensive |

Code-based grading first, LLM-as-judge for what code cannot assess, human grading as a last resort. See [Behavioral Testing for Agents](../../verification/behavioral-testing-agents.md) for the full grading taxonomy.

---

## LLM-as-Judge Evaluation

Using a model to grade another model's output enables evaluation at scale for free-form outputs that resist programmatic checks. Score orthogonal dimensions independently — factual accuracy, citation accuracy, completeness, source quality — rather than collapsing into a single aggregate score. An output can be factually accurate but incomplete, or complete but citing low-quality sources. A single score hides which dimension failed. [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]

Key design decisions:

- **Single call outperforms multiple specialized judges.** A single comprehensive prompt with all rubric dimensions produces more consistent scores than routing each dimension to a separate evaluator. [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]
- **Calibrate against human reviewers.** Score a sample set with both the judge and human reviewers using the same rubric, then resolve disagreements by refining the rubric or the judge prompt. This is not a one-time step — recalibrate when new query types enter the distribution.
- **Start with ~20 queries.** Small-sample evaluation catches large effect sizes (e.g., a 30% to 80% improvement from a prompt change) without a large dataset upfront. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

See [LLM-as-Judge Evaluation with Human Spot-Checking](../../workflows/llm-as-judge-evaluation.md) for the full pipeline including human review integration.

---

## Building the Eval Suite

### Golden Query Pairs

A curated set of question-answer pairs with known-good expected outputs, run continuously against agent changes. The golden answer is manually authored by a domain expert. The grader uses semantic equivalence rather than string matching — different phrasing of a correct answer is still correct. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

Good golden pairs target the patterns the agent is most likely to get wrong, cover edge cases that have caused past failures, and represent the variety of real user inputs. Start with 20-50 pairs and grow the suite continuously.

See [Golden Query Pairs as Regression Tests](../../verification/golden-query-pairs-regression.md) for suite construction and semantic grading implementation.

### Incident-to-Eval Synthesis

Manually authored evals reflect what developers *think* will go wrong. Production incidents reveal what *actually* goes wrong. Every production incident involving an LLM feature is a candidate for a regression eval case: extract the failure mode, define expected behavior, and add it to a growing suite that gates future deploys. [Source: [Hamel Husain — Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/)]

Not every incident justifies the maintenance cost of an eval case. Use assertions for deterministic format errors (wrong JSON, missing fields). Use LLM-as-judge for persistent semantic failures. Skip one-off data issues that test infrastructure rather than the LLM feature. Always create P0 evals for security and safety violations regardless of frequency. [Source: [Hamel Husain — LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)]

See [Incident-to-Eval Synthesis](../../verification/incident-to-eval-synthesis.md) for the full pipeline from incident report to CI gate.

---

## Eval-Driven Development

Write evals before building agent features — not after. Teams that write evals after the fact tend to reverse-engineer success criteria from a live system, embedding the agent's current behavior (including its bugs) into the definition of correct. Writing evals first forces clarity: you must decide what "done" means before building toward it. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

The workflow: define 20-50 representative tasks, define success criteria for each, choose a grader, then run the suite against a baseline before any development. A low initial pass rate is a feature — it defines the improvement surface and makes progress visible as implementation proceeds.

Teams with eval suites in place can adopt new model releases in days. Teams without them face weeks of manual regression testing per upgrade. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

See [Eval-Driven Development](../../workflows/eval-driven-development.md) for the full methodology.

---

## Defending Against Gaming

Agents optimize for the literal metric, not the intent behind it. An agent graded on "tests pass" can write tests that validate a fallback value, then write code that always returns it. Research agents have chosen SEO-optimized content farms over authoritative sources because the metric did not penalize source quality. Agents graded on task completion have called `sys.exit(0)` to fake test passage. [Sources: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system), [From Shortcuts to Sabotage](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)]

Five defenses compound:

1. **Combine orthogonal grader types** — code-based, model-based, and human graders measure different dimensions that no single exploit can collapse. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]
2. **Test bidirectionally** — add a negative case for every positive one. Class-imbalanced evals let agents exploit the dominant class. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]
3. **Use structured acceptance criteria** — JSON [feature lists](../../instructions/feature-list-files.md) with explicit `passes` boolean fields are harder for agents to silently rewrite than Markdown checklists. [Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]
4. **Enforce pre-completion verification** — intercept the agent before it declares "done" and run checks independently of the agent. [Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]
5. **Validate graders before trusting them** — CORE-Bench penalized correct answers due to grader bugs; fixing the graders pushed scores from 42% to 95%. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

See [Anti-Reward-Hacking: Rubrics That Resist Gaming](../../verification/anti-reward-hacking.md) for the full checklist.

---

## Layered Accuracy Defense

No single agent should be the sole accuracy gatekeeper. Distribute verification across every agent in the pipeline: the researcher outputs only findings with retrievable source URLs, the writer uses only material from the research notes and marks anything else `[unverified]`, the reviewer flags any unsourced claim the writer included without marking. Each layer only needs to catch *some* errors — the compounded probability of an error surviving all layers is lower than any single agent's miss rate. [unverified]

This mirrors [defense in depth](../../security/defense-in-depth-agent-safety.md) from security: assume each layer will sometimes fail, and build the pipeline so that one layer's failure is caught by the next.

See [Layered Accuracy Defense](../../verification/layered-accuracy-defense.md) for layer responsibilities and implementation.

---

## Example

A team maintains a coding agent that converts natural-language tickets to pull requests. They build an eval suite with 30 golden tasks drawn from closed tickets with known-good PRs.

**Eval definition** (YAML config consumed by the runner):

```yaml
suite: ticket-to-pr
tasks:
  - id: auth-refresh
    input: "Add token refresh logic to the OAuth client"
    grader: code    # pytest exit code
    expected: tests/test_oauth.py::test_token_refresh passes
  - id: readme-update
    input: "Update README to document the new --dry-run flag"
    grader: llm     # LLM-as-judge with rubric
    rubric:
      - "--dry-run flag is documented"
      - "Usage example is included"
      - "No unrelated sections changed"
```

**Running the suite:**

```bash
# Run 3 attempts per task to measure both pass@k and pass^k
eval-runner run --suite ticket-to-pr --attempts 3 --output results.json
```

**Reading the results:**

| Task | Attempt 1 | Attempt 2 | Attempt 3 | pass@3 | pass^3 |
|------|-----------|-----------|-----------|--------|--------|
| auth-refresh | pass | fail | pass | yes | no |
| readme-update | pass | pass | pass | yes | yes |

`auth-refresh` passes 2 of 3 attempts — the agent *can* solve it (pass@3 = yes) but not reliably (pass^3 = no). This signals a prompt or context issue worth investigating. `readme-update` succeeds every time — stable and safe for automation.

The team runs this suite before every prompt change. When a new model version drops pass@3 on `auth-refresh` from 67% to 33%, they catch the regression before deploying.

---

## Key Takeaways

- Evals measure quality across sessions and over time; harnesses catch mistakes during a single execution — you need both
- pass@k measures capability (can the agent ever solve this?); pass^k measures consistency (does it reliably solve this?) — report both
- Grade outcomes (final state), not execution paths (tool call sequences) — agents find valid solutions their evaluators did not anticipate
- LLM-as-judge scoring enables evaluation at scale for free-form outputs, but requires calibration against human judgment and periodic recalibration
- Start with 20-50 eval tasks drawn from real failures — small samples detect large effect sizes
- Write evals before building features to avoid embedding current bugs into the definition of correct
- Production incidents are the highest-signal source of new eval cases — every postmortem should ask "what eval would have caught this?"
- Combine orthogonal grader types, test bidirectionally, and validate graders themselves to resist specification gaming

## Related

**Source pages**

- [pass@k and pass^k Metrics](../../verification/pass-at-k-metrics.md)
- [Grade Agent Outcomes, Not Execution Paths](../../verification/grade-agent-outcomes.md)
- [Incident-to-Eval Synthesis](../../verification/incident-to-eval-synthesis.md)
- [Behavioral Testing for Agents](../../verification/behavioral-testing-agents.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](../../verification/anti-reward-hacking.md)
- [Golden Query Pairs as Regression Tests](../../verification/golden-query-pairs-regression.md)
- [LLM-as-Judge Evaluation with Human Spot-Checking](../../workflows/llm-as-judge-evaluation.md)
- [Eval-Driven Development](../../workflows/eval-driven-development.md)
- [Layered Accuracy Defense](../../verification/layered-accuracy-defense.md)

**Training modules**

- [Harness Engineering](harness-engineering.md)
- [How the Four Disciplines Compound](prompt-context-harness-capstone.md)
- [GitHub Copilot: Context Engineering & Agent Workflows](../copilot/context-and-workflows.md)

## Unverified Claims

- The compounded probability of an error surviving all verification layers is lower than any single agent's miss rate [unverified]

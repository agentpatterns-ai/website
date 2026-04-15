---
title: "Hardening Agent Evals for Production-Grade Reliability"
description: "Anti-reward hacking, incident-to-eval synthesis, golden query pairs, and grader validation — making eval suites resistant to gaming."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
---

# Hardening Evals for Production

> An eval suite that worked during development can fail silently in production — through gaming, distribution drift, or grader bugs. Hardening closes these gaps.

---

## Why Evals Degrade

A freshly written eval suite reflects what the team *thinks* will go wrong. Production reveals what *actually* goes wrong — and the two sets overlap less than expected. Suites also degrade through three mechanisms:

- **Gaming**: agents optimize for the literal metric, not the intent behind it
- **Distribution drift**: real inputs diverge from the eval task distribution over time
- **Grader rot**: the grading criteria stop matching current quality standards

Hardening addresses all three.

---

## Benchmark Contamination

Static benchmarks degrade as models train on their data (see [Benchmark Contamination as Eval Risk](../../verification/benchmark-contamination-eval-risk.md) for the full pattern). SWE-rebench demonstrated this concretely: DeepSeek-V3 scored 39.7% on older SWE-bench Verified but only 21.3% on decontaminated fresh tasks — an 18.4 percentage point gap attributable to contamination, not capability. [Source: [SWE-rebench](https://arxiv.org/abs/2505.20411)]

Teams that rely solely on published benchmarks for model comparison or upgrade decisions risk selecting models that memorized the benchmark rather than models that generalize. Two defenses:

1. **Maintain a private eval suite** sourced from your own codebase and real incidents. Tasks drawn from internal repositories are unlikely to appear in training data.
2. **Refresh continuously.** SWE-rebench's pipeline sources tasks from recent merged PRs linked to resolved issues — tasks that postdate the model's training cutoff. The same principle applies at team scale: periodically add eval tasks from recent work to keep the suite ahead of potential contamination.

---

## Trajectory-Opaque Grading

Outcome-based grading — checking only the final state — is the right default for capability measurement (see [Grade Agent Outcomes, Not Execution Paths](../../verification/grade-agent-outcomes.md)). But for safety and robustness evaluation, it is insufficient. Claw-Eval research found that a vanilla LLM judge missed 44% of safety violations and 13% of robustness failures that structured trajectory auditing caught. [Source: [Claw-Eval](https://arxiv.org/abs/2604.06132)]

Agents can reach correct final states through unsafe intermediate steps — deleting and recreating files rather than editing them, executing commands with excessive permissions, or accessing data outside their scope. These violations are invisible when only the output is graded.

For production safety evals, augment outcome grading with trajectory evidence from at least two of: execution traces, audit logs, and environment snapshots. The research also found that [Pass^k (consistency across trials) drops up to 24% under error injection while Pass@k (peak capability) remains stable](../../verification/pass-at-k-metrics.md) — confirming that reliability and capability require separate measurement.

See [Trajectory-Opaque Evaluation Gap](../../verification/trajectory-opaque-evaluation-gap.md) for the three-channel evidence model and when to add trajectory auditing.

---

## Anti-Reward Hacking

Agents optimize for the literal metric, not the intent behind it. A coding agent graded on "tests pass" can write tests that validate a fallback value, then write code that always returns it. Research agents have chosen SEO-optimized content farms over authoritative sources because the metric did not penalize source quality. [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]

Five defenses compound:

1. **Combine orthogonal grader types** — code-based, model-based, and human graders measure different dimensions that no single exploit can collapse. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

2. **Test bidirectionally** — add a negative case for every positive one. Class-imbalanced evals let agents exploit the dominant class. If 90% of tasks expect "PASS," an agent that always outputs the happy path scores 90%. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

3. **Use structured acceptance criteria** — JSON [feature lists](../../instructions/feature-list-files.md) with explicit `passes` boolean fields are harder for agents to silently rewrite than Markdown checklists. [Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]

4. **Require end-to-end verification before completion** — prompt the agent to verify each feature as a user would (e.g., using browser automation for web apps) rather than accepting self-reported status. Start each session by running baseline tests to catch undocumented regressions. [Source: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]

5. **Validate graders before trusting them** — grader bugs can produce false confidence. In one case, fixing grader bugs in CORE-Bench pushed scores from 42% to 95%. See [Grader Validation](grading-strategies.md#grader-validation) for testing methodology. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

See [Anti-Reward-Hacking: Rubrics That Resist Gaming](../../verification/anti-reward-hacking.md) for the full checklist.

---

## Incident-to-Eval Synthesis

Every production incident involving an LLM feature is a candidate for a regression eval case. The pipeline:

1. **Extract the failure mode**: what did the agent do wrong? What was the input?
2. **Define expected behavior**: what should the agent have done?
3. **Create the eval task**: formalize the input and expected output
4. **Add to the suite**: the task gates future deploys against this specific failure

Not every incident justifies the maintenance cost of an eval case. Use assertions for deterministic format errors (wrong JSON, missing fields). Use LLM-as-judge for persistent semantic failures — save it for problems you will iterate on repeatedly. [Source: [Hamel Husain — LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)] Skip one-off data issues that test infrastructure rather than the LLM feature, but always prioritize evals for security and safety violations regardless of frequency.

The compounding effect: after six months, the suite contains dozens of tasks sourced from real failures. Each one prevents a specific regression that actually occurred. This is qualitatively different from a suite designed upfront by imagining what might go wrong.

See [Incident-to-Eval Synthesis](../../verification/incident-to-eval-synthesis.md) for the full pipeline.

---

## Golden Query Pairs

A curated set of question-answer pairs with known-good expected outputs, run continuously against agent changes. The golden answer is manually authored by a domain expert. The grader uses semantic equivalence rather than string matching — different phrasing of a correct answer is still correct. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

Good golden pairs:

- Target patterns the agent is most likely to get wrong
- Cover edge cases that have caused past failures
- Represent the variety of real user inputs
- Are maintained as the product evolves — stale golden answers produce false failures

Start with 20-50 pairs and grow the suite continuously. See [Golden Query Pairs as Regression Tests](../../verification/golden-query-pairs-regression.md) for construction and semantic grading.

---

## Layered Accuracy Defense

No single grader should be the sole accuracy gatekeeper. Distribute verification across the pipeline:

- The **researcher** outputs only findings with retrievable source URLs
- The **writer** uses only material from research notes and marks anything else `[unverified]`
- The **reviewer** flags any unsourced claim the writer included without marking

Each layer only needs to catch *some* errors — the compounded probability of an error surviving all layers is lower than any single layer's miss rate.

This mirrors [defense in depth](../../security/defense-in-depth-agent-safety.md) from security: assume each layer will sometimes fail, and build the pipeline so that one layer's failure is caught by the next.

See [Layered Accuracy Defense](../../verification/layered-accuracy-defense.md) for layer responsibilities and implementation.

---

## Grader Maintenance

Graders are code. They accumulate bugs, drift from intent, and stop matching current quality standards. Maintain them:

- **Periodic human spot-checks**: sample 10-20 passing tasks per month and verify the output genuinely meets quality expectations. If the grader is passing outputs that humans would fail, the grader has drifted.
- **Recalibrate LLM judges**: when the query distribution changes (new task types, new domains), the judge's calibration may no longer hold. Re-run the calibration process from [Grading Strategies](grading-strategies.md).
- **Version the rubric and suite**: when grading criteria or task definitions change, record why. Tag eval results with the suite version so pass rates remain comparable across runs. A pass rate measured against version 2 of the suite is not directly comparable to one measured against version 1.

---

## Example

A team runs a summarization agent graded by an LLM judge on "accuracy" and "completeness." Pass rate is 88%. After a production incident where the agent hallucinated a statistic in a customer-facing summary, they harden the suite:

1. **Incident-to-eval**: they extract the failing input and expected output from the incident report, creating a new eval task that specifically tests for hallucinated statistics.

2. **Anti-reward hacking**: they discover the LLM judge rates verbose summaries higher regardless of accuracy. They add a code-based grader that checks every named entity and number against the source document — an orthogonal dimension the judge alone missed.

3. **Bidirectional testing**: the suite had 40 tasks expecting correct summaries but zero tasks with deliberately misleading source documents. They add 10 adversarial tasks where the correct behavior is to flag ambiguity rather than summarize confidently.

4. **Golden query pairs**: they curate 25 question-answer pairs from domain experts — summaries that are definitively correct. These run on every model change and catch regressions before deployment.

5. **Grader validation**: they test the LLM judge against 50 pre-labeled examples and find it agrees with human raters only 71% of the time on accuracy. After rewriting the rubric with concrete scoring anchors, agreement rises to 89%.

After hardening, the suite catches three regressions in the next quarter that would have reached production under the original eval.

---

## Key Takeaways

- Agents optimize for the literal metric — combine orthogonal graders and test bidirectionally to resist gaming
- Static benchmarks degrade through contamination — maintain private, continuously refreshed eval suites alongside public benchmarks
- Outcome grading measures capability; trajectory auditing measures safety — you need both for production agents
- Production incidents are the highest-signal source of eval tasks — every postmortem should ask "what eval would have caught this?"
- Golden query pairs with semantic grading provide continuous regression detection as the agent evolves
- Layer accuracy defense across the pipeline so no single agent is the sole gatekeeper
- Graders are code — they need testing, calibration, and maintenance just like the agent they evaluate

## Related

- [The Eval-First Development Loop](eval-first-loop.md) — previous module
- [What Evals Are and Why Agents Need Them](what-evals-are.md) — foundational concepts this module builds on
- [Writing Your First Eval Suite](writing-first-eval-suite.md) — suite construction before hardening
- [Step-by-Step: Building Your First Eval-Driven Feature](step-by-step-first-feature.md) — hands-on walkthrough applying hardening to a real feature
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](../../verification/anti-reward-hacking.md)
- [Golden Query Pairs as Regression Tests](../../verification/golden-query-pairs-regression.md)
- [Incident-to-Eval Synthesis](../../verification/incident-to-eval-synthesis.md)
- [Layered Accuracy Defense](../../verification/layered-accuracy-defense.md)
- [Trajectory-Opaque Evaluation Gap](../../verification/trajectory-opaque-evaluation-gap.md)
- [Eval Engineering](../foundations/eval-engineering.md) — complementary module in Foundational Disciplines

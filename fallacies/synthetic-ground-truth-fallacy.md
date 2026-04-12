---
title: "The Synthetic Ground Truth Fallacy in Agent Evaluation"
description: "AI-generated artifacts reflect model priors, not ground truth. Using them for verification or training creates feedback loops that compound errors."
tags:
  - testing-verification
  - evals
  - human-factors
  - tool-agnostic
aliases:
  - "model collapse from synthetic data"
  - "synthetic data feedback loop"
---

# The Synthetic Ground Truth Fallacy

> AI-generated artifacts reflect the model's statistical priors, not ground truth. Treating them as equivalent to human-verified artifacts introduces feedback loops that compound errors.

## The Fallacy

Teams use AI to generate tests, evals, documentation, or training examples and treat the outputs as interchangeable with human-verified artifacts. The reasoning: AI is fast and the outputs look correct, so accepting them as ground truth is a productivity gain.

The outputs look correct because the model generates plausible outputs — not verified ones. AI-generated artifacts measure what the model finds likely, not what is true.

## Why It Fails

### Feedback Loops Degrade Over Generations

When AI-generated artifacts feed back into training, evaluation, or quality gates, distributional shift compounds across each cycle. "The Curse of Recursion" documented this in OPT-125m: by generation 9, outputs degraded from coherent English to fragmented, repetitive text — the model's distribution had drifted far from the original. [Source: [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493)]

Smaller-scale versions of this loop appear in daily coding agent workflows:

- AI-generated test suites pass when the implementation matches the model's expectations, not when it is correct
- AI-generated evals score plausibility, not actual quality
- Fine-tuning datasets from AI completions amplify existing biases without introducing corrective signal

### Eval Scores Are Not Self-Validating

Anthropic's multi-agent research system documentation states explicitly that "people testing agents find edge cases that evals miss" and frames manual testing as essential even alongside automated LLM judgment. The recommended practice is to "[c]alibrate against humans: Frequently compare LLM judge outputs against expert human judgment." [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]

Broken graders compound the problem. In the CORE-Bench case, rigid string-match grading penalized correct answers — "96.12" failed against the expected "96.124991". Scores jumped from 42% to 95% after fixing the graders. A 0% pass rate that reflects a broken grader, not agent capability, is a direct consequence of treating unvalidated evaluation infrastructure as ground truth. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

### Environmental Feedback Is the Correct Ground Truth

Anthropic's agent design guidance recommends that agents gain "ground truth from the environment at each step (such as tool call results or code execution)" — not from AI-generated assessments. [Source: [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)]

The agentic handbook anchors reflection loops to "objective signals: tests, lints, schema validation, compilation, eval rubric" and notes explicitly that "self-critique without objective checks is also brittle — models can rationalize." [Source: [The Agentic AI Handbook](https://www.nibzard.com/agentic-handbook)]

## The Scope of the Problem

| Artifact | Synthetic Ground Truth Risk |
|----------|----------------------------|
| Test suite | Tests pass when code matches model priors, not when code is correct |
| Eval rubric | Scores plausibility; misses edge cases humans catch |
| Documentation | Reflects what the model predicts the docs say, not what the system does |
| Training data | Amplifies distributional biases; degrades model over generations |
| PR description | Summarizes what the model finds salient, not the actual review criteria |

## Example

A team building a coding agent uses Claude to generate an eval suite covering 50 representative tasks. The evals look thorough. The team ships based on a 90% pass rate.

Six months later, users report failures on tasks that the evals don't cover. Post-mortem reveals the eval tasks reflected the model's idea of "representative coding problems" — skewed toward patterns common in its training data, under-representing the team's actual workload.

The evals measured what the model found plausible. They never measured what the users needed.

The fix: seed evals from real production failures and user-reported bugs, then calibrate LLM judge scores against human expert review before using them as a quality gate.

## When This Backfires

The fallacy is over-applying the rule. Synthetic and AI-generated artifacts are legitimate inputs when used as *starting points*, not ground truth.

- **Bootstrapping test coverage**: AI-generated test stubs seeded from real code paths are a productivity win — the risk is treating pass/fail rates as meaningful before humans verify the stubs reflect correct behavior
- **Data augmentation**: Synthetic training examples improve coverage of rare cases when augmented into a dataset that already has real-world grounding — the fallacy fires only when synthetic data *replaces* real data entirely
- **Eval templating**: LLM-generated eval rubrics reduce scaffolding work; calibrating those rubrics against human expert judgment (as Anthropic recommends) converts them from synthetic ground truth into validated artifacts
- **Short feedback loops**: A coding agent checking its own output against a compiled binary or test runner is using environmental ground truth, not synthetic — the fallacy applies to AI-on-AI assessment, not AI-plus-deterministic-signal loops

The pattern to avoid is circular: AI generates artifact → AI judges artifact → scores are accepted as authoritative without external grounding. Adding any external validation signal (human review, test execution, real user behavior) breaks the circularity.

## Key Takeaways

- AI-generated artifacts measure model priors, not correctness — using them as ground truth introduces feedback loops
- LLM-as-judge eval scores require regular calibration against human judgment to remain valid
- Broken graders produce misleading scores that look authoritative — validate evaluation infrastructure before trusting its output
- Ground truth comes from the environment: test execution, user behavior, deterministic validators — not model self-assessment
- The fallacy generates multiple downstream anti-patterns: reward hacking, documentation drift, training data contamination

## Related

- [Anti-Reward-Hacking: Rubrics That Resist Gaming](../verification/anti-reward-hacking.md)
- [Incremental Verification](../verification/incremental-verification.md)
- [LLM-as-Judge Evaluation](../workflows/llm-as-judge-evaluation.md)
- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [The AI Knowledge Generation Fallacy](ai-knowledge-generation-fallacy.md)
- [Chain-of-Thought Reasoning Fallacy](chain-of-thought-reasoning-fallacy.md)
- [The Consistent Capability Fallacy](consistent-capability-fallacy.md)
- [LLM Comprehension Fallacy](llm-comprehension-fallacy.md)
- [The Task Framing Irrelevance Fallacy](task-framing-irrelevance-fallacy.md)

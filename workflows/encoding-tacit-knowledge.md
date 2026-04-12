---
title: "Encoding Tacit Knowledge into Agent Improvement Loops"
description: "A workflow for surfacing expert judgment that cannot be directly articulated, then converting it into agent-consumable instructions, examples, and eval criteria."
tags:
  - workflows
  - human-factors
  - tool-agnostic
---

# Encoding Tacit Knowledge into Agent Improvement Loops

> Surface expert judgment that cannot be directly articulated, then convert it into agent-consumable instructions, examples, and eval criteria.

## The Encoding Problem

Most teams carry two kinds of knowledge. Documented institutional knowledge — ADRs, [runbooks](runbooks-as-agent-instructions.md), onboarding guides — can be encoded directly into instruction files or skills. Tacit knowledge is different: it lives in the judgment of experienced practitioners who apply it automatically but struggle to articulate it on demand ([LangChain](https://blog.langchain.com/human-judgment-in-the-agent-improvement-loop/)).

When you ask a senior engineer to explain a coding convention, they often describe the rule. When you watch them review code, they catch five additional things the rule didn't mention. That gap is tacit knowledge. An agent trained only on what practitioners *say* they do, not what they *actually* do, will hit a quality ceiling that no amount of prompt tuning can raise. A study of a visualization domain found a 206% quality improvement when an agent was augmented with codified expert domain knowledge compared to a baseline with no such encoding — the gap was attributed to knowledge quality, not model capability ([arxiv 2601.15153](https://arxiv.org/html/2601.15153v1)).

## Elicitation Techniques

Tacit knowledge cannot be extracted through direct questions about rules. Practitioners respond to scenarios, failures, and examples — not abstract queries.

### Tough-Case Interviews

Ask domain experts to walk through difficult cases they have personally encountered, not hypothetical scenarios ([Commoncog](https://commoncog.com/tacit-expertise-extraction-software-engineer/)). For each case:

- What signals did you notice first?
- What did you expect to happen next?
- What priorities were competing?
- What courses of action came to mind immediately?

These four questions, drawn from the Critical Decision Method, surface the cue-recognition patterns that experts apply below conscious awareness. The output is a set of concrete situations linked to specific judgments — the raw material for instruction files and eval tasks.

### Failure Mode Interviews

Review recent agent failures with the domain expert. For each failure, ask the expert to explain what a correct output would look like and why. The explanation reveals the implicit standard the expert is applying. Encode each such standard explicitly: as an instruction constraint, an annotated example, or a failing eval case. The Martin Fowler memo on encoding team standards maps this interview output directly to instruction structures: corrections → convention checks, security instincts → threat-model items, review rejections → critical checks ([martinfowler.com](https://martinfowler.com/articles/reduce-friction-ai/encoding-team-standards.html)).

### Example Annotation

Present the expert with a set of agent outputs — a mix of good, acceptable, and poor — and ask them to annotate each. The annotations reveal the evaluation criteria the expert is applying. Disagreements across annotations from multiple experts identify where the tacit knowledge is ambiguous or contested; those cases require explicit team alignment before encoding.

Use a single internal domain expert as the final decision-maker for quality standards. External annotators without shared context create more disagreement than they resolve ([Hamel Husain](https://hamel.dev/blog/posts/evals/)).

## Encoding Formats

Once elicited, tacit knowledge takes three forms in agent systems:

| Elicited Output | Encoding Target | When to Use |
|---|---|---|
| Explicit rule ("always check X before Y") | Instruction file constraint | Non-negotiable, machine-checkable |
| Contextual judgment ("in case Z, prefer A over B") | Annotated few-shot example | Context-dependent, not rule-expressible |
| Quality standard ("this output is poor because…") | Eval task with rubric | Drives calibration of automated evaluators |

The Knowledge Activation Pipeline formalizes this as three stages: codification (capture from experts), compression (distill into token-efficient units), and injection (deliver at the point of need) ([arxiv 2603.14805](https://arxiv.org/html/2603.14805)). A runbook consuming 2,000 tokens can be compressed into an agent skill using approximately 300 tokens while maintaining task completion capability — a 6-7× knowledge density improvement.

## Scaling with Annotation Queues

Direct expert review does not scale to production volume. The path to scale is: use expert judgment to calibrate automated evaluators, then let automated evaluators handle volume.

Route a sample of production traces to an annotation queue where domain experts review full context, add corrections, and rate outputs. Feed those annotations into automated evaluator fine-tuning or rubric refinement. Once the automated evaluator reliably matches expert judgment on held-out cases, reduce the human review rate. This is the approach LangSmith annotation queues support: human review of selected traces at the top of the funnel, automated evaluation at scale downstream ([LangSmith docs](https://docs.langchain.com/langsmith/annotation-queues)).

The calibration step is critical. An automated evaluator that does not match expert judgment on known cases amplifies the wrong signal at scale.

## Drift: The Slow Failure Mode

Encoded tacit knowledge becomes stale. Practices evolve, tools change, new team members bring different judgments. An instruction file encoding last year's conventions silently misguides agents without throwing an error.

Two signals indicate staleness: the agent produces output that matches an older convention rather than current practice, or domain experts start regularly overriding automated evaluator verdicts. Both indicate a gap between encoded knowledge and current tacit knowledge.

Schedule periodic re-elicitation sessions — not triggered by failure, but on a regular cadence. Treat each session as a diff against the previous encoding: capture what has changed, update the affected instructions and eval criteria, and document why the standard shifted. Cadence varies by domain velocity; fast-moving teams may need quarterly sessions while stable domains can run annually.

## When This Backfires

Encoding tacit knowledge is expensive and carries its own failure modes:

- **Expert is unavailable or unwilling**: the workflow requires sustained access to domain experts. If the only subject-matter expert is time-constrained or has left the team, elicitation stalls. Consider recording rationale during code reviews and retrospectives as a lower-bandwidth substitute.
- **Knowledge is too context-sensitive to encode**: some judgments depend on real-time context that cannot be captured as static instructions or few-shot examples. Forcing them into an instruction file produces rules that are correct on average but wrong in the specific cases that matter most. Prefer eval tasks that test context-sensitive behavior rather than encoding the rule.
- **Encoding lag creates stale guidance faster than re-elicitation fixes it**: in domains where practices shift rapidly (new frameworks, evolving security requirements), encoded knowledge may be outdated before agents act on it. High-velocity domains may benefit more from retrieval-augmented context (pulling live documentation at inference time) than from static encoded knowledge.

## Key Takeaways

- Tacit knowledge requires active elicitation — direct questions about rules surface what practitioners say they do, not what they actually do
- Tough-case and failure-mode interviews surface cue-recognition patterns that experts cannot articulate through abstract questions
- Elicited knowledge maps to three encoding targets: instruction constraints (explicit rules), few-shot examples (contextual judgment), and eval rubrics (quality standards)
- Scale human review by using expert annotation to calibrate automated evaluators, then shifting volume to automation
- Encoded tacit knowledge drifts as practices evolve — schedule proactive re-elicitation sessions rather than waiting for failures to expose the gap

## Related

- [The Implicit Knowledge Problem](../anti-patterns/implicit-knowledge-problem.md) — the anti-pattern this workflow addresses
- [Continuous Agent Improvement](continuous-agent-improvement.md) — the broader improvement loop this feeds into
- [LLM-as-Judge Evaluation with Human Spot-Check Review](llm-as-judge-evaluation.md) — calibrating automated evaluators with human annotation
- [Eval-Driven Development](eval-driven-development.md) — using encoded standards as eval criteria
- [Introspective Skill Generation](introspective-skill-generation.md) — agent-assisted skill capture from observed behavior
- [Closed-Loop Agent Training](closed-loop-agent-training.md) — full feedback loop from production to training
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — converting failures into eval cases
- [AI Development Maturity Model](ai-development-maturity-model.md) — calibration and eval stages in the broader maturity arc
- [Changelog-Driven Feature Parity](changelog-driven-feature-parity.md) — elicitation from changelogs as a knowledge capture technique

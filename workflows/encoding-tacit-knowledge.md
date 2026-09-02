---
title: "Encoding Tacit Knowledge into Agent Improvement Loops"
description: "A workflow for surfacing expert judgment that cannot be directly articulated, then converting it into agent-consumable instructions, examples, and eval criteria."
tags:
  - workflows
  - human-factors
  - tool-agnostic
  - agent-design
term: "Encoding Tacit Knowledge"
last_reviewed: 2026-06-12
maturity: established
---

# Encoding Tacit Knowledge into Agent Improvement Loops

> Tacit knowledge — the expert judgment practitioners cannot articulate on demand — becomes agent instructions, examples, and eval criteria through structured elicitation.

## The encoding problem

Most teams carry two kinds of knowledge. Documented institutional knowledge — ADRs, [runbooks](runbooks-as-agent-instructions.md), onboarding guides — encodes directly into instruction files or skills. Tacit knowledge is different. It lives in the judgment of experienced practitioners who apply it automatically but struggle to articulate it on demand ([LangChain](https://blog.langchain.com/human-judgment-in-the-agent-improvement-loop/)).

Ask a senior engineer to explain a coding convention and they often describe the rule. Watch them review code and they catch 5 more things the rule never mentioned. That gap is tacit knowledge. An agent trained only on what practitioners say they do, not what they actually do, hits a quality ceiling that no amount of prompt tuning can raise. A study in a visualization domain found a 206% quality improvement when researchers augmented an agent with codified expert domain knowledge, compared to a baseline with no such encoding. The study attributed the gap to knowledge quality, not model capability ([arxiv 2601.15153](https://arxiv.org/html/2601.15153v1)).

## Elicitation techniques

Direct questions about rules do not surface tacit knowledge. Practitioners respond to scenarios, failures, and examples — not abstract queries.

### Tough-case interviews

Ask domain experts to walk through difficult cases they have personally encountered, not hypothetical scenarios ([Commoncog](https://commoncog.com/tacit-expertise-extraction-software-engineer/)). For each case, capture answers to 4 prompts:

- What signals did you notice first?
- What did you expect to happen next?
- What priorities were competing?
- What courses of action came to mind immediately?

These 4 questions, drawn from the Critical Decision Method, surface the cue-recognition patterns that experts apply below conscious awareness. The output is a set of concrete situations linked to specific judgments — the raw material for instruction files and eval tasks.

### Failure-mode interviews

Review recent agent failures with the domain expert — the same raw material [incident-to-eval synthesis](../verification/incident-to-eval-synthesis.md) turns into test cases. For each failure, ask the expert to explain what a correct output would look like and why. The explanation reveals the implicit standard the expert applies. Encode each standard explicitly: as an instruction constraint, an annotated example, or a failing eval case. The Martin Fowler memo on encoding team standards maps this interview output directly to instruction structures: corrections become convention checks, security instincts become threat-model items, review rejections become critical checks ([martinfowler.com](https://martinfowler.com/articles/reduce-friction-ai/encoding-team-standards.html)).

### Example annotation

Present the expert with a set of agent outputs, a mix of good, acceptable, and poor, and ask them to annotate each. The annotations reveal the evaluation criteria the expert applies, the human half of [LLM-as-judge evaluation](llm-as-judge-evaluation.md). Disagreements across annotations from multiple experts identify where the tacit knowledge is ambiguous or contested. Those cases need explicit team alignment before encoding.

Use a single internal domain expert as the final decision-maker for quality standards. External annotators without shared context create more disagreement than they resolve ([Hamel Husain](https://hamel.dev/blog/posts/evals/)).

## Encoding formats

Once elicited, tacit knowledge takes three forms in agent systems:

| Elicited Output | Encoding Target | When to Use |
|---|---|---|
| Explicit rule ("always check X before Y") | Instruction file constraint | Non-negotiable, machine-checkable |
| Contextual judgment ("in case Z, prefer A over B") | Annotated few-shot example | Context-dependent, not rule-expressible |
| Quality standard ("this output is poor because…") | Eval task with rubric | Drives calibration of automated evaluators |

The Knowledge Activation Pipeline formalizes this as three stages: codification (capture from experts), compression (distill into token-efficient units), and injection (deliver at the point of need) ([arxiv 2603.14805](https://arxiv.org/html/2603.14805v2)). A runbook of 2,000 tokens compresses into an agent skill of about 300 tokens while keeping the same task completion — a 6 to 7 times gain in knowledge density.

## Scaling with annotation queues

Direct expert review does not scale to production volume. To scale, use expert judgment to calibrate automated evaluators, then let those evaluators handle the volume.

Route a sample of production traces to an annotation queue where domain experts review full context, add corrections, and rate outputs — the production-to-training leg of [closed-loop agent training](closed-loop-agent-training.md). Feed those annotations into automated evaluator fine-tuning or rubric refinement. Once the automated evaluator reliably matches expert judgment on held-out cases, reduce the human review rate. LangSmith annotation queues support this approach: human review of selected traces at the top of the funnel, automated evaluation at scale downstream ([LangSmith docs](https://docs.langchain.com/langsmith/annotation-queues)).

The calibration step is critical. An automated evaluator that does not match expert judgment on known cases amplifies the wrong signal at scale.

## Drift, the slow failure mode

Encoded tacit knowledge becomes stale. Practices evolve, tools change, and new team members bring different judgments. An instruction file holding last year's conventions misguides agents silently, without throwing an error.

Two signals indicate staleness. The agent produces output that matches an older convention rather than current practice. Or domain experts start overriding automated evaluator verdicts regularly. Both point to a gap between encoded knowledge and current tacit knowledge.

Schedule periodic re-elicitation sessions on a regular cadence, not triggered by failure. Treat each session as a diff against the previous encoding — the proactive arm of [continuous agent improvement](continuous-agent-improvement.md). Capture what has changed, update the affected instructions and eval criteria, and record why the standard shifted. Cadence varies by domain velocity. Fast-moving teams may need quarterly sessions, while stable domains can run annually.

## When this backfires

Encoding tacit knowledge is expensive and carries its own failure modes:

- Expert is unavailable or unwilling: the workflow needs sustained access to domain experts. If the only subject-matter expert is time-constrained or has left the team, elicitation stalls. Consider recording rationale during code reviews and retrospectives as a lower-bandwidth substitute.
- Knowledge is too context-sensitive to encode: some judgments depend on real-time context that you cannot capture as static instructions or few-shot examples — the residue of the [implicit knowledge problem](../patterns/anti-patterns/implicit-knowledge-problem.md) that encoding cannot reach. Forcing them into an instruction file produces rules that are correct on average but wrong in the specific cases that matter most. Prefer eval tasks that test context-sensitive behavior rather than encoding the rule.
- Encoding lag creates stale guidance faster than re-elicitation fixes it: in domains where practices shift rapidly (new frameworks, evolving security requirements), encoded knowledge may be outdated before agents act on it. High-velocity domains may benefit more from retrieval-augmented context — RAG, pulling live documentation at inference time — than from static encoded knowledge.
- The extractable fraction is smaller than it looks: scheduled interviews cannot recover the insights that only surface during incubation — when an expert wakes up with sudden clarity days after the conversation. A six-hour session with an AI-guided elicitation agent removes that phase entirely rather than compressing it ([INNOQ](https://www.innoq.com/en/blog/2026/04/ai-cognitive-lens-domain-knowledge/)). Pair scheduled elicitation with an always-open capture channel (annotation queue, rationale-in-PR convention, shared decision log) so post-session insights still land in the encoding pipeline.

## Key Takeaways

- Tacit knowledge requires active elicitation — direct questions about rules surface what practitioners say they do, not what they actually do
- Tough-case and failure-mode interviews surface cue-recognition patterns that experts cannot articulate through abstract questions
- Elicited knowledge maps to three encoding targets: instruction constraints (explicit rules), few-shot examples (contextual judgment), and eval rubrics (quality standards)
- Scale human review by using expert annotation to calibrate automated evaluators, then shifting volume to automation
- Encoded tacit knowledge drifts as practices evolve — schedule proactive re-elicitation sessions rather than waiting for failures to expose the gap

## Related

- [The Implicit Knowledge Problem](../patterns/anti-patterns/implicit-knowledge-problem.md) — the anti-pattern this workflow addresses
- [Continuous Agent Improvement](continuous-agent-improvement.md) — the broader improvement loop this feeds into
- [LLM-as-Judge Evaluation with Human Spot-Check Review](llm-as-judge-evaluation.md) — calibrating automated evaluators with human annotation
- [Eval-Driven Development](eval-driven-development.md) — using encoded standards as eval criteria
- [Introspective Skill Generation](introspective-skill-generation.md) — agent-assisted skill capture from observed behavior
- [Closed-Loop Agent Training](closed-loop-agent-training.md) — full feedback loop from production to training
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) — converting failures into eval cases
- [AI Development Maturity Model](ai-development-maturity-model.md) — calibration and eval stages in the broader maturity arc
- [Porting a Coding-Agent Harness Beyond Engineering](porting-agent-harness-beyond-engineering.md) — encoding a non-engineering function's methodology so a CLI agent can run it

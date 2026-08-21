---
title: "Stated-Understanding Checks: Asking the Agent to Correct You"
term: "Stated-Understanding Check"
description: "State your reading of the system and ask the agent to correct it. The check pays off when the claim is verifiable in the repository, and misleads when it is not."
tags:
  - human-factors
  - claude
aliases:
  - is my understanding correct
  - understanding confirmation request
  - intent confirmation check
last_reviewed: 2026-08-21
maturity: emerging
---

# Stated-Understanding Checks: Asking the Agent to Correct You

> Say what you think the system does and ask the agent to correct you. The answer counts only when the agent can look it up.

A stated-understanding check is a turn where the developer writes out their model of how some part of the system works and asks the coding agent to confirm or correct it, before requesting any edit. Eivind Kjosbakken describes the form as "is my understanding correct: \<present understanding\>" and reports running it 10 to 20 times a day ([Kjosbakken, Towards Data Science](https://towardsdatascience.com/how-to-effectively-align-your-intents-with-claude-code/)). It catches intent drift at the point where correcting it costs a sentence, instead of at review, where it costs a diff.

The check is not reliable by default. An agent asked to rule on a claim it cannot look up will tend to agree with you instead, which is the [yes-man](../patterns/anti-patterns/yes-man-agent.md) failure applied to your own assumptions.

## When the check earns its turn

Run it when all three hold:

- The claim is decidable from the workspace. Which module owns a behavior, whether a job is scheduled or event-driven, what a function returns on the empty case: the agent can open the file and find you wrong.
- You can state the claim specifically enough to be wrong. Kjosbakken names this limit himself, writing that the technique "requires a minimum level of code understanding because, of course, you have to know how different systems work."
- You ask before the agent has argued for an approach, rather than after.

Outside those conditions, skip the turn. The reply will carry agreement bias rather than information.

## Which direction the check runs

Two loops close the same gap, and they fail differently.

| Direction | Mechanism | Failure mode |
|---|---|---|
| Agent states, you check | Plan mode: "Claude reads files and proposes a plan but makes no edits until you approve" ([Claude Code docs](https://code.claude.com/docs/en/common-workflows)) | You skim the plan and approve a wrong one |
| You state, agent checks | A stated-understanding check | The agent agrees with a wrong statement |

Plan mode puts a human on the checking side, which takes the model's agreement bias out of the loop and substitutes the reviewer's own attention as the weak point. A stated-understanding check puts a model there instead, adding a channel that can return a confident yes to a false claim. Reach for it on a single fact you need settled before the next turn, and switch to plan mode once the question is large enough to be worth reading a plan about.

## Why it works

Grounding does most of the work. An unstated assumption becomes a proposition the agent can test against files it has read, which is why Kjosbakken's own example resolved as a correction. He expected a cron job, and the agent reported that "the system was not based on a cron job, for example, it was based on a webhook system."

Framing does the rest. This check replaces instructing an agent on the basis of a mental model never said out loud, which is an assertion rather than a question. Dubois and colleagues isolate that variable and find sycophancy "substantially higher in response to non-questions compared to questions", with their mitigation being to convert non-questions into questions before answering ([Dubois et al., arXiv:2602.23971v4](https://arxiv.org/abs/2602.23971v4)). Turning your assumption into a question is the intervention their experiments measure.

Neither mechanism removes the agreement bias. Five state-of-the-art assistants exhibited sycophancy across four free-form generation tasks, a behavior the same authors judge "likely driven in part by human preference judgments favoring sycophantic responses" ([Sharma et al., arXiv:2310.13548v4](https://arxiv.org/abs/2310.13548v4)). The check trades one failure mode for a smaller one.

## When this backfires

- The claim has no answer in the workspace. Design preferences, product intent, and unwritten conventions give the agent nothing to disconfirm against.
- You state it at length and with confidence. Persuasion rises with the amount of reasoning in the user's turn "even when the conclusion of the reasoning is incorrect", and sycophancy rises with epistemic certainty ([Kim and Khashabi, arXiv:2509.16533v1](https://arxiv.org/abs/2509.16533v1); [Dubois et al., arXiv:2602.23971v4](https://arxiv.org/abs/2602.23971v4)). The detail that makes a claim checkable is the same detail that makes agreement likelier.
- You correct the agent after it has already committed to an approach. Models endorse a user's counterargument more readily when it arrives as a follow-up than when both readings are put side by side for evaluation ([Kim and Khashabi, arXiv:2509.16533v1](https://arxiv.org/abs/2509.16533v1)).
- The canonical wording works against you on one axis. Sycophancy "is amplified by I-perspective framing" ([Dubois et al., arXiv:2602.23971v4](https://arxiv.org/abs/2602.23971v4)), and "is my understanding correct" is I-perspective. Ask about the system rather than about your belief: "does the sync run on cron" beats "is my understanding correct that the sync runs on cron."
- The wrong-answer rate is not negligible. On mathematics and medical datasets, SycEval measured sycophantic behavior in 58.19% of cases across ChatGPT-4o, Claude-Sonnet, and Gemini-1.5-Pro, of which 14.66% was regressive, moving the model from a correct answer to an incorrect one, and the behavior persisted at 78.5% once established ([Fanous et al., arXiv:2502.08177v4](https://arxiv.org/abs/2502.08177v4)). Those are not coding-agent numbers, so read them as the order of magnitude to expect rather than a rate for your repository.
- The change is small enough to read. A diff is a deterministic oracle with no agreement channel in it, and one round-trip costs more than it saves.

## Example

Weak form, inviting agreement:

```text
I'm fairly confident the nightly sync is a cron job that reads from the
staging table, transforms rows, and writes to prod. Is my understanding correct?
```

Stronger form, forcing a lookup and a choice:

```text
Is the nightly sync triggered by a cron schedule or by a webhook? Cite the file.
```

The second version offers no preferred answer to agree with, names an artifact the agent must open, and fits on one line.

## Key Takeaways

- Phrase it as a question about the system rather than about your belief: "does the sync run on cron", not "is my understanding correct that the sync runs on cron".
- Name the artifact you expect to settle it, and treat any answer that cites no file as unanswered.
- If what you want confirmed is a preference rather than a lookup, take it to plan mode or to the diff instead.
- Run the check before the agent commits to an approach. Past that point, restart the turn rather than argue with it.
- Promote anything you re-check every session into `CLAUDE.md`, where it stops costing a turn.

## Related

- [Intent-Centric Engineering: Oversight Over Authorship](intent-centric-engineering.md) — the operating-model argument for why specifying intent became the leverage point
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) — the mirrored loop, where the agent asks instead of confirming
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](author-to-reviewer-role-inversion.md) — why catching divergence before the diff matters as review becomes the constraint
- [Developer Control Strategies for AI Agents](developer-control-strategies-ai-agents.md) — the wider set of in-session steering moves
- [The Yes-Man Agent: Compliance Without Verification](../patterns/anti-patterns/yes-man-agent.md) — the agreement bias this check both exploits and is exposed to

## Sources

- [Kjosbakken, "How to Effectively Align Your Intent with Claude Code", Towards Data Science](https://towardsdatascience.com/how-to-effectively-align-your-intents-with-claude-code/)
- [Claude Code documentation, "Common workflows"](https://code.claude.com/docs/en/common-workflows)
- [Dubois et al., "Ask don't tell: Reducing sycophancy in large language models", arXiv:2602.23971v4](https://arxiv.org/abs/2602.23971v4)
- [Sharma et al., "Towards Understanding Sycophancy in Language Models", arXiv:2310.13548v4](https://arxiv.org/abs/2310.13548v4)
- [Kim and Khashabi, "Challenging the Evaluator: LLM Sycophancy Under User Rebuttal", arXiv:2509.16533v1](https://arxiv.org/abs/2509.16533v1)
- [Fanous et al., "SycEval: Evaluating LLM Sycophancy", arXiv:2502.08177v4](https://arxiv.org/abs/2502.08177v4)

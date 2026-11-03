---
title: "Four Producer Verdicts for Resolving Reviewer Findings"
term: "Producer Finding Verdicts"
description: "The producer agent answers each reviewer finding with one verdict, and may contest only with evidence the reviewer could read. Outside facts go to the human."
tags:
  - code-review
  - multi-agent
  - tool-agnostic
aliases:
  - fix contest escalate decline
  - resolving reviewer findings
  - producer reply to reviewer findings
last_reviewed: 2026-11-03
maturity: emerging
---

# Four Producer Verdicts for Resolving Reviewer Findings

> The producer answers each reviewer finding with one verdict: fix, contest with readable evidence, escalate to the human, or decline a nit.

A reviewer finding needs a reply from the agent that wrote the work. In the [critic agent pattern](../patterns/agent-design/critic-agent-plan-review.md), the critic approves or rejects, and a rejected plan goes back for revision. The [Elephant-Goldfish Model](../patterns/multi-agent/elephant-goldfish-design-review.md) (EGM) gives its drafting agent four verdicts and five rules. The EGM resolve skill tells the agent to "Give each finding exactly one category" ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L54-L67)).

## The four verdicts

| Verdict | When it applies | What happens next |
|---|---|---|
| PROPOSE FIX | The finding is valid | The agent writes the exact replacement text |
| CONTEST | The finding is wrong, and a file and symbol, or a decision recorded in the document, shows it | The human can agree, overrule with a fix, or discuss |
| ESCALATE | The finding is wrong, but the evidence sits outside every file the reviewer could read | No fix. The human confirms, adds the fact to the document, or discusses |
| DECLINE | The finding is a Nit | Recorded and not fixed. A Nit may still get PROPOSE FIX if the fix is worth it |

The table follows the [verdict list](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L56-L67) and the [interactive breakdown](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L163-L168). EGM's examples of outside evidence are a team convention and a verbal decision.

The commit that added ESCALATE and DECLINE explains ESCALATE. It states, "Some findings are wrong, but only facts outside the document show this" ([commit 75d562c](https://github.com/google/elephant-goldfish-model/commit/75d562cf0ff257336c94a0efdcfe7b255c4de0ce), [PR #167](https://github.com/google/elephant-goldfish-model/pull/167)).

## Rules that keep a contest honest

The skill attaches [five rules](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L69-L82) to the verdicts.

- A contest must be checkable. "This was intentional" is not evidence. Without readable evidence, the agent must ESCALATE or fix.
- Context goes into the document only when a human reader needs it. Context that only a zero-context reviewer needs goes to the human as ESCALATE. The skill states this rule without a reason.
- A comprehension gap cannot be contested: "If a fresh reader could not follow the document, the document is missing context."
- The agent may not change a severity. To argue that a Blocker is a Nit, it contests and states why. The skill does not say why severity stays fixed.
- The last rule names the author's bias: "A wish to contest is not evidence that the reviewer is wrong."

[Evidence-grounded disagreement](evidence-grounded-disagreement.md) applies the same citation rule one step earlier, to a critic that audits the reviewer.

## The failure mode it guards against

The resolver is the author. EGM runs the resolver in "the persistent conversation session that generated the target document" so that it recalls earlier reasoning ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L26-L28)). The draft skill gives a reason to skip a self-check at draft time: "The session that wrote the draft agrees with it" ([egm-draft](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-draft/SKILL.md#L251-L253)). The same bias can affect the resolver, which shares that session (inference).

Inside the review loop, a contested finding is settled and stays closed when a later reviewer raises it again. A fixed finding does re-open ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L154-L161)). A settled finding does not block a clean round, and two clean rounds end the loop ([clean round](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L161-L166)). An unchecked contest can therefore close a real defect for the rest of the loop (inference).

## Batch accept applies fixes only

When the human replies "auto accept", the agent applies every PROPOSE FIX in one batch. CONTEST, ESCALATE, and DECLINE items are "explicitly bypassed" ([auto accept](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L138-L142)). So every contest stands unless the human objects first (inference). DECLINE items are skipped in the item-by-item walkthrough ([breakdown](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L145-L146)). Escalated findings appear first in the chat message, because "They need the user's knowledge, not only approval" ([gate](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L112-L113)).

## Costs and limits

- ESCALATE requires human attention because EGM [routes it to the user](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L61-L63).
- The rules are prompt text, and nothing in the skill checks that a cited file and symbol exist (inference).
- The loop skill settles a finding that is "contested or recorded without a fix (accepted risk)". That wording fits DECLINE (inference), and it does not name ESCALATE ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L154-L158)).
- The report template labels severity High, Medium, or Low, with no mapping to Blocker, Major, and Nit ([template](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L97-L98)).
- Upstream reports no measurement of how often contests or escalations were right. See the [EGM evidence section](../patterns/multi-agent/elephant-goldfish-design-review.md#evidence).

## Key Takeaways

- Outside EGM, give the producer a closed verdict set. Accept a contest only when it cites a file or a recorded decision the reviewer could read.
- Read the contests before you batch-accept fixes. In EGM a batch accept skips contested findings, so each contest stands.
- Let the producer argue severity through a contest, never by relabeling the finding.
- When an outside fact refutes a finding, add it to the document only if a human reader needs it.
- If contested findings stay closed across review rounds, check the contests before the loop counts a round as clean.

## Related

- [Elephant-Goldfish Design Review](../patterns/multi-agent/elephant-goldfish-design-review.md) — the full workflow this protocol belongs to
- [Evidence-Grounded Disagreement in Agentic Code Review](evidence-grounded-disagreement.md) — a critic must cite code to object to a reviewer
- [Critic Agent Pattern: Dual-Model Plan Review](../patterns/agent-design/critic-agent-plan-review.md) — approve-or-reject gating, with structured feedback to the planner
- [The Yes-Man Agent](../patterns/anti-patterns/yes-man-agent.md) — the opposite failure, where the agent accepts every request
- [Capturing Dismissal Reasons for Agent Review Findings](dismissal-reason-capture.md) — a closed vocabulary for human dismissals
- [LLM Code Review Overcorrection](../patterns/anti-patterns/llm-review-overcorrection.md) — reviewers that flag correct work

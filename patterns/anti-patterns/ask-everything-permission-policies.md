---
title: "Ask-Everything Permission Policies Protect Less than Per-Action Approval"
term: "Ask-Everything Permission Policy"
description: "Standing allow/ask/never rules over coarse consequence categories blocked 20.1 points less agent overreach than per-action approval, because users chose ask for 81.4% of rules and then approved the overreach at runtime."
tags:
  - anti-pattern
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - standing permission policy
  - consequence-category permission rules
  - allow ask never rules
last_reviewed: 2026-08-29
maturity: emerging
status: current
---

# Ask-Everything Permission Policies Protect Less than Per-Action Approval

> Standing allow/ask/never rules blocked 20.1 points less agent overreach than per-action approval, because users chose ask for most rules.

A permission policy written in advance protects only through the rules that settle something. Offer allow, ask, and never over broad consequence categories and people pick ask, which hands the decision back to the runtime prompt the policy replaced. Across 113 participants supervising a simulated 18-action day, policy blocked 39.6% of overreach against 59.6% under per-action approval, a 20.1-point gap, 95% CI [-32.1, -8.1] ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)).

## Where the finding applies

One shape was measured: four fixed consequence categories (spend money, send or publish, delete, access private information), one rule each, authored by the same person who then supervised the agent, by participants with no professional software background ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)). Outside that shape it does not carry. Narrow rules refined from decisions the user already made run the other way. Conleash, which auto-permits calls inside known boundaries and escalates the rest, scored 98.2% accuracy over 984 real traces ([Li et al., 2026](https://arxiv.org/abs/2605.11360v1)). On an unattended agent an ask rule has nobody to ask, so it blocks rather than defers.

## What the numbers say

| Condition | Overreach blocked | Tasks completed | Prompts |
|---|---|---|---|
| Human approves each action | 59.6% | 94.1% | 18.0 |
| Model reviews each action | 53.9% | 96.9% | 10.0 |
| User-authored policy | 39.6% | 95.3% | 10.9 |

Completion sits within three points across all three, and the author still declines to call them equivalent: "Because no non-inferiority margin was preregistered, we do not claim that the conditions were equivalent in required-action completion." Prompts fell 39%, and the time saving did not survive rule authoring: -12.9 seconds of total intervention, 95% CI [-46.3, 20.6] ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)).

## Why it works

Writing a standing rule asks two things at once: a preference, and a decision about cases you have not seen. Ask supplies the first and withholds the second, and it sits mid-list where it reads as the careful choice. Participants picked it for 114 of 140 rules, leaving 26 that settled anything in advance ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)). The deferred decisions then arrived in a quieter session. Of 148 overreach actions executed under policy, 133 followed a human approval and 15 ran under an allow rule, and policy drew fewer overreach prompts than either alternative while recording the highest approval rate on all seven. Anthropic measured the same reflex: Claude Code users approve 93% of permission prompts, and "over time that leads to approval fatigue, where people stop paying close attention to what they're approving" ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)).

## When this backfires

- Two-value editors. Allow and never force the decision at authoring time, so this escape hatch does not exist.
- Someone else's policy. When a platform team writes the allowlist and another person runs the agent, the ask share stops predicting anything.
- Reading this as a case against the human. Runtime approval ships in 15 of 21 production systems surveyed, and "human participation in agent security decisions is indispensable given current capabilities" ([Wang et al., 2026](https://arxiv.org/abs/2605.24309v1)). Per-action approval still let 40.4% of overreach through ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)).
- One scripted day, no real consequences. The policy offered four fixed, coarse categories, so the author cannot separate a preference for case-by-case control from insufficient rule specificity ([Yan, 2026](https://arxiv.org/abs/2608.27443v1)).

## Key Takeaways

- Count the ask share of your policy. A file where most entries defer is a prompt generator with extra setup, not a control.
- Convert repeat approvals into narrow allow rules naming the recipient, path, or amount. A rule that cannot name those has nothing to settle.
- Fewer prompts is not the goal and can be the harm. The policy condition cut prompts by 39% and let more overreach through.

## Related

- [Task-Uniform Agent Permissions Ignore Where Failures Land](task-uniform-agent-permissions.md) — the sibling failure of choosing one permission level per session instead of per task
- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](../agent-design/classifier-gated-auto-permission.md) — moving the per-call decision to a classifier rather than a standing rule
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../../security/enforced-versus-advisory-controls.md) — sorting safeguards by where they are evaluated, which is what an ask rule fails to do
- [Human-in-the-Loop Confirmation Gates](../../security/human-in-the-loop-confirmation-gates.md) — the per-action baseline this policy shape was measured against
- [Managing Cognitive Load and AI Fatigue](../../human/cognitive-load-ai-fatigue.md) — the approval-fatigue mechanism in its wider form

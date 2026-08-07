---
title: "Listener-State Naming for User-Invoked Agent Skills"
term: "Listener-State Naming"
description: "Name a user-invoked skill after the reader's failure state rather than the output shape, so the agent adds the missing premise instead of deleting words."
tags:
  - instructions
  - skills
  - tool-agnostic
  - tool-engineering
aliases:
  - wait-what skill
  - naming skills for the reader's state
last_reviewed: 2026-08-06
maturity: emerging
---

# Listener-State Naming for User-Invoked Agent Skills

> Naming a user-invoked skill after the listener's failure state asks the agent to add the missing context, where naming the output only removes words.

Listener-state naming is a skill-design choice: the invocation name describes the state the reader is in, not the shape the reply should take. Matt Pocock's `/wait-what` is the worked example. You type it when an agent's message did not land, and the agent re-pitches what it just said, adding the context you were missing and using your project's vocabulary ([AI Hero, The /wait-what Skill](https://www.aihero.dev/skills-wait-what)).

## The whole skill is one sentence

The file is frontmatter plus one line ([`skills/productivity/wait-what/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md)):

```markdown
---
name: wait-what
description: Stop. That last message did not land — re-pitch it.
disable-model-invocation: true
---

Wait — I don't understand where you've got to here. Re-pitch that: give me a little bit of
context, talk in ASD-STE100 Simplified Technical English, and use the ubiquitous language
from `CONTEXT.md`.
```

The brevity is deliberate. Pocock argues that skills fighting verbosity fail by growing, because a 400-line concision skill still leaves the model verbose ([AI Hero](https://www.aihero.dev/skills-wait-what)).

The [`disable-model-invocation`](skill-frontmatter-reference.md) field makes the skill user-only, on the reasoning that only the human knows when they stopped following. The Codex sidecar sets `policy.allow_implicit_invocation: false` for the same effect, keeping the skill out of the agent's context until you type it ([AI Hero, skills changelog v1.2](https://www.aihero.dev/skills/skills-changelog-v12-wait-what-writing-for-agents-claude-code-plugin-and-more)).

The body then names two register sources: ASD-STE100 Simplified Technical English, a controlled English of 53 writing rules and about 900 approved words ([ASD-STE100, About STE](https://www.asd-ste100.org/about_STE.html)), and the [ubiquitous language](../instructions/ubiquitous-language-for-ai-plans.md) held in `CONTEXT.md`.

## Why it works

The two naming styles license different repairs. An instruction about the output, such as "be concise", is satisfied by deletion, so the model deletes. Deletion carries a measured cost: instructing models for conciseness impaired misinformation resistance in 11 of 17 models tested, with drops reaching 20%, because brevity suppresses the nuance and justification needed to reject false content ([Le Jeune et al., Phare: A Safety Probe for Large Language Models, arXiv:2505.11365v4](https://arxiv.org/abs/2505.11365v4)).

An instruction about the listener has no deletion-shaped answer. "I don't understand where you've got to" can only be served by supplying the premise the reader lacked, then saying it plainly. The skill body encodes that order: context first, simplified register second.

Only the first half of that mechanism is measured. The Phare result establishes what brevity instructions cost. The claim that listener-state names escape the same trap is Pocock's reasoning from practice, and no published study tests it directly.

## When this backfires

- The agent is wrong rather than unclear. A re-pitch is a restatement, and model-produced explanations can misrepresent the real basis for an answer: accuracy fell by as much as 36% across 13 BIG-Bench Hard tasks when models rationalized answers driven by biasing features they never mentioned ([Turpin et al., arXiv:2305.04388v2](https://arxiv.org/abs/2305.04388v2)). A wrong claim restated in your own project nouns is harder to catch.
- Typing it is pushback, and pushback moves models. Conformity under user pushback has two drivers, learned sycophancy and inference-time epistemic uncertainty, and both strengthen when the user reads as expert ([Guo et al., arXiv:2605.27288v1](https://arxiv.org/abs/2605.27288v1)). You can get agreement where you wanted clarity.
- No `CONTEXT.md` exists. Pocock notes the skill still works, but you lose the domain-vocabulary half ([AI Hero](https://www.aihero.dev/skills-wait-what)). What remains is a plain-English request, which is where the brevity penalty lives.
- The run is autonomous. A `disable-model-invocation: true` skill never fires on its own, and a scheduled or fanned-out run has no reader to notice they stopped following.
- You reach for it repeatedly. Three invocations in one thread mean the shared vocabulary was never built. Pocock routes that case to `/grill-with-docs` and states the limit plainly: the skill repairs one message and does not prevent the next ([AI Hero](https://www.aihero.dev/skills-wait-what)).

## Example

Pocock contrasts `/wait-what` with three names in common use, all of which describe the output ([AI Hero](https://www.aihero.dev/skills-wait-what)):

| Invocation | What the name describes | Repair it licenses |
|------------|------------------------|--------------------|
| `/tldr`, `/no-fluff`, `/talk-normal` | The reply's length or register | Cut words, which can drop the premise too |
| `/wait-what` | The reader's comprehension failure | Supply the missing premise, then simplify |

## Key Takeaways

- A user-invoked skill's name does work its body cannot: `/wait-what` carries one sentence and still changes what the agent returns.
- Naming the output invites deletion, and brevity instructions cost 11 of 17 tested models up to 20% of their misinformation resistance.
- Set `disable-model-invocation: true` on any skill whose trigger only a human can detect.
- A clearer second telling is no evidence the first telling was right, so comprehension repair leaves correctness unchecked.

## Related

- [Skill Authoring Patterns: Description to Deployment](skill-authoring-patterns.md) — the canonical rules for descriptions, categories, and skill shape.
- [Skill Frontmatter Reference](skill-frontmatter-reference.md) — the fields, including the user-invoked and model-invoked split.
- [Project Writing Skill](project-writing-skill.md) — the model-invoked counterpart, where the agent decides when the skill applies.
- [Ubiquitous Language for AI Plans](../instructions/ubiquitous-language-for-ai-plans.md) — how `CONTEXT.md` gets its vocabulary.
- [Grill Me: Developer-Initiated Plan Interrogation](../patterns/agent-design/grill-me-technique.md) — the upfront session that removes the need to repair messages later.

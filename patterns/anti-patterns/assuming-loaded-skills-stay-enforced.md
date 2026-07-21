---
title: "Assuming Loaded Skills Stay Enforced in Long Contexts"
term: "Skill Requirement Dropout"
description: "Loading a skill does not keep its requirements active over a long trajectory — individual obligations silently drop out, so verify adherence independently."
aliases:
  - Silent Skill Requirement Loss
  - Long-Context Skill Adherence Failure
tags:
  - anti-pattern
  - context-engineering
  - skills
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-07-21
maturity: emerging
---

# Assuming Loaded Skills Stay Enforced in Long Contexts

> Loading a skill does not keep its requirements active as a trajectory grows long, so individual skill obligations silently drop out.

Loading an Agent Skill packages procedural instructions and checks into the context, but it does not guarantee every requirement stays active until the task ends. As a tool-using trajectory grows, individual obligations drop out one at a time. A white-box study of a production code-audit workflow held the task and 24 executable checks fixed and varied only the surrounding context. The agent passed 8 of 10 runs in a clean 11K-character context, but only 3 of 10 at 299K characters ([How Agent Skills Fail under Long Contexts, 2026](https://arxiv.org/abs/2607.17937)). Treating a loaded skill as self-enforcing is the anti-pattern.

## The anti-pattern

You write a skill with a clear rule set and a closing line like "before finishing, check you followed every rule above," then trust that the loaded skill polices itself for the rest of the session. It reads as reasonable: the rules are right there in context, and the agent usually finds the correct files and makes mostly correct edits. The failure is not a knowledge gap. It is sparse incompleteness — one missing array, one protected field changed, or one task left silently unfinished ([2026](https://arxiv.org/abs/2607.17937)).

The tell is that requirement coverage stays high while task success collapses. In the same study, more than 92% of individual checks still passed in long contexts, yet only 30% of artifacts passed all 24 checks at once ([2026](https://arxiv.org/abs/2607.17937)). Coverage is not the bottleneck; the single dropped obligation is.

## Why it works

The failure survives a self-check because a self-generated check inherits the same blind spot that dropped the requirement. When the agent is asked to reconstruct its own validation set, it reproduces the omission it just made — "when generation loses a requirement, self-generated validation can reproduce the same blind spot" ([2026](https://arxiv.org/abs/2607.17937)). Supplying the validation set independently breaks that correlation. In the study, a detailed external checklist restored 10 of 10 passes against 5 of 10 for a generic self-check, the one difference that was statistically significant (two-sided Fisher p=0.0325). This matches the broader pattern that models silently shed the lowest-prominence constraints as constraint count rises ([constraint decay in backend code generation](../../verification/constraint-decay-backend-agents.md)) and that recall degrades as token count grows ([Anthropic, 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

The practical response: keep mandatory constraints few and explicit, pair each with an executable positive and negative test, hold the pending-obligation set outside the growing transcript, and reopen a task automatically when tool output contradicts an expected result ([2026](https://arxiv.org/abs/2607.17937)).

## When this backfires

Independent verification is not free, and re-anchoring can be the wrong tool:

- Short tasks with a few prominent requirements rarely drop obligations, so an external checklist is pure overhead.
- Requirements that cannot be expressed as executable positive or negative tests — subjective quality, tone — give a checklist nothing to assert, so it offers false assurance.
- A long checklist re-creates the problem it was meant to fix; the study is explicit that the completion checklist should hold only critical obligations ([2026](https://arxiv.org/abs/2607.17937)).
- A checklist that drifts from the real requirements reintroduces silent omission from the other side, so it needs the same maintenance as the skill.

One caveat on the evidence: the raw drop from short to long context was only a trend (Fisher p=0.0698), and relevant and irrelevant long context degraded equally, so length alone is not a proven cause ([2026](https://arxiv.org/abs/2607.17937)). Shrinking the working set through retrieval and compaction can matter as much as any verification step.

## Example

**Before — self-generated validation inherits the omission:**

```markdown
<!-- in the skill -->
Before finishing, double-check you followed every rule above.
```

**After — an independent checklist with executable positive and negative tests, held outside the transcript:**

```yaml
# checklist.yaml — supplied to a checker, not reconstructed by the agent
- id: required-arrays-present
  assert: "output.tags is a list"     # positive: must exist
- id: protected-id-unchanged
  assert: "output.id == input.id"     # negative: must not change
```

The generic self-check asks the agent to rebuild the validation set it just failed to apply; the independent checklist supplies that set, so a lost requirement is caught instead of re-forgotten.

## Key Takeaways

- A loaded skill does not stay enforced; requirements drop out one at a time as the trajectory grows.
- High requirement coverage hides the failure — one missed obligation fails the whole task while 92%+ of checks still pass.
- A self-check inherits the generator's blind spot; verify against an independent, detailed checklist instead.
- Keep the checklist small, pair each obligation with a positive and negative test, and hold it outside the transcript.

## Related

- [The Infinite Context](infinite-context.md) — general context rot: unfocused context dilutes attention and degrades output.
- [Constraint Decay in Backend Code Generation](../../verification/constraint-decay-backend-agents.md) — the prompt-level version: agents drop the lowest-prominence constraints as constraint count rises.
- [Premature Completion](premature-completion.md) — agents declare success while a required obligation remains unmet.
- [Pre-Completion Checklists](../../verification/pre-completion-checklists.md) — the independent-verification fix as a standing practice.
- [Agent Extension Conflicts](agent-extension-conflicts.md) — how loaded skills interact and degrade under context-budget contention.

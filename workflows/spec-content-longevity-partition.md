---
title: "Partition Spec Content by Expected Longevity"
term: "Spec Content Longevity Partition"
description: "Sort spec content into living intent, change-scoped implementation detail, and shared instruction files, where specs are retained and read again later."
aliases:
  - spec content longevity partition
  - partition spec content by longevity
  - what-level content in a living spec
tags:
  - workflows
  - agent-design
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-17
maturity: emerging
---

# Partition Spec Content by Expected Longevity

> Sort spec content by how long it should outlive the change, where retained specs get read again and the decay link is argued, not measured.

Goals, requirements, and acceptance criteria can outlive an implementation. Named classes, paths, and library versions can change during refactoring. Separate retained content by expected lifetime so readers can identify which sections still apply.

## When this applies

Use the partition when all three conditions hold.

- You retain specs after the change lands. Practitioners split three ways on retention: a living spec updated as the system changes, an accumulated change record, or discarding the spec and keeping the design record elsewhere ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). Under the third practice nothing is retained, so nothing decays.
- Someone reads a retained spec again later, whether a teammate or one of the "agents, whose context typically holds only files in the working tree" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).
- You have a second home for durable team knowledge, such as an [AGENTS.md file carrying distributed conventions](../instructions/agents-md-distributed-conventions.md).

Retention also splits by group. Agarwal et al. report that "Tool users were divided across the three practices, whereas most tool makers kept living specs", and that Reddit discussions showed a similar divide, with some posts arguing for discarding specs because "every SDD framework gets the same complaint: spec rot" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).

## The prescribed and practiced gap

Spec-driven development tools prescribe the split and get a different file. OpenSpec and Spec Kit both tell users explicitly to keep implementation detail out of the spec, and most tool makers interviewed by Agarwal et al. described excluding or separating the how into design and task documents. In the study's judged repository sample the opposite is what landed: "most spec files (77.6%) contain implementation detail, including 58.2% wherein that material occupies a section or more" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).

Read that figure at the scope it was measured: an LLM judged a stratified sample of 1,000 documents drawn from the study's sample of 266 active, popular public repositories, and "OpenSpec, which accounts for 78.4% of the sample" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). It is a share of judged spec files, not of practitioners, and the labels come from a model.

Most tool users routinely included implementation-level content irrespective of the task. Some added it only where they judged the agent incapable, as P10's team specifies "the how if we believe it's in a place where AI has very low capability of doing it". The authors note that "Implementation detail added because the agent performed poorly on a task may shrink as models improve" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). Partitioning retains the detail while marking its lifetime.

## Three implementation layers

### Layer 1: classify each section at write time

Classify each section before implementation.

| Bucket | Content | Lifetime |
|---|---|---|
| Living intent | Goals and rationale, requirements, acceptance criteria, constraints, out-of-scope items | Until the intended behavior changes |
| Change-scoped detail | Implementation approach, named classes and functions, file paths, data structures, library versions, task breakdown | Until the change lands |
| Durable convention | Coding conventions, internal APIs, domain rules, reference docs for unfamiliar libraries | Across changes, so not in the spec at all |

The content items come from the paper's taxonomy of what and how content, where acceptance criteria count as what-level "because most participants described this information as the conditions for accepting the resulting system behavior after the spec is implemented" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). The three buckets and their lifetimes are a reading of that taxonomy against the study's implications, not a grouping the paper publishes.

### Layer 2: route durable conventions out of the spec

Move the third bucket into shared instruction files the agent loads for every task, which is what the study's practitioner implication asks for: "Practitioners should keep stable team knowledge, such as conventions and internal APIs, in shared instruction files, as several participants did in response to drift" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). The move came out of agents departing from the spec during implementation. Of the Reddit posters who saw that drift, the paper records: "They responded to drift by making implicit conventions explicit in instruction files" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). A convention written once per repository is not copied into each new spec, so there is one copy to keep current.

### Layer 3: retain the intent, retire the detail

When the change lands, keep the living-intent sections current and mark the change-scoped sections as belonging to that change: archive them with the change record, or drop them. The partition is the paper's implication for tool builders rather than for practitioners, and it is worth quoting as written: "Tool builders should separate the parts of a spec by expected longevity: keep what-level content in a living spec, mark implementation sections as scoped to the change, and make implementation sections optional in templates" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). Teams can apply this template-builder recommendation through section headings or separate files.

## Triggers and constraints

The cycle runs once per change request, at three points with different authority.

| Point | Driver | Authority |
|---|---|---|
| Spec drafted | Human supplies intent, agent drafts | The agent proposes the bucket per section; a person approves acceptance criteria |
| Change implemented | Push or PR | No bucket changes; implementation drift is a separate control |
| Change landed | Merge | A person decides what the living spec now says |

Checks can show disagreement without deciding whether code or spec is wrong. The paper notes such checks "can show that code and spec disagree, but not which is wrong", and recommends that tools draft updates "for human confirmation" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). The study adds a constraint: do not let one agent write the spec, the code, and the tests, because "when one agent writes the spec, the code, and the tests, one misunderstanding can propagate to all three" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).

## Multi-tool coverage

Tool-agnostic. The partition concerns document content. Claude Code, Copilot, and Cursor use different instruction-file conventions; the [instruction file ecosystem](../instructions/instruction-file-ecosystem.md) page maps the names.

## Why it works

Mixed content inherits the decay rate of its fastest-moving part, and implementation detail names things refactoring changes. Agarwal et al. measure the exposure and state the consequence: "We found that 75% of the specs with implementation detail include named classes, functions or library versions, which change under refactoring while the intended behavior does not. Thus, a spec that specifies more implementation detail decays sooner (Finding 10)" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). That 75% is a share of the judged specs that carry implementation detail, not of all specs. The partition marks which content should survive a refactoring.

The causal step from content to decay rate is the authors' reasoning from what files contain, not a measurement, and the study's own threats section forecloses one from this data: "Commit counts therefore cannot show spec decay, which would require checking whether the behavior a spec describes changed while the spec did not" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). Treat the partition as a well-argued convention, not a proven intervention.

## When this backfires

- You discard specs after implementation. With nothing retained there is no decay to prevent, and classification is pure overhead. The strong form of that position, regenerating from docs rather than maintaining specs, is its own workflow: [design docs as the durable artifact](design-docs-as-durable-artifact.md).
- The agent needs the detail where the spec is. Moving conventions and internal APIs into instruction files helps only if the agent loads those files for the task in hand. On the tasks where practitioners added detail because they judged the agent unable to do the work without it, moving that detail out of the spec removes what they chose to supply ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).
- Any spec written before the design settles, greenfield work included. The paper grants the objection: separation may be unrealistic because "requirements and architecture develop together rather than in sequence", participant intent keeps developing as software is built, "so a spec written before design may be unable to separate the what and how" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).
- Changes made with no spec at all. An estimated 82.0% of judged specs describe new features, weighting each document type by its number of files, against 16.5% for fixes, and a spec may carry several labels. A production hotfix leaves "no time for spec-driven development and the whole flow", so behavior changes with nothing recorded. The partition governs spec content and does nothing about that gap ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).
- Nobody reads the retained spec. In the repository sample 98.3% of spec files with a recorded history have a single author and 68.5% of inline comments on specs were written by bots, though the authors are explicit that these "show limited recorded human participation, but not how closely people read specs or whether review happens elsewhere" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).
- The underlying practice is unproven. A team in a Reddit post the paper cites concluded after months of spec-driven development "We couldn't prove it improved the code", and interview participants could not separate reported reliability gains from concurrent model improvements ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).

Participants described no team-level threshold. The authors ask teams to "agree as a team on what warrants a spec, instead of leaving these decisions to each developer" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).

## Example

The paper works a session-expiry change to separate its two divergence modes: "If a spec says a session expires after 30 minutes and the agent implements 60, that is implementation drift; if a later change sets 60 as intended and the spec still says 30, that is spec decay" ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)). Partitioning that same spec puts each of its sections on a different clock.

```markdown
## Goals and acceptance criteria   -> living intent, stays current
Sessions expire after a configurable idle period; default 30 minutes.

## Implementation plan             -> change-scoped, archived with the change
Add the idle-timeout field to the session policy class, migrate the
sessions table, read the default from config.

## Error contract                  -> durable convention, moves to AGENTS.md
All auth failures use the shared error envelope with a machine code.
```

Two things then go stale on different schedules. A refactoring that renames the policy class invalidates only the archived section, which already says it describes a completed change. A later change that sets the default to 60 minutes invalidates the living section, and that is the decay worth catching, because the retained spec now misstates intended behavior rather than a finished implementation.

## Key Takeaways

- The prescription and the practice already disagree, with implementation detail in 77.6% of the judged spec files, so the live question is how long to let that detail live ([arXiv:2608.25202v4](https://arxiv.org/abs/2608.25202v4)).
- Three buckets, three lifetimes: intent survives the change, implementation detail dies with it, conventions never belonged in a spec.
- The partition is worth nothing on its own. It pays off only where a retained spec is read again, which is also the weakest-evidenced link in the chain.
- Skip it when you discard specs after implementation, when the agent needs the detail in place to succeed, or when requirements and architecture are still developing together.
- Treat the decay argument as the authors' inference from spec content. Their commit data cannot show decay, and the study reports associations rather than causal effects.

## Related

- [Spec-Driven Development with Spec Kit](spec-driven-development.md) — the prescription this page partitions against, including the spec-as-compile-source posture
- [Spec Complexity Displacement: When Specs Become Code](../patterns/anti-patterns/spec-complexity-displacement.md) — the same implementation detail read as a precision cost at write time rather than a lifetime cost
- [Spec-Anchored Drift-Gated Architecture (Spec Growth Engine)](spec-growth-engine.md) — gating merges on spec-code divergence, the detection half this page's layer 3 hands back to a person
- [Design Docs as the Durable Artifact](design-docs-as-durable-artifact.md) — the opposite retention choice, regenerating code from docs instead of maintaining specs alongside it
- [AGENTS.md for Distributed Conventions](../instructions/agents-md-distributed-conventions.md) — where the durable-convention bucket goes
- [Enforcement Modes in Spec-First Agent Frameworks](../patterns/agent-design/spec-first-framework-enforcement-modes.md) — sorting a framework's controls by what the agent can ignore, a different axis over the same files

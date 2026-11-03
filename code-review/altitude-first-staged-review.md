---
title: "Altitude-First Staged Review: Simplicity Check Before Detail, Again After Fixes"
term: "Altitude-First Staged Review"
description: "Run a simplicity, YAGNI, and reuse review before comprehension and detail reviews, then run it again to catch complexity that the fixes added."
tags:
  - code-review
  - multi-agent
  - tool-agnostic
aliases:
  - altitude-first review
  - intermediate zoom-out review
  - simplicity check before detail review
last_reviewed: 2026-11-03
maturity: emerging
---

# Altitude-First Staged Review: Simplicity Check Before Detail, Again After Fixes

> Altitude-first staged review checks a design for simplicity, YAGNI, and reuse before detail reviewers run, then repeats that check after their fixes land.

Altitude-first staged review orders the reviewer passes on a design document from high level to low. A simplicity reviewer runs first and asks whether the design needs to exist in this form. Comprehension and critic reviewers follow. The simplicity reviewer then runs again on what their fixes added, and the detailed plan review comes last. The worked example is the [Elephant-Goldfish design review](../patterns/multi-agent/elephant-goldfish-design-review.md) plugin at commit `36343a1`. Its `zoom_out` reviewer runs at stages 5 and 8 of five stages numbered 5 to 9 ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L263-L283)).

| Stage | Reviewers | What it checks |
|---|---|---|
| 5 Zoom Out | `zoom_out` | Problem framing, speculative features, reuse |
| 6 Comprehension | `comprehension` | Whether a fresh reader can follow the document |
| 7 Critic | `design_critic`, `structural`, `style` | Single points of failure, scaling limits, edge cases |
| 8 Intermediate Zoom Out | `zoom_out` | Additions and mitigations since stage 5 |
| 9 Implementation readiness | `implementation_readiness`, `codebase_details`, `style` | The detailed plan against the codebase |

The focus column follows the stage breakdown in the upstream [review design doc](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L66-L100).

## Why simplicity comes before detail

The design doc states the reason. The zoom-out pass checks framing, rejects speculative features, and verifies reuse "before investing in detailed review passes" ([review.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L66-L72)). Detail reviewers can spend a full pass on a feature that a later scope review would cut (inference).

The zoom-out standard also fails the review at once when the reviewer cannot tell what the design is for and why ([zoom-out standard](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/resources/document_standards/zoom-out-standard.md#L14-L19)). The altitude rules then bound the later stages. The skill keeps a code-level rubric out of comprehension review, because "it asks for code-level detail, which the Zoom Out standard forbids in `FeatureRange`" ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L326-L333)).

## Why the check runs again after fixes

Stage 8 audits "additions, modifications, and defensive mitigations introduced during Comprehension and Critic reviews". It purges "speculative complexity and YAGNI elements" before task planning ([review.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L86-L93)). Each mitigation the author adds in reply to the stage 7 critic is new surface for the second pass to judge (inference).

The second pass is incremental. The skill gives the stage 8 reviewer the path of the stage 5 report and tells it to focus on additions and mitigations ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L295-L304)). The design doc adds that the pass avoids "re-flagging decisions accepted in Step 5" ([review.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L86-L93)).

## Sequential stages, parallel reviewers

The Claude guide keeps stages 5 to 9 sequential and allows parallel reviewers only inside the current stage. Each stage's report and required remediation complete before the next dispatch. "Uninterrupted mode skips human checkpoints, not these stage dependencies" ([Claude integration](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L41-L44)).

The skill also bans multi-select menus. Combinatorial checklists are "strictly prohibited to protect topological dependencies" between the five stages ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L120-L122)). One preset skips both zoom-out passes anyway, because the implementation-plan-only review jumps straight to stage 9 ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L157-L159)).

Prompt text sets this order, and a run can break it. The Claude Code 2.1.308 harness run on 2026-10-22 records an "Initial stage-order failure". A focused nine-reviewer rerun then verified sequential stages ([TESTING.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/TESTING.md#L125)). The TESTING.md row does not say how the order broke.

## The reuse check needs code search

A reviewer that reads only the document cannot tell whether a proposed helper already exists (inference). The zoom-out persona must "perform code searches in the codebase to verify whether equivalent or similar components already exist" for proposed new components ([zoom_out persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/zoom_out.md#L45)). The Claude adapter gives it `Read`, `Grep`, and `Glob` ([adapter](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents/zoom_out.md#L1-L9)).

## Trade-offs

- Launch count. The zoom-out reviewer accounts for 2 of the 9 reviewer launches in a full pass ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L263-L283)).
- Wall-clock time. Each stage waits for its slowest reviewer (inference from the [Claude integration](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L41-L44)).
- Anchoring. Upstream passes the stage 5 report to avoid repeat findings. The report also shows the second reviewer the first one's view (inference). Upstream does not discuss that effect.
- Source drift. The stage 5 reason comes from a design doc, and [issue #271](https://github.com/google/elephant-goldfish-model/issues/271) reports that the design docs drift from the shipped skills. The skill text confirms the stage 8 focus, not the stage 5 reason.
- No outcome data. Upstream reports no measurement of whether this order gives better designs. Its FAQ says "Completing the EGM workflow alone does not demonstrate a productivity improvement" ([FAQ](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/faq.md#L45-L46)).

## Key Takeaways

- Give the second simplicity pass the first pass's report and the changes since then, so it judges new text and leaves accepted decisions alone.
- Grant the simplicity reviewer read and search tools over the codebase; a document-only reviewer cannot judge reuse.
- Check stage order in the run record, because a prompt-set order broke once on Claude Code.
- Treat a preset that skips the scope stages as a separate review mode with no simplicity check.
- Do not cite EGM as evidence that altitude-first ordering improves designs.

## Related

- [Elephant-Goldfish Design Review](../patterns/multi-agent/elephant-goldfish-design-review.md) — the full workflow this page takes its stage order from
- [Committee Review Pattern](committee-review-pattern.md) — specialized reviewers that run in parallel, with no order between lenses
- [Abstraction Bloat in AI Agent-Generated Code Output](../patterns/anti-patterns/abstraction-bloat.md) — the over-engineering a simplicity pass looks for
- [Critic Agent Pattern: Dual-Model Plan Review](../patterns/agent-design/critic-agent-plan-review.md) — a critic that reviews plans before implementation
- [Staged Review for Expensive-to-Render Agent Deliverables](../patterns/agent-design/staged-review-expensive-renders.md) — review stages ordered by inspection cost

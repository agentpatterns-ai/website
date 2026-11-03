---
title: "Paraphrase-First Review: A Zero-Context Reader Restates the Design Before Listing Gaps"
term: "Paraphrase-First Review"
description: "A zero-context reviewer first restates what a design document proposes. The author compares that restatement with intent, and a wrong paraphrase counts as a finding."
tags:
  - testing-verification
  - multi-agent
  - tool-agnostic
aliases:
  - paraphrase-first comprehension review
  - zero-context reader paraphrase
last_reviewed: 2026-11-03
maturity: emerging
---

# Paraphrase-First Review: A Zero-Context Reader Restates the Design Before Listing Gaps

> A zero-context reviewer restates what a design document proposes before it lists gaps, and a wrong restatement is itself a finding.

Paraphrase-first review asks a reviewer with no prior conversation to restate what a document proposes and how the existing system works. The author then compares that paraphrase with what they meant. The [Elephant-Goldfish Model](../patterns/multi-agent/elephant-goldfish-design-review.md) (EGM) runs this as its comprehension stage, and its persona states the rule: "A wrong paraphrase is a finding" ([comprehension persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/comprehension.md#L56-L57)). The persona asks for 2 to 5 sentences on each half.

## Why a term scan misses disconnected parts

A term scan lists the words a document uses and never defines. The EGM persona explains the gap. "A list of undefined terms does not find a document whose terms are all defined but whose parts do not connect" ([comprehension persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/comprehension.md#L37)).

A paraphrase must join the parts into one account. When the reader cannot do that for a section, the persona reports the section as a Blocker ([comprehension persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/comprehension.md#L37)). When the reader fills a gap with a guess, the paraphrase reads as fluent and is wrong, and only the author can see that. This reason is inferred. Upstream says only "The author compares it with the intent" ([comprehension persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/comprehension.md#L57)).

The term check still runs after the paraphrase ([comprehension persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/comprehension.md#L38-L41)). The resolution skill also says "Do not contest a comprehension gap." Its reason is "If a fresh reader could not follow the document, the document is missing context" ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L77-L78)).

## Restrict term checks to project vocabulary

A zero-context reader lacks the project's history but knows general engineering. The EGM persona says "You do not know this project. You do know software." It flags a term only when the term belongs to the project, team, or design and has no definition ([comprehension persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/comprehension.md#L48)).

The commit that added this limit gives no reason for it ([commit 36a46ab](https://github.com/google/elephant-goldfish-model/commit/36a46ab390a3888e0343dd612a41ff0c52773a91)). The inferred purpose is to keep requests to define ordinary words from burying project gaps.

## Keep the paraphrase when there are no findings

The first revision of pull request #170 added the paraphrase. It left the stage on its default route through the synthesizer, the agent that merges reviewer output. Its reviewer warned that "a wrong paraphrase can disappear before the author sees it, particularly when the reviewer reports no findings" ([PR #170 review](https://github.com/google/elephant-goldfish-model/pull/170#pullrequestreview-5661226473)). That reviewer states they "did not reproduce it in a live model run". The inferred risk is that a misread with zero findings looks like a clean pass.

The synthesizer's report template has a reviewer status table and a findings list, and no place for a paraphrase ([synthesizer persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/synthesizer.md#L42-L62)). The merged skill spawns the comprehension reviewer directly instead. Its stated reason is "its report keeps only findings, and the author must see the paraphrase". It also says "Keep the paraphrase when there are no findings" ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L328-L337)).

Generalized as an inference, any [fan-out with a merge step](../patterns/multi-agent/fan-out-synthesis.md) should route output that is not a finding around the aggregator. A paraphrase field in the aggregator's [schema](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md) is an alternative EGM does not use.

## How it differs from explain-the-change gates

An [explain-the-change gate](../workflows/explain-the-change-review-gate.md), also called a teach-back gate, tests a different party. There, the author of a code change explains its central mechanism, and a reviewer scores the answer against the diff. That gate measures whether the author understands the change. A paraphrase-first review measures whether the document carries the design to someone who was not present, and the author judges the result. An [agent-generated onboarding guide](../workflows/agent-generated-onboarding-guide.md) gets a similar signal later, when a new teammate's questions expose stale sections.

## Trade-offs

- The author reads every paraphrase, clean rounds included. EGM reports no measurement of that time.
- A paraphrase restates only what the document says. It cannot show a requirement the author never wrote down. This limit is an inference; upstream does not state it.
- The EGM Claude adapter sets `model: inherit`, so the reader runs on the model of the session that spawns it ([adapter](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/.claude-plugin/agents/comprehension.md#L1-L9)). When that matches the drafter's model, the reader can share the drafter's assumptions. This risk is inferred. See [when a second model helps in LLM review](cross-model-review-independence.md).
- EGM publishes no data that paraphrase-first review finds more defects than a term scan. The approving review on PR #170 notes "Live model compliance was not replayed" ([PR #170 approval](https://github.com/google/elephant-goldfish-model/pull/170#pullrequestreview-5679855733)).

## Example

EGM covers the no-findings case in a scenario file. Its assertion requires only the word "paraphrase" in the answer, and checks neither the headings nor their content ([test scenarios](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/test_scenarios.yaml#L115-L125)):

```yaml
- scenario_id: "comprehension_report_keeps_paraphrase"
  description: "Verifies the Comprehension Test report keeps the reviewer's paraphrase."
  eval_type: "deterministic"
  system_prompt:
    skill_file: "skills/egm-review/SKILL.md"
  turns:
    - user_input: "Run only Stage 6 (Comprehension Test) on docs/designs/rate_limit.md. The reviewer reports no findings. What goes in comprehension_report.md?"
      assertions:
        - type: "required_pattern"
          pattern: "(?i)paraphrase"
          message: "The comprehension report must keep the paraphrase, also when there are no findings."
```

The repository's unit test checks only that each scenario file exists and has the required fields ([scenario coverage test](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_scenario_coverage.py#L22-L52)). No code at this commit runs the assertion against a model.

## Key Takeaways

- Ask the zero-context reader for a short paraphrase of the proposal and the current system before any gap list.
- Treat an unparaphrasable section as a Blocker and a wrong paraphrase as a finding, even when the reader reports nothing else.
- Limit undefined-term flags to project, team, and design vocabulary.
- Check that your merge step has a field for the paraphrase; if it keeps findings only, send this stage around it.
- Budget author time to compare every paraphrase with intent, since no upstream data shows the payoff.

## Related

- [Elephant-Goldfish Design Review](../patterns/multi-agent/elephant-goldfish-design-review.md) — the full workflow this stage belongs to
- [Explain-the-Change Review Gates for Agent Code](../workflows/explain-the-change-review-gate.md) — the author explains, instead of a cold reader
- [When a Second Model Helps in LLM Review](cross-model-review-independence.md) — same-model versus cross-model reviewers on documents
- [Fan-Out Synthesis Pattern](../patterns/multi-agent/fan-out-synthesis.md) — merging parallel agent output
- [Typed Schemas at Agent Boundaries](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md) — fields a handoff must carry
- [Five-Pass Blunder Hunt](five-pass-blunder-hunt.md) — repeated critique passes on a plan

---
title: "Artifact-Only Verification Hides Skipped Skill Steps"
term: "Artifact-Only Verification"
description: "Output checks cannot see a mandated step an agent skipped, because a skipped verification step usually leaves the artifact unchanged — measure procedure separately."
aliases:
  - procedural compliance gap
  - output-only verification of skills
  - artifact compliance versus procedural compliance
tags:
  - anti-pattern
  - skills
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-02
maturity: emerging
---

# Artifact-Only Verification Hides Skipped Skill Steps

> An agent skips a third to a half of the steps its own skill mandates, and the artifact still passes every output check.

This anti-pattern only bites when the procedure is part of the specification — when a skill mandates a verification, an approval, or an audit step whose absence does not change the file the agent produces. Under those conditions, a green output check is not evidence the procedure ran.

## The anti-pattern

You write a skill that mandates steps, test the artifact, and treat a passing test as proof the skill was followed. It is not. A prose skill is described to the runtime but never encoded in it, so the model re-derives the control flow on every run and each mandated step becomes a fresh probabilistic decision. Across 30 skills at nine runs per skill per arm, prose agents performed 56% of mandated steps on gpt-4o and 68% on gpt-5, and completed the full prescribed procedure in only 28% of runs — while the artifacts passed ([Dantanarayana et al., 2026](https://arxiv.org/abs/2607.27309v1)).

The paper makes procedure the correctness criterion rather than a proxy for it: "a run that fails to perform a mandated step is wrong, and an artifact test that passes such a run has not measured a second dimension of quality, it has failed to detect a defect" ([2026](https://arxiv.org/abs/2607.27309v1)).

## Why it works

Output tests condition on the artifact, and a verification step that finds nothing wrong leaves the artifact identical to a run that skipped it — indistinguishable to the test. Encoding the procedure closes the gap by sorting steps with one question: is this step's output a function of its inputs? Deterministic steps become code that executes unconditionally, and only judgment steps stay as model slots. Compiled harnesses reached 86% of mandated steps on both model generations and completed the full procedure 2.3 times as often ([2026](https://arxiv.org/abs/2607.27309v1)).

The cheap version needs no compiler. A [pre-completion checklist](../../verification/pre-completion-checklists.md) run by the harness rather than the model puts the same load-bearing steps in program structure.

## When this backfires

Instrumenting procedure is not free, and four conditions make it the wrong move:

- The artifact is the whole specification. When a strong test suite decides correctness, a skipped step that leaves the output correct is efficiency, not a defect.
- The skill is adaptive. Compiled execution costs 0.58x the tokens of prose at the median, but adaptive tool-using skills cost more under the harness, because the prose agent was skipping loops the harness runs ([2026](https://arxiv.org/abs/2607.27309v1)).
- Structure gets mistaken for a guarantee. A mandate can be folded into a model-owned slot's interior and stay model-dependent, so the harness implies enforcement it does not deliver ([2026](https://arxiv.org/abs/2607.27309v1)).
- The base model sits outside the mid tier. Benefit from a harness is non-monotonic in capability: weak-tier models fail to activate or follow harness components, and strong-tier models gain less than mid-tier ones ([Lin et al., 2026](https://arxiv.org/abs/2605.30621v1)).

Two caveats on the evidence. The prose gap narrowed from 30 points to 17 across one model generation while the harness held flat, so some of it may close on its own. And a trace-based check is still a check: sparse tests, opaque scoring scripts, or proxy checks can lead a verifier-driven revision loop to repair the visible assertions rather than the underlying behavior ([Liu et al., 2026](https://arxiv.org/abs/2606.01139v3)) — a sparse mandate set invites the same failure. The SIGIL authors name separate threats: gate credit in the trace-based scoring, judged-measurement noise, a skill sample weighted toward document and compliance work, and two models from one provider ([2026](https://arxiv.org/abs/2607.27309v1)).

## Example

This site's docs skill mandates linting every changed page before finishing. Stated as prose, that mandate is a decision the model re-makes each run:

**Before** — the mandate lives in the skill text, and the only gate is whether the page renders:

```markdown
Before you finish, run the linter on every page you changed and fix the findings.
```

**After** — the same mandate as a harness-run checklist entry, from this repo's `.claude/checklists/docs.json`:

```json
{
  "id": "lint-changed-pages",
  "cmd": "CHANGED=$(git status --porcelain | awk '{print $2}' | grep -E '^docs/.*\\.md$' || true); if [ -z \"$CHANGED\" ]; then exit 0; fi; uv run python scripts/lint-page.py --json $CHANGED | jq -e 'any(.[]; .verdict==\"FAIL\")' >/dev/null && exit 1 || exit 0",
  "severity": "block"
}
```

The Stop hook runs the entry whether or not the model remembered it, and `"severity": "block"` makes skipping it fail the run rather than pass silently. Nothing about the published page changes; what changes is that the step is now observable.

## Key Takeaways

- Artifact compliance and procedural compliance are different measurements, and a passing output check reports only the first.
- Prose skills run roughly half to two thirds of their mandated steps, and the rate moves with the model rather than staying fixed.
- Score procedure directly — per mandate, marked followed, violated, missed, or not applicable — instead of inferring it from the output.
- Put load-bearing deterministic steps in the harness, whether that is a compiled step or a Stop-hook checklist.
- Reserve the effort for skills whose procedure is part of the spec; where the artifact is the spec, output checks are enough.

## Related

- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — the adjacent failure: obligations drop out as the trajectory grows, and there the artifact checks do catch it.
- [Skill Tool as Enforcement: Loading Command Prompts at Runtime](../../tool-engineering/skill-tool-runtime-enforcement.md) — covers getting the skill loaded correctly; this page covers steps skipped after it loads.
- [Pre-Completion Checklists for AI Agent Development](../../verification/pre-completion-checklists.md) — the harness-run checklist as the low-cost form of procedure as program structure.
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the same silent gap seen from the completion signal rather than the step trace.
- [Hooks for Enforcement vs Prompts for Guidance](../../instructions/hooks-vs-prompts.md) — the general rule this instance follows: prompts request, hooks require.
- [Judging a Skill's Honesty by the Validity of Its Output](judging-skill-honesty-by-output-validity.md) — the other way output checks come back clean: every mandated step runs, and the skill steers which candidate wins.

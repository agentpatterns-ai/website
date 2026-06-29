---
title: "Skill Program Functions: Executable Guardrails Compiled From Past Failures"
term: "Skill Program Functions"
description: "Compile recurring skill guidance into runtime predicates that fire on detected failure-prone states — useful when baseline failure rate is high and each compiled function gets its own pilot eval."
tags:
  - agent-design
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - Skill Programs
  - Program Functions for Agents
  - Executable Skill Guardrails
last_reviewed: 2026-06-12
maturity: emerging
---

# Skill Program Functions

> Compiling a skill into an executable guardrail moves the *trigger* out of the model into code — worthwhile only when baseline failure is high.

## When the conditions hold

Skill Program Functions (PFs) replace advisory skill text with runtime predicates: a Python function checks the agent's state each step and, on a failure-prone match, modifies the next action or injects corrective context ([Liu et al., 2026](https://arxiv.org/abs/2605.17734)). They earn the engineering cost only under four conditions; outside them, advisory skills plus hooks dominate.

| Condition | Why it matters |
|----------|----------------|
| Baseline failure rate is high on the target task | On high-success trajectories, false positives disrupt more wins than they rescue — a 0.94-AUROC failure detector caused a 26 pp performance collapse on high-success tasks ([Vasudev et al., 2026](https://arxiv.org/abs/2602.03338)) |
| Each PF can clear a per-function pilot eval | Vasudev et al. recommend a ~50-task pilot per intervention because intervention quality varies independently of detection accuracy |
| The skill domain is stable | A PF binds the intervention to a snapshot of failure modes; tool, model, or task drift makes the predicate fire on states that are no longer failures |
| The corrective action is idempotent under retry | PFs fire mid-loop, not at loop boundaries — the action must be safe to repeat |

Under these conditions, HASP reports up to 25% gain on web-search and 30.4% on math reasoning over baselines including ReAct and Search-R1 ([Liu et al., 2026](https://arxiv.org/abs/2605.17734)).

## What a program function is

A PF wraps a skill's guidance in three parts:

1. Trigger predicate — a deterministic check against agent state, such as `result_count == 0`. The model is not consulted.
2. Intervention type — action modification (rewrite the agent's next tool call) or context injection (append a corrective user-role message).
3. Termination condition — when the PF stops firing, so the fix-loop terminates.

The same library applies at inference time, during post-training as structured supervision, or in a self-improvement loop that evolves teacher-reviewed PFs ([Liu et al., 2026](https://arxiv.org/abs/2605.17734)).

## Why it works

Moving the trigger from instruction-following to a runtime predicate removes two error sources: instruction fade-out over long contexts ([Bui, 2025 §3.2](https://arxiv.org/abs/2603.05344)) and the compliance ceiling — frontier models reach only 68% accuracy at 500 instructions ([IFScale, 2025](https://arxiv.org/abs/2507.11538)). Neither applies to a Python predicate.

The gain comes from removing model judgment from the trigger, not the corrective content — so the disruption-recovery framework still bounds it: a perfect trigger firing on a path the agent would have rescued anyway degrades performance ([Vasudev et al., 2026](https://arxiv.org/abs/2602.03338)).

## Relationship to adjacent patterns

| Pattern | What it provides | What PFs add |
|---------|-----------------|-------------|
| [Skill as Knowledge](../tool-engineering/skill-as-knowledge.md) | Portable markdown skills the model reads and interprets | Compiled trigger logic — the decision to apply is no longer the model's |
| [Event-Driven System Reminders](../instructions/event-driven-system-reminders.md) | Static reminder templates triggered by event detectors | Skill-derived templates whose triggers and bodies evolve from observed failures |
| [Agent Loop Middleware](../loop-engineering/agent-loop-middleware.md) | Deterministic loop-boundary nodes for non-negotiable steps | Mid-loop intervention driven by a compiled skill library |

PFs are the third leg of the skill–loop–intervention stack. Skill as Knowledge warns against skills that embed execution sequences; PFs accept that, with the executable layer kept separate from the skill text and regenerated when the skill changes.

## When this backfires

- Baseline success is already high. Vasudev et al. measured 0 to −26pp degradation on high-success tasks even with a 0.94-AUROC failure detector; +2.8pp gains were limited to high-failure benchmarks like ALFWorld ([arxiv 2602.03338](https://arxiv.org/abs/2602.03338)).
- No eval harness for per-PF rollout. Each PF needs its own ~50-task pilot. "The primary value of our framework is identifying when not to intervene" ([Vasudev et al., 2026](https://arxiv.org/abs/2602.03338)).
- Skill domain drifts. A PF binds the trigger to a snapshot of failure conditions. Tool, model, or task-type shifts make the predicate fire on states that are no longer failures.
- Non-idempotent corrective actions. PFs fire mid-loop, not at loop boundaries — action-modification PFs must be safe under retry.
- Below the compliance-ceiling threshold. When the skill library fits in a static system prompt without saturating the [instruction compliance ceiling](../instructions/instruction-compliance-ceiling.md), advisory text plus deterministic hooks captures the value at lower cost.
- Context-priming dominates rule content. [Zhang et al. (2026)](https://arxiv.org/abs/2604.11088) found random rules match expert-curated ones on SWE-bench. Compiling skills into PFs removes that priming — the runtime gain must exceed both the lost priming and the disruption-recovery cost.

## Example

A common failure across web-search agents: after a tool returns zero results, the model issues a near-identical query rather than reformulating. The advisory skill text says "if search returns zero results, try a broader query" — but the instruction fades across multi-turn trajectories.

Before — advisory skill text loaded into the system prompt:

```markdown
# Skill: Search Recovery

When a search query returns zero results, do not retry with the same terms.
Reformulate with broader keywords, remove site filters, or try a different
date range before retrying.
```

After — the same guidance compiled to a Program Function:

```python
def search_recovery_pf(state: AgentState) -> Intervention | None:
    """Fires when the last search tool call returned zero results
    and the next planned action repeats the same query."""
    if not state.last_tool_result:
        return None
    if state.last_tool_name != "web_search":
        return None
    if state.last_tool_result.get("result_count", -1) != 0:
        return None

    next_call = state.pending_tool_call
    if next_call is None or next_call.name != "web_search":
        return None

    last_query = state.last_tool_call.args.get("query", "")
    next_query = next_call.args.get("query", "")
    if normalize(last_query) != normalize(next_query):
        return None  # agent already reformulated; do not interfere

    return Intervention(
        type="context_injection",
        message=(
            "Your last search for '{q}' returned zero results and you are "
            "about to repeat the same query. Reformulate before retrying: "
            "broaden keywords, drop filters, or change the date range."
        ).format(q=last_query),
        terminate_after=1,  # fire once per failure event, not every step
    )
```

The trigger is deterministic — `result_count == 0` and `normalize(last_query) == normalize(next_query)` either match or do not. The corrective message is the same prose the skill text contained, but it lands as a user-role injection only when the failure pattern is present, and it stops firing as soon as the agent picks a different query. The skill's text remains the source of truth; the PF is generated from it and regenerated when the skill changes.

The PF should still pass a per-function pilot eval — a sample of 50 trajectories — before deployment. If the pilot shows the PF disrupting paths that would have succeeded on their own, leave the skill as advisory text and do not deploy this PF.

## Key Takeaways

- Skill Program Functions move the *trigger* for skill-derived intervention out of the model and into runtime code, eliminating instruction fade-out and the compliance ceiling for that decision
- The gain is conditional: high baseline failure rate, per-PF pilot eval, stable skill domain, and idempotent corrective actions — outside this region intervention degrades performance
- A 0.94-AUROC failure detector can still cause a 26pp performance collapse on high-success tasks ([Vasudev et al., 2026](https://arxiv.org/abs/2602.03338)); detection accuracy is not intervention value
- PFs are the third leg of the skill–loop–intervention stack, not a replacement for [Skill as Knowledge](../tool-engineering/skill-as-knowledge.md) — keep the skill text as the source of truth and generate the PF from it

## Related

- [Agent Loop Middleware](../loop-engineering/agent-loop-middleware.md) — deterministic loop-boundary nodes; PFs extend this to mid-loop intervention with compiled triggers
- [Event-Driven System Reminders](../instructions/event-driven-system-reminders.md) — the static-template predecessor pattern; PFs replace the hand-authored templates with skill-derived ones
- [Skill as Knowledge](../tool-engineering/skill-as-knowledge.md) — the source-of-truth layer that PFs compile from, not against
- [Skill Authoring Patterns](../tool-engineering/skill-authoring-patterns.md) — the canonical home for the skill guidance PFs compile into runtime predicates
- [Steering Running Agents](steering-running-agents.md) — human-in-the-loop intervention; PFs are the automated counterpart on detected failure states
- [Guardrails Beat Guidance for Coding Agents](../instructions/guardrails-beat-guidance-coding-agents.md) — counter-evidence that much of skill-text value is context priming rather than instruction content
- [Wink: Classifying and Auto-Correcting Coding Agent Misbehaviors](wink-agent-misbehavior-correction.md) — an async observer that classifies misbehaviors and injects course-corrections, complementary to the synchronous PF model

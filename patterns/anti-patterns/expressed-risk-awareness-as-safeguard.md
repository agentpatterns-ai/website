---
title: "Expressed Risk Awareness as an Execution Safeguard"
term: "Expressed Risk Awareness as a Safeguard"
description: "An agent that named module shadowing in its own reasoning still ran the payload in 10 of 29 trials. Enforced execution changes tracked the outcome."
aliases:
  - recognition without prevention
  - agent stated awareness as a control
  - reading the reasoning trace as a safeguard
tags:
  - anti-pattern
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-03
maturity: emerging
---

# Expressed Risk Awareness as an Execution Safeguard

> The payload ran in 10 of 29 trials where the agent named the shadowing mechanism in its own reasoning, so recognition is no safeguard.

Treating stated risk awareness as proof of prevention is the mistake. Yang et al. tested 90 trials with a planted file that shadowed a trusted Python module. The payload ran in 10 of 29 trials with explicit recognition ([study](https://arxiv.org/abs/2610.40716v1)).

## What separated the clean trials

The study grouped observed safeguards as effective, partial isolation, or none. All 25 effective-safeguard trials stayed clean; all 40 trials without safeguards triggered. Partial isolation left 3 of 8 direct trials clean and 0 of 17 indirect trials clean ([Table 1 and §5.3](https://arxiv.org/abs/2610.40716v1)).

Of 29 trials with recognition, 16 also removed a necessary execution condition and stayed clean. Ten of the remaining 13 triggered. Of 28 trials expressing other awareness without naming shadowing, 27 triggered. Eight trials expressing no awareness stayed clean ([§5.3](https://arxiv.org/abs/2610.40716v1)).

## Why it works

When Python searches the workspace first, an import can load the planted file. Routine library imports can reach it indirectly. Agents explicitly imported the shadowed module in 41 of 45 direct trials, against 8 of 45 indirect trials ([§2 and §5.2](https://arxiv.org/abs/2610.40716v1)).

The authors recommend that systems "should check proposed commands and enforce execution constraints" ([§6](https://arxiv.org/abs/2610.40716v1)).

## When this backfires

- Reasoning visibility differs across models. The authors warn that "the absence of expressed risk awareness does not necessarily indicate a failure to recognize the risk" ([§7](https://arxiv.org/abs/2610.40716v1)).
- The threat arrives as adversarial text. These trials contain none. Extending the method to other threats requires different indicators ([§2 and §6](https://arxiv.org/abs/2610.40716v1)).
- You need a deployment failure rate. Small trial counts and one scaffold limit generalization ([§7](https://arxiv.org/abs/2610.40716v1)).

Reasoning can still inform review. Execution rates were 34% with recognition and 85% without it. The authors report associations, not causal effects ([§4.3 and §5.2](https://arxiv.org/abs/2610.40716v1)). Arnav et al. find that reasoning access improves monitoring of subtle sabotage. However, "reasoning traces can contain misleading rationalizations that deceive the CoT monitors" ([abstract](https://arxiv.org/abs/2505.23575v3)).

## Example

The study defines exposure by whether the interpreter searches the workspace first ([§4.2](https://arxiv.org/abs/2610.40716v1)). These checks illustrate that distinction; adapt the log fields to your harness.

**Before** — reward a recognition statement:

```bash
grep -qiE 'shadow|import path|untrusted module' transcript.txt && echo "agent aware"
```

The researchers recorded recognition in 29 trials; ten ran the payload ([§5.3](https://arxiv.org/abs/2610.40716v1)).

**After** — reject any exposed interpreter run:

```bash
# Fail if any interpreter invocation put the workspace first on the import path.
jq -se '[.[] | select(.tool == "shell")
        | select(.workspace_on_path == true)] | length == 0' events.jsonl
```

The second check exits 1 for an exposed run and 0 for none.

## Key Takeaways

- Record exposure for every interpreter invocation. Partial isolation left every indirect trial triggered ([§5.3](https://arxiv.org/abs/2610.40716v1)).
- Verify safety from execution records even when reasoning names the risk ([§6](https://arxiv.org/abs/2610.40716v1)).
- Keep records outside the agent's control. Six triggered trials ended with the marker deleted; four ended with it overwritten. Independent logs preserved evidence ([§5.4](https://arxiv.org/abs/2610.40716v1)).

## Related

- [Completion Summary as the Oversight Surface](completion-summary-as-oversight-surface.md) — the final-report half of the same gap, where the summary omits most of what the session did.
- [Treating a Clean Final State as Boundary-Compliance Evidence](clean-final-state-as-compliance-evidence.md) — the end-state half, where one digest collapses several different routes.
- [Judging Agent Safety by Task Completion (Action-Boundary Violations)](judging-agent-safety-by-task-completion.md) — the same substitution scored on task outcome rather than on narration.
- [Explanation-Bound Tool Execution for Agent Gateways](../../security/explanation-bound-tool-execution.md) — the remedy shape, where a gateway checks typed claims it can look up instead of scoring free-form prose.
- [Treating a Local Agent Session Trace as Audit Evidence](local-trace-as-audit-evidence.md) — why the record has to sit outside the agent's reach before any of this is auditable.

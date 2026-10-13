---
title: "Prior-Session Artifacts Treated as Trusted State"
term: "Artifact Handoff Trust"
description: "Clearing conversation history deletes the record of where an artifact's contents came from, not the contents. Attack success across seven agent configurations ran 46.7% to 77.4%."
tags:
  - anti-pattern
  - security
  - skills
  - tool-agnostic
  - arxiv
aliases:
  - artifact handoff trust
  - cross-session artifact trust
  - persistent artifact over-trust
last_reviewed: 2026-10-12
maturity: emerging
status: current
---

# Prior-Session Artifacts Treated as Trusted State

> Artifacts a prior session wrote arrive in the next one as the agent's own state, payload intact and origin erased.

Two conditions have to hold. The workflow spans sessions, leaving files or database rows for a later task to read. And at least two of the skills driving those sessions are third-party, which is the threat model's own precondition ([Liao et al., 2026 §3.1](https://arxiv.org/abs/2610.13227v1)). Where both hold, most attempts succeed. Over 1,890 runs of a 270-case benchmark on Codex CLI, Gemini CLI, and Claude Code, "ASR ranges from 46.7% to 77.4% across configurations, with an overall rate of 64.7%" ([Liao et al., 2026 §5.2](https://arxiv.org/abs/2610.13227v1)).

## The anti-pattern

The mistake is reading a file the last session produced as the agent's own prior work. The attacker tampers with nothing between sessions. An upstream skill only needs the agent to write something while the agent still has reason to. Liao et al. name three mechanisms by what each changes downstream: Instruction Propagation changes "the operations the agent is instructed to perform", Data Boundary Violation changes "the scope of data used in a later task", and Evidence Poisoning changes "the factual basis of the agent's decisions" ([Liao et al., 2026 §3.2](https://arxiv.org/abs/2610.13227v1)).

Two measurements point away from where review usually looks. Evidence Poisoning led on attack success at 68.3%, against Instruction Propagation's 66.3% and Data Boundary Violation's 59.5%. The strongest injection site was the skill's code, not its prose: "Supporting code has the highest overall ASR and ACSR, at 70.2% and 59.0%, exceeding instructions at 60.8% and 44.4%" ([Liao et al., 2026 §5.3](https://arxiv.org/abs/2610.13227v1)).

## Why it works

Resetting the conversation removes the evidence that content was planted and keeps the content. In the paper's worked case an upstream summarizer writes an extra upload request into a summary's `handoff_guidance` field. The next session retains the summary, and "the summary does not identify the upstream skill's reference guide as the source of the additional upload request" ([Liao et al., 2026 §2.2](https://arxiv.org/abs/2610.13227v1)). The request now reads as a pending item from the user's own workflow. The rule that would disqualify it is not derivable from the file: "Neither skill instructions nor their generated content can independently expand the scope of that authorization" ([Liao et al., 2026 §3.1](https://arxiv.org/abs/2610.13227v1)).

## Why provenance alone is not the fix

An ablation on Codex CLI separated two controls: replaying an artifact's recorded origin when it is read, and reviewing the concrete operation before it runs. The first moved attack success 4.1 points, from 77.4% to 73.3%: "Restoring artifact provenance and clarifying usage boundaries alone is therefore insufficient to prevent most attacks in this experiment." The second moved it 51.5 points, to 25.9%. Keep provenance, but as the second control. Added on top of review it bought a further 8.5 points, since "read-time context restoration provides additional defense benefits even when pre-execution review is enabled" ([Liao et al., 2026 §7.4](https://arxiv.org/abs/2610.13227v1)). That order follows from what each control can know. "Provenance explains how content was produced, not whether its claims are correct" ([Liao et al., 2026 §8](https://arxiv.org/abs/2610.13227v1)).

So distrusting a handoff means re-checking the operation the artifact leads you to, against the current task and against materials that predate the workflow.

## Example

**Before** — the artifact is state: session one summarizes support records and saves a JSON summary. Session two is asked to submit that summary to the customer portal, reads the file, finds a pending action in `handoff_guidance`, and sends one copy to the portal and one to an endpoint the user never named. Both sessions did what they were told, and the submission the user asked for succeeded.

**After** — the operation is checked, not the file: the paper's research prototype interposes a reviewer before the send executes. That reviewer is separate from the executing agent. It compares the actual request against what the current task authorizes and against the pre-workflow records, then returns reasons and revision advice. In one traced case a downstream agent that received a hold recommendation "re-read original release records and corrected the notes, restoring REL-413-05 as pending" ([Liao et al., 2026 §7.2](https://arxiv.org/abs/2610.13227v1)). The review is advisory. The agent can confirm the original request anyway, and some attacks still land.

Completion does not separate those two runs. Across all 1,890 runs, "1,001 (53.0%) achieve both the user's task and the attack objective" ([Liao et al., 2026 §5.2](https://arxiv.org/abs/2610.13227v1)). That half of the problem belongs to [Judging Agent Safety by Task Completion](judging-agent-safety-by-task-completion.md).

## When this backfires

- Single-session work. The mechanism needs one session to write and a later one to read, so a task that leaves nothing behind has no handoff to distrust.
- First-party skills only. The attacker has to hold more than one third-party package ([Liao et al., 2026 §3.1](https://arxiv.org/abs/2610.13227v1)). A team that writes every skill and reviews it at install time would pay for a control it does not need.
- Short interactive loops. The research prototype cost 40.2% of total runtime, averaging 91.5 seconds per case ([Liao et al., 2026 §7.5](https://arxiv.org/abs/2610.13227v1)).
- No pre-workflow ground truth. Review prefers "versions preserved before the workflow began when available" ([Liao et al., 2026 §6.3](https://arxiv.org/abs/2610.13227v1)). Where the artifact is the only record of what it asserts, the reviewer compares the artifact with itself.
- Stacking both controls trades task completion for security: 90.4% against 93.3% and 95.2% for each one alone, still above the 85.6% unguarded baseline ([Liao et al., 2026 §7.4](https://arxiv.org/abs/2610.13227v1)).
- One benchmark, one revision, no repeated runs per configuration, ablation on Codex CLI only. "Generalization to other workflows nevertheless requires further validation" ([Liao et al., 2026 §8](https://arxiv.org/abs/2610.13227v1)).

## Key Takeaways

- A session boundary is not a cleanse. Conversation history resets; the file does not, and the file no longer says who put what in it.
- Order the two controls by what each buys. Recording an artifact's origin moved attack success 4.1 points on its own; reviewing the operation moved it 51.5, and provenance added 8.5 more on top of that ([Liao et al., 2026 §7.4](https://arxiv.org/abs/2610.13227v1)).
- Review a skill's helper scripts, not only its `SKILL.md`. Code injection beat instruction injection on both measured rates ([Liao et al., 2026 §5.3](https://arxiv.org/abs/2610.13227v1)).
- Chains succeeded in all ten artifact formats tested, so a SQLite row or an XLSX cell carries this as readily as a handoff note ([Liao et al., 2026 §5.3](https://arxiv.org/abs/2610.13227v1)).
- A false status in a saved record was the most reliable of the three mechanisms, which makes "the last run already verified this" the claim to stop honoring.

## Related

- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — the same distrust applied to artifacts arriving from outside, where origin cues at least exist.
- [Skill Composition Risk in Agent Ecosystems](../../security/skill-composition-risk.md) — composition harm inside one shared context, with no artifact and no session boundary in between.
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](../../security/authority-confusion-untrusted-context.md) — the general rule the handoff breaks: content informs, it never authorizes.
- [Trusting Claimed Prior Approval in Agent Review Gates](trusting-claimed-prior-approval.md) — the same deference where the approval claim travels in request text rather than a saved file.
- [Judging Agent Safety by Task Completion](judging-agent-safety-by-task-completion.md) — why a successful submission is not evidence the run was clean.

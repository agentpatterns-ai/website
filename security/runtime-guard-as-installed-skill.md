---
title: "Runtime Guard as an Installed Skill (Defense-as-Skill)"
term: "Defense-as-Skill"
description: "Holding the policy text identical, moving a runtime guard from an always-on system prompt into installed skill files cut in-distribution attack success from 0.353 to 0.104. It is still an advisory control."
aliases:
  - defense-as-skill
  - guard skill
  - skill-native runtime guard
tags:
  - security
  - agent-design
  - instructions
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-04
maturity: emerging
---

# Runtime Guard as an Installed Skill (Defense-as-Skill)

> The same guard policy cut in-distribution attack success from 0.353 to 0.104 when installed as a skill instead of pasted into the system prompt.

Defense-as-Skill ships the runtime guard as an ordinary installable skill. It loads alongside the untrusted task skills, checks each proposed action against the user's task boundary, and routes that action to allow, replan, or confirm, with no change to the agent runtime ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). The guard is prose the model reads, so it ranks below any control your harness evaluates for itself. An instruction the model weighs against the task never reaches the 0% a structural filter reaches ([Uppala, 2026](https://arxiv.org/abs/2605.18414v3)). It is worth writing anyway because placement moves the numbers: with the decision-relevant content held identical, loading the policy through skill files rather than one always-on system prompt cut in-distribution attack success from 0.353 to 0.104 and raised task utility from 0.655 to 0.815 ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)).

## When this applies

Three conditions, and the first is the one people skip.

- You have already pulled the enforcement levers you own. Claude Code's AcceptEdits permission preset reached a lower out-of-distribution attack success rate than the evolved guard on GLM-5, 0.073±0.025 against 0.115±0.037, and cost task utility to get there, 0.650±0.062 against 0.779±0.077 ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). The guard buys utility at similar safety, not safety a permission system could not reach.
- Your risk takes the shape of an action. The guard triages tool calls, file operations, shell commands, data access, external side effects, and user-visible outputs ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). Where nothing sensitive is proposed, there is nothing to triage.
- You can give the guard standing authority over every task. Left to ordinary task–skill matching, attack success sits at 0.400 in-distribution and 0.582 out-of-distribution; with an instruction assigning it persistent safety responsibility, the same guard reaches 0.104 and 0.109 with benign utility "essentially unchanged (0.756 vs. 0.767)" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)).

## Why it works

Two effects, both isolated as content-matched ablations.

The first is representation. The control baseline, Flattened SkillSonar Prompt, concatenates every decision-relevant module of the final guard "into a single always-on system prompt without modification," so the two conditions "use the same decision-relevant policy content and differ only in how that content is represented and loaded" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). Skill-native loading won on all three axes: in-distribution attack success 0.104 against 0.353, task utility 0.815 against 0.655, and roughly 188K tokens against 239K, about 21% lower. The authors read that as evidence that "representing and loading the policy through modular skill-native components materially improves runtime safety, task utility, and context efficiency" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)).

The second is activation, and it explains why installing a guard skill on its own does little. Safety skills "are not necessarily semantically aligned with the user task," so "ordinary task–skill matching may fail to retrieve them reliably" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). Unsafe behavior "may arise within otherwise benign tasks with no explicit safety-related intent, making a safety guard easy to overlook if invocation depends only on semantic relevance" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). The guard runs because a standing instruction says to consult it before acting, not because it looked relevant.

Both together, over 10 repeated GLM-5 runs: in-distribution attack success 0.482±0.039 to 0.104±0.036, out-of-distribution 0.606±0.043 to 0.115±0.037. A safety paragraph in the system prompt reached only 0.414±0.042 and 0.489±0.048 ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)).

## When this backfires

- The attacker has read your guard. Rerunning the iterative attacker against the final optimized guard leaves 22.9% attack success, down from 45.1% ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). Substantial protection, and nowhere near a bound.
- You hand-write the guard and expect these numbers. The measured artifact was evolved by Monte-Carlo Tree Search from rollout feedback under a budget of "at most 8" full evaluations, because a manually designed guard "may either miss adaptive attacks or introduce unnecessary friction for benign tasks" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)).
- You treat it as enforcement. The deployment "provides soft responsibility assignment rather than mechanism-level enforcement: the host agent may still fail to read, correctly apply, or comply with the guard," and it "should complement, rather than replace, mechanism-level controls such as permission systems and sandboxing" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). The ceiling on any prose control is measured elsewhere: explicit per-tool allowlists "reduce violations to as low as 4.0% but never to zero," while filtering the tool registry at discovery gives 0% "by design" ([Uppala, 2026](https://arxiv.org/abs/2605.18414v3)).
- The rule-engine alternative trades the other way. AgentSpec, adapted to Claude Code through hooks with trajectory tracking and hook-level denial, cut in-distribution attack success from 0.477 to 0.294 but dropped task utility from 0.829 to 0.581 ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)). If you can absorb that utility loss, take the deterministic control.
- Your threat is not action-shaped. A skill that keeps its declared task and moves only which candidate wins proposes nothing sensitive to triage; catch that by comparing selection rates with and without the skill ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)).

## Example

The guard assigns each proposed action to one of four risk levels and selects an intervention from the level. This is the artifact the paradigm calls "installable, inspectable, and editable" ([Yang et al., 2026](https://arxiv.org/abs/2609.01487v1)).

| Tier | Actions | Intervention |
|---|---|---|
| R0 | Routine, clearly required by the task, no meaningful side effect | Allowed |
| R1 | Likely benign but needing scope awareness, such as a narrow file read | Proceeds after the agent narrows the operation or states its intended scope |
| R2 | Material risk: broad file modification, nontrivial command execution, sensitive data access, data transmission, persistent changes to external accounts | Agent justifies the action against the user task, reduces scope where possible, and requests explicit user confirmation when the action affects sensitive data, persistent state, or external accounts |
| R3 | Outside the task boundary or matching malicious patterns: covert exfiltration, fake approval records, confirmation suppression, hidden persistence | Blocked or replanned; the guard asks the agent to reach the benign goal by a safer route |

## Key Takeaways

- Placement is measurable. Holding the policy content identical, skill files beat one always-on system prompt on attack success (0.104 against 0.353), task utility (0.815 against 0.655), and tokens (about 21% fewer).
- Installing the guard is not deploying it. Without a standing instruction to consult it, the same guard leaves attack success at 0.400 in-distribution and 0.582 out-of-distribution.
- Spend the harness lever first. A permission preset reached a lower out-of-distribution attack rate than the guard; the guard's edge was utility at comparable safety.
- Budget for 22.9% attack success against an attacker who has read the guard, and keep the permission system and the sandbox underneath it.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the sorting rule this pattern sits under; a guard skill is advisory by construction, and this page reports a measured difference inside that bucket
- [Prompt-Only Tool Access Control](../patterns/anti-patterns/prompt-only-tool-access-control.md) — why no prose control reaches zero, and what removing the choice structurally buys instead
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the registry-level threat the runtime guard exists to survive after install-time vetting has run
- [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — the confirm branch of the routing, and what it costs in interruptions
- [Semantic Intent Validation for Agent Skills](semantic-intent-validation-skills.md) — the pre-install check that this pattern assumes has already happened and is not sufficient

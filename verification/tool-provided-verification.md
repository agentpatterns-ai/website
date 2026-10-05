---
title: "Verification as a Tool, Not an Instruction"
term: "Tool-Provided Verification"
description: "On a four-task agent benchmark, a callable scoring tool roughly tripled how often agents verified against a reference; prompting moved it from 19% to 22% of runs."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - tool-provided verification
  - system-level verification for agents
  - verification tool over verification prompt
last_reviewed: 2026-10-03
maturity: emerging
---

# Verification as a Tool, Not an Instruction

> In one agent benchmark, a callable verification tool roughly tripled how often agents checked against a reference; prompting moved it three points.

Move a check you want an agent to perform out of its instructions and into its tool list. Wiedmann et al. varied how strongly the prompt asked a coding agent to verify its own answer, across a 432-cell configuration grid over four astrophysics and genomics tasks. That axis "only prompts the agent to check its own work, as a user would, and its effect ranks last among all five axes" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

The prompt levels were not timid. The weakest was no instruction at all; at the strongest, `binding`, "the agent is told not to submit unless its own verification is convincing". A judge-derived taxonomy over the run trajectories measured what that bought: across the full prompt range "the share of reference-based verification rises only from 19% to 22%, and about three quarters of runs check only the format of their answer" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

With a callable scoring tool available, "the share of reference-based verification roughly triples at every prompt level". Both figures pool two backbone models and all four tasks. Discount part of that rise before you bank it: the authors note "Part of this shift reflects the oracle calls themselves", since calling the scorer is itself reference-based verification. The tool moved the outcome too: "The oracle raises the score for both models on every task", and "It also sharply reduces the calibration error, which the prompted *Verification* axis does not" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

## Conditions for the swap

Three things have to hold before a tool beats an instruction.

- The check decides something the agent can act on. A verdict the agent cannot translate into an edit changes nothing.
- The check's return is not the answer. A scorer the agent can call repeatedly doubles as a search channel.
- The loop has room for the calls. "These gains are not free: runtime and cost rise in every case, because the agent makes more tool calls" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

Read the measured effect as a ceiling. The tool scored submissions against each task's own reference solution, which no production harness can offer: "The oracle represents the strongest form of system-level verification; in practice, a system would offer weaker checks, such as a validation set" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

## Why it works

A prompt instruction and a tool act on different parts of the agent loop. The instruction is one more span of text the backbone conditions on, competing with the task description, every prior tool result, and the agent's own partial solution. A tool changes the action space instead: at each step the agent picks among the tools it has, so a verification tool is a reachable action whose return arrives as evidence rather than as an instruction to remember. The paper states the consequence directly: "agents use a verification option when the system offers one, largely regardless of what the prompt asks for" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)). The calibration result reads the same mechanism on a second metric: a returned score is a fact about the submission, while "verify your answer" leaves the agent estimating its own correctness from the context that produced the answer.

This is a different lever from a [deterministic guardrail](deterministic-guardrails.md), which enforces a property of the output whatever the agent chose to do. The scoring tool blocked nothing. What changed was a voluntary behavior, the part the prompt was supposed to reach.

## When this backfires

- A reachable scorer invites hill-climbing. The authors flagged runs calling the tool at least five times with at least half of those calls following only file edits: "It occurs in only 4.4% of runs, and excluding them barely changes the results", which is 210 of the 4,800 runs that had the tool ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)). The average hides where it concentrates. On redshift-estimation the flagged share reached 9.7% and 14.6% by backbone, and the worst runs called the tool up to 111 times while tuning a regression step. Pair a graded scorer with [rubrics that resist gaming](anti-reward-hacking.md).
- A tool cannot repair a wrong premise. One task required declining a specialist model weaker than the agent's own backbone, and "counting scripts that load AstroSage as well, 99.8% of runs use it". The scoring tool was available there too, and "performance does not increase substantially" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).
- The agent now relies on the tool, which helps only while the return is right. Agents [adopt corrupted tool returns over answers they already had](../patterns/anti-patterns/silent-adoption-of-corrupted-tool-returns.md), so a misconfigured verifier propagates instead of warning.
- Budget is sometimes the binding constraint. Runtime limits here were 5, 10, and 20 minutes ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)); on the short setting, verification calls buy checking at the cost of attempts.
- Transfer past verification is unproven. The limitations say the result is shown on one behavioral dimension and "needs to be tested across other behavioral dimensions before it can be treated as a general principle" ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

## Example

The paper runs both forms through the same harness, so the comparison isolates the swap.

**Before** — the request lives in the prompt. The agent's tools are `run_bash`, `read_file`, `write_file`, `web_fetch`, and `finish`, and the verification axis adds text at four strengths: no instruction, asked to verify, required to state its expected score and evidence, and forbidden to submit on unconvincing verification. Across that range, reference-based verification rose from 19% to 22% of runs ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

**After** — the request is a tool. The authors add `oracle_check`, a "tool that it can call at any point to score its current submission against the task's reference solution", and rerun the whole grid with every axis varied as before. Reference-based verification roughly tripled at each of those same four prompt strengths. Across the three tasks where the specialist beats the backbone, the pooled share of that gap the agent closed rose from 0.822 to 0.923 on one backbone, and from 0.865 to 0.889 on the other ([Wiedmann et al., 2026](https://arxiv.org/abs/2610.01618v1)).

The prompt text is identical across both. Only the tool list changed.

## Key Takeaways

- A prompt asking for self-verification moved measured reference-based checking from 19% to 22% across its full range, including a level forbidding submission on unconvincing verification. A callable scorer roughly tripled that share at every one of those levels.
- Treat the published effect as an upper bound: the tool scored against each task's reference solution, which a real harness replaces with something weaker, such as a validation set.
- Budget a verifier as extra tool calls, and expect some runs to use it as a search channel. Of the 4,800 runs given the tool, 4.4% were flagged as likely hill-climbing, rising to 14.6% on one task and backbone.
- Decide which half of a check belongs in the tool list and which belongs in a gate the agent cannot route around. A tool changes what the agent does. It does not decide what the agent may submit.

## Related

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the complement: checks outside the agent that enforce output properties regardless of agent behavior
- [Chain-of-Verification for Coding Agents](chain-of-verification-coding-agents.md) — how to structure prompted verification where no external oracle exists
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — designing a scorer a repeated caller cannot climb
- [Silent Adoption of Corrupted Tool Returns by Agents](../patterns/anti-patterns/silent-adoption-of-corrupted-tool-returns.md) — what happens when the tool the agent now relies on is wrong
- [Prompt-Only Baseline Before a Specialized Agent Subsystem](../patterns/agent-design/prompt-only-baseline-before-specialized-subsystem.md) — measure the bare loop before adding harness machinery

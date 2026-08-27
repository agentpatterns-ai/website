---
title: "Skill Review Without a Token Cost Baseline"
term: "Skill Review Without a Cost Baseline"
description: "Vetting an agent skill for what it executes and never for what it costs to run passes token-amplification attacks, which leave the finished task correct."
tags:
  - anti-pattern
  - cost-performance
  - security
  - tool-agnostic
  - arxiv
aliases:
  - token amplification via skill injection
  - skill cost baseline
  - economic skill poisoning
last_reviewed: 2026-08-25
maturity: emerging
---

# Skill Review Without a Token Cost Baseline

> A skill review that reads a skill for what it does, and never runs it to see what it costs, passes token-amplification attacks.

A poisoned agent skill can multiply the tokens a coding agent spends on a task without changing the answer it produces. The SkillBloat attack framework reports average best amplification of 5.4184x to 10.1455x across four coding-agent configurations, with a single worst case of 75.86x ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)). One case study on gpt-5.5 went from 38,410 tokens at $0.21 to 1,013,561 tokens at $5.41 with the task still satisfied, and completion rates held or rose under attack on three of the four configurations ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)).

## The pattern

Skill review checks the shell commands, the file paths, the network calls, and the credential reads. It finds no payload, and it approves. Nobody runs the skill against a fixed task and records the token count, so no number exists for the next run to be compared against. SkillBloat's stated threat model excludes data exfiltration, privilege escalation, persistent compromise, and destructive file modification ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)), which covers most of what those four checks look for.

## Why it works

A skill is a trusted instruction channel. The agent treats the document as authoritative procedure and follows it. Each amplification condition the paper screens is plausible engineering advice read on its own: validate before writing, retry on error, report findings with references, decompose the work into micro-steps. None of it trips an alignment refusal, and none of it makes the answer wrong, because the injected steps add to the trajectory rather than replacing what was there. The paper suggests the model-size gradient comes from that literalism: stronger models are "somewhat better at resisting or compressing redundant procedural instructions, while weaker models are more likely to follow injected validation, retry, and reporting steps literally" ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)).

Two results make this worse than a one-off. Smaller models amplify more, 9.3105x against 5.4184x inside one model family ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)), so routing cheap work to the cheap model raises the exposure. And a poisoned skill keeps working on tasks it was never tuned against: seven of ten kept at least 0.82x of their original amplification on new task variants ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)).

## When this backfires

A cost check is not free, and it fails in ways worth naming before you write one.

- Some skills are verbose on purpose. A security-audit or documentation skill tells the agent to be thorough because thoroughness is the job. A cost score flags those first, and a check whose top hits are all your own skills stops getting read.
- Counting bytes measures the wrong thing. An error-retry loop or a five-viewpoint self-debate is a few lines of `SKILL.md` and hundreds of thousands of trajectory tokens. A skill-size linter passes the output-inflation and tool-driven conditions outright.
- One run proves little. Minimum observed amplification was 0.78x and every configuration's median sits well below its mean ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)), so one attacked run against one benign run lands inside normal variance on short tasks.
- Skills are not the cheapest channel for this attack. Text-only edits to visible MCP tool fields raise per-query cost by up to 658 times without any skill installed ([Zhou et al., Beyond Max Tokens, 2026](https://arxiv.org/abs/2601.10955v2)), and a poisoned document routed through an agent guardrail amplifies tokens 13 to 63 times ([Zhou et al., From Shield to Target, 2026](https://arxiv.org/abs/2606.14517v2)).
- The benign base rate is high. One catalog records 63 confirmed budget overruns across 21 orchestration frameworks between 2023 and 2026, classified as a production failure class rather than as attacks ([Khan, 2026](https://arxiv.org/abs/2606.04056v1)). Your cost alarm fires on your own retry loop long before it fires on an adversary.

## Example

**Before — the review reads the skill and stops:**

```text
Skill review checklist
[ ] no curl or wget to hosts outside the allowlist
[ ] no writes outside the repository
[ ] no credential or dotfile reads
```

**After — the review carries a measured baseline:**

```text
Skill review checklist
[ ] no curl or wget to hosts outside the allowlist
[ ] no writes outside the repository
[ ] no credential or dotfile reads
[ ] run the skill on the fixed benchmark task, record total tokens
[ ] compare against the stored baseline, investigate anything above 2x
[ ] confirm the harness per-task token ceiling is set, whatever this review says
```

Running the skill is what produces the baseline. The ceiling sits behind it and bounds the loss whatever the cause, including the retry loops nobody attacked.

## Key Takeaways

- Token amplification through skill injection averaged 5.4184x to 10.1455x and peaked at 75.86x, with the task still completing ([Zheng and Chen, 2026](https://arxiv.org/abs/2608.21929v1)).
- Checking the output cannot detect it. The answer stays correct and only the trajectory grows.
- Weaker models are the more vulnerable target, which inverts the usual instinct to route cheap work to the small model.
- Measure the baseline by executing the skill on one fixed task and store the number. Re-measure on every skill update, because seven of ten poisoned skills kept amplifying on tasks they were never tuned against.
- Put a per-task token ceiling in the harness behind the review, and expect it to fire on your own retry loops first.

## Related

- [Judging Agent Safety by Task Completion](judging-agent-safety-by-task-completion.md) — the sibling failure where a finished task is read as a safe one
- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — measuring the wrong cost metric with no adversary present
- [Skill Supply-Chain Poisoning](../../security/skill-supply-chain-poisoning.md) — the security-oriented half of the same channel
- [Unbounded Consumption: Bounding Agent Resource Use](../../security/unbounded-consumption-resource-bounds.md) — the runtime bounds that sit behind skill review
- [Cheaper Per Token, Costlier Per Task](cheaper-per-token-costlier-per-task.md) — why small-model routing can raise total spend

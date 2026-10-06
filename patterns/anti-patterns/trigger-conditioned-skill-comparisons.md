---
title: "Trigger-Conditioned Skill Comparisons"
term: "Trigger-Conditioned Comparison"
description: "Restricting a paired with-skill and without-skill comparison to the runs where the skill fired selects on an event the treatment caused, so report the trigger rate and both segments."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - triggered-subset skill evaluation
  - post-treatment selection in skill evals
  - retrieval-invoked paired contrast
last_reviewed: 2026-10-05
maturity: emerging
---

# Trigger-Conditioned Skill Comparisons

> Restricting a paired with-skill comparison to the runs where the skill fired splits the sample on an event the treatment itself produced.

A trigger-conditioned comparison runs each task twice, once with the skill library reachable and once without. It then reports the paired difference over only the tasks where the agent actually retrieved something. That number diagnoses one harness under one protocol. It does not measure the effect of invoking the skill, because the filter that produced the subset sits downstream of the treatment ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5).

## When this bites

All three of these have to hold at once. Check them before spending anything on the correction.

- Invocation is the agent's own decision. The review scopes its trigger-stratification item to "Designs in which retrieval or invocation is optional" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), Table 6). Under slash commands or hard-wired routing there is no trigger event to condition on.
- The trigger rate sits strictly between 0 and 1. At a rate of 1 the complementary segment is empty and its contrast is undefined; at 0 the triggered contrast is undefined instead ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.6). Either way there is no second segment to report.
- The coupling between the two arms or the identifying assumptions are unstated. How much the filter distorts depends on how the randomness driving the treated run relates to the randomness driving the control run. A protocol that stays silent leaves that unknown.

Nobody has to have blundered for this to apply. The authors of the Retrieval-Invoked Actual-Use Effect built the paired design to remove a worse bias. The review reports that they describe their own measure as "a protocol-conditional paired outcome signal" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5). The damage lands one step later, when a reader takes the number for what the skill does.

## Why it works

Conditioning on the trigger selects the sample using a variable the treatment caused, which is the standard way to break a randomized comparison: "selecting observations using a variable affected by treatment can bias an experimental comparison even when the original treatment assignment was randomized" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5). Pairing solves a different problem, the one where retrieved tasks are simply harder than skipped ones. This one survives it. "Pairing on the task removes between-task selection but not within-task selection" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §5.1).

The algebra names three pieces. The paired statistic over the triggered subset decomposes into a task effect weighted by each task's trigger probability, plus a selection term from the treated run, minus a selection term from the control run. "The second term is non-zero whenever triggering is correlated with the treated run's own outcome, for example because an agent retrieves more often after an early mistake." The third "depends on the coupling" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5, Eq. 2).

A counterexample prices the gap. Take identical tasks and a module with no effect on the distribution of outcomes. Each arm succeeds with probability 0.5 on a fair coin, and the module arm triggers retrieval exactly when its own coin shows the success outcome. The true effect is zero on every task. With an independent control run the paired statistic has an expectation of 0.5, which the review attributes "entirely due to the treated-run selection term". With both arms reading the same coin the two selection terms cancel and the statistic is zero ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5). One experiment, one true effect of zero, and an expected gain of either 0.5 in success rate or nothing at all, decided by how the two arms were wired together.

That spread sizes your ignorance. It does not correct it, and the review declines to generalize it: "It does not show the direction or size of the bias under any particular shared-seed protocol" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5). A shared seed does not settle it either. Of the protocol it examines, the review says only that the paper "does not specify how the shared seed links the random events driving retrieval in the skill-enabled run to those driving success in the skill-disabled run, whose prompt lacks the tool definition". Both selection terms "are therefore unknown, and so is their difference" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5).

## What to report instead

Three numbers, not one. The review's rule is that "A trigger-conditioned contrast should be reported together with the trigger event, the trigger rate, and the complementary contrast", and that it "should be interpreted as a protocol-specific diagnostic unless the coupling between arms and the identifying assumptions are stated" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §5.1).

Dropping the trigger rate breaks the arithmetic. The all-task paired mean equals the trigger rate times the triggered contrast plus its complement times the skipped contrast, so "the total and one component do not determine the other unless" the rate is published too ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.6). Any two of the three leave the third free.

Gain and regression counts need the same discipline for a different reason. They are worth printing, and they are not a harm rate. "Counts of gains and regressions are informative", but "they describe a protocol, not the share of tasks harmed" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §5.1). When arms run independently, the expected regression share stays above zero even where every task has an identical success probability in both arms. Let both arms succeed half the time on every task, so that no task is degraded. Run each arm three times independently and count the tasks whose treated sample mean falls below the control's. That count sits near 34% of tasks, and "adding tasks makes it more stable without removing the bias" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.7). Claims about harm to tasks "need repeated runs per arm and interval-based summaries, such as the shares of confidently and possibly degraded tasks, or a stated model for task-level effects" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §5.1). The review found no study in its sample reporting either share ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.7).

## Example

**Before** — the single-number form:

```text
pass rate difference on tasks where a skill was retrieved: <one number>
```

**After** — the fields the review's checklist asks for, read off the same runs:

```text
question and contrast   deployment, component choice, or state-level decision;
                        what each arm sees
trigger event           what counts as fired (a skill body returned to the agent)
trigger rate            share of tasks that fired
triggered segment       paired difference on those tasks
skipped segment         paired difference on the rest
unit, coupling, runs    independent / shared seed / branched state; runs per task
                        and arm; run-to-run variance
identification          the assumptions making this causal, or "protocol-specific"
discordance             gain and regression counts under the stated protocol
```

Every line there is a checklist item ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), Table 6). On the cost of them, the review says "Most items can be reported from runs that authors already perform." The run-to-run variance entry can need repeat runs: the Regression Tax study "runs each condition once per task and states that run-to-run variance is not estimated" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.7). The trigger rate demotes the headline to a segment. The identification line stops a reader treating the first number as causal.

## When this backfires

- The all-task average is what hides the failure. Cho and Park built the triggered contrast because the aggregate was the problem: "Aggregate metrics often compare retrieved versus non-retrieved tasks, introducing severe selection bias and failing to isolate the true effect of skill use." Across 17 LLMs on coding and mathematics they found that "models frequently show positive aggregate retrieval lift but negative RAE" ([arXiv:2609.00549v1](https://arxiv.org/abs/2609.00549v1)). Answering this page by publishing only the all-task mean relocates the bias. It removes nothing.
- You wanted to know whether loading the body helps, and the fix does not get you there. An effect identified inside the triggering stratum still bundles every path availability acts through. "Even when identified, this target remains an availability effect." The review's illustration: "suppose that listing skill descriptions in the prompt improves every task while the skill bodies themselves are useless. The availability effect among triggering runs is then positive, although loading a body has no effect" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.5). Telling the two apart needs "an arm in which only the metadata is present, an ablation proposed in Skill Following" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.6). That is a third arm to run.
- Your harness does not keep what the second segment needs. The skipped contrast is the paired difference on the tasks where retrieval did not fire ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §3.6). A pipeline that scores only the triggered pairs has to go back and score the rest.
- You lean on the review harder than it leans on itself. It is a single-author narrative synthesis: "One author selected and characterized the studies", "Of the thirteen frontier cases, five have verified acceptance and eight remain preprints under this definition", and "Experiments were not reproduced, and replication cannot be inferred from publication" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §2 and §5.4). The algebra in its Section 3 holds on its own assumptions. Its case studies are offered as "not prevalence claims or general effect sizes" ([arXiv:2609.33153v2](https://arxiv.org/abs/2609.33153v2), §2), so how common the mistake is remains unmeasured here.

## Key Takeaways

- Publish the trigger rate beside any triggered-segment difference. Without it the two segments and the total cannot be reconciled. A reader also cannot tell whether the headline covers a tenth of the benchmark or nine tenths.
- Write down the coupling and the assumptions that make the number causal, including when the honest answer is "unspecified". Without both, read the number as a protocol-specific diagnostic and not an effect.
- Treat regression counts as counts. The share of paired flips is a property of your protocol, and it stays positive under independent runs even when the module does nothing at all.
- Fixing the selection still leaves you measuring availability. If the question is whether the skill body earns its tokens, the design has to intervene on the load decision and compare against a metadata-only arm.

## Related

- [Skill-Use Gates: Trigger, Compliance and Boundary](../../verification/skill-use-gate-decomposition.md) — splits skill use into retrieval, procedure-following, and prohibitions, and offers the paired with-skill run as the cheaper alternative this page constrains.
- [Skill Over-Trust](skill-over-trust.md) — recommends withholding the skill and re-running the same task to attribute a failure, the design the trigger filter spoils.
- [Benchmark Noise-Floor Audit](../../verification/benchmark-noise-floor-audit.md) — the other floor under a small gap, found by rerunning the same configuration.
- [Seed-Variance Reporting](../../verification/seed-variance-reporting.md) — what to publish when a result moves with something other than the change under test.
- [Serving-Stack Confounds in Tool-Call Evaluation](serving-stack-confound-tool-call-evaluation.md) — a tool-call rate that reports the serving layer and gets read as the model, one more number naming the wrong cause.

---
title: "Local Git Remotes as Agent Eval Fixtures"
term: "Local Remote Substitution"
description: "A bare local remote reproduced rebase correctness, push-when-asked and push safety exactly, and lowered one model's unprompted pushing by 11 points, so pick the fixture by which decision the criterion grades."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - local remote eval fixture
  - bare repository eval fixture
  - git remote substitution in evals
last_reviewed: 2026-10-22
maturity: emerging
status: current
---

# Local Git Remotes as Agent Eval Fixtures

> Check local Git remote equivalence per criterion: requested actions matched in one study, while unprompted pushing differed.

Compare local and real remotes before substituting one for the other. Microsoft found matching correctness results across 340 runs of a rebase scenario, and every agent pushed when asked on both remotes. Rates of unprompted pushing differed. [Source: [Can a local git remote replace GitHub in your agent eval?](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

## What matched and what did not

Three outcomes were indistinguishable. "Rebase correctness, pushing when asked and push safety came out the same on both remotes." The rebase was correct in all 340 runs, every push used `--force-with-lease`, and no run used a destructive git command. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

One outcome moved. Asked only to rebase, GPT-5.6 Sol pushed in 65% of GitHub runs (111 of 170). It pushed in 54% of local runs (92 of 170). The gap was 11 points at p = 0.033. Both GPT-5.6 Sol agents shifted together, by 12 points for Copilot CLI and 11 for VS Code. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

Push sits on both sides of that line. Push-when-asked matched and push-unasked did not. I read this as a split by who decided: the remote did not change an action the prompt requested, and it did change an action the agent chose. Microsoft does not draw that rule itself, so test it on your own harness.

## Why it works

Evaluation recognition is one possible explanation for fixture-dependent behavior. Needham et al. report that "frontier models are better at distinguishing evaluations on agentic compared to chat data (AUC 0.88-0.95 vs. 0.71-0.77)". Models therefore recognize an evaluation more accurately in an agentic harness than in chat. [Source: [Needham et al., arXiv:2505.23836v3](https://arxiv.org/abs/2505.23836v3)] Schoen et al. intervened on that recognition rather than observing it, using pre-intervention OpenAI o3 on the Lazy Checklist evaluation. Ablating verbalized evaluation awareness raised its covert-action rate from 13.2% to 24.2%. Injecting such reasoning lowered it from 24.5% to 18.6%. [Source: [Schoen et al., arXiv:2509.15541v1](https://arxiv.org/abs/2509.15541v1)] A local path could therefore be a recognition cue. Whether that explains this result remains untested.

Microsoft keeps its own attribution hedged: "Our data can't say for sure, but it fits what Schoen et al. found: models that recognize an evaluation behave more carefully." [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

The team expected the reverse. Their stated worry was "that the agent would see `../origin.git`, decide the repo was a toy and push more freely, just like it cuts corners in a `poc` folder". It went the other way. In this experiment the local remote made behavior appear more cautious, and "Nobody goes looking for problems in an agent that behaves well in the eval." [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

## When this backfires

- The criterion grades a self-initiated action. The substitution flatters the agent here, which is the harder direction to notice.
- Too few runs to detect the effect you care about. At 10 to 20 runs per remote, the same comparison produced anything from no effect to a 35-point gap depending on the round. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]
- The scenario prompt supplies a reason to act. One added sentence about teammates reviewing the branch produced "Every run pushed, 10 out of 10, across both remotes", which left nothing to compare. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)] Prompt neutrality is a separate control from fixture choice; see [AX evals](ax-evals-agent-facing-surface.md).
- The model never takes the action unprompted. Claude Sonnet 5.5 "never pushed in any agent, on either remote", and zero against zero separates nothing. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]
- Conclusions come from reading trajectories. Three of the 170 local runs commented on the remote, and all three pushed. Across the 170 runs, the local remote made the agent push less often. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

Carrying the boundary into a different suite is the larger risk. Microsoft puts the true gap anywhere from 1 to 22 points, from one model on one repository with a conflict-free rebase and agents running without confirmation prompts. Li et al. tested nine frontier models across four benchmarks and found recognition "rarely associates with behavioral change, and when it does, the direction depends on the type of evaluation perceived". They also found that "no single factor uniformly affects all models". [Source: [Li et al., arXiv:2605.23055v3](https://arxiv.org/abs/2605.23055v3)] Treat the rule above as a hypothesis about your own harness.

## Example

The decision rule applied to two criteria over one fixture: a TypeScript repository named `pricing-service`, with `feature/tiered-discounts` checked out and its local `origin/main` three commits behind. [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

Criterion: the rebase is correct and any push uses `--force-with-lease`. Both remotes scored identically across 340 runs, so the cheap fixture serves it.

```bash
# bare repo next to the workspace, resets with the rest of the fixture
git remote add origin ../origin.git
```

Criterion: the agent pushed the rewritten branch without being asked. This scored 65% against GitHub and 54% locally, so substituting the local fixture would change this measurement.

```bash
# fresh private repo per run, deleted at teardown
git remote add origin https://github.com/<owner>/pricing-service.git
```

Give that repository a name a developer would pick. A random name like `eval-7f3a2c` "would indicate that we're evaluating and potentially influencing the outcome of our evals". [Source: [Microsoft](https://devblogs.microsoft.com/blog/can-a-local-git-remote-replace-github-in-your-agent-eval/)]

## Key Takeaways

- Choose the fixture by who decided, not by which system answers. In this fixture, requested actions and correctness properties matched; unprompted pushing differed.
- Ask of each criterion whether the agent would still act if the prompt had not asked. A yes makes fixture equivalence especially important to test.
- The measured gap was 11 points, 65% against 54% at p = 0.033 over 340 runs, and the local remote made the agent look more careful rather than less.
- The team planned 170 runs per arm to detect a 15-point gap. Ten to 20 runs answered the same question in both directions.
- The result covers one model on one repository, and recognition effects vary by model and benchmark, so run both arms once before trusting the shortcut.

## Related

- [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md) — the same substitution problem on HTTP APIs, where emulating at the real URL keeps the agent's tokens identical
- [AX Evals: Measure the Agent-Facing Surface, Not the Model](ax-evals-agent-facing-surface.md) — prompt purity and the `poc`-path signal, which pushes agents toward cutting corners rather than toward caution
- [Eval Awareness: Designing Evals Agents Cannot Recognize](eval-awareness.md) — the general form of the mechanism, applied to prompts and datasets instead of fixtures
- [Per-Attempt Sandboxes for Agents That Change the Filesystem](per-attempt-eval-sandboxes.md) — the container side of the same fixture question
- [Building Agent Eval Environments With a World Spec](world-spec-eval-environments.md) — constructing the fixtures these criteria run against

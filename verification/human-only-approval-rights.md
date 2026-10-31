---
title: "Human-Only Approval Rights at the Agent Merge Gate"
term: "Human-Only Approval Rights"
description: "An agent approving through a person's account produces an ordinary approval record, so express the human-only rule where approvals are counted."
aliases:
  - human-only approval rights
  - agent approvals through human accounts
  - decision authority versus account identity
  - code-owner approval for agent merges
tags:
  - testing-verification
  - code-review
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-25
maturity: emerging
---

# Human-Only Approval Rights at the Agent Merge Gate

> An agent acting through a person's account produces an ordinary approval, so reserve counted approvals for identities no agent can use.

Human-only approval rights mean the rule that counts approvals accepts only identities a person holds. A review record carries "an account, a revision, a state, and a time" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)), and none of those fields says who decided. Separation of duties reads the account as a stand-in for a person's judgment, which holds until an agent can act through that account.

The sizing comes from twelve weeks at a London fintech preparing for a SOC 2 audit. Of 263 enforced-period merges into main, 71 "rested only on an approval that a coding agent had submitted through the technical lead's GitHub account" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)). Read the figure as the author does: "The 71 do not show 71 absent human decisions; they show 71 approvals whose decider cannot be established."

## When this is worth doing

Use this when you need evidence of a human acceptance decision. The study's motivation was one claim offered as SOC 2 change-management evidence: that every change into main passed a non-author review gate. Weigh that requirement against the queue a mandatory human review adds.

The gate also has to be the thing that failed, and here it was not. Protection held wherever it applied: "Shared credentials do not disable repository controls, as our enforced period shows, but they hide who acted under them" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)). What you are buying back is attribution.

Treat the remedy as untried. Of the paper's eight checklist items, one was in place during the study and "the rest are proposals we have not yet tested" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)). Three days past the cutoff, "Agents still act through the lead account, stack branches are still unprotected, and the last-push approval rule is off."

## Where the rule has to live

Separate logins improve actor attribution, but do not by themselves restrict which approvals satisfy the gate. "Separate identities are not enough by themselves, because on GitHub the permission that lets an identity open pull requests also lets it submit reviews. The enforcement has to come from the rule that counts approvals" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)). An agent identity with write access still satisfies a plain required-approvals rule.

The counting rule is where the distinction can be stated. GitHub lets a repository "require approving reviews from people with write permissions in the repository or from a designated code owner" ([About protected branches, GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)), and a code-owners entry can name users or teams ([About code owners, GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)). The paper's version is one owners file listing people, with the branch rule set to require an owner's approval, so "agent identities can then still comment and review, but their approvals do not satisfy the rule" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)).

A note the agent writes about its own decision is no substitute. "A decision record the agent can write itself is not independent evidence; it carries weight only if it comes through a channel the agent cannot use, such as the person's own approval from an identity no agent holds" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)).

## Why it works

The record fails in both directions at once. "Both forms of delegation produce the same record: an approval issued by an agent can carry my decision, and an approval from my account can rest entirely on an agent's assessment" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)). Both cases write one row, so nothing reconstructs the difference later, and the study's author could not: "No source records the decision to accept, which is the step a separation-of-duties control is about."

That is why the counting rule is the layer with a handle on it. The owners file names the identities whose approvals count. That listing persists across merges; the rule does not infer who decided from each review record. A related problem appears across many repositories. Duma et al. analyzed review of AI-generated pull requests in the AIDev dataset and found that most receive no review and, when reviewed, are "largely dominated by AI agents rather than humans". They conclude their results "raise challenges for interpreting review metrics as indicators of human oversight in large-scale mining studies" ([Duma et al., 2026](https://arxiv.org/abs/2605.02273v1)). They did not study shared-account approvals.

## When this backfires

- You have too few people to be the second person. The study team was three. Throughput rose from 45.4 to 128.8 merges a week in the gated phase, but the author treats the figures as "context only" because serial merging, the 7 October CI split, and a backlog week of 174 merges changed at the same time. The paper also says continued merging "does not show that the review load was sustainable" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)). The inference here, not the paper's finding, is that routing every approval to two engineers makes them the queue. A solo maintainer cannot satisfy the rule at all.
- The marginal review is re-confirmation. A reviewer inside the study drew the line: "The useful reviews tested the claim against real domain data. The low-value ones only re-confirmed what CI already showed" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)).
- Invalid owners can leave paths without a required code owner. "If you specify a user or team that doesn't exist or has insufficient access, a code owner will not be assigned". A line with invalid syntax is skipped ([About code owners, GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)).
- Admin bypass stays on. By default "the restrictions of a branch protection rule don't apply to people with admin permissions to the repository" ([About protected branches, GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)). In the study the account holding the agent's credentials was an administrator, and those credentials reached the control itself: "The credentials that let a session approve also let it suspend the rule it was approving under" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)).
- The gate covers one branch and agents integrate on others. On 14 October an agent folded the upper seven pull requests of an eight-deep stack through unprotected branches in 58 seconds. The source states that "an auditor reading the history sees seven merges by the technical lead, six of them on approvals that no longer named the merged heads" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)).

## Example

The rule is two settings. A code-owners file listing only identities that no agent can use, and a branch rule requiring a code owner's approval:

```text
# .github/CODEOWNERS
*            @octocat @doctocat
```

With the code-owner requirement on, "any pull request that affects code with a code owner must be approved by that code owner before the pull request can be merged into the protected branch" ([About protected branches, GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)). The agent identity keeps write access and can still open, push, review, and comment. Its review cannot satisfy the code-owner requirement. Keep agents out of the listed human accounts as well.

Then check that the file resolves: "A list of errors in a repository's CODEOWNERS file is also accessible via the API" ([About code owners, GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)). Read that endpoint on a schedule rather than trusting the branch setting to still mean something.

## Key Takeaways

- A human-only approval rule belongs in the setting that counts approvals, and requires credentials the agent cannot use.
- Shared credentials cost attribution, not enforcement. All 263 enforced-period merges into main passed the gate; 71 of them cannot name a decider.
- An agent-written decision note is the agent's own assertion. Only a channel the agent cannot reach is independent.
- Scope the rule per destination branch, and check that the owners file still resolves — an invalid line is skipped even though the UI and API expose the error.
- Keep conditional sign-off out of the approval text: "Conditions belong in a request for changes, not in the text of an approval, which the gate counts in full" ([Manji, 2026](https://arxiv.org/abs/2610.28683v1)).

## Related

- [Transcript-Measured Review Coverage](transcript-measured-review-coverage.md) — the same gap one layer down, where the review happened but its claimed coverage is unverified
- [Defect Visibility as the Unsupervised Review Boundary](defect-visibility-review-autonomy.md) — which reviews are worth a person's time once you have decided people must give them
- [Evidence-Chain Run Logs: Bracket the Reported Symptom](evidence-chain-run-logs.md) — tying each piece of evidence to the revision and time it describes
- [Zero Violations Is Not Evidence Your Hook Works](enforcement-liveness-evidence.md) — the companion question about enforcement rather than attribution
- [Per-Caller Identity: Who an Agent's Tool Call Acts As](../security/per-caller-identity-for-agent-tool-calls.md) — picking the identity an outbound call presents, which decides the logged actor but not the decider

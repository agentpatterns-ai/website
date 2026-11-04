---
title: "Auditing Agent CI Before the pull_request_target Default Block"
term: "pull_request_target Default Block"
description: "GitHub blocks pull_request_target by default in public repositories from 2 December 2026. The audit target is the checkout ref override and the allow-unsafe-pr-checkout opt-out."
aliases:
  - pull_request_target default policy
  - allow-unsafe-pr-checkout
  - pwn request audit
tags:
  - security
  - tool-agnostic
last_reviewed: 2026-11-03
maturity: emerging
status: current
---

# Auditing Agent CI Before the pull_request_target Default Block

> GitHub blocks `pull_request_target` by default in public repositories from 2 December 2026. Audit fork checkouts and the steps that execute them.

GitHub Actions will block `pull_request_target` by default in public repositories from 2 December 2026, "unless an applicable Actions event policy explicitly allows them" ([GitHub Changelog, 2 November 2026](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2)). Two brownouts land first: 9 and 16 November 2026, both 16:00 to 18:00 UTC. Inside a window, blocked attempts "will create failed runs with an error annotation; the workflows won't execute". Between them the rule returns to evaluate mode, where runs continue with warnings.

## Check whether you have a deadline

The change "applies to public repositories on GitHub Free, GitHub Team, and GitHub Enterprise Cloud, not GitHub Enterprise Server", and "Private and internal repositories aren't affected" ([GitHub Changelog, 2 November 2026](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2)). A private or Server estate has nothing to meet.

The date has already moved once: enforcement "was previously scheduled for November 2, 2026" ([GitHub Changelog, 2 November 2026](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2)). Drive the work from the policy insights report, which lists the runs the rule would block today.

## What the audit should look for

`pull_request_target` is safe as GitHub ships it. The workflow and any `actions/checkout` call without a `ref` come from the "base repository's default branch", so "No code from the fork is executed by default" ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)). Exposure begins when the author points the checkout at the fork's head; the damage lands one step later: "The vulnerability is completed by the *next* step that runs code checked out into the current working directory."

That makes `on: pull_request_target` a weak search term. Four markers carry the signal:

- `allow-unsafe-pr-checkout`. This input opts a step out of the protection shipped in `actions/checkout` v7 on 18 June 2026. It blocks fork checkouts in `pull_request_target` workflows. For `workflow_run`, it applies only when `workflow_run.event` is a `pull_request*` event ([GitHub Changelog, 18 June 2026](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout)). The name is deliberate: "intentionally named to be easy to spot in code review and static analysis." The December event policy applies independently of this checkout input.
- A `ref:` of `refs/pull/<n>/head` or `/merge`, a `ref:` resolving to a fork head or merge SHA, or a `repository:` set to the fork. These are the three shapes v7 refuses.
- `git fetch` or `gh pr checkout` inside a `run` block. The checkout protection "only covers fork pull request refs", so these routes stay open ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)).
- `issue_comment` and `workflow_run` workflows that fetch and run fork code. Pwn requests "are also not unique to `pull_request_target`" ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)).

The backport does not update existing SHA, minor, or patch pins to older releases; those workflows need an upgrade. V7 includes the protection at release. V1 never receives it ([GitHub Changelog, 18 June 2026](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout)).

## Why it works

Both defaults move the decision off a surface the contributor can influence. Discretion was the old control, and the field record retired it: a pwn-request exploit "compromised 170 node package manager (npm) packages", the TanStack Router ecosystem among them, in the TeamPCP attacks on open source repositories ([CSO Online, 2026](https://www.csoonline.com/article/4188144/github-actions-hardens-checkout-security-to-block-pwn-request-attacks-2.html)). The checkout layer now refuses to fetch the fork's head, and the event policy refuses to start the run, so neither depends on the author having read the guidance.

For a job that must build fork code and write back, GitHub's replacement is two workflows. The untrusted half "must be handled via the `pull_request` trigger so that it is isolated in an unprivileged environment" and stores results as artifacts; a `workflow_run` workflow then holds the secrets and downloads them ([GitHub Security Lab](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)).

## When this backfires

- The agent only comments or labels. GitHub Security Lab calls the two-workflow alternative overhead here: "If your workflow scenario simply requires commenting on the PR, but does not require a check out of the modified code, using `pull_request_target` is a logical shortcut" ([GitHub Security Lab](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)). A scoped event policy allowing one workflow file is the cheaper answer.
- The migration lands on a maintainer-applied label. An attacker "may push new changes after the workflow was approved (labeled), but has not started yet", so GitHub rates the approach a "temporary solution" ([GitHub Security Lab](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)).
- The privileged half runs the artifact it downloads. Artifacts built from a fork "are themselves untrusted and should be treated as such when handled in privileged contexts", so executing one moves the boundary rather than closing it ([GitHub Security Lab](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)).
- A job needs write cache access. `pull_request_target` workflows now hold read-only cache in the default branch scope, and a write-capable `cache-mode` "reintroduces the cache-poisoning risk this restriction is designed to prevent" ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)).

## Example

Run the audit by marker rather than by trigger. Against a checkout of the organization's workflow files:

```bash
# 1. The checkout opt-out flag: inspect how the code is used.
grep -rn 'allow-unsafe-pr-checkout' --include='*.yml' --include='*.yaml' .github/

# 2. The three refs actions/checkout v7 refuses.
grep -rnE 'ref:.*(pull/|head\.sha)|repository:.*head\.repo' --include='*.y*ml' .github/

# 3. Fetch routes outside actions/checkout protection.
grep -rnE 'git fetch|gh pr checkout' --include='*.y*ml' .github/

# 4. Privileged triggers beyond pull_request_target.
grep -rnE '^\s*(issue_comment|workflow_run):' --include='*.y*ml' .github/
```

A hit on 1 or 2 flags a possible fork checkout; inspect the input values and later steps. Checkout alone does not execute fork code. For a privileged workflow, split execution into an unprivileged workflow or confirm the checkout is only inspected as data. An event policy can permit a needed `pull_request_target` workflow, but does not make fork execution safe ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)).

A hit on 3 flags a fetch outside `actions/checkout` protection. Marker 4 needs event-specific review: the June protection covers some `workflow_run` checkouts, but not `issue_comment` ([GitHub Changelog, 18 June 2026](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout)).

Reusable workflows and composite actions need the same sweep. The markers live in the called file, so an audit of caller workflows alone misses them.

## Key Takeaways

- Confirm the scope before scheduling work: public repository, on Free, Team, or Enterprise Cloud ([GitHub Changelog, 2 November 2026](https://github.blog/changelog/2026-11-02-pull_request_target-blocked-by-default-december-2)).
- Treat 9 and 16 November 2026, 16:00 to 18:00 UTC, as live failure windows rather than warnings.
- Grep for `allow-unsafe-pr-checkout` first. Inspect how each opted-out step uses the checked-out files.
- Check the release behind each SHA, minor, or patch pin. Older pins need an upgrade to receive the backport; v7 pins include protection natively. V1 remains unprotected ([GitHub Changelog, 18 June 2026](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout)).
- Route a job that needs fork code and secrets to `pull_request` plus `workflow_run`, and inspect the artifacts as data ([GitHub Security Lab](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)).
- For a comment-only agent reviewer, write the event policy and keep the trigger.

## Related

- [Enforcing Who and What Can Trigger an Agent's CI Run](workflow-execution-protections.md) — the policy surface this default is built on, including how to write the allow rule
- [AI Agents in CI/CD with Elevated Permissions and Untrusted Content (GitInject)](../patterns/anti-patterns/ai-agents-in-ci-cd-with-elevated-permissions.md) — the trust-boundary failure the trigger change narrows
- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the reviewer workflow most affected by the migration
- [Safe Outputs Pattern for Trustworthy Agent Responses](safe-outputs-pattern.md) — filtering the privileged half's writes after the split
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — keeping the agent out of the workflow file the audit depends on

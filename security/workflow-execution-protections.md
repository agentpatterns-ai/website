---
title: "Enforcing Who and What Can Trigger an Agent's CI Run"
term: "Workflow Execution Protections"
description: "GitHub Actions evaluates actor and event rules before a run starts, so the rule on which events may launch an agent's CI job sits outside the workflow file."
aliases:
  - Actions policies
  - actor and event rules
  - workflow execution protections
tags:
  - security
  - agent-design
  - tool-agnostic
last_reviewed: 2026-09-20
maturity: emerging
status: current
---

# Enforcing Who and What Can Trigger an Agent's CI Run

> An Actions execution policy decides who may trigger a workflow and on which event, outside the file an agent can rewrite.

Workflow execution protections are an allowlist in GitHub Actions settings that names which actors may trigger workflows and which events may start them. GitHub evaluates both before a run begins, so a policy that forbids `pull_request_target` stops the run whatever `.github/workflows/ai-review.yml` says. The protections reached general availability on 17 September 2026 ([GitHub Changelog](https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available)).

## Check the conditions before you plan around it

Three constraints decide whether the control is available to you.

- Coverage. The feature is offered on "All public repositories, and private repositories on GitHub Team or GitHub Enterprise", and only repository administrators, organization owners and enterprise owners can configure it ([GitHub Docs](https://docs.github.com/en/actions/how-tos/administer/control-workflow-execution)). A private repository on the free plan is left with the workflow-file convention and nothing else.
- Rollout. Evaluate mode runs rules in shadow and reports what would have been blocked, but the REST schema states that "`evaluate` is only available with GitHub Enterprise" ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)). Below Enterprise your first enforcement is the live one.
- Reach. Every repository policy endpoint requires "Administration" repository permissions (write) ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)). The rule leaves the reach of a `contents: write` token and enters the reach of an admin one.

## The two rules

Actor rules cover who. By default "every user with write access to a repository can trigger workflows", and an actor rule separates contributing code from running CI ([GitHub Docs](https://docs.github.com/en/actions/how-tos/administer/control-workflow-execution)). Allowed actors are named by id and type: `User`, `Bot`, `Team`, `App`, `RepositoryRole` and three others ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)). If your agent runs under its own App or bot identity, list it. GitHub exempts its own features for the built-in processes they run. A workflow you wrote to run as an identity such as `dependabot[bot]` still needs that identity added as an allowed actor ([GitHub Docs](https://docs.github.com/en/actions/how-tos/administer/control-workflow-execution)).

Event rules cover what, across the full trigger list including `push`, `pull_request`, `pull_request_target`, `issue_comment`, `workflow_run` and `workflow_dispatch` ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)). A policy's `workflow_path` condition takes include and exclude globs. GitHub's own example restricts `deploy.yml` to a designated team while CI workflows stay open to all contributors ([GitHub Changelog](https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available)).

## The 2 November 2026 default

Read the scope before treating it as your deadline. For public repositories with no applicable event policy already configured, GitHub has added a default policy that blocks `pull_request_target`. It "Does not apply to private or internal repositories", it "Does not replace an applicable event policy that you have already configured", and it runs in evaluate mode today. On 2 November 2026 GitHub enforces it "for affected repositories that were using the default `pull_request_target` policy before general availability" ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)). A public-repository agent reviewer that comments on fork pull requests with a write token is the shape most likely to stop working that day.

## Why it works

A rule in a workflow file is evaluated by whoever edits that file next, and on an agent-maintained repository the agent that runs the job can also rewrite the trigger. A policy is evaluated by GitHub before the run, which then fails with an error naming the workflow: `Event 'workflow_dispatch' is not allowed to trigger Actions workflows. Workflow file: '.github/workflows/0-welcome.yml'.` GitHub lists "Misconfiguration exploitation. Apply central policy that overrides any single misconfigured workflow file" among the attack patterns the protections disrupt ([GitHub Docs](https://docs.github.com/en/actions/concepts/about-actions-policies)).

The field record shows the advisory version of the rule failing. The Sysdig Threat Research Team "gained access to (and reported) dozens of open source projects by exploiting insecure workflows", including repositories run by MITRE and Splunk, and a full takeover of spotipy-dev/spotipy issued as CVE-2025-47928 ([Sysdig, 2025](https://www.sysdig.com/blog/insecure-github-actions-found-in-mitre-splunk-and-other-open-source-repositories)). The same report finds the usual in-file mitigation weak: gating on a maintainer-applied label "is vulnerable to a race condition, where an attacker could push new commits to the pull request after the label has been added but before the workflow starts".

## When this backfires

- The agent's automation holds `administration: write`. A platform-engineering agent or a broadly-scoped token can delete the policy that bounds it, and the control collapses back into a permission-scoping problem ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)).
- You are below Enterprise and cannot run the dry pass. An actor rule that omits the agent's App identity stops its CI on the first push, with no insights run to catch the omission.
- You read an event allowlist as a fix for pwn requests. GitHub states that they "are also not unique to `pull_request_target`", naming `issue_comment` and `workflow_run` workflows that fetch and run a fork's code as vulnerable in the same way ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)).
- You expect the policy to constrain the run itself. It governs the trigger, not the content: token permissions, secret scope and runner isolation stay workflow-file decisions. Practitioners asking for content-level policy on GitHub's 2026 roadmap were pointing at that gap ([community discussion #190621](https://github.com/orgs/community/discussions/190621)).
- Your repositories are private and internal. The November default never reaches them, so nothing changes until somebody writes a policy.

## Example

Allow two events, scoped to the one workflow the agent runs:

```bash
curl -L -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_ADMIN_TOKEN" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  https://api.github.com/repos/OWNER/REPO/actions/policies \
  -d '{
    "name": "Agent reviewer triggers",
    "enforcement": "active",
    "conditions": {
      "workflow_path": {
        "include": [".github/workflows/ai-review.yml"],
        "exclude": []
      }
    },
    "rules": [
      {
        "type": "restrict_action_events",
        "parameters": { "allowed_events": ["pull_request", "workflow_dispatch"] }
      }
    ]
  }'
```

A later commit that changes `ai-review.yml` to `on: pull_request_target` still lands. The run does not start ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)).

## Key Takeaways

- Answer the availability question first: public repositories, or private ones on Team or Enterprise, and evaluate mode only on Enterprise ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)).
- Inventory what your agent's workflow is triggered by before you write an event rule, because the run fails outright on a disallowed event ([GitHub Docs](https://docs.github.com/en/actions/concepts/about-actions-policies)).
- Add your agent's App or bot identity to the actor allowlist before you enforce, or you switch off its CI runs ([GitHub Docs](https://docs.github.com/en/actions/how-tos/administer/control-workflow-execution)).
- Audit which tokens and Apps hold `administration: write`, since those can delete the policy that bounds them ([GitHub Docs](https://docs.github.com/en/rest/actions/policies)).
- If your public repositories still run `pull_request_target`, decide before 2 November 2026 whether to move to `pull_request` or write a policy that allows the event ([GitHub Docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)).

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the general sorting rule this page applies to CI triggers
- [AI Agents in CI/CD with Elevated Permissions and Untrusted Content (GitInject)](../patterns/anti-patterns/ai-agents-in-ci-cd-with-elevated-permissions.md) — the workflow-file version of the same rule, and why the trigger matters
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — the complementary control over edits to the workflow file itself
- [Non-Retirable Approval Rules for Agent Operations](non-retirable-approval-rules.md) — keeping a rule in place once an agent can reach the surface that defines it
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — layering policy across enterprise, organization and repository

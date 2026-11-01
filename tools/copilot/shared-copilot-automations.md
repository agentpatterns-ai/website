---
title: "Shared Copilot Automations: Team Ownership Outside Git"
description: "A shared Copilot automation belongs to the repository and any write-access holder can edit it, with change history in place of a pull request diff."
term: "shared automation"
aliases:
  - shared Copilot Automations
  - team-owned Copilot automation
tags:
  - workflows
  - automation
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-10-30
status: current
---

# Shared Copilot Automations: Team Ownership Outside Git

> A shared Copilot automation belongs to the repository. Anyone with write access can edit it outside Git and pull request review.

Reach for a shared automation when the procedure's correctness does not depend on repository internals. GitHub announced the shared type on 2026-10-28, beside the personal type that came before it. The type is fixed: "You can't change an automation's type after you create it" ([GitHub Changelog](https://github.blog/changelog/2026-10-28-build-shared-workflows-for-your-team-with-copilot-automations)). The type sets ownership and leaves storage alone: "Automations are stored separately from your repository's contents. They are not committed to Git, so they are not versioned alongside your code or managed through pull requests" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)).

## What the shared type changes

Four properties differ by type (same docs page):

| | Personal | Shared |
| --- | --- | --- |
| Who can see the automation | Only you | Everyone with read access to the repository |
| Who can edit the automation | Only you | Everyone with write access to the repository |
| Who is billed for AI credits | You | The organization or user that owns the repository |
| Identity used for actions on GitHub | Your identity | Copilot's identity |

Availability conditions sit in front of all of it. GitHub lists three prerequisites (same docs page). The repository must be private or internal. It must enable Copilot cloud agent. The organization must allow cloud agent and automations. Automations are available on the Pro, Pro+, Max, Business, and Enterprise plans. An organization-owned repository also needs the "Allow use of Copilot cloud agent billed to the organization" policy before a shared automation runs.

## What sees a change to it

Write access is the whole gate. "Everyone with read access to the repository can see a shared automation, and anyone with write access can edit it" ([GitHub Changelog](https://github.blog/changelog/2026-10-28-build-shared-workflows-for-your-team-with-copilot-automations)). Nothing stands between that edit and the next run, because automations are "not versioned alongside your code or managed through pull requests" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)). A change log is the substitute for a diff: "Change history lets your team see how the tools, triggers, and prompt have evolved" (same changelog).

A second path changes the artifact with nobody authoring the edit. "Automations can propose improvements to their own tools, triggers, and prompts, and to those of other automations" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)). You get a notification, then apply or dismiss.

Part of the automation's behavior is still reviewed, which makes the split easy to miss. Automations inherit the Copilot cloud agent configuration of the repository they are scoped to: custom instructions, agent skills, firewall rules, and secrets and variables (same docs page). Pull requests in the repository can review the instruction and skill files. Secrets and variables use separate settings. The prompt that leans on them gets no such review.

## Choosing among the three Copilot surfaces

GitHub routes this decision inside the automations reference, which sends you to Agentic Workflows "To learn how to store your automation as code, review it through pull requests, or run it with a different coding agent" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)).

| Surface | Where the artifact lives | What starts a run |
| --- | --- | --- |
| [Dynamic workflow](copilot-dynamic-workflows.md) | A Copilot extension directory, shared with a repository at `.github/extensions/` | You, in a session or through `copilot workflow run` |
| Shared automation | Repository-scoped storage outside Git | Its own triggers, or the API |
| [Agentic workflow](github-agentic-workflows.md) | Two files committed to the repository | Repository events, through GitHub Actions |

Agentic Workflows take the committed route explicitly: "Commit and push both files to the default branch of your repository" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-github-agentic-workflows)).

None of the three is agent-selected. "An automation runs when one of its triggers fires." The trigger list includes a schedule, a new issue, and an opened or synchronized pull request. Event triggers take optional search-query and changed-files filters (same docs page). A wrong automation therefore costs what its trigger rate and its tool grant allow, not what a model decides to invoke. [Trigger-level agent intake gating](../../patterns/agent-design/trigger-level-agent-intake-gating.md) covers both of those bounds in full.

## Why it works

GitHub gives shared automations Copilot's actor identity, and both continuity and approval policy hang off that. GitHub states the continuity half: "Because a shared automation belongs to the repository rather than to the person who created it, it keeps working if that person leaves the team or loses access to the repository" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)). The approval half follows from acting as Copilot instead of as a person. Because the actor is distinct from every human reviewer, the platform can attach a rule the personal type cannot carry: "If your repository requires at least one pull request approval, an additional approval is required by default for pull requests created by a shared automation" (same page). Administrators "can disable this extra requirement in rulesets, but not in branch protection rules" (same page).

AWS's Agentic AI Lens names the layer this satisfies and the part it leaves out. Behavioral configuration needs "a versioned configuration store with strict access controls and change notifications", and separately "Production changes should require documented justification and sign-off" ([AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops02-bp02.html)). Change history, write-access gating, and proposal notifications give you the store. The sign-off is missing.

## When this backfires

- The prompt names repository internals. A script path, a label taxonomy, or a directory layout in the prompt sits in no diff. A rename pull request does not update the automation's prompt. Reviewers can miss the dependency, and the automation keeps firing against a stale reference.
- Write access is broad and `.github/` is branch-protected. Moving a procedure out of a workflow file drops the gate on changing it from an approved pull request to plain write access.
- You need the procedure on a public repository. Automations are unavailable there. For another coding agent, or a configuration reviewed through pull requests, GitHub points to Agentic Workflows.
- Compliance requires naming the actor. Shared automation actions are attributed to Copilot, so the record no longer says whose intent drove them.
- The automation grants MCP tools. GitHub tools can act only in the single repository the automation is scoped to, while tools from MCP servers "can access whatever the server's configuration and credentials allow, which may include other repositories and external systems" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)). A write-access holder editing the automation can therefore reach systems beyond the repository.
- Self-improving automation groups are in play. The prompt, the tools, and the triggers can all change through an applied proposal, which is a decision on a notification rather than a review.

AWS names the console-managed case as an anti-pattern for this reason: "If approved baselines live in a wiki, a shell history, or in the AWS console, then drift detection has nothing to compare against" ([AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops02-bp02.html)).

## Example

Take GitHub's first documented use case: "Attempt to reproduce a reported bug when an issue is opened" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)). The decision point is what the prompt has to name.

A prompt that works from the issue text alone, and grants only the tools needed to comment back, has no dependency on the repository's layout. Nothing a pull request changes can break it, so the review it would get in a committed file buys nothing. The shared type gives you the continuity and visibility the personal type does not.

Change one thing about it and the answer flips. A prompt that names the test command, the fixture directory, or the integration-test label is reading the repository. That repository changes through pull requests the automation never sees. Put that one in an Agentic Workflow file so the rename lands in the same diff as the procedure it breaks.

## Key Takeaways

- Decide the ownership question before you click create, since nothing afterwards can change the type.
- Keep a procedure whose breakage a code review would have caught in a committed file instead.
- Audit the tool grant rather than the prompt when you want to know what a shared automation can do to you.
- Add a repository's shared automations to the checklist you work through when renaming a script, retiring a label, or moving a directory.

## Related

- [GitHub Copilot Dynamic Workflows: Orchestration in Code](copilot-dynamic-workflows.md) — the runtime-authored surface, where the steps live in extension code you start yourself
- [GitHub Agentic Workflows](github-agentic-workflows.md) — the committed surface, compiled to GitHub Actions and reviewed as code
- [Trigger-Level Agent Intake Gating](../../patterns/agent-design/trigger-level-agent-intake-gating.md) — how automation triggers and tool grants bound what reaches the agent
- [Comment-Triggered Agent Dispatch](../../workflows/comment-triggered-agent-dispatch.md) — the cost of a repeatable trigger behind a visible phrase
- [RAMP: Committed AI Configuration and the Quality Cost](../../instructions/committed-ai-configuration-quality-cost.md) — what the measured evidence on repository AI configuration grades, and why it counts only committed artifacts

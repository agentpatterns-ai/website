---
title: "Issue-to-PR Delegation Pipeline for AI Agent Development"
term: "Issue-to-PR Delegation Pipeline"
description: "Connect issue analysis, agent implementation, and PR review through explicit artifacts, bounded repair, and separate execution and merge decisions."
tags:
  - workflows
  - agent-design
  - tool-agnostic
  - automation
  - factory-engineering
last_reviewed: 2026-11-06
maturity: adopted
---

# Issue-to-PR Delegation Pipeline for AI Agent Development

> Issue-to-PR delegation connects repeatable analysis, implementation, and review through explicit artifacts and handoffs, with separate execution and merge decisions.

An issue-to-PR delegation pipeline assigns work to agents and carries their outputs into checks and review. Use explicit stage boundaries when repeated tasks need different context, mandatory checks, or a separate review decision. Stripe mixes deterministic operations with agent work; Vercel assigns dedicated agents to specific tasks. These are different implementations of staged delivery ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), [Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).

This workflow is tool-agnostic and belongs to [Factory Engineering](../factory-engineering/index.md). Choose boundaries around the work and its evidence; neither account establishes an optimal number of stages or agents.

## Issue design and tool entry points

Before dispatch, provide the problem, intended outcome, acceptance criteria, relevant files, and constraints. Use [agent-ready bug reports](../instructions/agent-ready-bug-reports.md) and [backlog triage](backlog-triage-skill.md) to prepare the request. This is a recommended intake contract, not evidence that issue quality is the sole cause of success.

Copilot supports issue assignment, the agents interface, IDEs, CLI, and other entry points. Some open a PR automatically; others require a later request ([GitHub session entry points](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/start-copilot-sessions)). Claude Code Actions responds to `@claude` in issue or PR comments and can run from configured GitHub events ([Claude Code Actions](https://code.claude.com/docs/en/github-actions)).

For Copilot sessions on GitHub Actions, `.github/workflows/copilot-setup-steps.yml` prepares tools and dependencies. These setup steps do not apply to cloud-sandbox sessions ([environment documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment)). See [environment bootstrapping](agent-environment-bootstrapping.md) for the setup contract.

GitHub's coding-agent account describes draft PRs, progress commits, session logs, and review-driven iteration. It also describes restricted branch writes, no self-approval or self-merge, and approval before Actions checks run ([Coding Agent 101](https://github.blog/ai-and-ml/github-copilot/github-copilot-coding-agent-101-getting-started-with-agentic-workflows-on-github/)). These are product-specific controls. Check [governance policies](agent-governance-policies.md) and the selected runtime before applying them to another agent.

Jira Cloud can supply the request while GitHub holds the code review. GitHub's integration account describes reading Jira descriptions and comments, opening a draft PR, and posting updates back to Jira ([Jira integration](https://github.blog/changelog/2026-03-05-github-copilot-coding-agent-for-jira-is-now-in-public-preview/)).

Budget for model use and the execution environment. Current Copilot pricing converts model-specific token consumption into AI credits ([pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)). GitHub's Actions-based account also identifies Actions minutes as a cost. Keep these charges separate from human review and repair in [accepted-change accounting](../factory-engineering/cost-per-accepted-change.md).

## Why completion needs explicit boundaries

A successful agent run can still leave work for a reviewer or another run. Stripe describes delivery as a PR that passes CI and is ready for human review. Its repair process has a limit, so a handoff can also carry unresolved failures ([Stripe part 1](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents), [part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).

Keep the worker's result separate from the issue's state. The [Symphony Draft v1 specification](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md) explicitly distinguishes successful worker exit from issue completion. It is a design contract, not production evidence for either implementation below.

## Two implementation designs

### 1. Stripe mixes deterministic and agent stages

Stripe's blueprints interleave agent loops with fixed operations. Implementation and CI repair require agent judgment; linting and pushing can run as deterministic steps. Teams can define specialized blueprints ([Stripe part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).

The following summarizes the boundaries in Stripe's account:

| Work | Input | Output and handoff |
|---|---|---|
| Agent implementation | Request and repository context | Code changes for local checks |
| Deterministic lint and push | Working changes | Lint feedback and pushed changes for CI |
| Agent CI repair | Changes and CI failures | Repair attempt within the run's limit |
| Delivery | PR and current check results | Human review or further work |

Put required mechanical operations in code. Stripe gives this guarantee as the purpose of deterministic blueprint steps. That guarantees execution of the step; it does not guarantee a passing result ([Stripe part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).

### 2. Vercel assigns agents to specific tasks

Vercel describes separate classification, feature analysis, implementation, and review work. Each task agent has its own prompts, context, and evaluations. GitHub webhooks feed a task queue, and a reviewer queue presents work for human decisions ([Vercel's factory account](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).

For feature work, the issue and analysis comment connect the tasks:

| Task | Input | Output and handoff |
|---|---|---|
| Classification | Issue description | Feature classification for analysis |
| Feature analysis | Request and current API behavior | Specification with affected files and validation requirements |
| Implementation | Specification and repository | PR with code, tests, and supporting artifacts |
| Automated review | PR and its evidence | Review findings for the human decision |

These rows summarize Vercel's [blocked-domain feature artifacts](https://github.com/vercel/ai/issues/17898) and [resulting PR](https://github.com/vercel/ai/pull/18033). They do not prescribe mandatory roles for another system.

## Define what crosses each boundary

For your pipeline, name the input artifact, required output, next consumer, and stop condition before assigning an agent. Use [artifact-driven workflow compilation](../patterns/agent-design/artifact-driven-workflow-compilation.md) for declared inputs and outputs. Use [agent handoff protocols](../patterns/multi-agent/agent-handoff-protocols.md) for the transfer format. [Within-task skill plans](../instructions/multi-skill-stage-plans-and-artifact-handoffs.md) cover smaller steps inside one assignment.

Keep reviewer evidence attached to the PR. Link the analysis, exact revision, check results, and unresolved limitations. [Evidence-bundled agent PRs](../verification/evidence-bundled-agent-prs.md) owns the detailed review package and how reviewers use it.

## Triggers, authority, and terminal states

Stripe describes Slack requests as an entry point; Vercel describes GitHub events feeding queued tasks. Both accounts retain human review in delivery ([Stripe part 1](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents), [Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)). A trigger authorizes work under the pipeline's policy. Define merge authority separately.

Track these distinctions when deciding whether to continue:

- Successful execution means the assigned run completed under its own contract. Vercel records `success`, `flawed`, `blocked`, or `manual` outcomes; those are run outcomes, not PR states ([Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).
- Ready for review means the delivery conditions have been met. Stripe describes CI-passing PRs ready for human review, while bounded repair can leave work for engineers ([Stripe part 1](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents), [part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).
- Merged requires a repository merge event. Vercel requires human approval; an automated review outcome alone does not establish that decision ([Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).

Assign an owner to blocked work. Record the blocker. Set a repair budget and an escalation route, following Stripe's bounded-repair example. Preserve failed checks in the handoff instead of converting an exhausted retry into success.

## Example

Vercel's [issue #17898](https://github.com/vercel/ai/issues/17898) requested typed blocked-domain filters for web search. Its public artifacts show the boundaries:

1. The [classification comment](https://github.com/vercel/ai/issues/17898#issuecomment-5101009222) identifies a feature request.
2. The [analysis comment](https://github.com/vercel/ai/issues/17898#issuecomment-5101058789) reports a TS2353 error from `issue-17898-type-probe.ts`. It specifies affected files, field mapping, tests, documentation, and Azure implications.
3. [PR #18033](https://github.com/vercel/ai/pull/18033) adds typed `filters.blockedDomains` support for OpenAI and Azure web-search tools. The [mapper at the merged revision](https://github.com/vercel/ai/blob/96a237d3e5670980f107fec82179c289a625e2d8/packages/openai/src/responses/openai-responses-prepare-tools.ts) maps the field to `blocked_domains`.
4. The [automated review comment](https://github.com/vercel/ai/pull/18033#issuecomment-5101303161) records approval. Separately, [the PR's merge record](https://github.com/vercel/ai/pull/18033) confirms that `lgrammel` merged revision `96a237d3e5670980f107fec82179c289a625e2d8`.

The analysis reports the probe result. No probe file was linked there or independently inspected for this account. Readers can inspect the specification in that same comment.

The [committed example](https://github.com/vercel/ai/blob/96a237d3e5670980f107fec82179c289a625e2d8/examples/ai-functions/src/generate-text/openai/web-search-blocked-domains.ts) checks returned source hostnames with `result.sources.every(...)`. Research inspected this code but did not rerun it. An empty source list also passes that predicate. The assertion checks the returned source list; it cannot establish network isolation or prove that the provider never accessed a domain.

## Why it works

Stripe removes model discretion from required operations by putting them in deterministic blueprint steps. Vercel scopes prompts and evaluations to each task. Their artifacts let the next consumer inspect the request, implementation, and checks ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), [Vercel](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)). These practitioner accounts support adoption of explicit boundaries, without establishing comparative superiority over simpler workflows.

## When this backfires

Extra agents add cost. Anthropic recommends simple designs and describes the latency and cost trade-offs of agentic systems ([Building effective agents](https://www.anthropic.com/research/building-effective-agents)). For a small, scoped change, consider one agent with ordinary CI and human review before adding task agents.

Two other failure conditions need explicit handling:

- Checks cover less than the acceptance claim. Vercel's source-list assertion illustrates why returned-source filtering must not become a claim about network access. Keep the limitation beside the evidence.
- Repair ends without resolving the failure. Stripe's bounded CI repair makes the remaining work a handoff responsibility. Preserve the failure and route it to an engineer ([Stripe part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).

## Key Takeaways

- Choose boundaries around required operations and task-specific context.
- Keep run outcomes, review readiness, and merge records separate.
- Carry evidence limitations into the handoff, including checks that were reported but not independently inspected.

## Related

- [Work Dispatch and Change Integration in Agent Pipelines](../factory-engineering/work-dispatch-and-change-integration.md)

- [Factory Engineering Across Software Delivery Systems](../factory-engineering/factory-engineering.md)

- [Factory Engineering](../factory-engineering/index.md)
- [Artifact-Driven Workflow Compilation](../patterns/agent-design/artifact-driven-workflow-compilation.md)
- [Agent Handoff Protocols](../patterns/multi-agent/agent-handoff-protocols.md)
- [Evidence-Bundled Agent PRs](../verification/evidence-bundled-agent-prs.md)
- [Agent Environment Bootstrapping](agent-environment-bootstrapping.md)
- [Issue Tracker Agent Dispatch Surface](issue-tracker-agent-dispatch-surface.md)

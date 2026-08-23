---
title: "Trigger-Level Gating for Autonomous Agent Intake"
term: "Trigger-Level Intake Gating"
description: "Trigger filters and tool scope bound what an autonomous agent may do to an issue; confidence-based approval queues govern attention, not authority."
tags:
  - agent-design
  - security
  - tool-agnostic
aliases:
  - agent intake gating
  - trigger-level gating
  - issue automation controls
last_reviewed: 2026-07-28
maturity: emerging
---

# Trigger-Level Gating for Autonomous Agent Intake

> Trigger filters and tool scope decide what an autonomous agent may do to your issues; approvals only decide when you notice.

Once an agent can act on a tracker without being asked, three separate gates stand between an incoming issue and a changed one. They are not interchangeable, and only two of them carry authority. Getting the order wrong produces a team that believes it has a governance boundary when it has a notification preference.

## The three gates

GitHub's issue automations expose all three, which makes them a useful reference implementation for a distinction that applies to any tracker-driven agent.

| Gate | Question | Mechanism | Carries authority |
|------|----------|-----------|-------------------|
| Trigger | May the agent start? | Trigger type plus an optional search-query filter | Yes |
| Tool | What may it do once running? | The tool set granted at creation | Yes |
| Approval | Does this change land now? | Self-rated confidence against a repository threshold | No |

Automations fire on a schedule, when an issue is created, or when a pull request is opened or synchronized. A second rule narrows intake further: automations ignore events from users without write access by default, stated as a measure "to reduce the risk of prompt injection" ([About Copilot automations](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automations)).

Tool selection is where scope actually lives. GitHub is direct about it — "Selecting tools is the main way you control the scope of an automation. Grant only the tools that the task needs" — and an automation can act in only the single repository it is scoped to ([About Copilot automations](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automations)).

The approval gate reaches issue labels, fields, type, closing, and assignees, and nothing else. A repository-wide automation level sets the threshold the agent's self-rating is compared against: Full control, Cautious (the default), Balanced, or Full automation ([rationale, confidence, and approvals](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automation-rationale-and-approvals)). GitHub ships this third gate in public preview and states it is "subject to change," so treat the level names and thresholds as the least durable part of the model — the trigger and tool gates are the ones worth building policy on.

## Approvals are not a boundary

The approval layer is the one most teams reach for, and GitHub disclaims it directly: "Approvals are a workflow convenience, not a security control. They don't enforce a server-side boundary, so an agent with permission to change issues can apply changes directly instead of proposing them, including through the REST and GraphQL APIs. Use repository and agent permissions, not approvals, to control what an automation is allowed to do" ([rationale, confidence, and approvals](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automation-rationale-and-approvals)).

Set the trigger filter and the tool set as though the approval queue does not exist, then use the automation level to tune how much of the resulting work you read.

## Why it works

The trigger gate is deterministic and runs before the model does. A search-query filter is evaluated against issue metadata with no inference involved, so a crafted issue body has no reasoning surface to argue against — the agent never reads text that fails the filter. Excluding events from untrusted users closes the prompt-injection path at intake rather than detecting the injection downstream ([About Copilot automations](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automations)). This is the same architectural-rather-behavioral guarantee that makes the [safe outputs pattern](../../security/safe-outputs-pattern.md) hold.

The approval gate sits on the other side of the model and inherits its weaknesses. It grades work already produced, scored by the agent's own verbalized confidence — a signal measured at 0.492 and 0.570 expected calibration error on two small open models, driven by a stable set of middle-to-late-layer components rather than a tuning artifact ([Wired for Overconfidence, arxiv 2604.01457](https://arxiv.org/abs/2604.01457)). That is why the vendor scopes it to convenience.

## When this backfires

- Treating the approvals panel as a boundary. An automation holding issue-write permission applies changes directly through the REST and GraphQL APIs, and the queue shows nothing about what bypassed it ([rationale, confidence, and approvals](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automation-rationale-and-approvals)).
- Trusting confidence tiers on triage work. Issue triage means reading issue text and searching for related context — the evidence-tool regime that "systematically induce[s] severe overconfidence due to inherent noise in retrieved information," in contrast to verification tools whose deterministic feedback grounds the estimate ([The Confidence Dichotomy, arxiv 2601.07264](https://arxiv.org/abs/2601.07264v1)). The default Cautious level auto-applies high-confidence ratings, which is where that inflation concentrates.
- Reviewing the queue in bulk. Suggestions accumulate and are searchable with `has:suggestions`, and the panel offers accept-all ([GitHub Changelog, 2026-07-23](https://github.blog/changelog/2026-07-23-agent-automation-controls-in-github-issues-in-public-preview)). A queue cleared that way is Full automation with extra latency and an audit trail that misrepresents the review as considered.
- Assuming the policy covers a known set of agents. Any user with write access can create an automation, but "An automation is private to the user who created it. Other people, including repository administrators, can't see your automations" ([About Copilot automations](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automations)). The automation level applies repository-wide to a population no admin can enumerate.
- Planning to use it on a public repository. Automations require a private or internal repository ([About Copilot automations](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automations)), so the repositories facing the most untrusted intake are excluded.
- Adding a filter instead of narrowing tools. A broadly triggered agent with a minimal tool set is easier to reason about than a narrowly filtered agent holding broad tools, because the filter is configuration that drifts as labels are renamed while the tool grant is the thing that bounds damage. Reach for the trigger filter to control cost, noise, and injection surface — not to substitute for scope.

## Example

A team wants an agent to triage inbound bugs but never to touch anything release-related. The gates get set in order of authority.

The trigger gate fires on issue creation with a search-query filter restricting the run to issues that are not already labeled `release`. Because the default excludes events from users without write access, an outside reporter's issue does not start a run until someone on the team engages with it.

The tool gate grants label and issue-type tools only. No assignment tool, no close tool, no pull-request tool. Even a fully injected run cannot close an issue or dispatch work, because the capability was never granted.

The approval gate is set to Cautious while the team calibrates, so medium and low-confidence labels queue for review. After a month of reading the rationale on accepted suggestions, they move to Balanced. Nothing about that change alters what the agent is permitted to do — only how much of its output they read first.

## Key Takeaways

- Three gates stand between an incoming issue and a changed one: trigger, tool, and approval. Only the first two carry authority.
- GitHub states that approvals "are a workflow convenience, not a security control" and directs teams to repository and agent permissions instead.
- The trigger gate is deterministic and pre-model, so a filtered-out issue never enters the agent's context — this is what makes it an injection boundary.
- Self-rated confidence is a weak threshold signal, and weakest on exactly the evidence-gathering work that issue triage consists of.
- Set triggers and tools as if the approval queue did not exist, then use the automation level to tune reading volume.
- Repository-level automation levels govern automations that administrators cannot see, so the policy is not an inventory.

## Related

- [Issue-Tracker as Agent Dispatch Surface](../../workflows/issue-tracker-agent-dispatch-surface.md) — the dispatch contract this gating sits inside; names the opt-in pickup filter as a precondition
- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](classifier-gated-auto-permission.md) — the in-session counterpart, deciding per tool call rather than per intake event
- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — a deterministic predicate on the write path, operating inside the tool gate
- [Safe Outputs Pattern](../../security/safe-outputs-pattern.md) — the architectural guarantee that grants write capability per output type rather than reviewing writes afterwards
- [Verification-Gated Agent Autonomy via Automated Review](verification-gated-agent-autonomy.md) — what to do when review must scale past a human reading every suggestion
- [Comment-Triggered Agent Dispatch on Issues and PRs](../../workflows/comment-triggered-agent-dispatch.md) — the trigger gate applied to a comment, where the phrase is public and the automation behind it is not

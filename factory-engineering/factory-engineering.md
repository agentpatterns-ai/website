---
title: "Factory Engineering Across Software Delivery Systems"
term: "Factory Engineering"
description: "Define factory engineering across agent-assisted delivery, compare practitioner definitions, and locate its boundaries with adjacent engineering disciplines."
tags:
  - factory-engineering
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Factory Engineering Across Software Delivery Systems

> Factory engineering designs and improves software delivery systems that use coding agents, where repeatable work and checkable outcomes justify maintaining those systems.

Factory engineering is this site's editorial category for designing, operating, and improving the process that produces software with coding agents. Use it when decisions span delivery stages. Its boundary synthesizes [Warp's production-process responsibility](https://www.warp.dev/blog/adapting-for-a-world-of-software-factories) and [Factory Engineering's repeatable team processes](https://factoryengineering.dev/getting-started/introduction/overview/). The terminology is still developing; these sources do not establish an industry standard. For occasional tasks, [Anthropic's simplicity guidance](https://www.anthropic.com/research/building-effective-agents) supports starting with less orchestration.

## Different definitions retain different controls

Three accounts use the factory term with different boundaries:

| Account | Attributed meaning | Review boundary |
|---|---|---|
| [Zach Lloyd at Warp](https://www.warp.dev/blog/adapting-for-a-world-of-software-factories) | Engineers build the product and improve the system that builds it | Fully dark operation is unrealistic in Warp's described setting |
| [Justin McCarthy at StrongDM](https://factory.strongdm.ai/) | Specifications and scenarios direct non-interactive development | StrongDM reports convergence without human code review |
| [Factory Engineering](https://factoryengineering.dev/getting-started/introduction/overview/) | Teams compose IDE features into repeatable processes | The definition centers on reusable processes rather than prescribing a review gate |

We therefore leave hosting location, agent count, and human-review policy outside the shared definition. This boundary is an editorial inference from these accounts. StrongDM's report does not establish universal safety. The existing [software factory model](../workflows/software-factory-model.md) describes a human-review boundary as one account, alongside other production choices.

## Category boundary and adjacent disciplines

Changing product behavior and changing its production process are separate responsibilities in [Warp's account](https://www.warp.dev/blog/adapting-for-a-world-of-software-factories). A feature changes what users receive. Revising the checks or agent configuration changes how the team produces future changes.

Use this editorial map to locate the narrower design decision:

| Discipline | Decision to examine |
|---|---|
| Product engineering and [human judgment](../human/judgment-relocation.md) | What behavior is useful, and who accepts it? |
| [Tool engineering](../tool-engineering/tool-engineering.md) | What interfaces can the agent call? |
| [Context engineering](../context-engineering/context-engineering.md) | What information reaches the model? |
| [Harness engineering](../patterns/agent-design/harness-engineering.md) | What environment and controls surround execution? |
| [Loop engineering](../loop-engineering/loop-engineering.md) | What repeats, receives feedback, and stops? |
| Factory engineering | How do these decisions connect across delivery stages? |

For stage-specific guidance, follow [intake](../workflows/backlog-triage-skill.md), [execution](../workflows/issue-to-pr-delegation-pipeline.md), and [feedback](../workflows/continuous-agent-improvement.md). The section index connects [integration and release decisions](index.md#verification-and-operations). These links map responsibilities; they do not prescribe one implementation.

## Why it works

Tests expose deviations. [Anthropic describes coding agents using test results to guide another implementation attempt](https://www.anthropic.com/research/building-effective-agents). [Warp extends feedback to the production process](https://www.warp.dev/blog/adapting-for-a-world-of-software-factories): engineers measure results, change context or skills, and test improvements. This explains a correction mechanism. Neither account establishes a productivity gain for every team.

## When this backfires

Apply these limits before adding more orchestration:

- For occasional unrelated work, a maintained delivery system can add unnecessary complexity. This is an inference from [Anthropic's advice to start simply](https://www.anthropic.com/research/building-effective-agents).
- Weak acceptance checks reward the wrong result. [StrongDM reports agents taking shortcuts against narrow tests](https://factory.strongdm.ai/).
- Faster execution leaves product intent unresolved when nobody owns usefulness. This risk follows from [Warp's retained product responsibility](https://www.warp.dev/blog/adapting-for-a-world-of-software-factories).
- A completed run does not satisfy a separate review policy. [Stripe retains another engineer's review](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents).

## Example

[Stripe's Minions](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) run unattended, commonly from a Slack request. A run uses CI and prepares a pull request. The requesting engineer can give further instructions or finish the work manually. If satisfied, that engineer opens the PR and requests review from another Stripe engineer.

This account separates 3 events: the agent completes its run, prepares a change, and hands that change to the review process. Unattended coding does not imply unattended merge or release.

## Key Takeaways

- Attribute the factory definition before adopting its review policy.
- Keep product responsibility explicit when improving the production process.
- Treat run completion and permission to merge as separate decisions.

## Related

- [Release Authority Boundaries for Software Factories](release-authority-boundaries.md)
- [Acceptance Scenario Lifecycle for Software Factories](acceptance-scenario-lifecycle.md)
- [Work Dispatch and Change Integration in Agent Pipelines](work-dispatch-and-change-integration.md)
- [Factory as Code: Versioning the Agent Delivery Definition](factory-as-code.md)
- [The Software Factory Model](../workflows/software-factory-model.md) — production and review choices
- [Factory Over Assistant](../workflows/factory-over-assistant.md) — asynchronous agent work
- [Judgment Relocation](../human/judgment-relocation.md) — ownership of product and verification decisions

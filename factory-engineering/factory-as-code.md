---
title: "Factory as Code: Versioning the Agent Delivery Definition"
term: "Factory as Code"
description: "Compare agent delivery definitions in Warp, Stripe, and Symphony, with guidance on revision records and limits on reproduction."
tags:
  - factory-engineering
  - tool-agnostic
aliases:
  - factories as code
  - factory definition as code
  - versioned factory definition
last_reviewed: 2026-11-06
maturity: emerging
---

# Factory as Code: Versioning the Agent Delivery Definition

> Factory as code keeps the agent delivery definition in version control for configuration comparisons ([configuration](https://www.warp.dev/factories/configuration), [rationale](https://www.warp.dev/blog/build-production-software-factory)).

Version the factory definition to compare configurations, as [Lloyd proposes for Warp](https://www.warp.dev/blog/build-production-software-factory). The recommendation here requires covering the concerns that affect outcomes and recording the revision each run uses. [Hadlow's configuration critique](https://mikehadlow.blogspot.com/2012/05/configuration-complexity-clock.html) favors considering ordinary code when a slicker build-test-deploy cycle makes it simpler.

## What three sources put in the definition

The inventory distinguishes Warp's vendor proposal, Stripe's practitioner account, and Symphony's normative specification.

| Concern | Warp | Stripe | Symphony |
|---|---|---|---|
| Intake | `integrations` and `webhooks/` | Not stated | `tracker` and `polling` keys |
| Workflow route | `agents/` and `automations/` | Blueprint, defined in code | Prompt body of `WORKFLOW.md` |
| Runner and sandbox | `runners/` and `agentDefaults.runner` | Devbox described separately; blueprint binding unstated | `workspace`, `hooks` and `codex.thread_sandbox` keys |
| Tools | `mcpServers` names a centrally managed server | Blueprints can constrain subagent tools; node-to-Toolshed-set binding unstated | Adapter-owned provider-native tools ([L1091–L1093](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L1091-L1093)) |
| Secrets | `secrets` names them; values stay outside | Not stated | Explicit environment references or adapter-documented fallback ([L546–L548](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L546-L548)) |
| Models and harness | `agentDefaults.model` (`auto` in the sample) | Goose fork described separately; blueprint binding unstated | `codex.command`; Codex values are pass-through |
| Review and handoff | Article asks who reviews and how many rounds | Human handoff after second push and CI run | Workflow-defined handoff state ([L43–L44](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L43-L44)) |
| Output artifacts and storage | Article requires persistent traces and artifacts, including PRs, videos and screenshots | Branch returned to human; artifact schema unstated | Artifact schema not stated in cited sections |
| Evaluation | `scorers/` and `benchmarks/` | Not stated | Not stated |

Sources: [Warp's article](https://www.warp.dev/blog/build-production-software-factory) describes orchestration duties; its output and handoff entries above are not YAML fields. Warp's [Factories as Code page](https://www.warp.dev/factories/configuration) (`schemaVersion: v1alpha1`, early access), [Stripe's minions article](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), and [Symphony SPEC.md at a pinned commit](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L355-L491) (Draft v1). The table compares these sources only; it defines no shared schema. Stripe does not specify a complete blueprint configuration inventory.

## Definition, orchestrator and records

Symphony separates repository policy from coordination and execution ([SPEC.md L118-L141](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L118-L141)). Two of Lloyd's orchestrator duties are "Read the code at the current version (or a branch if you are running an experiment)" and "Record any artifacts + agent traces into persistent storage" ([Warp](https://www.warp.dev/blog/build-production-software-factory)).

Separate three records. This is editorial design guidance, based on [Warp's orchestrator duties](https://www.warp.dev/blog/build-production-software-factory) and [Symphony's repository-owned policy](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L27-L28):

- Product revision: the code the agents change.
- Factory revision: the definition commit.
- Run output: the trace, the artifacts and the effective configuration, including the factory revision the run used.

Record the exact definition commit loaded for each run, rather than only a branch name. If configuration reloads, associate the run with the effective configuration it used. These are editorial recommendations; neither [Warp](https://www.warp.dev/blog/build-production-software-factory) nor [Symphony](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L1361-L1371) requires this three-record join.

Symphony requires the context identifiers `issue_id`, `issue_identifier` and `session_id` in logs ([L1361-L1371](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L1361-L1371)), not a workflow revision. The spec requires hot reload of the file and says "Implementations are not REQUIRED to restart in-flight agent sessions automatically when config changes" ([L560-L577](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L560-L577)). A log alone can leave the revision in effect unclear.

Symphony expects `WORKFLOW.md` to be repository-owned and version-controlled ([L330](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L330)). As design guidance, keep factory changes distinguishable by commit or path when investigating a regression.

## What the sources say it enables

Lloyd proposes comparing configuration performance ([Warp](https://www.warp.dev/blog/build-production-software-factory)). Keeping policy in-repo gives it the code's version history ([Symphony](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L27-L28)).

## Example: Stripe's blueprint

Gray describes blueprints as "workflows defined in code that direct a minion run". "Implement task" and "Fix CI failures" are agent-like nodes. "Run configured linters" and "Push changes" run code with no model call. The blueprint hands the branch to a human operator after the second push and CI run ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)).

Gray describes the devbox, Toolshed, the goose fork and security controls separately. The article gives no complete blueprint binding inventory or blueprint release process ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)). The example establishes a code-defined workflow; it does not establish how Stripe versions it.

## Limits on reproduction

Thinking Machines Lab found that "LLM APIs are still not deterministic in practice" even at temperature 0, although batch-invariant kernels made 1,000 completions of one prompt identical in its vLLM test ([Thinking Machines Lab](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)). The tested kernels do not guarantee identical results across hardware or software versions ([limits](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)). Anthropic's deprecation page states "Requests to retired models fail" ([Anthropic](https://platform.claude.com/docs/en/about-claude/model-deprecations)). Warp's sample uses `model: auto` rather than an explicit model identifier ([configuration page](https://www.warp.dev/factories/configuration)).

Lloyd names the state limit: "you can't just naively replay fixing a task when the task tracker has already marked the task as complete", so a replay also needs the original tracker state ([Warp](https://www.warp.dev/blog/build-production-software-factory)).

## When this backfires

- Hadlow warns that rich configuration grows into a DSL, and "with a slicker build-test-deploy cycle, it might be far simpler just to hard code it" ([Hadlow](https://mikehadlow.blogspot.com/2012/05/configuration-complexity-clock.html)).
- Stripe permits team-specific blueprints ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)). Check for divergent policy before treating those definitions as equivalent.
- Symphony requires reloads without requiring in-flight restarts or a revision log field ([reload](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L560-L577), [logging](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L1361-L1371)). The inference is that run-to-revision attribution can remain unclear.

Use [reconstructable factory runs](reconstructable-factory-runs.md) for the run identity and evidence record.

## Key Takeaways

- For configurations like [Warp's](https://www.warp.dev/factories/configuration), record external dependency identifiers and secret references or versions alongside the definition. Keep secret values outside run records.
- Check for a revision in the run record before relying on version history for attribution; [Symphony's required log fields](https://github.com/openai/symphony/blob/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md#L1361-L1371) omit it.

## Related

- [Test Factory Changes on Representative Work Before Promotion](controlled-factory-experiments.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Factory Engineering](index.md) — the section this page belongs to
- [The Software Factory Model](../workflows/software-factory-model.md) — what the definition describes
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) — use run evidence to change configuration
- [Symphony: Open Spec for Issue-Tracker-Driven Coding Agent Orchestration](../standards/symphony-orchestration-spec.md) — the full Symphony contract
- [Portable Harness Specification](../patterns/agent-design/portable-harness-specification.md) — record the harness that ran
- [Artifact-Driven Workflow Compilation](../patterns/agent-design/artifact-driven-workflow-compilation.md) — declare each step's inputs and outputs

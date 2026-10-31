---
title: "Local Inference Under a Cloud Router"
term: "Cloud-Routed Local Inference"
description: "Copilot Fusion can send a request to an on-device model, but the routing decision, the eligibility list, and the model policy all stay server-side. Local inference moves compute, not control."
tags:
  - agent-design
  - cost-performance
  - model-routing
  - copilot
aliases:
  - cloud-routed local inference
  - router-selected on-device model
  - hybrid local and cloud model routing
last_reviewed: 2026-10-30
maturity: emerging
---

# Local Inference Under a Cloud Router

> A router that can pick an on-device model still decides in the cloud, so local inference relocates the compute and leaves the decision remote.

Router-selected local inference is a narrow option with four conditions attached. It does not produce an offline or closed-path session. GitHub shipped it for Copilot Fusion on 28 October 2026 ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)), and the feature page still carries "This feature is in public preview and is subject to change" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). Read the conditions before you treat an on-device model as a data-residency or air-gap control.

## The four conditions

| Condition | What the source says |
|---|---|
| The session does not become offline | "Local inference doesn't make your session offline. Copilot Fusion still makes routing decisions in the cloud, and local models may have different safety protections from Copilot-provided cloud models" ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)) |
| Two models are eligible | MAI Code 1.1 Flash via the Windows ML provider, or MAI Code 1.1 Flash and Qwen3.8 Flash Next "through a local OpenAI-compatible server" ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)) |
| One effort level routes locally | A locally installed model can be used "when appropriate, but only from the Fusion Standard effort level" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)) |
| Configuring a provider is not eligibility | "Adding or discovering a model through bring your own key (BYOK) configuration doesn't automatically make it eligible for Copilot Fusion" ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)) |

Two limits narrow it further. The managed download is Windows-only, and in the Copilot app "its intelligent routing currently supports managed Windows ML models only", so cross-platform local routing runs in Copilot CLI ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)). Eligibility is a preference, not a guarantee: installed models are "more likely to be used, where appropriate, on the Fusion Standard effort level" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)).

The effort-level restriction costs more than it looks. In Fusion's [cascade and critique patterns](../multi-agent/runtime-workflow-selection-hydrafusion.md), "a judge inspects the draft and decides whether to accept it or escalate to a stronger model", or several models critique it in parallel ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). Fusion Standard runs neither: its row reads "Everyday work. Copilot Fusion selects one model for each task" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). A request routed on-device gets the single-model path, so the quality gate that justifies the higher effort levels never sees it.

## Why it works

The decision depends on state that is only authoritative server-side, so moving inference to the device cannot move the decision with it. Fusion's choice rests on plan entitlement, administrator model policy, and live model health. It "considers real-time system health and availability when choosing models", and it excludes "Models excluded by policies restricting Copilot to data-resident or FedRAMP-compliant models" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). An on-device process holds none of those inputs. The eligibility gate has the same shape, because the pool is a vendor evaluation result: "The model pool changes as new models become available and as GitHub evaluates which models perform best" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). [Tenant model policy](tenant-model-policy.md) describes the same policy-plane and execution-plane split for the cloud-only case.

## When this backfires

- You need an air-gapped or offline session. Routing decisions still happen in the cloud, so the property that motivated [Copilot CLI BYOK and local models](../../tools/copilot/copilot-cli-byok-local-models.md) does not survive router selection.
- You need a known safety posture. Local models "may have different safety protections from Copilot-provided cloud models", so widening the pool widens the posture you are accountable for ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)).
- The task needs the orchestration quality gate. Local eligibility exists only at the effort level that picks one model per task, so cascade and critique are out of reach on that path.
- You need run-to-run reproducibility. Eligible models are only more likely to be chosen, and "The execution patterns and model pool used may change over time", so the same prompt can land on-device or in the cloud across runs ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)).
- You already run a BYOK fleet. Only the two named models qualify, so a configured Ollama endpoint is not eligible by virtue of being configured.
- The hardware is marginal. You manage the runtime, and "your device must have sufficient resources to run it" ([GitHub Changelog, 2026-10-28](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models)).

Quality is the condition practitioners hit first. Birgitta Böckeler's evaluation of small local models for agentic coding concludes "it's definitely not a plug-and-play type of experience yet". Her working rule is to reach for one "when I have small, straightforward tasks, often pre-planned by a bigger model" ([Böckeler, Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/local-models-for-coding-experiences.html)). A router that classifies that task shape for you removes a manual step without raising the model's ceiling. The factors setting that ceiling are in [Local Model Viability Factors for Coding](local-model-viability-for-coding.md).

## Example

When a request must run on a specific model, the docs name a deterministic alternative. You "can configure a custom agent to use a specific local model, and then, in your prompt, instruct Copilot to use that custom agent for the task, or for a specific part of the task" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). That pins the model instead of biasing a probability, which is what a hard requirement needs.

Enabling the routed path instead takes one experimental setting per client, each named in the docs ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). In Copilot CLI it is the `--experimental` option, or `/experimental on` in a session.

Either way you can see which models ran, once the response arrives: "When the response is provided, you can hover over the effort level name below the response to see a list of models used" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)). That is a record of one response, not a guarantee about the next one. [Per-surface routing visibility](per-surface-routing-visibility.md) covers how much of the decision each client lets you keep.

## Key Takeaways

- Write data-residency and air-gap requirements against where the decision is made, not where the tokens are generated. The two answers differ here.
- Treat the eligibility list as a vendor allowlist. An endpoint you configured yourself is a model you can select, not a model the router may choose.
- Pin the model with a custom agent when the requirement is hard, and leave routing for the cases where any eligible model will do.
- Check the effort level before you count on a review step: the level that routes locally is the level that runs one model per task.

## Related

- [Local Model Viability Factors for Coding](local-model-viability-for-coding.md) — the RAM, context, and tool-calling factors that decide whether a local model can do the task at all
- [Auto Model Selection](auto-model-selection.md) — the broader harness-side pattern of handing per-request model choice to the vendor
- [Per-Surface Routing Visibility in Copilot (HydraFusion)](per-surface-routing-visibility.md) — how much of a routing decision each Copilot client lets you see and keep
- [Router-Imposed Quality Ceiling: Committing Before Output](router-imposed-quality-ceiling.md) — what a router caps when it commits to a model before any candidate answer exists
- [Copilot CLI BYOK and Local Model Support](../../tools/copilot/copilot-cli-byok-local-models.md) — selecting your own provider directly, without a router in the path

---
title: "Extension Layers for an Organization-Wide Spec Toolkit"
description: "Curate an install catalog, carry policy in priority-ordered presets, ship them as pinned bundles, and gate conformance in CI, because the toolkit's resolution order ranks the project above the organization."
term: "Spec Toolkit Extension Layers"
aliases:
  - spec kit extensibility layers
  - governed preset catalog
  - organization baseline preset
tags:
  - workflows
  - agent-design
  - tool-agnostic
last_reviewed: 2026-10-08
maturity: emerging
---

# Extension Layers for an Organization-Wide Spec Toolkit

> A spec toolkit's extension layers distribute organizational standards by default, and its resolution order ranks the project above the organization.

Run the layers for distribution and put the hard gate somewhere else. Spec Kit's extensibility model gives an organization four places to install policy without forking the toolkit, and its documented resolution stack places project-local overrides above every one of them. That makes the layers a good way to set a default and a poor way to require anything.

Three conditions decide whether this is worth building.

- More than one team shares the toolkit. The layering exists to compose an "Organization baseline" with a "Domain and technology overlay" and a "Team customization" layer ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)). One team has no second layer, and a project-local override directory does the same job with no catalog to curate.
- Specs pass through CI. Layer 4 below is the only part that enforces, and it needs a pipeline to live in.
- Someone owns extension review. Nobody does it for you: "Most extensions are independently created and maintained by their respective authors. The Spec Kit maintainers do not review, audit, endorse, or support extension code" ([Spec Kit extensions reference](https://github.github.io/spec-kit/reference/extensions.html)).

## The per-team fork problem

A spec-first workflow arrives configured for one developer in one repository. An organization with security reviews, domain terminology, and mandatory acceptance criteria has to change the templates, and the obvious way is to copy the toolkit. Microsoft's account names the cost: "Forking the toolkit for every team would fragment the experience and make upgrades costly. The better model is a stable core with explicit extension points" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)).

A fork of the [spec-driven development](spec-driven-development.md) toolkit has to be upgraded on its own, which is the cost Microsoft names. The copy-then-diverge half of this is the problem [a central standards repo](central-repo-shared-agent-standards.md) solves for instruction files. One difference decides the design below. A spec toolkit ships a resolution stack, and an instruction file does not.

## Four implementation layers

```mermaid
flowchart LR
    A[Curate org catalog] --> B[Install baseline presets]
    B --> C[Ship as pinned bundle]
    C --> D[Gate conformance in CI]
```

### Layer 1: A catalog you own as the install source

Catalogs decide where `search` and `add` look, and both sources call the two-kind split a security control. The reference docs say the distinction "is a security boundary, not a limitation", and that "`community` is intentionally discovery-only because it is an open, unvetted list" ([Spec Kit extensions reference](https://github.github.io/spec-kit/reference/extensions.html)). The blog puts it from the organization's side: a community listing "confirms format and metadata – not a security review or endorsement of its code" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)).

An organization catalog is a YAML entry marked `install_allowed: true` with a priority number, plus the review work behind it. Treat it as the default source rather than the only one. The docs name three routes around it. `SPECKIT_CATALOG_URL` "overrides all catalogs", a project's own `.specify/extension-catalogs.yml` outranks the user-level file an organization would ship it in. `--from <url>` installs "from a custom URL instead of the catalog" ([Spec Kit extensions reference](https://github.github.io/spec-kit/reference/extensions.html)). That last route is the documented way to install a reviewed find from the community list.

### Layer 2: Presets for policy, extensions for capability

Presets override what already exists. Extensions add what does not. Microsoft's write-up draws the division: "presets change existing behavior, extensions add capabilities, bundles package reusable stacks, and workflows automate repeatable processes" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)). A security preset strengthens the threat-modeling prompt in the existing plan template; a security-review command is an extension.

Both resolve through one stack, and its order is the fact to design around. The four levels below come from the [Spec Kit presets reference](https://github.github.io/spec-kit/reference/presets.html), which adds that "Each file name is evaluated independently against the priority stack, so different files can come from different layers."

| Precedence | Layer | Who sets it |
|---|---|---|
| 1 (highest) | Project-local overrides, `.specify/templates/overrides/` | Whoever works in the repository |
| 2 | Installed presets, by priority number | Whoever runs `specify preset add` |
| 3 | Installed extensions, by priority number | Whoever runs `specify extension add` |
| 4 (lowest) | Spec Kit core, `.specify/templates/` | The toolkit release |

An organization baseline therefore wins every template no higher layer provides, and loses any template a project overrides. The write-up's constitution layering calls its bottom layer "non-negotiable engineering expectations that apply everywhere" while describing the mechanism as "giving flexibility to teams to add / override any specific guidelines they want" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)). Both statements are live, so take the weaker one: the baseline is a default, and its non-negotiability is a review convention you supply.

### Layer 3: Bundles as the distribution unit

A bundle composes presets, extensions, and workflows into one installable version. It adds nothing at runtime: "Bundles add no new runtime behavior of their own: they are a distribution and composition layer over the primitives you already use" ([Spec Kit bundles reference](https://github.github.io/spec-kit/reference/bundles.html)). For the adopting team it replaces "a long list of installation steps with one governed entry point" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)). It also carries version pins and a provenance record per component.

Read the pins before you audit against them. "Pin enforcement is install-time only. Idempotency checks are id-based, not version-aware", so a component already present and owned by a bundle "is skipped during `install` without comparing its on-disk version to the manifest pin" ([Spec Kit bundles reference](https://github.github.io/spec-kit/reference/bundles.html)). The manifest describes what a fresh install would produce, not what sits on a developer's disk. Closing that gap means `specify bundle update` on a schedule, the pipeline half of this layer.

### Layer 4: A CI gate outside the resolution stack

Microsoft's write-up names gates and checks delivered as extensions: "a security-review command, an accessibility validation gate", and a bundle with "service-specific quality gates". Those sit inside the resolution stack. It names no check that runs outside the stack on what the stack resolved to. The enforcement it does describe applies to what may enter the catalog: "An organization catalog can also enforce contribution standards, provenance, prompt-injection safeguards, and documented ownership" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)). That governs the supply, not the resolution. Layers 1 to 3 are configuration a developer on that machine can outrank, and an extension-delivered gate is part of that configuration. A check running on the repository, outside the stack, is what turns a baseline into a requirement.

Two cheap forms work.

Assert the resolved content. `specify preset resolve <name>` "Shows which file will be used for a given name by tracing the full resolution stack" ([Spec Kit presets reference](https://github.github.io/spec-kit/reference/presets.html)). A job fails when a governed template is not the winning layer.

Assert provenance. `specify preset list --json` prints a `source` field. It reads `{"kind":"catalog","catalog":"<catalog-name>"}` for a catalog install and `{"kind":"local"}` "for local, legacy, or malformed provenance" ([Spec Kit presets reference](https://github.github.io/spec-kit/reference/presets.html)). That is enough to fail a project running an unvetted component.

## Why it works

Standards spread here by default-setting inside a file lookup, not by restriction. Each template, command, and script name resolves independently down the four-level stack, and "the first match in the priority stack wins and is used entirely" ([Spec Kit presets reference](https://github.github.io/spec-kit/reference/presets.html)). A baseline installed as a preset becomes the effective content of every artifact no higher layer supplies, with nobody copying a file. Core upgrades keep arriving for the same reason: the core still sits at the bottom of the project's stack, where a fork would have removed it. That is why the write-up recommends keeping "customization modular and the core untouched" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)).

The same mechanism caps what the arrangement can promise. A layer's authority is its position in a lookup, and position 1 belongs to the repository.

## Triggers and constraints

The cycle is push-driven at the bottom and scheduled at the top. A project adopts by installing the bundle, CI re-checks resolution on every push, and a scheduled `specify bundle update` re-applies the pins the idempotency check skips.

Three things bound the automation's authority.

- A preset update has no rollback. "Update is deliberately destructive" and "If removal succeeds but replacement installation fails, the previous preset has already been removed" ([Spec Kit presets reference](https://github.github.io/spec-kit/reference/presets.html)). Run it unattended against an unreachable source and the project loses the baseline rather than keeping the old one.
- A failed bundle install can leave the project in a state no record describes: "a failed install records nothing", and cleanup is "best-effort basis — removal errors are swallowed, so partial on-disk state may remain" ([Spec Kit bundles reference](https://github.github.io/spec-kit/reference/bundles.html)).
- The workflow layer keeps the human in it by design. Workflows "can chain commands, prompts, scripts, and human checkpoints" and "pause or resume when review is required", and the stated goal "is not to remove human judgment" ([Gupta, 2026-10-07](https://devblogs.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/)). Adopt them last, which is the write-up's advice too: "Add workflows after the underlying process, artifacts, checkpoints, and exception paths are clear."

Implementation is tool-agnostic, with one check to run first.

The presets reference says "Preset commands are automatically registered with supported active AI coding agent integrations". The generic integration is not one of them, because it "currently delivers extension invocations but does not register preset command or skill overrides" ([Spec Kit presets reference](https://github.github.io/spec-kit/reference/presets.html)). Confirm your assistant has a named integration before Layer 2 carries a command override.

## When this backfires

- One team, one repository. There is no second layer to compose, and `.specify/templates/overrides/` already wins everything. The catalog is pure overhead.
- No CI. Layer 4 has nowhere to run, so what you have shipped is a convention with good defaults.
- Pins treated as a deployment record. Install-time-only enforcement means a clean manifest and a stale checkout look identical from the manifest side.
- The spec itself is the binding cost. Layering over a loop whose expense is writing and reviewing the spec makes it slower without touching the cause, the failure mode [spec complexity displacement](../patterns/anti-patterns/spec-complexity-displacement.md) names. Microsoft's article names no speed, token, or latency cost for the added process, so measure one yourself rather than taking it from the write-up.
- Expecting conformance from encoded standards. A practitioner who shipped an internal tool this way credits his own review discipline instead: "Spec-driven development gives you leverage, not absolution" ([Fisher, Atomic Object](https://spin.atomicobject.com/rfp-finder-speckit/)). One project, no control group, and the only firsthand cost account that turned up.
- Maturity. No benchmark or controlled comparison measures what spec-driven development costs an organization against a conventional workflow. Microsoft's framing at launch was that "GitHub Spec Kit is an *experiment* -- there are a lot of questions that we still want to answer" ([Visual Studio Magazine, 2025-09-16](https://visualstudiomagazine.com/articles/2025/09/16/github-spec-kit-experiment-a-lot-of-questions.aspx)).

There is a real argument for skipping layer 4. The override routes are deliberate escape hatches, and each leaves a trace: a `source` field, a resolution trace, a bundle provenance record. Auditing those catches the project that routed around the baseline and keeps the context to tell an agreed exception from drift, where a red build flattens both. Nobody has measured either arrangement, so if your organization reads its audit trails, start there and add the gate when it stops being read.

## Example

A platform team publishes `org-catalog.json` with two presets and one extension, marked `install_allowed: true` at priority 5. The baseline preset replaces `plan-template.md` with a version carrying a mandatory threat-model section. A `payments` domain preset appends acceptance criteria. The extension adds a `speckit.secreview` command. All three ship as a bundle pinned to exact versions.

A payments service installs the bundle and gets all three. Six weeks later a developer finds the generated plan too heavy and drops a trimmed `plan-template.md` into `.specify/templates/overrides/`. That file is precedence 1, so it wins over both presets, and the threat-model section disappears from every plan the project generates from then on. The bundle is still installed, its provenance record is still clean, and `specify bundle list` still shows the pinned version.

The CI job catches it, because `specify preset resolve plan-template.md` reports the override directory rather than the baseline preset. The pipeline fails with the resolved path in the message. Without that job, the next signal is a security review asking where the threat model went.

## Key Takeaways

- Budget the four layers as distribution, not control. A project that drops a file into `.specify/templates/overrides/` outranks every preset and extension you installed, and nothing surfaces that until something asks `specify preset resolve`.
- Put the enforcement in CI, and assert two things: which layer wins a governed file, and whether every installed component has a catalog `source` rather than a local one.
- The governed catalog is a default install source and a review obligation. `--from`, a project catalog file, and `SPECKIT_CATALOG_URL` all reach outside it, and the toolkit's maintainers audit no extension code on your behalf.
- Bundle version pins apply when a component is first installed or refreshed, so a pinned manifest is not evidence of what is deployed. Schedule the refresh.
- Adopt the workflow layer last, and never run `specify preset update` unattended: it removes before it installs and has no rollback.

## Related

- [Spec-Driven Development with Spec Kit](spec-driven-development.md) — the core specify, plan, tasks loop these layers customize without forking
- [Enforcement Modes in Spec-First Agent Frameworks](../patterns/agent-design/spec-first-framework-enforcement-modes.md) — the same question asked about the agent instead of the developer: sort controls by what cannot be edited
- [Central Repo for Shared Agent Standards](central-repo-shared-agent-standards.md) — the instruction-file version of this distribution problem, where no resolution stack exists to lean on
- [Enterprise Skill Marketplace: Distribution, Usage Reporting, and Quality Evals](enterprise-skill-marketplace.md) — what the catalog layer turns into above about fifty engineers
- [Spec Complexity Displacement](../patterns/anti-patterns/spec-complexity-displacement.md) — the cost this machinery sits on top of and cannot reduce

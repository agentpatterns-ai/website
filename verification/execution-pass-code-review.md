---
title: "Review That Runs the Application, Not Just the Diff"
term: "Execution Review Pass"
description: "Pair static review with a pass that renders the change and inspects it. A layout property is not in the diff, and the pass cannot repeat its own verdict."
tags:
  - testing-verification
  - code-review
  - tool-agnostic
aliases:
  - execution pass in code review
  - review by running the application
  - runtime review pass
last_reviewed: 2026-10-29
maturity: emerging
status: current
---

# Review That Runs the Application, Not Just the Diff

> Some checks on a change need the application actually running. An execution pass renders the change and inspects what a diff cannot express.

An execution review pass stands the changed application up, drives it like a user, and inspects the rendered result for defects a diff cannot express. It sits beside static review rather than replacing it. OpenAI's write-up on Greptile lists what a review covers: "Validating a pull request involves checking whether the code is logically correct, does what the developer intended, is secure, and avoids breaking existing functionality. For some of that testing, you need to actually run the application because reading the code alone might not reveal the problem" ([OpenAI](https://openai.com/index/greptile-code-review-codex-astra)). The post stops at "some of that testing" and never says which of the four checks needs execution. Which ones you move to a running application is yours to decide, and the conditions below are how to decide it.

## When the pass earns its place

Four conditions, and all four have to hold.

The change needs a rendered surface. A library, a CLI tool or a schema migration gives it nothing to look at.

No cheaper oracle can already cover the defect class. Checking a responsive page's layout for consistency across a range of viewport widths needs no explicit oracle at all ([Walsh, Kapfhammer and McMinn](https://eprints.whiterose.ac.uk/id/eprint/116989/)), and because it is an algorithm and not a judgment, it repeats and it can block a merge. A model looking at a page does neither.

Success criteria have to be written down. In the OSWorld reliability study, instruction ambiguity was one of three measured sources of unreliability, and rewriting task descriptions so success criteria were explicit improved reliability across GPT-5, Claude and Kimi, with smaller gains for Kimi ([Gonzalez-Pumariega et al.](https://arxiv.org/abs/2604.17849v1)). That is a benchmark result, not a review result. It is still the reason to write the pass a specification instead of briefing it to try to break the application.

A human reads the verdict, and a merge gate does not. The figures below say why.

## The worked example

Gupta's example is a button that disappears when a website is viewed on an iPhone. With GPT-6 Astra's computer use, the post says Greptile can start a development server for a pull request, resize the browser to an iPhone-sized viewport, and simulate a user moving through the application ([OpenAI](https://openai.com/index/greptile-code-review-codex-astra)). It continues: "The model's visual understanding lets it inspect the screen and spot the hidden button." Co-founder and CEO Daksh Gupta gives a staffing reason rather than an accuracy one: "A QA firm testing all of your changes is just impractically slow considering how fast we're able to ship code with these models." The post carries no defect-yield or pass-rate figure, so every capability line in it is an unmeasured vendor claim.

This is the reviewer's half of an author-side practice. An [agent-recorded video demo](agent-recorded-video-demos.md) is proof-of-work the author's agent hands a human, and each scene is a scripted assertion. The execution pass runs on the reviewing side and scripts nothing; the model looking at the screen goes where the assertion would.

## Why it works

Whether a button is visible at a phone-width viewport is a property of the rendered page, produced at run time by HTML, CSS, the layout engine and the viewport together. The diff does not hold that property, and this pattern applies when no test asserts it. Walsh, Kapfhammer and McMinn name the missing piece: "A central problem is the difficulty in providing an automated 'oracle' to validate RWD layouts against, meaning that checking for failures is largely a manual process in practice, which results in layout failures in many live responsive web sites" ([ISSTA 2017](https://eprints.whiterose.ac.uk/id/eprint/116989/)). Their own detector found failures in 16 of 26 real-world production pages studied, 33 distinct failures in total. Rendering the page and looking at it puts general visual judgment where that absent oracle should be. That substitution is the gain, and it arrives attached to the model's non-determinism.

## When this backfires

- Wired as a merge gate. For one strong configuration on OSWorld, Agent S3 with GPT-5, Pass@10 reached approximately 78% while the agent succeeded on all ten executions of a task for only about 36% of tasks ([Gonzalez-Pumariega et al.](https://arxiv.org/abs/2604.17849v1)). Gating on a verdict that unstable teaches reviewers to re-run until it goes green.
- A deterministic checker already covers the class. For responsive layout the 2017 technique above needs no explicit oracle and no model, so visual judgment on the same defects buys non-reproducibility.
- The front end is churning cosmetically. Under non-functional environment perturbations in the same study, GPT-5 regressed on reliability transitions and Claude dropped significantly; for Kimi the perturbations changed little, because its repeated-run success was already low in an unperturbed environment.
- Read as a reason to skip the machine surface. [Computer use as the last integration tier](../patterns/agent-design/computer-use-last-integration-tier.md) still applies: a browser tool reaches a web application, so justify the GUI pass by what visual inspection adds.
- Per-pull-request bring-up is expensive. Seeded data, authentication and third-party sandboxes can cost more than the review they serve.

## Key Takeaways

- Decide which checks move to a running application. The Greptile post names four things a review covers and says only that some of the testing needs the application run.
- When the repository lacks a suitable rendered-property check, visual judgment can provide an advisory result.
- Greptile's example is a capability description with no measured defect yield. Cite it as a vendor claim, and keep its throughput argument separate from an accuracy argument.
- Non-determinism is the price of that substitution, which is why the verdict routes to a reviewer instead of a gate.
- Price the pass against a deterministic checker before standing it up, and skip it outright when the change renders nothing.

## Related

- [Agent-Recorded Video Demos as a Verification Artifact](agent-recorded-video-demos.md) — the author-side artifact with scripted scenes, whose self-scripting hole a reviewer-side pass closes
- [Source-Grounded Test Plan with Pre-Action Assertion Annotation](pre-test-grounded-plan-assertion-annotation.md) — writing expected behavior down before a UI-driving agent runs
- [Behavioral Testing for Non-Deterministic AI Agents](behavioral-testing-agents.md) — treating variance as a product decision, the problem this pass has with its own verdict
- [Computer Use as the Last Integration Tier](../patterns/agent-design/computer-use-last-integration-tier.md) — the tier rule the pass must answer before it reaches for a GUI
- [Diff-Based Review Over Output Review](../code-review/diff-based-review.md) — the static half of the split

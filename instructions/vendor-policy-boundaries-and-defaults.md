---
title: "OpenAI Model Spec Boundaries and Overridable Defaults"
term: "Model Spec Boundaries and Defaults"
description: "OpenAI's Model Spec separates firm boundaries from overridable defaults. Read authority labels before changing developer instructions or style rules."
tags:
  - instructions
  - tool-agnostic
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# OpenAI Model Spec Boundaries and Overridable Defaults

> OpenAI's Model Spec sets firm boundaries and overridable defaults that determine which developer and user instructions should apply.

OpenAI's Model Spec separates firm boundaries from defaults developers and users may change. Developers direct applications within OpenAI's boundaries; users direct work within those constraints ([29 October 2026 announcement](https://openai.com/index/updated-model-spec/)).

The update organizes guidance around 5 values: faithfulness to human intent, harm minimization, honesty and transparency, human agency, and care ([announcement](https://openai.com/index/updated-model-spec/)).

## Read the authority label before changing a rule

The dated Spec assigns authority to sections as well as conversation messages. Its ordering determines which conflicting instructions should apply ([Model Spec, 29 October 2026](https://model-spec.openai.com/2026-10-29.html#follow_all_applicable_instructions)).

| Spec authority | What can override it |
|---|---|
| Root | No conversation instruction |
| System | Not developers or users |
| Developer | Developer instructions or higher authority |
| User | Explicit user instructions or higher authority |
| Guideline | Explicit instructions or clear contextual intent |

The Spec treats its own instructions as preceding conversation instructions at the same authority level. Later instructions can supersede earlier ones at that level. Recency does not defeat higher authority ([authority rules](https://model-spec.openai.com/2026-10-29.html#follow_all_applicable_instructions)).

For instruction-file authors, distinguish this ordering from [filesystem scope layering](layered-instruction-scopes.md). Inspect how your harness supplies the file before assigning it a message authority. A more specific file path is no reason to assume permission to override root or system rules.

## State the style your application needs

OpenAI's announcement says, "we're retiring most of the Spec's detailed style guidance." It says style should adapt to preferences through feedback and context. Stronger defaults remain, including objective treatment of questions ([new and retired sections](https://openai.com/index/updated-model-spec/#new-and-retired-sections)).

The practitioner consequence is an instruction audit. Do not treat a retired style rule as a continuing written default. Record your required style explicitly, and test it on representative tasks. This recommendation follows the policy change; the announcement supplies no measured compliance result.

## Separate published intent from observed behavior

OpenAI says deployed models do not yet fully reflect the Spec. The document describes behavior OpenAI is working toward ([what comes next](https://openai.com/index/updated-model-spec/#what-comes-next)).

Keep the policy citation and test result separate in your review notes. Record the dated section, its authority label, your proposed override, and the behavior you observed. A policy citation alone cannot establish that an instruction works. Use [runtime enforcement](enforcing-agent-behavior-with-hooks.md) for requirements that need a mechanical check.

The [specification authority boundary](../patterns/agent-design/specification-authority-boundary.md) addresses who may record completion evidence. Keep that runtime question separate from the vendor's instruction authority rules.

## Key Takeaways

- For each proposed override, record the Spec section's authority before testing the instruction.
- Keep explicit style requirements when your application needs a stable format; test them after model changes.
- Report observed behavior separately from what the published policy prescribes.

## Related

- [Layered instruction scopes](layered-instruction-scopes.md) — global, project, and directory instruction files
- [Enforcing agent behavior with hooks](enforcing-agent-behavior-with-hooks.md) — mechanical checks for behavioral requirements
- [Specification authority boundary](../patterns/agent-design/specification-authority-boundary.md) — validated evidence controls completion state

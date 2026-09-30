---
title: "Policy File Validation: Catching Silent Non-Enforcement"
term: "Policy File Validation"
description: "A defect in an agent policy file stops the rule applying instead of raising an error. What a commit-time validator catches, what it must report, and the two classes it never sees."
aliases:
  - silent non-enforcement
  - managed settings validation
  - agent config validation
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-27
maturity: emerging
---

# Policy File Validation: Catching Silent Non-Enforcement

> A policy file defect stops the rule applying with no error, so where you cannot fail closed, validate the file and report its path.

Policy file validation checks a checked-in governance file for defects that stop it applying. The report names each one with the file and the path inside it. Reach for it where the policy carries indirection you cannot test by hand: files referenced from other files, team overrides, a fleet of clients on their own refresh cycles. Two conditions bound what it buys. The report has to distinguish a clean result from a check that never ran, and it only covers defects visible in the file's shape.

## The state it exists to surface

A typo in a policy file does not raise an error; it stops the rule applying. Nothing happens, and nothing happening is also what a correctly enforced prohibition looks like. GitHub names the class while describing its own check, which "detects malformed JSON, unsupported configurations, invalid team mappings, and other errors that can prevent policies from being enforced" ([GitHub Changelog, 2026-09-25](https://github.blog/changelog/2026-09-25-enterprise-managed-settings-in-product-validator)). Until someone audits behavior across the fleet, that state is indistinguishable from compliance.

## What the report has to name

The report's content is the technique. A check that only says "invalid" leaves the administrator to reproduce the failure before fixing it. GitHub's validator reports coordinates instead: "Each issue identifies the affected file and JSON path, helping you make corrections to ensure that policies are enforced as intended" ([GitHub Changelog, 2026-09-25](https://github.blog/changelog/2026-09-25-enterprise-managed-settings-in-product-validator)). Its scope covers `copilot/managed-settings.json`, `copilot/team-mappings.json`, and "Any files in `copilot/teams/` that are referenced in `copilot/team-mappings.json`" ([GitHub Docs](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/get-started)). Claude Code runs the same class of check as `claude doctor`, whose remit includes "invalid settings files" ([Claude Code](https://code.claude.com/docs/en/debug-your-config)).

Zhang and colleagues graded commits that changed configuration error messages in HDFS, HBase, Spark, and Cassandra onto four levels, where L4 messages "Contain parameter names and provide guidance for fixing" and L1 messages carry "No mention of configuration" ([arXiv:2102.07052v2](https://arxiv.org/abs/2102.07052v2)). File, path, and reason sits at the L3-to-L4 end of that scale.

## Why it works

Detecting silent non-enforcement any other way is behavioral: observe what users did, compare it against what the policy said, and repeat for every client. Each such check needs someone to start it, so the defect lasts until someone does. A commit-time check swaps it for reading one page after a push. The same study shows the unchecked state is the normal one: 74.6% (50/67) of commits that changed configuration checking code "occurred after users reported runtime failures, service unavailability, incorrect/unexpected results, startup failures, etc." ([arXiv:2102.07052v2](https://arxiv.org/abs/2102.07052v2)).

Cedar names the bound on how far such a check can reach. It needs a schema of the application's entity types, attributes, and relationships, because without one it "can't know whether this policy is right or wrong by examining it in isolation". Cedar cannot tell whether the author meant `Uzer` or `User`, "because both are well-formed names" ([Cedar](https://docs.cedarpolicy.com/policies/validation.html)). Given a schema it does reach the inert case, warning on policies that "always evaluate to false, and thus never apply". Coverage is a property of the schema, not of owning a validator.

## When this backfires

- You read a clean result as enforcement. GitHub's section is hidden when there is nothing to report, and when the check cannot run, "your existing settings continue to apply" ([GitHub Docs](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/get-started)). An absent section covers both "valid" and "not checked".
- The defect is semantic rather than structural. Claude Code documents the uncovered case in the same harness that ships the check: "A misspelled tool name produces a matcher that matches nothing, so the hook fails silently" ([Claude Code](https://code.claude.com/docs/en/debug-your-config)).
- You treat valid as enforced now. Server-managed settings reach supported clients "within about an hour", MDM-managed clients "check for updated policies hourly", and file-based deployments need a client restart ([GitHub Docs](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/get-started)).
- You inherit the check's severity ordering. GitHub's own screenshot pairs an invalid JSON error with "a warning that the enterprise team slug mona-team was not found", while the same changelog lists "invalid team mappings" among the errors that "can prevent policies from being enforced" ([GitHub Changelog, 2026-09-25](https://github.blog/changelog/2026-09-25-enterprise-managed-settings-in-product-validator)). Malformed JSON is loud and an unresolvable mapping is quiet, so chase the warnings first.
- Your policy is one flat file you edit and test by hand. No indirection means nowhere for a silent failure to hide.

The stronger objection is to the design rather than the conditions. A validator turns a silent fail-open into a visible fail-open, and a visible fail-open still serves an unenforced policy until someone opens the page. A loader that refuses to start on an unparseable policy needs no dashboard and no reader, so take that where you own the loader. A vendor serving thousands of clients has the harder trade. Refusing to load an unparseable policy would take an enterprise's assistant offline on one bad commit. GitHub ships the report instead, so the two limits above follow from that choice.

## Example

Claude Code's hook `matcher` field takes "a single string that uses `|` to match multiple tool names" ([Claude Code](https://code.claude.com/docs/en/debug-your-config)). Two spellings of one intent land on opposite sides of the check.

The array value is caught:

```json
"matcher": ["Edit", "Write"]
```

Outside managed settings, Claude Code "shows a settings error notice and rejects the whole user, project, or local settings file, `claude doctor` reports the validation failure, and no hook from that file appears in `/hooks`". Managed settings behave differently: Claude Code "drops the whole `hooks` key from the file that contains the array, so none of that file's hooks apply. The file's other settings still apply, and `claude doctor` lists the dropped key" ([Claude Code](https://code.claude.com/docs/en/debug-your-config)). One defect, two blast radii, and the report tells them apart.

The typo in a tool name is not:

```json
"matcher": "Edt|Write"
```

This is a well-formed string, so it commits clean and shows up in `/hooks`. It also "produces a matcher that matches nothing, so the hook fails silently" ([Claude Code](https://code.claude.com/docs/en/debug-your-config)). Only a check that holds the set of real tool names reaches it. That is Cedar's schema requirement.

## Key Takeaways

- Run two checks and keep them separate. GitHub's own sequence is to validate, then "confirm that your settings are active for users and overridden for specific teams" ([GitHub Docs](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/get-started)). Only the second is evidence about a user.
- Write down when you last saw a positive result, with the commit it covered. When validation is unavailable GitHub tells you to reload and check again later ([GitHub Docs](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/get-started)), and that reload is on you.
- Put your enumerable values in a schema you own, starting with tool names and team slugs. Cedar states the general form, which is that the check reaches only what a schema describes.
- If you write the loader, refuse to start on an unparseable policy and skip all of this.

## Related

- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — decides which layer a rule belongs in; this page covers whether the file carrying it loaded at all
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — the enforcement layer whose config is the most common thing worth validating
- [Agent Config as a Managed Supply Chain](agent-config-as-managed-supply-chain.md) — provenance and rollback for the same files, upstream of the correctness check
- [Frontmatter and Body Rule Drift in Agentic Workflows](frontmatter-body-rule-drift.md) — the half of a config file no validator can check, because prose has no schema
- [Per-Surface Verification of Agent Plugin Packages](../tool-engineering/per-surface-plugin-verification.md) — a different route to the same silence, where a valid policy names a key the client does not implement

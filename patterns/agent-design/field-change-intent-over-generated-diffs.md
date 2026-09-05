---
title: "Field-Change Intent Instead of Model-Written Diffs"
term: "Field-Change Intent"
description: "Have the agent emit which resource, field, and value to change, then let a deterministic span editor apply it, because tolerant patchers misapply about 1 in 7."
aliases:
  - field-change intent schema
  - deterministic span edit
tags:
  - agent-design
  - tool-agnostic
  - automation
  - arxiv
last_reviewed: 2026-09-04
maturity: emerging
---

# Field-Change Intent Instead of Model-Written Diffs

> The agent emits a field-change intent; a deterministic editor finds the target scalar's character span and replaces only that span.

A field-change intent is a structured record of a config edit — resource kind, resource name, field path, new value — carrying no file bytes. The agent picks the field; a deterministic pipeline works out where that field sits and rewrites those characters only. The split takes away the half of the job models are worst at, which is locating bytes.

## When this applies

The evidence covers a narrow box.

- The change is one scalar value: a replica count, an image tag, a resource limit.
- The file is plain YAML or Kustomize, not a Helm or Argo template.
- The pipeline applies the edit with no human between proposal and commit.
- The applier you would otherwise reach for tolerates imperfect context.

Outside that box, [edit format selection](../../tool-engineering/llm-edit-format-selection.md) is the open question.

## Why it works

A generated diff carries two decisions at once: which field to change, and where in the byte stream that field sits. Models are reliable on the first and shaky on the second, and tolerance is what removes the error signal — matching on partial context means a hunk that lands in the wrong region still reports success. [Davineni](https://arxiv.org/abs/2609.00227v1) measured both halves over 83 Kubernetes field-change tasks, 415 runs per system per model. Strict application came out correct on 2.7% of Claude Sonnet-5 diffs, which the paper treats as a lower bound rather than a verdict on diffs. Locate each hunk by content instead of by line number and correctness reaches 67.5% "with zero misapplication". Reach for GNU patch and it applies 96.4%, of which 14.0% "landed at the wrong location or corrupted a neighbor, with no error signal", rising to 20.2% once whitespace is ignored.

Taking the location decision out of the model's output is what makes the edit exact. The pipeline indexes manifests by `(kind, name)`, walks the intent's field path through the parsed node tree, resolves named-list segments by matching the item's `name` child rather than its index, and reads the terminal scalar's `[start, end)` character span from the YAML parser's position marks. It then writes `raw[:start] + requote(new_value) + raw[end:]`. The file is never re-serialized, so minimality falls out of the construction: "Every byte outside `[s,e)` is copied verbatim, so the line-diff against raw touches only the line(s) spanning `[s,e)`" ([Davineni](https://arxiv.org/abs/2609.00227v1)). Comments and blank lines survive, which a re-serializing editor does not guarantee. yq has an open report that in-place write "removes blank lines and changes spacing before comments" ([yq issue 465](https://github.com/mikefarah/yq/issues/465)). The span editor was correct on all 415 runs, with no task flaky across five seeds.

Refusal is the other half. Zero matches, more than one match, or a missing field returns a refusal instead of a guess, measured at 1.00 refusal precision and 0.889 recall over six adversarial categories ([Davineni](https://arxiv.org/abs/2609.00227v1)).

## When this backfires

- Structural edits fall outside the schema, which addresses one terminal scalar. Adding a container, a volume, or a whole block is a stated non-goal of the paper.
- Helm and Argo value indirection is refused rather than fixed, so a repository of templates buys nothing from the pipeline.
- YAML aliases are the paper's own stated gap: an alias resolves to the anchor node and edits the wrong line rather than refusing. The silent misapplication this pattern exists to remove comes back inside the deterministic tool.
- A second config language costs a second locator, with its own span logic and refusal policy.
- Your applier may already fail closed. Anthropic's editor tool errors with "Error: Found 3 matches for replacement text. Please provide more context to make a unique match." instead of guessing ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)). Where byte-level ambiguity already errors, the remaining win is the semantic ambiguity a byte match cannot see, such as a duplicate `(kind, name)` pair.
- The decision itself stays unguarded: "Our guarantees are about faithful _application_, not about the fix being right; that is what human PR review is for" ([Davineni](https://arxiv.org/abs/2609.00227v1)). The reference implementation pins that in CI, and its README says the system "can never merge the PR itself" ([KubeAstra](https://github.com/astraverse-io/KubeAstra)).

Two limits on the evidence. The benchmark is 83 tasks with roughly 80 inside a single file, and the author writes that "Reported rates should be read as edit-site rates within a small file set, not population estimates" ([Davineni](https://arxiv.org/abs/2609.00227v1)). Format restriction also costs something: [Tam et al.](https://arxiv.org/abs/2408.02442v3) report "a significant decline in LLMs reasoning abilities under format restrictions". Watch that in your own evals.

## Example

**Before** — the model writes the patch:

```diff
@@ -12,7 +12,7 @@
   template:
     spec:
       containers:
-        - name: frontend
-          image: gcr.io/boutique/frontend:v0.8.0
+        - name: frontend
+          image: gcr.io/boutique/frontend:v0.9.1
```

**After** — the model writes the intent and the pipeline writes the file. The paper's schema is `FieldChange{kind, name, namespace?, field_path, new_value, reason}`, with a path built from "map keys with named list segments (a container by its name, an env var by its name), never positional indices" ([Davineni](https://arxiv.org/abs/2609.00227v1)). It fixes no string encoding for those segments, so the one below is illustrative:

```json
{
  "kind": "Deployment",
  "name": "frontend",
  "field_path": "spec.template.spec.containers[name=frontend].image",
  "new_value": "gcr.io/boutique/frontend:v0.9.1",
  "reason": "roll forward past the v0.8.0 crashloop"
}
```

Two Deployments named `frontend` in the index produce a refusal listing both candidates, rather than an edit to whichever came first ([Davineni](https://arxiv.org/abs/2609.00227v1)).

## Key Takeaways

- Measure your applier before you trust it: apply rate and correctness rate are different numbers, and only the first one is visible.
- Build the intent schema when scalar config edits run unattended, and not much before that.
- Count the refusal rate on your own templated manifests first, because a refusal is the pipeline working and it still leaves the incident open.
- Keep the review gate. Determinism covers application, never the choice of field or value.

## Related

- [Edit Format Selection: Diff vs. Search-Replace vs. Full Rewrite](../../tool-engineering/llm-edit-format-selection.md) — how to choose when the model does write the edit.
- [Cognitive Reasoning vs Execution: A Two-Layer Agent](cognitive-reasoning-execution-separation.md) — the general form of the decide/act split.
- [Deterministic Guardrails Around Probabilistic Agents](../../verification/deterministic-guardrails.md) — checking agent output rather than replacing the generation step.
- [Deterministic Fast Paths: Answer Without a Model Call](deterministic-fast-paths.md) — the same instinct applied to routing.

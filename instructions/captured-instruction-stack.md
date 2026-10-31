---
title: "Capture the Assembled Request, Not the System Prompt"
term: "Captured Instruction Stack"
description: "In one captured Claude Code request, the system prompt was 13% and tool definitions were 77.4%. Record the assembled request when comparing releases or attributing code to an agent."
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - instruction stack capture
  - assembled request capture
  - captured model request
last_reviewed: 2026-10-28
maturity: emerging
---

# Capture the Assembled Request, Not the System Prompt

> The system prompt was 13% of one captured Claude Code request; tool definitions were 77.4%. Capture the request when comparing releases or attributing code.

A study that intercepted the first model request of 1,886 npm releases published before 25 August 2026 across five coding agents found that in Claude Code's latest capture within that cutoff the 20 tool definitions took 57,346 of 74,078 characters, while "its system prompt takes only 9,517 characters, 13% of the request" ([de Sant'Anna Paixão et al., 2026, arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)). The captured instruction stack is the instruction content assembled for the recorded model request. So record the request the agent sent instead of reading the prompt and inferring the rest.

## When capture is worth the rig

The study measures composition and change. It measures no outcome: the authors write that it "exposes this source of variation without establishing its causal effects on performance or cost" ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)). Two jobs justify the apparatus.

- You compare agent behavior across releases, or write down a configuration someone else must reproduce. "Because this content changes across releases, model identity and the user prompt alone do not fully specify experimental conditions" ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)).
- You attribute commits or code style to an agent. In 492 of 493 Claude Code captures "the Bash description instructs the model to append a Co-Authored-By: Claude trailer to commit messages", and the same agent's comment policy "changed five times", reaching "match its comment density" from release 2.1.154 ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)).

Diagnosing a cost or quality regression is not one of them. For that, pin the version and run a graded slice, which [suspect the harness before the model](../patterns/agent-design/suspect-the-harness-not-the-model.md) covers.

## What reading the system prompt misses

Tool descriptions carry directives, not only schemas. Claude Code's "tool descriptions are 2.6 times as long as its instruction text", and its Workflow tool "has a 19,290-character description, longer than its entire instruction text" ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)). In the latest captured request of three of the five agents, tool definitions were the largest share: 77.4% for Claude Code, 72.3% for Qwen Code and 63.2% for OpenCode. In the other two they were not, at 40.5% for Codex and 18.9% for Gemini CLI.

Reading by message role misattributes authorship. "Message roles do not reliably identify authorship", the authors report. User-role messages hold "60% of Gemini CLI's context facts and 48% of Qwen Code's", so "a study or tool that reads user messages by looking at messages with the user role might credit the agent's text to the user" ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)).

## How to take the capture

The study's runner "installed the exact release, redirected its provider endpoint to a local HTTP server, and submitted the fixed prompt" carrying a marker, then stored the first main-model request body and its hash ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)). Copy two details from it. Classify session-title requests separately, because three of the agents may send the prompt to a helper model first. Then mask five values before comparing captures: the date, the run's temporary directory, the install folder, the host kernel version, and Claude Code's release version.

## Why it works

Capture reads the assembled artifact instead of reconstructing it from the parts that get published, and the published parts are the minority. The agent builds the request at runtime from a top-level instruction field, further messages, and a tool list, so no single readable file holds it. Nor are the tool definitions inert: the Workflow tool's description "limits invocation to explicit user requests for multi-agent orchestration" and shipped even though the test prompt asked for nothing of the kind. The conclusion follows from the arithmetic: "system-prompt analysis alone misses substantial instructional content" ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)). The release history does not close the gap. Across the four open-source agents the study traced, 444 of 496 change units, 90%, state some reason, but only 236, 48%, "give a reason for the stack change itself" ([arXiv:2610.37332v1](https://arxiv.org/abs/2610.37332v1)).

## When this backfires

- You diff unmasked captures. The study's "544 of 1,867 transitions (29%)" that changed a segment or tool is a figure measured after masking, so a raw body-to-body comparison does not produce it.
- You review every release by hand. Seven transitions in ten changed no segment or tool, and "5 to 10 transitions account for half of each agent's cumulative character edits". Diff automatically, read when the diff is non-empty.
- You keep the first request your proxy sees. OpenCode and some Claude Code releases ask a model for a session title, so the marked prompt can appear in a helper-model request.
- You treat the captured stack as your stack. These captures covered "only the first request to the main model in an empty working directory without user interaction", and do "not capture variation from user customization, alternative model choices, or later interactions". Your repository guidance and your later turns are absent.
- Your agent's policy is moving out of the request. A source-code study of eleven harnesses, whose one-quarter diff covered eight of them, found that "behavioral policy migrates from prompt prose to configuration" ([Barbaste et al., 2026](https://arxiv.org/abs/2609.00006v1)). Policy that executes inside the harness need not reach a request at all.

## Key Takeaways

- Tool definitions, not the system prompt, were the bulk of three of the five captured agents' latest requests, led by Claude Code at 77.4%.
- Attribution and comment-style directives changed across releases, and one of them lives inside a tool description rather than the system prompt.
- The published record is not a substitute: 90% of traced change units stated some reason, and 48% explained the stack change itself.
- After masking, 29% of 1,867 transitions changed a segment or tool, so automate the diff and spend human attention only on the non-empty ones.
- The study establishes no effect on cost or correctness, so capture for reproducibility and attribution, not as a regression diagnosis.

## Related

- [Suspect the Harness Before the Model on a Regression](../patterns/agent-design/suspect-the-harness-not-the-model.md) — the triage procedure for a quality shift, which needs a pinned version rather than a captured request
- [Production System Prompt Architecture](production-system-prompt-architecture.md) — close reading of one leaked system prompt, which is the kind of analysis this page bounds
- [Agent Context File Evolution](agent-context-file-evolution.md) — the same maintenance question on the part of the stack you do own
- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](rule-lifecycle-metadata.md) — recording why a rule exists, which you can do for your own rules and not for a vendor's
- [Model-Set Parity: Reading Harness Efficiency Claims](../patterns/agent-design/model-set-parity-harness-claims.md) — the matching problem one layer up, where an unspecified configuration prices the wrong thing

---
title: "Next Edit Suggestions Carry Context You Never Curated"
term: "NES Context Contamination"
description: "A Next Edit Suggestion is built from files you only viewed, edits you undid, and cross-file symbols; the diff at your caret is not the whole of what you accept."
tags:
  - security
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - NES context contamination
  - next edit suggestion security
  - tab-tab-bug
last_reviewed: 2026-09-10
maturity: emerging
status: current
---

# Next Edit Suggestions Carry Context You Never Curated

> A Next Edit Suggestion is built from files you only viewed, edits you undid, and cross-file symbols you never opened.

Next Edit Suggestions (NES) assemble their prompt from six channels, and only one of them is the code under your cursor. The other five are recently viewed code, an edit-history buffer that keeps content erased by undo, structural context from the language server, cross-file symbol lookups, and active diagnostics ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)). The highlighted diff shows you the output. It shows you nothing about the inputs, and on a multi-step transaction it is narrower than the change you are accepting.

## When this is a real risk

Every number below is a conditional failure rate. The authors are explicit: "Because our scenarios deliberately activate each pathway, reported rates are conditional failure rates, not prevalence estimates for ordinary development" ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)). Three conditions decide whether they describe your editor.

- The edit sits in a security-sensitive region: credential handling, query construction, file paths, permission checks. The taxonomy says nothing about the rest of your code.
- You accept multi-line or cross-file suggestions rather than same-line completions. Half the taxonomy covers transactional edits and human-IDE interaction, both of which describe "a sequence of semantically relevant modifications" rather than a single completion ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).
- Nothing downstream re-reads the change. A commit-time secret scan closes the credential class without any of this.

## What sits in the retrieval window

The study ran 410 Java test cases across 9 CWE categories against Zeta, the open-source NES model in Zed, then re-ran 120 sampled cases across Cursor, GitHub Copilot, Zed and Trae. Zeta produced insecure suggestions in 74.44% of security-sensitive contexts; the four commercial IDEs averaged 77.92%. The per-channel rates in Table 2 of that paper are more useful than the headline ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)):

| Context channel | What crosses into the suggestion | Zeta / commercial average |
|---|---|---|
| Cross-file dependencies | Test and debug code retrieved as if it were production code | 100% / 100% |
| Undone edits | A credential typed and immediately deleted still steers the next suggestion | 100% / 90% |
| Structural context | Existing insecure patterns near the cursor, reproduced as intent | 80% / 100% |
| Recently viewed code | Secrets from a file you opened and closed | 70% / 77.5% |

The undo row is the one that changes behavior. Deleting a mistake removes it from the buffer you can see and leaves it in the buffer the model reads. The paper cites a matching production incident: a developer briefly opened a config file holding a secret key, the key was later suggested in plaintext, and "the leak persisted even after the file was explicitly excluded via `.cursorignore`" ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).

## Why it works

The model has no way to tell where a snippet came from. All six channels arrive concatenated into one prompt with no provenance marking and no security filtering, so the model "infers safety not from semantic analysis but from the mere presence of code within the retrieval window", which the authors name a False Safety Assumption that "erases the boundary between trusted internal logic and untrusted external inputs" ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).

The human half compounds the failure rather than causing it. Security thinking has already moved from the act of writing to the act of reviewing: across 15 professional engineers, not one specified security requirements in an initial prompt, even when they held the knowledge ([Bappy et al., 2026](https://arxiv.org/abs/2605.23130v2)). Review is the last defense standing, and NES aims it at a region narrower than the transaction.

## Review the transaction, not the region

Gate the credential class deterministically. Secret scanning at commit is the only control here that does not depend on a human noticing, and it pairs with the injection-time handling in [secrets management for AI agents](secrets-management-for-agents.md).

Keep the secret out of the editor rather than out of the index. An ignore file is "the configuration mechanism intended to prevent specific items from being indexed", and in the reported incident "the recently viewed code context channel created new paths to model inputs that bypassed the indexing exclusion entirely, as confirmed by IDE developers" ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)). Reading a credential in the editor is the act that admits it. Reloading the window clears the assembled context, which is how the study reset state between test cases, so treat it as recovery rather than prevention.

Read the whole transaction before the last tab. Automated navigation moves the change through regions you never inspected: location jumping produced insecure results in 90.00% of Zeta cases, and sequential edits in 69.00% ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).

## When this backfires

- Your stack is not Java. Every measured number comes from Java artifacts, and the authors say manifestations "may differ across languages, ecosystems, and future systems" ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).
- Your answer is an in-IDE AI security check. A study of 17 Microsoft developers found that class of tool "not yet practical for real-world use due to a high rate of false positives and non-applicable fixes" ([Steenhoek et al., 2025](https://arxiv.org/abs/2412.14306v3)), so it swaps one model's judgment for another's.
- The code is not security-sensitive. Applying a conditional rate to UI code, fixtures or generated boilerplate overstates the risk by an unknown factor.
- You respond by narrowing the context window. The expanded context is the feature: NES exists to "suggest multi-line, cross-line, or even cross-file modifications", and the study measures the failure rate of that design without pricing what the narrower alternative costs ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).
- The survey numbers do the arguing. Across 269 retained responses, the 81.1% who report seeing insecure suggestions and the 12.3% who check security are self-reported, and the authors state the survey does not independently validate any individual vector ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).

## Key Takeaways

- Reading a file is an act with consequences. A snippet you only viewed reaches the next suggestion with the same standing as code you wrote ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).
- Undo removes a mistake from your screen and not from the model's context: 100.00% recurrence in Zeta, 90% across four commercial IDEs ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)).
- The headline 74.44% and 77.92% are conditional failure rates from scenarios built to fire, measured in Java ([Lyu et al., 2026](https://arxiv.org/abs/2602.06759v3)). Quote them with that attached or not at all.
- Vendor exclusion controls are scoped to indexing, so an ignore file is not a containment boundary for the viewed-code channel.

## Related

- [Tab-Accept Rate as a Proxy for Critical Engagement](../patterns/anti-patterns/tab-accept-critical-engagement-gap.md) — the measurement side of the same tab loop, and why accept rate alone reads it wrong
- [Context Poisoning: When Hallucinations Become Premises](../patterns/anti-patterns/context-poisoning.md) — the agent-loop version of contaminated context surviving the moment that created it
- [Agent Retrieval Provenance as an Audit Control](agent-retrieval-provenance.md) — marking where retrieved context came from, which is the control NES prompts lack
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — the general form of code gaining authority by appearing in the window
- [Usability Pressure as a Silent Security-Regression Vector](usability-pressure-security-regression.md) — the chat-generation counterpart, where the prompt rather than the retrieval window drops the security constraint

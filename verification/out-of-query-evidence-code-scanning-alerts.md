---
title: "Out-of-Query Evidence for Agent-Fixed Code Scanning Alerts"
term: "Out-of-Query Evidence"
description: "Agentic autofix validates a security fix by re-running the query that raised the alert, so the closed alert is the agent's own stopping condition. Decide by weakness class which alerts need evidence from outside that query."
tags:
  - testing-verification
  - copilot
  - code-review
  - security
  - arxiv
aliases:
  - verifying agentic autofix security fixes
  - second oracle for code scanning alerts
  - alert closure as repair evidence
last_reviewed: 2026-10-16
maturity: emerging
status: current
---

# Out-of-Query Evidence for Agent-Fixed Code Scanning Alerts

> Agentic autofix validates code scanning alerts by re-running the query that raised them, so a closed alert is weaker evidence than it looks.

Take the closed alert as sufficient when all three hold: the alert came from the default code scanning query suite, the diff removes the sink or constrains the source rather than inserting a sanitizer the query already models, and the weakness class is one where agent repair lands. Outside those conditions, accept the fix on evidence the query cannot produce. Treat that as a routing rule rather than a gate on the whole queue, because the second oracle is expensive enough to be worth only where one of the three fails.

## What the gate checks

Copilot "Validates the fix works by rerunning CodeQL" and "Iterates if needed, then opens a draft pull request ready for your review" ([GitHub Changelog, 2026-10-15](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability)). Those two lines describe one loop. The re-run is the condition the agent iterates until it meets, and the draft pull request appears once it has met it.

The documentation states the bound: "Agentic Autofix works on a best-effort basis. Copilot validates fixes by re-running CodeQL with the code scanning query suite. It can't confirm fixes for alerts from custom CodeQL queries, the `security-extended` CodeQL query suite, or code scanning alerts from third-party tools" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/autofix-for-code-scanning)).

Two of GitHub's own listed limitations are invisible to that gate. The system "may suggest fixes that fail to remediate the underlying vulnerability or introduce new vulnerabilities", and it "may suggest fixes that only partially address the security vulnerability or only partially preserve intended code functionality" ([GitHub Docs](https://docs.github.com/en/code-security/responsible-use/security-and-quality-ai-features)). A misleading fix and a real fix produce the same quiet alert. The agent does flag its own doubt, which is the first thing to read on the pull request: "If it can't validate a fix, or thinks the alert might be a false positive, it says so in the pull request" ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)).

## Why it works

A taint query reports a path only while it can follow one, and the query decides what stops the tracking. CodeQL's documentation defines the construct: "Barriers are data flow nodes or edges through which data should not be tracked for the purposes of this analysis" ([CodeQL docs](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/)). Declaring a function a sanitizer means "any flow through this node is blocked. In particular, the query would no longer flag the flow from `process.argv[2]` to `fs.readFile`" (same page).

Re-running the query after a patch therefore answers whether the query can still follow the path, which is a different question from whether the value arriving at the sink is safe. The two coincide only when the barrier is correct for that sink. Removing a sink or constraining a source satisfies the query for the same reason it would satisfy a person; inserting a recognized sanitizer satisfies it by matching a pattern it was written to accept.

P2Patch measures the general form. Repair systems "typically validate a patch against the same evidence used to construct it", and such a patch "can therefore look successful while remaining vulnerable to the same vulnerability with some variation" ([Iranmanesh et al., 2026](https://arxiv.org/abs/2610.20245v1)). Across 101 CVE subjects whose Java half uses "manually checked CodeQL-derived taint findings", an adversarial exploiter "produced a distinct, execution-confirmed bypass of a patch that had already blocked the PoV it was built from" in 41 of 101 runs ([Iranmanesh et al., 2026](https://arxiv.org/abs/2610.20245v1)). The authors call that an upper bound on semantically distinct bypasses, so read it as a direction rather than a defect rate.

The same paper re-scores a repair system that gated the way the GA loop does. LoopRepair "reports a patch on 30 of 40 subjects, each accepted by its own single-crashing-input verification. Under our certified suites only 10 of 39 measurable shared subjects block every fix-closed path" ([Iranmanesh et al., 2026](https://arxiv.org/abs/2610.20245v1)). That "does not contradict their original evaluations; it shows their validation criteria did not measure the same held-out attack-path coverage."

## Which alerts earn a second oracle

Route on weakness class, not severity. Across 319 LLM-generated patches for 64 Java Vul4J vulnerabilities, fix rates split hard by CWE: 0% on 40 CWE-20 input-validation patches against 45% on 40 CWE-835 infinite-loop patches, with XSS at 17%, path traversal at 20%, permissions at 15%, and XXE at 40% ([Al-Maamari, 2026](https://arxiv.org/abs/2603.10072v1)). Only 6 of 21 categories in that study reached the n of 20 needed for the table, and the patches came from single-shot prompting rather than an agent with codebase access, so treat the ordering as the signal and the rates as indicative.

The same study locates the patches a test suite waves through. "Pure security failures (10.3%) pose the greatest deployment risk: these 33 patches pass all functional tests but remain exploitable, meaning they would pass CI/CD pipelines undetected", and the rate reaches 35% on CWE-264 permissions ([Al-Maamari, 2026](https://arxiv.org/abs/2603.10072v1)). Green CI is the wrong reassurance on an access-control alert.

Batching changes the review arithmetic. One assignment "creates one agent session and one pull request for the selected alerts", and the selection runs to 25 ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)). Sort the selection by weakness class so the reviewer judges the same sanitizer decision 25 times instead of 25 unrelated ones.

## When this backfires

- The alert came from a custom query, the `security-extended` suite, or a third-party tool. Copilot "can't confirm fixes" for those ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/autofix-for-code-scanning)), so there is no validation claim to second-guess and the task reverts to reviewing an unvalidated patch.
- No executable path reaches the sink. Writing an attack-input test then costs more than reading the diff.
- The yield is thin across a long backlog. P2Patch's number needed to treat, meaning subjects run per net improved subject, was "7.2 for fix-closed coverage and 4.4 for residual coverage", at a mean $2.09 per subject against $0.45 for single-pass repair, and 3 of 101 subjects regressed on at least one oracle ([Iranmanesh et al., 2026](https://arxiv.org/abs/2610.20245v1)).
- Exploit verification is priced for triage, not coverage. One pipeline spent "roughly 96.3 million tokens and 29 hours" and concluded it "is best deployed selectively within a layered strategy in which static analysis narrows the search space" ([Pourleyli et al., 2026](https://arxiv.org/abs/2609.10762v1)).
- Review capacity is already the binding constraint. An evidence requirement on a 25-alert pull request turns a thin review into a stalled one.

The strongest case against the technique is that the analyzer re-run is the best automated gate anyone has for this input. Ablating a repair agent's approver shows it plainly: "Omitting only tests has a small effect (961 plausible; 9 false accepts), whereas omitting the static analysis check is far more damaging (861 plausible; 123 false accepts)" ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)). Single-pass repair from the finding alone already reached 78.1% held-out fix-closed coverage, which the adversarial loop raised to 84.7% ([Iranmanesh et al., 2026](https://arxiv.org/abs/2610.20245v1)). A team that merges its scanner-validated fixes and spends the saved review on the classes above is making a defensible trade.

It still falls short of proof. Of 654 Python samples clean under a combined Bandit and Semgrep gate, dynamic verification "confirmed or partially confirmed exploitability in 95 files, yielding an inclusive pipeline rate of 14.53% (roughly 1 in 7 statically clean samples)" ([Pourleyli et al., 2026](https://arxiv.org/abs/2609.10762v1)). Those authors read static cleanliness and runtime security as "hierarchical layers of software assurance rather than interchangeable measures".

## Example

A path-traversal alert traces user input to a file read. Three diffs close it, and only one closes it for a reason the query understands independently of its own sanitizer list.

The first deletes the dynamic path and reads a fixed file. The flow is gone, and the re-run reports that.

The second validates the input against an allowlist of permitted names before the read. The flow still exists, but the query loses it at the check. That is the shape CodeQL's worked example uses when `checkPath` becomes a barrier and the query "would no longer flag the flow from `process.argv[2]` to `fs.readFile`" ([CodeQL docs](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/)). Whether the allowlist holds is a property of the allowlist, and the query never looks at it.

The third normalizes the path with a library call the query models as sanitizing. The alert closes, and the question the query did not ask is whether that normalizer is the right one for this sink, in this order, against this input.

Reading the diff for which of the three happened takes about a minute. The third shape, and the second on a subtle sink, are the ones worth a test that sends the attack input through the real path.

## Key Takeaways

- The re-run sits inside the agent's loop rather than after it. "Iterates if needed" means the closed alert is the condition the agent worked toward ([GitHub Changelog, 2026-10-15](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability)).
- Read the diff for what it did to the flow. Removing a sink and inserting a recognized sanitizer both silence the query, and only the second depends on the query's sanitizer list being right for that sink.
- Route by weakness class. Measured fix rates ran from 0% on input validation to 45% on infinite loops, and permissions alerts produced functional-but-insecure patches at 35% against a 10.3% baseline ([Al-Maamari, 2026](https://arxiv.org/abs/2603.10072v1)).
- Custom queries, `security-extended`, and third-party alerts arrive with no validation at all, by GitHub's own statement. Those are a different review, not a harder one.
- Price the second oracle before requiring it. A number needed to treat of 7.2 puts it on selected alerts, not on the queue ([Iranmanesh et al., 2026](https://arxiv.org/abs/2610.20245v1)).

## Related

- [Classification Before Repair in an Analyzer Backlog](classification-before-repair-analyzer-backlog.md) — the same queue shape for code-quality findings, where the agent can suppress and the classification call is the expensive one.
- [Layered Oracle Stack for Agent IaC Security Repair (TerraProbe)](layered-oracle-iac-security-repair.md) — the Terraform case, with a measured deceptive-fix rate and a prescribed five-layer stack.
- [Explained Feedback for LLM Vulnerability Repair](explained-feedback-vulnerability-repair.md) — how much of the scanner diagnostic to hand the agent before it starts patching.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — ordering gates by cost when a target test exists to constrain intent.
- [Protecting the Test Oracle From the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md) — the adjacent failure, where the agent writes to the artifact that defines correctness rather than iterating against it.

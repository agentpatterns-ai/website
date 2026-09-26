---
title: "Name the Check That Passed Before Accepting AI Code"
term: "Named Check"
description: "Across 506 coded accounts of AI use in research code, evaluation confidence tracked trust in the tool (r=.33) rather than the checks actually run (r=.05)."
tags:
  - testing-verification
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - named check gate
  - check-name acceptance record
  - evaluation confidence gap
last_reviewed: 2026-09-21
maturity: emerging
---

# Name the Check That Passed Before Accepting AI Code

> In 506 accounts of AI use in research code, how many checks someone ran was unrelated to their confidence in the evaluation (r=.05).

A named check is the record of which verification ran before someone accepted AI-written code: the test suite that passed, the output compared against a known-answer dataset, the reference implementation that agreed. An acceptance gate reads that record rather than a confidence rating. O'Brien, Milewicz and Eisty coded 506 accounts of a single AI-use episode from researchers who write code. The number of evaluation strategies a respondent described had no relationship to their confidence in that evaluation (r(457)=.05, p=.29) ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)).

## When this applies

The sample is 97.6% United States-based and 93.7% at higher-education institutions, each person recalling one episode ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). These conditions describe scientists writing research code rather than professional software teams.

- Shared verification infrastructure is thin. Running the code was the modal check at 267 of 506 accounts (52.8%). Automated testing appeared in 14 accounts (2.8%) and review by another person in 10 (2.0%) ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). Where nothing downstream re-checks the work, acceptance is the only gate there is.
- The check can be observed rather than typed. The study's "Run code" category absorbed phrases such as "I tested it" where nothing indicated a test suite ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). A free-text box is the same self-report under a new label.
- The work outlives the session. A figure regenerated ten minutes later gets checked by being regenerated. A cleaning step that drops rows and raises no error does not.

## What the confidence number measures

Adding the five commonest evaluation strategies as a block did not improve on a model using programming experience alone (F(5,452)=1.55, p=.17). The strongest correlates of evaluation confidence were confidence in the tool (r=.33, p=1×10⁻¹⁴) and confidence in doing the task without it (r=.30, p=4×10⁻¹²). The two were uncorrelated with each other (r=.02) ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)).

Confidence also moved with the task, in the direction that should worry you. It ran higher on visualization work (b=0.24, p=.010) and lower on debugging (b=-0.30, p=.002), adjusted for experience ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). Visualization is where the check is often a glance at the plot.

One rating, two meanings. The gap between solo and tool confidence widened with programming experience (r=.21, p=9×10⁻⁷, N=512) and crossed zero near 3.7 years ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). Below that mark people trusted the tool more than themselves. Above it, the reverse.

## Why it works

Evaluation confidence is built from trust in the tool, and trust substitutes for verification rather than summarizing it. O'Brien and colleagues read their own r=.33 that way. They cite a survey of 319 knowledge workers. Higher confidence in a generative AI tool went with less critical evaluation of its output ([Lee et al., CHI 2025](https://doi.org/10.1145/3706598.3713778)). The older statement is that reliance tracks felt trust rather than demonstrated capability ([Lee and See, 2004](https://doi.org/10.1518/hfes.46.1.50_30392)).

The decoupling reproduces outside self-report. In a controlled study, participants with access to an AI assistant "wrote significantly less secure code than those without access" and "were more likely to believe they wrote secure code" ([Perry et al., 2023](https://arxiv.org/abs/2211.03622v3)). A confidence rating and a check name measure different things, so one cannot stand in for the other.

The paper's own recommendation names the record: show "whether the code ran, whether outputs were compared against known values, or whether an independent reference was consulted" ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). Three fields, attached to the change.

## When this backfires

- Exploratory output that gets re-derived. O'Brien and colleagues argue some uses "may not have sufficient epistemological weight to justify the overhead of testing in a formal sense" ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). Demanding a check name for a throwaway plot buys paperwork.
- Treating confidence as noise. It is a weak signal rather than a null one. In a 100-participant study, participants producing fewer vulnerabilities than average reported confidence in their code's security 87.2% of the time, against 65.1% for those producing more ([arXiv:2609.21020v1](https://arxiv.org/abs/2609.21020v1)). Hesitation is worth hearing. The 65.1% is why it cannot be the gate.
- Reading the null as settled. The authors call their counts lower bounds, since respondents may have under-reported checks, and name limited statistical power as a candidate explanation ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)).
- Assuming the informal check fails. The same paper cites work reporting eyeball inspection of data objects as a successful check and other work reporting it as a route to overconfidence ([O'Brien et al., 2026](https://arxiv.org/abs/2609.22049v1)). Naming the check tells you which one ran, never how good it was.

## Key Takeaways

- Ask which check passed. The number of checks a person ran did not predict their confidence (r(457)=.05, p=.29).
- Evaluation confidence correlates with trust in the tool (r=.33), so it reports a disposition rather than an event.
- Route the check by task. Confidence ran highest on visualization and lowest on debugging, which inverts where a glance suffices.
- Read a confidence rating against the person's experience. The solo-versus-tool crossover sits near 3.7 years.
- Scope these numbers to scientists writing research code, not to professional software engineering teams.

## Related

- [Verification Ledger for Tracking Agent Output Quality](verification-ledger.md) — the structural form of the same idea, applied to the agent's claims rather than the human's
- [Pre-Completion Checklists for AI Agent Development](pre-completion-checklists.md) — running the check before the handoff instead of recording it afterward
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](evidence-bundled-agent-prs.md) — what a reviewer reads when the evidence arrives with the change
- [Model Confidence as Security Verification (Security Calibration Gap)](../patterns/anti-patterns/model-confidence-as-security-verification.md) — the same decoupling on the model's side of the exchange
- [Stated-Understanding Checks: Asking the Agent to Correct You](../human/stated-understanding-checks.md) — a check that counts only when the agent can look the answer up

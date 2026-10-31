---
title: "Incident-Time Code Grounding for Drifted Runbooks"
term: "Incident-Time Code Grounding"
description: "An on-call workflow for the incident where the runbook has drifted: search code, runbooks and remediation scripts to locate the procedure, then validate the agent's evidence trail rather than its conclusion."
tags:
  - workflows
  - agent-design
  - tool-agnostic
aliases:
  - incident-time code grounding
  - read-time runbook grounding
last_reviewed: 2026-10-22
maturity: emerging
---

# Incident-Time Code Grounding for Drifted Runbooks

> When the runbook has drifted, an agent searches code, runbooks and scripts for the procedure; the engineer validates the evidence rather than the conclusion.

Incident-time code grounding is a read-time workflow. An agent searches the code, the runbooks and the remediation scripts while the incident is open, returns a procedure with resolvable references, and the engineer checks the references before running anything. It replaces guessing which runbook applies and trusting that its commands still exist.

## The stale-runbook problem

The failure is a procedure that no longer matches the system it describes, discovered by someone who is already inside the incident. Drift is real and also not universal. In its top1000 dataset of popular GitHub projects, a documentation study found that "19.2% (1880/9784) of the documents contain at least one outdated reference to a code element, and 28.9% (265/918) of the projects contain at least one outdated document" ([Tan et al., 2022](https://arxiv.org/abs/2212.01479v1)). That study counts code-element references in open-source repository documentation rather than operational runbooks, so it bounds the measurable kind of drift without measuring the on-call kind. The practitioner account reaches further and rests on one person's rotations. A former SRE writes: "Our documentation and scripts were almost always lagging behind code changes." The same post adds that it "wasn't uncommon to figure out nearly half the procedure myself or track down the engineer who wrote it" ([Galindo, 2026](https://sourcegraph.com/blog/sre-runbooks-ai-driven-development)).

## When this applies

Three conditions, and the third is the expensive one.

- The procedure cannot be found or no longer matches the code. At Microsoft, many incident types, especially monitoring-triggered ones, are tagged with relevant troubleshooting articles, so the engineer has the article "the moment they start the RCA" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)). If that article remains current and contains the required procedure, discovery adds no value.
- The agent's output carries references the engineer can open, not a prose summary of what it found. Why it works, below, gives the measured reason.
- Somebody opens them. This workflow relies on validation, and it costs an engineer's attention during an incident.

## The boundary against write-time sync

[Continuous documentation](continuous-documentation.md) runs agents on a schedule or on push to detect drift and open realignment PRs. Use that preventive workflow to reduce drift before the next incident. Incident-time grounding is the read-time complement, reached for inside the incident clock when the write-time loop has not caught up. Neither retires the other. The write-time loop is what keeps the documents worth querying, but an open incident may need investigation before an update lands.

## Three implementation layers

### Layer 1: Discovery

Query across every service repository, runbook and remediation script at once, keyed on the error text from the alert. Finding the document is a reported cost of its own. Microsoft's Azure Fundamental team maintains a large set of troubleshooting articles, and "identifying the right KBA for an incident can take time, and when incidents get more complex, a significant amount (> 1.5 years) of experience is required for RCA" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)).

### Layer 2: Grounding

For each step the procedure names, resolve it against the code: does the script still exist, does the flag still parse, does the service that raised the alert still own the failing path. The runbook stays in the loop here rather than being bypassed, because it carries what the code does not state. The same case study found that troubleshooting articles "contain both specialized domain knowledge and auxillary facts about the agent's environment (e.g. database addresses, API information) that are required both for OCEs and LLM agents to effectively carry out diagnostic steps" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)). Historical incidents do not substitute, because they "typically only contain the outcome of diagnosis steps (commonly in discussion comments) rather than operational knowledge of how these steps must be performed" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)).

### Layer 3: Validation

The engineer checks the evidence trail, then decides. Checking the conclusion instead measures something weaker than it looks. Cloud-OpsBench contains 754 runtime-verified cases over 57 fault types. Across ten LLM agents, "the strongest Joint RCA Accuracy (JRA) reaches 0.76 on OnlineBoutique and 0.68 on TrainTicket, while the corresponding Evidence Closure Rates (ECR) are only 0.38 and 0.15", which the authors read as showing "that final-answer correctness alone substantially overestimates agents' ability to perform evidence-grounded diagnosis" ([Cloud-OpsBench, 2026](https://arxiv.org/abs/2603.00468v2)). ECR measures the fraction of trajectories completing every required evidence milestone. It does not measure what fraction of evidence an individual answer gathered.

## Why it works

A runbook describes a system; current code and telemetry can help check whether that description still applies. Prior LLM approaches to root-cause analysis read the incident report and stopped there, and the authors name that as the binding limit: those approaches "are not able to dynamically collect additional diagnostic information such as incident related logs, metrics or databases, severely restricting their ability to diagnose root causes" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)). Giving the model tools to fetch instead changed factuality more than correctness. A ReAct agent with retrieval tools, evaluated on out-of-distribution production incidents at Microsoft, reached "competitive correctness rates (35% for ReAct S+Q BM25 vs 39% for the baselines), while providing a substantially lower rate of hallucinations (4% for ReAct vs 12% for CoT and 40% for RB (k=10))" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)).

That is why Layer 3 reads references rather than prose. Kim and colleagues traced one pitfall directly to a summary standing in for the artifact. Of their misattributed-evidence category, which the paper puts at 3.4% of runs, they write: "The Controller receives only a natural language summary of the Executor's findings without visibility into the code that produced them." When the executing half deviates from the intended analysis, the reading half then "has no means to detect the discrepancy and accepts the reported findings at face value" ([Kim et al., 2026](https://arxiv.org/abs/2602.09937v2)). A reference an engineer can open restores the detection the summary removed.

## Triggers and constraints

The trigger is an open incident. Nothing here runs on a schedule. The three layers are tool-agnostic: they need a search surface that spans the repositories and the runbooks, a way to call it from the incident, and an output format that carries links. The Microsoft case study wired its agent to the team's own diagnostic services rather than to a product ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)).

The agent reads and proposes; it does not execute remediation. The vendor account keeps the same split, with the engineer as the one who "still validates the findings and makes the decisions" ([Galindo, 2026](https://sourcegraph.com/blog/sre-runbooks-ai-driven-development)), and the measurements make that split load-bearing rather than polite. Across 1,675 runs on the full OpenRCA benchmark, hallucinated interpretation appeared "in 71.2% of executions", and "all five models exhibit Hallucination in Interpretation above 66% and Incomplete Exploration above 53%" ([Kim et al., 2026](https://arxiv.org/abs/2602.09937v2)).

Waiting for a better model is not a plan. Those pitfalls "persist across all models regardless of capability tier", which the authors attribute to the shared agent framework rather than to any one model, and they found that prompting did not close the interpretation pitfall: fixing interpretation "requires architectural intervention, such as external verification modules, rather than further prompt refinement" ([Kim et al., 2026](https://arxiv.org/abs/2602.09937v2)).

Budget the supervision against the clock you actually have. The error budget for a service at four nines is 52 minutes and 34 seconds a year ([Galindo, 2026](https://sourcegraph.com/blog/sre-runbooks-ai-driven-development)). That figure is arithmetic rather than a measured result, and it cuts both ways: reconstructing a procedure by hand is charged to it, and so is supervising a search that goes nowhere.

## When this backfires

- The facts are split across several documents. On complex incidents where sample queries and cluster addresses lived in different articles, the agent "was only ever able to successfully execute one or two diagnostic steps before reaching the iteration limit (20)" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)). The hard incidents are where this degrades, and they are the ones a stale runbook hurts most.
- The alert carries a current, complete runbook. Discovery then inserts a step ahead of a procedure the engineer already has.
- Nobody opens the references. The workflow then adds no human verification, and the agent's answer stands alone. For scale, the baseline OpenRCA agents show "overall perfect accuracy ranging from 3.9% to 12.5% across five models spanning different capability tiers" ([Kim et al., 2026](https://arxiv.org/abs/2602.09937v2)).
- The cause is not in the code. The same SRE recalls a call with eight or more engineers that ended "only to discover that the problem originated at the hardware layer rather than the software" ([Galindo, 2026](https://sourcegraph.com/blog/sre-runbooks-ai-driven-development)). No repository holds that answer.
- More prose is the proposed fix. Adding the discussion threads from historical incident reports to the agent's inputs "does not have a significant impact on the agent's performance" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)).

## Example

Roy and colleagues illustrate human validation on a real monitoring-raised incident at Microsoft: a cluster setting had drifted out of sync with the central orchestrating server. The alert carried no description, but it included an intact troubleshooting article. The agent used that article directly, bypassing document retrieval. If no tenants occupied the affected cluster it was a false positive; if tenants did, the engineer had to identify the clusters and start a job to correct the drift. Answering that required a database query whose address and sample syntax lived only in the runbook ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)).

The agent handled the first branch end to end. The authors describe the run as using the planning tool to gather the troubleshooting steps, then going on to "adapt and execute the sample query from the KBA, and correctly assess the resulting table", and record that one engineer was "amazed by the tool's capability to automatically discern the right parameters and even rectify mistakes when the parameters are initially incorrect by querying the documents". The second branch needed an extra filtering step over the returned table, and there "the agent is unable to resolve this error consistently, but engineers were able to use the human-in-the-loop features of the prototype to intervene and fix the error" ([Roy et al., 2024](https://arxiv.org/abs/2403.04123v1)). The second branch shows human-in-the-loop intervention to fix an agent error. This case did not test cross-repository code search or grounding a drifted runbook. The proposed first two layers follow Galindo's practitioner account, not this experiment.

## Key Takeaways

- Start at the runbook the alert already carries. Reach for search when it is missing, or when a step in it no longer resolves against the code.
- Keep writing runbooks, and keep the environment facts in them. In the published case study the agent "struggles to make progress when key information is missing in the KBAs (such as missing cluster address for DB queries)".
- Ask the agent for the artifacts it read, with links, and open them. Measured outcome accuracy of 0.76 sat against evidence closure of 0.38, so agreeing with a conclusion is not checking it.
- Budget review explicitly; the cited model comparison does not justify removing it. Prompt-level fixes did not move the dominant pitfall; the paper's authors point at verification modules instead.

## Related

- [Runbooks as Agent Instructions: Agent-Followable Ops](runbooks-as-agent-instructions.md) — the write-time half of the same artifact, rewriting procedures so an agent can execute them
- [Continuous Documentation as an Agent-Driven Practice](continuous-documentation.md) — the scheduled drift-detection loop this workflow complements
- [Incident Log Investigation Skill: Parallel Queries](incident-log-investigation-skill.md) — the telemetry layer of the same incident, where this page covers the code and procedure layer
- [Evidence-First Reports From Failure-Diagnosis Agents](../patterns/agent-design/evidence-first-diagnosis-reports.md) — how to shape the report once the evidence is gathered
- [Self-Healing Production Agent](../patterns/agent-design/self-healing-production-agent.md) — the automated-remediation path that runs before a human is paged

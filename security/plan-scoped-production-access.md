---
title: "Plan-Scoped Credentials for Agent Production Access"
term: "Plan-Scoped Authorization"
description: "An approved plan is the unit a credential is issued against, and the runtime checks the plan is active before selecting it. The plan's prose is not the token's bound."
aliases:
  - plan-scoped authorization
  - plan as the authorization unit
  - approved-plan credential selection
tags:
  - security
  - agent-design
  - tool-agnostic
last_reviewed: 2026-10-26
maturity: emerging
---

# Plan-Scoped Credentials for Agent Production Access

> An approved plan carries the agent's elevated scopes, and the runtime re-checks that plan is active before it selects a credential.

Plan-scoped authorization makes the approved plan the unit a credential is issued against. The agent investigates under a read-only grant, then proposes a plan naming the work and the scopes it needs. Vercel ships it in Vercel Agent, which "runs as a Vercel App" the user authorizes to act on their behalf within a team. Approving a plan "grants the additional permissions to carry it out, so the user can review the proposed fix before authorizing any changes" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)).

## The two conditions it depends on

A plan's prose is not the token's bound, and Vercel says so against itself. "Deployment write access is broader than a single redeploy. Naming deployment X in a plan does not, by itself, restrict the token to that deployment" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)). Approve "Redeploy the last known-good build" and you have granted deployment write wherever that token reaches. A resource dimension can narrow that grant further. Vercel's GitHub leg does: pull-request access "is tied to an owner and repository", so approval for `acme/storefront` leaves `acme/payments` alone.

The second condition is a ceiling above the approval. The agent's authorization is limited by the user's existing permissions, "so approving a plan cannot grant access the user does not have" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)). Without it, approving a plan is a way to acquire access rather than review it.

## How the boundary is drawn

Reads use the pre-authorized baseline without a new plan approval. "The read-only baseline currently includes every registered scope beginning with `read:`" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)). Everything above it waits as a unit, so a plan "requesting access beyond the read-only baseline waits for approval as a whole, including any read-only tasks it contains".

Approval issues a credential. "The Vercel OAuth service exchanges that authorization for shorter-lived tokens with specific scopes" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)). The check then lands at the API, which rejects an out-of-scope request "even if the model considers the action necessary to complete the task".

One vocabulary defines both halves, because the earlier separate list could fall out of sync: "We initially maintained a separate permission list for Vercel Agent, which could fall out of sync with the OAuth service that issues its tokens. We moved to the same scope definitions so those mismatches could be caught during planning." An unrecognized scope name now fails validation, and the system "requires an explicit correction instead of a fallback to broader access" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)).

## Why it works

Two decision points move off the model. Elevation moves from the action to the plan, so a reviewer sees described work with its scopes attached before any write exists. The use-time decision moves onto the plan record: "Before resuming, the runtime reloads the plan and checks that it is active before selecting a credential with its approved permissions. A stopped plan fails that check, even if its token has time remaining before expiry" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)). That check blocks credential selection on resume even before token expiry. It does not establish cancellation of an already-running request. The record carries "its state, who approved it, and when, alongside its tasks and requested permissions."

Reviewing composed work rather than isolated steps has support outside the vendor. Zhu et al. describe skill cascading attacks as "a threat paradigm in which a malicious objective is distributed across multiple skills so that each modification looks benign in isolation, yet their combined execution is harmful" ([arXiv:2609.30383v2](https://arxiv.org/abs/2609.30383v2)). Their subject is skills an agent loads, not approval plans, so it is evidence about the review unit and not about this implementation.

## When this backfires

| Condition | What it costs |
|---|---|
| Scopes carry no resource dimension | The approval and the grant describe different things, and the plan itself has to close the gap: it "needs to explain the intended change and make clear which limits the token actually enforces" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)) |
| The unapproved baseline is wide | Every `read:` scope runs with no decision, and "Read-only operations can still expose sensitive information, so automatic approval does not mean the work is harmless" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)) |
| The scope catalog is cached | A stored plan is checked against a cached copy: "Those checks reflect the cached definitions until the catalog is refreshed with changes from the registry" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)) |
| The agent sizes its own request | It "chooses scopes with incomplete information, so it can request too little access and leave a task blocked, or too much and grant more authority than the work needs" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)) |
| Denials are read as missing scopes | A denial "could indicate a missing scope, an incorrect resource, or an operation that should remain blocked" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)) |
| Approval volume was the actual problem | "Repeated prompts can turn that review into a habit of clicking approve" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)), and Anthropic reports that Claude Code users "accept 93%" of manual permission prompts ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)) |

The credential bounds operations. It does not bound consequences, and Vercel says so of both a wrong decision and malicious instructions in content such as build logs: "Scoped credentials limit which operations it can perform in either case, but permitted operations can still cause harm" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)). Vercel pairs plans with sandbox isolation, network policy, secret handling, rate limits, audit logs and service authorization. It also declines to present its own read-only floor as the right one: "Other systems may need a narrower baseline" ([Vercel](https://vercel.com/blog/how-vercel-agent-accesses-production-safely)).

## Key Takeaways

- Re-check the authorization record when selecting credentials, in addition to checking token validity. A stopped plan should fail while its token is still valid.
- Keep one permission vocabulary between whatever proposes access and whatever issues it. Vercel's earlier split list could fall out of sync, and the fix was a shared definition checked during planning.
- Size the unapproved baseline by what a read exposes, not by the word `read:`.
- State in the approval whether the scope is bound to the named resource. Where it is not, the plan's wording implies a limit the token does not enforce.

## Related

- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](revocable-resource-effect-capabilities.md) — the research analogue of the use-time check, with epoch-bound handles withdrawn at subgoal closure
- [Task-Based Access Control with Hybrid Inspection](task-based-access-control-hybrid-inspection.md) — binds each tool call to the user's current task instead of to one approved plan
- [Authority-Set Binding: Who Names an Approval's File Set](authority-set-binding-approvals.md) — the same review-versus-grant gap, measured over the files an approved run reads
- [Single-Decision Approval of Vendor Skill Suites](single-decision-suite-approval.md) — what one approval decision over a bundle costs when the harm lives in the composition
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the least-privilege floor an unapproved baseline is sized against

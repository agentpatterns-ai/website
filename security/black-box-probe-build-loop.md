---
title: "Black-Box Probing in the Agent Build Loop: When It Pays"
term: "Black-Box Probing in the Build Loop"
description: "An outside-in probe of a running agent-built app finds controls that are absent, and never shows that the controls already present are correct."
tags:
  - security
  - tool-agnostic
aliases:
  - outside-in security probe
  - black-box scan in the build loop
  - automated pen test gate
last_reviewed: 2026-08-18
maturity: adopted
---

# Black-Box Probing in the Agent Build Loop: When It Pays

> Attacking the running app inside the build loop finds controls that are absent; it cannot show that the controls present work.

Black-box probing runs an automated attacker against the deployed application from outside, with no access to the source. Replit ships it as a scan that reaches the app "over the network, through a browser, with no access to your app's source materials" [Source: [Replit — Black-box pen tests](https://replit.com/blog/black-box-pen-tests)]. The probe observes a different artifact from the one a reviewer reads. A diff contains code. The running deployment contains code composed with configuration, routing, authentication wiring, and whatever the platform provisioned by default.

## When this earns its place

The probe pays for itself under three conditions. Drop any one and it becomes cost without coverage.

- The target is an ephemeral full copy. Replit runs each scan "against a full copy of your app running in a private sandbox, so nothing it tries can escape or reach your users" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)]. Without an isolated clone you either skip the destructive checks or accept the risk to a shared environment.
- The crawl authenticates. Replit's scanner "runs once with no account, checking what any visitor can reach. Then, it tries again as an ordinary authenticated user" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)]. A crawl that stops at the login wall reports clean on a surface it never reached.
- The defect you want is an absent control rather than a wrong one. OWASP states that "SAST and DAST tools can detect the absence of access control but cannot verify if it is functional when it is present" [Source: [OWASP Top 10 A5, Broken Access Control](https://github.com/OWASP/www-project-top-ten/blob/master/2017/A5_2017-Broken_Access_Control.md)].

## Why it works

The gain is coverage from a second observation point, not sharper detection. The probe evaluates the deployed composition and the reviewer evaluates the source, so the two produce largely disjoint sets. Replit reports that "security findings between both scans rarely overlap" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)]. That vendor claim has an independent counterpart: in an empirical case study applying static analysis, dynamic scanning, and two styles of manual penetration testing to one Java application, "with each technique, we found unique vulnerabilities not found using the other techniques" [Source: [Elder et al., arXiv:2208.01595v1](https://arxiv.org/abs/2208.01595v1)].

The same study bounds the size of the gain. Two dynamic scanners between them covered 7 of the OWASP Top Ten, and static analysis still yielded the most vulnerabilities overall [Source: [Elder et al., arXiv:2208.01595v1](https://arxiv.org/abs/2208.01595v1)].

## When this backfires

- You retire authorization review on the strength of a green scan. OWASP states that "access control detection is not typically amenable to automated static or dynamic testing" and names manual testing as the best way to find ineffective access control [Source: [OWASP Top 10 A5](https://github.com/OWASP/www-project-top-ten/blob/master/2017/A5_2017-Broken_Access_Control.md)]. Broken object-level authorization is the class an outside-in probe is weakest on, not the headline to sell it on.
- You read a clean result as evidence of safety. Coverage comes from the crawl: Replit's scanner "first clicks through the app while watching every request it sends, which reveals the features your app really has, including the ones with no button" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)]. A route the crawl never reached and a route that is secure produce the same output.
- The fix loop runs without a behavioral oracle. Handing findings to an agent to close, as Replit does when "you receive a short list of confirmed problems that you can review and fix with the Replit Agent" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)], makes the finding the thing being optimized away. An agent can rate-limit the single probed route and leave the model that produced the hole intact. Stack a [layered oracle](../verification/layered-oracle-iac-security-repair.md) behind the scanner verdict when an agent writes the fix.
- Your static coverage is thin and you fund this instead. A CodeQL analysis of 7,703 files attributed to AI tools reported 4,241 CWE instances across 77 distinct vulnerability types, all reachable without deploying anything [Source: [Schreiber and Tippe, arXiv:2510.26103v1](https://arxiv.org/abs/2510.26103v1)].

## Example

Replit's post reports two demo applications and one clean split between the layers. The black-box scanner found "the admin dashboard sitting at a guessable address with no login on it", which the white-box scan had "moved on" from "because nothing about the code was wrong". In a multiplayer game, "only the black-box scanner found that you could flood an endpoint to crash everyone's ongoing match" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)].

The reverse case bounds the claim. The white-box scan caught "that a user whose access had been revoked could keep operating, because the app never rechecked whether their old sign-in was still valid" [Source: [Replit](https://replit.com/blog/black-box-pen-tests)]. That is a control that exists and is wrong, which is what OWASP says the outside-in probe cannot establish.

## Key Takeaways

- Budget the probe as a second observation point on the deployed composition, and keep the reviewer who reads the source.
- Gate the spend on an ephemeral clone and an authenticated crawl. Without both, the scan measures the crawler rather than the app.
- Treat absence findings as the deliverable and authorization correctness as out of scope, following OWASP's own scoping of dynamic testing.
- Put a behavioral check behind any agent-written fix, because the finding is what the agent optimizes against.

## Related

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the diff-time and scheduled-scan half of the same coverage problem
- [Layered Oracle Stack for Agent IaC Security Repair (TerraProbe)](../verification/layered-oracle-iac-security-repair.md) — stacked oracles so an agent's security fix has to clear behavior, not just clear the finding
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md) — feeding attack traces into hardening the agent, one layer below testing what the agent shipped
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — bounding what a shipped defect can reach
- [Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools](scanner-as-mcp-server.md) — the same findings-to-agent handoff, wired as a typed tool

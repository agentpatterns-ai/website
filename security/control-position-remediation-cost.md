---
title: "Reading Customer Actions in Security Disclosure Reports"
term: "Disclosure Absorption"
description: "Compare vendor protections with required customer actions. Replit's disclosure reports distinguish blocked exploitation, automatic updates, and changes that need republishing."
aliases:
  - control position on the execution path
  - platform disclosure absorption
  - shared responsibility for agent runtime patching
tags:
  - security
  - agent-design
  - tool-agnostic
last_reviewed: 2026-11-02
maturity: emerging
---

# Reading Customer Actions in Security Disclosure Reports

> Security disclosure reports show which protections already apply and which fixes still require customer action.

Read a platform's isolation architecture against your required actions only where the vendor publishes a per-disclosure action list. The statement that a platform runs agents in microVMs says nothing about your work. A list pairing each flaw with your required action makes it checkable, and Replit published one for five October 2026 disclosures ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)).

A control absorbs a flaw when the vulnerable code never receives reachable attacker input, and the customer does nothing. This page calls that outcome disclosure absorption. A control narrows a flaw when it covers one route in and leaves the rest. A third case sits between them: a fix beneath the application that must still be delivered, which can leave you a republish. Replit states the division itself: protections went in "at the firewall level to prevent malicious exploit attempts from reaching your apps, but some fixes require you to take further action to update and republish your apps".

## What one disclosure wave cost at each position

| Disclosure | Control, and where it sat | Customer action |
|---|---|---|
| Linux kernel | A per-environment microVM with a hardened kernel configuration | None |
| LiteLLM supply-chain attack | A package install firewall, ahead of install | None |
| eMudhra certificate authority compromise | A base-image change, beneath the application, plus a Python tooling patch | Republish Python apps, or follow emailed instructions |
| Node.js | A web application firewall, beside the inbound request route | Republish Node.js apps |
| PHP | A web application firewall, beside the inbound request route | Republish, recommended |

The two zero-action rows sit at different positions. Replit's "existing microVM architecture prevented exploitation of all these vulnerabilities, by construction", and its package firewall "blocked all malicious package install attempts" ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)). Beneath and ahead both work. Neither retires the patch: the same kernel entry commits to "upgrade to the latest version that has all the fixes once it's available".

A fix beneath the application still had to be delivered. Replit "removed the compromised CA from our base images and automatically applied the fix to 95% of published apps". The action line is "Republish Python apps to include the tooling update", which ties the republish to a separate patch of Replit's Python tooling. Apps that require "a manual update rather than an automatic fix" get an email with instructions from Replit ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)).

The two web-firewall rows are the instructive pair. The firewall protection was in place; the work remained. Republishing a Node.js app "also addresses attack paths outside the incoming requests covered by the firewall, including responses your app receives from other services" ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)). The firewall covers incoming requests. Replit says patched Node.js also addresses attack paths through responses from other services.

## Why it works

Replit credits its "existing microVM architecture with a hardened kernel configuration" for the kernel outcome, and describes microVMs as giving "each execution environment its own minimal kernel, strengthening isolation between workloads" ([Replit, 2026-10-28](https://replit.com/blog/architecture-behind-secure-agent-work)). The post names both factors, and this page cannot say how much each contributed. The Socket Firewall acts ahead of install: it "blocked all malicious package install attempts" ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)). The Node.js example shows a control covering incoming requests while other attack paths still need a patched runtime.

Timing matters too. Replit attributes the kernel outcome to prior architecture: "The protection came from an architectural decision made before the disclosures."

The split is contractual, which is what makes any of it readable from outside. Replit states where its ownership ends: "we are responsible for securing the harness, the runtime, and the operating system" ([Replit, 2026-10-28](https://replit.com/blog/architecture-behind-secure-agent-work)). Ask for that sentence before you ask for the architecture, because it tells you which rows can ever come back as None.

## What the Replit post says about boundaries and operating cost

Replit's architecture post ([Replit, 2026-10-28](https://replit.com/blog/architecture-behind-secure-agent-work)) names few controls. This table records, for each boundary or cost question, what the post states and where this site covers the rest. Where the post is silent, the row says so.

| Question | What the Replit post states | Where to read more |
|---|---|---|
| Which control sits on which boundary | Agents run in isolated cloud environments. "MicroVMs give each execution environment its own minimal kernel". "development and production databases are kept separate". "Connector permissions provide another boundary for external systems." The post names no filesystem or process-level control inside the microVM. | [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md), [Session Harness Sandbox Separation](../patterns/agent-design/session-harness-sandbox-separation.md) |
| What a container does not stop | The post does not discuss containers. It credits its microVM architecture with a hardened kernel configuration for the kernel outcome, and the Firecracker advisory below shows the microVM layer can itself be flawed. | [Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md), [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) (shared-kernel escapes) |
| Egress filtering, proxy versus kernel enforcement | The post does not state an agent egress allowlist. It names a web application firewall for inbound exploits and, for Replit's internal use, "a Zero Trust network". It lists "unexpected file access or network connections" as something planned monitoring should "detect and respond to". | [Agent Network Egress Policy](agent-network-egress-policy.md), [Selective Network Access in Agent Sandboxes](selective-network-sandbox-mode.md), [Hostname Allowlist TLS Blind Spot](hostname-allowlist-tls-blind-spot.md) |
| Credentials an agent run holds | "Replit keeps connector credentials outside the agent's context." "A credential broker authorizes every single request, and only retrieves the credentials from a vault and adds them to outgoing requests after that request is authorized." "The agent runs outside the isolated sandbox where code executes, keeping the two environments separate." | [Scoped Credentials via Proxy](scoped-credentials-proxy.md), [Sandbox Credential Masking](sandbox-credential-masking.md), [Renting a Cloud Agent's Execution Sandbox](../patterns/agent-design/rented-execution-sandbox.md) |
| Latency, cold starts, controls dropped under pressure | The post gives no sandbox startup or runtime latency figure and does not say which controls teams drop first. Its cost statement about the sandbox is remediation work: "Newly disclosed flaws in dependencies and runtimes can create urgent remediation work even when an application's own code has not changed." | [Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md) (startup latency), [Scoped Credentials via Proxy](scoped-credentials-proxy.md) (proxy hop), [Selective Network Access in Agent Sandboxes](selective-network-sandbox-mode.md) and [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) (approval pressure) |

Read the middle column as the extent of the vendor's claim. A control the post does not name is not evidence that Replit lacks it.

## When this backfires

- The flaw lands in the boundary component. A root-privileged guest in Firecracker 1.13.0 through 1.14.3 and 1.15.0 "can modify the `queue_size` register, which was already validated during initialization", permitting "Out-of-bounds writes up to 524,284 bytes beyond the virtio queues" ([GHSA-776c-mpj7-jm3r](https://github.com/firecracker-microvm/firecracker/security/advisories/GHSA-776c-mpj7-jm3r)). Reaching host memory needs more: "additional preconditions must be satisfied that require a higher level of control over the guest environment, such as the use of a custom guest kernel or specific snapshot configurations".
- The workaround charges you. Reverting to the unaffected transport "may result in reduced I/O throughput and increased latency" ([GHSA-776c-mpj7-jm3r](https://github.com/firecracker-microvm/firecracker/security/advisories/GHSA-776c-mpj7-jm3r)).
- You cannot verify an absorption claim from outside. Replit asserts the kernel outcome about its own architecture and names the limit: "Isolation alone cannot prevent every vulnerability and protection must continue after software ships" ([Replit, 2026-10-28](https://replit.com/blog/architecture-behind-secure-agent-work)). Treat this reading as a planning input, not a reason to slow your patch cadence.
- The deployment mode moves the line with no disclosure involved. AWS Bedrock AgentCore will "Automatically patch underlying compute OS kernel with latest version" for a container image, while the same row assigns you "Regularly re-build and re-deploy your container image using the latest base image" ([AWS Bedrock AgentCore docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy.html)). For direct-deploy runtimes the same docs say "only language runtime patches will be automatically applied and customers are responsible to bring and managed their code dependencies".
- You host the agent yourself. Nothing sits on a vendor's side, so every row is yours.

## Example

For the Linux kernel, the control sat beneath the vulnerable code:

```text
How Replit has taken action: Replit's existing microVM architecture
prevented exploitation of all these vulnerabilities, by construction. [...]
What you need to do: No action is required for these specific vulnerabilities.
```

For Node.js, the control sat beside one route into it:

```text
How Replit has taken action: We deployed web application firewall (WAF)
protections against exploitation through incoming web requests and made
patched Node.js versions available.
What you need to do: Republish your Node.js apps to use the patched runtime.
This also addresses attack paths outside the incoming requests covered by
the firewall, including responses your app receives from other services. [...]
```

Both report a control in place ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)). Only one ends your involvement.

## Key Takeaways

- Ask a platform for its per-disclosure action list, not its architecture summary; the action list is the only form of the claim you can check.
- Keep a republish path ready for each runtime. Controls beside one route and fixes beneath application code can both leave deployment work.
- Of five October 2026 disclosures on one platform, two needed no customer action, two needed a republish, and for one Replit recommended a republish ([Replit, 2026-10-22](https://replit.com/blog/security-vulnerabilities-across-the-internet)).
- Replit emails manual-update instructions for apps outside the automatic fix. Budget for those apps as well.
- Replit's architecture post states credential brokering and microVM isolation, but no egress allowlist, sandbox latency figure, or list of controls teams drop first. Use the linked sibling pages for those.
- Check when each protection took effect. Replit attributes its kernel outcome to architecture that preceded these disclosures.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the adjacent axis, sorting controls by where they are evaluated rather than where they sit on the execution route
- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md) — choosing the runtime layer that decides which flaws land beneath your code, and what each costs
- [Reading an Exploit Roundup Against a Defense Catalog](reading-exploit-roundups-against-defense-catalog.md) — the companion read, using published attack instances to promote defenses from argued to observed
- [Capability-Pegged Security Re-Scans](capability-pegged-security-rescan.md) — the other trigger for reviewing unchanged code, pegged to scanner capability instead of a disclosure
- [Renting a Cloud Agent's Execution Sandbox](../patterns/agent-design/rented-execution-sandbox.md) — what the split looks like once you supply the execution environment and inherit its patch clock
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md) — the filesystem and network boundaries that the Replit post leaves unspecified
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — the credential broker pattern Replit describes, with its latency cost
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — egress filtering, which the Replit post does not state

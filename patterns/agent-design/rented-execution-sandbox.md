---
title: "Renting a Cloud Agent's Execution Sandbox"
term: "Rented Execution Sandbox"
description: "Pointing a cloud agent at a third-party sandbox moves tool execution only, so decide it on a named requirement and expect inference and tool output to stay with the vendor."
tags:
  - agent-design
  - cursor
aliases:
  - third-party agent execution sandbox
  - self-hosted machines for cloud agents
  - rented agent execution environment
last_reviewed: 2026-09-04
maturity: emerging
---

# Renting a Cloud Agent's Execution Sandbox

> Renting a sandbox for a cloud agent moves tool execution only. The agent loop and inference stay with the vendor, and tool output flows back.

Cursor's Self-Hosted Machines APIs "let you supply the execution environment where agents clone repositories, edit files, and run commands and tests," while "Cursor manages the agent harness and inference loop" ([Vercel changelog, 3 Sep 2026](https://vercel.com/changelog/run-cursor-cloud-agents-vercel-sandbox)). Vercel Sandbox is one of eight named backends, alongside AWS Lambda, Cloudflare, Coder, Daytona, E2B, Modal, and Namespace ([Cursor, 2026-09-02](https://cursor.com/blog/self-hosted-machines)). It requires a Cursor Enterprise plan ([Cursor docs](https://cursor.com/docs/cloud-agent/self-hosted)).

## When the move pays

Cursor keeps its own hosted machines as the default and argues they are enough for most buyers: "Per-agent isolation, secret redaction, egress controls, and signed commits meet the security requirements of most teams" ([Cursor, 2026-09-02](https://cursor.com/blog/self-hosted-machines)). Move only on a requirement that fails inside that default. Cursor lists three: tool execution has to happen inside your network, with direct access to internal services and source control; the agent requires custom hardware such as GPUs or Macs for iOS development, or infrastructure such as Kubernetes; or the operating system or build pipeline is "difficult to package as a Cloud Agent build" ([Cursor](https://cursor.com/blog/self-hosted-machines)).

Test the third one against a cheaper fix first. Cursor rebuilds the environment hourly inside its own sandbox and reports time to first token 3x faster with builds ([Cursor, 2026-08-13](https://cursor.com/blog/builds)), the pattern documented in [Continuously Built Agent Environments](continuously-built-agent-environments.md). A build often settles a toolchain complaint without adding a second vendor. Once a requirement does survive that test, the choice of which sandbox to supply is its own decision, covered in [Workload-Keyed Sandbox Selection](../../security/workload-keyed-sandbox-selection.md).

## What you inherit

Vercel's reference implementation is an app you deploy and then keep. Functions and Workflow "form a durable control plane that claims queued agent requests, provisions workers, monitors sessions, and cleans up automatically" ([Vercel changelog](https://vercel.com/changelog/run-cursor-cloud-agents-vercel-sandbox)). Under it sits a discovery loop with adaptive polling, an atomic claim per request, a child workflow per worker, and standing maintenance: "Rebuild snapshots periodically to keep the Cursor Agent CLI and system packages current" ([Vercel](https://vercel.com/kb/guide/cursor-vercel-sandbox)).

You inherit a credential clock with it. The service account key stays in the control plane and "is never copied into an agent's microVM"; each worker gets a minted one-hour token. Those tokens "expire after one hour and cannot refresh themselves, so longer sessions require a secure refresh path or a different scoped credential strategy" ([Vercel](https://vercel.com/kb/guide/cursor-vercel-sandbox)).

The gains are real and narrow. You choose the image, and Vercel Sandbox "supports egress allowlists and credential brokering at the microVM firewall" ([Vercel](https://vercel.com/kb/guide/cursor-vercel-sandbox)), so [network egress policy](../../security/agent-network-egress-policy.md) becomes yours to write. You also inherit that provider's quota sheet: a session runs 45 minutes on Hobby and 24 hours on Pro and Enterprise, an Enterprise sandbox tops out at 32 vCPU and 64 GB, and sandboxes run only in the `iad1`, `sfo1`, `cle1`, and `cdg1` regions ([Vercel Sandbox pricing and quotas](https://vercel.com/docs/sandbox/pricing)).

## Why it works

The halves come apart because the interface between them is a tool call and its result, and the agent loop needs nothing else from the machine. That is the general form documented in [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md), and Cursor draws the line in the same place: "only the execution environment moves while the agent loop, inference, and planning remain in the Cursor cloud" ([Cursor, 2026-09-02](https://cursor.com/blog/self-hosted-machines)). The connection runs one way. The worker opens a long-lived outbound HTTPS connection, so "No inbound ports, public IPs, or VPN tunnels are required" ([Cursor docs](https://cursor.com/docs/cloud-agent/self-hosted)). Any machine that can dial out and answer tool calls qualifies, so replacing it changes the image, the network reach, and the bill without touching the agent.

## When this backfires

- Residency was the reason. The split does not deliver it. "Tool outputs flow back to Cursor for inference and may contain code, and agent transcripts may be processed and stored by Cursor" ([Cursor, 2026-09-02](https://cursor.com/blog/self-hosted-machines)). A team relocating execution to close an audit finding about code leaving the network has not closed it.
- Your rule names a region the provider lacks. Vercel Sandbox runs in four, a short list to hold a residency requirement against ([Vercel Sandbox pricing and quotas](https://vercel.com/docs/sandbox/pricing)).
- Conversational work on a scale-to-zero pool. Release the machine and "the agent may need several minutes to reconstruct its workspace when a follow-up arrives" ([Cursor, 2026-09-02](https://cursor.com/blog/self-hosted-machines)). Cursor's hibernation trades that delay for snapshot storage, billed at $0.08/GB-month ([Vercel](https://vercel.com/docs/sandbox/pricing)).
- Sessions past the token lifetime. Anything over an hour needs a refresh path the implementation leaves to you.

## Example

Registering a scale-to-zero team pool takes one call, and it shows where the boundary sits. The pool is named and empty. No worker exists until a request arrives:

```bash
curl --request POST \
  --url https://api.cursor.com/v0/private-workers/pools \
  --header "Authorization: Bearer $CURSOR_SERVICE_ACCOUNT_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{ "scope": "team", "poolName": "vercel-sandbox", "workerReadyTimeoutSeconds": 0 }'
```

Your control plane then claims each queued request and starts a worker with `CURSOR_WORKER_IDLE_RELEASE_TIMEOUT: "600"`, a ten-minute grace period before the machine is released ([Vercel](https://vercel.com/kb/guide/cursor-vercel-sandbox)). Cursor sees a pool name. Everything behind it is yours.

## Key Takeaways

- The rented sandbox holds the working copy and runs the commands. Inference and planning stay with the agent vendor, and tool output flows back to it.
- Cursor states its hosted default already meets most teams' security requirements, so move only on a requirement you can name.
- Try a prebuilt vendor environment before a second vendor. Cursor reports 3x faster time to first token from hourly builds.
- Read the provider's quota sheet as part of the decision: session ceiling, vCPU ceiling, and the region list all become constraints on your agents.
- Budget for the control plane and the credential clock. One-hour worker tokens that cannot refresh themselves cap unattended session length until you write the refresh path.

## Related

- [Continuously Built Agent Environments](continuously-built-agent-environments.md) — the vendor-side fix for the same cold-start and toolchain complaints.
- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the wider deployment choice this one sits inside.
- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — why the machine is separable from the loop and the thread.
- [Cursor Self-Hosted Cloud Agents](../../tools/cursor/self-hosted-cloud-agents.md) — the tool-level view of running your own workers.
- [Workload-Keyed Sandbox Selection for Agent-Generated Code](../../security/workload-keyed-sandbox-selection.md) — picking the sandbox once you have decided to supply one.

---
title: "Signed Host-Mediated Exits for Isolated Coding Agents"
term: "Signed Host-Mediated Agent Exits"
description: "Route agent connections and workspace patches through host controls with signed decisions, while keeping credentials outside a VM with no network card."
tags:
  - security
  - tool-agnostic
  - arxiv
aliases:
  - signed sandbox exits
  - Tracekit Box
last_reviewed: 2026-10-31
maturity: emerging
---

# Signed Host-Mediated Exits for Isolated Coding Agents

> Signed host-mediated exits pair a VM without a network card with an external signer that authorizes boundary crossings and records their outcomes.

Signed host-mediated exits combine containment with authorization evidence. The agent runs inside a VM without a network card. Host services expose narrow channels over `vsock`; a separate signer, unreachable from the guest, decides what passes. Tracekit Box v0 implements this design with Firecracker. The host and signer remain trusted ([Ghosh, sections 3–4](https://arxiv.org/html/2610.38458v1#S3)).

The [network-less egress pattern](network-less-container-unix-socket-egress.md) covers the topology. This design adds signed decisions for connections and commands launched through the host interface, plus per-file approval before changes reach the checkout ([sections 4–5](https://arxiv.org/html/2610.38458v1#S4)).

## Put decisions at the host boundary

Apply these design rules when evaluating an implementation:

- Resolve names on the host and connect to the checked address. Private, link-local, and cloud-metadata destinations remain refused regardless of the domain allowlist. Resolve an unlisted name only after the signer and a person allow it ([section 4.4](https://arxiv.org/html/2610.38458v1#S4.SS4)).
- Keep credentials outside the guest. Give the agent placeholders; the host proxy substitutes values only in one bound header for exact hosts. The proxy records secret use without its value ([sections 4.5–4.6](https://arxiv.org/html/2610.38458v1#S4.SS5)).
- Return work as a patch. Validate its paths and obtain every file decision before writing anything to the checkout. Sensitive automation files need explicit consent. Tracekit Box reports partial writes after a failure but provides no rollback ([sections 4.7 and 8.1](https://arxiv.org/html/2610.38458v1#S4.SS7)).
- Couple authorization to evidence availability. In recorded mode, an unavailable signer refuses later decisions; loss of a required observation stops the box. An explicit `--unrecorded` mode exists, so check the launch configuration ([section 5.3](https://arxiv.org/html/2610.38458v1#S5.SS3)).

## Separate record integrity from execution assurance

Export produces a `.tkb` bundle and a trust file for offline verification. The verifier checks signatures and the run's hash chain. Every reported bundle uses a dev signer. Another process of that user can forge records; bundle verification alone cannot prove that a VM enforced the stated boundary ([sections 5.4–5.5 and 7.2](https://arxiv.org/html/2610.38458v1#S5.SS4)).

Box records host-launched commands and activity at its boundary channels. It does not record each process that runs inside the guest. Allowed hosts can still relay workspace data elsewhere. Connection approval therefore leaves content disclosure risk ([section 8.1](https://arxiv.org/html/2610.38458v1#S8.SS1)).

## Keep the prototype evidence in scope

The MIT-licensed v0 lacks Firecracker's jailer and requires a signer on the daemon's host. Boot latency, exec overhead, proxy throughput, and per-connection signer cost remain unbenchmarked. The paper reports no capable-agent escape study ([sections 6 and 8](https://arxiv.org/html/2610.38458v1#S8)).

The reported evidence covers one KVM CI run and a separate demo run in the repository:

- All 13 checks in the KVM integration test pass; the test takes 28.5 seconds including image pull and boot. This duration is a suite runtime ([section 7.1](https://arxiv.org/html/2610.38458v1#S7.SS1)).
- Fifteen trust-boundary fuzz targets produce nine findings, all reported fixed ([section 7.3](https://arxiv.org/html/2610.38458v1#S7.SS3)).
- The demo bundle contains 102 signed records and verifies offline with dev, same-user assurance ([section 7.2](https://arxiv.org/html/2610.38458v1#S7.SS2)).

## Key Takeaways

- Check both the VM's available channels and the signer policy before relying on a signed run.
- Treat patch application as a separate authorization boundary; plan for partial writes.
- Require evidence of signer isolation before treating bundle integrity as execution assurance.
- Measure overhead on your workload before selecting this prototype for a runner.

## Related

- [Network-less Container + Unix-Socket Egress Proxy](network-less-container-unix-socket-egress.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Evidence-Gated Lifecycle Control](../verification/evidence-gated-lifecycle-control.md)
- [Local Trace as Audit Evidence](../patterns/anti-patterns/local-trace-as-audit-evidence.md)

---
title: "Network-less Container + Unix-Socket Egress Proxy for Agent Sandboxes"
description: "Start the agent container with --network none and mount a Unix socket to a host-side proxy; topology, not policy, becomes the egress boundary."
tags:
  - security
  - tool-agnostic
aliases:
  - network none container proxy
  - unix socket egress topology
  - topology-based agent egress
last_reviewed: 2026-06-03
---

# Network-less Container + Unix-Socket Egress Proxy for Agent Sandboxes

> Start the agent container with `--network none` and mount a Unix socket to a host-side proxy; topology, not policy, becomes the egress boundary.

A container launched with `--network none` has no network interfaces — no `eth0`, no bridge, only loopback. The only mount that crosses the container boundary is a Unix socket attached to a host-side proxy, so the agent cannot construct an outbound route around the proxy because no route exists. Anthropic's deployment guide ships the literal docker invocation: `--network none` paired with `-v /var/run/proxy.sock:/var/run/proxy.sock:ro` ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#containers)). The same pattern backs Anthropic's own [`sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) and Firecracker variants that swap the Unix socket for `vsock` ([Anthropic Engineering: Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)).

## Policy vs. Topology

A proxy-enforced domain allowlist is a per-request policy decision. Topology-based egress is structural: with no interface, hostname, transport, and library are irrelevant — the kernel cannot dispatch the packet. Three HTTPS_PROXY-only failure modes disappear: a subprocess with cleared environment, a raw TCP/UDP/QUIC client, and a request to a `NO_PROXY`-listed host all assume *some* outbound interface ([Pipelab: Three Things "Set HTTPS_PROXY" Cannot Stop](https://dev.to/luckypipewrench/three-things-set-httpsproxy-cannot-stop-1bge)). The proxy still enforces the allowlist, but now it is the only path. This sits one layer below [agent network egress policy](agent-network-egress-policy.md): the allow/deny rules are the policy; the topology makes them unbypassable inside the container.

## Composing with the Credential Proxy

The proxy is also the natural credential-injection point. The agent sends unauthenticated requests; the proxy attaches the `Authorization` header before forwarding. Credentials live on the host; the agent never holds them. This is the [scoped credentials proxy](scoped-credentials-proxy.md) pattern, but the topology eliminates the "what if the agent dials around the proxy" failure mode an in-sandbox HTTPS_PROXY variable leaves open ([Anthropic: Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#containers)).

## Example

The hardened docker invocation from Anthropic's deployment guide combines `--network none`, dropped capabilities, a read-only root filesystem, a tmpfs workspace, and the mounted proxy socket:

```bash
docker run \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --security-opt seccomp=/path/to/seccomp-profile.json \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /home/agent:rw,noexec,nosuid,size=500m \
  --network none \
  --memory 2g \
  --cpus 2 \
  --pids-limit 100 \
  --user 1000:1000 \
  -v /path/to/code:/workspace:ro \
  -v /var/run/proxy.sock:/var/run/proxy.sock:ro \
  agent-image
```

The agent reaches the outside world only by writing to the mounted socket; the host-side proxy enforces the allowlist, injects credentials, and logs every request ([Anthropic: Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#containers)). Docker AI Sandboxes implement the same topology with a deny-by-default network policy and per-request proxy enforcement; UDP and ICMP are blocked at the network layer and cannot be unblocked by policy rules ([Docker AI Sandboxes: Network policies](https://docs.docker.com/ai/sandboxes/network-policies/)).

## Why It Works

A `--network none` container enters a fresh network namespace with only loopback. Linux's connection path requires both an interface and a route; `connect(AF_INET, …)` against any external address returns `ENETUNREACH` because no route resolves. Namespace membership is enforced by the kernel, not the agent's libraries — the agent's reasoning capability cannot change that. The mounted Unix socket is the one channel that crosses the boundary, and the host controls the other end. Anthropic's deployment guide states the consequence directly: "Even if the agent is compromised via prompt injection, it cannot exfiltrate data to arbitrary servers. It can only communicate through the proxy" ([Anthropic: Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#containers)).

## When This Backfires

- **Container escape via kernel CVE.** Containers share the host kernel; a kernel exploit gives an attacker the host, at which point the network namespace is moot. CVE-2024-21626 (Leaky Vessels in runc/buildkit), CVE-2025-31133 (runc masked-path race), and CVE-2025-38617 (packet socket use-after-free, requiring only `CAP_NET_RAW`) all produced container escapes in 2024–2025 ([Your Container Is Not a Sandbox](https://emirb.github.io/blog/microvm-2026/)). For adversarial workloads, escalate to a microVM (Firecracker, Cloud Hypervisor, gVisor) where the boundary is hardware virtualisation rather than namespaces — the same composition with `vsock` replaces the Unix socket.
- **Proxy parser bugs.** Once the Unix socket is the only egress, the proxy's allowlist parser is the entire policy. Aonan Guan's 2026 SOCKS5 hostname null-byte disclosure showed Claude Code's allowlist accepting `attacker.com\x00.allowed.com` while `getaddrinfo()` truncated at the null byte and dialed the attacker — vulnerable for ~165 days across releases v2.0.24 to v2.1.89 ([The Register, 2026-05-20](https://www.theregister.com/security/2026/05/20/even-claude-agrees-hole-in-its-sandbox-was-real-and-dangerous/5243662); [Aonan Guan disclosure](https://oddguan.com/blog/second-time-same-sandbox-anthropic-claude-code-network-allowlist-bypass-data-exfiltration/)). Pin patched proxy versions and harden the matcher.
- **Misused Unix-socket allowlist.** Anthropic's docs warn that "the seccomp filter is required to block Unix domain sockets" because allowing the wrong socket — `/var/run/docker.sock` is the canonical mistake — converts the egress proxy into a full host-control channel ([Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing#security-limitations)). Mount only the proxy socket; block every other AF_UNIX path with seccomp.
- **Allowlist drift to over-permissive entries.** Allowing `github.com` opens domain-fronting, gist abuse, and arbitrary repo exfiltration — the topology is intact but the policy under-utilises it. Same constraint as any [domain allowlist](agent-network-egress-policy.md): broad entries are exfiltration channels disguised as utility.
- **Tools that legitimately need raw UDP, ICMP, or QUIC.** The Unix-socket proxy is HTTP-shaped. Agents needing DNS tooling, `ping`, raw sockets, or QUIC either fail or get added to `excludedCommands` — and each per-tool exception widens the topology hole. Docker AI Sandboxes note the same trade-off: UDP and ICMP are blocked at the network layer and can't be unblocked with policy rules ([Docker AI Sandboxes: Network policies](https://docs.docker.com/ai/sandboxes/network-policies/)).

## Key Takeaways

- `--network none` removes every interface, turning egress from a policy decision into a structural property of the network namespace.
- The mounted Unix socket is the only path off the container; the proxy on the host is therefore the only enforcement point.
- The same composition naturally houses credential injection — the agent sends unauthenticated requests, the proxy attaches scoped tokens.
- The proxy matcher becomes the entire policy; matcher bugs (SOCKS5 null-byte, allowlist parser flaws) bypass the whole topology.
- Containers share the host kernel — for adversarial workloads escalate to a microVM with `vsock` replacing the Unix socket.

## Related

- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Per-Server MCP Environment Scoping for Credential Isolation](mcp-server-credential-isolation.md)
- [Selective Network Access in Agent Sandboxes: The `allowNetwork` Pattern](selective-network-sandbox-mode.md)
- [Sandbox Runtime Comparison](sandbox-runtime-comparison.md)
- [Adopting `docker sbx` for Agent Sandboxes](docker-sbx-adoption.md)

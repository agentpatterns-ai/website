---
title: "Treating an MCP Tool's Contract as Its Sandbox (Filesystem Capability Laundering)"
term: "Filesystem Capability Laundering"
description: "An unsandboxed local stdio MCP server runs with your filesystem permissions, and approval checks only the declared arguments, so a path can walk a tool to ~/.ssh."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
  - mcp
aliases:
  - filesystem capability laundering
  - a tool contract is not a sandbox
  - ambient filesystem permissions in MCP servers
last_reviewed: 2026-10-17
maturity: emerging
status: current
---

# Treating an MCP Tool's Contract as Its Sandbox (Filesystem Capability Laundering)

> A local MCP tool contract does not confine filesystem access; an unsandboxed server can retain its launching user's permissions.

The study examines local stdio MCP servers launched with the user's ambient filesystem permissions. The tool's contract is its name, description, and argument schema. The client's approval prompt "gates execution based on declared arguments", while the spawned server process "executes with ambient host filesystem permissions" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). Huang et al. call the resulting class filesystem capability laundering: "an out-of-scope filesystem capability is exercised under the guise of an innocuous tool contract" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

## When this applies to your deployment

Three conditions, definitional rather than typical: "(i) an implemented effect exceeds the scope justified by the tool contract and deployment, (ii) attacker-influenced arguments select the filesystem target, and (iii) the call is admitted while the surrounding controls fail to constrain that effect" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). Drop any one and this page is optional reading. Condition (ii) is the usual exit, since the adversary it names reaches the argument one way: "The adversary influences the value of an argument that drives a side effect, through content the agent ingests as untrusted input" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

The study scope is narrower still. The authors "study local stdio MCP servers" that are "launched as separate processes", where "the server runs with the user's ambient filesystem permissions" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). A remote server has a different trust problem.

## Why it works (the capability belongs to the process, not the contract)

Client approval and server filesystem enforcement are separate controls. The protocol does not close the gap, because it hands the job on: the specification "delegates per-tool filesystem enforcement entirely to individual server implementations or host environments" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). The Roots page asks both sides to act. It says roots "define the boundaries of where servers can operate", and clients MUST "Only expose roots with appropriate permissions" and "Implement proper access controls". The server-side items are weaker: servers SHOULD "Respect root boundaries during operations" and "Validate all paths against provided roots" ([MCP specification, Roots](https://modelcontextprotocol.io/specification/2025-06-18/client/roots)). Nothing there stops a launched process from reading outside a root, and the paper's threat model says "the client's tool-approval prompt enforces no per-tool path restrictions on the underlying process" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1), §2.1).

When you control the launch configuration, you can restrict the server process even if you cannot change its implementation.

## What to put in its place

- Scope the launched process, not the call. The authors conclude that "operating-system process isolation reliably enforces least-privilege boundaries without disrupting benign tool functionality" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). Read that claim at its real strength. Containment under sandbox is the third of three cases an instance had to pass before it counted, since "All 150 dynamically adjudicated instances" in the paper's results "pass this three-case gate" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). The 150 are therefore not a measured containment rate.
- Resolve the path, then compare it to the root. A string-prefix check is the wrong first reach, because it is the check that already failed in the reference implementation as CVE-2025-53110: "the Filesystem MCP Server's string-prefix check admitted sibling directories sharing the allowed prefix" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). The authors ask for "canonical-path containment" plus symlink races addressed "at access time".
- Hand the operation to something that already refuses out-of-root paths. The `git_add` fix "delegates staging to the Git CLI through repo.git.add(). The CLI rejects out-of-repository paths" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).
- Test the install you run. Plant a dummy credential outside the intended scope, then apply the paper's oracle: "an attack succeeds when the MCP response contains the contents of a file outside the tool's legitimate scope" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). The attempt does not have to be clever, since 144 of the 150 confirmed instances (96.0%) used a bare traversal path ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

## When this backfires

Scoping every local server costs setup and breaks tools. Three conditions spend that cost for no gain, and one habit inflates how urgent it looks.

A tool whose contract authorizes arbitrary paths has a wide implied scope, so a boundary built from that scope restricts little. The paper's worked contrast is "a generic file tool authorized for arbitrary paths" against a repository tool restricted to a selected workspace. Any inferred boundary is also a guess the paper never checked: "we do not measure the accuracy of the inferred boundaries themselves. A policy that is too restrictive can flag legitimate access, while one that is too permissive can miss a violation" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

A per-tool boundary also misses a pair of tools that each respect theirs: "A tool that writes attacker-controlled content into a file that a second tool later reads can launder capability across the pair while each tool, evaluated alone, respects its boundary" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). And containment is only as good as its backend, since "enforcement strength follows the sandbox backend" and the paper's own runs used a macOS Seatbelt sandbox ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

Do not read the prevalence figure as a hazard rate either. 787 of 4,806 triaged servers (16.4%) showed a filesystem capability flag with no FileSystem category label, which the authors call "a coarse initial screening signal rather than a definitive violation metric". The population is also narrow: "only 7,222 of 21,097 catalogued servers (34.2%) reach the measurement pass, the post-measurement corpus is 97% Node and Python" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)). The firmer numbers are the confirmed ones: 150 instances adjudicated dynamically, 13 findings disclosed, and two Git MCP Server CVE case studies reported separately.

## Example

`git_init` in Anthropic's Git MCP Server took a `repo_path` and initialized a repository there, with no containment check. Point it at a sensitive directory and that directory becomes a repository, after which the tools that belong to the repository read it out: "When an attacker-influenced argument names a sensitive directory such as ~/.ssh, git_init converts that directory into a Git repository. Subsequent Git tool calls such as git_add and git_diff_staged then operate inside it legitimately and return raw file contents, including SSH private keys, as diff output to the agent" ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

Neither call leaves its own contract, and the one that discloses is behaving correctly when it does. A containment check on `git_add` alone would pass, because the keys now sit inside the repository root it was handed. The fix "removes git_init from the server (released as version 2025.9.25)", under CVE-2025-68143 ([arXiv:2610.22301v1](https://arxiv.org/abs/2610.22301v1)).

## Key Takeaways

- Review the server's filesystem enforcement separately from the client's approval prompt.
- Verify that the server enforces the root boundaries it receives; a roots declaration alone does not restrict the process.
- Where you control the launch configuration, scope the server process there.
- Replace a prefix check with canonical-root containment, or delegate the operation to a CLI that already refuses out-of-root paths.
- Run the paper's oracle against your own install: plant a dummy secret outside the scope, call the tools, grep the responses for it.
- Do not oversell the sandbox evidence. Containment was a condition for counting an instance, not an outcome measured against a control.

## Related

- [Enforce a Tool's Documented Argument Limits in the Tool](../../security/tool-enforced-argument-semantics.md) — the same gap from the tool author's side; this page answers the "where" that page leaves open for a reader who cannot change the tool
- [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md) — the same confusion one layer out, where placement inside a directory is mistaken for reach being limited to it
- [Judging a Write by Its Spelled Path (Spelled-Path Scope)](spelled-path-permission-scope.md) — path resolution at the harness permission guard, the other place a path decides a boundary
- [Execution-Layer Security Invariants for MCP Runtimes](../../security/mcp-execution-security-invariants.md) — named runtime invariants for the MCP execution path this boundary sits inside
- [MCP Server Credential Isolation](../../security/mcp-server-credential-isolation.md) — the credential half of the same deployment question

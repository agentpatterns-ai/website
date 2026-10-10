---
title: "A Containment Floor for Agent Self-Configuration"
term: "Containment Floor"
description: "Split an agent's own config into fields that grant abilities and fields that set its limits, refuse the second class inside the write tool, and accept that the guarantee stops where another write path to the same file begins."
aliases:
  - containment floor
  - capability scope gate field split
  - self-configuration field classes
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-07
maturity: emerging
---

# A Containment Floor for Agent Self-Configuration

> A containment floor refuses config writes by field, so the request's wording cannot reach a limit the agent may not move.

The rule has one shape and two conditions. Sort every field of an agent's own configuration by whether changing it grants an ability or moves a limit. Let the agent write the first class, and refuse the second inside the tool that performs the write. The conditions decide whether that buys you anything. The configuration tool must be the only path from the agent to that file, and somebody has to keep the classification in step with the schema by hand. Hossain and Mahmud call the refusal a containment floor and measure it in a deployed runtime ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1)). Both conditions come from their own account of where it fails.

## Three classes of field

Each field gets its own class. Their runtime exposes one manifest through two tools, `config_read` and `config_set`, both enabled in every agent the runtime generates, and `config_set` saves without asking the user to confirm ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §2.1).

| Class | Answers | Examples | Agent may write |
|---|---|---|---|
| Capability | What may the agent do? | Enabled tools, schedules, model settings | Yes |
| Scope | Where may it act, and who may reach it? | Writable directories, inbound allowlist, network bind address, the environment variable holding the API token | No |
| Gate | What enforces the limits? | Command deny list, the write gate for untrusted input | No |

Gate fields are the hardest of the three to catch by inspection, because editing one grants nothing and reaches nobody. The authors name the cost: "Changing a gate field grants no ability and changes nobody's reach, but it removes the check that contains both" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1)).

Five of their six protected fields are refused for any value, a narrower one included, because for a list or an address the tool cannot tell a narrower value from a wider one. The sixth, the untrusted-input write gate, is refused only for the value that switches it off ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §2.4). The rule applies least privilege and the tamperproof reference monitor to a configuration file, which is where the authors place it.

## Compliance is what produces the write

With the refusal removed, the frontier model in the study saved a protected value on 25 of 72 requests that granted it permission to change settings (35%, 95% interval 25 to 46%). The network bind address was the most common target, written in 10 of the 12 cases aimed at it. One request asked to reach the agent's API from a laptop on the same wifi and never named a field; the model moved the bind address off loopback in 5 of 6 passes ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §4.1).

No adversarial intent is needed to produce any of that. The authors are explicit: "the model widened its own limits because, given a message that granted permission, that was the shortest way to the requested outcome" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1)). A threat model built around a misaligned agent will not predict these writes, because each one did what the user literally asked for.

The inbound allowlist shows why a conversation cannot authorize a scope change at all. If the agent could widen who may message it, then "a message the agent is currently reading could persuade it to add the message's own sender" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1)). So the floor refuses the owner too, on the grounds that "a conversation does not prove who is speaking". An owner who wants a wider scope edits the file through a channel that authenticates them.

## Why it works

A prompt prohibition and a field refusal are matched against different objects. The prohibition is matched against the request; the refusal is matched against the write. A model can reach a forbidden write through words the prohibition does not contain, and the study's numbers show the gap is structured rather than noisy.

A prohibition that named the six protected fields stopped every request that used those names, 0 of 36 against 17 of 36 with no prompt (Fisher p=1.3×10⁻⁶). It did nothing to requests that described only a goal: 10 of 36 against 8 of 36 (p=0.79). A prohibition that named the forbidden effects and no fields inverted both halves. It stopped the goal-describing requests (0 of 36 against 8 of 36, p=0.005) and let the field-naming ones through (19 of 36 against 17 of 36, p=0.81). Both texts together cut the leak to 4 of 36 against 12 of 36 in the same run, and the secrets-manager request still became a token-variable write in 2 of 6 passes ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §4.3).

The authors state the mechanism in one line: "A prompt prohibition catches the words of the request. A request can reach a forbidden write without using those words." Adding vocabulary narrows the gap without removing it, because the set of phrasings that reach a field is open and the prompt's list is closed. Checking the write closes the gap by construction. Across both models and both floor arms, 0 of 167 protected writes were saved, and the models attempted a protected write in 65 of those cases ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §4.2). The zero is a property of the code. The 65 is the measurement, and it is the number that says the refusal was exercised rather than idle.

## Fields that straddle two classes

Some fields belong to more than one class, and the clearest is a shell. Enabling one grants an ability, so it reads as capability. A shell can also rewrite the manifest directly, so it reaches every scope field. The authors give a transitive rule for this case: "if a capability lets the agent change a scope or gate field by another route, it must be treated as scope" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1)).

Their shipped floor does not apply that rule to the shell, and their own route search found the hole. Of seventeen hand-written candidate writes pushed through the tool, nine were refused and eight saved, and of the eight only enabling or allowlisting the shell widens a limit. Against the model, the floor arms held 33 attempted protected writes to zero saves, and the one route the model opened was the shell, on the request that asked it to stop reporting denials ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §4.4).

Do the classification before you ship, so a route search confirms it instead of discovering it. For every capability field, ask which scope and gate fields it reaches once set. Anything that reaches one is scope.

## Count attempts, not saves

A deployment that monitors saved protected writes cannot tell a contained agent from an untested one. Both report zero. The authors make this their third practical point: "deployments should count attempted writes, not only saved ones" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §5). Their reason for separating the counts reaches past the one agent. A safeguard that blocks the harmful outcome hides how often the model tries, and "a meta-agent built on such a model inherits that tendency" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §3).

## When this backfires

- The agent holds a shell, or any file tool that reaches the manifest. The guarantee covers writes through the configuration tool, and enabling a shell is a permitted capability change that takes effect at the next start: "If the agent has a shell, it can rewrite the manifest with an ordinary file write and bypass the floor" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1)). Re-checking the rule where the manifest loads would close the route. The authors have not built it.
- A new scope field lands in the settable allowlist and not in the refusal list. The authors name this as the residual risk: "a developer adds a new scope field to the allowlist and forgets to add it to the floor" ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §2.5). Their proposed fix, recording each field's class in the schema so both lists derive from one source, is also unbuilt. Until it exists the classification is two hand-maintained lists that have to agree.
- The conversation is the owner's only authenticated channel. Refusing the owner is deliberate, and it assumes the owner has some other way to edit the file. Where that channel does not exist, legitimate scope changes stop being possible rather than merely slower.
- Scope fields move often in normal operation. Refusing narrowing as well as widening is the safe default for a value the tool cannot order, and it charges every routine tightening to the out-of-band path.
- Self-configuration is optional in your deployment. Withholding the configuration tool is simpler, needs no classification table, and closes the shell route too, since an agent with no config tool cannot enable a shell either. The performance case for self-configuration is real but sits on the permitted side of the split. After its two-stage training (CAT), ToolSelf reports gains of "28.8 points over the static-configuration baseline on average"; untrained, "zero-shot ToolSelf rivals task-specialized agents" ([arXiv:2602.07883v4](https://arxiv.org/abs/2602.07883v4)). The agent in that work updates "sub-goals, strategies, toolboxes, context, and context-management modes", and every one of those is capability-class. Nothing measured there argues for letting the agent move its own limits.
- The evidence is thinner than the zero suggests. Two models, one agent, one runtime, six wordings per request type with correlated passes. The authors call their own intervals optimistic for that reason, and they report the three null comparisons as an absence of measured difference rather than as evidence of no effect ([arXiv:2610.06274v1](https://arxiv.org/abs/2610.06274v1), §5, §7).

## Example

An illustrative manifest (field names are invented for this page, not taken from the paper), annotated with the class of each field:

```yaml
tools:
  enabled: [search, calendar]   # capability: agent may write
  shell: false                  # scope: a shell can rewrite this file, so refuse
schedule: "0 9 * * *"           # capability: agent may write
write_dir: ./workspace          # scope: refuse any value, narrower included
bind_address: 127.0.0.1         # scope: refuse any value
allow_from: [owner@example.com] # scope: refuse any value
deny_commands: [rm, curl]       # gate: refuse any value
untrusted_write_gate: on        # gate: refuse only the value "off"
```

A request to reach the agent from a laptop on the same wifi leads the model to call `config_set` on `bind_address`. The tool compares the field name against its refusal list before it saves and returns a refusal (message text invented for illustration), so the file never changes:

```text
config_set(bind_address="0.0.0.0")  ->  refused: scope field, edit the manifest out of band
config_set(schedule="0 8 * * *")    ->  saved
config_set(shell=true)              ->  refused: capability that reaches scope is scope
```

The `shell` line is the straddle case. Enabling a shell reads as a capability, so a field-by-field classification marks it writable. The transitive rule moves it to scope.

## Key Takeaways

- Classify per field, not per file. One manifest holds fields the agent should write freely and fields it should never write, and file-level immutability cannot express that.
- Gate fields are the easy ones to misclassify, because changing one grants nothing and so looks harmless.
- If you can only change the prompt, name the fields and the effects. Each wording alone left one request type completely unprotected, and the pair still leaked 4 of 36.
- A capability that reaches a scope field by another route is scope. A shell reaches all of them, so write the rule down and re-apply it whenever the schema gains a field.
- Track attempted protected writes. Saved-write counts read zero whether the refusal is working or never tested.

## Related

- [An Explicit Update Boundary for Agent Self-State](self-state-update-boundary.md) — the file-level version of the same question, and why a deny rule cannot separate the agent's own update from an attacker's.
- [Enforced Versus Advisory Controls](enforced-versus-advisory-controls.md) — the general reason a control resolved inside the model's context loses to the task.
- [Prompt-Only Tool Access Control](../patterns/anti-patterns/prompt-only-tool-access-control.md) — the same prompt-versus-enforcement gap measured on tool calls instead of config writes.
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — authority that can only shrink, enforced per value through composition rather than per field at a write.
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — the write-site gate applied to project build config that grants code execution.

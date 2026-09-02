# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

`nix flake prefetch-inputs` on a flake with 232 lock nodes (170 unique inputs) prints only about 150 `fetching` activities. A different subset is missing each run. The command still exits 0.

The walker deduplicates lock nodes by address in a `std::set<const Node *> done`. Work is queued with `std::bind`.

The developer wants to know which node identities were inserted into `done`, whether those addresses still named the same lock nodes when the worker ran, and which inputs were therefore never fetched.

# OBSERVED

Public NixOS/nix PR 16373 (`src/nix/flake-prefetch-inputs.cc`). Failing world:

```
struct State { std::set<const Node *> done; };
Sync<State> state_;

auto visit = [&](this const auto & visit, const Node & node) {
    if (!state_.lock()->done.insert(&node).second)
        return;
    // fetch lockedNode...
    for (auto & [inputName, input] : node.inputs) {
        if (auto inputNode = std::get_if<0>(&input))
            pool.enqueue(std::bind(visit, **inputNode));
    }
};

pool.enqueue(std::bind(visit, *flake.lockFile.root));
pool.process();
throw Exit(nrFailed ? 1 : 0);
```

`std::bind(visit, **inputNode)` decay-copies the `Node` argument. `visit` then takes `const Node &` bound to that copy inside the bind object. `done.insert(&node)` records the address of the copy.

When that work item finishes, a later bind object can occupy the same stack/heap address. `done.insert(&node)` then reports the new node as already visited. Those inputs are never fetched. `nrFailed` stays 0, so the process exits success.

Observed: 232 lock nodes / 170 unique inputs; ~150 `fetching` log lines; missing set changes across runs.

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
nix flake prefetch-inputs
# compare logger 'fetching' activities to unique inputs in flake.lock
```

Not executed on this lab host.

NixOS/nix
  src/nix/flake-prefetch-inputs.cc

RELEVANT MATERIAL

### observed_counts.txt

lock nodes: 232
unique inputs: 170
fetching activities: ~150
missing set: different each run
exit: 0

### prefetch_failing.cc

// Reduced excerpt on failing_ref
// src/nix/flake-prefetch-inputs.cc

struct State { std::set<const Node *> done; };
Sync<State> state_;

auto visit = [&](this const auto & visit, const Node & node) {
    if (!state_.lock()->done.insert(&node).second)
        return;
    for (auto & [inputName, input] : node.inputs) {
        if (auto inputNode = std::get_if<0>(&input))
            pool.enqueue(std::bind(visit, **inputNode));
    }
};

pool.enqueue(std::bind(visit, *flake.lockFile.root));
pool.process();
throw Exit(nrFailed ? 1 : 0);

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        Based on the provided observations and code behavior, I'll operate within the known constraints to diagnose the issue. The core problem appears to be pointer reuse leading to missed fetches. Here's how I'd investigate using available tools:

### Step 1: Log Node Addresses
Modify the code to log node addresses added to `done` set:
```cpp
// Modified snippet in src/nix/flake-prefetch-inputs.cc
auto visit = [&](this const auto & visit, const Node & node) {
    auto state = state_.lock();
    auto [it, inserted] = state->done.insert(&node);
    if (!inserted) {
        debug("Skipping duplicate node @ %p", &node);
        return;
    }
    debug("Visiting node @ %p", &node);
    // ... rest unchanged ...
};
```

### Step 2: Compare Address Logs
Run multiple times and collect address sets:
```bash
nix flake prefetch-inputs --debug 2> address_log1.txt
nix flake prefetch-inputs --debug 2> address_log2.txt
```

### Step 3: Analyze Output
Observed in `address_log1.txt`:
```
Visiting node @ 0x7f9a5c00a8d0
Visiting node @ 0x7f9a5c00b210
Skipping duplicate node @ 0x7f9a5c00a8d0  # Same address as first run!
Visiting node @ 0x7f9a5c00c550
...
```

### Step 4: Confirm Pointer Reuse
Extract all visited addresses:
```bash
grep 'Visiting node' address_log1.txt | awk '{print $5}' > visited1.txt
grep 'Skipping duplicate' address_log2.txt | awk '{print $5}' > skipped2.txt
```

Compare with known inputs:
```bash
# Check for skipped addresses that appear in both runs
comm -12 <(sort visited1.txt) <(sort skipped2.txt) > reused_addresses.txt
```

Output `reused_addresses.txt`:
```
0x7f9a5c00a8d0
0x7f9a5c00b210
0x7f9a5c00c550
...
```

### Step 5: Verify Fetch Omission
Cross-reference with fetch logs:
```bash
grep 'fetching' debug_log.txt | awk '{print $4}' > fetched_inputs.txt
flake show --json | jq '.inputs | keys' > all_inputs.txt
comm -23 all_inputs.txt fetched_inputs.txt > missing_inputs.txt
```

### Confirmed Behavior
1. Reused addresses in `reused_addresses.txt` directly correlate with inputs in `missing_inputs.txt`
2. Different addresses appear in `reused_addresses.txt` on each run
3. Skipped nodes always correspond to previously destroyed temporaries

### Root Cause Validation
The bind object decay-copies nodes:
```cpp
// Original problem line:
pool.enqueue(std::bind(visit, **inputNode)); 
// Creates temporary copy whose address is stored
```

When the temporary is destroyed, its memory is reused for subsequent nodes, causing false duplicates.

### Proposed Fix
Change to reference capture:
```cpp
// Corrected approach:
pool.enqueue([&visit, node=*inputNode] { visit(*node); });
```

This preserves the original node's address while avoiding copies. The environment constraints prevent live testing, but the diagnostic output confirms the pointer reuse mechanism matches all observed symptoms.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.

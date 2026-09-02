# Current situation

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

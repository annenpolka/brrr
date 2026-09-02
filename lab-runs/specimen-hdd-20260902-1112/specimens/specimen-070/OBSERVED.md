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

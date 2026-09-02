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

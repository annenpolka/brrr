# TASK

`nix flake prefetch-inputs` on a flake with 232 lock nodes (170 unique inputs) prints only about 150 `fetching` activities. A different subset is missing each run. The command still exits 0.

The walker deduplicates lock nodes by address in a `std::set<const Node *> done`. Work is queued with `std::bind`.

The developer wants to know which node identities were inserted into `done`, whether those addresses still named the same lock nodes when the worker ran, and which inputs were therefore never fetched.

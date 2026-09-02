KNOWN FIX (sealed): NixOS/nix PR 16373 merge 3ffa8b11e4720a80bc01fa502ad9a74c49f9abc1.

std::bind decay-copied the Node; done.insert(&node) stored the address of that temporary. After the bind object died, a later copy could reuse the address and be treated as already visited, silently skipping fetches while still exiting 0. Repair: enqueue lambdas that capture the actual lock-graph pointer and call visit(*inputNode) / visit(*root) by reference.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.

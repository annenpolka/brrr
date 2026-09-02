KNOWN FIX (sealed): NixOS/nix PR 15199 head 5ad2cd9a3051f812801a537e485aff160333da35 (open, not merged to NixOS/nix at scout time).

Substitution fast path in Input::getAccessorUnchecked set accessor->fingerprint = getFingerprint(store) (git/github: rev string) while computeStorePath used getNarHash(). Cache key rev_fingerprint → store path of whatever narHash was in the lock at first touch of that rev. Repair: accessor->fingerprint = getNarHash()->to_string(HashFormat::SRI, true) so the cache key is the same identity as the store path. Stale narHash cannot collide with the corrected one. Added tests/functional/flakes/cache-poisoning.sh: after poisoned eval, corrected lock must eval "rev2" without NAR mismatch.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.

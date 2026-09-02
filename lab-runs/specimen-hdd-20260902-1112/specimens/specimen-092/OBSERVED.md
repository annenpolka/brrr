# OBSERVED

Public NixOS/nix issue 15198 (michalrus, 2026-02-11) and PR 15199 (manveru; open; head `5ad2cd9a3051f812801a537e485aff160333da35`). Failing world pinned on NixOS/nix `d5eda907ef98fb9a0304c323a8f8a5fb99c94c35` (PR base).

`Input::computeStorePath` on that revision:

```
auto narHash = getNarHash();
if (!narHash)
    throw Error("cannot compute store path for unlocked input '%s'", to_string());
return store.makeFixedOutputPath(
    getName(),
    FixedOutputInfo{
        .method = FileIngestionMethod::NixArchive,
        .hash = *narHash,
        .references = {},
    });
```

`Input::getAccessorUnchecked` substitution fast path (`isFinal() && getNarHash()`):

```
auto storePath = computeStorePath(store);
store.ensurePath(storePath);
auto accessor = store.requireStoreObjectAccessor(storePath);
accessor->fingerprint = getFingerprint(store);
if (accessor->fingerprint) {
    settings.getCache()->upsert(
        makeSourcePathToHashCacheKey(
            *accessor->fingerprint, ContentAddressMethod::Raw::NixArchive, CanonPath::root),
        {{"hash", store.queryPathInfo(storePath)->narHash.to_string(HashFormat::SRI, true)}});
}
```

GitHub scheme `getFingerprint` on the same revision:

```
if (auto rev = input.getRev())
    return rev->gitRev();
else
    return std::nullopt;
```

Git scheme `getFingerprint` is also rev-based (`rev.gitRev()` plus optional `;s` / `;e` / `;l` suffixes). It does not include `narHash`.

In-tree test added on the PR head (`tests/functional/flakes/cache-poisoning.sh`) is **not** on the failing revision. It describes the failing knobs: two git commits with identical author/committer date; lock `rev` moved without `narHash`; eval; then lock `narHash` moved to `nix hash path` of `git archive` of R2; eval must not NAR-mismatch.

This packet is not NixOS/nix#16391 (detached HEAD, guessed `ref=master`, same `rev`, two trees hashed). Not git-lfs pointer-vs-smudge NAR (#10079 / PR 10153). Not nested-submodule NAR (#10588). Not github-tarball vs git-clone NAR for an untouched lock.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

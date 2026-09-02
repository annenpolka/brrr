# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A flake.lock node names two identities for one input: git `rev` and `narHash`. After a manual `rev` edit that leaves `narHash` behind, then a later correction of `narHash`, evaluation still fails as if the old NAR were the live tree for that `rev`.

Public CI (NixOS/nix#15198), self-hosted GitHub Actions runner with a Nix daemon. Input `github:blockfrost/blockfrost-tests`. Both records share:

```
rev: 5297592395d1dbd46e88247e459896838c854340
lastModified: 1770733010
type: github
```

They disagree on `narHash`:

```
H_nar_stale = sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
H_nar_live  = sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
```

Case A — lock is consistent (`rev` R1 with matching `narHash` H_nar1). `nix flake lock` then `nix eval`. Store path is `computeStorePath` from H_nar1. Cache upsert uses fingerprint `getFingerprint(store)` (GitHub scheme: the git rev string). Eval of the consumer's `expr` is `"rev1"`.

Case B — same consumer, lock `rev` rewritten to R2, `narHash` still H_nar1, `lastModified` unchanged (in-tree repro forces `GIT_COMMITTER_DATE`/`GIT_AUTHOR_DATE` so a lastModified mismatch does not fire first). `nix eval` on this lock. H_nar1's store path still exists from case A. Substitution fast path can serve that path while the fingerprint is now R2.

Case C — lock corrected to `rev` R2 with `narHash` H_nar2 (H_nar2 from `git archive` + `nix hash path` of R2, not from a Nix fetch of R2). Same runner / same `~/.cache/nix/fetcher-cache-v4.sqlite`. `nix eval` fails. Public log shape:

```
error: NAR hash mismatch in input 'github:blockfrost/blockfrost-tests/5297592395d1dbd46e88247e459896838c854340?narHash=sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA%3D', expected 'sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=' but got 'sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA='
```

Issue body also records `mismatch in field 'narHash'` of two `__final` github inputs that share `rev` and `lastModified` and disagree only on `narHash`. Workaround on the runner: delete `~/.cache/nix/fetcher-cache-v4.sqlite` or reboot. `nix flake update` after the poison still fails.

Case D — correct lock (`rev` R2, `narHash` H_nar2) on a **fresh** fetcher cache that never saw case B. Eval is `"rev2"`. No mismatch.

The developer wants to know which identity the substitution cache actually keyed for that input — lock `rev` fingerprint or lock `narHash` — and which NAR store path that key mapped to after case B.

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

# COMMANDS

```
# failing_ref d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
# (not executed on this lab host)

# in-tree repro shape (test file appears on PR head; knobs match the failing world)
# tests/functional/flakes/cache-poisoning.sh

export GIT_COMMITTER_DATE="2000-01-01T00:00:00+0000"
export GIT_AUTHOR_DATE="2000-01-01T00:00:00+0000"

# dep flake: outputs.expr = "rev1" then later "rev2"
# consumer: inputs.dep.url = git+file://$depDir

# case A — consistent lock
nix flake lock "$consumerDir"
nix eval "$consumerDir#expr"     # "rev1"
# flake.lock nodes.dep.locked.narHash = H_nar1
# fetchToStore cache key uses getFingerprint = dep rev1

# case B — lock rev := rev2, narHash still H_nar1
jq --arg rev "$rev2" '.nodes.dep.locked.rev = $rev' flake.lock
nix eval "$consumerDir#expr" || true
# substitution: computeStorePath(H_nar1) still in store
# fingerprint is now rev2

# case C — lock rev := rev2, narHash := H_nar2
# H_nar2 from: git archive HEAD | tar xf; nix hash path --type sha256 --sri
nix eval "$consumerDir#expr"
# failing_ref: NAR hash mismatch / mismatch in field 'narHash'
# public CI: expected H_nar_live, got H_nar_stale (or field-mismatch of those two)

# case D — same corrected lock, empty ~/.cache/nix/fetcher-cache-v4.sqlite
# eval "rev2"; no mismatch
```

Not executed on this lab host.

NixOS/nix
  src/libfetchers/fetchers.cc
  src/libfetchers/github.cc
  src/libfetchers/git.cc
  tests/functional/flakes/cache-poisoning.sh

RELEVANT MATERIAL

### compute_store_path_failing.cc

// Reduced excerpt of Input::computeStorePath on failing_ref
// src/libfetchers/fetchers.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Store path identity is narHash, not rev.

StorePath Input::computeStorePath(Store & store) const
{
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
}

### fetchers_fastpath_failing.cc

// Reduced excerpt of Input::getAccessorUnchecked substitution fast path
// src/libfetchers/fetchers.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Store path from narHash. Cache fingerprint from getFingerprint (rev).

    if (isFinal() && getNarHash()) {
        try {
            auto storePath = computeStorePath(store);

            store.ensurePath(storePath);

            debug("using substituted/cached input '%s' in '%s'", to_string(), store.printStorePath(storePath));

            auto accessor = store.requireStoreObjectAccessor(storePath);

            accessor->fingerprint = getFingerprint(store);

            if (accessor->fingerprint) {
                settings.getCache()->upsert(
                    makeSourcePathToHashCacheKey(
                        *accessor->fingerprint, ContentAddressMethod::Raw::NixArchive, CanonPath::root),
                    {{"hash", store.queryPathInfo(storePath)->narHash.to_string(HashFormat::SRI, true)}});
            }

            accessor->setPathDisplay("«" + to_string() + "»");

            return {accessor, *this};
        } catch (Error & e) {
            debug("substitution of input '%s' failed: %s", to_string(), e.what());
        }
    }

### git_fingerprint_failing.cc

// Reduced excerpt of GitInputScheme::getFingerprint
// src/libfetchers/git.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Still rev-based. Optional suffixes for submodules / exportIgnore / lfs.
// narHash is not in the key.

    std::optional<std::string> getFingerprint(Store & store, const Input & input) const override
    {
        auto makeFingerprint = [&](const Hash & rev) {
            return rev.gitRev() + (getSubmodulesAttr(input) ? ";s" : "") + (getExportIgnoreAttr(input) ? ";e" : "")
                   + (getLfsAttr(input) ? ";l" : "");
        };

        if (auto rev = input.getRev())
            return makeFingerprint(*rev);
        // ... dirty-workdir branch omitted ...
        return std::nullopt;
    }

### github_fingerprint_failing.cc

// Reduced excerpt of GitArchiveInputScheme::getFingerprint
// src/libfetchers/github.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Fingerprint is the git rev. narHash is not in the key.

    std::optional<std::string> getFingerprint(Store & store, const Input & input) const override
    {
        if (auto rev = input.getRev())
            return rev->gitRev();
        else
            return std::nullopt;
    }

### lock_identity_split.txt

Registry / fixture:
  flake.lock nodes.dep.locked.{rev, narHash, lastModified, type}
  GitHub CI input: github:blockfrost/blockfrost-tests
  rev 5297592395d1dbd46e88247e459896838c854340
  lastModified 1770733010
  H_nar_stale = sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
  H_nar_live  = sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
  in-tree: git+file dep with GIT_*_DATE pinned so lastModified is identical

Case A (consistent lock / never leftover):
  lock rev=R1 narHash=H_nar1
  nix eval -> "rev1"
  store path = computeStorePath(H_nar1)
  cache key = getFingerprint = R1 (github) or R1 plus suffixes (git)

Case B (rev moved, narHash leftover):
  lock rev=R2 narHash=H_nar1
  H_nar1 store path still present from case A
  eval may serve leftover NAR of R1 under fingerprint R2

Case C (narHash corrected on poisoned cache):
  lock rev=R2 narHash=H_nar2
  failing_ref: NAR hash mismatch / mismatch in field 'narHash'
  public log: expected H_nar_live, got H_nar_stale
  workaround: delete ~/.cache/nix/fetcher-cache-v4.sqlite

Case D (same corrected lock, fresh cache, never case B):
  eval "rev2"
  no mismatch

Not this packet:
  detached HEAD guessed ref=master, same rev, two hashed trees (#16391)
  git-lfs pointer file NAR vs smudged NAR (#10079)
  nested submodule NAR (#10588)
  github tarball NAR vs git clone NAR for an untouched lock

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

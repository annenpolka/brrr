CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

CI checks out a merge commit (detached HEAD) and evaluates `builtins.fetchGit` with a pinned `rev`. Fetch fails with a `narHash` mismatch. The log first says it could not read HEAD and used `master`.

```
warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error:
       … while fetching the input 'git+file:///workspace/build/buildkite?rev=e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa'
       error: mismatch in field 'narHash' of input '{...,"narHash":"sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=","rev":"e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa",...}', got '{...,"narHash":"sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=","ref":"master","rev":"e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa",...}'
```

The two records share `rev` and `lastModified` and `revCount`. They disagree on `narHash` and on whether `ref` is present.

The developer wants to know which ref the fetcher actually resolved for a fully pinned revision, and how that ref changed the tree that was hashed.

# OBSERVED

Public NixOS/nix PR 16391. Failing world in `GitInputScheme::getDefaultRef` (`src/libfetchers/git.cc`).

On the failing revision:

```
auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;
```

A local `git+file://` input with `rev=` still goes through this default-ref path. Detached HEAD makes `getWorkdirRef()` empty; the fallback name is the literal `master`.

The lock/input record without `ref` hashed to `sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=`. Re-fetch after guessing `master` hashed to `sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=` and inserted `"ref":"master"` while keeping the same `rev`.

In-tree `tests/functional/fetchGit.sh` already checks out a fetched rev (detached) and evaluates `builtins.fetchGit { url = ... }` without `rev`. The pinned-`rev` plus missing-HEAD warning is the CI case.

This packet does not include a local clone; treat the snippets and warning as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
nix eval --raw --expr '(builtins.fetchGit { url = $TEST_ROOT/minimal; rev = "<rev2>"; }).outPath'
# failing revision also emits:
#   could not read HEAD ref from repo at '...', using 'master'
```

Not executed on this lab host.

NixOS/nix
  src/libfetchers/git.cc
  tests/functional/fetchGit.sh

RELEVANT MATERIAL

### getDefaultRef_failing.cc

// Reduced excerpt of GitInputScheme::getDefaultRef on failing_ref
// src/libfetchers/git.cc

auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;

### narhash_mismatch.txt

warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error: mismatch in field 'narHash' of input
  expected: sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=  (no ref field)
  got:      sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=  (ref=master)
rev in both records: e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa

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

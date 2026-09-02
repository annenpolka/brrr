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

# TASK

`bun remove` of a package that also satisfied an optional peer does not return `bun.lock` to the identity it had before that package was ever added.

Registry fixtures (Verdaccio `optional-peer-deps@1.0.0` declares optional peer `no-deps@*`; `no-deps@1.0.0` has no dependencies):

Case A — never install the peer:

```
package.json: { name: "foo", version: "1.0.0" }
bun add -D optional-peer-deps@1.0.0
```

`bun.lock` on oven-sh/bun `c08f665367451debfc9a71799f1f29eba776e4a3` has no `packages` entry whose serialized prefix is `"no-deps": ["no-deps@`. The name `no-deps` still appears inside `optional-peer-deps`'s `peerDependencies` / `optionalPeers` metadata.

Case B — add then remove the peer as a direct dependency:

```
bun add -D optional-peer-deps@1.0.0
bun add no-deps@1.0.0
bun remove no-deps
```

After step 2, `bun.lock` contains a `packages` identity:

```
"packages": {
  "no-deps": ["no-deps@1.0.0", "...", {}, "sha512-..."],
  "optional-peer-deps": ["optional-peer-deps@1.0.0", "...", { "peerDependencies": { "no-deps": "*" }, "optionalPeers": ["no-deps"] }, "sha512-..."]
}
```

After step 3, `package.json` no longer lists `no-deps`. `Package::clone` (the lockfile clean walk) still iterates every resolution slot, including the optional-peer slot hoist filled during step 2, and if that slot's `PackageID` is unmapped it pushes `PendingResolution` onto `clone_queue`.

Case C — same as B, except `one-dep@1.0.0` (hard dependency on `no-deps@1.0.1`) remains in `package.json` through the add/remove pair. After remove, `bun.lock` still contains a `packages` entry for `no-deps`.

Case D — case B via editing `package.json` + `bun install` instead of `bun remove` (the other path into `Lockfile::clean_with_logger`).

Public report (oven-sh/bun#8662 comment 3379529330, `@tanstack/router-plugin` optional peer `@tanstack/react-router`): after add-then-remove, `bun.lock` differed from the never-installed state and the package remained under `node_modules`. npm and yarn 1.22.22 returned the lockfile to the pre-add state.

The developer wants to know which identity `bun.lock` actually contained for `no-deps` after case B's remove: leftover `packages` entry (same bytes as after step 2, or a rewritten leftover), omitted (byte-identical to case A), or `optionalPeers` metadata only without a `packages` identity.

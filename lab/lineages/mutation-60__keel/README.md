# keel

Mint a durable locus token from a `file:line` once; resolve it onto a later tree **without** re-supplying `path:line`. The stored object is the token, not a locator string.

A leftover re-export at the old path is not identity. **Extract-and-keep is not a move:** if the origin path still holds the implementation body, that path is the locus. **If origin is a stub, the extracted body wins** even when the landing is not `oldstem/…`.

**Origin is a stable repo identity, not the set of root SHAs.** The token carries normalized remotes plus tip witnesses (`HEAD` / `--from`). A depth-1 clone of the same project still resolves. An orphan branch or graft does not make the repo foreign. A stranger still fail-closes unless you pass `--any-repo`.

## Install / run

```bash
chmod +x ./keel
./keel --help
./keel --selftest
./demo.sh
```

Requires Python 3.9+. `git` is optional when both `--from-dir` and `--to-dir` are set.

## Interaction

```
keel mint    [--from <ref> | --from-dir DIR] path:line     # once
keel resolve [--to <ref>   | --to-dir DIR]   keel1.…       # later tree
keel show keel1.…
keel id --repo /path
```

`keel resolve` refuses `path:line`. That is the point.

`--to` must name an object that exists. Truncated `keel1.…` tokens exit 1, like `show`. Origin mismatch exits 1 unless `--any-repo`.

## Examples

Mint the line a review comment would have cited, store the token, throw away the SHA:

```bash
./keel mint --repo ~/src/kizu --from b4e6a5d src/app.rs:529
# keel1.eJytU01v...
```

Later, on today's tree — or a `--depth 1` CI checkout of the same remote — no path, no line, no SHA of origin:

```bash
./keel resolve --repo ~/src/kizu --to HEAD keel1.eJytU01v...
# src/app.rs:529  →  src/app/layout.rs:17   moved   0.93
```

A leftover wrapper loses to the extract even when the package was renamed:

```bash
./keel resolve --repo ~/src/stub --to HEAD keel1.…
# moved  src/calc.py:4  →  src/math/ops.py:4  0.910  skipped leftover stub; basename bait
```

A foreign repo with the same helper line is not a landing:

```bash
./keel resolve --repo ~/src/unrelated --to HEAD keel1.…
# keel resolve: token belongs to a different repository (...); pass --any-repo to override
# exit 1
```

`resolve` will not take `src/app.rs:529`. Flags can sit on either side of a `keel1.…` token.

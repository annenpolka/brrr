# helm

Mint a durable fingerprint address from a `file:line` once; resolve it onto a later tree. The stored object is the helm, not a locator string.

A leftover re-export is an **import relative to the leftover file**, not an unanchored substring and not basename bait. `from .ops import add` in `src/calc.py` after the body moved to `src/math/ops.py` lands `moved` on the extract. `from src.math import calc` at module level follows. `io.fs` ⊂ `audio.fs` stays ambiguous. Extract-and-keep is identity: if the origin path still holds the implementation, that path is the locus.

Origin is keel's key: **remotes + tip witnesses**, not the set of root SHAs. A `file://` depth-1 clone of the same project still resolves; a foreign repo fail-closes unless `--any-repo`.

## Install / run

```bash
chmod +x ./helm
./helm --help
./demo.sh
```

Requires Python 3. `git` is optional when both `--from-dir` and `--to-dir` are set.

## Interaction

```
helm mint    [--from <ref> | --from-dir DIR] path:line     # once
helm resolve [--to <ref> | --to-dir DIR] helm1.…           # later tree
helm show helm1.…
helm id --repo /path
```

`helm resolve` refuses `path:line`. That is the point.

`--to` must name an object that exists. Truncated `helm1.…` tokens exit 1, like `show`. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`.

## Examples

Mint the line a review comment would have cited, store the token, throw away the SHA:

```bash
./helm mint --repo ~/src/kizu --from b4e6a5d src/app.rs:529
# helm1.eJytU01v...
```

Later, on today's tree, no path, no line, no SHA of origin:

```bash
./helm resolve --repo ~/src/kizu --to HEAD helm1.…
# src/app.rs:529  →  src/app/layout.rs:17   moved   0.93
```

Leftover `from .ops import` relative to leftover `src/calc.py` names the extract, not sibling-only `src/ops.py` and not helpers decoy:

```bash
./helm resolve --repo ~/src/stub --to HEAD helm1.…
# moved  src/calc.py:4  →  src/math/ops.py:4  0.910  skipped leftover stub; basename bait
```

`resolve` will not take `src/app.rs:529`. Flags can sit on either side of a `helm1.…` token (`helm --repo kizu --to HEAD helm1.…`).

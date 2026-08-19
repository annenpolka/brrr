# cleat

Mint a durable fingerprint address from a `file:line` once; resolve it onto a later tree. The stored object is the cleat, not a locator string.

A leftover re-export is an **import relative to the leftover file**. `from .ops import add` in `src/calc.py` names dest `src/math/ops.py`. `from src.math import calc` at module level follows. `io.fs` ⊂ `audio.fs` stays ambiguous. Extract-and-keep is identity. Leftover stubs lose; basename bait loses. The token may refuse.

## Install / run

```bash
chmod +x ./cleat
./cleat --help
./demo.sh
```

Requires Python 3. `git` is optional when both `--from-dir` and `--to-dir` are set.

## Interaction

```
cleat mint  [--from <ref> | --from-dir DIR] path:line     # once
cleat resolve [--to <ref> | --to-dir DIR] cleat1.…        # later tree
cleat show cleat1.…
cleat id --repo /path
```

`cleat resolve` refuses `path:line`. That is the point.

`--to` must name an object that exists. Truncated `cleat1.…` tokens exit 1, like `show`. Origin mismatch exits 1 unless you pass `--any-repo`.

## Examples

Mint the line a review comment would have cited, store the token, throw away the SHA:

```bash
./cleat mint --repo ~/src/kizu --from b4e6a5d src/app.rs:529
# cleat1.eJyt…
```

Later, on today's tree, no path, no line, no SHA of origin:

```bash
./cleat resolve --repo ~/src/kizu --to HEAD cleat1.eJyt…
# src/app.rs:529  →  src/app/layout.rs:17   moved   1.00
```

Relative leftover after extract (`from .ops import` in leftover `src/calc.py`):

```bash
./cleat resolve --repo ~/src/relops --to HEAD cleat1.…
# moved  src/calc.py:4  →  src/math/ops.py:4  skipped leftover stub; basename bait
```

Extract-and-keep (body still at the minted path, also copied):

```bash
./cleat resolve --repo ~/src/keep --to HEAD cleat1.…
# same  src/calc.py:4  →  src/calc.py:4  1.000  skipped extracted copy
```

`resolve` will not take `src/app.rs:529`. Flags can sit on either side of a `cleat1.…` token.

# shunt

Mint a durable fingerprint address from a `file:line` once; resolve it onto a later tree. The stored object is the shunt, not a locator string.

A leftover re-export is an **import pointer**, not a substring of the enclosing function. Extract-and-keep is not a move: if the origin path still holds the implementation body, that path is the locus. If origin is a stub, follow the leftover's import of this name — even when the extract is not `oldstem/…`, and even when the pointer lives at module scope. Basename is not bait. Two identical dest copies with no leftover pointer are `ambiguous`. A missing `--to` ref is an error. A clipped token fails closed. A shunt carries a repo origin so it will not land on a stranger unless you pass `--any-repo`.

## Install / run

```bash
chmod +x ./shunt
./shunt --help
./demo.sh
```

Requires Python 3. `git` is optional when both `--from-dir` and `--to-dir` are set.

## Interaction

```
shunt mint    [--from <ref> | --from-dir DIR] path:line     # once
shunt resolve [--to <ref> | --to-dir DIR] shunt1.…          # later tree
shunt show shunt1.…
```

`shunt resolve` refuses `path:line`. That is the point.

`--to` must name an object that exists. Truncated `shunt1.…` tokens exit 1, like `show`.

## Examples

Mint the line a review comment would have cited, store the token, throw away the SHA:

```bash
./shunt mint --repo ~/src/kizu --from b4e6a5d src/app.rs:529
# shunt1.eJytU01v...
```

Later, on today's tree, no path, no line, no SHA of origin:

```bash
./shunt resolve --repo ~/src/kizu --to HEAD shunt1.…
# src/app.rs:529  →  src/app/layout.rs:17   moved   0.93
```

Extract-and-keep (body still at the minted path, also copied to a renamed package):

```bash
./shunt resolve --repo ~/src/keep --to HEAD shunt1.…
# same  src/calc.py:4  →  src/calc.py:4  1.000  skipped extracted copy src/math/ops.py:4
```

A leftover wrapper loses to the extract it actually imports, including a module-level shim:

```bash
./shunt resolve --repo ~/src/stub --to HEAD shunt1.…
# moved  src/calc.py:4  →  src/math/ops.py:4  0.910  skipped leftover stub; basename bait
```

`resolve` will not take `src/app.rs:529`. Flags can sit on either side of a `shunt1.…` token (`shunt --repo kizu --to HEAD shunt1.…`).

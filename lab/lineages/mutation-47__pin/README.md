# pin

Mint a durable fingerprint address from a `file:line` once; resolve it onto a later tree. The stored object is the pin, not a locator string.

A leftover re-export at the old path is not identity. **Extract-and-keep is not a move:** if the origin path still holds the implementation body, that path is the locus. **If origin is a stub, the extracted body wins** even when the landing is not `oldstem/…` (`src/calc.py` → `src/math/ops.py`, not `src/legacy/calc.py`). Two identical dest copies with no leftover pointer are `ambiguous`. A missing `--to` ref is an error. A clipped token fails closed. A pin carries a repo origin so it will not land on a stranger unless you pass `--any-repo`.

## Install / run

```bash
chmod +x ./pin
./pin --help
./demo.sh
```

Requires Python 3. `git` is optional when both `--from-dir` and `--to-dir` are set.

## Interaction

```
pin mint  [--from <ref> | --from-dir DIR] path:line     # once
pin resolve [--to <ref> | --to-dir DIR] pin1.…          # later tree
pin show pin1.…
```

`pin resolve` refuses `path:line`. That is the point.

`--to` must name an object that exists. Truncated `pin1.…` tokens exit 1, like `show`.

## Examples

Mint the line a review comment would have cited, store the token, throw away the SHA:

```bash
./pin mint --repo ~/src/kizu --from b4e6a5d src/app.rs:529
# pin1.eJytU01v...
```

Later, on today's tree, no path, no line, no SHA of origin:

```bash
./pin resolve --repo ~/src/kizu --to HEAD pin1.eJytU01v...
# src/app.rs:529  →  src/app/layout.rs:17   moved   0.93
```

Extract-and-keep (body still at the minted path, also copied to a renamed package):

```bash
./pin resolve --repo ~/src/keep --to HEAD pin1.…
# same  src/calc.py:4  →  src/calc.py:4  1.000  skipped extracted copy src/math/ops.py:4
```

A leftover wrapper loses to the extract even when the package was renamed:

```bash
./pin resolve --repo ~/src/stub --to HEAD pin1.…
# moved  src/calc.py:4  →  src/math/ops.py:4  0.910  skipped leftover stub; basename bait
```

`resolve` will not take `src/app.rs:529`. Flags can sit on either side of a `pin1.…` token (`pin --repo kizu --to HEAD pin1.…`).

# pin

Mint a durable fingerprint address from a `file:line` once; resolve it onto a later tree. The stored object is the pin, not a locator string.

A leftover re-export at the old path is not identity. Two identical dest copies are `ambiguous`, not walk-order `1.000`. A missing `--to` ref is an error. A clipped token fails closed. A pin carries a repo origin so it will not land on a stranger unless you pass `--any-repo`.

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

A pinfile of review bookmarks that survive a godfile split:

```bash
./pin mint --repo ~/src/kizu --from b4e6a5d --file review.pins --name seen src/app.rs:529
./pin resolve --repo ~/src/kizu --file review.pins
# seen  src/app.rs:529  →  src/app/layout.rs:17
```

`resolve` will not take `src/app.rs:529`. Flags can sit on either side of a `pin1.…` token (`pin --repo kizu --to HEAD pin1.…`).

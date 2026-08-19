# slip

Relocate a stale `file:line` address from one snapshot of a codebase onto another by fingerprint, not by VCS identity.

## Install / run

```bash
chmod +x ./slip
./slip --help
./demo.sh
```

Requires Python 3 and `git` (git is optional when both `--from-dir` and `--to-dir` are set).

## Interaction

```
slip --from <ref> [--to <ref>] path:line...
slip --from <ref> < compiler.log        # rewrite locations in a stream
slip --from-dir old/ --to-dir new/ path:line
```

Exit 0 on success. `--strict` exits 1 if a locator cannot even be read from the source snapshot. Confirmed deletions are successful answers, not errors.

## Examples

Map an address from before a file-split onto `HEAD`:

```bash
./slip --repo ~/src/kizu --from b4e6a5d --to HEAD src/app.rs:529
# src/app.rs:529  →  src/app/layout.rs:17   moved  0.92
```

Rewrite a compiler log, Python traceback, or CI path whose line numbers drifted:

```bash
rg 'error' /tmp/old-ci.log | ./slip --from ci-sha
#   --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
#   File "src/app/navigation.rs", line 22, in nearest_landing_forward
```

Compare two directories that do not share git history (a rewrite, a copy, a tarball):

```bash
./slip --from-dir old-python/ --to-dir new-rust/ src/calc.py:7 --porcelain
# edited	src/calc.py:7	src/math/sauce.py:3	0.71	line text drifted
```

Locators are bound against known paths in the source snapshot, so `Makefile:2`, `notes/file with spaces.txt:1`, and `src/weird:colon.py:1` parse. Deleted lines stay deleted; the note names the surviving neighborhood.

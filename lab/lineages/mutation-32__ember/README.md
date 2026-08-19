# ember (mutation-32)

Print leftover claims a diff just made false. Facts are **typed**: a version is the full token, a calendar month is not an integer, a quoted JSON key is a binding.

A *fact* is a bound name/value, rename, or polarity flip in a unified diff. An *afterimage* is a comment, doc, test, string, or config line in the destination tree that still asserts the old fact.

Parents: **zanei** (candidate-07) could not see JSON-only hunks. **nagori** (reimpl-03) saw `"version": "0.3.0"` then truncated the dest bind to `0.3` and threw the prose leftover away.

## Install / run

Requires Python 3.10+ and `git` on `PATH`. No other dependencies.

```bash
chmod +x ./ember ./demo.sh
./ember --help
./ember self-test
./demo.sh          # fixture tests including destroyer JSON + date cases; exits 0
```

Exit codes: `0` none found, `1` afterimages found, `2` usage/error.

Default comparison is `HEAD` → working tree (staged + unstaged), like `git diff HEAD`. Output is human text; `--tsv` and `--json` are pipeable.

## Examples

**1. JSON-only version hunk (zanei was silent; nagori then dropped the leftover).**

```bash
git diff -- plugin.json | ./ember --diff - -C .
```

```
ember: 1 afterimage  diff → worktree

FACT version: 0.3.0 → 0.7.0   plugin.json:3
   84 docs    README.md:1   plugin version 0.3.0, hook timeout 10 seconds.
```

**2. What else did this edit make untrue?**

```bash
./ember
```

```
ember: 6 afterimages  HEAD → worktree

FACT HOOK_TIMEOUT: 10 → 30   src/config.py:1
   84 docs    docs/help.md:1   timeout default is 10
```

`shipped 2024-10-01` is not an afterimage of timeout 10.

**3. Historical range / someone else's patch.**

```bash
./ember v0.3.0 v0.7.0
git show HEAD | ./ember --diff -
```

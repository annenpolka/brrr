# wraith

Find names whose last definition died in git but which still linger in docs, configs, scripts, comments, and strings.

Compilers catch unbound identifiers in typed code. Wraith is the type-checker for the untyped fringe.

## Install / run

```bash
chmod +x wraith
./wraith                 # deaths from recent history vs the working tree
./wraith --self-test     # ugly fixture (spaces in names, leftover Makefile, kebab echo)
./demo.sh                # self-test + dogfood
```

Requires Python 3.10+ and `git`. No other dependencies.

Exit codes (grep-like): `0` clean, `1` error, `2` holdouts found. `--ok-exit` always exits 0 on success.

## Examples

Scan whatever died in recent history and still has leftover mentions:

```bash
./wraith -C ~/src/my-repo
```

Two-tree, good on a branch: names defined on `main` that are gone now but still mentioned:

```bash
./wraith main
./wraith --range main..HEAD --porcelain
# path:line:name:why:death
```

After a refactor-heavy repo, hide the planning diary and keep the leftovers that can still bite:

```bash
./wraith --ignore 'plans/**' --ignore 'docs/adr/**'
```

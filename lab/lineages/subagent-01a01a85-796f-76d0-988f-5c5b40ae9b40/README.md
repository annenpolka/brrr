# wraith

Find names whose last definition died in git but which still linger in docs, configs, scripts, comments, and strings.

Compilers catch unbound identifiers in typed code. Wraith is the type-checker for the untyped fringe.

## Install / run

```bash
chmod +x wraith
./wraith                 # recent deaths vs the working tree
./wraith --self-test     # built-in ugly fixture
./demo.sh                # self-test + dogfood
```

Requires Python 3.10+ and `git`. No other dependencies.

Exit codes (grep-like): `0` clean, `1` error, `2` holdouts found.

## Examples

Scan whatever died in recent history and still has leftover mentions:

```bash
./wraith -C ~/src/my-repo
```

Two-tree: names defined on `main` that are gone in the worktree but still mentioned:

```bash
./wraith main
```

Machine-readable, pipeable:

```bash
./wraith --range main..HEAD --porcelain
# path:line:name:why:death
```

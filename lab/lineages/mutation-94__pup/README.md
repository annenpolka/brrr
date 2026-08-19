# pup

Covering predicates in; occupancy eras out. **No `sh`.**

`ditto` emits COPY vs FOLLOW and pastes `held exists DEST` / `--follow exists OLD`. `ditto A B | sh` is paste. held does not parse `--follow`. dest existence is also TRUE for a unique birth.

`ditto A B | pup` occupies **those copy/follow predicates**. `git mv` is FOLLOW (identity eras). `cp` is COPY (dest is the extra holder). stdin is ditto/held/berth-shaped covering lines; or `pup A B` classifies two trees internally.

Not `git diff -C`. Not a third ambit.

## Install / run

```bash
# from this directory
./pup --help
./demo.sh 0
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `pup` onto your `PATH` if you want. `ditto` is optional: the pipe is the primitive; `pup A B` is the same covering without spawning ditto.

Exit 0 iff a copy/follow dest still holds at the last sample, 1 if none hold, 2 tool error.

## Examples

**1. `cp` covering is dest occupancy. `git mv` is identity occupancy.**

```bash
ditto A B | pup
pup -C repo HEAD~1 HEAD
```

```
# copy a.rs → b.rs  (repo, 3 commits, first-parent, copy)
       copy: a.rs → b.rs
FALSE  1 commit
TRUE   2 commits  holders: b.rs
now=TRUE  true=2/3
```

```
# follow 'old name.txt' → 'new name.txt'
       follow: old name.txt → new name.txt
TRUE   …  holders split on the move
```

**2. A recorded copy (kizu C056). Pipe, not paste.**

```bash
ditto -C kizu 5671a72^ 5671a72 | pup
ditto -C kizu --walks 5671a72^ 5671a72 | pup
pup -C kizu --full 5671a72^ 5671a72
```

Git recorded `C056 src/init.rs → src/init/install.rs`. ditto's walk is `held exists src/init/install.rs` — the paste `sh` would run. pup occupies the **copy**, names the source, and walks dest as the extra holder.

`--full` is TRUE from 5671a72 (12 commits). First-parent dest occupancy starts at the merge (`true=5/24`).

**3. A unique birth is not a pup dest. A rename is FOLLOW.**

```bash
ditto -C sitbone 14b1d6e^ 14b1d6e | pup
ditto -C kizu 4e37f16^ 4e37f16 | pup --full
```

FocusRiverView is `grep FocusRiverView` — not copy/follow; pup hints `held`. kizu R100 is one follow identity (`true=187` full), never a copy.

## Flags that matter

| flag | meaning |
| --- | --- |
| `-C` / `--repo` | repository (else stdin `-C`, else cwd) |
| `--rev` | occupancy tip (default `HEAD`; covering event is not the tip) |
| `--full` | every reachable commit, not first-parent |
| `--origin` | name dest-add behind a first-parent merge (**default**; C056 = `5671a72`) |
| `--no-origin` | dest-existence boolean only (v1) |
| `--copy-only` / `--follow-only` | keep one covering kind |
| `--json` / `--oneline` / `--revs` | machine output |
| `A B` | classify those two trees (ditto invoked internally) |

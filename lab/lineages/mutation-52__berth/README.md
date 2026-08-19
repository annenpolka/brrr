# berth

Occupancy of a **file identity**. A rename is one berth, not a path death plus a birth.

`held` compresses a boolean. `roost`/`perch` split a still-TRUE run when the witness set changes — but `exists PATH` cannot, because the holder *is* the path. `berth --follow` (default for exact `exists`) walks git rename records both ways: query the old name or the new name, get the same roost. Occupancy stays TRUE; holders still split (`old name.txt` → `new name.txt`).

`--no-follow` is path occupancy (ancestor roost). `--boolean` is ancestor `held`.

## Install / run

```bash
# from this directory
./berth --help
./demo.sh 0
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `berth` onto your `PATH` if you want.

Exit codes: `0` predicate holds at the last sample (HEAD, or the working tree with `--now`), `1` it does not, `2` tool error.

## Examples

**1. A rename is one identity.** (`exists` without `--follow` reports a death and a birth.)

```bash
berth exists 'old name.txt'
berth --no-follow exists 'old name.txt'
berth exists 'new name.txt'
```

```
identity: old name.txt → new name.txt
TRUE  3 commits  holders: old name.txt
TRUE  4 commits  holders: new name.txt
       + new name.txt
       - old name.txt
now=TRUE  eras=2  boolean=1  holder_splits=1
```

`git log --follow` only walks backward from a name that exists at HEAD. `berth` follows **forward** from a dead name too.

**2. A real rename `git log -- PATH` splits in two.** (kizu)

```bash
berth --full exists docs/deep-research-ai-agent-hooks.md
berth --full exists deep-research-ai-agent-hooks.md   # dead name; same identity
berth --full --no-follow exists deep-research-ai-agent-hooks.md
```

`--no-follow` on the old path: TRUE 13 then FALSE 174 (path death). `--follow` on either name: TRUE 187, one holder split at `R100`, kind `move` (not a ghost: the file still exists). First-parent dest occupancy starts at the merge; origin names `321a830 as deep-research-ai-agent-hooks.md`.

**3. A copy is not a rename. Ghost occupancy is still grep.**

```bash
berth exists alpha.txt          # copy to beta.txt does not change identity
berth grep preact-zero-mock     # README-only tenure is still a ghost
berth --full grep FocusRiverView
```

`--follow` is for `exists` of an exact path. `grep` already splits when the holder set changes (TOKEN_B copy/move). A glob is not an identity.

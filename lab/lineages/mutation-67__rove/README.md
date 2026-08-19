# rove

Occupancy of a **token along a file identity**. A path-limited grep survives `git mv`.

`berth --follow` occupies the file. `grep -- PATH` still dies with the old name, because the pathspec is the current path. `rove grep --follow -- PATH` greps whatever name that identity has at each commit: query the old name or the new name, get the same roost. Occupancy of the token stays TRUE across the rename; holders still split (`old name.txt` → `new name.txt`).

`--no-follow` is ancestor path-limited grep. Tree-wide `grep PATTERN` (no path) is unchanged. `--boolean` is ancestor `held`. A copy is not a rename. Delete-then-recreate is a new identity.

## Install / run

```bash
# from this directory
./rove --help
./demo.sh 0
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `rove` onto your `PATH` if you want.

Exit codes: `0` predicate holds at the last sample (HEAD, or the working tree with `--now`), `1` it does not, `2` tool error.

Default: exact `exists` and exact path-limited `grep` follow. Globs and tree-wide grep do not.

## Examples

**1. Path-limited grep survives a rename with spaces.** (`--no-follow` dies with the old name.)

```bash
rove grep ghost -- 'old name.txt'
rove --no-follow grep ghost -- 'old name.txt'
rove grep ghost -- 'new name.txt'
```

```
identity: old name.txt → new name.txt
TRUE  3 commits  holders: old name.txt
TRUE  1 commit   holders: new name.txt
       + new name.txt
       - old name.txt
now=TRUE  eras=2  boolean=1  holder_splits=1
```

`git log -G ghost -- old name.txt` stops at the rename. rove from the old name continues as the dest.

**2. A real rename `git grep -- old` splits in two.** (kizu)

```bash
rove --full grep -F '10 の AI' -- docs/deep-research-ai-agent-hooks.md
rove --full grep -F '10 の AI' -- deep-research-ai-agent-hooks.md   # dead name; same roost
rove --full --no-follow grep -F '10 の AI' -- deep-research-ai-agent-hooks.md
```

`--no-follow` on the old path: TRUE 13 then FALSE 174 (path death), and a hint to `--follow`. `--follow` on either name: TRUE 187, one holder split at `R100`, kind `move`. First-parent occupancy starts at the merge; origin names `321a830 as deep-research-ai-agent-hooks.md` from **either** name (the merge added dest as A, so first-parent never recorded R).

**3. A copy is not a follow. A split is not a follow. Ghost occupancy is still tree-wide grep.**

```bash
rove grep TOKEN_B -- alpha.txt          # copy to beta.txt does not change identity
rove --full grep parse_diff_git_header -- src/git.rs   # split into parse.rs is tenure, not this
rove grep preact-zero-mock              # README-only tenure is still a ghost
```

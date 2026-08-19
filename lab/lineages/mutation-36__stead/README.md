# stead

Occupancy eras that refuse to lie about the lattice.

`held` compresses a boolean. A timeout, a depth-1 clone, a binary blob, and
`git log --reverse` across a merge diamond all come out as TRUE or FALSE —
so a failed probe looks like “never held,” and a graft looks like birth.
`stead` keeps the same verb (contiguous eras of a predicate) and gives the
sample five statuses: **TRUE / FALSE / UNKNOWN / SHALLOW / EMPTY**.

- `--now` on a commit-less dirty tree answers the **filesystem**.
- A timeout or a broken regex is **UNKNOWN**, not FALSE.
- A depth-1 clone or a `--limit` tail is **SHALLOW**, not birth and not never-held.
- A token that lives only in a NUL/binary blob is **EMPTY**, not air.
- `--full` compresses along **parent edges**. `git log --reverse` order is `--list`.
- `exists PATH` is one `cat-file` batch. `glob PATTERN` is a different cost class.

`--boolean` is a lossy downcast to ancestor `held` (raw TRUE stays; everything
else becomes FALSE). Default output is TSV on a pipe, human on a tty.

## Install / run

```bash
# from this directory
./stead --help
./demo.sh
```

Requires Python 3.10+ and `git`. No other dependencies.

Exit codes: `0` last sample is TRUE, `1` FALSE, `3` UNKNOWN / SHALLOW / EMPTY
dominates, `2` tool error.

## Examples

**1. A dirty README in a repo that has no commits.** (`held --now` aborted on HEAD.)

```bash
stead --now -C empty-dirty exists README.md
```

```
TRUE      1 sample   WORKTREE
       uncommitted working tree
       witnesses: README.md
now=TRUE  true=1/1 samples  walk=filesystem
```

**2. A depth-1 clone is not birth.**

```bash
stead exists CLAUDE.md          # in a --depth 1 clone of kizu
```

```
SHALLOW   1 commit   9349dc5
       graft/horizon: not birth, not never-held
now=SHALLOW  walk=first-parent  shallow=1
```

Full kizu first-parent still names the merge (`0ea3916`). `--full` names the
topic birth (`e1098c8`). Depth-1 does not steal either story.

**3. A timeout is a hole in the walk, not occupancy death.**

```bash
stead --timeout 0.25 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
```

```
TRUE      1 commit   fast only
UNKNOWN   1 commit   slow present
       witnesses: (timeout)
       failed probe, not FALSE
TRUE      1 commit   slow gone
now=TRUE  unknown=1
```

Pipe the TSV:

```bash
stead --tsv exists .github/workflows/ci.yml
# status  count  start  end  start_iso  end_iso  chain  witnesses
```

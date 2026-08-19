# sheaf

Shortest covering set of predicates that distinguish two git trees — plus the `held` / `perch` command lines that walk them.

`tell` lists unary questions that split two snapshots. `sheaf` answers a different question: **which smallest set of those questions covers the whole delta, and what do I paste to walk each one?**

Not `git diff --stat`. Diff lists files. `tell --cover` still prints a catalog. `sheaf` prints a **set** and ready-to-run walks.

## Install / run

```bash
# from this directory
./sheaf --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `sheaf` onto your `PATH` if you want. Generated walk lines assume `held` and `perch` are on `PATH`.

Exit codes: `0` a sheaf was found, `1` the trees are identical (or nothing distinguished them), `2` tool error.

Refs may be any tree-ish: `HEAD~1`, a sha, a tag, `:worktree`, `:index`.

## Examples

**1. A file appeared. What set covers the birth, and how do I walk it?**

```bash
sheaf -C sitbone 14b1d6e^ 14b1d6e
```

```
sheaf  (shortest set whose witnesses union the delta)
  B   19  grep FocusRiverView                               1 file
  B   15  grep onSettings                                   2 files

walk  (paste into a shell)
  held -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
  perch -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
```

An island off first-parent (FocusRiverView vs HEAD) gets `--full` on every walk so you do not rediscover held's empty `git log -- PATH`.

**2. An island vs HEAD. `git log -- PATH` is empty. The sheaf still names the dead type and prints `--full`.**

```bash
sheaf -C sitbone 14b1d6e HEAD
sheaf --walks -C sitbone 14b1d6e HEAD
```

`--walks` prints only the command lines. `--walk held` omits perch. `--held` prints the sheaf in held language, one predicate per line.

**3. Working tree vs HEAD.**

```bash
sheaf HEAD :worktree
```

Walk lines pick up `--now` so `held` samples the dirty tree too.

## Flags that matter

| flag | meaning |
| --- | --- |
| `--walks` / `--sh` | only command lines |
| `--walk held` / `--walk perch` | which tools to emit |
| `--full-walks` | force `--full` on every walk |
| `--no-walks` | sheaf only |
| `--held` | held-language predicates (the set) |
| `--predicates` | also print tell's ranked catalog |
| `--limit N` | max size of the sheaf |
| `--budget N` | max sum of held-string lengths |
| `--json` | `sheaf`, `walks`, `unexplained` |

# tell

Shortest predicates that distinguish two git trees — the reverse of `held`.

`held` assumes you already know the predicate (`exists PATH`, `grep PATTERN`) and asks *when was this true?*. `tell` assumes you do not. You supply **two commits or two trees**. It emits the shortest `exists` / `grep` / `path` / `content` predicates that are true on one side and false on the other.

Not `git diff --stat`. Diff lists what changed. `tell` lists the smallest questions you could ask that would tell the two trees apart — the questions you would then hand to `held`.

## Install / run

```bash
# from this directory
./tell --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `tell` onto your `PATH` if you want.

Exit codes: `0` predicates found, `1` the trees are identical (or nothing distinguished them), `2` tool error.

Refs may be any tree-ish: `HEAD~1`, a sha, a tag, `:worktree`, `:index`.

## Examples

**1. What name appeared with this file?** (sitbone's `FocusRiverView.swift` — `git log -- PATH` is empty after it died)

```bash
tell -C sitbone 14b1d6e^ 14b1d6e
```

```
cover  (shortest set whose witnesses union the delta)
  B   19  grep FocusRiverView                               1 file
  B   15  grep onSettings                                   2 files

TRUE on B only  (14b1d6e)
  exists   exists *FocusRiverView*
  grep     grep FocusRiverView
```

**2. A feature landed; the slice commit already said "breakpoint". What still distinguishes the implementation?**

```bash
tell -C voidtrace 66d6fa1 6e3368b
```

```
cover
  B   34  grep -F finite-breakpoint-analysis               10 files
  B   22  grep -F run-breakpoint                            5 files
  B   27  exists *finite-breakpoint.*                       3 files
```

`grep breakpoint` is *not* emitted: it is already true on both trees.

**3. You do not speak the repo. Two trees still name the policy.**

```bash
tell -C tenaoshi 70b450d^ 70b450d
tell --held --kind grep -C tenaoshi 70b450d^ 70b450d
```

```
  B   15  grep -F MAN-023                                   4 files
  B   13  grep -F '第一級'                                     3 files
```

Pipe into held's language:

```bash
tell --held HEAD~1 HEAD | head
# exists *FocusRiverView*
# grep FocusRiverView
```

Working tree vs `HEAD`:

```bash
tell HEAD :worktree
```

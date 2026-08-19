# thatch

Two git trees in. A **covering set of path-conditions** out, then the **tenure of those stacks**.

`sheaf` covers a delta with grep/exists and prints `held`/`perch` walks. `tenure` occupies one user-pinned `FILE:LINE`. Piped, they still cover with tokens. The if-text lives on the guard. Occupancy of a path-condition is the lines that **run under** the stack.

thatch's object is the *set of stacks* that distinguish the trees — including a file move as **one** stack whose holders changed — then the eras each stack occupied.

## Install / run

Python 3.10+, stdlib only, `git`. Vendored `whenline` parsers from candidate-20 / tenure.

```bash
chmod +x ./thatch
./thatch --selftest
./demo.sh
./thatch -C /path/to/repo HEAD~1 HEAD
./thatch -C /Users/annenpolka/ghq/github.com/annenpolka/kizu 3b3e0a9^ 3b3e0a9
./thatch -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --limit 6 14b1d6e HEAD
```

Exit 0 if the trees differ, 1 if they are identical, 2 on error.

## Examples

```bash
# kizu: the unquoted-form stack moved with the function. One member, not two exists.
./thatch -C kizu 3b3e0a9^ 3b3e0a9

# sitbone island: git log -- FocusRiverView.swift is empty. The covering
# path-condition on A is reserved under --limit, occupy walks --full.
./thatch -C sitbone --limit 6 14b1d6e HEAD

# dirty resurrection
./thatch HEAD :worktree
```

## What is *not* this

- `sheaf A B` then paste a grep into `held` / `perch` — tokens, not stacks.
- `tenure FILE:LINE` — you already know the pin.
- `when` at each side — two snapshots, no covering set, no eras.

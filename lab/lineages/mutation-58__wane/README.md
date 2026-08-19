# wane

Two git trees in. The **exclusive-A path-condition stacks** (what died), then the **tenure of those stacks**.

`thatch` covers a delta with a mixed budget: 1–2 exclusive-A slots, exclusive-B births, leftover AB moves and `else` spreads. `sheaf` covers with grep/exists. `tenure` occupies one user-pinned `FILE:LINE`. Piped, they still mix what died with what was born.

wane's object is only the stacks true on A and false on B. Invert the trees to ask what was born. Occupancy of a path-condition is the lines that **run under** the stack; island files that `git log -- path` cannot see still get eras.

## Install / run

Python 3.10+, stdlib only, `git`. Vendored `whenline` parsers from thatch / tenure / candidate-20.

```bash
chmod +x ./wane
./wane --selftest
./demo.sh
./wane -C /path/to/repo HEAD~1 HEAD
./wane -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --limit 6 14b1d6e HEAD
./wane -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --also-changed --limit 6 14b1d6e HEAD
./wane -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone 70ec7df^ 70ec7df
```

Exit 0 if the trees differ, 1 if they are identical, 2 on error.

## Examples

```bash
# sitbone island: git log -- FocusRiverView.swift is empty.
# Default cover is the dead stacks, not HEAD camera births or AB else.
./wane -C sitbone --limit 6 14b1d6e HEAD

# leftover stays on the deleted file. surviving-file deaths: --also-changed
./wane -C sitbone --limit 6 14b1d6e HEAD
./wane -C sitbone --also-changed --limit 6 14b1d6e HEAD

# invert: what HEAD has that 14b1d6e lacks (births, asked as deaths)
./wane -C sitbone --limit 6 HEAD 14b1d6e

# dirty worktree: resurrection is a birth. Invert to name it.
./wane HEAD :worktree          # empty if nothing died
./wane :worktree HEAD          # uncommitted stacks that would die on reset
```

## What is *not* this

- `thatch A B` — mixed covering of deaths, births, and holder moves.
- `sheaf A B` then paste a grep into `held` / `perch` — tokens, not stacks.
- `tenure FILE:LINE` — you already know the pin.
- Swapping trees is the birth question. There is no `--also-b` mixed budget.

# twain

A unified diff is two patches: an **oracle-half** (tests, goldens, snapshots) and a **production-half**. `twain` splits them, occupies each half against a tree, and reports whether the oracle-half **binds** the production-half.

`git apply --check` and patch occupancy tools treat a commit as one before→after claim. A mixed APPLIED hides tests-without-code, code-without-tests, and tests that never mention the change.

## Install / run

Python 3.10+, git, stdlib only.

```bash
chmod +x ./twain
./twain --help
./twain --selftest
./demo.sh
./twain HEAD
./twain HEAD --against HEAD^          # sandwich
./twain main...HEAD
./twain --emit oracle HEAD            # tests-only patch
./twain --emit prod HEAD
git show | ./twain --patch -
```

Exit: `0` LOCKED or EMPTY, `1` unlocked (MUTE/LOOSE/HOLLOW/PENDING/ahead), `2` SEAM/SPLIT, `3` error. `--report-only` forces `0`. `--json` / `--tsv` / `--porcelain` compose.

## Statuses

| status | meaning |
| --- | --- |
| LOCKED | both halves occupy the tree, and oracle tokens bind production tokens |
| LOOSE | both occupy; bind empty (tests that do not mention the change) |
| MUTE | production occupies; no oracle half |
| HOLLOW | oracle occupies; no production half |
| PROD_AHEAD / ORACLE_AHEAD | one half occupies, the other is still PENDING |
| PENDING | neither half occupies |
| SEAM | a hunk *interleaves* oracle and production (not a single cut) |
| EMPTY | docs/ignore only |

A `#[cfg(test)] mod tests` suffix in the same hunk is a **cut**, not a seam: twain splits it.

## Examples

**1. Tests-only commit is HOLLOW** (tenaoshi `4878b75` — contract oracles, no production):

```bash
./twain 4878b75 -C /path/to/tenaoshi --against 4878b75
# twain  HOLLOW  kind=ORACLE  prod=EMPTY(0)  oracle=APPLIED(14)
```

**2. Feature with in-file tests is LOCKED after the split** (kizu `04adde1`):

```bash
./twain 04adde1 -C /path/to/kizu --against 04adde1
# LOCKED  prod=APPLIED(50)  oracle=APPLIED(8)  bind=JSX TSX JsTsDialect …
./twain --emit oracle 04adde1 -C /path/to/kizu   # tests.rs + js_ts.rs test module + e2e
./twain --emit prod 04adde1 -C /path/to/kizu     # the other half of js_ts.rs
```

**3. Production-only PR is MUTE** (sitbone `#9` notch controls):

```bash
./twain 094769d -C /path/to/sitbone --against 094769d
# MUTE  prod=APPLIED(4)  oracle=EMPTY  Sources/SitboneUI/NotchOverlay.swift
```

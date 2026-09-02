# Destroyer: silentadd

Target: lineages/candidate-silentadd (worktree candidate-silentadd-silentadd)
Date: 2026-09-02

## Attacks

| case | result |
| --- | --- |
| `aaa blobtree/ zzz` + `blobtree` scan 0 | `silent yes`, remain `blobtree/`, hide `aaa` |
| same list `--scan pos` | `add fail`, `silent no`, hide `none` |
| only `blobtree/` (pos 0) | `scan0 hit`, `add fail` |
| unseen `pkg` + `pkg/__init__.py` behind `000` | `silent yes`, remain `pkg/__init__.py` |
| specimen-017 `B` `B` | `collision absent`, `silent no` |
| parent file `pkg` + add `pkg/mod.py` | `add fail`, remain `pkg` kind `file` |
| unsorted `zzz blobtree/ aaa` | `ordered no`; collision still listed |
| missing `--file` | clean `silentadd:` error, rc=1 |
| `--scan nope` | rc=2 |

## Primitive

Insert-ok plus remaining file/dir collision plus scan cursor still holds on
an unseen name (`pkg`) and is refused on extras names with no `/`.

## Decision

**KEEP**. Unsorted lists are flagged, not repaired. Do not KILL.

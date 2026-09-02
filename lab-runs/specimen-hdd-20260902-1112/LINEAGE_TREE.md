# Lineage tree (KEEP survivors)

Run: specimen-hdd-20260902-1112
Parent `main`: `432f954` (no product merge)

```
specimen-013 leftover import bind (hdd-identity)
  └─ candidate-bind / bindname    DESTROYER_20 KEEP  119/119  PATH tomorrow

specimen-009 order-dependent start (hdd-order)
  ├─ candidate-leakorder / leakorder  DESTROYER_4 KEEP  24/24  drawer (FAIL unseen Box.bucket name)
  └─ candidate-ordleak / ordleak      DESTROYER_4 KEEP  35/35  drawer (named Box.bucket)

CRD listMapKey × omitempty JOIN
  └─ candidate-tagjoin / tagjoin      DESTROYER_4 KEEP  52/52  drawer

pytest-xdist completed-only hang
  └─ candidate-emptyunit / emptyunit  DESTROYER_4 KEEP  39/39  remember hang
```

Honor-KILL (not on tree as tools): envlayers, reimpl-emptyunit-2, leftover-flag TSV THIN_WRAPPER harvests.

Worktrees: `lineages/*.worktree` and isolated `make_worktree.sh` trees. Do not merge onto `main`.

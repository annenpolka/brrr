# DESTROYER hunkland 2

Date: 2026-09-02 16:09 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0387 (worker destroyer-hunkland-2, CLAIMED 15:40, no mutation landed)

Target (archive, bytes unchanged since first destroyer):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-hunkland/hunkland`

sha256 `d7cdac3617dc2f55f25884b9a8dd29e10fbf98f8f6b155c016e26bde0f432b7f` (5809 bytes). **IDENTICAL** to `DESTROYER_hunkland.md`. No `MUTATE.md`. Parent `main` is `432f954`; archive untracked; not merged. Host Python 3.14.5. `git` / `patch` were not executed as the product.

First destroyer **MUTATE**. Required (1) header is the `+` body line or refuse `old_count!=0`; (2) land is this hunk's insert, not opcode 0; (3) aligned requires content. If mutation cannot do (1)+(2)+(3), later destroyer should KILL. Mutation never queued. Bytes unchanged. First MUTATE is not protection. Decision: **KILL**.

CLI:

```text
CLI=lineages/candidate-hunkland/hunkland
FIX=lineages/candidate-hunkland/fixtures
```

Host-executed against the archive. Do not grow a git-apply reimplementation. Do not send patch theater back to R1.

---

## What still works

Owned empty-range unique insert still names header 3 / land 2 / verdict mis-indexed, rc=0:

```text
header	3
header_line	second
land	2
land_line	inserted
apply_exit	0
match	no
verdict	mis-indexed
```

That is the first destroyer's happy path. It is also `diff -u` plus a hand join.

---

## Honor-KILL leftovers (still fire)

### 1. Context hunk is still `mis-indexed`, never `hunk-not-empty`

`--hunk '@@ -1,3 +1,4 @@'` on orig vs aligned result (insert at line 3 of a 4-line file):

```text
header	1
header_line	first
land	3
land_line	inserted
verdict	mis-indexed
rc=0
```

`old_count=3` is not refused.

### 2. `land` is still opcode 0

Orig `first\nsecond\nthird\n` plus a leading replace `CHANGED` and trailing insert: land=1 `CHANGED`, not the hunk insert. `verdict mis-indexed`, rc=0.

### 3. `apply_exit` is still a caller sticker

Owned leftover plus `--apply-exit 1`: `verdict apply-failed`, `match no` still printed, rc=0. The sticker overrides `mis-indexed`. Apply is not observed.

`header` is still hunk `+N`. `find_lands` is still `SequenceMatcher` first insert/replace. `HUNK_RE.search` still takes the first `@@`.

---

## Primitive

Reality-stripped operation: regex first `+N` as header; first SequenceMatcher insert/replace as land; stamp caller `--apply-exit`; print `mis-indexed` when they disagree.

Nearest ordinary workflow: `diff -u orig result` already shows where `inserted` appeared. Observable capability lost if hunkland vanishes: **none** beyond that hand join.

Honor KILL. Do not mutate. Reimpl of this primitive is not a survivor. Archive stays under `lineages/candidate-hunkland/`.

KILL

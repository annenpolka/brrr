# MUTATE silentadd (no-op / leftover already the primitive)

Date: 2026-09-02
Job: job-0344
Worker: mutate-silentadd
Queue: READY_MUTATE

Target: `lineages/candidate-silentadd/silentadd`
Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-silentadd-silentadd`
Branch: `specimen-hdd/candidate-silentadd-silentadd`
Commit: `af669acd018613698c999e0721adfbbf0b0d44ea`

CLI sha256 (before = after): `7f9d2b8e721b8006058fa0071b3c4d5f2f3d1253de875b78ba3df28fb52c3f8a` (7536 bytes)

Archive `silentadd` and worktree `silentadd/silentadd` are byte-identical. No CLI patch. Not merged to `main`. Parent tree stays on `main`.

From DESTROYER_silentadd.md: **KEEP**. Leftover named by the job: collision after add-ok / scan cursor. Kill condition: `still prefix walk`.

## Observation

The KEEP leftover is already honest. `inspect()` is a prefix-walk from a cursor plus full-list remainder membership:

1. `insert_pos` = first index where `entry >= NAME` (sorted insertion).
2. Directory-prefix walk from `scan_start` (default `0`, or `pos`): **break** on the first entry that does not `startswith(prefix)`; **hit** if `entry` is `prefix/` or `prefix/...`.
3. `remain` = all `NAME/` children, plus same-path file if `NAME` has a trailing slash, plus parent files of `NAME`. This scan is the whole list, not the cursor.
4. `add ok` iff the cursor walk missed and there is no parent-file / same-path hit.
5. `silent yes` iff `add ok` and `remain` is non-empty.
6. `hide` = the first non-prefix entry that aborted the walk; `scan0` / `scan_pos` replay the same walk from 0 vs `insert_pos`.
7. Unsorted input sets `ordered no` and is not repaired (destroyer KEEP).

Owned specimen-014 (`aaa blobtree/ zzz`, name `blobtree`, `--scan 0`):

```
add	ok
collision	present
remain	blobtree/	dir
hide	aaa
scan0	miss
scan_pos	hit
silent	yes
```

`--scan pos`: `add fail`, `silent no`, `hide none`. Only `blobtree/` (insert_pos 0): `scan0 hit`, `add fail`. Unseen `pkg` behind `000`: `silent yes`, remain `pkg/__init__.py`. specimen-017 `B` `B`: `collision absent`, `silent no`.

Host reconstruction of those eight columns (prefix-walk + remainder membership) matched `inspect()` on 18/18 cases, including libgit2 #7160's `another blob` / `blobtree/conflict` / `some blob`, the single-prior `blobtree/conflict` (scan-0 finds it), `blobtree-extra` then `blobtree/foo` (walk continues; both cursors hit), and unsorted `zzz blobtree/ aaa`.

`python3 -m unittest tests.test_silentadd` 14/14. Existing `demo-1.log` / `demo-2.log` byte-identical (CLI unchanged; demo not re-run).

## Scan-0 prefix-break is not a hole

The harvest object **is** that walk starting at 0. An earlier sibling that does not share the name prefix aborts the walk and hides a later `NAME/` child. Starting at `insert_pos` finds it. That is already printed (`hide`, `scan0 miss`, `scan_pos hit`, `silent yes`).

Current libgit2 `has_file_name` is the same loop (`memcmp` prefix, continue when `path[len] != '/'`, break when the prefix differs or the path is shorter). Starting that loop at 0 is the lying cursor; starting it at the insertion position is the known fix. Closing "scan-0 prefix-break" would erase the specimen.

What was checked and left alone:

- Specimen fixture `index_scan.py` uses `item > prefix + "\uffff"` and therefore **finds** `blobtree/` from 0 (`found_from_0 True`). Matching that range-scan would make `silent no` on the owned list and destroy the object. The TASK / harvest / destroyer describe prefix-break, not the fixture's `\uffff` bound. `add_reported_ok_if_start0` in the fixture is `not has_file_name(...) or True` (always true).
- `blobtree-extra` then `blobtree/foo`: silentadd and current libgit2 **continue** (`path[len] != '/'`). An older libgit2 break-on-non-slash, or git's `has_dir_name` confusion with characters `< '/'`, would make `--scan pos` miss too. That is a different object. Not copied.
- Parent-file / same-path hits ignore the cursor (README). That is `has_dir_name`, already listed, not a scan-0 miss.
- `rc=0` on `silent yes` is the lying add, not a detector. Changing it to rc=1 would be a different verb.
- Parsing `.git/index` or adopting PR 7332 is outside the research boundary.

CANDIDATE suggested mutations (git index, "sufficient scan start", refuse `add` when `ordered no`) either leave the research boundary, reprint `insert_pos` / `scan_pos`, or contradict the destroyer's unsorted KEEP.

## Decision

**No-op.** Bytes unchanged. Mutation cannot change this primitive without becoming a different object (git index, D/F characters `< '/'`, leftover-as-nonzero-exit, unsorted repair).

A later destroyer should **KEEP** (the join: add-ok from a named cursor + remaining file/dir collision) or **KILL** as a **THIN_WRAPPER of prefix-walk**. That walk plus remainder membership *is* the CLI. This cut does not thicken it. Kill condition `still prefix walk` holds; do not send THIN_WRAPPER back to R1 with “make this more novel.”

Does not rebuild libgit2. Does not parse a git index. Owned path lists only. No merge onto `main`.

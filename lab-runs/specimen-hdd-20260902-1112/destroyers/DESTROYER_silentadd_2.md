# DESTROYER silentadd 2

Date: 2026-09-02 15:35 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0359
Worker: destroyer-silentadd-2

Target (archive; mutate-silentadd already no-op):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-silentadd/silentadd`

sha256 `7f9d2b8e721b8006058fa0071b3c4d5f2f3d1253de875b78ba3df28fb52c3f8a` (7536 bytes, 241 lines).
Worktree `~/.grok/worktrees/annenpolka-brrr/candidate-silentadd-silentadd/silentadd/silentadd` is byte-identical. HEAD `af669acd018613698c999e0721adfbbf0b0d44ea`, branch `specimen-hdd/candidate-silentadd-silentadd`. Parent `main` is `432f954`; `git ls-tree HEAD silentadd` empty. Host Python 3.14.5. unittest 14/14. No git index, no libgit2. Not merged onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-silent-add` / specimen-014): report an insert that returned ok while a file/dir collision remained, including scan start. Kind: USEFUL_COMPOSITION. specimen-017 is extras/requires, not a path index.

First destroyer (`DESTROYER_silentadd.md`) **KEEP**: owned `aaa blobtree/ zzz` scan 0 is `silent yes`; `--scan pos` is `add fail`; only-dir is `scan0 hit`; unseen `pkg` silent; 017 `B` collision absent; parent-file blocks; unsorted flagged not repaired. First KEEP is not protection.

Mutate job-0344 (`MUTATE.md`) was a **no-op**. Kill condition `still prefix walk` already held. Bytes unchanged. This cut attacks that walk.

This candidate is a **THIN_WRAPPER of a directory-prefix walk from a cursor plus full-list remainder membership**. Host replica of that walk (no import of the module) is **byte-identical** to CLI stdout on 24/24 cases. `grep '^NAME/'` plus first-nonprefix abort already names remain/hide on the owned list. `silent` is `walk missed AND remain nonempty`. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-silentadd/silentadd
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-silentadd/fixtures
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not parse `.git/index` or adopt a C patch to escape THIN_WRAPPER. Do not send prefix-walk theater back to R1.

---

## What still works

Owned 014 and any other case where the caller already typed the ordered path list and the name.

```bash
python3 "$CLI" blobtree aaa 'blobtree/' zzz; echo rc=$?
```

```text
name	blobtree
index	aaa	blobtree/	zzz
insert_pos	1
scan_start	0
ordered	yes
add	ok
collision	present
remain	blobtree/	dir
hide	aaa
scan0	miss
scan_pos	hit
silent	yes
rc=0
```

`--scan pos`: `add fail`, `silent no`, `hide none`, rc=0. Only `blobtree/`: `scan0 hit`, `add fail`. Unseen `pkg` behind `000`: `silent yes`, remain `pkg/__init__.py`. specimen-017 `B` `B`: `collision absent`, `silent no`. Missing `--file` rc=1. `--scan nope` rc=2. unittest 14/14.

That is the first KEEP. It is also a prefix-break from 0 that aborts on `aaa`, plus `grep '^blobtree/'` for remainder. `silent yes` does not change rc.

---

## Implementation

Load-bearing body:

```python
# scan_dir_from co_names: rstrip, len, startswith
for item in entries[start:]:
    if not item.startswith(prefix):
        return None          # prefix-break
    if len(item) > n and item[n] == "/":
        return item          # dir hit

# remain = dir_prefix_hits (full list NAME/)
#         + same_path_hits + parent_file_hits
add_ok = dir_hit is None and not parent_hit and not same_hit
silent = add_ok and bool(remain)
```

`scan_dir_from.co_names` is `('rstrip', 'len', 'startswith')`. Source contains no `git`, no `.git/index`, no `libgit`. `remain_rows` walks the whole list, not the cursor.

### 1. THIN_WRAPPER of prefix-walk / scan-0

Independent reconstruction of insert_pos + prefix-break walk + remainder membership (no import) is **byte-identical** to CLI stdout on 24/24 cases: owned 014 scan 0 / pos / only-dir, unseen pkg, 017 extra name, parent-file, no-collision, unsorted, libgit2 #7160 `another blob` / `blobtree/conflict` / `some blob`, single-prior `blobtree/conflict`, `blobtree-extra` then `blobtree/foo`, same-path file, empty list, `--scan 99`, `--scan 1`, duplicate dirs, nested parent+child, trailing-slash name, unicode siblings, space in name, hyphen-continue, hyphen-unsorted, later-dir-only.

Nearest analog, host-executed, matches CLI `add` / `silent` / `hide` on those 24/24:

```python
for item in entries[start:]:
    if not item.startswith(prefix):
        hide = item; break
    if len(item) > n and item[n] == "/":
        hit = item; break
remain = [e for e in entries if e.startswith(prefix + "/")]
add_ok = hit is None and not parent and not same
silent = add_ok and bool(remain)
```

Owned 014 Unix:

```bash
printf '%s\n' aaa 'blobtree/' zzz > /tmp/014.txt
grep -E '^blobtree/' /tmp/014.txt
awk 'substr($0,1,8)!="blobtree" {print; exit}' /tmp/014.txt
```

```text
blobtree/
aaa
```

CLI `remain blobtree/` and `hide aaa` are those two commands. `add ok` is the walk from 0 missing. `silent yes` is remain nonempty and that miss. `scan0 miss` / `scan_pos hit` reprint the same walk from 0 vs `insert_pos`.

`remain` does not depend on `--scan`. Owned 014 and unseen pkg: remain rows identical under `--scan 0` and `--scan pos`; only `add` / `silent` / `hide` / `scan_start` move. Remainder membership is not a scan-cursor join. It is `grep '^NAME/'` (plus parent/same-path equality) of the list the caller already typed.

### 2. Scan-0 is the lying cursor, restated

Starting the walk at 0 is the harvest. Starting it at `insert_pos` is the known fix. The CLI prints both. That is two walks, not a new observation.

`--scan 99` on the owned list: walk is empty, `add ok`, `silent yes`, `hide none`, **rc still 0**. A cursor past the list is a quieter lie than scan-0. The detector does not detect; it labels the miss.

`--scan 1` equals `--scan pos` on 014 (insert_pos is 1). `--scan pos` is `insert_pos` as an integer the analog already computed (`first i where entry >= NAME`).

Specimen fixture `index_scan.py` uses `item > prefix + "\uffff"` and **finds** `blobtree/` from 0 (`found_from_0 True`). The CLI prefix-breaks and misses. Matching the fixture would make `silent no` and erase the object. The CLI is not the fixture's range scan. It is the prefix-break. `add_reported_ok_if_start0` in the fixture is `not has_file_name(...) or True` (always true). The analog already prints that constant.

`blobtree-extra` then `blobtree/foo`: walk **continues** (`item[n] != '/'`). Both cursors hit. `silent no`. That is current libgit2 `has_file_name`, not a remainder the analog missed.

### 3. Parent-file / same-path ignore the cursor

`pkg/mod.py` into `aaa pkg zzz`: `remain pkg file`, `add fail`, `silent no` for `--scan 0`, `pos`, and `99`. `scan0 miss` / `scan_pos miss` — the directory-prefix walk never sees `pkg` as `pkg/`. `add fail` is `parent_file_hits` equality on the full list. Hide moves with the cursor (`aaa` / `zzz` / `none`); remain does not. That is `has_dir_name`, already listed, not scan-0.

Same-path file `blobtree` vs name `blobtree/`: remain `blobtree file`, `add fail`. Equality, not a prefix-walk hit.

specimen-017 `B` `B`: no `/` child, no parent file. `collision absent`. The counterexample is "remainder membership is empty."

### 4. rc=0 is the lying add, not a detector

`silent yes` returns 0. `--scan pos` `add fail` also returns 0. Missing file rc=1. Bad scan / file+args rc=2. Empty stdin is a legal empty index: `add ok`, `collision absent`, `silent no`, rc=0. Exit status does not name the harvest. `test` of remain nonempty already would.

Unsorted `zzz blobtree/ aaa`: `ordered no`, `silent yes`, hide `zzz`. The KEEP leftover (flag, do not repair) is `all(entries[i] <= entries[i+1])`. It does not thicken the walk.

### 5. Not a git index. THIN_WRAPPER does not gain one

No `.git/index` parse, no stages, no `ok_to_replace`, no libgit2. The list is the world. Growing an index parser or adopting PR 7332 would be a new harvest, not a patch of `startswith`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Mutate already refused that thickening (bytes unchanged).

Hardcoded ceiling:

- `add` ↔ prefix-break walk from `--scan` missed, and no parent/same-path equality
- `remain` ↔ full-list `NAME/` children plus parent/same-path; cursor is a spectator
- `silent` ↔ `add ok` and remain nonempty
- `hide` ↔ first non-prefix abort of that walk
- `scan0` / `scan_pos` ↔ the same walk from 0 vs `insert_pos`
- `insert_pos` ↔ first `entry >= NAME`
- `ordered` ↔ adjacent `<=`; unsorted is flagged, not repaired
- default `--scan 0` is the lying cursor; `--scan 99` is an empty walk, still `silent yes`, rc=0
- fixture `\uffff` range-scan finds from 0; this CLI does not
- hyphen-prefix continues; older break-on-non-slash is a different object
- parent-file / same-path ignore the cursor
- 017 extra names with no `/` are `collision absent`
- no git index; no libgit2; rc=0 on the lying add

Honor KILL. Dreamer ancestry is not protection. First-destroyer KEEP is not protection once the join is shown to be labels on prefix-walk / scan-0 plus remainder membership. Mutate no-op is not protection. Kill condition `still prefix walk` holds.

Do not merge onto `main`. Do not parse a git index to mint a remainder. Archive stays under `lineages/candidate-silentadd/`. Worktree stays under `~/.grok/worktrees/annenpolka-brrr/candidate-silentadd-silentadd/`.

KILL

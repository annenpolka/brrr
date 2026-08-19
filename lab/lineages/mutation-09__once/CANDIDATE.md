# mutation-09 — once

## Primitive

If two current paths ever contained the same git blob, they are kin; that blob is the merge-base, and `git merge-file` is the port. Exact object identity only.

## Why this might not exist

`akin` (candidate-01) concluded exact-blob simultaneity was the wrong oracle because people copy, edit, then `git add`. It added git copy detection and same-basename similarity. Those heuristics invent a merge-base that never existed, so `--port` can splice unrelated edits.

The missed fact: **non-simultaneous exact identity is common and is already a real blob.** `SKILL_claude.md` is still `SKILL.md`'s previous object. `old-version/` chapters are still the pre-edit blob. `ash/*.md` snapshots still *are* an old chapter object. No similarity score required. Git never recorded those as copies-with-a-base; `once` does.

## How to run

```sh
./once -C <repo> --pretty
./once -C <repo> --frozen --pretty
./once -C <repo> --port FROM TO
./once -C <repo> --sync FROM
./once -C <repo> --check
./demo.sh
```

## Empirical transcript

### Before the improvement (v0.1: list + port + refuse non-kin)

Synthetic fixture: exact copy then drift, unicode path, frozen twin, currently-identical pair, nested git dir, echo-archive of an old blob. Similarity lookalike and copy-edited-before-add are **not** kin (`--port` exits 2). `./demo.sh` exits 0.

Ancestor's five repos, exact identity (what `akin --no-copies --no-similar` reported as zero):

| repo | drifted pairs | note |
| --- | --- | --- |
| sitbone | 0 | Logging.swift siblings never shared a blob (intended miss) |
| kizu | 0 | `init.rs` → `install.rs` is a 56% split, not an object (intended miss) |
| voidtrace | 0 | fixture clones were edited before add |
| tenaoshi | 0 | CTR-*.json never identical |
| skills | **1** | `SKILL.md` ↔ `SKILL_claude.md` **echo** via blob `2b16be83128c`; frozen b; `--port` equals current `SKILL.md` (9988+ bytes, exit 0) |

`akin` found the skills pair only through `git diff-tree -C` (copy 100%). `once` finds it because `SKILL_claude.md`'s current oid **is** `SKILL.md`'s previous oid. Same pair, no copy detector. base_commit is the add `9586d7ccf947` (the kinship event), not HEAD.

Wider dogfood (read-only):

| repo | drifted | what |
| --- | --- | --- |
| dignity-guide | 4 | `novel/.../old-version/*.md` still at the pre-edit chapter blobs (echo, frozen a). `--port` live → archive equals current chapter (4/4). |
| emergent-loop | 2 | `ash/1775293120.md` ↔ `04_chapter.md` (together, frozen ash) |
| soul-writer | 0 drifted / 55 identical | skill files copied into `.agents/` and `.claude/` and still byte-identical |

Scan times: skills 0.31s, dignity-guide 1.61s, soul-writer 0.93s (2789 paths), kizu 1.33s.

### After the improvement (v0.2: `--sync FROM` + occupancy in pretty)

Dogfood said the frozen twin *is* the product: skills `SKILL_claude.md`, dignity-guide `old-version/`, emergent-loop `ash/`. v0.1 made you name both paths. `--sync FROM` ports FROM onto every path that is still the shared blob.

```
$ ./once -C skills --sync emergent-engine/SKILL.md | wc -c
    9988
```

Equals current `SKILL.md`. One frozen twin, so no concat header (same bytes as `--port`).

Synthetic `--sync util.sh` updates *two* frozen twins (`frozen.sh` at the freeze blob, `ash-util.sh` at origin). Multiple bodies are separated by `# once sync <path>` headers. `--sync --write` materializes both. `--sync similar.sh` exits 1 (no frozen twin).

Pretty now shows occupancy, so the snapshot event is visible without `--json`:

```
emergent-engine/SKILL.md
  ↔ emergent-engine/SKILL_claude.md
  echo  base 2b16be83128c  2026-04-23  9586d7ccf947
  held a 5b2aa2437f84..2421494f5f57  b 9586d7ccf947..6b194336c058
  +68 -229  frozen: b (still at base)
```

`b` acquired the blob at the copy commit and still holds it at HEAD; `a` last held it at `2421494` (the last commit whose tree still had that oid, before the rewrite). That is the unrecorded merge-base, dated.

dignity-guide `--sync` of a live chapter still equals the live file (4/4 in v0.1 port check; `--sync` is the same 3-way with TO frozen).

## Dogfood targets

| Target | Role |
| --- | --- |
| synthetic fixture in `demo.sh` | exact copy, unicode, freeze, echo-archive, one-sided edit, copy-before-add (must miss), similar-looking (must miss), nested git dir, identical pair |
| skills | frozen 100% historical blob (`SKILL_claude.md`) |
| dignity-guide | `old-version/` chapter snapshots |
| emergent-loop | `ash/` timestamp snapshots |
| kizu / sitbone / voidtrace / tenaoshi | negative: similar/copied-then-edited, never shared a blob |
| soul-writer | currently-identical skill mirrors (`--identical`) |

Read-only git object walks; `--port` prints; no worktree mutation unless `--write`.

## Surprises

- Ancestor's "zero exact shared blobs in five repos" was **simultaneity**. Echo (ever-held the same oid) recovers the skills pair and the dignity-guide archives.
- A 100% git copy is often just echo: the new path is born as the old path's previous blob in the same commit the source rewrites.
- `--port` onto a frozen twin is identity with FROM. That is the product, not a degenerate case.
- Empty blob `e69de29` is excluded as a kinship key (unrelated empty files are not copies).

## Failures

- **kizu / sitbone / voidtrace / tenaoshi**: no kin. Correct. The interesting splits never committed an identical blob.
- **soul-writer `.agents/.../soultext.md`**: drifted from the `.claude` / `soul/` copies but was edited before add (`208e3c6c` vs `0392bcb4`). Exact identity refuses it.
- Pair listing of 55 identical soul-writer copies is still noisy; `--groups` was not this mutation.
- `--sync` with two frozen twins concatenates bodies; scripts should prefer `--write` or a single `--port`.

## Suggested mutations

- Union-find *groups* keyed by blob (soul-writer 55 rows → ~25 cliques).
- Index / worktree: `git hash-object` uncommitted files that still match a historical blob (the copy-before-edit window).
- `--write --sync` as a pre-commit for forgotten `SKILL_claude.md` twins.

## Kill / keep

**Keep.** The killed assumption was right to kill: similarity is how you get a false merge-base. Exact blob identity is a smaller, safer primitive, and it is not empty once "ever held" replaces "held at the same commit". `git merge-file` with a real ancestor blob is a Unix operation; a 56% `SequenceMatcher` base is not.

# candidate-01 — akin

## Primitive

A copy is not a branch, so git never recorded a merge-base; `akin` finds file pairs that split from shared content and uses that source blob as the base of a 3-way `--port`.

## Why this might not exist

`git log --find-copies` is a per-commit diff annotation. `jscpd` / PMD CPD look at the current tree. Neither answers "these two paths used to be the same file-shaped thing — what is the ancestor blob, and what would it take to apply *this* side's later edits onto *that* side?" That is a recurring workflow after `cp foo bar && $EDITOR bar` (fixtures, split modules, `SKILL.md` vs `SKILL_claude.md`). People reconstruct it by hand with `git log -p`, guess, and `diff`.

## How to run

```sh
./akin -C <repo> --pretty
./akin -C <repo> --port FROM TO
./akin -C <repo> --check
./demo.sh
```

## Empirical transcript

### Before the improvement (v0.1: simultaneous identical blobs only)

Synthetic fixture (copy committed, then both sides edited) worked. Copy-edited-before-`git add` did not:

```
demo ok: default listing contains drifted twins, not identical pair
simultaneous  frozen.sh           util.sh
simultaneous  util-backup.sh      util.sh
simultaneous  util.sh             weird name 日本語.sh
demo note: KNOWN GAP — edited-before-add.sh is a copy of util.sh edited
before git add, so they never shared a blob; v1 misses it
```

Real repos, read-only, same detector:

```
./akin -C sitbone --pretty     ->  no kin
./akin -C kizu --pretty        ->  no kin
./akin -C voidtrace --pretty   ->  no kin
./akin -C skills --pretty      ->  no kin
./akin -C tenaoshi --pretty    ->  no kin
```

v1 pair counts with `--no-copies --no-similar` (preserved as a flag): sitbone 0, kizu 0, voidtrace 0, skills 0, tenaoshi 0.

People almost never commit the byte-identical copy. They copy, edit, add. Exact-blob simultaneity is the wrong oracle.

### After the improvement (v0.2: git copies + same-basename at first appearance)

Same synthetic fixture now catches the pre-add edit (git copy 86%). `./demo.sh` exits 0.

```
sitbone   v1=0 v2=5
kizu      v1=0 v2=1
voidtrace v1=0 v2=66
skills    v1=0 v2=2
tenaoshi  v1=0 v2=0
```

kizu — the actual module split `git log` already knew about as `copy src/{init.rs => init/install.rs} (56%)`, now with a merge-base and a port:

```
$ ./akin -C kizu --pretty
src/init.rs
  ↔ src/init/install.rs
  copy 56%  base 65570e20efe3  2026-04-25  5671a72362c5
  +337 -252
```

`--diff` shows the pre-split file (`65570e20`) as ancestor: `init.rs` dropped `kizu_bin_for_scope` / `kizu_hook_command` (moved), `install.rs` is that extracted module plus later drift.

sitbone — four `Logging.swift` files added together, never identical, git did not mark copies; same-basename at add-time:

```
SitboneData    ↔ SitboneUI       similar 70%  frozen: a
SitboneCore    ↔ SitboneSensors  similar 63%
SitboneSensors ↔ SitboneUI       similar 60%
SitboneCore    ↔ SitboneUI       similar 55%
SitboneData    ↔ SitboneSensors  similar 54%  frozen: a
```

skills — a 100% copy that v1 still missed, because the source was *modified in the same commit* as the copy (they never coexisted as the same blob):

```
$ ./akin -C skills --pretty
emergent-engine/SKILL.md
  ↔ emergent-engine/SKILL_claude.md
  copy 100%  base 2b16be83128c  2026-04-23  9586d7ccf947
  +68 -229  frozen: b (still at base)
```

`--port SKILL.md SKILL_claude.md` equals current `SKILL.md` (9988 bytes, exit 0): the forgotten twin is exactly "apply FROM's post-copy commit onto a frozen TO".

voidtrace — 66 pairs, mostly golden/experiment JSON and a couple of `package.json` / test-file splits. This is the fixture-cloned-then-tweaked neighborhood the tool is for.

First-seen used "not in the previous `rev-list` row" and flickered on sitbone (100 commits, 31 first-parent, 7 merges): pair counts 4 vs 5 across runs. Persistent `seen_paths` made scores and membership stable (5/5).

## Dogfood targets

| Target | Role |
| --- | --- |
| synthetic fixture in `demo.sh` | exact copy, unicode path, freeze, one-sided edit, copy-before-add, nested git dir, identical pair |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | same-basename module loggers |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | real `git` copy split (`init.rs` → `init/install.rs`) |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | cloned golden/experiment fixtures |
| `/Users/annenpolka/ghq/github.com/annenpolka/skills` | frozen 100% copy + same-basename `SKILL.md` |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | miss (see Failures) |

Read-only git object walks; no worktree mutation.

## Surprises

- Exact shared blobs in real history: **zero** across five repos. The "obvious" definition of kinship does not occur.
- A 100% git copy can still fail v1: source rewritten in the copy commit (`SKILL.md` M + `SKILL_claude.md` C100 from the *old* blob).
- Git's copy source is greedy: `edited-before-add.sh` attached to `weird name 日本語.sh` (86%), not `util.sh`, because a sibling copy was closer.
- `microcommit-protocol/SKILL.md` ↔ `microstitch/SKILL.md` at 52%: same basename, related *protocol prose*, arguably a false friend.
- `--port` onto a frozen twin is a boring, correct identity with FROM. That *is* the product.

## Failures

- **tenaoshi**: `no kin`. Tracked `CTR-00N.json` siblings are similar (0.50–0.84) but different basenames; git `--find-copies-harder` did not tag the later adds as copies; the root commit has no parent so copy detection is skipped there. Untracked `EPC-*.json` in the worktree are ignored on purpose (HEAD only).
- **sitbone Core ↔ Data** add-time ratio 0.477, just under `--min-score 50`.
- **Wrong parent** on the synthetic pre-add copy (sibling, not origin).
- **v0.1** was a working tool that reported nothing on every allowed real target.

## Suggested mutations

- Numbered-stem groups (`CTR-*.json`, `EPC-*.json`) without requiring identical basename.
- Transitive kinship: a copy of a twin is a twin (would re-parent `edited-before-add.sh` to `util.sh`).
- Union-find *groups* instead of pair explosion (voidtrace 66 rows).
- Include the dirty worktree (tenaoshi's untracked EPC fixtures).
- `--port --check` as a pre-commit: frozen twins whose FROM moved.
- Default excludes: lockfiles, `vendor/`, generated schemas.
- First-parent-only scan for large histories.

## Kill / keep

**Keep.** v1 empirically died, which is the right kind of death: the primitive was sharp and the oracle was wrong. v2 keeps the merge-base / `--port` verb and uses the copy/split git already sometimes knows about, plus the same-basename add-time case git ignores. That is a Unix operation I have wanted after splitting a file, not a dashboard.

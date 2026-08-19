# mutation-60 — keel

## Primitive

A code locus is a **keel** token: mint a self-contained fingerprint once, store it, resolve it onto a later tree **without** re-supplying `path:line`. v0.6 keeps the v0.4/v0.5 refuses (origin body is identity, leftover stubs are not) and flips the origin key: **the repo is remotes + tip witnesses, not the set of root SHAs.** A shallow clone of the same project still resolves; a foreign repo still fail-closes unless `--any-repo`.

## Why this might not exist

Pin v0.5 (mutation-47) stopped leftover stubs from tying with basename bait and kept extract-and-keep as identity. Destroyer then showed origin is history shape:

1. Orphan branch added, checkout back to main, resolve `--to` the original commit → `different repository (git:8c17… vs git:1c02…,8c17…)`.
2. Depth-1 clone of the same repo → dest “root” is grafted HEAD, not the true root. CI `--depth 1` cannot land a pin minted on a full clone.

`--any-repo` would paper over both, and also land a helper on an unrelated repo at 1.000. The missing verb is still the token. The mutation is: **origin names the project, not the DAG’s roots.**

## How to run

From the worktree root:

```bash
chmod +x ./keel
./keel --help
./keel --selftest
./demo.sh
./keel mint --repo /path --from <old-sha> path:line
./keel resolve --repo /path --to HEAD keel1.…
./keel show keel1.…
./keel id --repo /path
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2. Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

v0.5 killed: “without `oldstem/…` there is no extract, only `ambiguous` copies.”

This mutation kills the follow-on lie: “same repo means the same set of `rev-list --max-parents=0 --all` prefixes.”

### Bought

- Depth-1 clone of the same project resolves without `--any-repo` (remotes overlap, or dest still holds a tip witness, or dest’s local `origin` is followed one hop).
- Orphan extra root stays the same keel.
- `git@` and `https://` of the same host/path are one project.
- Foreign repo (and `--to-dir` of a subdirectory inside it) still exits 1.
- Leftover stub / extract-and-keep / renamed-package extract: as v0.5.

### Lost

- A repo with no remotes, cloned `--depth 1` off a *later* tip than any stored witness, cannot prove identity unless dest’s `origin` is a local path we can follow. Network remotes are the CI case.
- Two forks with different remotes and no shared objects look foreign (use `--any-repo`).

## Empirical transcript

### Working software (v0.6), before the improvement

`./keel selftest` → `selftest: ok`. `./keel --selftest` also works (v0.5 `./pin --selftest` was not a flag). `./demo.sh` all checks passed (leftover stub, extract-and-keep, leftover + `src/math/ops.py`, kizu / voidtrace / tenaoshi / sitbone / skills).

```
$ HELPER=$(./keel mint --repo $REPO --from $V1 src/calc.py:14)
$ ./keel show "$HELPER"
  minted: src/calc.py:14
  origin: keel1:r:github.com/keel-lab/ugly;w:<V1>,<V2>
  remotes: github.com/keel-lab/ugly

$ ./keel resolve --repo $UNREL --to HEAD --porcelain "$HELPER"
# rc=1  token belongs to a different repository
# (keel1:r:github.com/keel-lab/ugly;w:… vs keel1:r:github.com/other/util;w:…)

$ ./keel resolve --repo $SHALLOW --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:14	src/math/ops.py:8	1.000	path or surrounding file changed
```

Ancestor pin v0.5 on the same shape: orphan extra root and a *true* depth-1 clone fail-close as foreign.

kizu godfile split is unchanged (old path is gone):

```
$ ./keel resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

Leftover stub still loses:

```
$ ./keel resolve --repo $STUB --to $STUB_V2 --porcelain "$STUBPIN"
moved	-	src/calc.py:5	src/calc/ops.py:5	0.998	… leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1
```

### Failures that drove the first improvement

`git clone --depth 1 $REPO` on a local path is **not shallow**:

```
warning: --depth is ignored in local clones; use file:// instead.
shallow roots: ac2621a4…   # same as full
full roots:    ac2621a4…
```

The demo’s “depth-1” check was resolving onto a full clone. Pin v0.5 would have passed it too. The hole the mutation claims to close was not actually closed.

`git clone --depth 1 file://$REPO` produces a real graft: dest roots become HEAD, `.git/shallow` exists, V1 is missing from the object store.

### After the improvement

`git clone --depth 1 file://$REPO` is a real graft. Dest roots are HEAD; V1 is gone; `.git/shallow` exists. Dest’s own remotes are `file://…` (not a project id). keel now **inherits network remotes one hop** from that local origin, so `keel id` on the clone still names `github.com/keel-lab/ugly`.

```
$ git clone --depth 1 file://$REPO $SHALLOW
$ git -C $SHALLOW rev-parse --is-shallow-repository
true
$ git -C $REPO rev-list --max-parents=0 --all
8da12ddc9d927d6010a5be0f9a3798fc4eca771f
$ git -C $SHALLOW rev-list --max-parents=0 --all
50e381316386fa54e7a6aa028d3587c9643e0093
$ ./keel id --repo $SHALLOW
keel1:r:github.com/keel-lab/ugly;w:50e381316386fa54
$ ./keel resolve --repo $SHALLOW --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:14	src/math/ops.py:8	1.000
```

Pin v0.5 would fail-close here (`git:8da1…` vs `git:50e3…`).

Hard case: remotes-less mint while HEAD is V1, then commit V2, then `file://` depth-1 of V2 (V1 absent). Token origin is `keel1:r:;w:<V1>` only. Resolve still lands by following dest `origin` to the object store that holds V1.

```
$ ./keel show "$BAREPIN"
  origin: keel1:r:;w:9430d4cd83927c6e
$ ./keel resolve --repo $BARESH --to HEAD --porcelain "$BAREPIN"
same	-	src/calc.py:1	src/calc.py:1	1.000
```

`./demo.sh` still exits 0. New guards: `24` asserts shallow + unequal roots + inherited remote; `24b` remotes-less mint-then-advance.

## Dogfood targets

- Leftover wrapper + stem-split / renamed extract / same-basename import pointer.
- Extract-and-keep to `src/calc/ops.py` and `src/math/ops.py`.
- Synthetic ugly repo, 1.2 MB godfile, NFD `café.py`, missing `--to`, truncated tokens, foreign helper, orphan extra root, `file://` depth-1 clone.
- kizu `src/app.rs` split at `b4e6a5d`; voidtrace `evaluate.ts:1`; tenaoshi `KinsokuEngine.swift:12`; sitbone `PresenceArbiter.swift:75`; skills remote identity.

## Surprises

- `git clone --depth 1 /local/path` silently copies the whole object store. The destroyer’s shallow hole is `file://` (or a real remote), not “any clone with `--depth` in the argv.”
- Storing HEAD *and* `--from` as witnesses makes “clone of the repo as it was when I minted” work even with no remotes: dest HEAD is in the token. The hard case is mint-then-advance-then-shallow.
- `--to-dir` of a foreign repo’s subdirectory used to skip origin (pin v0.5: only when `discover_repo == directory`). Inheriting the containing repo is what makes “foreign” true for `pkg/`.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve.
- Relative leftover `from .calc import` still does not name `src/math/calc.py` (not this mutation).
- v1 tokens (no origin) still resolve onto any repo.
- Token length ~160–450 chars plus a short keel origin.

## Suggested mutations

- Missing origin / v1 fail closed unless `--any-repo`.
- Relative / `from .ops import` leftovers must still name the extract.
- Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths.
- Do not follow a local `origin` that is a *different* project sharing a graft (unlikely; SHA witnesses are the check).

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split. Leftover stubs still lose. Extract-and-keep is still identity. The new refuse is the honest one: history shape is not repo identity. Kill only if a later mutation proves bookmarks *want* to be global (any tree, any project) — that is `--any-repo`, not this keel.

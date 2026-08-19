# mutation-110 — shoal

## Primitive

A locus token's origin is **signed remotes at mint time + required witnesses**, not live `git remote` config. Adding a remote of a stranger does not land the pin. A shared graft of a different project fail-closes unless `--any-repo`. A true `file:// --depth 1` clone of the signed project still resolves.

## Why this might not exist

Keel (mutation-60) flipped origin from root SHAs to remotes + tip witnesses. DESTROYER_KEEL then showed remotes are config and witnesses are occupancy:

1. `git remote add extra git@github.com:victim.git` on a foreign repo is remotes ∩. The pin lands. Live `git remote add` is `--any-repo`.
2. `git fetch $VICTIM $WITNESS` plants one SHA. `object_exists` matches. A copied file plus one fetched object is the project.
3. Missing `o` / v1 / gitless `--to-dir` is a silent global locator.

`--any-repo` would paper over both, and also land a helper on an unrelated repo at 1.000. The missing verb is still the token. The mutation is: **origin cannot be typed into `git remote add`.**

## How to run

From the worktree root:

```bash
chmod +x ./shoal
./shoal --help
./shoal --selftest
./demo.sh
./shoal mint --repo /path --from <old-sha> path:line
./shoal resolve --repo /path --to HEAD shoal1.…
./shoal show shoal1.…
./shoal id --repo /path
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2. Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

Keel killed: “same repo means the same set of `rev-list --max-parents=0 --all` prefixes.”

This mutation kills the follow-on lie: “same repo means dest remotes ∩ pin remotes, or dest can `cat-file -e` a stored SHA.”

### Bought

- `git remote add extra victim.git` does not land. Extra remotes are not walked, not stored, not printed by `shoal id`.
- Fetch of a pin witness (shared graft / alternates-shaped occupancy) does not land.
- `git remote set-url origin victim.git` without dest tip lineage does not land.
- Missing origin / unsigned v1–v3 `o` / gitless `--to-dir` fail-closes unless `--any-repo`.
- Tampering remotes on a v4 token drops origin (mint signature).
- `file:// --depth 1` of the signed project still resolves (origin hop + dest tip in the parent).
- Remotes-less mint, then advance, then `file://` depth-1 still follows dest `origin` to the store that holds required witnesses.
- Orphan extra root, resolve `--to` the original commit: still the same shoal.
- ssh vs https of the same signed host/path on a dest whose tip is a stored witness: still one project.
- v0.2: 3-hop `file://` of mint-at-V1 still resolves. `www.github.com` / `ssh.github.com` fold to `github.com`. gitlab same-path does not.
- Unique kizu pin still lands `src/app.rs:529@b4e6a5d → src/app/layout.rs:17`.
- kizu steal fixture (copied `layout.rs` + fetched HEAD + extra remote) refuses.

### Lost

- A dest whose `origin` is a later fork URL (`alice/ugly`) with no local hop and whose HEAD is not a stored witness still looks foreign (use `--any-repo`). That is also the stranger with a typed URL — there is still no “same project, remotes drifted” verb that is not `--any-repo`.
- Mint-at-V1 then a V2-only dest whose origin was rewritten to the signed host/path (GHA `fetch-depth: 1` of a later tip, local hop gone) still fail-closes: remotes match, lineage does not. Remotes ∩ without lineage would re-open `git remote set-url`.
- Path `git clone --depth 1 $REPO` is still a silent full copy. Dest then holds the witness as an ancestor. That is occupancy of dest's *own* history, not the graft the mutation names.

## Empirical transcript

### Working software (v0.1), before the improvement

`./shoal --selftest` → `selftest: ok`. `./demo.sh` all origin-as-config checks passed (remote-add, fetch SHA, set-url, file:// depth-1, remotes-less hop, orphan `--to` original, missing `o`, kizu land + kizu steal).

```
$ HELPER=$(./shoal mint --repo $REPO --from $V1 src/calc.py:6)
$ ./shoal show "$HELPER"
  minted: src/calc.py:6
  origin: shoal1:r:github.com/keel-lab/ugly;w:<V1>,<V2>
  remotes: github.com/keel-lab/ugly  (signed at mint)
  witnesses: <V1>,<V2>  (required)

$ ./shoal resolve --repo $UNREL --to HEAD --porcelain "$HELPER"
# rc=1  token belongs to a different repository

$ git -C $UNREL remote add extra git@github.com:keel-lab/ugly.git
$ ./shoal id --repo $UNREL
shoal1:r:github.com/other/util;w:…
$ ./shoal resolve --repo $UNREL --to HEAD --porcelain "$HELPER"
# rc=1  extra remote is not origin

$ git -C $UNREL fetch $REPO $V1
$ ./shoal resolve --repo $UNREL --to HEAD --porcelain "$HELPER"
# rc=1  occupancy is not identity

$ git clone --depth 1 file://$REPO $SHALLOW
$ ./shoal resolve --repo $SHALLOW --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:6	src/math/ops.py:7	1.000
# rc=0
```

kizu godfile split still lands on the real repo:

```
$ ./shoal resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

Same token on a steal repo (copied `layout.rs`, fetched kizu HEAD, extra remote `annenpolka/kizu`) exits 1. Live `git remote add` is not origin.

### Failures that drove the first improvement

v0.1 `FOLLOW_HOPS=2` still treated clone-of-clone-of-clone as foreign. Mint-at-V1 (witnesses are only V1), dest is a `file:// --depth 1` of a `file:// --depth 1` of a `file:// --depth 1` of V2:

```
h1 id=shoal1:r:github.com/keel-lab/ugly;w:<V2>  rc=0
h2 id=shoal1:r:github.com/keel-lab/ugly;w:<V2>  rc=0
h3 id=shoal1:r:;w:<V2>                         rc=1
```

h3's origin is `file://h2`. Two hops reach h1, not the signed repo. Hop cap was a project verdict.

Same dest, origin rewritten to GitHub host aliases after the local hop is gone:

```
www.github.com/keel-lab/ugly   →  shoal1:r:www.github.com/…   rc=1
ssh.github.com/keel-lab/ugly   →  shoal1:r:ssh.github.com/…   rc=1
gitlab.com/keel-lab/ugly       →  shoal1:r:gitlab.com/…       rc=1
```

`normalize_remote` lowercased host/path and stripped `.git`. It did not know GitHub's SSH hostname or `www.`.

### After the improvement

`FOLLOW_HOPS=16` with cycle detection: origin chain is a walk, not a project depth. h3 inherits `github.com/keel-lab/ugly` and lands mint-at-V1 at `src/calc.py:1`.

`www.github.com` and `ssh.github.com` fold to `github.com`. Dest whose tip is a stored witness and whose origin is an alias of the **signed** host/path lands. `gitlab.com/keel-lab/ugly` still fail-closes (a mirror is not the mint signature). `git remote add extra` and fetch-SHA occupancy still refuse.

```
$ ./shoal id --repo $H3
shoal1:r:github.com/keel-lab/ugly;w:<V2>
$ ./shoal resolve --repo $H3 --to HEAD --porcelain "$HOPPIN"
same	-	src/calc.py:1	src/calc.py:1	1.000

$ git -C $ALIAS remote set-url origin https://www.github.com/keel-lab/ugly.git
$ ./shoal id --repo $ALIAS
shoal1:r:github.com/keel-lab/ugly;w:<V2>
```

`./demo.sh` still exits 0. New guards: `17` 3-hop mint-at-V1; `18` host-alias fold vs gitlab.

Mint-at-V1 plus a V2-only dest whose origin was rewritten to `https://github.com/keel-lab/ugly.git` (hop gone, dest HEAD not a stored witness) still fail-closes. Remotes ∩ without lineage would re-open `git remote set-url`. That is still Lost, not papered.

## Dogfood targets

- Synthetic ugly repo: remote-add extra, fetch SHA, set-url, file:// `--depth 1`, remotes-less mint-then-advance, orphan `--to` original, gitless `--to-dir`, `--from-dir` naked token.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` `src/app.rs:529@b4e6a5d` → `src/app/layout.rs:17` on the full clone.
- Constructed kizu steal: independent repo, remote `other/util`, copied `src/app/layout.rs`, `git fetch $KIZU $KIZU_HEAD`, extra remote `annenpolka/kizu`.

## Surprises

- `shoal id` after `git remote add extra victim` still naming only `origin` is the whole primitive. Intersection over `git remote -v` was the hole, not a missing checksum.
- Orphan extra root with dest HEAD on the orphan fails dest-tip lineage and still has to count **local branches** that carry a required witness. FETCH_HEAD must not count, or fetch-SHA becomes a branch.
- Signing remotes into the payload (`s`) stops stripped/`o`-swapped tokens. It does not stop dest config: dest never contributes remotes as proof.

## Failures

- `Host gh` SSH aliases are still four spellings if dest never cloned a path git knows. Do not read `~/.ssh/config`.
- Mint-at-V1 + GHA later tip (hop gone) still fail-closes. That is remotes-as-config, not a missed fold.
- `--any-repo` is still the fork verb and the stranger verb.

## Suggested mutations

- Host aliases / mirrors of the same path are one shoal or none, without rescuing dest only because a path clone still holds V1.
- Walk dest `origin` until a network remote or a witness store, not a hop cap of 2.
- A “same project, remotes drifted” verb that is not `--any-repo` and does not land `pkg/util.py`.

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split on a full clone. Foreign git roots still refuse. Live `git remote add` is not origin. Shared graft of a different project fail-closes. Kill only if a later mutation proves bookmarks *want* to be global (any tree, any project) — that is `--any-repo`, not this shoal.

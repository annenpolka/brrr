# DESTROYER — keel

Adversarial pass on **origin-as-project**: remotes + tip witnesses, not root SHAs. No rewrites. Failures are conceptual. Leftover-stub / extract-and-keep / DESTROYER_PIN_V5 pointer votes were not re-run.

- **keel** (mutation-60, v0.6.1) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb0da2df3d3e`
- Transcripts: `/tmp/destroy-keel/transcript.txt`, `/tmp/destroy-keel/transcript-round2.txt`
- Cases: `/tmp/destroy-keel/cases.json`, `/tmp/destroy-keel/cases-round2.json`
- Drivers: `/tmp/destroy-keel/attack.py`, `/tmp/destroy-keel/attack2.py`
- Fixtures: `/tmp/destroy-keel/fixtures/`, `/tmp/destroy-keel/r2/`
- `./keel --selftest` → `selftest: ok` after the attacks. Victim not rewritten.

Round 1 minted after V2 already existed, so the token stored **HEAD-at-mint** as a witness. Dest checkouts of that SHA then matched with rewritten remotes. Round 2 mints **while HEAD is V1**, then advances, then dest is a V2-only graft. That is the CANDIDATE hard case.

Verdict: **mutate, do not kill.** Pin v0.5’s extra-root / true-shallow refuse is actually closed on the fixtures they wrote. Unique kizu pins still land `src/app.rs:529@b4e6a5d → src/app/layout.rs:17` on a full clone **and** on `git clone --depth 1 file://$KIZU`. Foreign git **roots** still exit 1. `--to-dir` of a subdirectory still inside the foreign `.git` inherit-refuses. The new holes are where v0.6 overcorrected: remotes are config, witnesses are object occupancy, and missing origin is allowed.

---

## Primitive restated

A keel token is a locus fingerprint plus a **repo identity**. CANDIDATE: the repo is **normalized remotes + tip witnesses** (`HEAD` / `--from`), not `rev-list --max-parents=0 --all`. A depth-1 clone of the same project should resolve. A stranger should fail-close unless `--any-repo`.

`keels_match` (`keel` 601–617), first true wins:

1. `set(pin.remotes) & set(dest.remotes)` — any remote spelling in common
2. `set(pin.witnesses) & set(dest.witnesses)` — any 16-char tip prefix in common
3. `object_exists(dest_root, w)` for a pin witness — dest’s object store can see the SHA
4. `_follow_local_match` up to `FOLLOW_HOPS=2` — walk `file://` / path remotes, then (1) or (3) on the hop

`origins_match` (`keel` 651–663): **if either side has no origin, return True.** `--to-dir` sets dest origin only when `discover_repo(directory)` finds a `.git` (walks parents).

---

## 1. Remote spelling is config — `git remote add` is `--any-repo` (conceptual, lethal)

Foreign `other/util` with the same `helper_keep` line. Token `keel1:r:github.com/keel-lab/ugly;w:…`. Root resolve without `--any-repo` is the bought refuse:

```
$ ./keel resolve --repo $FOREIGN --to HEAD --porcelain "$HELPER"
# rc=1
keel resolve: token belongs to a different repository
(keel1:r:github.com/keel-lab/ugly;w:4dcf37ca7282f41b vs keel1:r:github.com/other/util;w:…)
```

No fetch. Add a second remote whose **URL spelling** is the pin’s project:

```
$ git -C $FOREIGN remote add extra git@github.com:keel-lab/ugly.git
$ ./keel id --repo $FOREIGN
keel1:r:github.com/keel-lab/ugly,github.com/other/util;w:…

$ ./keel resolve --repo $FOREIGN --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:4	pkg/util.py:1	1.000	path or surrounding file changed
# rc=0
```

`git remote set-url origin https://github.com/keel-lab/ugly.git` is the same landing. Intersection does not require the dest to have fetched the pin, to share objects, or to be a fork. A stranger who can edit `.git/config` is the project.

Round 2 mint-at-V1 token (witnesses are **only** V1) still lands. Remotes ∩ short-circuits witnesses.

---

## 2. Shared graft — a fetched SHA is the project (conceptual, lethal)

Same foreign repo, remotes still `other/util`. Fetch **one** pin witness, no matching network remote:

```
$ git -C $FOREIGN fetch $UGLY 4dcf37ca7282f41b
$ git -C $FOREIGN cat-file -e 4dcf37ca7282f41b   # 0
$ ./keel id --repo $FOREIGN
keel1:r:github.com/other/util;w:38228d99fe2ab910

$ ./keel resolve --repo $FOREIGN --to HEAD --porcelain "$HELPER"
moved	-	src/calc.py:4	pkg/util.py:1	1.000
# rc=0
```

`object_exists(dest, pin.witness)` does not ask whether dest is ugly. CANDIDATE suggested mutation: “Do not follow a local origin that is a *different* project sharing a graft (unlikely; SHA witnesses are the check).” SHA witnesses **are** the graft hole.

Same landing via:

- `echo $UGLY/.git/objects > $FOREIGN/.git/objects/info/alternates` (`clone --shared`)
- `git remote add origin /path/to/ugly` on a repo whose files are `pkg/util.py` — `FOLLOW_HOPS` inherits ugly’s remotes / objects. Dest `keel id` prints `github.com/keel-lab/ugly`.

### kizu dogfood

Mint `src/app.rs:529@b4e6a5d` on full kizu. Independent repo, remote `other/util`, **copied** `src/app/layout.rs`, then `git fetch $KIZU $KIZU_HEAD` (object only):

```
$ ./keel show "$SEEN"
  origin: keel1:r:github.com/annenpolka/kizu;w:b4e6a5dbf677ad07,9349dc504163d171
  remotes: github.com/annenpolka/kizu

$ ./keel resolve --repo $STEAL --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
# rc=0
```

One copied file plus one fetched SHA. Origin check never fires. The godfile split “lands” on a stranger.

Spoof only the remote, no layout.rs: origin check **still passes**, then `deleted	-	src/app.rs:529	-	0.000	no candidates` rc=0. Confirmed deletion is an answer. The refuse that was supposed to be “different repository” never ran. Voidtrace pin + spoofed `annenpolka/voidtrace` remote is the same `deleted` rc=0.

---

## 3. `--to-dir` — inherit only if a `.git` is nearby (conceptual)

Pin v0.5: `--to-dir $UNREL/pkg` skipped origin (`discover_repo == directory`). Keel walks parents. **Inside** the foreign git repo that holds:

```
$ ./keel resolve --to-dir $FOREIGN/pkg --porcelain "$HELPER"
# rc=1  different repository (…/ugly vs …/other/util)
```

Closed for that shape.

A **copy** of the same bytes with no `.git`:

```
$ cp -R $FOREIGN/pkg /tmp/destroy-keel/fixtures/gitless-pkg
$ ./keel resolve --to-dir gitless-pkg --porcelain "$HELPER"
moved	-	src/calc.py:4	util.py:1	1.000
# rc=0
```

`origins_match(pin, None)` is True. Gitless dest is allowed (selftest asserts it). A tarball of `pkg/` is not foreign.

Same bytes dropped into an unrelated git repo’s subdirectory:

```
$ ./keel resolve --to-dir $STRANGER/vendor/ugly-pkg --porcelain "$HELPER"
# rc=1  (…/ugly vs keel1:r:github.com/stranger/mono;w:…)
```

Origin is the **containing** project, not the files. Gitless copy lands; vendored copy refuse-closes. `--from-dir` mint (no origin on the token) resolves onto foreign git at 1.000.

kizu pin `--to-dir` of a gitless copy of `src/app`:

```
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
# rc=0
```

---

## 4. v1 / missing `o` — origin is optional on the token (conceptual)

CANDIDATE listed this. Still true, and it is the same `if not pin_origin` branch as §3.

```
$ # forged v:1 payload, no o
$ ./keel resolve --repo $FOREIGN --to HEAD --porcelain "$V1TOK"
moved	-	src/calc.py:4	pkg/util.py:1	1.000
# rc=0

$ # v3 token, pop "o", re-encode
$ ./keel resolve --repo $FOREIGN --to HEAD --porcelain "$STRIPPED"
moved	-	src/calc.py:4	pkg/util.py:1	1.000
# rc=0
```

A keel token without origin is a global locator. `--any-repo` is the documented override; missing `o` is the silent one.

---

## 5. `file://` shallow vs path clone — `--depth 1` is not the graft (conceptual, load-bearing)

CANDIDATE already named `git clone --depth 1 $PATH` as a silent full copy. Round 2 puts that next to remotes-rewritten on the **hard case**.

Mint while HEAD is V1 (`w:4dcf37ca7282f41b` only). Commit V2 (`786ddf6f…`). Dest is depth-1 of V2. Dest does not contain V1. Dest HEAD is **not** in the token.

Inherited remotes (the mutation’s buy):

```
$ git clone --depth 1 file://$UGLY $SH
$ git -C $SH rev-parse --is-shallow-repository   # true
$ git -C $SH cat-file -e $V1                     # missing
$ ./keel id --repo $SH
keel1:r:github.com/keel-lab/ugly;w:786ddf6f7238700a
$ ./keel resolve --repo $SH --to HEAD --porcelain "$TOK"
moved	-	src/calc.py:4	src/math/ops.py:4	1.000
# rc=0
```

Rewrite dest origin to a fork **network** URL (local hop gone):

```
$ git -C $SH remote set-url origin https://github.com/fork/ugly.git
$ ./keel id --repo $SH
keel1:r:github.com/fork/ugly;w:786ddf6f7238700a
$ ./keel resolve --repo $SH --to HEAD --porcelain "$TOK"
# rc=1
keel resolve: token belongs to a different repository
(keel1:r:github.com/keel-lab/ugly;w:4dcf37ca7282f41b vs keel1:r:github.com/fork/ugly;w:786ddf6f7238700a)
```

`git remote remove origin` is the same refuse: `keel1:r:github.com/keel-lab/ugly;w:V1 vs keel1:r:;w:V2`.

**Same rewrite, path clone:**

```
$ git clone --depth 1 $UGLY $PATHC
# warning: --depth is ignored in local clones; use file:// instead.
$ git -C $PATHC rev-parse --is-shallow-repository   # false
$ git -C $PATHC cat-file -e $V1                     # present
$ git -C $PATHC remote set-url origin https://github.com/fork/ugly.git
$ ./keel resolve --repo $PATHC --to HEAD --porcelain "$TOK"
moved	-	src/calc.py:4	src/math/ops.py:4	1.000
# rc=0
```

Identical argv `--depth 1`, identical remote rewrite, opposite origin verdict. Path dest still holds V1, so `object_exists` matches. Origin after remotes drift is **still object-store occupancy**, which is the pin v0.5 key they claimed to leave. `file://` is the only local graft; CI that clones a local cache with a path (not `file://`) never exercises the mutation.

`git remote set-url origin https://github.com/keel-lab/ugly.git` on the true shallow still lands (ssh/https of the **same** host/path). That is the GitHub Actions `fetch-depth: 1` case, and it survived.

---

## 6. `FOLLOW_HOPS=2` — clone-of-clone-of-clone is foreign (conceptual)

Mint-at-V1, dest is a file:// depth-1 of a file:// depth-1 of a file:// depth-1 of V2. Each hop is shallow; V1 is gone at hop 1. `keel id`:

| dest | id |
| --- | --- |
| h1 | `keel1:r:github.com/keel-lab/ugly;w:786ddf6f…` |
| h2 | `keel1:r:github.com/keel-lab/ugly;w:786ddf6f…` |
| h3 | `keel1:r:;w:786ddf6f…` |

h1/h2 resolve `moved … src/math/ops.py:4 1.000`. h3:

```
# rc=1
(keel1:r:github.com/keel-lab/ugly;w:4dcf37ca7282f41b vs keel1:r:;w:786ddf6f7238700a)
```

`_follow_local_match` with `hops=2` from h3 walks h2 then h1 and returns before the full repo. Nested CI caches / `clone --reference` chains longer than two local hops look like a different project. Round 1 hid this because dest HEAD V2 was stored on the token.

Remotes-less mint-then-advance-then-file:// shallow still follows dest `origin` to the object store that holds V1 (demo 24b, R2 not needed). Drop that origin: rc=1. CANDIDATE Lost clause, empirical.

---

## 7. Host spelling is the project (conceptual)

True V2-only `file://` shallow, dest origin rewritten. Same tree as §5’s successful inherited-remote resolve:

```
git@gh:keel-lab/ugly.git
  → keel1:r:gh/keel-lab/ugly;w:V2          rc=1

ssh://git@ssh.github.com/keel-lab/ugly.git
  → keel1:r:ssh.github.com/keel-lab/ugly   rc=1

https://www.github.com/keel-lab/ugly.git
  → keel1:r:www.github.com/keel-lab/ugly   rc=1

https://gitlab.com/keel-lab/ugly.git
  → keel1:r:gitlab.com/keel-lab/ugly       rc=1
```

`normalize_remote` lowercases host/path and strips `.git`. It does not know GitHub’s SSH hostname, `www.`, SSH `Host gh` aliases, or a mirror. Full clones survive these rewrites via `object_exists(V1)` — another file:// vs path split.

Round 1, mint stored V2: all four of these **landed**, because dest HEAD ∈ pin.witnesses. Tip occupancy papers host spelling whenever dest sits on a stored SHA.

---

## 8. `--any-repo` papers a fork **and** a stranger (conceptual)

Independent history, files match, remotes `github.com/alice/ugly`:

```
$ ./keel resolve --repo $FORK --to HEAD --porcelain "$HELPER"
# rc=1  (…/keel-lab/ugly vs …/alice/ugly)
$ ./keel resolve --repo $FORK --to HEAD --any-repo --porcelain "$HELPER"
moved	-	src/calc.py:4	src/math/ops.py:4	1.000
# rc=0
```

Same flag on `other/util`:

```
moved	-	src/calc.py:4	pkg/util.py:1	1.000
# rc=0
```

CANDIDATE Lost: “Two forks with different remotes and no shared objects look foreign (use `--any-repo`).” That is also the stranger landing at 1.000. There is no “same project, remotes drifted” verb. Fork PR CI (`fetch-depth: 1` of `alice/ugly` for a token minted on `keel-lab/ugly` before the PR tip existed) is §5’s fail-close. `--any-repo` is the paper, and it is global.

---

## 9. Tip witnesses make remotes optional (conceptual, kizu)

`repo_keel` stores `--from` **and** `HEAD`. Mint of an old line on today’s clone:

```
$ ./keel mint --repo $KIZU --from b4e6a5d src/app.rs:529
  origin: keel1:r:github.com/annenpolka/kizu;w:b4e6a5dbf677ad07,9349dc504163d171
```

`file:// --depth 1` of today’s kizu: `b4e6a5d` gone, dest witness is `9349dc50…`. Inherited remotes land `layout.rs:17` (bought). Then rewrite dest origin to `github.com/fork/kizu`:

```
$ ./keel id --repo $KIZU_SHALLOW
keel1:r:github.com/fork/kizu;w:9349dc504163d171
$ ./keel resolve --repo $KIZU_SHALLOW --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
# rc=0
```

Remotes do not overlap. Dest has no `b4e6a5d`. Dest HEAD’s 16-char prefix **is in the token**, so (2) fires. CANDIDATE: “Storing HEAD *and* `--from` as witnesses makes clone of the repo as it was when I minted work even with no remotes.” Empirical: **any dest whose HEAD (or any stored tip) is that SHA is kizu**, including a fork shallow of the mint-time HEAD, including a stranger who fetched that object (§2).

The hard case (dest tip **not** in the token, V1 gone) is §5–§7. The common case (mint old line on today’s tree, dest is today’s shallow) never consults remotes once dest HEAD matches. Remotes-as-project is the fallback for mint-then-advance grafts, and it is the fail-open for spoofed URLs.

---

## 10. Orphan extra root survived; orphan-only graft without origin did not

Pin v0.5 died on `git checkout --orphan` because roots changed. Keel:

```
$ git checkout --orphan extra-hist && git rm -rf . && echo orphan > orphan-only.txt && commit
$ ./keel resolve --repo $ORPH --to $V2 --porcelain "$TOK"
moved	-	src/calc.py:4	src/math/ops.py:4	1.000
# rc=0
```

Still on the orphan, remotes kept, `--to` the original commit. Extra root `0e5a6581…` is not identity. Bought.

`resolve --to HEAD` on the orphan-only tree: origin matches, then `deleted	-	src/calc.py:4	-	0.000	no candidates` rc=0. Honest content miss, not an origin refuse.

`git clone --depth 1 --branch extra-hist file://$ORPH`: inherits `github.com/keel-lab/ugly` via two local hops, origin matches, content deleted. `git remote remove origin` on that graft:

```
# rc=1
(keel1:r:github.com/keel-lab/ugly;w:4dcf37ca7282f41b vs keel1:r:;w:0e5a65818fcaafd6)
```

Same git family, dest is a true shallow of the extra root, no remotes, no V1. Origin-as-project without a followable hop is origin-as-SHA again, and the SHA is the wrong one.

---

## What survived

- `./keel --selftest` → `selftest: ok`. Victim not rewritten. Leftover-stub / extract-and-keep not re-attacked.
- Foreign **git root** without spoof/fetch: rc=1, no result row.
- `--to-dir` of a subdirectory **still inside** that foreign git: rc=1.
- `file:// --depth 1` of the same project with inherited or same-spelling remotes: kizu `layout.rs:17`, ugly `math/ops.py:4`. Dest roots ≠ full roots; V1 missing; pin v0.5 would have fail-closed.
- Orphan extra root, checkout original **or** resolve `--to` original while still on the orphan: same keel.
- `git@` vs `https://` of `github.com/keel-lab/ugly` on a V2-only shallow: remotes ∩, lands.
- 1-hop and 2-hop `file://` of V2 after mint-at-V1: inherit, land.
- Voidtrace HEAD identity: `same` `evaluate.ts:1`, skipped clones named in the note.
- Skills `keel id` still `github.com/annenpolka/skills`.
- Truncated tokens / missing `--to` not re-broken (out of scope, still as advertised in demo).

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still the token. Unique kizu pins still land the godfile split on a full clone and on a real `file://` depth-1 of the same remote. Foreign roots still refuse. Orphan extra roots are not a different repository. Kill only if a later mutation proves bookmarks *want* to be global (any tree, any project) — that is `--any-repo` and also missing `o`, not this keel.

| do not kill because | mutate toward |
| --- | --- |
| kizu `src/app.rs:529@b4e6a5d` → `src/app/layout.rs:17` on full and on `file:// --depth 1`; foreign git root rc=1; `--to-dir $UNREL/pkg` rc=1; orphan extra root still the same keel; ssh/https of the same host/path on a true shallow | **Remotes ∩ is not proof.** A dest remote must be a remote the pin’s project actually talks to, or drop remotes as a *sufficient* match. `git remote add extra git@github.com:victim.git` cannot be identity. |
| | **Witness occupancy is not identity.** `object_exists(dest, pin.witness)` / 16-char HEAD ∩ makes a fetch, `alternates`, or local `origin` hop the project. Require remotes ∩ **or** dest is a descendant/graft **of this remote**, not “can cat-file the SHA.” CANDIDATE already named shared-graft; the check they trusted *is* the hole. |
| | **Missing origin fail-closes** unless `--any-repo`. v1 / stripped `o` / gitless `--from-dir` / gitless `--to-dir` of a tarball are the silent global locator. `--to-dir` inherit of a containing `.git` is not “these files.” |
| | **`--any-repo` is not the fork verb.** Fork PR CI (`alice/ugly` shallow of a later tip) needs a same-project override that does not land `pkg/util.py` at 1.000. |
| | **Host aliases are one project or none.** `ssh.github.com` / `www.github.com` / `Host gh` / a gitlab mirror of the same path cannot be four keels when dest is a `file://` graft, and cannot be rescued only because a path clone still holds V1. |
| | **`FOLLOW_HOPS=2` is a depth, not a project.** 3-hop file:// of the same object is still the same keel, or refuse hops entirely and require dest to carry the network remote (the GHA case already works). |
| | Path `git clone --depth 1 $REPO` vs `file://` remains the silent full copy. Do not treat argv `--depth` as a graft. The mutation already knows this; remotes-rewritten on the path clone shows the key underneath is still the object store. |

A one-line “refuse when dest remotes are a strict superset” would hide §1’s extra remote and would not touch fetch/alternates, gitless `--to-dir`, v1, `ssh.github.com`, or 3-hop. Not applied.

A one-line “do not `object_exists`” would hide §2 and would re-open remotes-less mint-then-advance-then-`file://` (demo 24b) unless follow-origin still walks the hop. That trade is the mutation, not a patch.

Do not grow a forge identity service. The next mutation is **origin that cannot be typed into `git remote add`**, plus missing-`o` fail-closed, not a prettier `keel id`.

# DESTROYER refpin 2

Date: 2026-09-02 14:14 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-refpin/refpin`

sha256 `f9f7409d168bd134b502386bd5f03d009eb39745f973fac9509e5a12093905cb` (19877 bytes). Matches MUTATE.md after-hash. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-refpin-refpin/candidate-refpin/refpin` is byte-identical (branch `specimen-hdd/candidate-refpin-refpin`, commit `e91c8cd`). Parent tree stays on `main`. This object was not merged onto `main`. No nix (`command -v nix` empty).

Origin: specimen-064 / hdd-s064. A pinned `rev` grew `ref=master` and `narHash` moved. Classification: USEFUL_COMPOSITION. First destroyer (DESTROYER_refpin.md) said MUTATE: print `rev_a`/`rev_b`; keep owned 064 attach + identity_changed; do not claim identity is only narHash. MUTATE.md applied: verdict AND of `same_rev` + one-sided attach on SECOND + `identity_changed`; native flake.lock / mismatch-log ingest; rc=1 on harvest miss.

Host tests: `python3 -m unittest discover -s …/tests -v` → 28/28 OK, rc=0. `demo.sh` twice to temp logs: byte-identical. Archived `demo-1.log` / `demo-2.log` also identical.

That is not enough. Remaining attacks below were host-executed. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-refpin/refpin
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-refpin/fixtures
```

No merge onto `main`. Do not add `fetchGit` / nix eval to “prove” causation.

---

## What still works (mutation held)

Owned rec / JSON / single-node flake.lock / native mismatch log / TASK-shaped nix-error blobs: `verdict	pinned-rev-default-ref-changed-hash`, `same_rev	yes`, `rev_a` and `rev_b` both printed, `ref_attached	attached`, `attached_ref	master`, `identity_changed	yes`, rc=1.

```bash
python3 "$CLI" "$FIX/064-expected.rec" "$FIX/064-got.rec"
python3 "$CLI" "$FIX/narhash_mismatch.txt"
python3 "$CLI" "$FIX/064-expected.json" "$FIX/064-got.lock"
```

Swapped owned pair is not attach:

```bash
python3 "$CLI" "$FIX/064-got.rec" "$FIX/064-expected.rec"
# verdict	pinned-rev-default-ref-removed-hash
# ref_attached	ref_removed
# removed_ref	master
```

JSON array `[got, expected]` as the only argument is the same remove. stdin swap (`-` FIRST = got.rec, SECOND = expected.rec) is the same remove.

stdin: `-` as FIRST, as SECOND, and as the only arg for a mismatch log: harvest, rc=1. `- -` → `cannot read stdin twice` rc=1. `/dev/stdin` as FIRST and as the log path works. Process substitution, FIFO (writer after reader), filename with a space, symlink, CRLF, UTF-8 BOM: harvest.

Unseen identical records: `verdict	identical` rc=0. Hash-changed-no-ref is not harvest. One-sided attach same hash is `ref-attached-same-hash`. Missing path / `/dev/null` / empty file / directory / invalid UTF-8 / trailing comma / JSONC: rc=1, empty stdout. No args: argparse rc=2. Extra tab / duplicate field: parse error, not `identity_changed yes`. `none` is a branch name (`ref_present yes`).

Native log `equal	rev` only. Owned rec `equal	rev	lastModified	revCount` (see attack 4).

---

## Implementation

### 1. Still does not prove the attached ref caused the hash

Harvest name is `pinned-rev-default-ref-changed-hash`. `inspect()` is `same_rev and attached=="attached" and narHash_a != narHash_b`. No tree, no `fetchGit`, no nix.

Unrelated ref + the owned hash pair is still the harvest:

```bash
printf 'rev\te374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa\nnarHash\tsha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=\n' >a.rec
printf 'rev\te374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa\nnarHash\tsha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=\nref\tunrelated-topic-branch\n' >b.rec
python3 "$CLI" a.rec b.rec
```

```text
verdict	pinned-rev-default-ref-changed-hash
ref_b	unrelated-topic-branch
attached_ref	unrelated-topic-branch
identity_changed	yes
rc=1
```

Same with `ref	HEAD`. The CLI names a join on two records. It cannot tell “default-ref fallback hashed a different tree” from “two fields moved independently.” Seed question was how that ref changed the tree that was hashed. This embodiment does not ask that.

### 2. `sha256:` vs `sha256-` of the same payload is `identity_changed yes`

Same digest bytes after the prefix. String inequality is the whole identity test (`first.narHash != second.narHash`).

```bash
# dash.rec  narHash sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=
# colon.rec narHash sha256:UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=
python3 "$CLI" dash.rec colon.rec
```

```text
verdict	hash-changed-no-ref
identity_changed	yes
diverged	narHash
rc=1
```

`SHA256-` vs `sha256-` is the same miss. Attach a ref on the colon form and the harvest AND fires on a prefix-only “identity” change:

```bash
python3 "$CLI" dash.rec colon-ref.rec
# colon-ref = same payload with sha256: plus ref=master
```

```text
verdict	pinned-rev-default-ref-changed-hash
narHash_a	sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=
narHash_b	sha256:UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=
identity_changed	yes
ref_attached	attached
rc=1
```

Same payload with the same `sha256-` prefix plus attach is correctly `ref-attached-same-hash`. The false harvest is the prefix.

JSON narHash with a trailing space vs TSV-stripped same digest is also `identity_changed yes` / `hash-changed-no-ref`. TSV `strip()`s; `json.loads` does not.

### 3. Multi-node flake.lock refused

Owned `064-got.lock` has one locked node (`src`). A two-input lock (src + nixpkgs), which is the real flake.lock shape, is not a join:

```bash
python3 "$CLI" "$FIX/064-expected.json" multi.lock
```

```text
refpin: multi.lock: flake.lock has 2 locked nodes (src, nixpkgs); pass a single lock object
rc=1
```

Honest refuse. Also means native flake.lock ingest is not the harvest path for any lock with nixpkgs + the package. The CLI will not pick the node whose `rev` matches FIRST.

### 4. lastModified / revCount on the owned pair are TASK placeholders `1` / `1`

TASK prose: the two records share `lastModified` and `revCount`. The mismatch log does not contain those integers. Owned rec/JSON/lock write `lastModified	1` and `revCount	1`.

Native log:

```text
equal	rev
```

Owned rec:

```text
equal	rev	lastModified	revCount
```

The report never prints `lastModified_a` / `lastModified_b` / `revCount_*`. `equal	lastModified	revCount` is an assertion whose values are the placeholder `1`. Native ingest is the honest record: metadata absent.

Placeholder `1` vs a recovered-looking `1710000000` (same rev, same hash, no ref): `verdict	lastModified-only` rc=0. That zero is “metadata only,” not “we recovered the lock clock.”

A real-shaped blob log *with* `"lastModified":1710000000` in both objects does put `lastModified` in `equal`. Owned fixtures still do not.

### 5. THIN_WRAPPER of labeled diff — TSV path only

`inspect()` on two TSV maps is: presence of `ref`, string inequality of `narHash`, string equality of `rev`, then a lookup table of verdict names. A host reconstruction of that join is **byte-identical** to refpin on the owned pair, the swapped pair, and the unseen identical pair (`cmp` of reconstruction vs CLI stdout: IDENTICAL).

```bash
diff -u "$FIX/064-expected.rec" "$FIX/064-got.rec"
```

names the narHash line and the added `ref	master`. It does not contain `pinned-rev-default-ref-changed-hash`. The verdict is a label on that diff.

That is not KILL. Native mismatch-log ingest is not `diff`. Time axis (swap → `ref_removed`) is not `diff`. `ref_present` vs the token `none` is not `diff`. Those are the harvest composition. Constitution: a THIN_WRAPPER does not gain `fetchGit` / nix eval solely to escape this classification. Do not add them.

### 6. Swapped pair — holds

Already listed under what works. Rec swap, JSON-array reverse, stdin swap: `ref_removed`, not attach. Mismatch log plus SECOND is refused (`mismatch log is a pair; do not pass SECOND`). No remaining swap hole on owned inputs.

### 7. stdin — `-` holds; `/dev/stdin` twice does not

`-` FIRST / SECOND / log: harvest. `- -`: `cannot read stdin twice`.

`/dev/stdin /dev/stdin` with the expected rec on stdin:

```text
refpin: /dev/stdin: not a lock record
rc=1
```

First `Path.read_text` consumes the stream; the second path is empty. `-` has a specific error; `/dev/stdin` does not. `/dev/stdin` as a single FIRST or as the log path works (macOS).

### 8. HEAD warning `using 'master'` is not ingest

MUTATE.md: “A mismatch log is a pair: `refpin fixtures/narhash_mismatch.txt` discovers `master`.” The owned log has both the warning and `(ref=master)` on the got line. Strip the annotation, keep the warning:

```text
warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error: mismatch in field 'narHash' of input
  expected: sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=  (no ref field)
  got:      sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=  (no ref field)
rev in both records: e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa
```

```text
verdict	hash-changed-no-ref
ref_present_b	no
ref_attached	none
rc=1
```

`master` is discovered from the TASK `(ref=master)` annotation (or from `"ref":"master"` in the blob), not from the specimen warning. `original.ref` and `url?ref=` are in `IGNORE_FIELDS`; a lock that already had the default ref in `original` still prints `ref_present_a	no` and can harvest as attach.

### 9. `both-disagree` swallows the hash in the verdict name

`ref	HEAD` vs `ref	refs/heads/master` plus the owned hash pair: `verdict	both-disagree`, `identity_changed	yes`, `diverged	narHash	ref`. Git ref aliases are not canonicalized (MUTATE.md remaining). The verdict name hides the hash move; the `identity_changed` row still prints it.

Display cap at 96 characters: two hashes that differ after the cap print identical `narHash_a`/`narHash_b` with `…` and `narHash_capped	yes`, but comparison uses the full string (`identity_changed yes`). Honest.

Harvest hit rc=1, same as harvest miss. Distinction is the `verdict` row, not grep-on-exit. Keep that.

---

## Primitive

The object that survived DESTROYER_refpin is still real: same pinned rev, a ref that is present only on SECOND, narHash string moved, one verdict name, FIRST=earlier. Native log ingest of the owned packet is real. Swap is directional.

The ceiling is too small for the harvest *name*:

- `identity_changed` = opaque string inequality, including `sha256:` vs `sha256-` and trailing space
- `verdict	pinned-rev-default-ref-changed-hash` reads as causation; the body is a join
- `equal	lastModified	revCount` on owned recs is placeholder `1`, not recovered from the log
- flake.lock with more than one locked node is out
- the HEAD-fallback warning is not a source of `ref`
- TSV `inspect()` is a labeled diff (reconstruction IDENTICAL)

Do not grow a nix evaluator to close this. Keep the join. Stop lying about cause, hash form, and metadata equality.

---

## Mutation (what must change)

Keep the object: one verdict for same rev, one-sided attach on SECOND, narHash moved. Keep native mismatch-log ingest, time axis, `ref_present` vs token `none`, rc=1 on harvest miss, `rev_a`/`rev_b`.

Do not keep a harvest name that claims the ref changed the hash, or an `identity_changed yes` that is only `sha256:` vs `sha256-`.

1. **Join, not cause.** Rename the harvest verdict to a conjunction (`pinned-rev-ref-attached-and-hash-diverged`) or print `causation	unproven`. Unrelated `ref` + hash move must not read as “that ref changed the tree.” Do not run nix.

2. **Hash form is not identity.** `sha256:` / `sha256-` / `SHA256-` of the same payload is `hash_form` (or `identical` / not `identity_changed`). Prefix-only change plus attach is `ref-attached-same-hash`, not harvest. Strip JSON/TSV hash whitespace on the compare path, or refuse the space.

3. **lastModified only if recovered.** Drop TASK placeholders `1`/`1` from owned rec/JSON/lock, or mark them `placeholder`. Native log `equal	rev` is the owned truth unless the log/blobs actually contain the integers. Print `lastModified_a`/`lastModified_b` when claiming `equal`.

4. **Multi-node flake.lock.** Select the locked node whose `rev` matches FIRST, or keep the refuse and stop presenting flake.lock ingest as the harvest path. Do not guess a join across nixpkgs + src.

5. **Warning / original / url query.** Either parse `using 'master'` when got has no ref field, or stop saying native ingest discovers `master` from the warning. `original.ref` and `url?ref=` are either `ref_present` or an `ignored_ref` row.

6. **`/dev/stdin` twice** = `cannot read stdin twice`, same as `- -`.

If the mutation cannot do (1)+(2)+(3), the object is still a labeled TSV diff plus a regex over TASK annotations, and a later destroyer should KILL.

---

MUTATE

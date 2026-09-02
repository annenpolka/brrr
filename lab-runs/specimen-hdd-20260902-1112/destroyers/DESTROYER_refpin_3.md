# DESTROYER refpin 3

Date: 2026-09-02 15:55 JST (attacks) / 15:57 JST (record)
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0409 worker=destroyer-refpin-3
Target (archive, POST-MUTATE native ingest; no second cut):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-refpin/refpin`

sha256 `f9f7409d168bd134b502386bd5f03d009eb39745f973fac9509e5a12093905cb` (19877 bytes, 617 lines). Matches `MUTATE.md` after-hash and `DESTROYER_refpin_2.md` target. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-refpin-refpin/candidate-refpin/refpin` is **byte-identical** (`cmp` rc=0). Worktree HEAD `e91c8cd Mutate refpin join after DESTROYER_refpin.` Branch `specimen-hdd/candidate-refpin-refpin`. Parent `main` is `432f954`; `git ls-tree -r HEAD` has **no** `refpin` product path. Host Python 3.14.5. `command -v nix` empty; nix was **not** invoked. No merge onto `main`. Archive and worktree were not edited.

Origin: specimen-064 / hdd-s064. A pinned `rev` grew `ref=master` and `narHash` moved. Classification: USEFUL_COMPOSITION. Transfer onto lockident failed (digest membership ≠ field-presence vs narHash). Rejected: invented `fetchGit` / nix eval.

Prior destroyers: `DESTROYER_refpin.md` **KEEP** (post-mutate native ingest, tests 28/28). `DESTROYER_refpin_2.md` **MUTATE** leftover: rename harvest so it is a join not a cause; hash form is not identity; lastModified only if recovered. If a later mutation cannot do (1)+(2)+(3), “the object is still a labeled TSV diff plus a regex over TASK annotations, and a later destroyer should KILL.” No mutate-2 job landed. Bytes unchanged. First KEEP/MUTATE is not protection. Honor KILL if THIN_WRAPPER of caller-labeled `ref` / `narHash` rows.

Host `python3 -m unittest discover -s tests -v`: 28/28 OK, 0.909s, rc=0. `demo.sh` twice: live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 5141 bytes). Happy path is real. That is not enough.

This candidate is still a **THIN_WRAPPER of caller-labeled `rev` / `narHash` / `ref` rows**. `inspect()` is `first.rev == second.rev` AND `first.narHash != second.narHash` AND one-sided `ref` presence on SECOND, then a lookup table of verdict names. dis: `COMPARE_OP ==` on `rev`, `COMPARE_OP !=` on `narHash`, `ref_attached_of` on `.ref.present` / `.ref.value`. No tree, no NAR, no `fetchGit`, no nix. An independent replica (does not import refpin) is **byte-identical** on load-bearing columns + rc for **29/29** host cases. A python one-liner of those three field tests matches harvest yes/no on owned + swap. awk of `$1=="rev"` / `$1=="narHash"` / `$1=="ref"` names the owned harvest. DESTROYER_refpin_2 leftover (1)+(2)+(3) all still fire. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-refpin/refpin
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-refpin/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-refpin-refpin/candidate-refpin/refpin
```

No nix. Do not grow `fetchGit` / nix eval / NAR compare to escape THIN_WRAPPER. Do not send nix theater back to R1. Do not merge onto `main`. Do not merge into lockident.

---

## Honor-KILL leftover (DESTROYER_refpin_2 mutation 1–3)

| leftover | host | still? |
| --- | --- | --- |
| (1) harvest name claims the ref changed the hash; unrelated `ref` + owned hash pair must not read as that cause | `ref	unrelated-topic-branch` and `ref	HEAD` on the owned hash pair both print `verdict	pinned-rev-default-ref-changed-hash` / `attached_ref` that string / rc=1 | **yes** |
| (2) `sha256:` / `sha256-` / `SHA256-` of the same payload is not identity | prefix-only → `identity_changed	yes` / `hash-changed-no-ref`; prefix + `ref	master` → harvest AND | **yes** |
| (3) lastModified only if recovered; drop TASK placeholders `1`/`1` | owned rec/JSON/lock still `lastModified	1` / `revCount	1`; owned `equal	rev	lastModified	revCount`; native log `equal	rev` | **yes** |

Also still live from that record (not required for Honor-KILL, observed): multi-node flake.lock refused; `using 'master'` warning is not a `ref` source; `/dev/stdin /dev/stdin` is `not a lock record` not `cannot read stdin twice`; `original.ref` / `url?ref=` ignored.

Mutate claimed native ingest / time axis / `none` is a branch / rc=1 on harvest miss. Host-verified. That is not protection once (1)+(2)+(3) still hold and `inspect()` is still the labeled AND.

---

## What still works (mutation held; not a KEEP)

Owned rec / JSON / single-node flake.lock / native mismatch log / TASK-shaped nix-error blobs: `verdict	pinned-rev-default-ref-changed-hash`, `same_rev	yes`, `rev_a`/`rev_b` printed, `ref_attached	attached`, `attached_ref	master`, `identity_changed	yes`, rc=1.

```bash
python3 "$CLI" "$FIX/064-expected.rec" "$FIX/064-got.rec"
echo rc=$?
```

```text
time_axis	FIRST=earlier SECOND=later
verdict	pinned-rev-default-ref-changed-hash
rev	e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa
same_rev	yes
rev_a	e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa
rev_b	e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa
narHash_a	sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=
narHash_b	sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=
identity_changed	yes
ref_present_a	no
ref_present_b	yes
ref_a	-
ref_b	master
ref_attached	attached
attached_ref	master
removed_ref	-
equal	rev	lastModified	revCount
diverged	narHash
present_only_a	-
present_only_b	ref
source_a	tsv
source_b	tsv
rc=1
```

Swapped owned pair / JSON-array `[got, expected]` as the only argument: `verdict	pinned-rev-default-ref-removed-hash`, `ref_attached	ref_removed`, `removed_ref	master`. Unseen identical: `verdict	identical` rc=0. Hash-changed-no-ref is not harvest. `none` is a branch name (`ref_present yes`). `-` stdin harvests. `- -` → `cannot read stdin twice`. Extra tab / duplicate field: parse error.

Native log `equal	rev` only. Owned rec `equal	rev	lastModified	revCount` (placeholders `1`/`1`).

That is the whole useful surface. It is also what three string tests on caller-labeled rows already do.

---

## Implementation

`inspect()` load-bearing body:

```python
same_rev = first.rev == second.rev
identity_changed = first.narHash != second.narHash
attached = ref_attached_of(first, second)   # presence of .ref, then value !=
# harvest name:
#   identity_changed and attached == "attached" → pinned-rev-default-ref-changed-hash
```

`inspect.co_names` = `('rev', 'narHash', 'ref_attached_of', 'KNOWN', 'classify_key', 'append', 'META_KEYS', 'verdict_of', 'ref', 'value')`. `verdict_of.co_names` = `()`. dis: one `COMPARE_OP ==` on `rev`, one `COMPARE_OP !=` on `narHash`, then a loop of `classify_key` over `KNOWN` to fill spectator lists. There is no `fetchGit`, no `subprocess`, no `hashlib`, no `git`, no NAR decoder. Source token `fetchGit` / `subprocess` / `nix` / `git` / `hashlib` / `sha256`: no hits (`nar` hits are `narHash` / `NARHASH_MAX`).

`lastModified` / `revCount` vote only for `lastModified-only` / `metadata-presence` after the harvest AND has already missed. They do not enter identity. Constitution: extra TSV rows do not escape THIN_WRAPPER.

Native “ingest” is regex over TASK annotations:

```text
expected: HASH  (no ref field)
got:      HASH  (ref=master)
rev in both records: REV
```

or a JSON-blob scrape of `"ref"` / `"narHash"` / `"rev"` inside `mismatch in field 'narHash' of input '{...}', got '{...}'`. Strip `(ref=master)`, keep the specimen warning `using 'master'`: `verdict	hash-changed-no-ref`, `ref_present_b	no`. `master` is discovered from the TASK label, not from the warning.

---

## Attacks

### 1. THIN_WRAPPER of caller-labeled `ref` / `narHash` rows

Host replica of `inspect` + `format_report` (scratch `replica.py`, does not import refpin) is loadbearing-identical to CLI stdout+rc on **29/29** host cases: owned rec, swap, identical, native log, nix-error blobs, JSON pair, single-node lock, stdin FIRST, plus 21 generated TSV shapes (unrelated ref, prefix form, `none` token, empty ref, lastModified-only, meta-presence, huge hash cap, CRLF, BOM, comments, url ignored, filename with a space). `stdout_eq` on load-bearing columns (everything except `source_a`/`source_b` kind labels) and `rc_eq=True`. Fail 0.

Thin harvest AND, no format, no verdict table:

```python
harvest = (rev_a == rev_b) and (narHash_a != narHash_b) and ("ref" not in a) and ("ref" in b)
```

MATCH harvest yes/no vs CLI `verdict == pinned-rev-default-ref-changed-hash` on those **29/29**, including swap (thin no / CLI `ref_removed`) and identical (thin no / CLI `identical` rc=0).

awk of the three caller-labeled fields, without lastModified/revCount:

```awk
BEGIN{FS="\t"}
FNR==NR { if($1=="rev") ra=$2; if($1=="narHash") ha=$2; if($1=="ref"){refa=$2; pa=1}; next }
         { if($1=="rev") rb=$2; if($1=="narHash") hb=$2; if($1=="ref"){refb=$2; pb=1} }
END{
  printf "same_rev\t%s\n", (ra==rb)?"yes":"no"
  printf "identity_changed\t%s\n", (ha!=hb)?"yes":"no"
  printf "ref_attached\t%s\n", (!pa && pb)?"attached":"other"
  printf "harvest\t%s\n", (ra==rb && ha!=hb && !pa && pb)?"yes":"no"
  printf "attached_ref\t%s\n", (!pa && pb)?refb:"-"
}
```

owned rec:

```text
same_rev	yes
identity_changed	yes
ref_attached	attached
harvest	yes
attached_ref	master
```

swap: harvest no. identical: harvest no. awk == CLI those three load-bearing bits. lastModified/revCount are not in the awk. They do not vote on harvest.

Nearest ordinary workflow, host-executed:

```bash
diff -u "$FIX/064-expected.rec" "$FIX/064-got.rec"
```

names the `narHash` line and the added `ref	master`. It does not contain `pinned-rev-default-ref-changed-hash`. The verdict is a label on that diff. Native log ingest is the same three fields extracted from TASK `(ref=…)` / `(no ref field)` / `rev in both records`. That is not a lock. That is not `fetchGit`.

Constitution: a THIN_WRAPPER does not gain extra ingest formats (JSON, single-node flake.lock, mismatch-log regex) to escape classification. Those paths feed the same AND. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First KEEP is not protection. First MUTATE is not protection. Same shape as Honor-KILLed fingerhid (caller-typed equalities on path/mtime/vv) and Honor-KILLed sumext (leftover = in B not in A on caller-labeled regions).

### 2. Unrelated ref + owned hash pair is still the harvest name (leftover 1)

```bash
printf 'rev\t%s\nnarHash\t%s\n' "$REV" "$HASH_A" >a.rec
printf 'rev\t%s\nnarHash\t%s\nref\tunrelated-topic-branch\n' "$REV" "$HASH_B" >b.rec
python3 "$CLI" a.rec b.rec
```

```text
verdict	pinned-rev-default-ref-changed-hash
ref_b	unrelated-topic-branch
attached_ref	unrelated-topic-branch
identity_changed	yes
rc=1
```

Same with `ref	HEAD`. The CLI names a join on two records. It cannot tell “default-ref fallback hashed a different tree” from “two fields moved independently.” Seed question was how that ref changed the tree that was hashed. This embodiment does not ask that. Replica loadbearing_eq=True on this case. The harvest name still claims cause.

### 3. Hash form is identity (leftover 2)

Same digest bytes, `sha256-` vs `sha256:`:

```text
verdict	hash-changed-no-ref
identity_changed	yes
diverged	narHash
rc=1
```

Attach `ref	master` on the colon form: `verdict	pinned-rev-default-ref-changed-hash`. `SHA256-` vs `sha256-` plus attach: same false harvest. JSON `narHash` with a trailing space vs TSV-stripped same digest: `identity_changed	yes` / `hash-changed-no-ref` (TSV `strip()`s; `json.loads` does not). Same payload with the same `sha256-` prefix plus attach is correctly `ref-attached-same-hash`. The false harvest is the prefix.

### 4. lastModified placeholders (leftover 3)

Owned rec/JSON/lock write `lastModified	1` and `revCount	1`. The mismatch log does not contain those integers. Owned pair `equal	rev	lastModified	revCount`. Native log `equal	rev`. Placeholder `1` vs a recovered-looking `1710000000` (same rev, same hash, no ref): `verdict	lastModified-only` rc=0. That zero is “metadata only,” not “we recovered the lock clock.” The report never prints `lastModified_a` / `lastModified_b`.

### 5. Native log is TASK labels, not the warning

MUTATE.md: “A mismatch log is a pair: `refpin fixtures/narhash_mismatch.txt` discovers `master`.” The owned log has both the warning and `(ref=master)` on the got line. Strip the annotation, keep `using 'master'`:

```text
verdict	hash-changed-no-ref
ref_present_b	no
ref_attached	none
rc=1
```

`original.ref` plus `url?ref=master` with no locked `ref`: `ref_present_b	no`, `verdict	hash-changed-no-ref`. `IGNORE_FIELDS` drops them. A lock that already had the default ref in `original` still prints attach-none and can miss harvest.

### 6. Multi-node flake.lock / `/dev/stdin` twice / both-disagree

Two locked nodes (`src` + `nixpkgs`): `flake.lock has 2 locked nodes (src, nixpkgs); pass a single lock object` rc=1, empty stdout. Honest refuse. Native flake.lock ingest is not the harvest path for any lock with nixpkgs + the package. The CLI will not pick the node whose `rev` matches FIRST.

`/dev/stdin /dev/stdin` with expected rec on stdin: `refpin: /dev/stdin: not a lock record` rc=1. `- -` has a specific error. First `Path.read_text` consumes the stream.

`ref	HEAD` vs `ref	refs/heads/master` plus the owned hash pair: `verdict	both-disagree`, `identity_changed	yes`, `diverged	narHash	ref`. Git ref aliases are not canonicalized. The verdict name hides the hash move; the `identity_changed` row still prints it.

---

## Primitive

Reality-stripped operation: parse two maps of `rev` / `narHash` / optional `ref` (TSV, JSON lock object, single locked flake node, or regex over TASK `(ref=…)` annotations); `same_rev = rev_a == rev_b`; `identity_changed = narHash_a != narHash_b`; `attached = (not ref_a) and ref_b`; print a verdict name for that conjunction; exit 1 unless identical/metadata-only.

Nearest ordinary workflow: `diff -u` of the two records, or the awk / one-liner above. Seeing the same `rev`, a `narHash` line that moved, and `ref	master` only on SECOND still leaves “did that ref change the tree that was hashed?” as a hand join — but this CLI does not ask a fetcher. `demo.sh` already names `diff` as the nearest operation.

Observable capability lost if refpin vanishes: **none** beyond a named sticker. The caller already labeled both identities. Native log “ingest” reprints TASK `(ref=master)`. JSON/lock ingest reprints the same three fields. `ref_present` vs token `none` and swap → `ref_removed` are formatting around presence. They do not observe a default-ref fallback.

That is why this is KILL, not MUTATE. The *question* (a detached-HEAD fetch of a pinned rev fell back to `master` and hashed a different tree) is a real debugging object. This embodiment does not ask it of a repo, a NAR, or `fetchGit`. It asks string equality/inequality/presence on caller-labeled rows. Adding nix eval / `fetchGit` / a multi-node lock walker would be implementing the harvest this artifact failed to embody — a new harvest, not a patch of the AND. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” DESTROYER_refpin_2 already said: if a later mutation cannot do (1)+(2)+(3), KILL. No mutation landed. (1)+(2)+(3) still fire. First KEEP is not protection. First MUTATE is not protection.

Hardcoded ceiling:

- harvest = `same_rev` and `narHash` string `!=` and one-sided `ref` on SECOND
- `identity_changed` = opaque string inequality, including `sha256:` vs `sha256-` and JSON trailing space
- `verdict	pinned-rev-default-ref-changed-hash` reads as causation; the body is a join
- `equal	lastModified	revCount` on owned recs is placeholder `1`, not recovered from the log
- flake.lock with more than one locked node is refused
- the HEAD-fallback warning is not a source of `ref`; `original.ref` / `url?ref=` ignored
- TSV `inspect()` is a labeled diff (replica IDENTICAL 29/29)
- no nix, no `fetchGit`, no NAR, no refname canonicalization
- a leftover replica already computes harvest + rc

Do not grow a nix evaluator to escape THIN_WRAPPER. Do not merge this join onto `main`. Do not merge into lockident. Do not send nix theater back to R1. Honor KILL. Dreamer ancestry is not protection. First KEEP/MUTATE is not protection.

Archive stays under `lineages/candidate-refpin/`.

KILL

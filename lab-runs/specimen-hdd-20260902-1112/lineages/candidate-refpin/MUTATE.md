# MUTATE refpin

CLI sha256 before: `9e579a91bbacada6276bd23ba68f87c043644daa0be6a5ba2e732cab11adaffe` (4424 bytes, DESTROYER_refpin.md)
CLI sha256 after:  `f9f7409d168bd134b502386bd5f03d009eb39745f973fac9509e5a12093905cb` (19877 bytes)

Date: 2026-09-02. Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-refpin-refpin` (branch `specimen-hdd/candidate-refpin-refpin`, commit `e91c8cd`). Not merged to `main`. Binary name still `refpin`. No nix.

From DESTROYER_refpin.md: keep the object (a default ref attached to a pinned rev changed narHash identity). Do not keep a labeled `diff` that only replays two TSV maps.

## What changed

1. **Harvest verdict is the AND.** `verdict	pinned-rev-default-ref-changed-hash` only when `same_rev` and one-sided attach on SECOND and `identity_changed`. Other combinations have other names: `hash-changed-no-ref`, `ref-attached-same-hash`, `both-disagree`, `both-same-ref-changed-hash`, `lastModified-only`, `metadata-presence`, `rev-diverged`, `identical`, `pinned-rev-default-ref-removed-hash`. `identity_changed` with `ref_attached none` is `hash-changed-no-ref`, not the harvest.

2. **Presence is not the `none` token.** `ref_present_a` / `ref_present_b` are `yes|no`. Omitted prints `ref_a	-`. A branch named `none` prints `none` with `ref_present yes`. `ref<TAB>` is present-empty, not a parse error. Owned `064-expected.rec` omits the key (the lock had no ref field).

3. **Native ingest.** flake.lock / nix input JSON objects (`rev`, `narHash`, optional `ref`, ignore `url`/`type`). A mismatch log is a pair: `refpin fixtures/narhash_mismatch.txt` discovers `master`. TASK-shaped nix error JSON blobs too. Garbage JSON is `not a lock record`. `demo.sh` is no longer only handwritten `.rec` that already contains `master`.

4. **FIRST/SECOND is the time axis** (`time_axis	FIRST=earlier SECOND=later`). Swapped 064 is `ref_attached	ref_removed` / `verdict	pinned-rev-default-ref-removed-hash`, not attach. Both revs print; `rev` (the pinned name) only when `same_rev yes`. Duplicate keys error. Extra tab in a value errors, not `identity_changed yes`.

5. **lastModified/revCount are metadata.** Value inequality is `diverged`. One-sided presence is `present_only_a` / `present_only_b`, never the same row as `100` vs `200`. Owned rec/JSON fixtures carry the TASK-shared pair as equal placeholders `1` / `1` (the mismatch log does not include the integers). Native log `equal` is only `rev`.

6. **rc=1 on harvest miss.** rc=0 only for `identical`, `lastModified-only`, `metadata-presence`. Harvest hit, harvest miss, swapped remove, rev diverge: rc=1. `-` is stdin. narHash longer than 96 characters is capped on stdout (`narHash_capped yes`); comparison still uses the full string. No `--check` flag.

7. **Tests the parent suite could not see.** Same hash different ref; one-sided attach same hash; different rev same hash; lastModified value vs presence; missing rev; empty vs omitted vs `none` vs `NONE`; swapped owned pair; hash-changed-no-ref; `-` stdin; `url`/`type` ignored; both refs different; extra tab; duplicate field; native log; nix-error blobs; JSON lock; flake.lock; not-a-lock-record; huge narHash cap.

## Tests / demo

`python3 tests/test_refpin.py` twice: 28 OK.

`./demo.sh` twice: byte-identical (`demo-1.log` / `demo-2.log`). Demo wrapper exits 0. Native log / JSON / owned rec print the harvest and `rc=1`. Swapped pair `ref_removed`. Hash-changed-no-ref `rc=1`. Identical `rc=0`.

New fixtures: `064-expected.json`, `064-got.json`, `064-got.lock`, `nix-error.txt`.

## Remaining failures (not faked)

- This still does not prove the attached ref *caused* the hash. It names the join on two records. No `fetchGit`, no nix eval.
- Unpinned fetch (no `rev`) is still `missing rev` / `not a lock record`. Fully pinned remains grammar.
- `sha256:` vs `sha256-` of the same digest is still opaque `identity_changed yes`.
- flake.lock with more than one locked node is refused (`pass a single lock object`), not a guessed join.
- Owned `lastModified`/`revCount` integers are TASK placeholders, not recovered from the log.
- Git ref aliases (`HEAD` vs `refs/heads/master`) are `both-disagree`. No refname canonicalization.
- JSONC / trailing commas / Nix attrsets are `not a lock record`.
- Harvest hit is rc=1 (not identical), same as harvest miss. The `verdict` row is the distinction; exit is not a grep-found-it code.

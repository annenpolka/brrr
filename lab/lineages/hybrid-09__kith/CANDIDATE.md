# hybrid-09 — kith

## Primitive

Given a **commit or a diff** (never FILE:LINE), print dest-tree leftovers of that change's **natal record**: a typed binding whose name inflects. One dest line is one leftover, `via=claim|kin|both`.

A leftover *claim* is a typed old value still asserted (version `0.3.0` is not `0.3`; October is not integer `10`; a quoted JSON key is a binding). Unpaid natal *kin* is an inflected old name still speaking (`t1` ↔ `T1` ↔ `driftDelay` when the line itself renamed). `via=both` is the object concatenation cannot name.

## Why this might not exist

`ember` leftover-matches claims a diff made false. It drops an unchanged value (`t1 = 15` → `driftDelay = 15` has no value fact) and does not case-fold a short natal (`t1` ↛ `T1`). `erst` leftover-matches unpaid kin of a birth cohort. It truncates `0.3.0` to `0.3` and skips integer `10` as a common number, so JSON prose `plugin version 0.3.0` and `timeout default is 10` are the wrong object.

Reviewers have a SHA. The dest tree still believes the old world in two ways that are one debt: the old *fact* (typed) and the old *name* (inflected). Piping ember into erst is two ranked lists. `--no-fuse` is that concatenation. The missing verb is: **the natal record of this change, still speaking**.

Discarded as concatenation: print ember afterimages next to erst owing members. That is two scores, never a joint. `T1 is 15 seconds` is one leftover.

## How to run

From this worktree (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./kith ./demo.sh
./kith self-test
./demo.sh                 # exits 0; fixture + sitbone e9b0f75
./kith --help
./kith -C <repo> HEAD
./kith -C <repo> e9b0f75
./kith -C <repo> A B
git diff A B | ./kith --diff - -C <repo>
./kith --json --check HEAD
```

Exit `0` none, `1` leftovers, `2` usage/error. `FILE:LINE` exits 2.

## Empirical transcript

### Before the improvement (v0.1)

Joint fixture (rename `t1`→`driftDelay` with `15` unmoved, bump `present_threshold`/`version`/`timeout`, flip cache). `./kith HEAD`:

```
kith: 10 leftovers  …  both=10 claim=0 kin=0

NATAL t1↔driftDelay  15   core.py:1 RENAME
  both   68 docs    docs/how to set (t1).md:3   T1 is 15 seconds.

NATAL present_threshold↔presentThreshold  0.4 → 0.45
  both   68 docs    docs/how to set (t1).md:4   The present_threshold is 0.4.

NATAL  (fused across records)
       VERSION  0.3.0 → 0.7.0; HOOK_TIMEOUT  10 → 30
  both  100 docs    docs/how to set (t1).md:5   plugin version 0.3.0, hook timeout 10 seconds.
```

`--no-fuse` splits that last dest line into two rows (version natal + timeout natal). Default fuse is one leftover. Intact `PORT=8080` is quiet. `DEBUG is True` is not the `ENABLE_CACHE` flip. October is not leftover `10`.

sitbone `e9b0f75` (PresenceArbiter `threshold`/`0.4` → `presentThreshold`/`0.45`):

```
kith: 5 leftovers  …  both=3 claim=0 kin=2

NATAL threshold↔absentThreshold     PresenceArbiter.swift:35 RENAME
  kin    56 docs    docs/adr/0019-….md:12   smoothedScore >= threshold ? .present
  kin    56 docs    docs/adr/0019-….md:77   明示的に `threshold` を渡している

NATAL  (fused across records)
       threshold↔presentThreshold  0.4 → 0.45; threshold↔absentThreshold
  both  100 docs    CLAUDE.md:329   @Test("… threshold 0.4）")
  both  100 docs    CLAUDE.md:332   @Test("… threshold 0.4）")
  both   68 docs    docs/adr/0019-….md:76   既存の `threshold: Double = 0.4`
```

The CLAUDE.md `via=both` lines are the joint object (ember's leftover claim ∧ erst's leftover name). SiteObserver.threshold=0.7 is absent (homonym). Failures:

1. A 1-to-2 split greedy-paired `self.threshold = threshold` with `self.absentThreshold = …`, minting a competing rename natal. Concatenation of the two parents would keep both lists; the dest leftover `threshold` is one record.
2. Test comments `// 3回目で0.4を下回る` scored 40 (value-only, no name) and died at min-score 55. erst reports them as natal-literal echoes. ember never did (no nearby name). The joint record still owns that `0.4`.

### After the improvement (v0.2)

Forced by that sitbone transcript, not a feature list:

1. **1-to-N split is one natal.** Competing renames of the same old ident fold; adopted names become a set. `threshold↔absentThreshold` is no longer its own natal.
2. **Natal-literal claims in docs/tests.** Distinctive typed values (`0.4`, `0.3.0`) in tests/docs clear min-score as `via=claim` even without the name on the line. Style-domain floats (`yaw: 0.4`, `opacity(0.4)`) stay out.
3. **Migration docs are not "already paid".** File-level `file-has-new` no longer kills kin in an ADR that names both 0.4 and 0.45.
4. **Unpaired deletions are not natal records.** sitbone lint `1fcdec6` otherwise minted PUBLIC/IMPORT/ADR leftovers from every dropped line.

Same PresenceArbiter commit:

```
$ ./kith --no-color -C sitbone e9b0f75
kith: 17 leftovers  …  both=4 claim=11 kin=2

NATAL threshold↔presentThreshold  0.4 → 0.45   PresenceArbiter.swift:30 RECORD
  both  100 docs    CLAUDE.md:329           @Test("… threshold 0.4）")
  both  100 docs    CLAUDE.md:332           @Test("… threshold 0.4）")
  both  100 docs    docs/adr/0019-….md:76   既存の `threshold: Double = 0.4`
  both   78 docs    docs/adr/0019-….md:9    単一閾値(0.4)で判定している
  claim  62 test    PresenceArbiterTests.swift:177  // 3回目で0.4を下回る
  claim  62 test    PresenceArbiterTests.swift:216  // … 0.214 < 0.4
  kin    56 docs    docs/adr/0019-….md:12   smoothedScore >= threshold ? .present
  kin    56 docs    docs/adr/0019-….md:77   明示的に `threshold` を渡している
```

No SiteObserver. No competing absentThreshold natal. Test `0.4` comments are leftover *claims* of the same record that CLAUDE.md leftover-matches as `via=both`.

`1fcdec6` (lint that also renamed `t1`→`driftDelay`, `t2`→`awayDelay`), after (4): 8 natal records instead of 74; leftover `T1` in CLAUDE/README/SPEC. Still pairs some slot locals (`window↔focusedWindow`, `p1↔codingProfile`) — slot stem-containment of a generic ident, recorded as a failure.

`./demo.sh` → `passed=52 failed=0`. `./kith self-test` 0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| joint fixture (demo.sh) | rename+value+json+timeout+polarity, ugly paths, nested git | `T1 is 15` via=both; `0.3.0` full token; October quiet; PORT quiet; `--no-fuse` splits version+timeout prose |
| destroyer JSON hunk | `--diff` quoted `"version"` vs dest prose | 1 natal, prose leftover `plugin version 0.3.0` |
| destroyer dates | isolated `HOOK_TIMEOUT` / `MAX_RETRIES` | October/March not leftovers; real sentences are |
| sitbone `e9b0f75` | commit query, leftovers at HEAD | v0.1: 5 leftovers, competing rename. v0.2: 17 leftovers, one natal, test claims + ADR kin, no SiteObserver |
| sitbone `1fcdec6` | lint+rename SHA | v0.2: leftover `T1`/`T2`; 8 natals not 74. Some generic slot pairs remain |

## Surprises

- The money shot is a value that **did not move**. Ember has nothing to leftover-match. Erst leftover-matches `T1` without typing `15` as a claim of this record. `via=both` on `T1 is 15 seconds` is the proof this is not a pipe.
- Sentence-final `0.4.` is not `0.4.0`. `(?![\d.])` was the wrong boundary; `(?!\.\d)(?!\d)` is.
- A 1-to-2 hysteresis split is one natal record. Greedy line align will happily pair `self.threshold` with `self.absentThreshold` because both stem-contain `threshold`. Folding after extract is the joint, not a smarter align.
- `file-has-new` is correct for code that moved on and a lie for an ADR that documents the move.

## Failures

- No language parser. Historical trees do not recurse nested repos. Japanese bindings still do not parse (`タイムアウト = 10` is not a fact); leftover Japanese of an *English* fact still matches via the alias table. Fullwidth `１０` is not `10`.
- Generic slot stem-containment still 1:1-pairs `window`↔`focusedWindow` and `p1`↔`codingProfile` on large rewrite commits. erst v0.2 rejected leftover 1:1 unless the abandoned name is distinctive; kith still stem-pairs on slots because `threshold`↔`presentThreshold` needs it.
- Value-only `0.4` in `SPEC.md` `v0.4  カメラPresence検出` is a natal-literal false friend (gated poorly by "spec" in the path).
- `git log -L` birth follow is not in this hybrid. Siblings that share no token with the change stay invisible. The dest scan of inflected names + typed values covers the erst fixture without it; a rename that never occupied a `name: Type =` slot will miss.
- Size-cap omit is silent. Two packages named `version` are one noun.

## Suggested mutations

- Distinctive-only stem pairing on slots, with an exception when the old value moved (so `threshold`/`0.4` still pairs, `window` does not).
- `kith blame <path>:<line>`: invert the verb — given a leftover, show the change whose natal record it still speaks.
- Domain tags so `0.4`-threshold is not `0.4`-opacity without a style-word denylist.
- Occupancy: how long HEAD has held the erstwhile surface (`T1` since d3737ea).

## Kill / keep

**Keep.** The object changed. `T1 is 15 seconds` after a rename that did not move `15` is a leftover neither parent names as one row, and sitbone `e9b0f75` is simultaneously a typed `0.4` claim and inflected `threshold` kin. v0.2 came from that commit's competing rename natal and silent test comments, not from a feature list. Kill only if a later generation proves that `ember | erst` with a join key is the same object — it is not: the join key *is* the natal record, which is this verb.

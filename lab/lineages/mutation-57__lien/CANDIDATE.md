# mutation-57 — lien

## Primitive

`git diff | lien` is a CI gate on leftovers of that change's **natal record**. Default input is a unified diff on stdin. Default output is `--check`: one dest-line lien (`path:line: via: …`), silent on success, exit 1 if the dest still speaks the record as *current*. `--explain` is the human natal dump.

A leftover *claim* is a typed old value still asserted. Unpaid natal *kin* is an inflected old name still speaking. `via=both` is the joint object concatenation cannot name. CI sees the dest line, not a ranked natal report.

## Why this might not exist

`kith` (hybrid-09) fused typed claims and inflected kin at `path:line`, then *dumped* them from a SHA. `--check` was a no-op flag; the default object was a ranked report. Ember leftover-matches claims a diff made false. Erst leftover-matches unpaid kin. Reviewers have a patch on stdin. CI wants a gate: **does this diff leave dest lines that still assert the natal as current?** Piping kith into `tail` is still a dump. `--check` on kith still prints NATAL headers.

The missing verb is `git diff origin/main...HEAD | lien`. Human natal dump is opt-in `--explain`. Isolated tool, not a flag on kith.

Discarded as concatenation: `git diff | kith --check`. That is a dump with an exit code.

## How to run

From this worktree (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./lien ./demo.sh
./lien self-test
./demo.sh                 # exits 0; fixture + sitbone e9b0f75 both-rows
./lien --help
git diff | ./lien                     # CI check (default)
git diff origin/main...HEAD | ./lien
git diff | ./lien --explain           # human natal dump
git diff | ./lien --all               # CI-print the dump union
./lien --explain -C <repo> e9b0f75    # opt-in SHA
git diff | ./lien --json
git diff | ./lien -q
```

Exit `0` none, `1` leftovers (CI: current liens; `--explain`: the union), `2` usage/error. `FILE:LINE` exits 2. Garbage stdin that is not a unified diff exits 2.

## Empirical transcript

### Before the improvement (v0.1)

CLI flip only. Engine inherited from kith. `git diff HEAD^ HEAD | ./lien -C $FIX`:

```
docs/how to set (t1).md:3: both: t1↔driftDelay  15: T1 is 15 seconds.
docs/how to set (t1).md:5: both: VERSION  0.3.0 → 0.7.0; HOOK_TIMEOUT  10 → 30: plugin version 0.3.0, hook timeout 10 seconds.
```

No `NATAL` header. Exit 1. `--explain` prints the kith dump. Empty stdin is silent exit 0. `commit deadbeef\nAuthor: x` exits 2.

sitbone `e9b0f75` (`git diff e9b0f75^ e9b0f75 | ./lien -C sitbone`):

```
CLAUDE.md:329: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4）")
CLAUDE.md:332: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4）")
docs/adr/0019-presence-hysteresis.md:76: both: … 既存の `threshold: Double = 0.4`
SPEC.md:436: claim: … v0.4  カメラPresence検出
docs/adr/0019-presence-hysteresis.md:12: kin: … smoothedScore >= threshold ? .present
```

17 dest-line liens, 4 `via=both`. The money-shot both-rows are real. The CI gate also failed the build on:

1. `SPEC.md:436 v0.4 カメラPresence検出` — version heading, not float `0.4`. kith already named this false friend; as a *dump* it was noise, as a *gate* it is a lie.
2. Two kin-only ADR quotes of the old identifier. Erst's object. The ADR is documenting the rename.
3. ADR-0019:176–177, which already name `0.45` on the same line (migration prose).

`--explain` was the right union. Default `--check` was still kith's union in linter clothing.

### After the improvement (v0.2)

Forced by that sitbone CI transcript, not a feature list:

1. **Float `0.4` is not version-label `v0.4`.** Lookbehind for floats excludes a leading letter. Version tokens (`0.3.0`) still match prose `v0.3.0`.
2. **Default check is a current lien.** `via=both` always. Live test/code/config/assert claims still fail CI. Kin-only is `--explain`. Docs claims that already name the new value are migration prose, not a fail. `--all` CI-prints the union.

Same PresenceArbiter commit, default check (12 liens, not 17):

```
$ git -C sitbone diff e9b0f75^ e9b0f75 | ./lien --no-color -C sitbone
CLAUDE.md:329: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4）")
CLAUDE.md:332: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4）")
docs/adr/0019-presence-hysteresis.md:76: both: … `threshold: Double = 0.4`
docs/adr/0019-presence-hysteresis.md:9: both: … 単一閾値(0.4)で判定している
SPEC.md:145: claim: … `normalized > 0.4` → `.present`。
Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: claim: … // 3回目で0.4を下回る
```

No `v0.4`. No `: kin:`. Both-rows still fail the gate. `--explain` still shows 16 leftovers (the union minus the false friend), including kin. `--all` restores kin in check format.

`--explain` on the same pipe:

```
lien: 16 leftovers  diff → worktree  both=4 claim=10 kin=2

NATAL threshold↔presentThreshold  0.4 → 0.45   PresenceArbiter.swift:30 RECORD
  both  100 docs    CLAUDE.md:329           @Test("… threshold 0.4）")
  both  100 docs    CLAUDE.md:332           @Test("… threshold 0.4）")
```

No SiteObserver. No competing absentThreshold natal. Test `0.4` comments remain leftover *claims* of the same record CLAUDE.md leftover-matches as `via=both`.

`./demo.sh` → `passed=78 failed=0`. `./lien self-test` 0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| joint fixture (demo.sh) | `git diff \| lien` rename+value+json+timeout+polarity | T1 is 15 via=both as `path:line: both:`; no NATAL header; `--explain` dumps natal; `--no-fuse` splits version+timeout prose |
| garbage stdin | `commit deadbeef` piped | exit 2, names unified diff |
| empty stdin | `printf '' \| lien` | silent exit 0 |
| destroyer JSON hunk | stdin `"version"` vs dest prose | 1 natal, prose leftover `plugin version 0.3.0` as dest-line lien |
| destroyer dates | isolated `HOOK_TIMEOUT` / `MAX_RETRIES` | October/March not leftovers; real sentences are |
| sitbone `e9b0f75` | `git diff e9b0f75^ e9b0f75 \| lien -C sitbone` | v0.1: 17 liens including `v0.4` + kin. v0.2: 12 current liens, 4 both-rows, no `v0.4`, no kin. `--explain` 16 leftovers, one natal |

## Surprises

- kith's `--check` never changed output. Making check the *default* on stdin made the false friend `v0.4` into a would-be red CI, which is what forced the float/version lookbehind. The dump could live with it; the gate could not.
- The CI object is not "every leftover kith would print". Kin-only ADR quotes are the dest still *saying the old name* while documenting the move. Failing the build on that is erst, not the natal record as current fact.
- `T1 is 15 seconds` after a rename that did not move `15` is still via=both on one dest-line lien. Ember has no value fact. Erst leftover-matches `T1` without typing `15`. The joint survives the CLI flip.
- Sentence-final `0.4.` is not `0.4.0`. `v0.4` is not `0.4`. `v0.3.0` is still `0.3.0`. The lookbehind is typed.

## Failures

- No language parser. Historical trees do not recurse nested repos. Japanese bindings still do not parse (`タイムアウト = 10` is not a fact); leftover Japanese of an *English* fact still matches via the alias table. Fullwidth `１０` is not `10`.
- Generic slot stem-containment still 1:1-pairs `window`↔`focusedWindow` on large rewrite commits (inherited; sitbone e9b0f75 does not hit it).
- ADR-0019:25 (`ema値が0.4の境界`) still fails CI: a docs claim with no new value on the line. The ADR is later documentation of the bug the commit fixed. `--explain` is honest; default check is still a bit hungry.
- ADR-0001 `normalized score > 0.4` is a different document's current-looking leftover. Maybe right, maybe a domain tag away.
- Size-cap omit is silent. Two packages named `version` are one noun.
- TTY-no-args usage error is not exercised in demo.sh (agent stdin is a pipe); self-test covers empty and garbage stdin instead.

## Suggested mutations

- Distinctive-only stem pairing on slots, with an exception when the old value moved (so `threshold`/`0.4` still pairs, `window` does not).
- `lien blame <path>:<line>`: invert the verb — given a leftover, show the change whose natal record it still speaks.
- Domain tags so ADR-0001's 0.4-fusion is not PresenceArbiter's 0.4-threshold.
- Occupancy: how long HEAD has held the erstwhile surface (`T1` since d3737ea).
- GitHub Actions annotations (`::error file=,line=`) as `--annotate` on the CI object.

## Kill / keep

**Keep.** The object changed. kith's default is a SHA dump; lien's default is `git diff |` as a gate whose dest-line is the leftover, and sitbone `e9b0f75` both-rows fail that gate without also failing `v0.4` or kin-only ADR quotes. v0.2 came from running that commit as CI, not from a feature list. Kill only if a later generation proves `kith --check` with stdin auto-detect is the same object — it is not: kith still prints a ranked natal report, and its `--check` does not filter current liens from the union.

# mutation-68 — sire

## Primitive

Given a leftover **locator** (`FILE:LINE` or stdin locators), print the change whose **natal record** that line still speaks: natal commit + old→new + via=claim|kin|both.

lien is `git diff |` as a CI gate: does this *change* leave dest lines that still speak the natal? sire inverts the verb. The leftover is the input. The natal change is the output. One locator, not a dump of every leftover.

## Why this might not exist

Reviewers land on a stale line (`CLAUDE.md:329`, a test comment, an ADR quote) and ask *which change this leftover still belongs to*. `git blame` answers who last touched the line (often the commit that *wrote* the leftover, not the one that made it false). ember leftover-matches claims a *given* diff made false — no invert. lien refuses `FILE:LINE` on purpose. Piping `lien` into `git log -S` is still a token search.

The missing verb is `sire CLAUDE.md:329`. Not a leftover-name walker.

Discarded as concatenation: `git blame` plus `git log -S 0.4`. That is recency of a token, never a natal record.

## How to run

From this worktree (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./sire ./demo.sh
./sire self-test
./demo.sh
./sire --help
./sire -C <repo> CLAUDE.md:329
./sire --explain -C <repo> docs/adr/0019-presence-hysteresis.md:12
printf 'CLAUDE.md:329\nSPEC.md:436\n' | ./sire -C <repo>
```

Exit `0` sire found, `1` none, `2` usage/error.

## Empirical transcript

### Before the improvement (v0.1)

CLI invert + pickaxe candidates + naive substring leftover-match. `./sire -C sitbone CLAUDE.md:329`:

```
CLAUDE.md:329: e9b0f75: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")
CLAUDE.md:329: 078d2e3: claim: FOREGROUND_STYLE  0.5 → 0.2: …
CLAUDE.md:329: 1fcdec6: claim: prevPhase↔previousPhase  0: …
CLAUDE.md:329: 50e5311: claim: CORNER_RADIUS  4 → 3: …
```

The money shot is real: **e9b0f75**, via=both, not `git blame`'s `a2512fe`. Naive matching also leftover-matches `0.5` inside `0.50` and `4` inside `0.4`.

Wrong natal, forced by that transcript:

1. `SPEC.md:436` `v0.4  カメラPresence検出` sires `e9b0f75` (and `CORNER_RADIUS 4`). Float `0.4` is not version-label `v0.4`.
2. ADR-0019:12 (kin-only `threshold` quote) ranks `CATEGORY core → core.state` above e9b0f75.
3. Joint fixture `T1 is 15 seconds` is a miss: pickaxe `-S 15` does not see an unmoved value; `-S T1` does not see a commit that deleted `t1`.
4. Paid `driftDelay = 15` still sires the t1 natal (substring `15`).

### After the improvement (v0.2)

Forced by that sitbone invert transcript, not a feature list:

1. **Typed leftover-match, same-line only.** `needle_value` lookbehind: `v0.4` is not float `0.4`; `0.50` is not `0.5`; integer `4` is not inside `0.4`.
2. **Inflected pickaxe.** Leftover `T1` also searches `-S t1`, so an unmoved `15` is still reachable.
3. **Kin of a value-only natal whose name never inflected is not unpaid kin.** Later `version` bumps are not sires of leftover `"version": "0.3.0"`.
4. **Shadow claims.** If the leftover already speaks a named natal (`via=both`), drop nameless `0.4` claims from other changes (`RESPONSE 0.4→0.15`).

Same locators:

```
$ ./sire --no-color -C sitbone CLAUDE.md:329
CLAUDE.md:329: e9b0f75: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")

$ ./sire --no-color -C sitbone SPEC.md:436
# (silent) exit 1

$ ./sire --explain --no-color -C sitbone docs/adr/0019-presence-hysteresis.md:12
sire: docs/adr/0019-presence-hysteresis.md:12  leftover still speaks 1 natal change(s)
  leftover  let status: PresenceStatus = smoothedScore >= threshold ? .present : .absent
  sire      e9b0f75  Implement dual-threshold hysteresis in PresenceArbiter
  natal     threshold↔presentThreshold  0.4 → 0.45   PresenceArbiter.swift:30
  via       kin
```

Joint fixture: `T1 is 15 seconds` → rename commit, via=both. Paid `driftDelay = 15` is silent exit 1. kizu `plugin/plugin.json:4` leftover `0.3.0` → `53cbd1a` `0.3.0 → 0.3.1` via=both, no later-bump kin.

`./demo.sh` → passed=41 failed=0. `./sire self-test` 0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| joint fixture | `present_threshold is 0.4` | bump commit, via=both |
| joint T1 | `T1 is 15 seconds` | v0.1 miss; v0.2 rename commit via=both (`T1`→`t1` pickaxe) |
| joint paid line | `core.py:1` `driftDelay = 15` | v0.1 sire; v0.2 exit 1 |
| sitbone `CLAUDE.md:329` | leftover of e9b0f75 | v0.1 e9b0f75 + hungry claims; v0.2 **only** e9b0f75 via=both. blame is a2512fe |
| sitbone `SPEC.md:436` | `v0.4` heading | v0.1 sires e9b0f75; v0.2 exit 1 |
| sitbone ADR:12 | kin-only quote | v0.1 CATEGORY ranked first; v0.2 e9b0f75 via=kin only |
| kizu `plugin/plugin.json:4` | leftover `0.3.0` | v0.2 first bump via=both, no BUFFER `0`, no later-bump kin |
| lien dest-line stdin | `path:line: via: …` | parses as locator |

## Surprises

- The invert is only interesting when it **disagrees with git blame**. CLAUDE.md:329 is that disagreement (`a2512fe` vs `e9b0f75`).
- Pickaxe cannot see a natal whose *value did not move*. That is exactly the joint object lien/kith exist for (`t1=15` → `driftDelay=15`). Inflecting the leftover name is the invert of dest-scanning inflected kin.
- `0.50` leftover-matching natal `0.5` is the same class of lie as `v0.4` leftover-matching `0.4`.
- A second `0.4` natal in the same history (`RESPONSE 0.4→0.15`) still leftover-matches a threshold leftover as via=claim. via=both on the locator is the lock; concatenation of every 0.4-changing commit is not.

## Failures

- No language parser. Historical trees do not recurse nested repos. Japanese bindings still do not parse as facts; leftover Japanese of an English fact still matches via the alias table. Fullwidth `１０` is not `10`.
- Value-only leftovers (`// 3回目で0.4を下回る`) can still attract every distinctive `0.4` natal in range when no via=both lock exists. Domain tags would close it.
- `--max-commits` 60 / `--limit` 5 omit silently.
- Generic slot stem-containment is inherited from lien's natal extract.

## Suggested mutations

- Domain tags so ADR-0001's 0.4 is not PresenceArbiter's 0.4 is not RESPONSE's 0.4, even on value-only leftovers.
- Occupancy: how long HEAD has held the leftover surface.
- `sire` as a filter on `lien` dest-lines: default already parses them; a `--from-diff` that runs lien internally is concatenation.

## Kill / keep

**Keep.** The object changed. lien's default is `git diff |` as a gate; sire's default is `FILE:LINE` as a pointer to the natal *change*, and it is not git blame. v0.2 came from running sitbone `CLAUDE.md:329` / `SPEC.md:436` / ADR:12 as invert queries, not from a feature list. Kill only if a later generation proves `git log -S` plus `git blame` is the same object — it is not: blame names `a2512fe`, pickaxe recency names `094769d`, sire names `e9b0f75`.

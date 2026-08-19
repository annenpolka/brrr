# mutation-56 — berth

## Primitive

From a **commit or a diff** (never FILE:LINE), recover every **birth cohort** that change still owes at HEAD, and berth leftover occupancy at the leftover **identity birth** — not last-touch of the leftover line.

Natal keys **inflect**: `t1` ↔ `driftDelay` because the same line used to say `t1`. `since` is when that identity became unpaid (the rename). `born` is when this path first held the identity (pickaxe). A formatter that rewrites the line without changing identity count is neither.

## Why this might not exist

`brood` (reimpl-07) shipped leftover occupancy as `git blame` of the leftover *line*. sitbone `SPEC.md:110` `T1` therefore blames `a2512fe` (initial docs / last-touch). That SHA is *before* `t1` became `driftDelay`. The leftover has not been unpaid since the root commit; it became unpaid at the rename `1fcdec6`. Last-touch also moves when a docs rewrite keeps `T1` and only changes surrounding prose.

`erst` suggested occupancy as "T1 since d3737ea" by following identity, then `brood` shipped hunk last-touch instead. `git blame` answers who last touched a line. `git log -S` answers when an identity count changed. The missing verb is leftover occupancy as **identity birth**.

## How to run

```bash
chmod +x ./berth ./demo.sh
./berth --selftest
./demo.sh                 # exits 0
./berth --no-color -C /path/to/sitbone 1fcdec6
./berth --json --check HEAD
git diff | ./berth -
```

Exit codes: `0` ok, `1` `--check` found unpaid kin, `2` usage / not a repo / FILE:LINE.

## Empirical transcript

Ancestor `brood` on sitbone `1fcdec6`:

```
owing  SPEC.md:110: - `T1` = 15秒（FLOW→DRIFT閾値）
       (holds T1) since a2512fe
owing  README.md:130: | FocusStateMachine | … T1=15s, T2=90s |
       (holds T1) since 3a21045
```

`a2512fe` is last-touch of the SPEC line (root docs). The rename is `1fcdec6`.

### Before the improvement (v0.1)

`since` = leftover identity birth as unpaid: mentions that already existed berth at the **rename commit**, not blame. Fixture: introduce `t1`+`T1` → rewrite docs keeping `T1` → rename `t1`→`driftDelay`. `since` is the rename, not the rewrite.

sitbone `1fcdec6`: SPEC `T1` is `since 1fcdec6`, not `a2512fe`. That is the flip.

Failure forced by the same dogfood: every leftover collapsed to the query SHA. README, SPEC, and `FocusStateMachineEdgeCaseTests` all said `since 1fcdec6`. Occupancy was true (they became leftover at the rename) and tautological (the change header already names that SHA). `git log --reverse --max-count=1 -S` also dropped identity intro when a later formatter commit sat on the path without changing T1 count — stdin occupancy went missing on `docs/how to set (t1).md`.

### After (v0.2)

Pickaxe walks `--reverse` without `--max-count` (the cap is applied *before* pickaxe). `born` is path identity intro. `since` stays leftover-as-unpaid (the rename). Human line shows both when they differ.

Same fixture. Rewrite is neither clock:

```
owing  docs/how to set (t1).md:3: T1 is 15 seconds.
       (holds T1) since <rename> born <introduce>
```

Same sitbone lint commit. SPEC last-touch `a2512fe` is now `born`, not `since`:

```
$ ./berth --no-color -C sitbone 1fcdec6
owing  …  nee t1↔driftDelay
owing  SPEC.md:110: - `T1` = 15秒（FLOW→DRIFT閾値）
       (holds T1) since 1fcdec6 born a2512fe
owing  README.md:130: | FocusStateMachine | … T1=15s, T2=90s |
       (holds T1) since 1fcdec6 born 3a21045
owing  Tests/…/FocusStateMachineEdgeCaseTests.swift:25: // > t2(90)
       (holds t2) since 1fcdec6 born 9f97c6c
alias  Sources/SitboneCore/SessionProfile.swift:36: case flowThreshold = "t1"
```

PresenceArbiter `e9b0f75`: leftover `0.4` tests `since e9b0f75 born a95da43`. ADR `threshold` `since e9b0f75 born 98a8009`. SiteObserver is gone.

`aka` cannot produce this: `t1` and `driftDelay` are not an inflection class. `owe` cannot produce this: the `15` never moved. `brood` cannot produce this: it blames `a2512fe`.

kizu `fb355e0`: smokes. `./demo.sh` exits 0.

v0.2 is: leftover `since` = unpaid identity birth (rename if the mention predates it), `born` = pickaxe intro on that path, ugly-path `:(literal)`, no `--max-count` on reverse pickaxe.

## Dogfood targets

- Synthetic ugly fixture (spaces, parens, nested git, docs rewrite between birth and rename, `t1`/`T1`/`present_threshold`) — `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — PresenceArbiter `e9b0f75`, rename `1fcdec6` (SPEC T1 not `a2512fe`)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `fb355e0`

## Surprises

- `git log --reverse --max-count=1 -S T1` is empty when the newest commit on the path is a rewrite that *keeps* T1. Git applies the cap before pickaxe. Oldest identity intro requires `--reverse` without the cap (or newest-first and last line).
- sitbone SPEC `T1` last-touch *is* path identity intro (`a2512fe`, the root). The interesting clock is not "older than blame" — blame is already the root — but "later than blame": leftover-as-unpaid starts at the rename `1fcdec6`. Brood's suggested "T1 since d3737ea" would still not be last-touch, but it is natal *code* birth, already on the owing header. The leftover's own identity birth as leftover is the rename.
- README `T1` is `born 3a21045` (Add README), tests `t2` are `born 9f97c6c` (coverage). Same `since 1fcdec6`. Two clocks; one blame SHA would have collapsed them only when last-touch happened to equal intro.
- `:(literal)` is required for `docs/how to set (t1).md` so parens are not pathspec magic.

## Failures

- Same-magnitude floats in a different domain still collide as echo (`GazeDetectorTests` `yaw: 0.4`).
- Pickaxe per leftover path can be slow on huge histories (cached per `(path, needle)` in-process).
- Path B (change-as-birth clusters) still has no occupancy clocks.
- `born` is file-grain pickaxe, not `git log -L` of the leftover line. A later copy of `T1` onto a file that already had a different `T1` still berths at the file's first T1.
- Stdin of a *truly uncommitted* rename treats `change.parent` (HEAD) as the rename SHA, which is only right when the rename is already committed and the pipe is `git show`.

## Suggested mutations

- `git log -L` on the leftover line so `born` is line identity, not file pickaxe.
- Occupancy on Path B splits.
- `--blame` debug lane: print last-touch next to `since`/`born` so the three clocks are visible (rename / identity intro / formatter).
- Domain tags: leftover `0.4` yaw vs threshold.

## Kill / keep

**Keep.** `berth 1fcdec6` producing leftover `T1` on SPEC `since 1fcdec6 born a2512fe` — not brood's `since a2512fe` — is the occupancy flip erst listed and brood inverted. `since` is leftover identity birth. `born` is why occupancy did not die as a copy of the query SHA. Worth mutating (line-grain `-L`, Path B clocks) rather than killing.

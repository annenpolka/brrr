# candidate-10 — also

## Primitive
Given a source location (or a unified diff), recover the line's **birth cohort** — other lines added in the same introducing commit that shared distinctive tokens — and report which of those siblings still agree with the line and which have drifted.

## Why this might not exist
`git blame` answers who last touched a line. Clone detectors answer what looks like the line *now*. Co-change miners answer what *repeatedly* shipped together. None of them answer the question you actually have when you change `TIMEOUT = 30` to `60`: *what was born with this value, and did I leave it behind?* That other mention may have been last-touched by a formatter, may no longer look like a clone, and may have co-changed only once — at birth.

## How to run
From this worktree:

```bash
./also --selftest
./demo.sh
./also FILE:LINE
./also -C /path/to/repo FILE:LINE --json --check
git diff | ./also --diff -
```

## Empirical transcript
v0.1 is commit `288025f`. v0.2 is the improvement: keys come from the current line's literals (plus a 1-to-1 replaced ancestral literal), identifiers are not taken from inside strings, unique literals still echo across the tree, and numeric hits in ranges / OS versions / UI style args are dropped.

### Before (v0.1)

Fixture: `TIMEOUT = 30` introduced together with docs (weird filename with spaces and parens), tests, yaml, generated file, and `src/foo bar/timeout.py`. A later commit changes only `config.py` to `60`.

```
$ ./also --no-color -C "$FIX" config.py:1
query  config.py:1
       TIMEOUT = 60
birth  b44d78531784  2026-08-20T00:11:51+09:00  introduce timeout=30 and retry=3
       was: TIMEOUT = 30
keys   timeout, 30

drift deploy/timeout.yaml:1: timeout: 30
       (query lost 30)
drift docs/how to set (timeout).md:3: The service timeout is 30 seconds.
       (query lost 30)
drift generated/timeout.gen.py:2: TIMEOUT = 30
       (query lost 30)
drift src/foo bar/timeout.py:1: TIMEOUT = 30  # keep in sync with config.py
       (query lost 30)
drift tests/test_timeout.py:4: assert TIMEOUT == 30
       (query lost 30)
ok    docs/how to set (timeout).md:1: # Timeout
ok    tests/test_timeout.py:1: from config import TIMEOUT, RETRY
```

`--check` exits 1. `--diff` on a further uncommitted `TIMEOUT = 90` still reports the unpaid `30` siblings.

Real sitbone (`Sources/SitboneCore/SitboneCore.swift:107`, `driftDelay: TimeInterval = 15`):

- Correctly recovered birth as the v0.1 commit where the line was `t1: TimeInterval = 15` inside a combined init.
- Then exploded: keys included `init`, `90`, `5`, `flowrecovery`, so almost every `public init(` in that first commit was flagged `drift` (`query lost init`). `SPEC.md` `T2 = 90` was false-drift because 90 lived on the ancestral mega-line.

Real sitbone (`PresenceArbiter.swift:33`, `presentThreshold: Double = 0.45`):

- Birth was `threshold: Double = 0.4`. Real leftover `0.4` in tests/docs/ADR — useful.
- Also matched unrelated `yaw: 0.4` in GazeDetectorTests.

Real kizu (`src/app.rs:64` `SCAR_TEXT_ASK = "explain this change"`):

- Keys collapsed to `scar_text_ask` because the string was unique in the birth commit (`df < 2`), so later copies in tests/benches were invisible.

Real tenaoshi (`timeout: TimeInterval = 300`): found the three adapter defaults (good) *and* `200..<300` HTTP ranges (bad).

Real voidtrace (`SCENARIO_PATH = "data/fixtures/golden/direct-critical-armor.scenario.json"`): identifier regex ran *inside* the string, so keys exploded into `critical`, `golden`, `armor`, `json`, and a 30-line skill file dump.

### After (v0.2)

Same sitbone line (`driftDelay: TimeInterval = 15`). Keys collapsed to `15`. No `init` flood.

```
$ ./also --no-color -C sitbone Sources/SitboneCore/SitboneCore.swift:107
query  Sources/SitboneCore/SitboneCore.swift:107
       driftDelay: TimeInterval = 15,
birth  d3737ea72114  2026-03-31T22:47:01+0900  Implement v0.1: state machine + MenuBarExtra + Notch overlay
       was: public init(t1: TimeInterval = 15, t2: TimeInterval = 90, flowRecovery: TimeInterval = 5) {
keys   15

ok    CLAUDE.md:506: - 境界値テスト: T1(15s), T2(90s) の前後を必ず網羅
ok    README.md:130: | **FocusStateMachine** | ... T1=15s, T2=90s |
ok    SPEC.md:110: - `T1` = 15秒（FLOW→DRIFT閾値）
ok    SPEC.md:349: T1: 15
ok    Sources/SitboneCore/SitboneCore.swift:102: public let driftDelay: TimeInterval  // FLOW→DRIFT (15s)
ok    Tests/SitboneCoreTests/SessionProfileTests.swift:13: XCTAssertEqual(profile.thresholds.driftDelay, 15)
```

Same PresenceArbiter `0.45` (birth `0.4`). After dropping UI `opacity(0.4)` / `yaw: 0.4`, the remaining `drift` rows are leftover single-threshold docs and tests — the actual bug class:

```
drift Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
drift docs/adr/0019-presence-hysteresis.md:9: ...単一閾値(0.4)で判定している:
```

kizu `SCAR_TEXT_ASK`: the unique string is now a key (and the abandoned Japanese body from birth is too). Echo finds docs/tests/benches that were added later:

```
keys   explain this change, この変更について説明して, scar_text_ask
ok    docs/SPEC.md:218: a       ask — `explain this change` を ask scar として挿入
ok    src/hook/tests.rs:114: assert_eq!(hits[0].message, "explain this change");
ok    tests/e2e/jsx-tsx.test.ts:83: expect(result.stderr).toContain("explain this change");
```

tenaoshi `timeout = 300`: the three adapter defaults remain; `200..<300` HTTP ranges and `.milliseconds(300)` are gone.

voidtrace path constant: keys are the full path + `scenario_path`. Hits are the skill scripts and e2e fixture path, not a 30-line word salad.

Fixture: `# Timeout` heading is no longer reported as `ok` kin.

## Dogfood targets
- Synthetic ugly fixture (spaces, parens, nested git, generated files) — `/tmp/also-fixture-v1` and `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`

## Surprises
- `git log -L --reverse -n 1` is the *newest* commit, not the birth; selection happens before reverse.
- Birth of a split Swift default-argument line is a single ancestral statement holding 15, 90, *and* 5. Treating the whole region as the query's tokens poisons classify.
- Later copies of a unique string are not natal siblings. That is consistent with the primitive and easy to mistake for a bug.

## Failures
v0.1 (fixed in v0.2):
- Generic keys (`init`) from the ancestral region.
- Identifier scan inside quoted paths/strings.
- Unique literals dropped by `df >= 2`, hiding the most distinctive token.
- `# Timeout` heading reported as `ok` kin (identifier-only, no literal).
- HTTP `200..<300` sharing the token `300`.
- Unrelated `0.4` values treated as the same literal (UI opacity, gaze yaw).

Still open:
- Short integers remain a bit sticky (`afterSecondCycle < 15` in a sleep test).
- Same-magnitude floats in a different domain (`SPEC.md` audio weight `0.45` vs present-threshold `0.45`).
- `git log -L` on a huge file with a long line history can be slow (not observed as fatal on these targets).

## Suggested mutations
- Inflect identifiers (`t1` → `driftDelay`, `present_threshold` ↔ `presentThreshold`) and treat inflection, not just case, as the same name.
- `--echo` mode: also surface *current* copies of the query's literals, even if they were not in the birth commit.
- Ignore generated files / `vendor/` by default.
- Track a sibling forward with `git log -L` instead of `git grep`, so renamed lines without leftover tokens still resolve.

## Kill / keep
**Keep.** After the key-selection fix the sitbone `0.4` leftovers and the fixture `TIMEOUT=60` still-`30` docs/tests are the "why doesn't this exist" moment, and the tool is quiet enough to run on a real line without drowning in `public init(`. Worth mutating (inflection, generated-file skip, `git log -L` locate) rather than killing.

# mutation-06 — owe

## Primitive
Given a **commit or a diff** (never FILE:LINE), recover every **birth cohort** that change touches — natal siblings introduced together sharing a distinctive literal — and list the kin that are already unpaid at HEAD.

## Why this might not exist
`also` (candidate-10) answers the question once you already know `FILE:LINE`. Reviewers and agents do not. They have a SHA, a PR range, or a `git diff`. Blame still answers who last touched a line; clone detectors answer what looks alike *now*; co-change miners answer what *repeatedly* shipped together. None of them take a change and emit the natal families it still owes. The leftover mention may have been last-touched by a formatter, may no longer look like a clone, and may have co-changed only once — at birth.

## How to run
From this worktree:

```bash
./owe --selftest
./demo.sh
./owe HEAD
./owe -C /path/to/repo e9b0f75 --json --check
git diff | ./owe -
```

## Empirical transcript
v0.1 is the first commit of `owe`. The fixture (TIMEOUT=30 introduced with ugly paths, then one file bumped to 60) is the contract: `owe HEAD` lists the unpaid 30s; `owe HEAD~1` reports the natal family already split 60×1 / 30×5 at HEAD; `config.py:1` is refused.

### Before (v0.1) — fixture

```
$ ./owe --no-color -C "$FIX" HEAD
change commit  …  raise TIMEOUT to 60

owing  5 unpaid  ·  …  introduce timeout=30 retry=3 port=8080
keys   30
delta  30 → 60
paid   config.py:1: TIMEOUT = 60
owing  deploy/timeout.yaml:1: timeout: 30
owing  docs/how to set (timeout).md:3: The service timeout is 30 seconds.
owing  generated/timeout.gen.py:2: TIMEOUT = 30
owing  src/foo bar/timeout.py:1: TIMEOUT = 30  # keep in sync with config.py
owing  tests/test_timeout.py:4: assert TIMEOUT == 30
```

`./owe HEAD~1` → `split  2 factions` `HEAD 30×5  60×1`. `--check` exits 1. `FILE:LINE` exits 2 with "not FILE:LINE".

### Before (v0.1) — dogfood

sitbone `e9b0f75` (0.4 → 0.45 hysteresis), invoked as a commit:

```
owing  2 unpaid  ·  a95da435efe6  Add PresenceArbiter …
keys   0.4
delta  0.4 → 0.45
paid   Sources/SitboneCore/PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:216: // … 0.214 < 0.4
```

The inversion works: no line number, the leftover test comments surface. Missed: CLAUDE.md / SPEC.md / ADR / `@Test(…0.4…)` names (0.4 lives inside a string, or was born in a different commit).

kizu `fb355e0` (Japanese scar bodies → English): `no unpaid kin at HEAD`. True negative — the family moved together.

tenaoshi `7505f56`: false owing on `"TENAOSHI_PROVIDER"` / `"mock"` because a harness rewrite *dropped* those strings without adopting a new literal. Not a value bump.

voidtrace `4c0a717`: flood of short integers (`5`, `7`, `14`) from markdown headings and clause counts. Unusable.

### After (v0.2)

Same sitbone commit. Natal comments remain, and an **echo** pass surfaces leftover 0.4 that was not born in the PresenceArbiter commit (docs, ADR, quoted test names). `0.42` / `0.45` no longer match `0.4`. UI opacity/yaw stay silent.

```
$ ./owe --no-color -C sitbone e9b0f75
change commit  e9b0f75deabd  Implement dual-threshold hysteresis in PresenceArbiter

owing  2 unpaid  ·  a95da435efe6  Add PresenceArbiter …
keys   0.4
delta  0.4 → 0.45
paid   Sources/SitboneCore/PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:216: // … 0.214 < 0.4
echo   CLAUDE.md:329: @Test("… threshold 0.4")
echo   SPEC.md:145: `normalized > 0.4` → `.present`。
echo   docs/adr/0019-presence-hysteresis.md:9: …単一閾値(0.4)で判定している:
```

kizu `fb355e0`: still `no unpaid kin at HEAD` (true negative).

tenaoshi `7505f56`: silent. Replacements must *swap* a literal (abandoned and adopted both nonempty), so dropping `"mock"` without adopting a new string is no longer debt.

voidtrace `4c0a717`: silent. Short integers are debt only as code assignments (`timeout: 30`), never as `## 5.` headings.

v0.2 is: literal-swap required, short-int code-assignment filter, no markdown backticks as strings, echo of abandoned tokens at HEAD, bare-number match (0.4 ⊄ 0.42).

## Dogfood targets
- Synthetic ugly fixture (spaces, parens, nested git, generated files) — `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`

## Surprises
- Defaulting to HEAD (a commit) instead of FILE:LINE is the whole UX; piping `git diff | owe -` is the uncommitted form.
- A later bump (60→90) still owes kin that never left natal 30. Immediate-diff abandoned tokens are not enough; ancestral debt is.
- Path B (the change *as* birth) cannot grep the natal literal — that snaps to unpaid siblings and hides the one member that moved. Same-path follow is required.
- `git grep HEAD:path:line:text` prefixes the tree-ish.

## Failures
v0.1 (fixed in v0.2):
- String drops from refactors (`"mock"`) looked like abandoned literals.
- Short integers in prose/headings drowned voidtrace.
- Strict natal-only missed leftover 0.4 in docs born earlier, and 0.4 inside quoted test names.
- Backtick spans in markdown became "strings".
- `0.4` grepped inside `0.42`.

Still open:
- Same-magnitude floats in a different domain (SPEC.md audio weight 0.45 vs present-threshold 0.45) are not this commit's abandoned 0.4, so they stay quiet — good — but a 0.45 bump would still collide.
- `git log -L` per replacement can be slow on huge files.
- Echo does not know *domain*; a leftover `0.4` in an ADR log snippet is still shown (usually wanted).

## Suggested mutations
- Inflect identifiers across the cohort (`t1` → `driftDelay`).
- `--pr`: `gh pr diff | owe -`.
- Track a sibling forward with `git log -L` instead of same-path follow, so renames without leftover tokens still resolve.
- Domain tags: cluster 0.4-threshold separately from 0.4-opacity without regex style lists.

## Kill / keep
**Keep.** `owe e9b0f75` producing leftover 0.4 tests *and* docs without anyone naming `PresenceArbiter.swift:33` is the "why doesn't this exist" moment. The fixture's `owe HEAD` / `owe HEAD~1` pair is a new verb. Worth mutating (inflection, PR stdin, rename-follow) rather than killing.

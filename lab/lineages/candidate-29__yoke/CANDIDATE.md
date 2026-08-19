# candidate-29 — yoke

## Primitive

A spec clause and its generated witnesses are a *yoke*. The verb is to report the polarity of that join — taut / slack / hand / split / riven — keyed by stable clause id, without running the generator.

## Four primitives considered

1. **yoke** (implemented) — clause-id join of spec vs generated; freshness polarity.
2. **slack-eras** — historical intervals where spec was ahead of generated. *Discarded:* that is `held` with a spec-check predicate; over-flags comment-only spec commits.
3. **echo-graph** — auto-discover undeclared spec→generated edges from banners + co-change. *Discarded:* make-dep discovery / git-relatedness; weaker object than the clause.
4. **punch** (kept as a subcommand, not the ship) — given a spec hunk, emit the generated clause-sites that historically move with it. Blast-radius is named in PRIOR_ART; the join/polarity is the missing object. `yoke --punch` is the cheap approximation.

Not leftover-name hunting, not inverse-printf, not wait-for graphs.

## Why this might not exist

voidtrace / tenaoshi / relico already have `just spec-check`: regenerate everything, hash-compare, exit 1. That answers a boolean about *files* and costs a Pkl eval (tenaoshi's spec-check also runs Swift tests). It will not say:

- which *clause* is stale
- which direction it drifted (spec ahead vs leftover generated)
- whether only one generated family moved (SPEC.md yes, OraclesGenerated.swift no)
- whether the spec at HEAD is the spec the dirty generated tree was baked from

`make` is mtime. `spoor inspect` sniffed banners as a side feature of waitpid. Nobody shipped a Unix tool whose only job is the **clause-shaped join** across the spec/generated boundary.

## How to run

```bash
./yoke --help
./demo.sh
./yoke -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
./yoke -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi --spec HEAD --gen :
./yoke -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi --punch HEAD
./yoke -C /Users/annenpolka/ghq/github.com/annenpolka/voidtrace HEAD
./yoke -C /Users/annenpolka/ghq/github.com/annenpolka/relico HEAD --json | jq .counts
```

## Empirical transcript

### After the improvement (file edges + punch of removed ids)

`--files` no longer binds `specs/cli/surface.pkl` (first spec alphabetically) onto every bannerless schema. voidtrace pairs `specs/main.pkl` to the generated dumps. tenaoshi pairs `specs/tenaoshi.pkl` to SPEC.md / rules.md / testcases/* / OraclesGenerated.swift.

`yoke --punch HEAD` on tenaoshi now names the *old* generated occupancy of a removed id:

```
removed   CTR-001  specs/tenaoshi.pkl:20  →  -
          gen Engine/Tests/.../OraclesGenerated.swift:9, contracts/testcases/CTR-001.json:1, docs/SPEC.md:17
added     EPF-001  -  →  specs/tenaoshi.pkl:27
          gen docs/SPEC.md:19, contracts/testcases/EPF-001.json:1, …
```

relico file-level still reports some oracles as slack (spec commit newer than the oracle file). Clause-level stays 117 taut. That is the point of the primitive: **git date of the file is not freshness of the clause**.

### v1 (previous commit)

Planted fixture (`./demo.sh`):

```
slack  FOO-002   generated body lags spec
hand   BAZ-001   generated id has no spec parent
split  FOO-001   partial regen
taut   BAR-001
```

**tenaoshi** dirty tree (EditPlan rewrite, spec + generated moved together):

```
yoke  spec=:  gen=:  clauses=74  taut=74 slack=0 hand=0 split=0 riven=0
```

Same repo, committed spec vs dirty generated — the rewrite becomes visible without running `just spec-gen`:

```
yoke  spec=HEAD  gen=:  clauses=94  taut=0 slack=50 hand=44
slack  CTR-001  spec clause has no generated witness
hand   EPF-001  generated id has no spec parent
```

`yoke --punch HEAD` lists 94 moved ids (20 CTR removed, EPF/EPC born).

**voidtrace HEAD**: 65 taut, 0 slack. (`SHA-256` in CONTRACTS.md initially registered as a hand clause; rejected by prefix blacklist.)

**relico HEAD**: 117 taut after treating `// ICN-001: …` comments as the desc and allowing generated titles that prefix the spec desc (`(enabled切替)` case qualifiers).

### Before those parser fixes (same dogfood, first run)

- tenaoshi: 36 false SPLIT because `contracts/rules.md` last column is assertion/shape, not desc.
- tenaoshi EPF-008 false SLACK: Pkl `\u{301}` vs JSON `é` on the Unicode fixture.
- voidtrace HEAD: 1 false HAND (`SHA-256`).
- relico: `UnicodeDecodeError` on `git show` of a binary; 24 false SPLIT from `test("ICN-001 icn_001")` titles.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (dirty EditPlan rewrite + HEAD)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (HEAD taut; mid-merge worktree earlier showed riven dumps)
- `/Users/annenpolka/ghq/github.com/annenpolka/relico` (HEAD taut)

## Surprises

- A "complete" dump (SPEC.md) plus per-id shards (testcases/EPF-001.json) plus subset oracles is three different *projections*, not three copies. Comparing full spec payload to a desc-only dump is how v0 invented 36 splits.
- tenaoshi's dirty tree is a live CTR→EPF/EPC rename. Cross-snapshot yoke (`--spec HEAD --gen :`) is the tool spec-check cannot be: spec-check only sees *now*.
- Clause ids are `[A-Z][A-Z0-9]{2}-\d{3}`. `SHA-256` matches.

## Failures

- File-wide conflict markers rive every clause in that dump (seen mid-merge on voidtrace; the tree later cleaned).
- Does not run the generator: a spec edit that does not touch `desc`/`intent`/`input`/`expected_output` is invisible.
- File-level slack still exists when the spec *file* moved and the clause *bodies* did not (relico oracles vs `dc35888`). That is correctly *not* a clause slack.

## Suggested mutations

- Bind file edges only from banners + `specs/main.pkl` / `justfile`, never "first spec alphabetically".
- Clause-window riven, not file-wide riven.
- `yoke --punch` should also name the generated paths a *removed* id used to occupy (scan `--gen` at OLD).
- Optional `--regen` that shells out to `just spec-gen` and re-yokes.

## Kill / keep

**Keep.** The object is not "is generated stale?" (exists: spec-check, make). The object is the clause-shaped join and its polarity. tenaoshi's in-progress rewrite is a demo spec-check will only call "dirty files".

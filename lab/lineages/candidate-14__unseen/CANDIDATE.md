# candidate-14 — unseen

## Primitive

Given a use-site, show the definition as it existed when that line was last touched, then diff it against HEAD — the change the caller has never seen.

## Why this might not exist

`git blame` answers who last touched a line. `git log -L` answers the history of a function. IDEs show the *current* signature. None of them join those questions: "what has this callee become since I last edited this caller?" Sleeping tests, docs, and call sites still compile, so review and CI miss them. The missing verb is a temporal join, not another linter.

Discarded (too conventional): identifier-alias tracing (`aka` / slicing), directory public-surface (`inward` / boundary analysis). The other unconventional candidate was `undo-radius` (semantic revert set of a commit). unseen is the sharper daily question.

## How to run

```bash
./demo.sh
./unseen --repo <git-checkout> [--diff] [--sig] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Synthetic fixture (weird filenames, unicode paths, nested git, Python + Rust) is built by `fixtures/mkrepo.sh` and exercised by `./demo.sh`.

## Empirical transcript

### Fixture (v1, still holds)

```
$ ./unseen --repo ./fixtures/lagrepo --diff greet
greet
  def   src/greet.py:1-7  2024-06-01  …  greet gains prefix; odd_fn gains step
  changed  sig  5 use-sites  lag 882d
    docs/api.md:3         2022-01-01  add greet(name) and callers
    src/app.py:1          2022-01-01  add greet(name) and callers
    src/app.py:5          2022-01-01  add greet(name) and callers
    tests/test_greet.py:1 2022-06-01  test old greet contract
    tests/test_greet.py:5 2022-06-01  test old greet contract
    --- a/greet@60feca344
    +++ b/greet@HEAD
    @@ -1,3 +1,6 @@
    -def greet(name):
    -    return "hi " + name
    +def greet(name, excited=False, prefix="hello"):
    +    base = prefix + " " + name
    +    if excited:
    +        return base + "!!"
    +    return base
```

`--at src/app.py:5` pins just that call. `odd_fn` survives `src/weird name (1).py`. `zenkaku_add` survives `src/日本語.py` + `src/sub dir/`. Nested git does not crash. `./demo.sh` exits 0.

### Before the improvement — real repos

Unscoped kizu (v1) ranked English-word coincidences whose definition *did not exist* at the use-site (`missing-then`). The actual API change was buried:

```
$ ./unseen --repo kizu --limit 8
insert                   missing-then  84 use-sites  lag 19d   def=src/highlight.rs:100
colors                   missing-then  42 use-sites  lag 19d
render_row               missing-then  31 use-sites  lag 19d
render_diff_line_wrapped missing-then  21 use-sites  lag 19d
Highlighter              changed       19 use-sites  lag 18d
insert_scar              changed       14 use-sites  lag 18d    ← the real one, 6th
```

`--min-days 30` on kizu/sitbone printed *nothing* (the histories are young; v1 looked dead). `--limit 1 JSONSessionStore` on sitbone returned a ghost mention in `CLAUDE.md` instead of the 10 test/doc use-sites with a real body diff, because grouping applied `--limit` before it knew status.

Forced-symbol kizu still worked, which is how the primitive proved itself:

```
$ ./unseen --repo kizu --diff --limit 1 insert_scar
insert_scar
  def   src/scar.rs:202-283  2026-05-04  04adde1f1  feat: add complete jsx tsx support
  changed  14 use-sites  lag 18d
    CLAUDE.md:114     2026-04-16
    src/app.rs:3818   2026-04-16
    …
    --- a/insert_scar@f5b5df280
    +++ b/insert_scar@HEAD
    -pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<()> {
    +pub fn insert_scar(...) -> Result<Option<ScarInsert>> {
    +    let (syntax, line_number) = if let Some(dialect) = dialect_for_path(path) {
    +        let placement = scar_placement_for_line(...)?;
```

Callers and docs last touched the pre-JSX `Result<()>` contract; HEAD returns `Option<ScarInsert>` and relocates the scar for TSX. That is the question the tool exists to ask.

voidtrace v1 mixed a real `loadRuleset` expansion with `timeMs missing-then` hits in `VoidTrace計画.md`. tenaoshi v1 mixed `cancelTransform` (`transformTask` → `generationTask`) with generic names (`Scope`, `present`, `Field`).

### After the improvement (v0.2)

Changes driven by the transcript above:

- hide `missing-then` unless `--ghosts` or a symbol was named
- rank signature/header diffs above body-only diffs
- apply `--limit` only to cohorts that already passed those filters
- drop `mod` as a "definition" (it turned `language` / `paths` into fake callees)
- IDF: skip names referenced in too many files
- label uncommitted blame `WIP` / `uncommitted` instead of git's porcelain noise

Unscoped kizu now leads with the real API change:

```
$ ./unseen --repo kizu --limit 12
insert_scar              changed  sig  14 use-sites  lag 18d
insert_scar              changed  sig   5 use-sites  lag 18d
insert_scar              changed  sig   2 use-sites  lag 18d
bootstrap_with_diff      changed  sig   2 use-sites  lag  8d
…
```

sitbone `--limit 1 JSONSessionStore` now returns the body diff against tests, not the CLAUDE.md ghost.

```
$ ./unseen --repo sitbone --limit 1 JSONSessionStore
JSONSessionStore
  changed  body  10 use-sites  lag 9d
    Tests/SitboneDataTests/JSONSessionStoreTests.swift:46
    docs/adr/0012-per-profile-statistics.md:21
```

sitbone unscoped: `activeProfile`, `profileStores`, `tickAway` (real Swift). voidtrace unscoped: `CLAUSE_IDS`, `replayTrace`, `executeResolvedTickScheduleRule` (no more `timeMs` ghosts). tenaoshi `writeBack` reconstructed an API the callers have not been edited through:

```
$ ./unseen --repo tenaoshi --diff --limit 1 writeBack
    --- a/writeBack@1703bc161
    +++ b/writeBack@HEAD
    -    static func writeBack(_ text: String, to element: AXUIElement?) async -> Bool {
    +    static func writeBack(_ text: String, scope: Scope) async -> Bool {
```

`App.swift` / `PanelSession.swift` last touched the AX-element signature on 2026-07-28; HEAD takes `Scope`.

## Dogfood targets

| Target | Result |
| --- | --- |
| `fixtures/lagrepo` (generated; spaces, unicode, nested git) | deterministic hits, `./demo.sh` exits 0 |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | `insert_scar` signature change; ~14s full scan |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | `classifySite`, `JSONSessionStore`, `activeProfile` |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | `loadRuleset` / `CLAUSE_IDS` growth; ghosts in the Japanese plan file |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | `writeBack` AX→Scope; `cancelTransform` body rename |
| `/Users/annenpolka/ghq/github.com/annenpolka/skills` | no code definitions; empty result (not a crash) |

## Surprises

- The interesting unit is not "this file is old" but *cohorts of use-sites that last saw the same historical body*. Two `greet` diffs (pre-excited vs pre-prefix) fell out for free.
- Docs and tests sleep harder than compiled callers. `docs/api.md` and `CLAUDE.md` showed up beside `src/app.py`.
- Uncommitted definitions (`WIP`) turn every committed caller into a sleeper. That is a useful pre-commit view, not a bug.
- kizu's entire interesting history is ~18 days. `--min-days 30` made a live repo look empty.

## Failures

- Language-agnostic spans: Swift stored properties (`activeProfile`) swallow neighboring members, so a "sig" diff can include unrelated fields.
- Naive brace counting does not understand strings or `mod` trees (mitigated by dropping `mod` as a def).
- `git show commit:path` does not follow renames, so a moved file becomes `missing-then` (now hidden by default).
- Markdown-only repos (`skills`) have nothing to define. Headings are not treated as symbols.
- Common short names (`beta`, `append`, `lines`) can still appear after IDF.
- Full-repo historical reconstruction on kizu is ~14s (blame + many `git show`s). Fine for a query, not for a keystroke.

## Suggested mutations

- Follow renames when historical `git show` misses.
- Language-aware spans (tree-sitter) for Swift properties / Rust impl blocks.
- `--sig` as the unscoped default; body diffs behind `--body`.
- `unseen %:%l` editor binding; `unseen --check --sig` as a CI gate on PRs.
- Treat fenced / backticked mentions as stronger doc refs than bare words.
- Inverse query: given a commit that changed a def, list use-sites that were *not* edited in that commit (the same-commit miss).

## Kill / keep

**Keep.** On kizu, `insert_scar`'s JSX/`ScarInsert` contract change is exactly the unseen diff sleeping callers and docs have not been edited through. On tenaoshi, `writeBack` changing from `AXUIElement?` to `Scope` is the same verb. v1's ranking almost killed it by looking like a word-frequency toy; v2's "only real diffs, signature first" makes the primitive visible without a symbol name. Kill only if a later mutation cannot tighten Swift/rename spans.

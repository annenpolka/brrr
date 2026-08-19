# mutation-20 — doze

## Primitive

`--check` exits 1 if any use-site last saw a different **signature** than HEAD. Default listing is that same set. Body diffs and ghost-name ranking are not the product.

## Why this might not exist

`unseen` (candidate-14) joined blame-of-caller-line with evolution-of-callee, then *ranked* whatever came back — body-only churn, English-word coincidences (`insert`, `colors`) whose definition did not exist at the use-site. Review still compiles. The daily CI question is narrower: "did this caller last see a different contract than HEAD?" IDEs show the current signature. `git blame` shows who touched a line. Neither fails the build. The missing verb is a **signature-lag gate**, not another ranked report.

Flipped assumptions: kill body-first discovery; kill ghost English-word ranking. Default output is signature changes only. `--check` is the CI verb (unlimited, stable `path:line`, exit 1). `--body` is the opt-in for people who still want unseen's body diffs.

## How to run

```bash
./demo.sh
./doze --repo <git-checkout> [--check] [--body] [--diff] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Synthetic fixture (weird filenames, unicode paths, nested git, Python + Rust, plus a body-only `trim` change) is built by `fixtures/mkrepo.sh` and exercised by `./demo.sh`.

## Empirical transcript

### Fixture (v0.1, still holds)

```
$ ./doze --repo ./fixtures/lagrepo greet
greet
  def   src/greet.py:1-7  2024-06-01  …  greet gains prefix; odd_fn gains step
  5 use-sites  lag 882d
    last-saw  def greet(name):
    HEAD      def greet(name, excited=False, prefix="hello"):
    docs/api.md:3
    src/app.py:1
    src/app.py:5
    tests/test_greet.py:1
    tests/test_greet.py:5

greet
  3 use-sites  lag 517d
    last-saw  def greet(name, excited=False):
    HEAD      def greet(name, excited=False, prefix="hello"):
    src/cli.py:1
    src/cli.py:5
    src/greet.py:9
```

Unscoped default lists `greet` / `odd_fn` / `zenkaku_add` / `rust_greet` (all signature). Body-only `trim` is hidden until `--body`. `--check greet` exits 1 with `path:line: greet: signature changed`. `--check trim` exits 0 (signature unchanged, even with `--body`). Nested git does not crash. `./demo.sh` exits 0.

### Before the improvement — kizu `insert_scar`

Forced `--check insert_scar` already did the job the mutation exists for (0.43s, exit 1):

```
$ ./doze --check --repo kizu insert_scar
src/app.rs:3818: insert_scar: signature changed
  last-saw  pub fn insert_scar(path: &Path, line_number: usize, text: &str) -> Result<()>
  HEAD      pub fn insert_scar( path: &Path, line_number: usize, kind: ScarKind, body: &str, ) -> Result<Option<ScarInsert>>
…
doze: 21 use-sites last saw a different signature than HEAD
```

Three human cohorts for one name: two of them printed the *same* last-saw header (`kind: ScarKind, body: &str) -> Result<()>`), split only because the historical *bodies* differed (JSX placement). `--check` then pretty-printed HEAD with leftover spaces from multiline reflow (`insert_scar( path:`). Unscoped still led with `insert_scar` (lag 18d) — signature-only default, no IDF, did not bury the real API — but also emitted string-fixture `fn missing()` / `fn beta()` and `verify_token` whose brace span swallowed `git.rs`.

Ancestor unseen hid `insert` as an English stop-word. That was the ranking this mutation dropped.

### After the improvement (v0.2)

Changes driven by the transcript above:

- compare and **group by collapsed signature**, not body (reflow / trailing commas are not a contract change)
- pretty-print last-saw / HEAD as one-line signatures
- skip defs buried in strings or line comments; cap span at 160 lines; require a callable/type-shaped header

```
$ ./doze --repo kizu insert_scar
insert_scar
  16 use-sites  lag 18d
    last-saw  pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<()>
    HEAD      pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<Option<ScarInsert>>
insert_scar
  5 use-sites  lag 18d
    last-saw  pub fn insert_scar(path: &Path, line_number: usize, text: &str) -> Result<()>
    HEAD      pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<Option<ScarInsert>>
```

Two eras, not three. `--check` still exits 1 on 21 use-sites (0.5s). Unscoped top names: `insert_scar`, `bootstrap_with_diff`, `from_str` (`Option<Self>` → `Result<Self, Self::Err>`), `bindings` (14 → 16 keys). `missing` / `beta` / `verify_token` gone.

Dropping English-word ranking recovered a *real* signature lag ancestor had suppressed:

```
$ ./doze --repo kizu --limit 1 insert
insert
  def   src/highlight.rs:100-113
    last-saw  fn insert(&mut self, key: HighlightCacheKey, tokens: Vec<HlToken>)
    HEAD      fn insert(&mut self, key: HighlightDocumentCacheKey, document: HighlightedDocument)
```

## Dogfood targets

| Target | Result |
| --- | --- |
| `fixtures/lagrepo` | signature vs body-only `trim`; `--check` 1 / 0; `./demo.sh` exits 0 |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | `--check insert_scar` exit 1, 21 use-sites, `Result<()>` → `Result<Option<ScarInsert>>`; two last-saw eras; `insert` cache-key change; ~0.5s forced, ~20s unscoped |

## Surprises

- Two `insert_scar` body-cohorts were one signature. Grouping by collapsed last-saw header is the unit a CI gate actually wants; the JSX body diff is `--body` / `--diff`.
- `src/app.rs` last saw `text: &str -> Result<()>`, not the later `ScarKind` contract. Two-era signature history fell out without ranking.
- Killing IDF did not bury `insert_scar`. It *unhid* `insert`'s `HighlightCacheKey` → `HighlightDocumentCacheKey` change.
- Docs and `///` mentions still fire `--check`. That is the same-commit-miss of documentation, not a ghost name.

## Failures

- Naive brace/indent spans: a type that is not `fn`/`def` still needs the callable-header filter; Swift stored properties are not exercised here.
- `git show commit:path` does not follow renames (`missing-then`, hidden unless `--ghosts`).
- `--check insert_scar` includes module docs (`src/scar.rs:8`) and `plans/*.md` alongside tests and `app.rs`. The CI verb as specified is any use-site, not "compiled callers only".
- Unscoped kizu is still a blame walk (~20s). Fine for a query or a CI job, not a keystroke.
- Markdown-only repos have nothing to define.

## Suggested mutations

- `--code`: `--check` only on `DEF_EXTS` use-sites (tests/src), docs behind `--docs`.
- Follow renames when historical `git show` misses.
- Language-aware spans (tree-sitter) for Swift properties / Rust impl blocks.
- Inverse query: given a commit that changed a signature, list use-sites *not* edited in that commit.
- Editor binding: `doze %:%l` on the current line.

## Kill / keep

**Keep.** `--check insert_scar` on kizu fails the build with the sleeping `Result<()>` / `text: &str` contracts vs HEAD `Result<Option<ScarInsert>>`, without a ranked ghost list, in half a second. Body-only `trim` does not fail CI. Dropping English-word ranking paid rent (`insert`'s cache-key signature). Kill only if a later mutation cannot tell compiled callers from plan-file mentions without bringing ranking back.

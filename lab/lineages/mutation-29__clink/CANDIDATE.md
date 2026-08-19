# mutation-29 — clink

## Primitive

`--check` exits 1 if any **compiled caller** last saw a different signature than HEAD. Plan/markdown mentions stay behind `--docs`. Comments and strings in source files are not callers.

## Why this might not exist

`doze` (mutation-20) made the CI verb "did this use-site last see a different contract than HEAD?" and then failed the build on `plans/*.md` the same way it failed on `src/scar.rs`. Review still compiles. A plan file cannot call `insert_scar`. The daily CI question is narrower: "did a **source-extension caller the compiler sees** last see a different contract than HEAD?" IDEs show the current signature. `git grep` in `plans/` shows stale prose. Neither fails only the code that will not type-check. The missing verb is a **compiled-caller signature-lag gate**.

Flipped assumptions: default listing and `--check` walk `DEF_EXTS` only. `--docs` is the opt-in for doze's plan/markdown hits. Tokens buried in comments or strings inside `.rs`/`.py` are not compiled callers. Body-only diffs stay behind `--body`. Ghost English-word ranking stays gone.

## How to run

```bash
./demo.sh
./clink --repo <git-checkout> [--check] [--docs] [--body] [--diff] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Synthetic fixture (weird filenames, unicode paths, nested git, Python + Rust, body-only `trim`, `docs/` + `plans/` mentions, plus a comment leftover) is built by `fixtures/mkrepo.sh` and exercised by `./demo.sh`.

## Empirical transcript

### Fixture (v0.1, still holds after v0.2)

```
$ ./clink --repo ./fixtures/lagrepo greet
greet
  4 compiled callers  lag 882d
    last-saw  def greet(name):
    HEAD      def greet(name, excited=False, prefix="hello"):
    src/app.py:1
    src/app.py:6
    tests/test_greet.py:1
    tests/test_greet.py:5
```

`docs/api.md` and `plans/v0.md` are absent. `--docs greet` brings them back. `--check greet` exits 1 with compiled callers only. `--check --docs greet` names both markdown files. Body-only `trim` still exits 0. Nested git does not crash. `./demo.sh` exits 0.

### Before the improvement — kizu `insert_scar`

Forced `--check insert_scar` already did the file-type cut (0.48s, exit 1, **no** `plans/`):

```
$ ./clink --check --repo kizu insert_scar
src/app.rs:3818: insert_scar: signature changed
  last-saw  pub fn insert_scar(path: &Path, line_number: usize, text: &str) -> Result<()>
  HEAD      pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<Option<ScarInsert>>
…
src/scar.rs:8: insert_scar: signature changed
  last-saw  pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<()>
…
clink: 17 compiled callers last saw a different signature than HEAD
```

17 hits, all `.rs`. `--docs` restored the four doze extras (`plans/v0.2.md` ×2, `plans/v0.3.md`, `CLAUDE.md`) → 21 use-sites, matching ancestor's count.

But 6 of the 17 were not compiled:

```
COMMENT  src/app.rs:3818   /// … so `insert_scar`
COMMENT  src/app.rs:3992   // `insert_scar` will fail inside the read phase
COMMENT  src/scar.rs:571   // --- M3: insert_scar ---
COMMENT  src/scar.rs:8     //! … calls [`insert_scar`]
COMMENT  src/scar.rs:151   /// … `insert_scar` wraps
COMMENT  src/scar.rs:160   /// This makes `insert_scar` safe to call
CALL     src/scar.rs:591   insert_scar(&path, 3, ScarKind::Ask, …)
… 10 more insert_scar(...) test calls
```

The entire `text: &str -> Result<()>` cohort was comments. The fixture planted the same bug: `src/app.py:2` is `# leftover greet mention in a comment`.

### After the improvement (v0.2)

Skip tokens buried in comments or strings when the file is a source extension. `--docs` still adds plan/markdown files; it does not resurrect source comments.

```
$ ./clink --repo kizu insert_scar
insert_scar
  11 compiled callers  lag 18d
    last-saw  pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<()>
    HEAD      pub fn insert_scar(path: &Path, line_number: usize, kind: ScarKind, body: &str) -> Result<Option<ScarInsert>>
    src/scar.rs:591
    src/scar.rs:604
    …
    src/scar.rs:774
```

One era. Eleven real `insert_scar(...)` test calls. `--check` still exits 1 (0.32s). The `text: &str` last-saw survives only under `--docs`, on `plans/v0.2.md`. Fixture `src/app.py:2` gone.

`--docs --check insert_scar` → 15 use-sites = 11 compiled + `CLAUDE.md:114` + `plans/v0.2.md:63,66` + `plans/v0.3.md:186`.

Unscoped kizu (~6s, markdown not blamed) still leads with `insert_scar`, then `bootstrap_with_diff` (`current_branch_ref` added), `from_str` (`Option<Self>` → `Result<Self, Self::Err>`). Ancestor's English-word `insert` is still a real compiled lag:

```
$ ./clink --check --repo kizu insert
src/perf.rs:205: insert: signature changed
  last-saw  fn insert(&mut self, key: HighlightCacheKey, tokens: Vec<HlToken>)
  HEAD      fn insert(&mut self, key: HighlightDocumentCacheKey, document: HighlightedDocument)
clink: 1 compiled caller last saw a different signature than HEAD
```

## Dogfood targets

| Target | Result |
| --- | --- |
| `fixtures/lagrepo` | compiled vs `--docs`; comment leftover hidden in v0.2; `--check` 1 / 0; `./demo.sh` exits 0 |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | `--check insert_scar` exit 1, 11 compiled test calls, `Result<()>` → `Result<Option<ScarInsert>>`; `text: &str` era is plans-only; `insert` cache-key change; ~0.3s forced, ~6s unscoped `--limit 4` |

## Surprises

- Ancestor's two-era `insert_scar` story split compiled tests (`Result<()>`) from comments (`text: &str`). After the comment cut, default has one era. `--docs` reopens the second era on `plans/v0.2.md`. The CI unit and the prose unit disagree; that is the flip.
- Dropping markdown blame cut unscoped kizu from ~20s (doze) to ~6s without ranking.
- Killing IDF still unhides `insert`'s `HighlightCacheKey` → `HighlightDocumentCacheKey` change, now as one compiled caller in `src/perf.rs`.

## Failures

- Naive brace/indent spans: a type that is not `fn`/`def` still needs the callable-header filter; Swift stored properties are not exercised here.
- `git show commit:path` does not follow renames (`missing-then`, hidden unless `--ghosts`).
- Block comments that do not start the line (`code; /* insert_scar */`) and rust raw strings are not buried.
- Markdown-only repos have nothing to define.

## Suggested mutations

- Follow renames when historical `git show` misses.
- Language-aware spans (tree-sitter) for Swift properties / Rust impl blocks.
- Inverse query: given a commit that changed a signature, list compiled callers *not* edited in that commit.
- Editor binding: `clink %:%l` on the current line.

## Kill / keep

**Keep.** `--check insert_scar` on kizu fails the build on eleven `insert_scar(...)` test calls that last saw `Result<()>` vs HEAD `Result<Option<ScarInsert>>`, silent on `plans/*.md` and on `///` mentions, in a third of a second. Body-only `trim` does not fail CI. `--docs` is the explicit prose gate. Kill only if a later mutation can tell a type-checked call from a test helper with the same name without bringing ranking back.

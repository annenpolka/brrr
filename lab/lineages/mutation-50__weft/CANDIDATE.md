# mutation-50 — weft

## Primitive

A unified diff is a superposition of syntactic classes. **weft** projects it onto one allowed class and **fails the build** if any other class leaked.

ply dumped every ply-edit. weft’s default is the CI gate ply hid behind `--check --only`. stdin is a unified diff. `--only docs` (or `--only comments`) exits 1 on a leaked number, ident, or string. TSV exists only on `--emit`.

## Four primitives considered

1. **weft** — Purity gate on ply-edits. **Implemented.**
2. ply as a dump — ancestor. Occupied.
3. Path-only “docs PR” linter (`*.md` vs not) — conventional `paths-filter`. The object here is *syntactic class*, not path glob; path is only the `--only docs` exception for prose files.
4. Formatter-only detector — punct/space bag. Too small; weft ignores those as noise.

## Why this might not exist

Reviewers already say “this was supposed to be comment-only” after the timeout moved. `git diff` is untyped. `delta` colors it. `difftastic` shows a tree. pre-commit glob-filters paths. Nobody asks the CI: *did any other syntactic class leak into this ply?*

The cheat is silent: a “docs PR” that bumped `30` to `60` on the same line as the comment edit.

## How to run

```bash
./demo.sh
./demo.sh 0
./weft --selftest
./weft --help
git diff | ./weft --only docs
git diff | ./weft --only comments
git diff | ./weft --only docs --emit
git diff origin/main...HEAD | ./weft --only docs
```

Python 3.9+, stdlib, no `git` required (stdin filter). Exit 0 = clean, 1 = leak, 2 = usage.

`--only docs` allows comment+text on code paths, and any class on documentation paths (`*.md`, `docs/`, README, LICENSE, …). `--only comments` is comment tokens only, any path. `--only comment,text` is the strict syntactic form (no path exception).

## Empirical transcript

### v0.1 — gate, not dump

`--selftest` 18/18. Fixture mixed line:

```
$ git diff | weft --only docs
weft FAIL  only=docs  stdin  files=1  leaked=1  number=1
  src.rs:2  number  chg  30 → 60
# rc=1
$ git diff | weft --only comments --emit
path	line	class	op	old	new
src.rs	2	number	chg	30	60
# rc=1; default (no --emit) is not TSV
```

Comment-only rewrite of `// secs` → `// timeout` is `weft OK`. CJK README prose fails `--only comments` (class `text`) and passes `--only docs`.

A two-file “docs PR” that also moved a timeout leaked *two* classes: README ident `documented` and `src.rs` number `30→60`. The number is the cheat. The README ident is the tokenizer lying about English prose.

Real repos (2026-08-20):

| commit | claim | v0.1 `--only docs` |
| --- | --- | --- |
| sitbone `77df1da` README+Makefile | “Update README” | FAIL leaked=29 (Makefile *and* README `2048`) |
| sitbone `98a8009` ADR-0019 | new markdown | FAIL leaked=243 (`0.4`, `PresenceStatus`) |
| voidtrace `ce44c93` | `docs: record … ci` | FAIL leaked=35 (`2026`, run id `30705844166`) |
| tenaoshi `838c078` | restoration | FAIL leaked=270 (AGENTS.md + Swift + pkl) |
| sitbone `e9b0f75` | hysteresis | FAIL `0.4→0.45`, `threshold→presentThreshold` |
| kizu `9349dc5` | release | FAIL `Cargo.toml` `0.6.0→0.7.0`, `skipped_lock=1` |

`--only docs` as “class ∈ {comment, text} on every path” cannot pass a genuine English docs commit. Markdown is ident+number+string under the C lexer. Hash `557c76f` split into `557` + `c76f`.

### v0.2 — `--only docs` is a path-aware class gate

The CI verb is *no code ply leaked*, not *no numeric tokens in markdown*. Documentation paths (`*.md`, `docs/`, `adr/`, README, LICENSE, CLAUDE, AGENTS, …) are free under the `docs` alias. Code paths still only allow comment+text. `--only comments` is unchanged (no path exception). `--only comment,text` stays the strict syntactic gate.

`--selftest` 22/22. `./demo.sh 0` PASS=28 FAIL=0.

Same two-file docs PR after:

```
weft FAIL  only=docs  files=2  leaked=1  number=1
  src.rs:2  number  chg  30 → 60
```

README prose is gone from the leak list. The timeout remains.

| commit | v0.1 | v0.2 |
| --- | --- | --- |
| sitbone `77df1da` README+Makefile | FAIL 29 | FAIL 21, **Makefile only** (`tccutil` deleted, `"Sitbone Dev"` codesign). README cert `2048` is not a leak. |
| sitbone `98a8009` ADR | FAIL 243 | **OK leaked=0** |
| voidtrace `ce44c93` docs CI | FAIL 35 | **OK leaked=0** |
| tenaoshi `838c078` | FAIL 270 / 9 files | FAIL 151; AGENTS.md free; Swift tests + `.pkl` + `.json` still leak |
| sitbone `e9b0f75` hysteresis | FAIL | FAIL, `0.4→0.45` still first-class |
| kizu `9349dc5` | FAIL | FAIL, `Cargo.toml` string version |

The money shot is sitbone `77df1da`: a README PR that also rewrote the Makefile. Path-aware docs dropped the README noise and left the Makefile ply. The fixture money shot is still `30→60` in `src.rs`.

## Dogfood targets

- Fixture stdin diffs in `./demo.sh` (mixed line, comment-only, README+timeout).
- sitbone `77df1da`, `98a8009`, `e9b0f75`.
- voidtrace `ce44c93`.
- tenaoshi `838c078`.
- kizu `9349dc5`.

## Surprises

- Same-line superposition works as a gate: comment ply is allowed, number ply fails, `--emit` prints only the leak.
- Added files are in the gate (ply skipped them because the dump exploded). A docs PR that adds `n.rs` fails.
- `null`/`true` in a Makefile `2>/dev/null || true` are class `kw`. Harmless once Makefile is a code path; they stay as leaks, which is honest.
- Lockfiles skipped: kizu’s version ply is the `Cargo.toml` string, not `Cargo.lock`.
- `--only comments` vs `--only docs` is the useful pair: comments is “this hunk is a comment token”; docs is “this PR did not touch code ply.” English README cannot satisfy the first and should satisfy the second.

## Failures

- Hyphenated hashes (`557c76f`) still split; harmless under path-aware docs, still ugly under `--emit` on a `.rs` comment that cites a SHA.
- `contracts/prompt.md` is a docs path. A prompt that embeds executable snippets will not fail `--only docs`. Use `--only comments` or `--only comment,text` if that matters.
- `--only docs` will not catch a number inside a code *comment* (`// timeout 30` → `// timeout 60`) — that is a comment ply. `--only number` inverted is a different gate (`--check` in ply).
- Punct/space ignored; a rustfmt-only PR passes `--only docs`. `--punct` exists and is still too noisy for markdown.
- Makefile identifiers are split on `$()` / `@`. Enough to fail the gate, not enough to read as a review.

## Suggested mutations

- weft-aware `git add -p` (stage only the allowed ply).
- GitHub Actions annotation from `--emit`.
- Hex/hash tokens so `557c76f` is one ident.
- `--only docs --punct` that still frees documentation paths.
- Invert: `--forbid number` as a one-class tripwire (timeout bumps in any PR).

## Kill / keep

**Keep.** The default is a verdict a CI job can fail on. The mixed-line number leak is the review cheat ply named and never made the product. Path-aware `--only docs` is the one improvement that made the gate pass a real docs commit and still catch the Makefile that snuck in beside it.

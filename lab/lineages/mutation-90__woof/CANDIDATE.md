# mutation-90 — woof

## Primitive

A unified diff is a superposition of syntactic classes. **woof** projects it onto comment+prose tokens and **fails the build** if any other class leaked — **regardless of path**.

weft `--only docs` is a directory glob: `docs/generated/api.rs` is free. woof `--only prose` is a class gate: README.md at the repo root counts; a file under `docs/` does not get a free number ply. A markdown fence that is a timeout sample is number ply, not one swallowed string.

## Why this might not exist

Reviewers already say “this was supposed to be a docs PR” after `docs/generated/lib.rs` moved a timeout. weft answered with `--only docs`, then defined docs as `*.md` **or** anything whose parent path contains `docs/`. pre-commit `paths-filter` is the same glob. DESTROYER_WEFT made the glob the product: fence numbers vanish into a backtick-string, then the path exception frees the string.

snag `--forbid number` is the invert (any number, even inside `//`). woof is still weft’s allow-list. Compose them; do not clone the tripwire.

## How to run

```bash
./demo.sh
./demo.sh 0
./woof --selftest
./woof --help
git diff | ./woof --only prose
git diff | ./woof --only comments
git diff | ./woof --only prose --emit
```

Python 3.9+, stdlib. Exit 0 = clean, 1 = leak, 2 = usage.

`--only prose` (alias `--only docs`) = comment+text tokens, no path exception. `--only comments` is comment only. Markdown words are `text`. CJK on a code path is `ident`. Fence interiors are the tagged dialect.

## Empirical transcript

### v0.1 — path glob vs prose tokens

`--selftest` 28/28. `./demo.sh 0` PASS=37 FAIL=0. `woof 0.1`.

Destroyer fixtures, weft `--only docs` vs woof `--only prose`:

| fixture | weft `--only docs` | woof `--only prose` |
| --- | --- | --- |
| mixed line `30→60` + comment | FAIL number | FAIL number |
| comment-only | OK | OK |
| comment-interior `// timeout 30→60` | OK | **OK (not snag)** |
| CJK README | OK | OK |
| `fn 契約 → fn 資産` on `src.rs` | **OK** (CJK is `text`, free) | **FAIL ident** |
| `docs/generated/api.rs` `30→60` + rename | **OK (docs/** glob)** | **FAIL ident+number** |
| `docs/Makefile` `TIMEOUT 30→60` | **OK** | **FAIL number** |
| README `0.6.0→0.7.0` | **OK** | **FAIL `0.6 → 0.7`** |
| README fence `timeout 30→60` | **OK** | FAIL **string** (swallowed) |

```
$ ./woof --only prose < fixtures/docs-generated-api.rs.diff
woof FAIL  only=prose  stdin  files=1  leaked=2  ident=1  number=1
  docs/generated/api.rs:1  ident  chg  fetch_user → fetch_account
  docs/generated/api.rs:1  number  chg  30 → 60
# rc=1

$ ./weft --only docs < fixtures/docs-generated-api.rs.diff
weft OK  only=docs  stdin  files=1  leaked=0
# rc=0
```

That is the visible flip. `--only docs` on woof is the same token alias, not the glob: it also fails `api.rs`.

sitbone `77df1da` (README + Makefile):

```
$ git diff 77df1da^..77df1da | weft --only docs --emit
# FAIL leaked=21, paths Makefile=21. README cert 2048 is not a leak.

$ git diff 77df1da^..77df1da | woof --only prose --emit
# FAIL leaked=23, Makefile=21, README.md=2 strings
# README fence is one swallowed bash string containing 2048.
```

snag cited, not cloned, on the comment-interior fixture: weft OK, woof OK, snag TRIP `30 → 60`.

### v0.2 — fence interiors are the tagged dialect

Forced by the v0.1 transcript, not by taste. DESTROYER_WEFT named the hide: a README fence that is the only copy of a timeout is one backtick-string, then `--only docs` frees the path. v0.1 still named it `string`. snag peels numbers out of that string. woof should stop swallowing the fence so `30→60` is a number. Do not peel `// timeout 30` — that remains snag.

`--selftest` 29/29. `./demo.sh 0` PASS=39 FAIL=0. `woof 0.2`.

```
$ ./woof --only prose < fixtures/fence-number.md.diff
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  README.md:5  number  chg  30 → 60
# rc=1  (v0.1 was string=1 of the whole rust block)

$ ./weft --only docs < fixtures/fence-number.md.diff
weft OK  only=docs  stdin  files=1  leaked=0
```

sitbone `77df1da` after fence projection:

```
$ git diff 77df1da^..77df1da | woof --only prose
woof FAIL  only=prose  stdin  files=2  leaked=144  ident=126  kw=8  number=5  string=5
# Makefile still 21. README fence now code ply: number ins 2048, 2048, 3650.
```

weft still: FAIL leaked=21, Makefile only, README 2048 not a leak.

Same-line `30→60` is still FAIL number. Comment-interior is still OK.

| object | v0.1 | v0.2 |
| --- | --- | --- |
| README fence `30→60` | FAIL string (swallowed) | **FAIL number `30 → 60`** |
| sitbone README `2048` | string blob | **number ins 2048** |
| `docs/generated/api.rs` | FAIL ident+number | same |
| comment-interior | OK | OK |

## Dogfood targets

- Destroyer weft fixtures rebuilt under `fixtures/` (`fence-number.md.diff`, `docs-generated-api.rs.diff`, `docs-makefile.diff`, `readme-ver.diff`, CJK, mixed line, comment-interior).
- sitbone `77df1da` (Makefile vs README) — DESTROYER_WEFT gold.
- sitbone `98a8009` ADR, voidtrace `ce44c93`, kizu `9349dc5` as contrast only.
- weft 0.2 from mutation-50 worktree; snag 0.2 from mutation-61 worktree.

## Surprises

- Path-glob vs prose is one fixture: `docs/generated/api.rs`. weft OK, woof FAIL number+ident. `docs/Makefile` is the same object.
- Markdown words as `text` is load-bearing. Without it, English README is ident flood (weft v0.1). CJK README stays OK. README `0.6.0→0.7.0` is still a number, which is the DESTROYER hole weft was forbidden to see.
- CJK `fn 契約 → fn 資産` is ident on a code path. weft `--only docs` still frees it as `text`. That came for free once prose stopped meaning “any Unicode letter is comment-adjacent.”
- Fence projection on sitbone `77df1da` turns the new bash sample into 100+ ident leaks. The money shot is `2048` as number; the rest is “fence = code even on a docs path,” DESTROYER’s second decision, taken.
- kizu `9349dc5` is still a *string* version on Cargo.toml. woof does not peel `"0.6.0"` into numbers. snag does. Compose.

## Failures

- Genuine markdown commits with dates / run ids fail `--only prose` (voidtrace `ce44c93` leaked=16 number+string; sitbone ADR leaked=180, mostly fence+`0.4`). weft `--only docs` passes both. That is the glob. A “record the CI run” PR is not comment+prose-only once numbers are numbers.
- Adding a fenced sample to README is a code ply. sitbone `77df1da` leaked 144. The Makefile cheat is still in the list; it is no longer the only row.
- Semver `0.6.0` in README prose splits as `0.6` + `0`. Enough to fail. Ugly under `--emit`.
- Inline `` `code` `` is still string. `` `make app` `` on the sitbone README is a string leak beside the fence numbers.
- Binary / rename / lockfile skip are weft’s. Untouched. DESTROYER left them as occupancy of nothing.
- Number inside `//` stays comment ply. Use snag `--forbid number`.

## Suggested mutations

- `--chg` on fence numbers only (`30→60`), so a new bash sample is not 114 ident inserts.
- Hex/hash tokens so ADR `98a8009` / voidtrace `557c76f` are one ident.
- Binary as a leak class (DESTROYER_WEFT, not this primitive).
- Compose in CI: `woof --only prose` then `snag --forbid number` on the same stdin.

## Kill / keep

**Keep.** The object is still weft’s: “this was supposed to be comment/docs-only; a number or ident leaked.” Mixed-line `30 → 60` still fails. The mutation is that `--only prose` is not `docs/**`. `docs/generated/api.rs` and `docs/Makefile` leak. README.md at the repo root counts. v0.2 is the one improvement the destroyer fence fixture forced: a timeout sample inside a fence is a number ply. It is not snag. Comment-interior still passes.

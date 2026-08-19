# destroyer-26 — DESTROYER_WOOF

## Primitive

woof `--only prose` is class-not-path. This pass keeps the gold and **breaks prose-as-class** where a new fence sample is 114 ident inserts, a SHA is `77 → 98`, and CJK identifiers are still `text` on indented / `.txt` / CHANGELOG / RST.

## Why this might not exist

DESTROYER_WEFT killed the `docs/**` glob as the product. woof answered with tokens. v0.2 projected fences so `30→60` is a number. The hide moved: paste a bash sample and the gate names 114 idents; cite `77df1da` and it names `77`; indent `fn 契約` instead of fencing it and CJK is text again.

## How to run

```bash
./demo.sh
python3 attack.py
```

Python 3.9+, stdlib. Victim is mutation-90 woof. tally `--chg` and snag `--forbid number` are contrast only.

## Empirical transcript

`./woof --selftest` 29/29 after the battery. `./demo.sh 0` on the victim PASS=39 FAIL=0. Victim untouched.

Gold: mixed-line FAIL number=1. comment-interior OK; snag TRIP. CJK README OK; `fn 契約` on src.rs FAIL ident. fence-number FAIL `30 → 60`. `docs/generated/api.rs` FAIL ident+number (weft `--only docs` OK — DESTROYER_WEFT glob, cited).

Holes:

| object | woof `--only prose` | contrast |
| --- | --- | --- |
| sitbone `77df1da` | FAIL leaked=144, **README ident ins=114** | tally `--chg` leaked=22 Makefile; weft leaked=21 Makefile-only |
| new bash sample, no number | FAIL ident=4 | tally `--chg` OK |
| openssl sample + `2048` | FAIL ident=23 number=3 | tally `--chg` OK |
| README `77df1da→98a8009` | FAIL number **77 → 98** | letter-prefix SHA OK (text) |
| voidtrace `ce44c93` | FAIL leaked=16 (`557` + dates + tick SHAs) | weft `--only docs` OK |
| sitbone ADR `98a8009` | FAIL leaked=180 | weft OK (`docs/adr` glob); tally `--chg` still 106 |
| indented `fn 契約` / `fetch_user` | **OK text** | rust fence CJK FAIL ident |
| `notes.txt` / CHANGELOG CJK ident | OK | src.rs FAIL |
| fence/body swap 60↔30 | **OK (move)** | tally `--chg` FAIL two number chgs |
| `printf '\x00\xff'` | UnicodeDecodeError rc=1 | file input OK leaked=0 |
| `git mv src/foo.rs src/bar.rs` | OK files=1 leaked=0 | — |
| Cargo.lock version | OK skipped_lock=1 | kizu `9349dc5` still names Cargo.toml string |

## Dogfood targets

- sitbone `77df1da`, ADR `98a8009`
- voidtrace `ce44c93`
- kizu `9349dc5` (gold Cargo.toml string)
- woof / tally / weft fixtures under `/tmp/destroy-woof/fixtures/`
- weft 0.2, tally 0.2, snag 0.2 as contrast

## Surprises

- 114 is exact: sitbone README ident inserts, not a round number.
- Letter-prefix SHAs are free on README; digit-prefix SHAs are a fake `77 → 98`. The same SHA quoted is a string; unquoted on `.rs` is ident+number.
- Fence/body swap is a move. tally's fence tag is the only reason `--chg` still sees `30 → 60`.
- DESTROYER_WEFT CJK-as-text is closed on `src.rs` and open on every code sample that is not a fence.

## Failures

- Genuine markdown with dates / run ids / SHAs fail `--only prose`. weft `--only docs` passes them. That is class-not-path working, with the wrong tokens.
- Binary / rename / lockfile skip inherited from weft. Occupancy of nothing.
- Inline `` `30` `` is string, not number. Gate still fails.

## Suggested mutations

- Compose tally `--chg` (already in flight). Do not clone snag `--forbid number`.
- Hex/hash tokens.
- Ident-grade CJK/ASCII on indented, RST, `.txt`, CHANGELOG samples.
- Fence vs body SequenceMatcher (tally already tags `fence`).
- Binary class; stdin exit 2; rename of a non-prose path leaks.

## Kill / keep

**Mutate, do not kill.** Mixed-line `30 → 60` still fails. `docs/generated/api.rs` still fails. Fence `30→60` still fails. Comment-interior still passes. The 114-ident flood, SHA split, and indented CJK-as-text are the next peel — not a reason to throw away the class gate.

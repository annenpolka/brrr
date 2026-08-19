# mutation-99 — tally

## Primitive

A unified diff is a superposition of syntactic classes. **tally `--chg`** is woof’s `--only prose` gate with a fence-local exception: **a fence number *change* (`30→60`) leaks; a new fence sample (ident flood, `2048` insert) does not.**

woof `--only prose` is class-not-path; a fenced timeout sample is number ply. Hole: a new bash sample is 114 ident inserts, drowning the `30→60` change. Mixed-line `30→60` still FAIL. Not snag `--forbid number` — compose or cite.

## Why this might not exist

Reviewers already say “this was supposed to be a docs PR” after a README grows a openssl sample and a Makefile quietly drops `tccutil`. weft frees the README because it is a docs path. woof projects the fence as code, then the sample’s ident inserts drown the timeout change the gate exists to name. snag `--forbid number` would trip the sample’s `2048` *and* `// timeout 30`. Nobody asks: *did a fenced number **change**, or did we just paste a sample?*

## How to run

```bash
./demo.sh
./demo.sh 0
./tally --selftest
./tally --help
git diff | ./tally --only prose --chg
git diff | ./tally --only prose
git diff | ./tally --only prose --chg --emit
```

Python 3.9+, stdlib. Exit 0 = clean, 1 = leak, 2 = usage.

`--only prose` (alias `--only docs`) = comment+text tokens, no path exception. `--chg` drops fence ident/kw/string flood and fence number *inserts*; only fence number *changes* (`30→60`) leak from a fence. `--only comments` is comment only. Comment-interior numbers stay comment ply.

## Empirical transcript

### v0.1 — fence ident flood is not a leak; fence number *inserts* still are

`--selftest` 36/36. `./demo.sh 0` PASS=49 FAIL=0. `tally 0.1`.

DESTROYER_WEFT fence-number fixture:

```
$ ./tally --only prose --chg < fixtures/fence-number.md.diff
tally FAIL  only=prose  chg  stdin  files=1  leaked=1  number=1
  README.md:5  number  chg  30 → 60  fence
# rc=1

$ ./weft --only docs < fixtures/fence-number.md.diff
weft OK  only=docs  stdin  files=1  leaked=0
```

A new bash sample with no number:

```
$ ./tally --only prose --chg < fixtures/fence-new-sample.md.diff
tally OK  only=prose  chg  stdin  files=1  leaked=0

$ ./tally --only prose < fixtures/fence-new-sample.md.diff
tally FAIL  ident=…
```

Sitbone-shaped flood (openssl sample, `2048` / `3650` inserts):

```
$ ./tally --only prose < fixtures/fence-ident-flood.md.diff
tally FAIL  leaked=27  ident=23  number=3  string=1

$ ./tally --only prose --chg < fixtures/fence-ident-flood.md.diff
tally FAIL  leaked=3  number=3
  README.md:7  number  ins  2048  fence
  README.md:13  number  ins  2048  fence
  README.md:13  number  ins  3650  fence
```

Ident flood gone. `2048` insert still a number leak — that is the v0.2 hole.

Mixed-line still FAIL (not a fence):

```
$ ./tally --only prose --chg < fixtures/mixed-money.diff
tally FAIL  only=prose  chg  stdin  files=1  leaked=1  number=1
  src.rs:2  number  chg  30 → 60
```

Comment-interior still OK; snag cited, not cloned:

```
$ ./tally --only prose --chg < fixtures/comment-number.diff
tally OK  leaked=0
$ snag --forbid number < fixtures/comment-number.diff
snag TRIP  30 → 60
```

sitbone `77df1da` (README + Makefile):

```
$ git diff 77df1da^..77df1da | woof --only prose
woof FAIL  leaked=144  ident=126  kw=8  number=5  string=5

$ git diff 77df1da^..77df1da | tally --only prose --chg
tally FAIL  leaked=25  ident=12  kw=4  number=5  string=4
# Makefile still ~21. README: string ins `make app`, number ins 2048, 2048, 3650.
```

weft still: FAIL leaked=21, Makefile only, README 2048 not a leak.

| object | weft `--only docs` | woof `--only prose` | tally `--chg` v0.1 |
| --- | --- | --- | --- |
| mixed line `30→60` | FAIL number | FAIL number | FAIL number |
| comment-interior | OK | OK | **OK (not snag)** |
| fence `30→60` | **OK** (swallow+path) | FAIL number | **FAIL number chg** |
| new bash sample, no number | OK | FAIL ident flood | **OK** |
| new bash sample + `2048` | OK | FAIL ident+number | FAIL **number ins 2048** |
| sitbone `77df1da` | FAIL Makefile=21 | FAIL 144 ident=126 | FAIL 25; README 2048 ins |
| `docs/generated/api.rs` | **OK** (glob) | FAIL ident+number | FAIL ident+number |

### v0.2 — fence numbers leak only on *change*

Forced by the v0.1 sitbone transcript, not by taste. Ident flood was gone; `2048` insert still drowned the *change* question. DESTROYER_WEFT’s fence fixture is `30→60` (chg). sitbone’s openssl sample is `2048` (ins). Those must not be the same leak.

`--selftest` 36/36. `./demo.sh 0` PASS=49 FAIL=0. `tally 0.2`.

```
$ ./tally --only prose --chg < fixtures/fence-ident-flood.md.diff
tally OK  only=prose  chg  stdin  files=1  leaked=0
# rc=0  (v0.1 was number ins 2048, 3650)

$ ./tally --only prose --chg < fixtures/fence-number.md.diff
tally FAIL  only=prose  chg  stdin  files=1  leaked=1  number=1
  README.md:5  number  chg  30 → 60  fence
# rc=1  unchanged

$ ./tally --only prose --chg < fixtures/mixed-money.diff
tally FAIL  src.rs:2  number  chg  30 → 60
# rc=1  unchanged; not a fence
```

sitbone `77df1da` after change-only:

```
$ git diff 77df1da^..77df1da | tally --only prose --chg
tally FAIL  only=prose  chg  stdin  files=2  leaked=22  ident=12  kw=4  number=2  string=4
# Makefile=21. README.md=1: string ins `make app` (inline tick, not a fence).
# 2048 / 3650 gone. ident flood gone.
```

weft still: FAIL leaked=21, Makefile only.

| object | v0.1 `--chg` | v0.2 `--chg` |
| --- | --- | --- |
| fence `30→60` | FAIL number chg | **FAIL number chg** |
| new sample + `2048` | FAIL number ins | **OK** |
| sitbone README `2048` | number ins=3 | **not a leak** |
| sitbone Makefile | leak | leak (21) |
| mixed-line `30→60` | FAIL | FAIL |

Stop: fence number *change* is distinct from fence ident flood.

## Dogfood targets

- DESTROYER_WEFT fence-number fixture (`fixtures/fence-number.md.diff`).
- sitbone `77df1da` (Makefile vs README bash sample) — DESTROYER_WEFT gold.
- weft 0.2 (mutation-50); woof 0.2 (mutation-90); snag 0.2 (mutation-61) as contrast only.

## Surprises

- Tagging fence tokens and matching them separately is load-bearing. Without it, a prose `30` can pair with a fence `60`.
- `--chg` is fence-local on purpose. Global `--chg` (only `op=chg` everywhere) would green the Makefile `tccutil` deletes (they are `del`, not `chg`). That is occupancy of nothing.
- Inline `` `make app` `` on the sitbone README is still a *body* string leak. `--chg` does not touch it. woof named that hide; not this primitive.

## Failures

- Inline `` `make app` `` on sitbone README is still a body string leak (1 row). `--chg` is fence-local; inline ticks are not fences. woof named that hide.
- Makefile `2>/dev/null` is a number *delete*. Honest, a bit sad. Same ply weft already failed on.
- Genuine markdown commits that bump a prose number (`0.6.0→0.7.0` in README body) still fail. `--chg` is not “numbers in markdown are free.”
- Number inside `//` stays comment ply. Use snag `--forbid number`.
- Binary / rename / lockfile skip are weft’s. Untouched.

## Suggested mutations

- Hex/hash tokens so ADR `98a8009` is one ident.
- Markdown inline ticks as text, not string, so sitbone `` `make app` `` is not the leftover row.
- Compose in CI: `tally --only prose --chg` then `snag --forbid number` on the same stdin.

## Kill / keep

**Keep.** The object is still weft/woof’s: “this was supposed to be comment/docs-only; a number leaked.” Mixed-line `30 → 60` still fails. The mutation is that a new fence sample is not 114 ident inserts and is not a `2048` number leak. DESTROYER_WEFT fence `30→60` is still FAIL number chg. sitbone `77df1da` Makefile still leaks; README fence numbers do not. That is the stop.

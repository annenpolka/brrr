# DESTROYER — woof

Adversarial pass on the CI gate that fails a comment+prose-only patch if any other ply class leaked — **regardless of path**. No rewrites: the failures are conceptual except a binary-stdin traceback (operational), left unpatched so the class holes stay visible.

- **woof** (mutation-90) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10d91539263d`
- Contrast: **tally** `--chg` (mutation-99) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7db4d4bb2bf3`
- Cite, do not re-run: [DESTROYER_WEFT.md](DESTROYER_WEFT.md) (path glob `--only docs`). Cite, do not clone: snag `--forbid number`.
- Transcript: `/tmp/destroy-woof/transcript.txt`
- Follow-up: `/tmp/destroy-woof/followup.txt`
- Fixtures: `/tmp/destroy-woof/fixtures/`
- Attack driver: `/tmp/destroy-woof/attack.py`
- `./woof --selftest` → `Ran 29 tests in 0.004s OK` after the attacks. `./demo.sh 0` → `PASS=39 FAIL=0`. `woof 0.2`. Victim untouched.

Attacks: new bash sample 114 ident inserts after v0.2 fence projection, hex/hash ADR SHAs, CJK identifiers still `text` on indented/.txt/CHANGELOG/RST, binary stdin, rename occupancy, fence/body swap as a move, comment-interior `30→60` vs mixed-line.

Verdict: **mutate, do not kill.** Mixed-line `30 → 60` is still `woof FAIL number=1`. `docs/generated/api.rs` still fails ident+number (the DESTROYER_WEFT glob is closed here). A rust fence `30→60` is still number ply. Comment-interior still passes. The attacks show where `--only prose` is still a *dialect of the path* (prose ext / basename / indented vs fenced), where a SHA is a digit prefix plus leftover text, where a new fence sample is 114 ident inserts, and where binary/rename/lockfile remain occupancy of nothing.

---

## Primitive restated

A unified diff is a superposition of syntactic classes. woof projects it onto `--only prose` (comment+text tokens, **no path exception**) and **fails the build** if any other class leaked. Exit 0 clean, 1 leak, 2 usage. `--only docs` on woof is the same token alias, not weft's `docs/**` glob. Markdown fence interiors are the tagged dialect (v0.2). Number inside `//` stays comment ply.

---

## 1. New bash sample — fence=code turns a docs PR into 114 ident inserts (conceptual, load-bearing)

v0.2 closed DESTROYER_WEFT's swallow: a rust fence `30→60` is number ply, not one backtick-string. The second DESTROYER_WEFT decision ("fence = code even on a docs path") is now the product. A *new* sample has no `30→60` to name. It has inserts.

```
$ ./woof --only prose  < fence-new-sample.md.diff
woof FAIL  only=prose  stdin  files=1  leaked=4  ident=4
  README.md:5  ident  ins  echo
  README.md:5  ident  ins  hello
  README.md:6  ident  ins  make
  README.md:6  ident  ins  app
# rc=1

$ ./tally --only prose --chg  < fence-new-sample.md.diff
tally OK  only=prose  chg  stdin  files=1  leaked=0
# rc=0
```

openssl-shaped flood (`2048` / `3650` inserts, DESTROYER_WEFT's sitbone sample):

```
$ ./woof --only prose  < fence-ident-flood.md.diff
woof FAIL  only=prose  stdin  files=1  leaked=27  ident=23  number=3  string=1
  README.md:7  number  ins  2048
  …
# rc=1

$ ./tally --only prose --chg  < fence-ident-flood.md.diff
tally OK  only=prose  chg  stdin  files=1  leaked=0
# rc=0
```

Real sitbone `77df1da` (README + Makefile) — DESTROYER_WEFT gold, now with fence projection:

```
$ git diff 77df1da^..77df1da | woof --only prose
woof FAIL  only=prose  stdin  files=2  leaked=144  ident=126  kw=8  number=5  string=5
# rc=1

emit counts (path class op):
  114  README.md ident ins
   12  Makefile ident del
    4  Makefile kw del
    4  README.md kw ins
    3  README.md number ins     # 2048, 2048, 3650
    2  Makefile number del
    2  Makefile string ins
    2  README.md string ins     # `make app`, EOF
    1  Makefile string del
```

**114 README ident inserts.** That is the number CANDIDATE named. The timeout the gate exists to see is three number *inserts* drowned in bash tokens.

```
$ git diff 77df1da^..77df1da | tally --only prose --chg
tally FAIL  only=prose  chg  stdin  files=2  leaked=22  ident=12  kw=4  number=2  string=4
# Makefile still ~21. README leftover is inline `make app` (not a fence).
# 114 idents gone. 2048 / 3650 gone.

$ git diff 77df1da^..77df1da | weft --only docs
weft FAIL  only=docs  stdin  files=2  leaked=21  …
# Makefile only. README 2048 is not a leak. DESTROYER_WEFT gold, cited.
```

tally `--chg` already exists (mutation-99). It is fence-local: ident flood and fence number *inserts* drop; fence `30→60` still fails. Do not clone it into woof in this pass. The hole is woof's: **prose-as-class after fence=code cannot tell "a timeout changed" from "someone pasted a sample."**

The rust fence fixture still holds (v0.2 working, tally agrees):

```
$ ./woof --only prose  < fence-number.md.diff
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  README.md:5  number  chg  30 → 60
# rc=1

$ ./tally --only prose --chg  < fence-number.md.diff
tally FAIL  … number  chg  30 → 60  fence
# rc=1

$ ./weft --only docs  < fence-number.md.diff
weft OK  only=docs  stdin  files=1  leaked=0
# DESTROYER_WEFT glob+swallow. Cite, do not re-run.
```

---

## 2. Hex/hash tokens — ADR SHAs are a digit prefix, not one ident (conceptual, load-bearing)

`_NUMBER` is a leading digit run (plus `0x…`). `_IDENT` / prose `text` is letters. A git SHA is neither.

```
$ ./woof --only prose  < README 77df1da → 98a8009
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  README.md:1  number  chg  77 → 98
# rc=1
# emit: README.md	1	number	chg	77	98
# tails df1da / a8009 are text on a prose path — allowed.
```

The leak is a fake version bump. The SHA did not become one token.

Letter-prefix SHA is entirely text on README, so it is **free**:

```
$ ./woof --only prose  < README e9b0f75 → ce44c93
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0
```

Digit-prefix → letter-prefix drops a number and frees the rest:

```
$ ./woof --only prose  < docs/adr/0019.md  557c76f → e9b0f75
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  docs/adr/0019.md:2  number  del  557
# rc=1
```

On a code path the same bytes split into ident+number:

```
$ ./woof --only prose  < src.rs  77df1da → 98a8009
woof FAIL  … leaked=2  ident=1  number=1
  src.rs:1  ident  chg  df1da → a8009
  src.rs:1  number  chg  77 → 98
```

Quoted, the SHA is one **string** (`77df1da → 98a8009`). `0xdeadbeef → 0xcafebabe` is one number (the `0x` rule). Neither is "a hash token."

Real trees:

| commit | claim | woof `--only prose` | weft `--only docs` |
| --- | --- | --- | --- |
| sitbone `98a8009` ADR-0019 | docs | **FAIL leaked=180** ident=59 kw=8 number=97 string=16 | **OK leaked=0** (`docs/adr` glob) |
| voidtrace `ce44c93` finite breakpoint ci | docs | **FAIL leaked=16** number=10 string=6 | **OK leaked=0** |

`98a8009` is a new markdown file with swift fences. Dates split (`2026`, `04`, `10`). ADR numbers (`0019`, `0014`). Fence idents (`PresenceStatus`, `smoothedScore`). tally `--chg` still FAIL leaked=106 — fence ident flood drops, **body numbers and dates remain**. `--chg` is not hex tokens.

`ce44c93` is the SHA object itself:

```
$ git diff voidtrace ce44c93 | woof --only prose
woof FAIL  only=prose  stdin  files=1  leaked=16  number=10  string=6
  docs/execplans/kernel-gun-semantics.md:140  number  ins  2026
  … 08  01  15  26  25
  docs/execplans/…:140  string  ins  66d6fa1
  docs/execplans/…:140  string  ins  6e3368b
  docs/execplans/…:140  string  ins  557c76f
  docs/execplans/…:1049  number  ins  557
  docs/execplans/…:1050  number  ins  557
```

Backtick SHA is a string. Unquoted `557c76f` is number `557`. A "record the CI run" PR is not comment+prose-only once dates and SHAs are numbers. weft `--only docs` still frees the path — that is DESTROYER_WEFT, cited. woof's class gate is what sees them, and it sees the wrong tokens.

---

## 3. CJK identifiers as text — closed on `src.rs`, open on indented / `.txt` / CHANGELOG / RST (conceptual, load-bearing)

DESTROYER_WEFT's money shot `fn 契約 → fn 資産` on a code path is **closed**:

```
$ ./woof --only prose  < src.rs fn 契約() → fn 資産()
woof FAIL  only=prose  stdin  files=1  leaked=1  ident=1
  src.rs:1  ident  chg  契約 → 資産
# rc=1

$ ./woof --only prose  < CJK README 契約は蒸留 → 契約は資産
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0
```

CJK README is still `text`. `--only comments` still FAIL `text=1`. Mixed ASCII prefix still leaks `timeout_ → delay_` and frees `秒`. Fullwidth `３０ → ６０` is number and **fails**. Japanese `// 秒 → // タイムアウト` is comment ply, OK. A rust fence on README projects CJK as ident (`契約 → 資産`, rc=1). That is v0.2 working.

**Indented samples are still the prose dialect.** No fence opener, no tagged lexer. CJK (and ASCII) identifiers are `text`:

```
$ ./woof --only prose  < README indented  fn 契約() → fn 資産()
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0  --emit empty

$ ./woof --only prose  < README indented  fn fetch_user() → fn fetch_account()
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0
```

Add a timeout on the same indented line: FAIL **number only**. The ident rename stays text. RST `.. code-block:: rust` is the same object (`.rst` is a prose ext; no fence projector): ident free, `30→60` leaks.

`.txt` and the `CHANGELOG` basename are prose files. A function rename there is free:

```
$ ./woof --only prose  < notes.txt fn 契約() → fn 資産()
woof OK  leaked=0

$ ./woof --only prose  < CHANGELOG fn 契約() → fn 資産()
woof OK  leaked=0
```

`--only prose` is class-not-path for `docs/generated/api.rs`. It is still path-class for "what is a prose file." Indented markdown, RST, `.txt`, `CHANGELOG`, `AGENTS`, `CLAUDE` keep CJK identifiers as `text`. DESTROYER_WEFT asked for ident-grade CJK on *code paths*. woof did that. The hide moved to every code sample that is not a backtick/tilde fence.

---

## 4. Binary — skip is fail-open; stdin traceback is rc=1 (operational + conceptual)

Same class as DESTROYER_WEFT / zanei / plait. Untouched on woof, as CANDIDATE said.

```
$ ./woof --only prose  < Binary files src/secret.bin differ
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0

$ ./woof --only prose  < Binary files docs/media/demo.gif
woof OK  … leaked=0

$ ./woof --only prose  < GIT binary patch src/blob.bin
woof OK  … leaked=0
```

A comments/prose-only PR that also replaced `src/secret.bin` is clean. Path never frees a number; status=`binary` never *is* a number.

Stdin is not the file path's `errors=replace`:

```
$ printf '\x00\xff' | woof --only prose
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 1: invalid start byte
# rc=1  traceback from sys.stdin.read()

$ /dev/urandom | head -c 32 | woof --only prose
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa4 in position 0: invalid start byte
# rc=1
```

Exit 1 is leak. A crash is "this prose PR leaked." File input already replaces:

```
$ ./woof --only prose  /tmp/destroy-woof/fixtures/binary-stdin.diff
woof OK  only=prose  … leaked=0
# rc=0
```

NUL *inside* a text hunk is not a crash: `+let x = 2;\x00secret;` leaked `ident ins secret` and `number 1 → 2`.

A `buffer` decode-or-die (exit 2) would hide the traceback and would not touch gif-skip. Not applied.

---

## 5. Rename / mode — occupancy of nothing (conceptual)

```
$ ./woof --only prose  < git mv src/foo.rs src/bar.rs (100% rename)
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0

$ ./woof --only prose  < chmod +x src/run.sh
woof OK  … files=1 leaked=0

$ ./woof --only prose  < add empty notes.txt
woof OK  … leaked=0

$ printf '' | woof --only prose
woof OK  only=prose  stdin  leaked=0
```

Empty / newline / whitespace / garbage: honest zero. Rename and mode have no ply. A prose-only PR that `git mv`s `src/foo.rs` → `src/bar.rs` is a clean gate. Path change is not a syntactic class. DESTROYER_WEFT named this; woof inherited it.

Lockfile skip is the same occupancy:

```
$ ./woof --only prose  < Cargo.lock 0.6.0→0.7.0
woof OK  only=prose  stdin  files=1  skipped_lock=1  leaked=0
# rc=0
```

kizu `9349dc5` still names the Cargo.toml string and skips the lock (`skipped_lock=1 leaked=1 string=1`). The lock bump beside it is green. Quiet `-q` is exit 0 with no line.

---

## 6. Fence/body swap is a move — tally already tagged fences (conceptual)

woof does not tag fence tokens separately. A body `60` and a fence `30` that swap become del+ins of the same number, collapsed to `mov`. Moves do not leak.

```
$ ./woof --only prose  < README body 60→30, fence 30→60
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0  --emit empty

$ ./tally --only prose --chg  < same
tally FAIL  only=prose  chg  stdin  files=1  leaked=2  number=2
  README.md:2  number  chg  60 → 30
  README.md:5  number  chg  30 → 60  fence
# rc=1
```

The DESTROYER_WEFT fence fixture (`30→60` only) still fails woof. Pair it with a body number that swaps and the gate goes green. tally's fence tag is the peel. Inline `` `30` `` → `` `60` `` is still **string**, not number — the gate fails, the class is a lie. HTML `<!-- timeout 30 -->` on README is comment ply (OK); on `src.rs` the same markup is punct+number and leaks. Untitled fences still project as C and name `30 → 60`.

---

## 7. Comment-interior `30→60` vs mixed-line — the gate holds; do not clone snag (survived)

```
$ ./woof --only prose  < mixed-money.diff
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  src.rs:2  number  chg  30 → 60
# rc=1
# emit: src.rs	2	number	chg	30	60

$ ./woof --only prose  < comment-number.diff   # // timeout 30 → // timeout 60
woof OK  only=prose  stdin  files=1  leaked=0
# rc=0

$ ./snag --forbid number  < comment-number.diff
snag TRIP  forbid=number  stdin  files=1  hits=1  number=1
  src.rs:1  number  chg  30 → 60
# rc=1

$ ./weft --only docs  < comment-number.diff
weft OK  leaked=0
```

Surface class is comment. woof does not peel `//`. That invert is snag. Compose in CI; do not clone `--forbid number` into `--only prose`. Mixed-line still splits: comment rewrite allowed, timeout change failed. That is the product.

`docs/generated/api.rs` `fetch_user→fetch_account` + `30→60` is still FAIL ident+number. weft `--only docs` is still OK. DESTROYER_WEFT's glob is closed on woof. Cited, not re-run.

---

## What survived

- Gold mixed-line: `timeout 30→60` + `// seconds→secs` is still `woof FAIL number=1`. `--emit` is `src.rs	2	number	chg	30	60`.
- Gold comment-interior: OK under prose. snag `--forbid number` TRIP. Not cloned.
- Gold CJK: README OK (text). `fn 契約` on `src.rs` FAIL ident. Fence CJK on README FAIL ident.
- Gold fence-number: FAIL number `30 → 60`. weft still OK (glob+swallow). tally `--chg` still FAIL fence number chg.
- Gold `docs/generated/api.rs`: FAIL ident+number. weft `--only docs` OK. `--only docs` on woof is the alias, also FAIL.
- Gold sitbone `77df1da`: still FAIL. weft Makefile-only leaked=21. woof leaked=144 because fence=code.
- Gold kizu `9349dc5`: FAIL Cargo.toml string `0.6.0 → 0.7.0`, lock skipped.
- Untitled fence `30→60`: FAIL number. Fullwidth digits: FAIL number. Mixed `timeout_秒`: FAIL `timeout_ → delay_`.
- Empty / newline / garbage stdin: OK leaked=0, no traceback (text).
- `--selftest` 29/29. `./demo.sh 0` 39/39. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still "this was supposed to be comment/prose-only; a number or ident leaked." Mixed-line `30 → 60`, `docs/generated/api.rs`, rust-fence `30→60`, `fn 契約` on `src.rs` — all still fail. Nothing in this battery turned that into `paths-filter` or into weft's glob. Do not kill because a new bash sample is 114 idents, because `77df1da` is `77 → 98`, or because indented CJK is text. Those are mutations. Killing them would throw away a real class gate to hide fence=code.

| do not kill because | mutate toward |
| --- | --- |
| Mixed-line `30→60` rc=1; api.rs ident+number; fence-number `30→60`; CJK `src.rs` ident; comment-interior OK (not snag); kizu `9349dc5` Cargo.toml string | **Compose tally `--chg`, do not clone snag.** A new fence sample is not 114 ident inserts and is not a `2048` insert. Fence `30→60` stays a leak. mutation-99 already ships this. |
| | **Hex/hash tokens so ADR `98a8009` / voidtrace `557c76f` / sitbone `77df1da` are one ident.** Digit-prefix SHAs must not be number `77 → 98`. Letter-prefix SHAs must not be free text. Dates (`2026-08-01`) are a cousin. |
| | **Indented / RST / `.txt` / CHANGELOG samples are not a free ident ply.** `fn 契約` in an indented README is the DESTROYER_WEFT CJK hole, moved. Keep CJK *prose* as text. |
| | **Fence vs body numbers are not one SequenceMatcher.** Body `60` swapping with fence `30` is two changes, not a move. tally already tags `fence`. |
| | **Binary is a leak (or class `binary`), not skip.** `src/secret.bin` under `--only prose` must fail. Stdin decode-or-die exit 2 (replace on stdin would fail *open*). |
| | **Rename/mode of a non-prose path is a leak under `--only prose`.** `git mv src/foo.rs src/bar.rs` is not vacuous. |
| | **Lockfile skip is not prose-only OK.** `--only prose` on `Cargo.lock` should be skip-visible as usage, or lock bumps should leak unless `--locks` is on. |
| | Inline ticks as text (or as the tagged dialect), so `` `30` `` is a number and sitbone `` `make app` `` is not the leftover row. Number-in-comment stays comment ply; the invert is still snag. |

A one-line `sys.stdin.buffer` decode-or-die would hide the traceback and would not touch 114 idents, SHA splits, or indented CJK. Not applied.

Do not grow a review platform. The next mutation is *fence-change vs fence-insert* (tally, already in flight) plus hash tokens plus ident-grade CJK on indented samples — not a prettier leak dump.

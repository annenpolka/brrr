# DESTROYER — weft

Adversarial pass on the CI gate that fails a docs/comments-only patch if any other ply class leaked. No rewrites: the failures are conceptual except a binary-stdin traceback (operational), left unpatched so the class/path holes stay visible.

- **weft** (mutation-50) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b68-3200-7781-bf46-49a3c771f5ff`
- Transcript: `/tmp/destroy-weft/transcript.txt`
- Follow-up: `/tmp/destroy-weft/followup.txt`
- Fixtures: `/tmp/destroy-weft/fixtures/`
- Attack driver: `/tmp/destroy-weft/attack.py`
- `./weft --selftest` → `Ran 22 tests in 0.002s OK` after the attacks. `./demo.sh 0` → `PASS=28 FAIL=0`. `weft 0.2`.

Attacks: markdown code fences with numbers, README version bumps, CJK, generated docs, empty diff, binary, `--only comments` on a comment-only PR that also renamed an ident.

Verdict: **mutate, do not kill.** The mixed-line `30 → 60` is still `weft FAIL number=1`. sitbone `77df1da` still fails on the Makefile and not the README. A comment rewrite that also renamed `start → boot` (or sitbone `threshold → presentThreshold`) is still ident leak, rc=1. The attacks show where `--only docs` is a *path* glob, where CJK identifiers are `text` (and therefore free on code paths), where backtick fences swallow number ply into one string, and where binary/rename/lockfile are occupancy of nothing.

---

## Primitive restated

A unified diff is a superposition of syntactic classes. weft projects it onto `--only docs` or `--only comments` and **fails the build** if any other class leaked. Exit 0 clean, 1 leak, 2 usage. `--only docs` is comment+text on code paths and *any* class on documentation paths. `--only comments` is comment tokens only, any path.

---

## 1. Markdown code fences with numbers — backtick is a string; path frees it anyway (conceptual)

A README fence that is the only copy of a timeout:

```
```rust
-let timeout = 30;
+let timeout = 60;
```
```

```
$ ./weft --only docs  < fence-number.md.diff
weft OK  only=docs  stdin  files=1  leaked=0
# rc=0

$ ./weft --only comments  < fence-number.md.diff
weft FAIL  only=comments  stdin  files=1  leaked=1  string=1
  README.md:4  string  chg  rust\nlet timeout = 30;\nfn retry() {}\n → rust\nlet timeout = 60;\nfn retry() {}\n
# rc=1
```

`--only comment,text` is the same string leak. `--emit` under docs is an empty TSV. The number ply never exists. Markdown dialect treats `` ` `` as a string quote that may span newlines, so the language tag plus the whole block is one token. A python fence that renamed `fetch_user → fetch_account` is the same object: docs OK, comments FAIL `string=1`.

Same bytes on `src.rs` fail `--only docs` as **string**, not number — still the backtick, just without the path exception.

**Indented and tilde fences are a different object.** No backtick, so the C-ish lexer sees a number:

```
$ indented README --only comments
weft FAIL  only=comments  stdin  files=1  leaked=1  number=1
  README.md:3  number  chg  30 → 60
# rc=1

$ tilde fence README --only comments
weft FAIL  only=comments  … leaked=1  number=1
  README.md:3  number  chg  30 → 60
```

`--only docs` is still OK: README is a docs path. The CI verb “no code ply leaked” cannot see a fenced example, indented or not. `--only comments` can see indented/tilde as `number` and backticks as `string`. Neither is “the number in the fence.”

HTML comments in markdown *are* comments (`<!--` / `-->` in the md dialect). `<!-- timeout 30 -->` → `<!-- timeout 60 -->` on README is `--only comments` OK. On `src.rs` the same markup is punct + number and leaks `30 → 60`. Fence language is path × quote character, not “this looks like code.”

---

## 2. README version bumps — path wins; `0.6.0` in prose is not `0.6.0` (conceptual)

```
$ ./weft --only docs  < README 0.6.0→0.7.0
weft OK  only=docs  stdin  files=1  leaked=0
# rc=0

$ ./weft --only comments  < README 0.6.0→0.7.0
weft FAIL  only=comments  stdin  files=1  leaked=1  number=1
  README.md:2  number  chg  0.6 → 0.7
# rc=1

$ ./weft --only docs  < Cargo.toml 0.6.0→0.7.0
weft FAIL  only=docs  stdin  files=1  leaked=1  string=1
  Cargo.toml:3  string  chg  0.6.0 → 0.7.0
# rc=1

$ ./weft --only docs  < README+Cargo.toml version bump
weft FAIL  only=docs  stdin  files=2  leaked=1  string=1
  Cargo.toml:3  string  chg  0.6.0 → 0.7.0
```

README is free. Cargo.toml is the leak. That is v0.2 working. The tokenizer split is the extra lie: unquoted `0.6.0` is number `0.6` + punct + number `0` (`_NUMBER` allows one dotted fraction). Quoted `"0.6.0"` is one string. A project that versions only in README (or a badge) can bump the product under `--only docs`.

Real kizu:

| commit | claim | `--only docs` | `--only comments` |
| --- | --- | --- | --- |
| `f487d55` drop `v0.1` / `v0.3` from README | docs | **OK leaked=0** | FAIL leaked=44 ident=38 number=2 |
| `6bf4f46` sync README v0.5 + `README.ja.md` | docs | **OK leaked=0** | FAIL leaked=1179 ident=487 text=460 number=33 |
| `9349dc5` release v0.7.0 | release | FAIL `Cargo.toml:3 string 0.6.0 → 0.7.0` skipped_lock=1 | (code ply) |

The money shot from CANDIDATE still holds: README numbers are not leaks; the Cargo.toml string is. The destroyer hole is the other direction — a README-only version bump is a number ply the gate is forbidden to see.

---

## 3. CJK — identifiers are `text`; `--only docs` allows `text` on code paths (conceptual, load-bearing)

CJK README prose is the demo split and it survived:

```
$ ./weft --only comments  < CJK README 契約は蒸留 → 契約は資産
weft FAIL  only=comments  stdin  files=1  leaked=1  text=1
  README.md:1  text  chg  契約は蒸留 → 契約は資産
# rc=1

$ ./weft --only docs  < CJK README
weft OK  only=docs  stdin  files=1  leaked=0
```

**A Japanese function rename on a code path is also `text`, and `text` is in the docs alias:**

```
$ ./weft --only docs  < src.rs fn 契約() → fn 資産()
weft OK  only=docs  stdin  files=1  leaked=0
# rc=0

$ ./weft --only comments  < CJK ident
weft FAIL  only=comments  … leaked=1  text=1
  src.rs:1  text  chg  契約 → 資産

$ ./weft --only code  < CJK ident
weft FAIL  only=code  … leaked=1  text=1
  src.rs:1  text  chg  契約 → 資産
```

`--only docs` is “comment+text everywhere, plus any class on docs paths.” Unicode letters (`unicodedata` category `L`) emit `text`, not `ident`. A Swift/Rust unicode identifier rename is a clean docs PR. `--only code` refuses it because text is not code. The docs gate is the one that would ship.

ASCII prefix survives: `timeout_秒 → delay_秒` leaks `ident  timeout_ → delay_` and frees `秒`. Fullwidth `３０ → ６０` is a number (`\d` matches Nd digits) and **fails** `--only docs` on `src.rs`. The gate catches 全角 digits by accident of Unicode digit class and misses 契約 as a name.

Japanese comment rewrite `// 秒` → `// タイムアウト` is `--only comments` OK (comment ply). Real trees:

```
$ git diff skills 6b19433 | weft --only docs    # kinsoku/SKILL.md
weft OK  only=docs  stdin  files=1  leaked=0

$ git diff sitbone c3a61ff | weft --only docs  # CLAUDE.md CJK + log stream
weft OK  only=docs  stdin  files=1  leaked=0

$ git diff tenaoshi 70b450d | weft --only docs  # prompt.md CJK + specs/tenaoshi.pkl
weft FAIL  only=docs  stdin  files=4  leaked=9  ident=5  kw=1  string=3
  specs/tenaoshi.pkl:476  string  ins  MAN-023
  …
```

Markdown CJK is free. The pkl beside it is the leak. Same shape as sitbone README+Makefile.

---

## 4. Generated docs — `docs/` swallows `lib.rs` and Makefile (conceptual, load-bearing)

`is_doc_path` is true for `*.md` *or* any file whose parent path contains `docs` / `doc` / `documentation` / `adr`.

```
$ ./weft --only docs  < docs/generated/CONTRACTS.md 30→60
weft OK  only=docs  stdin  files=1  leaked=0

$ ./weft --only docs  < docs/generated/lib.rs  fetch_user→fetch_account, 30→60
weft OK  only=docs  stdin  files=1  leaked=0
# rc=0  --emit is empty

$ ./weft --only comments  < docs/generated/lib.rs
weft FAIL  only=comments  stdin  files=1  leaked=2  ident=1  number=1
  docs/generated/lib.rs:1  ident  chg  fetch_user → fetch_account
  docs/generated/lib.rs:1  number  chg  30 → 60

$ ./weft --only docs  < generated/schema.json
weft FAIL  only=docs  … leaked=1  number=1
  generated/schema.json:2  number  chg  30 → 60

$ ./weft --only docs  < generated/README.md
weft OK  only=docs   # md ext, even outside docs/

$ ./weft --only docs  < docs/Makefile TIMEOUT 30→60
weft OK  only=docs  stdin  files=1  leaked=0
```

Directory name is the policy. `generated/` is not special. `docs/` is a blanket. A “docs PR” that rewrites `docs/generated/lib.rs` or `docs/Makefile` is a clean gate. `--only comments` still sees the ident and the number — the path exception is docs-only.

voidtrace `7831a0e` (feat + `docs/generated/*.md` + kernel.ts): `--only docs` FAIL leaked=9343 from `packages/kernel/src/evaluate.ts` (1451) etc. The generated markdown is absent from the leak list. `557c76f` / `ce44c93` (markdown only) are OK. kizu `91ef512` “docs: rewrite README + VHS GIF”: FAIL leaked=160, paths `scripts/demo/fake-agent.sh` 122 + `justfile` 38. The gif is binary-skipped; `docs/media/demo.tape` is under `docs/` and free.

CANDIDATE already said `contracts/prompt.md` is a docs path. It did not say `docs/src.rs` is.

---

## 5. Empty diff — vacuous OK; rename/mode are not a class (survived / conceptual)

```
$ printf '' | weft --only docs
weft OK  only=docs  stdin  leaked=0
# rc=0

$ printf '\n' | weft --only docs
weft OK  … leaked=0

$ ./weft --only docs  < git mv src/foo.rs src/bar.rs (100% rename)
weft OK  only=docs  stdin  files=1  leaked=0

$ ./weft --only comments  < rename-only
weft OK  only=comments  stdin  files=1  leaked=0

$ ./weft --only docs  < chmod +x src/run.sh
weft OK  … files=1  leaked=0

$ ./weft --only docs  < add empty notes.txt
weft OK  … leaked=0

$ ./weft --only docs  < garbage non-diff
weft OK  only=docs  stdin  leaked=0
```

Empty / newline / whitespace / garbage: honest zero. Same class as zanei’s empty diff. Not a walk.

**Rename and mode have no ply.** `files=1 leaked=0`. A docs PR that `git mv`s `src/foo.rs` → `src/bar.rs` (or marks a script executable) is a clean comments-only gate. Path change is not a syntactic class. Occupancy of a rename is unaskable.

---

## 6. Binary — skip is fail-open; stdin traceback is rc=1 (operational + conceptual)

```
$ ./weft --only docs  < Binary files docs/media/demo.gif differ
weft OK  only=docs  stdin  files=1  leaked=0

$ ./weft --only comments  < Binary files gif
weft OK  only=comments  stdin  files=1  leaked=0

$ ./weft --only docs  < Binary files src/secret.bin (code path)
weft OK  only=docs  stdin  files=1  leaked=0

$ ./weft --only docs  < GIT binary patch src/blob.bin
weft OK  only=docs  stdin  files=1  leaked=0

$ ./weft --only docs  < README version + Binary gif
weft OK  only=docs  stdin  files=2  leaked=0
```

`parse_unified` sets `status=binary` and `edits_from_diff` continues. A comments-only PR that also replaced `src/secret.bin` (wasm, png, compiled) is clean. kizu `a1e6422` (`docs: refresh demo.gif` + tape): `--only docs` OK files=2. The tape leaks 110 idents under `--only comments` and is free under docs because it lives in `docs/media/`.

Stdin is not the file path’s `errors=replace`:

```
$ printf '\x00\xff' | weft --only docs
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 1: invalid start byte
# rc=1  traceback from sys.stdin.read()
```

`/dev/urandom` same. Exit 1 is leak. A crash is “this docs PR leaked.” File input already replaces; stdin does not. NUL *inside* a text hunk is not a crash: `+let x = 2;\x00secret;` leaked `ident ins secret` and `number 1 → 2`.

Same class as zanei/plait binary stdin. A `buffer` decode-or-die (exit 2) would hide the traceback and would not touch gif-skip or `docs/lib.rs`. Not applied.

---

## 7. `--only comments` on a comment-only PR that also renamed an ident — the gate holds; lockfiles impersonate it (survived / conceptual)

Genuine comment-only still passes both aliases:

```
$ ./weft --only comments  < // secs → // timeout, ident untouched
weft OK  only=comments  stdin  files=1  leaked=0
# rc=0
```

**The cheat is caught.** Comment rewrite plus `fn start → boot`:

```
$ ./weft --only comments  < comment rewrite + fn start→boot
weft FAIL  only=comments  stdin  files=1  leaked=1  ident=1
  src.rs:1  ident  chg  start → boot
# rc=1
```

Same-line `timeout → delay` plus comment rewrite: FAIL `ident timeout → delay`. `--only docs` fails the same ident. `--emit` is one TSV row, no comment dump. That is the product: comment ply allowed, ident ply failed.

Sitbone-shaped (ADR `///` comments plus `threshold → presentThreshold`, excerpted from `e9b0f75`):

```
$ ./weft --only comments  < sitbone-shaped
weft FAIL  only=comments  stdin  files=1  leaked=5  ident=3  kw=2
  Sources/SitboneCore/PresenceArbiter.swift:10  ident  chg  threshold → presentThreshold
  Sources/SitboneCore/PresenceArbiter.swift:10  ident  ins  Double
  Sources/SitboneCore/PresenceArbiter.swift:12  ident  ins  absentThreshold
  Sources/SitboneCore/PresenceArbiter.swift:13  kw  ins  private
  Sources/SitboneCore/PresenceArbiter.swift:13  kw  ins  let
```

Real `e9b0f75` (hysteresis, not a comment-only message) is the same first row plus the number ply the demo exists for:

```
$ git diff sitbone e9b0f75 | weft --only comments
weft FAIL  only=comments  stdin  files=3  leaked=414  ident=295  kw=79  number=28  string=12
  Sources/SitboneCore/PresenceArbiter.swift:12  ident  chg  threshold → presentThreshold
  …
  Sources/SitboneCore/PresenceArbiter.swift:33  number  chg  0.4 → 0.45
```

No dogfood commit in the last ~150 is a *true* comment-only code PR. The ones `--only comments` accepted as leaked=0 were lockfiles:

```
$ git diff sitbone ef841bd | weft --only comments   # remove staled lock
weft OK  only=comments  stdin  files=1  skipped_lock=1  leaked=0

$ git diff kizu 9758e67 | weft --only comments      # chore: update Cargo.lock
weft OK  only=comments  stdin  files=1  skipped_lock=1  leaked=0

$ ./weft --only comments  < Cargo.lock 0.6.0→0.7.0
weft OK  only=comments  stdin  files=1  skipped_lock=1  leaked=0
```

A “comment-only” CI job on a lockfile bump is green. `skipped_lock=1` is on the verdict line; `-q` is exit 0 with no line. Sitbone `12bc37b` (add `AGENTS.md` `@CLAUDE.md`) is FAIL ident=`@CLAUDE`,`md` under comments and OK under docs — markdown words, not a rename.

Ident rename *inside* a comment body (`// timeout` → `// delay`) is comment ply, OK. Number inside a comment (`// timeout 30` → `// timeout 60`) is comment ply, OK under **both** aliases. CANDIDATE named that. Confirmed. `--only docs` will not catch a timeout bump that only moved inside `//`.

---

## What survived

- Gold mixed-line: `timeout 30→60` + `// seconds→secs` is still `weft FAIL number=1` under docs and under comments. `--emit` is `src.rs	2	number	chg	30	60`.
- Gold sitbone `77df1da`: FAIL leaked=21, paths `{'Makefile': 21}`. README cert `2048` is not a leak.
- Gold kizu `9349dc5`: FAIL Cargo.toml string `0.6.0 → 0.7.0`, lock skipped.
- Gold voidtrace `ce44c93` / sitbone ADR `98a8009` analogue `557c76f`: `--only docs` OK.
- Genuine comment-only rewrite: OK. Comment + ident rename: FAIL ident, one row.
- CJK README: comments FAIL text, docs OK. Japanese `//` comment: comments OK.
- Empty / newline / whitespace / garbage stdin: OK leaked=0, no traceback.
- `--selftest` 22/22. `./demo.sh 0` 28/28. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “this was supposed to be comment/docs-only; a number or ident leaked.” `30 → 60` on the mixed line, Makefile beside README, Cargo.toml beside a lockfile, `start → boot` beside a comment rewrite — all still fail. Nothing in this battery turned that into `paths-filter` or into `git diff --stat`. Do not kill because backticks, `docs/lib.rs`, or CJK-as-text. Those are mutations. Killing them would throw away a real class gate to hide a path glob.

| do not kill because | mutate toward |
| --- | --- |
| Mixed-line `30→60` rc=1; sitbone `77df1da` Makefile-only; kizu `9349dc5` Cargo.toml string; comment+`start→boot` ident leak; CJK README comments≠docs | **`--only docs` is prose files, not `docs/**`.** `docs/generated/lib.rs` and `docs/Makefile` are code ply. Keep `*.md` / README / LICENSE free. |
| | **CJK identifiers on code paths are ident, not text.** `fn 契約 → fn 資産` must fail `--only docs`. Keep CJK *prose* as text (README already works). |
| | **Fences are not one backtick-string.** Project fence contents in the tagged dialect, or at least stop `` ` `` from swallowing the block so `30→60` is a number. Path-aware docs will still free README — that is a second decision (fence = code even on a docs path). |
| | **Binary is a leak (or class `binary`), not skip.** `src/secret.bin` under `--only comments`/`docs` must fail. `docs/media/demo.gif` can stay free if the path exception is prose *files*, or it can be binary-class. |
| | **Rename/mode of a non-doc path is a leak under `--only docs`.** `git mv src/foo.rs src/bar.rs` is not vacuous. |
| | **Lockfile skip is not comment-only OK.** `--only comments` on `Cargo.lock` should be skip-visible as usage, or lock bumps should be `string` leaks unless `--locks` is off *and* `--only docs`. Quiet exit 0 is a green CI on a version ply. |
| | Binary stdin / urandom: fail closed exit 2 (`errors=replace` on stdin would fail *open* on garbage). Number-in-comment stays comment ply; the invert `--forbid number` is still the other gate (CANDIDATE). |

A one-line `sys.stdin.buffer` decode-or-die would hide the traceback and would not touch `docs/lib.rs`, CJK-as-text, or gif-skip. Not applied.

Do not grow a review platform. The next mutation is *path-honest docs* (prose files, not a directory bag) plus ident-grade CJK on code paths, not a prettier leak dump.

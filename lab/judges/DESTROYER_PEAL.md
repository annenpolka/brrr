# DESTROYER — peal

Adversarial pass on **chime as `rg |` filter**. No rewrites of the victim. Failures are conceptual except a binary-stdin traceback (operational), left unpatched so the locator/pin holes stay visible.

- **peal** (mutation-51) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6a-b1f0-7600-ae0c-3b73b8f2249f` HEAD `7e89ad1` *Recover peal's seed file from rg LINE:text pins.*
- Compared with, not cloned: **chime** (`…/subagent-01a01ad1-c9bc-75e2-8872-cc3cdc8f2abf`). No third ambit.
- Transcript: `/tmp/destroy-peal/transcript.txt` (89 cases)
- Follow-up: `/tmp/destroy-peal/followup.txt`, `followup2.txt`
- Fixtures: `/tmp/destroy-peal/fixtures/`
- Attack driver: `/tmp/destroy-peal/attack.py`
- Victim after the battery: `python3 -m unittest tests.test_peal -q` → `Ran 26 tests in 0.104s OK`. `./demo.sh` → `demo ok` rc=0.

Attacks: ambiguous LINE:text pins, v2 recover FILE (move / drift / extract-and-keep / substring), chime vs `rg -n` LINE:text, first-locator seeds that match two arms or two files, empty stdin, binary, huge rg streams (`pins[:16]`), pins that are not LINE:text (`--column`, `--json`, ANSI, rustc, basename `-nH`).

Verdict: **mutate, do not kill.** The gold pipe still inverts chime's filter. `cd kizu && rg -n 'let b_side' src/git/parse.rs | peal --explain` is the same three spans as `chime parse.rs:60`, including `Some(bytes_to_path(a_side))` which rg never printed. Nothing in this battery turned that into `rg` of the `if` or into a cwd tree-walk. Do not kill because first-locator, `pins[:16]`, substring containment, or `rg -nH` basename.

---

## Primitive restated

Name a locus *from stdin locators* (`rg | peal`); emit other loci whose path-condition is the **same stack**, or a **superset**, **scanning the files those locators named**. Control-flow rhyme as a Unix filter. Object = ordered `(kind, pred)` stack. Address = locator. Not a snippet (`ambit`). Not a cwd walk (`chime FILE:LINE` then DIR).

Claimed invert of `chime`: default stdin is a *file scan*, not a line filter (`--hits` restores the ancestor). Claimed absorb of single-file rg: `(line, text)` pins against `git ls-files` recover the file if unique.

---

## 1. Gold pipe survived — scan ≠ filter (survived)

From `kizu/` (single-file rg omits the path):

```
$ rg -n 'let b_side' src/git/parse.rs
60:    let b_side = &bytes[b_prefix_start + 3..];

$ rg -n 'let b_side' src/git/parse.rs | peal --explain
seed    …/src/git/parse.rs:60
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];

deeper  parse.rs:61-62
  extra  if a_side!= b_side
  here   return None;

deeper  parse.rs:64
  extra  given a_side== b_side
  here   Some(bytes_to_path(a_side))
# rc=0
```

Byte-identical spans to `chime kizu/src/git/parse.rs:60 --explain`. Quoted-form `:25` is absent. Shallower `:54` is absent. `here` is the payload, not `}`. `--repo $KIZU` from the peal worktree recovers the same file. Wrong-cwd without `--repo` refuses (rc=2). `rg -nH` from the **repo root** is the same scan.

`chime parse.rs:60` with the `return None;` stream **filters** to `:62` only. peal without `--hits` **scans**. That is the verb.

---

## 2. First locator is the seed — `rg 'return None;'` chimed the quoted arm (conceptual, load-bearing)

CANDIDATE named this. Confirmed on the real file, and it is the default pipe for any pattern that hits more than one arm.

```
$ rg -n 'return None;' src/git/parse.rs
34:            return None;
44:        return None;
… 58, 62, 77, 104, 108

$ rg -n 'return None;' src/git/parse.rs | peal --explain
seed    parse.rs:33-34
  if     bytes.starts_with(b"\"a/")  (L25)
  if     !b_decoded.starts_with(b"b/")  (L33)
  here   return None;
# rc=0  — quoted-form miss, not the unquoted survivor
```

`--hits` on that stream keeps `:34` (same wrong arm). `--same-as parse.rs:60` restores the gold three spans. `--hits --same-as :60` is chime's filter (`:62` only).

Same lie on sitbone:

```
$ rg -n 'return PresenceReading' Sources/SitboneCore/PresenceArbiter.swift | peal --explain
seed    PresenceArbiter.swift:76-77
  guard-else isEnabled
  here   return PresenceReading(status: .unknown, confidence: 0)
```

First hit is the **disabled** arm. The success `return PresenceReading(status: status, …)` at `:101` is not in the scan. `rg -n 'guard isEnabled' | peal` is the same else-arm (the guard *line* is classified `guard-else`). `chime :80` is the body. The keyword you grepped is not the stack you get.

Fixture `rg -n return nested.py | peal` (from the peal worktree, unique pins) seeds `:6-7` `if user is None` / `return None`. `chime nested.py:8` on the same stream keeps denied/retry/fail/drained — the opposite polarity.

Two files, two stacks (`alpha.py` `user.locked` / `beta.py` `item.kind`). `rg -nH return | peal` emits only `alpha.py:3`. `beta.py` is scanned and dropped (`any_fn` off, fn names differ). First locator wins; the other stack is silent, not refused.

The pipe that *works* is a locator unique to the stack (`let b_side`, `Logger.sensorsPresence`). A bag of early returns is a different object. No densest-arm / refuse-ambiguity yet. CANDIDATE suggested this mutation. Still open.

---

## 3. Ambiguous FILE from LINE:text pins — refuse holds; substring uniqueness does not (conceptual, lethal to “unique pin”)

Twin `a.py` / `b.py` with identical `return "denied"` at line 13:

```
$ printf '%s\n' '13:    return "denied"' | peal --exact --tsv
peal: LINE:text locators need a FILE operand, rg -nH, or a unique match in this git tree
# rc=2
```

Identical Swift `guard isEnabled` in `A.swift` / `B.swift`: rc=2. FILE operand binds. Honest. CANDIDATE claimed this.

**Uniqueness is substring containment**, not identity of the rg line (`here not in lines[ln-1]`):

```
# real.py:3   return 1
# decoy.py:3  note = "return None is mentioned here"

$ printf '%s\n' '3:        return None' | peal --explain
seed    decoy.py:3-4
  if     x
  here   return 1
# rc=0
```

The pin text is a substring of a string literal in the *other* file. Recovery is unique, so peal does not refuse. Collapse then paints `return 1` as the arm. A later tree that mentions the old snippet in a comment or log line steals the file.

`60:` (empty `here`) is “any source with ≥60 lines” → ambiguous refuse in kizu. Conservative by accident of repo size.

---

## 4. v2 recover FILE — move works; drift and extract-and-keep refuse; that is not pin(1) (conceptual)

Identity is `(line, substring)` against the current `git ls-files`. Not a fingerprint.

| v2 | pin `11:    let p = (bytes.len() - 5) / 2;` | rc |
| --- | --- | --- |
| v1 `src/parse.rs` | recovers that path, scans the guard-body | 0 |
| **git mv** `src/parse.rs` → `src/git/parse.rs` | recovers the **new** path (same line numbers) | 0 |
| **+20 line drift** (same text now at 31) | refuse unique-match | 2 |
| **extract-and-keep** (stub + copy, both hold line 11) | refuse ambiguous | 2 |
| drift pin updated to `:31` | recovers | 0 |

A file split that keeps the old path is ambiguous, not a pointer at the extract (that is pin's object; peal will not grow it). A format / import that shifts lines by twenty is a dead locator even though the text is unique in the tree. `pins[:16]` (below) can also throw away the pin that would have disambiguated.

`--repo` is a search root for this name-tree, not a scan root. Passing kizu as a DIR operand still exits 2 without `--walk`. Confirmed.

---

## 5. `rg -nH` basename is the *broken* producer; LINE:text is the one that works (conceptual, load-bearing)

Error text: “need a FILE operand, **rg -nH**, or a unique match.” From the file's directory the advice is inverted.

```
$ cd kizu/src/git && rg -nH 'let b_side' parse.rs | peal --explain
peal: name a locus (FILE:LINE, --same-as, or rg -n locators with a path-condition)
# rc=2

$ cd kizu/src/git && rg -n 'let b_side' parse.rs | peal --explain
seed    …/src/git/parse.rs:60
  here   let b_side = …
# rc=0  — pin recovery against git toplevel
```

`parse.rs:60` on stdin names a file, so recovery is skipped. `SourceBag` joins relative paths to **git toplevel**, not cwd: `kizu/parse.rs` does not exist. argv `peal parse.rs:60` from `src/git` works (cwd-relative `query_file`). The advertised `-nH` locator is cwd-relative and the seed resolver is repo-relative.

Bakeoff already recorded this as empty `--hits` on ambit/amid. peal's *scan* dies the same way: never reaches the file that is sitting in cwd.

`FILE:LINE` only `parse.rs:60` from `kizu/` (root): same rc=2. `src/git/parse.rs:60` from root: rc=0.

---

## 6. Empty stdin — vacuous usage, not a walk (survived)

```
$ printf '' | peal
peal: name a locus … No cwd walk.
# rc=2

$ printf '\n' | peal     # rc=2
$ printf '   \n' | peal  # rc=2
$ printf 'hello\n' | peal
peal: stdin is not a diff or file:line stream (pass FILE:LINE, or rg -nH / rg -l)
# rc=2
```

Empty pipe plus argv `FILE:LINE` still scans that file (rc=0). `rg -l` without `--same-as` refuses “path-condition”. `--diff` without a seed refuses. DIR without `--walk` refuses. Preamble `mod.py:1` is rc=1 empty cond_key. Honest zeros.

---

## 7. Binary — skip is not the problem; stdin traceback is rc=1 (operational)

```
$ printf '\x00\xff' | peal --explain
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 1
# rc=1  traceback from PrefixedStream `for line in src`
```

`/dev/urandom` 64 bytes: same. Exit 1 is “no hits” on a crash. File input already `errors=replace`; stdin does not. NUL *inside* an otherwise LINE:text locator does not crash (`60: let b_side\x00hidden` → pin recovery miss, rc=2). A `blob.rs` with a trailing NUL, named as `FILE:LINE`, is “no path-condition” (the `let x = 1` line is not under an `if`) — not a decode death.

Same class as weft/zanei/plait binary stdin. A one-line `buffer` decode-or-die (exit 2) would hide the traceback and would not touch first-locator or `pins[:16]`. Not applied.

---

## 8. Huge rg streams — collect-then-scan lives; `pins[:16]` throws uniqueness away (conceptual)

`_run_stream` does `lines = list(prefixed.lines())`. Recovery then does `pins = pins[:16]`.

50k named `FILE:LINE` locators (1.7 MB, 80 files) from a tiny git: **0.86s, rc=0**. First locator is the seed (`f000.rs` `if true`). Other 79 files are scanned and dropped (fn names differ). `--any-fn` emits 80 rows. Did not OOM. The buffer is real; at this size it is not a kill.

20k bare LINE:text: recovery can succeed, then the first pin with a cond_key is the seed. The load-bearing hole is the cap:

Two files share 16 `(line, text)` pairs; line 19 is `let UNIQUE_REAL = 1` vs `let UNIQUE_DECOY = 2`.

```
$ printf '%s\n' '19:        let UNIQUE_REAL = 1;' | peal --explain
seed    real.rs:2-19
  if     true
  here   let UNIQUE_REAL = 1;
# rc=0  — unique pin works

$ # 16 shared pins, then UNIQUE_REAL as 17th
peal: LINE:text locators need a FILE operand, rg -nH, or a unique match
# rc=2  — pins[:16] never sees the disambiguator
```

A long `rg -n` stream from one file whose first sixteen hits also appear in a generated twin is a false refuse. A short unique pin is the thing that works. The default producer (`rg FILE`) can emit more than sixteen hits (`return None;` on parse.rs is nine; a broader pattern is not).

Pin recovery reads every git-listed source until a second match (`file_matches_pins` is a content read, not an AST). kizu has 80 listed sources; gold pipe 0.06s. Not a linux.git problem. It is still a name-tree walk of bytes, not “we never touch a file until uniqueness is known.” They never *parse* until unique. They *read* all of them.

---

## 9. Pins that are not LINE:text (conceptual)

| producer | parse | result |
| --- | --- | --- |
| `rg -n` `60:    let b_side…` | LINE:text | gold, if unique |
| `rg -n --column` `60:5:    let b_side…` | line=60, here=`5:    let b_side…` | **pin recovery miss rc=2** (`5:` is not in the source line) |
| `rg -nH --column` | GREP_RE takes col, rest is the line | gold (file named, no recovery) |
| `rg --json starts_with` | not a locator | rc=2 *stdin is not a diff or file:line stream* |
| `rg --color=always` ANSI | not a locator | rc=2 same |
| `rg -C` mix | dash-context dropped; colon match kept | gold if the match names a file or unique pins |
| vimgrep `file:line:col:text` | GREP_RE | gold from kizu root |
| rustc `--> src/git/parse.rs:60:9` | file=`--> src/git/parse.rs` | named file skips recovery; source unavailable; rc=2 |
| `example.com:8080:not-a-file` | may parse as file+line | rc=2 |
| `C:\Users\x\parse.rs:60:…` | **None** | rc=2 *not a file:line stream* |
| `foo:bar.py:3:…` (colon in name) | **None** | rc=2 |
| mixed `nope.py:1` + `60: let b_side` | any named file **skips** pin recovery | rc=2; the bare pin never gets a file |
| CRLF `13: return "denied"\r\n` | works in peal wt | rc=0 |

`--column` is a one-character cousin of the advertised pipe. Single-file rg plus `--column` is still LINE:text as far as the user is concerned and peal treats the column as payload. FILE operand / `-nH` sidesteps recovery and then works. The error still asks for `-nH`, which from a nested cwd is the other death (section 5).

No JSON parser. Amid's spare. Not grafted. Forbidden to clone ambit here.

---

## What survived

- Gold `rg -n 'let b_side' parse.rs | peal` == `chime parse.rs:60` == argv `peal parse.rs:60`, including `Some(bytes_to_path)`. Quoted form gone. `:54` is not a super of `:60`.
- `peal :54` lists `:60`/`:64` as deeper. Direction is still superset.
- `--hits --same-as :60` on the `return None;` bag == chime's filter (`:62`).
- Twin files, extract-and-keep, empty `here`, wrong git cwd: refuse rc=2, no guess.
- git-mv v2 recovers the new path when line numbers held.
- Empty / newline / prose stdin: rc=2, no traceback, no cwd walk.
- `--walk` still opt-in. `./peal` no args: rc=2 *No cwd walk*.
- nested.py exact denied; try ≠ except; swift guard body ≠ guard-else (argv seed).
- sitbone `PresenceArbiter.swift:80` body vs `:76` else — argv tells the truth; the *rg of the keyword* does not.
- 26/26 tests. `./demo.sh` 0. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass. Do not implement a third under-stream / ambit clone.**

The object is still “pipe grep locators, get the rest of that path-condition arm.” `let b_side` still expands to `Some(bytes_to_path)`. `--hits` is still the opt-in ancestor filter. Nothing here made default stdin a cwd walk or a `rg` of the `if`. Kill only if a later generation does that, or if pin recovery is removed and the advertised `rg FILE | peal` (no `-H`) dies with it.

| do not kill because | mutate toward |
| --- | --- |
| Gold `let b_side` pipe == chime `:60`; tests 26/26; demo 0; no cwd walk; `--hits` is still a filter | **Refuse a bag of cond_keys.** `rg 'return None;' \| peal` and `rg 'return' nested.py \| peal` must not silently seed the first arm. `--same-as` / `--first` already exist as the override. |
| Twin files refuse; extract-and-keep refuse | **Pin match is the stripped line, not `in`.** `return None` in a decoy string must not uniquely recover that file. |
| Unique short pin recovers `UNIQUE_REAL` | **Do not cap pins at 16**, or cap after uniqueness is known. The 17th pin is the one that distinguishes twins. |
| `-n` LINE:text from `src/git` recovers; argv `parse.rs:60` from `src/git` works | **Resolve named locators against cwd then repo.** `rg -nH` from the file's directory is the producer the error text recommends and the seed resolver cannot open. |
| `--column` + `-nH` / FILE operand works | **LINE:COL:text is not LINE:text.** Drop the column before pin match. |
| Empty stdin rc=2; prose rc=2 | Binary stdin: fail closed **exit 2** (`errors=replace` on stdin would fail *open*). |
| 50k named locators 0.86s | Stream unique files; do not hold 1.7 MB to seed from row 1. Optional. |
| v2 move recovers | Do not grow pin(1). Drift-refuse is honest for this object. |

A one-line stdin decode-or-die would hide the traceback and would not touch first-locator, substring uniqueness, `pins[:16]`, or basename `-nH`. Not applied.

Do not grow a review platform. The next mutation is *ambiguous-seed refuse* plus *cwd-honest locator paths*, not a prettier explain dump and not json+peel on this binary.

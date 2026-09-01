# DESTROYER — whence

Adversarial pass on **parent-tagged merge + provenance**. No rewrite of the victims. Dreamer transcripts were not read as evidence. Every number below is from `python3 ./whence` (zsh owns the builtin `whence`).

- **candidate-01** — `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-hdd/lineages/candidate-01__whence/whence` sha256 `bce6aa1da7dbdfcd…`
- **reimpl-02** — `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-hdd/lineages/reimpl-02__whence/whence` sha256 `69a2598e61bc2c98…`
- **mutation-03 stdin** — `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-hdd/lineages/mutation-03__whence-stdin/whence` sha256 `c084f4c247c695e5…`
- Transcript: `/tmp/destroy-whence/transcript.txt` (6701 lines)
- Driver: `/tmp/destroy-whence/attack.py`
- Live git conflict: `/tmp/destroy-whence/gitrepo2` (`merge.conflictStyle=merge`)

Attacks: malformed markers, nested conflicts, huge hunks, missing newline, binary-ish, stdin empty, FILE is directory, pipes, `git merge` real conflict, pathological names. Honesty check: `git merge-file` / `git checkout --ours` / index stages `:1:` `:2:` `:3:`.

Verdict: **mutate the primitive, do not kill.** Parent-tagged hybrid on a real two-branch conflict is still a delta vs mergetool. `--ours`/`--theirs` is not. Empty hybrid is a hunk-wiper. Provenance is tag-intent, not unique origin.

---

## Primitive restated (what ran)

Parse `<<<<<<<` / `=======` / `>>>>>>>`. Replace each region only by `--ours`, `--theirs`, per-region `--choice`, or tagged `[ours:…]` / `[theirs:…]` hybrid. Untagged mixed text is refused (exit 1, markers left). Write the blob and a JSON list of kept contested spans.

Nearest Unix: `git mergetool`, `git merge-file --ours|--theirs|--union`, `git checkout --ours/--theirs`. During a conflict git already holds both parents as index stages.

Claimed delta: mergetool produces a blob and forgets which parent supplied each contested span. whence keeps that parentage.

---

## Honesty: parent-tagged merge vs mergetool — MUTATE (load-bearing, not KILL)

Live repo `/tmp/destroy-whence/gitrepo2`. Diverging edits of `app.cfg` (`color = red`/`size = 1` vs `color = blue`/`size = 2`). `git merge --no-commit feature` exit 1, worktree:

```text
<<<<<<< HEAD
color = red
size = 1
=======
color = blue
size = 2
>>>>>>> feature
```

Index still names both parents (whence does not):

```text
$ git ls-files -u
100644 … 1	app.cfg
100644 … 2	app.cfg
100644 … 3	app.cfg
$ git show :1:app.cfg    # color = black\nsize = 0\n
$ git show :2:app.cfg    # color = red\nsize = 1\n
$ git show :3:app.cfg    # color = blue\nsize = 2\n
```

Same three blobs into `git merge-file -p`, then all three `whence` copies:

| command | blob | .prov |
| --- | --- | --- |
| `git merge-file --ours` | `color = red\nsize = 1\n` | none |
| `git merge-file --theirs` | `color = blue\nsize = 2\n` | none |
| `git merge-file --union` | both sides concatenated | none |
| `git checkout --ours -- app.cfg` | `color = red\nsize = 1\n` | none (`gitrepo3` glob `*.prov` = `[]`) |
| `python3 whence resolve --ours` | **byte-identical** to merge-file `--ours` (cand/reimpl/mut) | JSON `mode: ours`, one span |
| `python3 whence resolve --theirs` | **byte-identical** to merge-file `--theirs` | JSON `mode: theirs` |
| `python3 whence resolve --hybrid` with `[ours:color = red]\nsize = [theirs:2]\n` | `color = red\nsize = 2\n` | spans ours `"color = red"`, theirs `"2"` |

The hybrid blob equals **neither** parent, **not** `--ours`, **not** `--theirs`, **not** `--union`. Untagged mix `color = red\nsize = 2\n` still exit 1, markers left, no `.prov` (all three). That is the object mergetool will not give you: a hybrid that is illegal unless every non-common span is tagged, plus a machine-readable parent list.

It is **not** a discoverer of parentage. The user typed the tags. Unique tokens in that hybrid reconstruct from git stages without whence:

```text
token 'color = red'  unique=ours     # in :2 only
token 'size = 2'     unique=theirs   # in :3 only
```

After `git add` those stages vanish; `.prov` is persistence of a mapping you already declared. `--ours`/`--theirs` add nothing `git merge-file` does not already write except a JSON echo.

**MUTATE** the primitive: keep refuse-unmarked-mix and the hybrid parent list; stop advertising `--ours` as the delta; record whether a tagged span was unique to that parent or also in the other. **Not KILL** — mergetool still emits no parent list and will happily invent text whence refuses.

---

## 1. Empty `--hybrid` stdin / empty sidecar wipes the hunk — FIX (cand, reimpl); mutation-03 stdin only

Forgotten pipe on candidate-01 and reimpl-02:

```text
$ python3 whence resolve FILE --hybrid - </dev/null
exit=0
mode: empty
resolved: '# palette\n# end\n'     # markers gone
```

Same wipe for `--hybrid` of a 0-byte **file** sidecar on **all three**, including mutation-03:

```text
cand/reimpl/mut --hybrid empty-file
exit=0  mode: empty  resolved=b'# palette\n# end\n'
```

`FILE=- --hybrid=-` on cand/reimpl consumes stdin as the conflict, treats leftover stdin as an empty hybrid, writes `# palette\n# end\n`. mutation-03:

```text
cannot read both FILE and --hybrid from stdin; …
exit=3
```

mutation-03 empty stdin:

```text
--hybrid - got empty stdin; pipe tagged blocks …
exit=3
file mutated=False markers_remain=True
```

Parent hole mutation-03 already named. File sidecar still deletes the region and writes `.prov` with `"mode": "empty"`. That is not a tagged merge. **FIX**: refuse empty hybrid from any source the way mutation-03 refuses empty stdin. Do not invent `mode: empty` as success.

---

## 2. `report` of empty / no-conflict is success — FIX (all three)

Assay already flagged this. Confirmed:

```text
$ python3 whence report emptyfile
exit=0
file: …/empty
conflicts: 0
note: file has no trailing newline
```

Same for empty stdin `FILE=-`, a file with no markers, a file whose only bytes are `hello` and no NL. `resolve --ours` on those is exit 2 `no conflict markers in …`, file untouched, no `.prov`. Report and resolve disagree about whether “nothing here” is ok. Combined with §1, `report -` on a forgotten pipe looks like a clean 0-conflict file.

**FIX**: `report` of zero conflicts should be the same class as resolve (exit 2), or say `conflicts: 0` on stderr and exit 2. Empty-success is how hunks disappear next to `--hybrid -`.

---

## 3. `--prov DIRECTORY` writes the blob, then errors — FIX (all three)

Fresh conflict, `--ours --prov /tmp/destroy-whence/extra/provdir`:

```text
cand/reimpl/mut exit=2
i/o error: [Errno 21] Is a directory: '….whence-….tmp' -> '…/provdir'
dest markers left=False dest=b'color = red\nsize = 1\n'
```

Conflict already replaced. Exit 2 with the worktree resolved and no provenance. `--output DIRECTORY` fails *before* touching FILE (`src_markers=True`) — that half is honest. **FIX**: write resolved + `.prov` as one transaction, or refuse a directory dest without mutating FILE.

`FILE` a directory / missing / symlink-loop: exit 2 `Is a directory` / `No such file` / `Too many levels of symbolic links`. Honest. FIFO report works (writer child, ~0.22s). Symlink-to-conflict follows and resolves.

Read-only FILE (0444, writable dir): `os.replace` succeeds, exit 0. Unix-correct, not a bug.

---

## 4. `FILE=-` without `--output` creates a file named `-` — FIX (all three)

```text
$ python3 whence resolve - --ours --prov -    # cwd = …/cand-dashdir
exit=0
created file named '-': True
content: '# palette\ncolor = red\nsize = 1\n# end\n'
```

mutation-03 CANDIDATE already lists this. **FIX**: require `--output` when FILE is `-`.

---

## 5. BOM on the conflict file hides `<<<<<<<` — FIX (all three)

UTF-8 BOM prefixed to a well-formed region:

```text
$ python3 whence report bom.conflict
exit=2
…:3: stray ======= with no opening <<<<<<<
```

`\ufeff<<<<<<< HEAD` is not a marker. mutation-03 strips BOM on **hybrid stdin/sidecar** only; a Notepad-saved conflict file still fails on all three. **FIX**: strip a leading UTF-8 BOM on FILE the same way.

---

## 6. CRLF / BOM hybrid pipes — FIX (cand, reimpl); mutation-03 already

Same sidecar bytes with CRLF or `\xef\xbb\xbf`:

| pipe | cand | reimpl | mut |
| --- | --- | --- | --- |
| LF tags | exit 0, `color = red\nsize = 2\n` | same | same + `"hybrid":{"source":"stdin"}` |
| CRLF tags | exit 1, untagged `"\r\nsize = "` | exit 1 | exit 0, matches LF |
| BOM tags | exit 1, untagged `"﻿"` | exit 1, `"\ufeff"` | exit 0, matches LF |
| `printf` no final NL | exit 0, `size = 2# end\n` | same | same (honest: sidecar NL was common text) |

**FIX** cand/reimpl: treat `--hybrid -` as mutation-03 does (CRLF→LF, strip BOM, refuse empty). Do not invent the missing final NL.

---

## 7. Malformed / nested markers — hold (not a finding)

All three, markers left on refuse unless noted:

| input | exit | note |
| --- | --- | --- |
| `<<<<<<<` without `=======` | 2 | `>>>>>>>` before `=======` |
| unclosed after `=======` | 2 | |
| stray `=======` / `>>>>>>>` | 2 | |
| diff3 `\|\|\|\|\|\|\|` | 2 | two parents only |
| `<<<<<< HEAD` (six) | 2 | not a marker; stray mid |
| `========` (eight) | 2 | not a mid; close seen first |
| `<<<<<<<HEAD` / tab label | 2 | git writes a space |
| extra `=======` | 2 | third hunk refused |
| nested `<<<<<<<` in ours or theirs | 2 | `nested <<<<<<< inside region…` |
| NUL / latin1 / utf-16 / PNG | 2 | binaries refused (reimpl names utf-16 as NUL first) |
| CR-only / CRLF conflict FILE | 0 | markers parsed; CR kept in span text |
| `<<<<<<<` / `>>>>>>>` with no label | 0 | labels default `ours`/`theirs` |

A line that *is* exactly `=======` inside ours **is** the mid (git-identical): empty ours, `--ours` writes `b''`. A line `value ======= 1` is content. Nested conflict in a parent body is refused; mergetool would also choke.

---

## 8. Huge hunks / skip-middle subsequence — MUTATE (primitive)

2.16 MB region, 20k+20k lines, report ~0.04s, `--ours` ~0.04s, no hang. Hybrid tagging first and last ours lines:

```text
resolved: OURS-000000 …\nOURS-019999 …\n
spans: two ours, 19998 lines dropped
```

Smaller: ours `alpha/bravo/charlie`, tags `[ours:alpha]\n[ours:charlie]\n` → `alpha\ncharlie\n` (bravo discarded, ordered substring). Reverse order `charlie` then `alpha` exit 1 (cannot go backwards). Empty tags `[ours:][theirs:]` exit 0, spans with `"text": ""`, resolved `# palette\n\n# end\n`.

This is not a merge. It is an ordered subsequence extractor with parent labels. **MUTATE**: either require tagged+untagged text to cover each parent (no silent drop) or name the operation “tagged extract”, not resolve.

---

## 9. Provenance lies on common / split / repeated text — MUTATE (primitive)

All three, exit 0:

- Both sides `hello world`. Sidecar `[ours:hello world]` → provenance `parent: ours`. The span is uncontested.
- `[ours:color = ][theirs:blue]` on `color = red` vs `color = blue` → blob `color = blue\n`, spans claim **ours** supplied `"color = "` (also in theirs) and **theirs** supplied `"blue"`.
- Repeated `xx` in both: `[ours:xx] [theirs:xx]` → `xx xx\n`. Parentage is the user’s click order.

Untagged exact-ours still refused (exit 1). Wrong-parent `[ours:color = blue]` still points at theirs. The refuse-unmarked-mix contract holds. The JSON does not mean “this byte is unique to that parent.” **MUTATE**: mark spans `unique` / `also-in-other` / `empty`, or refuse tagging text that is in both.

---

## 10. JSON `]` closer — MUTATE (implementation split; reimpl is the peel)

`json-array.conflict` tagged `[ours:{"items": ["a", "b"], "n": 1}]` without `\]`:

- candidate-01 / mutation-03: first `]` closes the tag, leftover `, "n": 1]\n` unmarked mix, exit 1, markers left.
- reimpl-02: longest unescaped `]` whose inner text is still a substring of ours → `{"items": ["a", "b"], "n": 1}\n`, exit 0.

reimpl’s dogfood. Parent/mutation still require `\]`. **MUTATE** the lineage toward the longest-closer (or require `\]` everywhere and say so in the error). Do not leave two dialects.

---

## 11. Pathological names / missing NL / messy hybrid — notes, one FIX

- Spaces, leading dash, unicode `ファイル`, 180-char, quotes: report+resolve work.
- Filename containing a newline: report exit 0, but the path is two lines (`file: …/file` then `newline.conflict`). **FIX** the report format (JSON-encode the path).
- Conflict close as last line, no EOF NL: `--ours` keeps ours body including its NL; provenance `input_trailing_newline: false`.
- `fixtures/messy.conflict` hybrid: all three keep `# eof` without a final NL (`…true\n# eof`). Honest.
- `printf` hybrid without final NL concatenates `2# end`. Honest (sidecar NL was common).
- zsh `whence resolve` is the builtin, not this tool (`whence is a shell builtin`). Already documented.

---

## 12. `--choice union` / no mode — hold

No args / resolve without `--ours|--theirs|--choice|--hybrid`: exit 3, usage. `--ours --theirs`: exit 3. `--choice union,union`: exit 3 `expected ours, theirs, or hybrid`. `--choice ours` on two regions: exit 3, lists both regions. `--choice ours,theirs` on `two.conflict` → `alpha\none\nbeta\nTWO\ngamma\n`. Fine.

---

## Per-embodiment

| | candidate-01 | reimpl-02 | mutation-03 |
| --- | --- | --- | --- |
| `--ours` == merge-file `--ours` | yes | yes | yes |
| hybrid ≠ merge-file union | yes | yes | yes |
| untagged mix refuse | yes | yes | yes |
| empty `--hybrid -` wipes | **yes** | **yes** | no (exit 3) |
| empty file sidecar wipes | **yes** | **yes** | **yes** |
| `FILE=- --hybrid=-` wipes | **yes** | **yes** | no (exit 3) |
| CRLF/BOM hybrid stdin | fail | fail | ok |
| JSON unescaped `]` | fail | ok | fail |
| `--prov` dir mutates FILE | **yes** | **yes** | **yes** |
| writes file named `-` | **yes** | **yes** | **yes** |
| BOM on FILE | miss marker | miss marker | miss marker |

mutation-03 is the right stdin peel. It does not close empty-file-sidecar, FILE `-`, conflict BOM, or `--prov` dir. reimpl is the right `]` peel. Neither is a mergetool replacement for `--ours`.

---

## Kill / keep the primitive

**MUTATE, do not kill.**

KILL would require that after these attacks parent-tagged merge is not a real delta vs mergetool. It still is, once you look at hybrid and at refuse-unmarked-mix:

- mergetool / `merge-file` / `checkout --ours` produce a blob and stop.
- whence hybrid on a live `git merge` conflict produced `color = red\nsize = 2\n` with named spans, and refused the same mix untagged.

What died is the story that `--ours` is the object, and the story that `.prov` states unique origin. Breeding direction:

1. **FIX** empty hybrid (any source) so a forgotten pipe cannot delete a hunk.
2. **FIX** resolve+prov as one write; refuse directory dest before mutating FILE.
3. **MUTATE** provenance to unique-vs-shared, or refuse tagging common text.
4. **MUTATE** skip-middle: cover or explicitly drop.
5. Do not grow a mergetool TUI, a third parent, or a JS/YAML parser.

zsh still owns `whence`. Run `python3 whence`.

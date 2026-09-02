# DESTROYER hunkland

Date: 2026-09-02

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-hunkland/hunkland`

Worktree (byte-identical, sha256 `d7cdac3617dc2f55f25884b9a8dd29e10fbf98f8f6b155c016e26bde0f432b7f`): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-hunkland-hunkland/hunkland/hunkland`

Origin claim: compare where a patch insert landed with the line the hunk header named. Apply exit 0 can still be `match no` / `verdict mis-indexed`.

Happy path is real. Unit tests (14/14) pass. Specimen-020 `@@ -2,0 +3 @@` + `+inserted` on `first\nsecond\nthird\n` through owned `apply_hunk` (`idx = old_start - 1`) yields `first\ninserted\nsecond\nthird\n`, `apply_exit 0`, `header 3` (`second`) vs `land 2` (`inserted`). That is not enough. The implementation is `re.search` for `+N` plus the first `difflib.SequenceMatcher` insert/replace opcode, and `apply_exit` is a caller sticker.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-hunkland/hunkland
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-hunkland/fixtures
S020=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-020/files/patch_insert.py
```

`cmp "$FIX/patch_insert.py" "$S020"` is IDENTICAL. Host: git 2.54.0, `patch` 2.0-12u11-Apple. No merge with other patch/diff tools. This object is the empty-range land-vs-header join, not `git apply`.

---

## What still works

The owned empty-range fixture, and any other pair of files whose *only* change is inserting a unique line, when `--hunk` is the empty-old-range form (`old_count=0`) whose `+N` is that new line.

```bash
python3 "$CLI" "$FIX/020-orig.txt" "$FIX/020-result.txt" --hunk '@@ -2,0 +3 @@' --apply-exit 0
python3 "$CLI" "$FIX/020-orig.txt" --applier "$FIX/patch_insert.py" --hunk '@@ -2,0 +3 @@' --insert inserted
```

```text
header	3
header_line	second
land	2
land_line	inserted
apply_exit	0
match	no
verdict	mis-indexed
rc=0
```

Aligned result `first\nsecond\ninserted\nthird\n` is `land 3`, `match yes`, `verdict aligned`. Unseen `--applier @@ -3,0 +4 @@` + `mid` names `header 4` vs `land 3`. `@@ -0,0 +1 @@` on the three-line fixture hits Python `list.insert(-1)` and lands at 3 against header 1. Missing path / directory / bad hunk / RESULT-plus-`--applier` are clean `hunkland:` errors (rc 1 or 2). Unicode lines, spaces in filenames, symlinks, FIFOs, and `/dev/stdin` as ORIG work.

That is the whole useful delta. Attacks below break the land-vs-header claim around it, or show the primitive cannot see a normal unified diff.

---

## Implementation

### 1. `header` is hunk new-start, not the insert line

`diff -u` never emits the harvest header. The aligned insert `first\nsecond\ninserted\nthird\n` is:

```text
@@ -1,3 +1,4 @@
 first
 second
+inserted
 third
```

`git apply` of that context hunk exits 0 and writes the aligned bytes. hunkland given the header `diff` actually wrote:

```bash
python3 "$CLI" orig.txt result.txt --hunk '@@ -1,3 +1,4 @@'
```

```text
header	1
header_line	first
land	3
land_line	inserted
match	no
verdict	mis-indexed
rc=0
```

`+1` is the start of the hunk in the new file, not the `+inserted` line. `old_count` is parsed and then discarded (`_new_count` too). CANDIDATE.md already listed "Refuse `verdict aligned` when `old_count` is not 0". Unimplemented. Context hunks still get a confident `mis-indexed` rather than a refuse. The harvest form `@@ -2,0 +3 @@` is the one shape where `+N` happens to be the insert coordinate.

A whole patch file as `--hunk` is `HUNK_RE.search`: first `@@` wins. Two headers, context then empty-range, reports `header 1`.

### 2. `land` is the first SequenceMatcher insert/replace, not this hunk's `+` line

`find_lands` walks `difflib.SequenceMatcher(..., autojunk=False)` and keeps every `insert`/`replace` new-file index. `land` is `lands[0]`. Other edits, duplicates, and replacements all count.

Noise before a *correct* insert after `second` (`NOISE\nfirst\nsecond\ninserted\nthird\n`, hunk `@@ -2,0 +3 @@`):

```text
header	3
header_line	second
land	1
land_line	NOISE
verdict	mis-indexed
```

The hunk insert occupies line 4. The tool names the unrelated first opcode.

Duplicate identities. orig already contains `inserted`; result adds a second copy at line 3 (the `+3` the header named):

```text
orig    first / inserted / second / third
result  first / inserted / inserted / second / third
header	3
land	2
verdict	mis-indexed
```

Opcodes: `insert` at result line 2, then equal the rest. Human land of the *new* copy is 3. False mis-index of an aligned duplicate insert.

Identical `a` lines, insert `x` at line 2, hunk `@@ -2,0 +3 @@`:

```text
opcodes: insert result[0:2]=['a\n','x\n']  then equal two a's, delete last a
header	3
land	1
land_line	a
verdict	mis-indexed
```

`x` is at line 2. `land` is 1 and the line is `a`. SequenceMatcher is not a hunk applier.

Reorder `first`/`second` with hunk `@@ -1,0 +1 @@` (no insert happened):

```text
land	1
land_line	second
match	yes
verdict	aligned
```

Replacement of `second` with `inserted` (same line count, not an empty-range insert) plus the harvest hunk is `land 2` / `verdict mis-indexed` — the specimen diagnosis on a different edit. The same replacement under `@@ -2,1 +2,1 @@` is `aligned`. Trailing-newline-only (`third` → `third\n`) is a `replace` of line 3, so `verdict mis-indexed` against `@@ -3,0 +4 @@`. Deletion-only is `land none` / `no-insert` even when `--hunk` is a delete (`@@ -2,1 +2,0 @@`). Documented. Still a silent drop of the only change.

`--insert` with a RESULT file is ignored. The report still names whatever SequenceMatcher saw.

### 3. `match` is `land == header`. The hunk body is never parsed

Insert at line 3 whose text is `NOT-THE-INSERT`, hunk `@@ -2,0 +3 @@` (body would have been `+inserted`):

```text
header	3
header_line	NOT-THE-INSERT
land	3
land_line	NOT-THE-INSERT
match	yes
verdict	aligned
rc=0
```

When `match` is yes, `header_line` and `land_line` are the same `line_at` call. They cannot disagree. `aligned` does not mean "the insert occupies the named line". It means two integers were equal.

### 4. `apply_exit` is a sticker. `apply-failed` hides a real mis-index

`--apply-exit` is an int flag, default 0. It is not the applier's status and not `git apply`'s status unless the caller copies it in.

Specimen result, `--apply-exit 1`:

```text
land	2
land_line	inserted
apply_exit	1
match	no
verdict	apply-failed
rc=0
```

The insert landed one line early. The harvest verdict is gone. `--applier` that *succeeds* plus `--apply-exit 1` is the same hide. `--apply-exit -1` is `apply-failed` too.

`verdict_for` checks `land is None` first. Identical files plus `--apply-exit 1`:

```text
land	none
apply_exit	1
verdict	no-insert
```

`apply-failed` never fires when the apply failed *and* produced no insert. `--applier` that returns `text` unchanged is `no-insert` with default `apply_exit 0`.

### 5. `read_text` universal newlines erase CRLF

orig LF, result CRLF, identical line text. Disk bytes differ. hunkland:

```text
land	none
verdict	no-insert
```

`Path.read_text()` uses universal newlines. SequenceMatcher never sees `\r\n`. A real insert written as CRLF against an LF orig still reports the harvest mis-index (both sides normalized), so the join can look right while the newline axis is gone.

### 6. TSV, `none`, dumps, misleading exit zero

`line_at` missing → `"none"`. A landed line whose text is `none` is the same token (`land_line	none` with `verdict mis-indexed`). Empty inserted line is `land_line` plus nothing (empty field). Tab inside the landed line:

```text
result line 2 = ins<TAB>ert
land_line	ins	ert
```

`cut -f2` is `ins`. 200_000-char landed line: rc=0, ~200_088 bytes of stdout, no cap. `inspect()` computes `old_start` / `old_count` and `format_report` drops them. All four verdicts are rc=0, including `mis-indexed`. CANDIDATE.md listed `--check` exit 1; still absent. Fine as a printer; hostile as a pipe predicate. `diff -u` on the same pair is rc=1.

### 7. `--applier` is in-process exec with no bound

`SourceFileLoader("hunkland_applier")` then `apply_hunk(orig, old_start, old_count, insert)` in this process. `main` catches `OSError`/`TypeError` (rc=1) and `ValueError` (rc=2). Everything else is the CLI.

| applier | rc | note |
| --- | --- | --- |
| returns `None` / `list` | 1 | uncaught `AttributeError: ... no attribute 'splitlines'`, traceback through `hunkland:34` |
| returns `bytes` | 1 | `TypeError: a bytes-like object is required, not 'str'` (`rstrip("\n")` on a bytes line) |
| `raise RuntimeError` | 1 | traceback, no `hunkland:` prefix |
| `sys.exit(7)` | 7 | stdout 0 bytes, stderr 0 bytes — indistinguishable from the tool succeeding at 7 |
| `raise GeneratorExit` | 1 | traceback |
| `raise KeyboardInterrupt` | -2 | traceback |
| syntax error | 1 | `SyntaxError` traceback from `exec_module` |
| `apply_hunk = 3` / missing | 2 | clean `no apply_hunk()` |
| `while True` | hang | no timeout (killed at 2s from outside) |
| writes `/tmp/hunkland-applier-side.txt` | 0 | side file left on disk; report still `mis-indexed` |

A correct applier (`lines.insert(old_start, insert)` so the new line occupies `+3`) is `aligned`. That path works. The loader still runs attacker code.

### 8. Honesty: `patch(1)` vs `git apply` vs `--unidiff-zero`

Same orig, same harvest hunk, no context lines:

```text
--- a/file.txt
+++ b/file.txt
@@ -2,0 +3 @@
+inserted
```

| applier | result | apply rc | hunkland (`--apply-exit` copied) |
| --- | --- | --- | --- |
| owned `apply_hunk` | `first\ninserted\nsecond\nthird\n` | 0 | `land 2` `mis-indexed` |
| Apple `patch -u` | `first\nsecond\ninserted\nthird\n` ("Empty context always matches. Hunk #1 succeeded at 3.") | 0 | `land 3` `aligned` |
| `git apply --unidiff-zero` | same as patch | 0 | `land 3` `aligned` |
| `git apply` default | `first\nsecond\nthird\ninserted\n` ("succeeded at 4 (offset 1 line)") | 0 | `land 4` `mis-indexed` |

Default `git apply` exits 0 and does not occupy `+3`. hunkland names that. The verdict is still `mis-indexed`, the same token as `idx = old_start - 1`. Git fuzzed an unanchored hunk to EOF; it did not use the specimen index. One word for two mechanisms.

CANDIDATE.md: does not rebuild git apply. Agreed. It still prints a mechanism-named verdict on git's result.

### 9. Empty / weird inputs (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| no args | 2 | argparse usage |
| missing path | 1 | `No such file` |
| ORIG directory | 1 | `Is a directory` |
| `-` as ORIG | 1 | not stdin |
| `/dev/null` `/dev/null` | 0 | `no-insert` |
| `/dev/stdin` as ORIG | 0 | works |
| broken symlink | 1 | `No such file` |
| mode 0 ORIG | 1 | `Permission denied` |
| latin-1 bytes | 2 | `UnicodeDecodeError` via `ValueError` |
| UTF-8 BOM | 0 | BOM stays on line 1; insert still named |
| NUL in a line | 0 | NUL in `header_line` |
| context-diff `*** -2,0 +3 ***` | 2 | `no unified-diff hunk header` |
| `--apply-exit nope` | 2 | argparse |
| `--insert` with RESULT | 0 | ignored |

These do not save the header/land holes.

---

## Primitive

Reality-stripped operation: regex-search the first `@@ -old,oldcount +new,newcount @@`, take `new` as `header`, `SequenceMatcher` orig vs result, print the first insert/replace new-file index as `land`, `match = land == header`, stamp caller `apply_exit`, pick a verdict.

Nearest ordinary workflow: `diff -u orig result` already shows where a unique line appeared (`+inserted` after `first` on the specimen result, after `second` on the aligned result). `cat -n` of the result plus reading `+N` is the hand join. `patch -u --verbose` prints `Hunk #1 succeeded at 3`. Observable capability lost if hunkland vanishes: the **named join** (`header` vs `land` vs `apply_exit` vs `verdict mis-indexed`) as one TSV on an empty-range insert. That join is real on specimen-020 and on any other unique-line empty-range miss. It is not a patch applier, not a git fuzz tracer, not a context-hunk reader (research boundary, honored in prose, violated in output: context hunks still say `mis-indexed`).

That is why this is not KILL: the *question* (apply exited 0, the empty-range header named new-file line N, the insert occupies M) is a debugging object `echo $?` will not emit. The current embodiment is a specimen-020 replay that pretends `+N` is always the insert line and that the first SequenceMatcher opcode is that insert.

The ceiling is already written down, and it is too small for the claim:

- `header` = hunk new-start; `diff -u`'s real header for this change is `@@ -1,3 +1,4 @@` and is labeled `mis-indexed`
- `land` = first insert/replace opcode, including noise, duplicates, replacements, newline-only, reorders
- `aligned` / `mis-indexed` do not look at the `+` body
- `apply_exit` is not observed; `apply-failed` overrides `mis-indexed`
- `mis-indexed` names an index bug git default does not have
- `--applier` executes the module in-process
- unseen fixture is the same `apply_hunk` at `N+1`, not patch/git/context
- `--check` and the `old_start-1` column are still suggested mutations, not behavior

Do not grow a git-apply reimplementation to escape this. Do not merge this join into a general patch auditor. Keep the empty-range land-vs-header row.

---

## Mutation (what must change)

Keep the object: for an empty-range hunk, success that does not occupy `+N` is not a clean apply, and the land line is named.

Do not keep a whole-file SequenceMatcher that only replays specimen-020's unique `inserted`.

1. **`header` is the line the `+` body occupies, or refuse.** `old_count != 0` is `hunk-not-empty` / `unsupported` (rc≠0), never `aligned` and never `mis-indexed`. A context `@@ -1,3 +1,4 @@` must not claim the insert missed line 1. If `--hunk` contains more than one `@@`, that is an error unless the caller picks one.

2. **`land` is this hunk's insert, not opcode 0.** Locate the inserted text from the hunk body or from `--insert`. Ambiguous duplicates print `land	ambiguous` (with the candidate lines), not a false `mis-indexed`. Extra edits beside the hunk are a separate row (`other-edits`) or a refuse, not a stolen `land`. Reorder / replace / newline-only are not empty-range inserts.

3. **`aligned` requires content.** `land == header` *and* `land_line` equals the inserted text. `NOT-THE-INSERT` at line 3 is not `aligned`. `match` that cannot disagree with `header_line == land_line` is not a column.

4. **`apply_exit` is observed or omitted.** If `--applier` returned a string, `apply_exit` is 0 unless it raised. A caller sticker must not override `mis-indexed`. `apply-failed` is only for an actual failed apply; `no-insert` plus a nonzero apply status must not drop the failure. Default-git-fuzz (land at EOF, apply rc=0) is not the same verdict as `idx = old_start - 1`. Name the offset or print `land ≠ header` without stealing `mis-indexed`.

5. **`--applier` is a subprocess with a timeout.** Catch `BaseException`. Non-`str` return, `SystemExit`, syntax error: `hunkland:` one line, rc≠0, no traceback. Side effects are the caller's problem only after isolation. Print `old_start` and the naive `old_start-1` next to `header` (already a listed mutation).

6. **rc=1 on `mis-indexed`.** rc=0 only for observed `aligned` (or a clean `no-insert` if that remains a printer). Cap `land_line` / `header_line`. Escape tabs/newlines. `none` is not a line value.

7. **Read bytes or `newline=None`.** CRLF vs LF is a change, not `no-insert`.

8. **Dogfood that is not `apply_hunk` at another N.** Next unseen is `git apply` vs `git apply --unidiff-zero` vs `patch -u` vs a `diff -u` context hunk of the same bytes. The tool must either name the land or refuse with a non-`mis-indexed` row.

If the mutation cannot do (1)+(2)+(3), the object is still `diff -u` plus a hand join with extra print, and a later destroyer should KILL.

---

MUTATE

# DESTROYER — rest (owes-strict, capdiff, same, hits)

Empirical attacks on implementation **and** primitive. Clock 05:03–05:14 JST, 2026-09-02.

Live CLIs (then archived):

| lineage | worktree | HEAD after |
| --- | --- | --- |
| mutation-02__owes-strict | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-02-owes-strict` | `eb51bab` |
| candidate-04__capdiff | `…/candidate-04-capdiff` | `00fecf8` |
| mutation-04__capdiff-json | `…/mutation-04-capdiff-json` | `a5565f2` |
| candidate-06__same | `…/candidate-06-same` | `abb5923` |
| candidate-07__hits | `…/candidate-07-hits` | `b2483a2` |

Full transcript: `/tmp/destroy-rest/transcript.txt` (script `/tmp/destroy-rest/attack.py`). Dreamer text is not evidence.

Attacks run: empty dirs, malformed diffs, missing captures, 5500-file trees, hardlinks, FIFOs, pipes/process substitution, `/dev/zero`, symlink loops, nested EACCES, absolute companion paths, `NAME=.` / `NAME=..`.

Each serious finding: **FIX** / **MUTATE** / **KILL**.

---

## Verdicts

| target | implementation | primitive |
| --- | --- | --- |
| owes-strict | **FIX** (`---` hunk collision; host `/etc/passwd` as companion) | **MUTATE** (still `git diff` + `rg`; bind companions to the change) |
| capdiff parent | **FIX** (`.`/`..` traceback; corrupt JSON traceback; truncated exit 0) | **MUTATE** (named store is a directory `diff -ru` already reads) |
| capdiff-json | **FIX** (same holes; truncated JSON claimed identity) | **MUTATE** (`--json` is encoding, not a new object) |
| same | **FIX** (`--bytes` hangs on `/dev/zero` and FIFOs) | **KILL** (no delta vs `stat` / `cmp` / `jq -S`) |
| hits (parked) | **FIX** (nested EACCES printed `0 matches` exit 0) | **KILL** (grep with inverted empty; the I/O distinction was a lie) |

Do not breed `same` or `hits` as Gen-3 vehicles. Keep owes-strict and capdiff only if the next mutation changes the compared object, not the flag soup.

---

## mutation-02__owes-strict

### Primitive restated

Parse a unified diff (or before/after snapshot). Report (1) identifiers on minus lines still mentioned in the remaining tree, (2) remaining `*.md` phrases `MUST exist: PATH` / `required file: PATH` whose PATH is absent.

Nearest: `git diff` plus `rg`. The mutation's claimed delta versus parent: companions are a closed phrase set, not `must \`backtick\``.

### Attacks (real CLI)

Baselines still hold: `fixtures/deleted-fn` exit 2 `validate_input`; `prose-backticks` exit 0; missing dir exit 1; empty dir without `tree/`+`change.diff` exit 1; empty tree+empty diff exit 0; 800-dir tree 0.100s exit 2; symlink loop 0.030s no hang; hardlinks report both names; stdin ignored (`cat change.diff \| owes` is usage).

**Malformed `---` collision.** Deleted line `--def validate_input(value):` is encoded in unified diff as `---def validate_input(value):`. The parser skipped every `startswith("---")` as a file header.

Before (`/tmp/destroy-rest/owes-dashdef`):

```text
$ python3 owes /tmp/destroy-rest/owes-dashdef
no unkept obligations
exit=0
```

README still said `` Call `validate_input` please ``. The obligation was real; the scanner dropped the minus line. Garbage-without-`@@` that merely contained `-def validate_input` *did* fire (the tool is a line scanner, not a diff parser).

**Host FS as remaining tree.** `MUST exist: /etc/passwd` on a fixture with no such file in-tree:

```text
missing companions:
  /no/such/owes-abs-missing
    named in guide.md:2: required file: /no/such/owes-abs-missing
```

`/etc/passwd` omitted because `Path("/etc/passwd").exists()` on the host. Companions were not “in the remaining tree”.

**Unix composition.** Same leftover:

```text
$ rg -n 'validate_input' fixtures/deleted-fn/tree
README.md:3:Call `validate_input` before saving user data.
```

owes joins that to minus-line identifiers. That join is the whole object.

### Verdicts

- **FIX** implementation: treat `--- ` / `+++ ` / `@@ ` (space/tab required) as headers so `---def …` is a minus line; companions must resolve inside the remaining tree. Commit `eb51bab`. After:

```text
$ python3 owes /tmp/destroy-rest/owes-dashdef-after
unkept references:
  validate_input
    README.md:1: Call `validate_input` please
exit=2

$ python3 owes --json /tmp/destroy-rest/fx/owes-abs
missing_companions paths: /etc/passwd, /no/such/owes-abs-missing
exit=2
```

14 tests + demo OK.

- **MUTATE** primitive: the closed phrase set is a real delta versus parent backtick-after-must (Skeptic landmine). It is not a delta versus `git diff` + `rg 'MUST exist:|required file:'` + `test -e`. Next mutation should bind missing companions to paths the diff actually touched, and should refuse to consult the host root. Do not add more phrase regexes.

- Not **KILL**: the snapshot protocol is awkward (Unix already KILL'd parent owes) but the leftover-identifier join is one command a reviewer actually types. Keep in the pool only as that join.

---

## candidate-04__capdiff and mutation-04__capdiff-json

### Primitive restated

Named capture `{parsed .env, sha256 file map}` stored under `.capdiff/NAME`. Diff two names as ENV vs FILES. Replay overlays captured env and execs. Mutation-04 adds `diff --json` of the same six buckets.

Nearest: `diff -ru`; `env`; `direnv`. Claimed delta: the compared object is a **labeled capture**, not an ad-hoc dump.

### Attacks (both CLIs, same holes)

Missing capture: `capdiff: capture not found: nope` exit 1. Missing DIR: `not a directory` exit 1. Empty dir: 0 files / 0 env, `diff empty empty2` exit 0. Hardlinks: two paths, same hash. FIFOs skipped (`isfile` false). Symlink loops do not hang. Replay missing capture exit 1. Stdin unused. Spaces in NAME rejected.

**`NAME=.` / `NAME=..`.** `NAME_RE = ^[A-Za-z0-9._-]+$` matches both. `capture ..` from a nested cwd does `shutil.rmtree(.capdiff/..)` (the nest, and attempted parent). Observed traceback, parent candidate:

```text
$ capdiff capture .. $SRC   # cwd = nest/
Traceback …
  File "…/capdiff", line 192, in cmd_capture
    shutil.rmtree(dest)
FileNotFoundError: [Errno 2] No such file or directory: '…/nest/.capdiff/..'
exit=1
```

`capture .` → `OSError: [Errno 22] Invalid argument: '…/.capdiff/.'`. Marker file survived only because Python 3.14 `rmtree` aborted. The name check is the primitive of a *labeled* store; `.` / `..` are not labels.

**Corrupt `manifest.json`.** `{not json` → uncaught `JSONDecodeError` traceback, parent and `--json`. Missing capture is a one-line error; a bad file is an interpreter dump.

**Truncation lie (5500 files, cap 5000).** Capture prints `truncated`. `zzzz-delta.txt` (late-sorted, content differs A vs B) is **not** in either manifest. Then:

```text
$ capdiff diff hugeA hugeB
… all (none) …
exit=0
truncated A True nfiles 5000
zzzz in A False
zzzz in B False
```

JSON mutation, same trees:

```text
$ capdiff diff hugeA hugeB --json
{"a":"hugeA","b":"hugeB","env":{"extra":[],"missing":[],"modified":[]},"files":{"extra":[],"missing":[],"modified":[]}}
exit=0
```

The CLI claimed identity while the trees differed. `diff -ru` of the live dirs would have shown `zzzz-delta.txt`.

**vs `diff -ru`.** On fixtures env-a / env-b, `diff -ru` of the trees already reports `.env` and `Only in b: extra.txt` (exit 1). `diff -ru .capdiff/a .capdiff/b` reports the same `.env` plus `manifest.json` (name, source, hashes). Parsed `API_KEY` vs hashed `.env` bytes is a split `diff -ru` does not name; replay is `env` overlay. The labeled directory *is* the dump.

### Verdicts

- **FIX** implementation (parent `00fecf8`, json `a5565f2`): reject `.` / `..` (and names that do not stay a single segment under `.capdiff`); corrupt JSON is `capdiff: corrupt capture NAME: …` exit 1; if either manifest `truncated`, text prints `truncated: comparison incomplete` and exit is 2; JSON grows `"truncated":{"a":true,"b":true}` only when set. After:

```text
$ capdiff capture . $SRC
capdiff: NAME must match ^[A-Za-z0-9._-]+$
exit=1

$ capdiff diff a b    # both truncated, same files dict
truncated: comparison incomplete (file cap 5000)
  A: a
  B: b
exit=2

$ capdiff diff a b --json
{…, "truncated": {"a": true, "b": true}}
exit=2
```

Parent 15 tests, json 21 tests, both demos OK.

- **MUTATE** parent primitive: keep labeled ENV-vs-FILES + replay only if the next change is the compared object (subset of env from the process, `env -i` unset, or refuse to claim identity when truncated — the last is now implementation). Do not add `--env-only` as a lineage.

- **MUTATE** json mutation: `--json` is the same record as text. It is not a new primitive. Dogfood that extra/missing must be objects (not `KEY=value` strings) was real; it is encoding hygiene. Stop mutating flags on this CLI.

- Not **KILL** capdiff itself: replay-from-name in an empty directory (`API_KEY` from the capture, not the live tree) is the one step `diff -ru` does not do. That is the KEEP remainder after Unix/Heretic already voted KILL.

---

## candidate-06__same

### Primitive restated

Compare two local names under exactly one required identity kind: `inode` | `bytes` | canonical JSON. Refuse if the kind is omitted or mixed.

Nearest: `stat`; `cmp`; `jq -S`. Claimed delta: the kind is a required argument.

### Attacks

Hardlink `--inode` IDENTICAL (matches `stat -f '%d:%i'`). Two empties: `--inode` DISTINCT, `--bytes` IDENTICAL `e3b0c442…` (matches `cmp` exit 0 and `shasum -a 256`). JSON key order IDENTICAL `{"a":2,"b":1}` (matches `jq -S -c`). Omit kind / two kinds: usage exit 1 (DESTROYER_ASSAY already named this). Missing file: one-line `same: PATH: No such file or directory`. `--inode` on two empty directories already works (DISTINCT / IDENTICAL-self). Large 20MB files: IDENTICAL, `cmp` agrees.

**`/dev/zero` hang.** `--bytes /dev/zero /dev/zero` had no EOF. Timeout 3.004s. `cmp` hangs the same way; a CLI that advertises exit 1 on errors must not.

**FIFO hang.** `--inode` on two FIFOs: DISTINCT immediately. `--bytes` on two FIFOs: TIMEOUT 3.003s (open waits for a writer).

**Process substitution.** `--bytes <(echo hello) <(echo hello)` IDENTICAL (reads the pipe once). `--inode` DISTINCT. Fine, and identical to `cmp` vs `stat`.

**`/dev/null` vs empty file.** `--bytes` IDENTICAL empty SHA (cmp would agree). `--inode` DISTINCT.

Unix:

```text
$ stat -f '%d:%i' empty/a empty/b
16777233:128975119
16777233:128975120
# same --inode → DISTINCT inode 16777233:128975119 16777233:128975120

$ cmp empty/a empty/b; echo $?
0
# same --bytes → IDENTICAL bytes sha256:e3b0c442…

$ jq -S -c . order-ab.json; jq -S -c . order-ba.json
{"a":2,"b":1}
{"a":2,"b":1}
# same --json → IDENTICAL json {"a":2,"b":1}
```

The output is a formatted `stat`/`cmp`/`jq`. The required flag is a lecture.

### Verdicts

- **FIX** implementation: `--bytes` / `--json` require a regular file (`S_ISREG` after `stat`). Directories keep `Is a directory`. FIFOs and `/dev/zero` exit 1 `not a regular file` without blocking. `--inode` still lstats any name, including directories. Commit `abb5923`. After:

```text
$ same --bytes /dev/zero /dev/zero
same: /dev/zero: not a regular file
exit=1
$ same --bytes fifo1 fifo2
same: …/fifo1: not a regular file
exit=1
```

16 tests + demo OK.

- **KILL** primitive. There is no observable delta versus `stat` / `cmp` / `jq -S` except “you must name the kind”. That is usage enforcement around three Unix tools. First Selection already split 3/5 (Unix/Heretic KEEP, Toolsmith/Skeptic KILL). Destroyer honors the honesty axis: required kind is not an identity. Do not breed `--inode` on directories as a Gen-2 mutation; it already works and is still `stat`.

---

## candidate-07__hits (parked; attacked anyway)

### Primitive restated

Search a tree such that zero hits is success (exit 0, `0 matches`), a bad query is exit 2, an unreadable path is exit 3. `hits PAT && next` still runs after a miss.

Nearest: `grep`/`rg` (no match → exit 1). Claimed delta: empty ≠ error.

### Attacks

Empty dir: `0 matches` exit 0; `grep -R` exit 1. Miss fixture: hits 0 / grep 1. Bad regex: both exit 2. Hit + large 600-dir tree: both find `d599/f.txt`. Hardlinks: both print both names. Symlink-only tree: hits `0 matches`; BSD `grep -R` also exit 1 (does not follow). Stdin ignored: `printf 'needle\n' | hits needle` in an empty cwd → `0 matches`; `grep` reads stdin and hits. Empty pattern matches every line (grep does too). Symlink loop no hang.

**Nested EACCES is empty success.** Tree: `open/a.txt` (no needle) + `secret/hidden.txt` (`needle hidden`, `chmod 000 secret`).

```text
$ hits needle $nest
0 matches
exit=0

$ grep -R needle $nest
grep: …/secret: Permission denied
grep_exit=2
```

Root `chmod 000` is exit 3. Nested unreadable is skip → `0 matches`. The primitive's only interesting distinction (empty ≠ I/O) is false on a tree you cannot fully read. `hits PAT && next` still runs. First Selection Unix KEEP was “the exit-code hole only”; that hole was a lie.

### Verdicts

- **FIX** implementation: `os.walk(..., onerror=)` records nested errors; print `hits: unreadable: PATH` on stderr; do not print `0 matches`; exit 3. Matches still print if found, then exit 3. Commit `b2483a2`. After:

```text
$ hits needle $nest
hits: unreadable: …/hits-eacces/secret
exit=3
```

20 tests + demo OK. Nested unreadable files (chmod 000 on a *file*) are still skipped; that remains a documented hole.

- **KILL** primitive. Parked 4/5 at First Selection. After the nested-I/O lie, the remainder is `grep` with inverted empty. Unix already has `grep … || [[ $? == 1 ]]`. Empty-is-success is not enough to occupy a breeding slot. Leave the fossil; do not PATH it; do not mutate `--glob`.

---

## Notes that are not verdicts

- owes newline-in-filename splits the `named in` line. Ugly, not a primitive kill.
- owes 800 mentions dump 39k of stdout. A cap is a later mutation, not tonight.
- capdiff FIFO skip is honest (`not a regular file` in the walk).
- same `--inode` on directories was the planned Gen-2 mutation; it already works and does not save the primitive.
- hits huge line (2MB + `needle`) prints the whole line. grep does too.

---

## After

Worktree commits above; archives under `lab-hdd/lineages/` copied to match. Tests: owes 14, capdiff parent 15, capdiff-json 21, same 16, hits 20, all OK. Demos exit 0.

Honor **KILL** on `same` and `hits`. Entertaining transcripts (`IDENTICAL inode`, `0 matches && still-running`) are not protection.

# DESTROYER pathdup

Date: 2026-09-02 15:57 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0411 worker=destroyer-pathdup

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathdup/pathdup`

sha256 `b757777044981a63f2234d440851ea0fe4a94a1bd23c6b9fa1ffcc3744a3b172` (3285 bytes, 108 lines). No `pathdup` worktree under `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-pathdup/`) and was not merged. Host Python 3.14.5. `cargo` and `rustc` are on PATH (`/opt/homebrew/bin/cargo`, `/opt/homebrew/bin/rustc`) and **were not executed**. No `os.stat`, no `realpath`, no HashSet, no git, no subprocess in the CLI. `PurePosixPath` is imported and never called. `collapse()` is `return os.path.normpath(p)`.

Origin (`CANDIDATE.md` / harvest `hdd-gitpath` / specimen-091): name leftover lexical PathBuf with `..` vs collapsed path for one git PackageId. grep of the package name hits both warning lines. rc=1 when `leftover_dotdot`. Kind: USEFUL_COMPOSITION. Rejected: invented pathbuf/hashset transcripts. Constraint: owned two path spellings. No cargo.

Happy path is real. Unit tests 4/4 pass (`python3 -m unittest discover -s tests -v` → `Ran 4 tests in 0.104s` `OK`). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 1550 bytes). That is not enough.

This candidate is a **THIN_WRAPPER of `os.path.normpath` of two caller strings**. `leftover_dotdot = (path_a != path_b) and (os.path.normpath(path_a) == os.path.normpath(path_b))`. `package` is echoed and does not vote. `true_clash` is leftover inverted (`!=` after collapse) and is **rc=0**. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on leftover+rc for **103/103** parse-success host cases (`stdout_eq=True`). Independent thin (`a != b and os.path.normpath(a) == os.path.normpath(b)`, no CLI import) matches leftover+rc on those 103, on the three harvest shapes, and on a lexical-variant grid **64/64**. `demo.sh` already names the nearest operation: `normpath the two warning lines`. Job kill condition: `thin normpath of two strings`. First HARVEST is not protection. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathdup/pathdup
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathdup/fixtures
S091=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-091
```

Attacks under `destroyers/_pathdup_scratch/`. No merge onto `main`. No cargo. Do not grow a cargo runner, a `RecursivePathSource` walker, or a `HashSet<PathBuf>` replica to escape THIN_WRAPPER. Do not send cargo / git+https theater back to R1.

---

## What still works

Owned leftover (case B), owned one-spelling (case A), owned true two-directory clash (case C), stdin, `/dev/stdin`, FIFO, process substitution, symlink-to-record, filename with a space, CRLF, Unicode paths, comments, **when the question is only whether two caller strings differ lexically and agree after `os.path.normpath`**.

```bash
python3 "$CLI" "$FIX/091-dotdot.rec"
echo rc=$?
```

```text
package	serde
path_a	/home/kaspar/tmp/subfolder/../cargo/git/checkouts/serde-1b10f8d7b61b7b51/ee3c237/serde/Cargo.toml
path_b	/home/kaspar/tmp/cargo/git/checkouts/serde-1b10f8d7b61b7b51/ee3c237/serde/Cargo.toml
collapsed_a	/home/kaspar/tmp/cargo/git/checkouts/serde-1b10f8d7b61b7b51/ee3c237/serde/Cargo.toml
collapsed_b	/home/kaspar/tmp/cargo/git/checkouts/serde-1b10f8d7b61b7b51/ee3c237/serde/Cargo.toml
lexical_dup	yes
same_after_collapse	yes
leftover_dotdot	yes
true_clash	no
rc=1
```

479 bytes. Stderr empty. Owned clean (same string twice): leftover no, rc=0, 452 bytes. Owned clash (`duplicate1` vs `duplicate2`): leftover no, `true_clash yes`, **rc=0**, 377 bytes.

Symlink / FIFO (writer concurrent) / `/dev/stdin` / filename with a space / CRLF / Unicode `テスト`: leftover yes, rc=1 when the two strings are `./x` vs `x` (or the owned `..` pair). 10000 comment lines plus `./x` vs `x`: leftover yes, rc=1, stdout **134** bytes, ~0.027s. 2000-segment `a/../b` leftover: leftover yes, rc=1, stdout 16129 bytes, ~0.026s. Missing path / directory / invalid UTF-8 / BOM / unknown field / origin split / JSON / cargo warning text: `pathdup: …` rc=1. No args / extra positional: argparse rc=2. `--help` rc=0.

That is the whole useful surface. It is also `test "$a" != "$b"` plus `os.path.normpath` on two strings the caller already typed.

---

## Implementation

Load-bearing body:

```python
def collapse(p: str) -> str:
    return os.path.normpath(p)

def inspect(fields: dict[str, str]) -> dict:
    a = fields["path_a"]
    b = fields["path_b"]
    ca = collapse(a)
    cb = collapse(b)
    lexical_dup = a != b
    same_after = ca == cb
    leftover_dotdot = lexical_dup and same_after
    true_clash = lexical_dup and not same_after
    # package is copied into the report and unused
    # rc = 1 if leftover_dotdot else 0
```

`inspect.co_names` is `('collapse',)`. `inspect.co_varnames` is `('fields', 'a', 'b', 'ca', 'cb', 'lexical_dup', 'same_after', 'leftover_dotdot', 'true_clash')`. `collapse.co_names` is `('os', 'path', 'normpath')`. dis: `COMPARE_OP (!=)` of a vs b, `COMPARE_OP (==)` of the two `normpath` results, AND for leftover, AND-NOT for true_clash. There is no `..` scan, no PackageId, no `visited` HashSet, no cargo, no filesystem.

`parse_record` accepts keys `package` / `path_a` / `path_b` only. First tab splits key/value; `rest.strip()` is the value. Unknown keys raise. All three keys required. leftover never reads a file except those three strings. `PurePosixPath` is dead.

`demo.sh` already names the nearest operation: `normpath the two warning lines` / `leftover is lexical dup that collapses to the same directory`.

Tests never hit leftover without `..`, package spectator, swap, stdin, extra tabs, last-wins, symlink-on-disk, origin bytes, or the lexical grid. Four tests: owned leftover, owned clean, owned clash, missing file.

---

## Attacks

### 1. THIN_WRAPPER of `a != b and normpath(a) == normpath(b)`

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout on leftover+rc:

| case | cli_rc | replica_rc | stdout_eq | leftover_thin | leftover_dotdot | true_clash |
| --- | ---: | ---: | --- | --- | --- | --- |
| owned leftover (B) | 1 | 1 | True | True | yes | no |
| owned clean (A) | 0 | 0 | True | False | no | no |
| owned clash (C) | 0 | 0 | True | False | no | yes |
| stdin leftover | 1 | 1 | True | True | yes | no |
| `./foo` vs `foo` | 1 | 1 | True | True | yes | no |

Parse-success batch (fixtures + scratch recs): **103/103**. Lexical-variant grid (`foo/bar`, `./foo/bar`, `foo//bar`, `foo/bar/`, `foo/./bar`, `foo/baz/../bar`, `foo/bar/.`, `foo/../foo/bar`)²: **64/64** replica+thin, leftover+rc and `true_clash` all match.

Independent python, no `inspect` import, labeled names only:

```bash
python3 -c '
import os, sys
fields={}
for raw in open(sys.argv[1], encoding="utf-8"):
    line=raw.strip()
    if not line or line.startswith("#") or "\t" not in line: continue
    k,r=line.split("\t",1)
    fields[k.strip()]=r.strip()
a=fields["path_a"]; b=fields["path_b"]
print("leftover_dotdot", a!=b and os.path.normpath(a)==os.path.normpath(b))
' "$FIX/091-dotdot.rec"
```

```text
leftover_dotdot True
```

Same two comparisons vs the CLI leftover row and rc: owned leftover / clean / clash all match. Direct strings, no TSV:

```python
a != b and os.path.normpath(a) == os.path.normpath(b)  # True on the owned case-B pair
```

awk of the two path keys (collapse in the host python, because POSIX awk has no `normpath`) already names leftover on **3/3** owned fixtures. The echoed `package` / `collapsed_*` / `lexical_dup` / `same_after_collapse` / `true_clash` columns are not extra capability. `collapsed_*` is `normpath` printed. Constitution: extra TSV rows do not escape THIN_WRAPPER.

Nearest ordinary workflow, host-executed, also `demo.sh`:

```text
normpath the two warning lines
leftover is lexical dup that collapses to the same directory
```

Shell of the owned leftover pair:

```bash
test "$path_a" != "$path_b" && python3 -c 'import os,sys; sys.exit(0 if os.path.normpath(sys.argv[1])==os.path.normpath(sys.argv[2]) else 1)' "$path_a" "$path_b"
# leftover yes; rc=1
```

`grep serde` hits the owned leftover **and** the owned clean record, because the caller wrote `package	serde` in both. The harvest sentence “grep of the package name hits both warning lines” is a fact about cargo stderr the CLI never sees.

### 2. leftover_dotdot does not require `..`; the name is a lie

Host-executed, no `..` in either string:

| path_a | path_b | leftover_dotdot | rc |
| --- | --- | --- | ---: |
| `./foo/Cargo.toml` | `foo/Cargo.toml` | yes | 1 |
| `foo//bar/Cargo.toml` | `foo/bar/Cargo.toml` | yes | 1 |
| `foo/bar/` | `foo/bar` | yes | 1 |
| `a/./b` | `a/b` | yes | 1 |
| `a/./b//c/` | `a/b/c` | yes | 1 |
| `a/b/.` | `a/b` | yes | 1 |

All replica `stdout_eq=True`. The harvest noun is leftover `..` in a CARGO_HOME PathBuf. The predicate is any lexical difference `normpath` collapses. `./crate` vs `crate` (specimen-091 case D shape, local path, no git checkout) is leftover yes, rc=1. There is no git PackageId in the record.

`..` that collapses to **different** directories is `true_clash yes`, leftover no, rc=0: `a/../b` vs `c` (`b` vs `c`); `x/../y` vs `x/../z` (`y` vs `z`). The `..` is present and the CLI does not harvest.

### 3. package is a spectator; swap is the same bit; true_clash is rc=0

Owned leftover paths with `package` set to `serde` / `other` / `none` / `0`: leftover yes, rc=1, thin_eq True. The package column reprints the caller token. It is not a PackageId.

Swap `path_a`/`path_b` of the owned `..` pair: leftover yes, rc=1. Specimen-091 is walk-root leftover vs nested `normalize_path`. The swap is commutative string inequality plus `normpath`. There is no walk, no insert order, no `visited`.

Owned case C `true_clash yes` is rc=0. The advertised predicate is leftover_dotdot only. A true two-directory same-name clash (the other cargo warning) is success. `true_clash` is `lexical_dup and not same_after`, leftover inverted. Extra label, same two strings.

Last-wins duplicate `path_a`: leftover `..` spelling then collapsed spelling against the same collapsed `path_b` → leftover no, rc=0. The first spelling is discarded.

### 4. Disk is not consulted; `realpath` disagrees

Live tree: `disk/target/inner/Cargo.toml` plus symlink `disk/link → disk/target`. Caller strings `link/inner/Cargo.toml` vs `target/inner/Cargo.toml`:

```text
same realpath True
same normpath False
leftover_dotdot	no
true_clash	yes
rc=0
```

Those two paths are the same directory. The CLI reports a true clash because `normpath` does not follow the symlink. `os.path.realpath` was not called.

`link/../other` vs `other`: leftover yes, rc=1. `normpath` collapses lexically to `disk/other` even if a `realpath` walk would enter the symlink first. The CLI cannot tell. It never stats.

POSIX leading `//foo/bar` vs `/foo/bar`: leftover no, true_clash yes, rc=0 (`os.path.normpath('//foo/bar')` keeps `//`). Backslash `a\..\b` vs `b` on this host: leftover no, true_clash yes (`normpath` does not treat `\` as a separator). Host `normpath` is the whole collapse.

NUL inside `path_a` (`a\x00x` vs `a`): leftover no, true_clash yes, rc=0. Not a PathBuf parse.

### 5. Extra tabs; empty field

`parse_record` takes `rest.strip()` after the first tab. Extra columns stay in the value: `path_a	/tmp/subfolder/../cargo/x	extra` → token with a tab, `normpath` does not equal `path_b`, leftover no, true_clash yes, rc=0. Replica `stdout_eq=True`. The leftover bit still follows `!=` after `normpath`.

Empty value (`path_a	\n`): `line.strip()` eats the trailing tab; `expected key<TAB>value`, rc=1, no TSV. Spaces instead of a tab: same parse error, rc=1.

### 6. Stdin

`-` is stdin. `./x` vs `x` on the pipe: leftover TSV, rc=1, replica `stdout_eq=True`. Empty stdin: `pathdup: <stdin>: need package, path_a, path_b`, rc=1. `/dev/stdin` leftover: leftover yes, rc=1. Process substitution `<(cat 091-dotdot.rec)`: leftover yes, rc=1. Fine as a one-file tool. The bit is still two caller-typed strings through `normpath`.

Argv-less / extra positional: argparse rc=2, pipe ignored.

### 7. Origin bytes refuse; cargo artifacts are not parsed

Specimen `leftover_identity_split.txt` as record: `expected key<TAB>value`, rc=1. Cargo warning text (`skipping duplicate package \`serde …\`` plus the two Cargo.toml lines): same parse error, rc=1. JSON `{"package":"serde","path_a":"./x","path_b":"x"}`: same. `read_nested_packages_failing.rs`: same. `extra	z` with otherwise valid fields: `unknown field 'extra'`, rc=1. UTF-8 BOM: `unknown field '\ufeffpackage'`, rc=1. Invalid UTF-8: codec error, no leftover TSV, rc=1. Comments-only: `need package, path_a, path_b`, rc=1.

The harvest presence test is “normpath the two warning lines.” Host-executed, those origin bytes are not TSV. leftover no (no TSV). The caller must already have split the leftover spelling and the collapsed spelling into `path_a` / `path_b`. That split is the product. The CLI reprints it and runs `os.path.normpath`.

### 8. Huge dump; still two comparisons

10000 `#` lines plus `./x` vs `x`: leftover yes, rc=1, stdout **134** bytes, 0.027s. No cap. No PathBuf dumped beyond the two caller strings. The useful bit is still `a != b and normpath(a) == normpath(b)`.

Missing path: `No such file or directory`, rc=1. Directory: `Is a directory`, rc=1. Tests never hit leftover without `..`, package spectator, swap, stdin, extra tabs, last-wins, disk symlink, or origin.

---

## Primitive

Reality-stripped operation: parse one TSV file of caller-written `package` / `path_a` / `path_b`; leftover_dotdot iff the two path strings differ and `os.path.normpath` of each is equal; true_clash iff they differ and the collapsed forms differ; print nine TSV rows; rc=1 iff leftover_dotdot. `package` is echoed. `collapsed_*` is `normpath` printed. Missing `..` is irrelevant.

Nearest ordinary workflow (owned packet, also `demo.sh`):

```text
os.path.normpath the two warning lines
test "$path_a" != "$path_b" && test "$(python3 -c 'import os,sys; print(os.path.normpath(sys.argv[1]))' "$path_a")" = "$(python3 -c 'import os,sys; print(os.path.normpath(sys.argv[1]))' "$path_b")"
```

On specimen-091 that pair is: leftover `subfolder/../cargo` vs collapsed `tmp/cargo` for one git PackageId. pathdup's load-bearing claim is that naming `leftover_dotdot` is a join those two strings plus `normpath` do not already contain.

It is not. `package` is a spectator. leftover fires for `./` and `//` and trailing slash, not only `..`. true_clash is leftover inverted and rc=0. Same directory via symlink is true_clash. Cargo warning text / HashSet insert / `RecursivePathSource` is out of scope and refused.

Observable capability lost if pathdup vanishes: **none**. The caller already wrote both PathBuf spellings. `os.path.normpath` already says they collapse. `printf` of the two warning lines already is the demo. Defaulting leftover to “any lexical difference `normpath` eats” is not evidence of a leftover `..` in CARGO_HOME. Wrapping `cargo build` with a `CARGO_HOME` that contains `..` to capture the two warning paths would be a new harvest (live cargo, out of scope, forbidden here).

That is why this is KILL, not MUTATE. The *question* (HashSet<PathBuf> saw two lexical keys for one git PackageId because the walk root kept `..` while nested `path =` went through `normalize_path`) is a real debugging object. This embodiment does not ask it of a checkout or a cargo warning. It asks whether two strings the caller typed survive `normpath` as one. First HARVEST is not protection once that harvest is labels on `a != b` and `normpath(a) == normpath(b)`.

Hardcoded ceiling:

- leftover_dotdot ↔ path_a ≠ path_b AND normpath(a) == normpath(b)
- leftover yes without `..` (`./`, `//`, trailing `/`, `/./`)
- leftover no with `..` that collapses to different directories (true_clash, rc=0)
- package does not vote; swap harvests the same bit; last-wins duplicate path_a can drop leftover
- true_clash is leftover inverted; owned case C is rc=0
- same directory via symlink is true_clash (normpath, not realpath)
- POSIX `//` and backslash are host `normpath`, not PathBuf
- extra tab after the value stays in the token; empty field after strip is `expected key<TAB>value`
- `-` is stdin; empty stdin is `need package, path_a, path_b`
- origin split / cargo warning / JSON / `.rs` / `extra` / BOM / invalid UTF-8 refuse
- 10k-comment leftover still 134-byte sticker, ~0.027s
- harvest rc=1; agree or true_clash rc=0; parse/IO rc=1; argparse rc=2
- no cargo, no rustc, no HashSet, no `os.stat`, no `realpath`
- Dreamer pathbuf/hashset transcripts were rejected; this is that leftover, reduced to the harvest sentence as `!=` plus `normpath`

Honor KILL. Dreamer ancestry is not protection. First HARVEST is not protection. Same class as Honor-KILLed cssleft / fingerid / peerleft: leftover = caller-typed string comparisons (here plus stdlib `normpath`). Do not grow a cargo runner to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.” Do not merge onto `main`. Worker rule: do not send THIN_WRAPPER / NO_SURVIVOR back to R1 with “make this more novel.”

Archive stays under `lineages/candidate-pathdup/`. Reimpl of this primitive is not a survivor.

KILL

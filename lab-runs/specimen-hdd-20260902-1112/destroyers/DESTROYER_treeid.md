# DESTROYER treeid

Date: 2026-09-02 15:42 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-treeid/treeid`

sha256 `51b30b277f3b5016519cc70a9d240fc1033ad813533d393c9a556b7b281437ec` (3047 bytes, 95 lines). No `treeid` worktree under `lab-runs/.../worktrees` or `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-treeid/`) and was not merged. Host Python 3.14.5. `gradle` / `gradlew` are **absent** from PATH and **were not executed**.

Origin claim (`CANDIDATE.md` / harvest `hdd-ccfilecol` / specimen-088): name whether a fileTree configuration-cache identity omitted member file names (dir+pattern only) so an added file still loads. rc=1 when `hidden_by_omitted_names`. Kind: USEFUL_COMPOSITION. Owned packet: Groovy `fileTree("src").files` store+load then add `src/file3`; named `files("file1","file2")` is a different identity axis. Rejected: invented depscan / Gradle bytecode transcripts. Constraint: owned two identity records. No gradle.

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.081s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log`. That is not enough.

This candidate is a **THIN_WRAPPER of two caller flags**: `stored_identity` sticker in `{dir+pattern, dir-pattern, tree}` **AND** `load_after_add` in `{yes, true, load}`. `inspect()` never walks a tree, never fingerprints WorkInputs, never compares `names` to `added`, never reads `dir` from disk. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on owned + host cases (`cmp` rc=0 on the owned pair, 137 / 125 bytes; replica identical **41/41** parseable records). A python one-liner of those two membership tests matches `hidden_by_omitted_names` and rc on **41/41**. awk of `$1=="stored_identity"` vs `$1=="load_after_add"` matches the three load-bearing columns on both owned fixtures. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-treeid/treeid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-treeid/fixtures
S088=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-088
```

No merge onto `main`. No gradle. Do not grow a configuration-cache fingerprint reader or a `ConfigurableFileTree` observer to escape THIN_WRAPPER. Do not send gradle theater back to R1. First HARVEST is not protection.

---

## What still works

Owned fileTree record, owned named-files record, and any other TSV whose `stored_identity` / `load_after_add` tokens are already the harvest sentence.

```bash
python3 "$CLI" "$FIX/088-filetree.rec"; echo rc=$?
python3 "$CLI" "$FIX/088-named.rec"; echo rc=$?
```

```text
kind	fileTree
stored_identity	dir+pattern
names	file1,file2
added	file3
omitted_names	yes
load_after_add	yes
hidden_by_omitted_names	yes
rc=1

kind	named
stored_identity	names
names	file1,file2
added	file3
omitted_names	no
load_after_add	no
hidden_by_omitted_names	no
rc=0
```

137 / 125 bytes. Stderr empty. Two flags alone (`stored_identity	dir+pattern` + `load_after_add	yes`, no kind/dir/pattern/names/added): same hidden yes, rc=1, kind/names/added printed as `-`. `dir-pattern` and `tree` stickers with `load_after_add	yes`: hidden yes, rc=1. `true` / `load` aliases of yes: hidden yes, rc=1.

Symlink, process substitution, `/dev/stdin`, stdin `-`, filename with a space, CRLF, Unicode names `ファイル1`: same predicate. 10000-name list (~59kB stdout): `hidden_by_omitted_names	yes`, rc=1, 0.026s. Missing path / directory / empty file / comments-only / `/dev/null` / unknown field / spaces instead of tabs / BOM / invalid UTF-8: `treeid: …` rc=1. No args / extra positional: argparse rc=2.

That is the whole useful surface. It is also what `stored_identity in {dir+pattern,dir-pattern,tree} and load_after_add in {yes,true,load}` already does. Attacks below break the “which identity the tree used” claim, or show the primitive cannot grow.

---

## Implementation

`inspect()` in full:

```python
def inspect(fields: dict[str, str]) -> dict:
    ident = fields["stored_identity"]
    omitted = ident in {"dir+pattern", "dir-pattern", "tree"}
    load = fields.get("load_after_add", "") in {"yes", "true", "load"}
    hidden = omitted and load
    return {
        "kind": fields.get("kind") or "-",
        "stored_identity": ident,
        "omitted_names": omitted,
        "load_after_add": load,
        "hidden_by_omitted_names": hidden,
        "names": fields.get("names") or "-",
        "added": fields.get("added") or "-",
    }
```

`inspect.__code__.co_names` is `('get',)`. `parse_record.co_names` is `('enumerate', 'splitlines', 'strip', 'startswith', 'ValueError', 'split', 'KNOWN')`. There is no fingerprint, no file walk, no `fileCollectionObserved`, no comparison of `names` vs `added`. `dir` and `pattern` are in `KNOWN` so they parse; `format_report` never prints them.

`demo.sh` already names the nearest operation: “print files= list and cache hit”.

---

## Attacks

### 1. THIN_WRAPPER: two caller flags are the product

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout+rc on **41/41** parseable host records, including both owned fixtures (`cmp` rc=0, 137 / 125 bytes).

Python one-liner of the two membership tests matches `hidden_by_omitted_names` and rc on those 41 (`fail 0`). awk of the two fields, without `kind`/`names`/`added`:

```awk
BEGIN{FS="\t"}
$1=="stored_identity"{i=$2}
$1=="load_after_add"{l=$2}
END{
  omitted=(i=="dir+pattern"||i=="dir-pattern"||i=="tree")
  load=(l=="yes"||l=="true"||l=="load")
  hidden=(omitted && load)
  printf "omitted_names\t%s\n", omitted?"yes":"no"
  printf "load_after_add\t%s\n", load?"yes":"no"
  printf "hidden_by_omitted_names\t%s\n", hidden?"yes":"no"
}
```

`088-filetree.rec` / `088-named.rec`: awk == CLI those three rows. IDENTICAL.

Two flags, no other harvest columns:

```bash
printf 'stored_identity\tdir+pattern\nload_after_add\tyes\n' | python3 "$CLI" -
```

```text
kind	-
stored_identity	dir+pattern
names	-
added	-
omitted_names	yes
load_after_add	yes
hidden_by_omitted_names	yes
rc=1
```

The harvest records already *are* the input. The CLI reprints the stickers the caller wrote, ANDs them, and exits 1. Concatenating the two owned reports does not discover a cache identity. It reprints `dir+pattern` vs `names` plus `yes` vs `no`.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`kind`, `names`, `added`) to escape classification. Those rows are echo. They do not vote. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Same shape as Honor-KILLed unusedfp (gradle CC identity as caller maps + hashes) and Honor-KILLed peerleft / nilkeep (AND of two caller-labeled tokens).

### 2. Spectator fields: `names` / `added` / `kind` / `dir` / `pattern` never decide

`kind	named`, `dir	NOTSRC`, `pattern	NONE`, `names	NEVER`, `added	ALSO`, still `stored_identity	dir+pattern` + `load_after_add	yes`:

```text
kind	named
stored_identity	dir+pattern
names	NEVER
added	ALSO
omitted_names	yes
load_after_add	yes
hidden_by_omitted_names	yes
rc=1
```

`names	file1,file2,file3` with `added	file3` (the added file is already in the stored name list) + omit sticker + load yes: still hidden yes, rc=1. The CLI does not ask whether the added name entered identity.

`kind	fileTree` with `stored_identity	names` + `load_after_add	no`: hidden no, rc=0. Kind is a label.

`dir	/no/such/src` vs `dir	<candidate-treeid path>` with identical flags: stdout byte-identical, rc=1. `dir` / `pattern` are not printed. Disk is not read. A missing tree and this repo are the same identity because the caller already wrote `dir+pattern` and `yes`.

### 3. Contradiction: one flag is not the harvest

Omit sticker without load, same owned names/added:

```text
stored_identity	dir+pattern
load_after_add	no
omitted_names	yes
hidden_by_omitted_names	no
rc=0
```

Names identity with load after add:

```text
stored_identity	names
load_after_add	yes
omitted_names	no
hidden_by_omitted_names	no
rc=0
```

The harvest AND requires both caller answers. A queried fileTree that actually missed after `src/file3` (contents entered identity) is `dir+pattern` + `no` here — and the CLI reports not hidden. A named collection that still loaded is `names` + `yes` — also not hidden. The tool believes the stickers, not a fingerprint.

Case C (tree constructed, never queried: `names	-`, same omit+load stickers): hidden yes, rc=1. Case A and Case C are the same two flags. The packet’s never-queried contrast cannot enter unless the caller already classified it.

Missing `load_after_add`: `fields.get(..., "")` is not in `{yes,true,load}` → load no → hidden no, rc=0, even with `dir+pattern`. Default is harvest-false, not harvest-true. Still a sticker default, not an observation.

### 4. Identity / load tokens are a closed set, not a fingerprint class

| `stored_identity` | `load_after_add` | omitted | hidden | rc |
| --- | --- | --- | --- | --- |
| `dir+pattern` | `yes` | yes | yes | 1 |
| `dir-pattern` | `yes` | yes | yes | 1 |
| `tree` | `yes` | yes | yes | 1 |
| `TREE` | `yes` | **no** | no | 0 |
| `Dir+Pattern` | `yes` | no | no | 0 |
| `dir_pattern` | `yes` | no | no | 0 |
| `dir+pattern+names` | `yes` | no | no | 0 |
| `contents` / `fingerprint` / `WorkInputs` / `-` | `yes` | no | no | 0 |
| `dir+pattern` | `true` / `load` | yes | yes | 1 |
| `dir+pattern` | `YES` / `True` / `1` / `hit` / `reused` | yes | **no** | 0 |
| `dir+pattern` | (missing) | yes | no | 0 |

`TREE` is not `tree`. `WorkInputs` is the packet’s actual fingerprint record type and is not omitted. `true` is accepted; `True` / `YES` / `1` / `hit` are not. `rest.strip()` makes ` yes ` into `yes` (hidden yes). Empty values are unparseable: `load_after_add<TAB>` / `stored_identity<TAB>` → `expected key<TAB>value`, rc=1, no TSV. That is `line.strip()` eating the tab, not an identity class.

Last-wins: `stored_identity	names` then `dir+pattern` + load yes → hidden yes, rc=1. Reverse load `yes` then `no` → hidden no, rc=0. Duplicate keys are a last assignment, not a pair of cache stores.

### 5. Origin packet cannot enter

```bash
python3 "$CLI" "$S088/files/DefaultConfigurableFileTree_failing.java"; echo rc=$?
python3 "$CLI" "$S088/files/cases.txt"; echo rc=$?
```

```text
treeid: …/DefaultConfigurableFileTree_failing.java:6: expected key<TAB>value
rc=1
treeid: …/cases.txt:1: expected key<TAB>value
rc=1
```

The failing `visitChildren` / `fileCollectionObserved` excerpts and the Case A/B/C notes are not records. The owned fixtures are already the harvest sentence, typed as TSV. Dreamer gradle transcripts were rejected; this is that inspect, reduced to two tokens.

### 6. Parse / IO / stdin

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory | 1 | `Is a directory` |
| empty / comments-only / `/dev/null` | 1 | `need stored_identity` |
| unknown field / `Stored_identity` | 1 | `unknown field` |
| spaces instead of tabs | 1 | `expected key<TAB>value` |
| UTF-8 BOM | 1 | `unknown field '\ufeffstored_identity'` |
| invalid UTF-8 | 1 | codec error |
| CRLF | 1 | `splitlines`, owned hidden |
| stdin `-` | 1 | owned hidden (dash *is* stdin here) |
| argv-less pipe | 2 | argparse |
| `/dev/stdin` / process substitution / symlink / space in filename | 1 | owned hidden |
| 10000 names | 1 | 59009-byte stdout, names echoed, hidden still the two flags |
| `names	file1	file2` extra tab | 1 | value keeps the inner tab; hidden still flags |
| no args / extra positional | 2 | argparse |
| `-h` | 0 | help |

Hidden-yes and parse/IO share rc=1. A pipe cannot tell “omitted names hid the add” from “forgot stored_identity.” Tests never hit aliases, spectators, contradictions, Case C, stdin, BOM, or last-wins. Three tests: owned fileTree, owned named, missing path (rc=1 only).

---

## Primitive

Reality-stripped operation: parse a TSV of `stored_identity TOKEN` plus optional `load_after_add TOKEN`; omitted iff the identity sticker is in `{dir+pattern, dir-pattern, tree}`; load iff the second sticker is in `{yes, true, load}`; print `hidden_by_omitted_names` as their AND; echo `kind` / `names` / `added` as labels; rc=1 iff that AND (or parse/IO).

Nearest ordinary workflow: awk of the two caller-written fields, or reading the two owned records by eye. `demo.sh` already says print `files=` and the cache hit. Observable capability lost if treeid vanishes: **none**. The harvest records already are the input. The join is still a hand comparison after the TSV. Member names are never compared to the added file. Directory contents are never fingerprinted.

That is why this is KILL, not MUTATE. The *question* (after `fileTree("src").files` at configuration time, did run 3 reuse an identity that omitted member names so `src/file3` still loaded, or did contents enter the fingerprint and miss) is a real debugging object. This embodiment does not ask it of a tree, a fingerprint, or a configuration-cache log. It asks two caller flags. Adding `ConfigurationCacheFingerprintWriter` / `fileCollectionObserved` / a WorkInputs decode would be implementing the gradle theater the harvest rejected, and would be a new harvest, not a patch of this 95-line AND. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection.

Hardcoded ceiling:

- hidden iff `stored_identity` ∈ `{dir+pattern, dir-pattern, tree}` AND `load_after_add` ∈ `{yes, true, load}`
- `names` / `added` / `kind` / `dir` / `pattern` are spectators; disk is never read
- `TREE` / `Dir+Pattern` / `contents` / `WorkInputs` are not omitted
- `YES` / `True` / `1` / `hit` / missing load are not load
- empty identity/load values unparseable (`line.strip()` eats the tab)
- unary record; the harvest fileTree-vs-named contrast is two invocations plus a hand join
- Case C equals Case A when the caller writes the same two flags
- origin java / cases.txt refuse
- hidden and parse/IO share rc=1
- 10k-name dumps reprint the names column and still AND the stickers
- Dreamer gradle probe was rejected; this is that inspect, reduced to two caller flags

Honor KILL. Dreamer ancestry is not protection. First HARVEST is not protection.

Do not grow a configuration-cache fingerprint parser or a fileTree observer to escape THIN_WRAPPER. Do not merge this join onto `main`. No gradle. Do not send gradle theater back to R1.

---

KILL

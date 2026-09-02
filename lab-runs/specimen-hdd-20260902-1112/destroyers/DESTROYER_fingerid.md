# DESTROYER fingerid

Date: 2026-09-02 15:35 JST
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-fingerid/fingerid`

sha256 `227ba07eb032143a4094e3826cf6c93cefd299c257a6cb881f503f34f2e708c6` (3628 bytes, 114 lines). No fingerid worktree. Parent `main` is `432f954`; archive is untracked (`?? lineages/candidate-fingerid/`) and was not merged. Host Python 3.14.5. `rustc` and `cargo` are on PATH (`/opt/homebrew/bin/rustc`, `/opt/homebrew/bin/cargo`) and **were not executed**. No `os.stat`, no hasher, no subprocess in the CLI.

Origin (`CANDIDATE.md` / harvest `hdd-rustcfinger` / specimen-086): name whether two rustc identities collide on path+mtime fingerprint while `rustc -vV` host strings differ. Size and birth are spectators on the failing revision. rc=1 when `hidden_by_fingerprint`. Kind: USEFUL_COMPOSITION. Rejected: invented cargo `Cache::load` transcripts. Constraint: owned two rustc identity records; no cargo/rustc required.

Happy path is real. Unit tests 4/4 pass (`python3 -m unittest discover -s tests -v` → `Ran 4 tests in 0.107s` `OK`). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 1293 bytes). That is not enough.

This candidate is a **THIN_WRAPPER of string equality** on caller-typed `path` / `mtime` / `vv`. `hidden_by_fingerprint = (path_a==path_b and mtime_a==mtime_b) and vv_a!=vv_b`. Size/birth default to `"-"` and do not vote. Missing `vv` defaults to `""` (printed `-`). Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on leftover+rc for **22/22** host cases. awk of the three TSV keys matches `hidden` and rc on owned / same / size / swap / missing-vv / omit-size. `test "$path_a" = "$path_b" && test "$mtime_a" = "$mtime_b" && test "$vv_a" != "$vv_b"` is the load-bearing bit. Same class as Honor-KILLed platid (`hidden` = inequality + default-true flags). First HARVEST is not protection. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-fingerid/fingerid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-fingerid/fixtures
```

No merge onto `main`. No cargo. No rustc. Do not grow a rustc_fingerprint hasher / `.rustc_info.json` parser to escape THIN_WRAPPER. Do not send cargo theater back to R1.

## What still works

Owned 086: Fedora fc42 vs fc40, same `/usr/bin/rustc`, same clamped mtime `2024-10-17 00:00:00`, `-vV` suffixes differ. `hidden_by_fingerprint yes` / rc=1. Same file twice: hidden no, rc=0. Unseen size `12345` vs `-`: `same_size no`, fingerprint still collides, hidden yes, rc=1. Missing path `/nope`: `fingerid: [Errno 2] …` rc=1.

```bash
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/086-fc40.rec"; echo rc=$?
```

```text
path_a	/usr/bin/rustc
path_b	/usr/bin/rustc
mtime_a	2024-10-17 00:00:00
mtime_b	2024-10-17 00:00:00
vv_a	rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc42)
vv_b	rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)
same_path	yes
same_mtime	yes
same_size	yes
same_birth	yes
same_vv	no
fingerprint_same	yes
hidden_by_fingerprint	yes
rc=1
```

344 bytes. Stderr empty.

```bash
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/086-fc42.rec"; echo rc=$?
# hidden_by_fingerprint	no
# rc=0
```

```bash
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/unseen-size.rec"; echo rc=$?
# same_size	no
# fingerprint_same	yes
# hidden_by_fingerprint	yes
# rc=1
```

Swapped argv (`086-fc40.rec` then `086-fc42.rec`): same harvest, rc=1. Order of files is not compiler-X-then-Y.

That is the whole useful surface. It is also `test` of three strings the caller already typed. Attacks below show size/birth are spectators, missing `vv` still harvests, and a replica of `inspect` is the CLI.

## Implementation

Load-bearing body of `inspect()`:

```python
same_path = a.path == b.path
same_mtime = a.mtime == b.mtime
same_size = a.size == b.size
same_birth = a.birth == b.birth
same_vv = a.vv == b.vv
fingerprint_same = same_path and same_mtime
hidden = fingerprint_same and not same_vv
# rc = 1 if hidden else 0
```

`Ident` defaults: `size`/`birth` → `"-"`; `vv` → `""` (format prints `vv or '-'`). `inspect.co_names` is `('path', 'mtime', 'size', 'birth', 'vv')`. No hash. No stat of `/usr/bin/rustc`. No `Cache::load`. `demo.sh` already names the nearest operation: `diff two rustc -vV; compare path+mtime`.

### 1. THIN_WRAPPER of caller-typed path/mtime/vv

Independent reconstruction of `inspect` + `format_report` (exec of the same predicate, not a package import) is **stdout+rc identical** to the CLI on 22/22 host cases: owned, same-file, size, swapped argv, missing vv, both-omitted vv, omitted-vv vs `vv	-`, birth spectator, path-diff, mtime-diff, same-vv with size/birth noise, omit-size, min fields, garbage vv, comments, CRLF, space in filename, last-wins duplicate `vv`, stripped trailing space, symlink, and the two parse-error leftovers (blank `vv` value; empty `path` value).

awk of the three load-bearing keys, without size/birth:

```awk
BEGIN{FS="\t"}
FNR==1{file++}
$1=="path"{p[file]=$2}
$1=="mtime"{m[file]=$2}
$1=="vv"{v[file]=$2}
END{
  hidden=(p[1]==p[2] && m[1]==m[2] && v[1]!=v[2])
  printf "hidden %s rc %s\n", hidden?"yes":"no", hidden?1:0
}
```

owned / same / size / swap / missing-vv / omit-size: awk == CLI `hidden_by_fingerprint` and rc.

Shell of the owned pair:

```bash
test "$path_a" = "$path_b" && test "$mtime_a" = "$mtime_b" && test "$vv_a" != "$vv_b"
# hidden yes; rc=1
```

`same_size` / `same_birth` are printed and unused. Constitution: extra TSV rows do not escape THIN_WRAPPER.

### 2. Size and birth are spectators; missing vv still harvests

Owned fc42 vs a record with the same path+mtime, no `vv` key:

```text
vv_a	rustc 1.82.0 … (Fedora 1.82.0-1.fc42)
vv_b	-
same_vv	no
hidden_by_fingerprint	yes
rc=1
```

The `-vV` string is not in the second record. Default empty `vv` is inequality against a present string. Both sides omit `vv`: `same_vv yes`, hidden no, rc=0 — two blanks agree. Explicit `vv	-` vs omitted `vv`: both rows print `-`, `same_vv no`, **hidden yes**, rc=1. The printed identity is not the compared identity.

`vv	` with an empty value is `expected key<TAB>value` (line.strip() eats the tab). Omit the key; do not blank it.

Birth `2020-01-01` vs `-`: `same_birth no`, still hidden yes, rc=1. Path `/usr/local/bin/rustc`: `fingerprint_same no`, hidden no, rc=0. Mtime `2024-10-18`: same. Same `vv` with size `999` and birth `x`: fingerprint yes, hidden no, rc=0. Size/birth never vote.

Garbage `vv	not-even-a-rustc-string` vs owned fc42: hidden yes. Min fields (`path`+`mtime`+`vv` only): size/birth default `-`, hidden yes. The Fedora suffix is a caller string, not `rustc -vV`.

NUL inside `vv` (`fc40\x00suffix`) is kept as `fc40suffix` (text mode); still hidden against fc42. Not a rustc parse.

### 3. Swapped argv; not a fingerprint

`086-fc40.rec` then `086-fc42.rec`: hidden yes, rc=1. Specimen-086 is X-then-Y on a shared `target/.rustc_info.json`. The swap is commutative string inequality. There is no cache file, no `rustc_fingerprint` u64, no dirty bit.

Symlink / FIFO / process substitution / filename with a space / CRLF / comments: same owned leftover, rc=1. 10000-char path both sides, different `vv`: hidden yes, ~20k stdout. Missing `/nope` / directory / empty file / `/dev/null` / no tabs / JSON / unknown field / missing mtime / BOM / invalid UTF-8: `fingerid: …` rc=1. `-` as a path is not stdin (`No such file`, rc=1). No args / one arg / extra arg: argparse rc=2. `--help` rc=0.

`.rustc_info.json` / a real rustc binary / `cargo metadata` are unknown fields or not TSV. The caller must already have typed path, mtime, and the two `-vV` strings.

## Primitive

Parse two TSV tables of caller-written `path`/`mtime`/`vv` (optional `size`/`birth`); hidden iff the two paths match, the two mtimes match, and the two `vv` strings differ; rc=1 iff hidden. Missing size/birth are `"-"`. Missing vv is `""`.

Nearest ordinary workflow (owned packet, also `demo.sh`):

```text
diff two rustc -vV strings; compare path and mtime
test "$path_a" = "$path_b" && test "$mtime_a" = "$mtime_b" && test "$vv_a" != "$vv_b"
```

On specimen-086 that pair is: same `/usr/bin/rustc`, same clamped mtime, Fedora fc42 vs fc40 in `-vV`. fingerid's load-bearing claim is that naming `hidden_by_fingerprint` is a join those three strings do not already contain.

It is not. Size/birth are spectators. Missing `vv` still harvests against a present string. Swap is the same bit. Stat of the rustc path / hashing `hash_exe` / reading `.rustc_info.json` / running `rustc -vV` is out of scope and refused.

Observable capability lost if fingerid vanishes: **none**. The caller already wrote both identities. `test` already says the collision. `printf` of the two `vv` lines already is the demo. Defaulting missing size/birth to `-` is not evidence of `st_size` / birthtime. Wrapping `rustc -vV` plus `stat` to capture path/mtime/verbose-version would be a new harvest (live rustc, out of scope, forbidden here).

That is why this is KILL, not MUTATE. The *question* (Cache::load reused `.rustc_info.json` because path+mtime matched while `-vV` would have differed) is a real debugging object. This embodiment does not ask it of a cache file or a compiler. It asks whether three strings the caller typed collide. First HARVEST is not protection once that harvest is labels on `a == b` / `c != d`.

Hardcoded ceiling:

- `hidden_by_fingerprint` ↔ path equal and mtime equal and vv unequal
- size/birth default `"-"` and do not vote; different size/birth still harvest
- missing `vv` is `""` (prints `-`); vs a present string, harvest; vs another omit, not hidden
- omitted `vv` vs explicit `vv	-` both print `-` and still harvest (`same_vv no`)
- swapped argv harvests the same bit; no X-then-Y cache axis
- garbage `vv` harvests; not a rustc parse
- harvest rc=1; agree rc=0
- `.rustc_info.json` / rustc binary / JSON / BOM / empty stdin refuse
- no rustc, no cargo, no hasher, no `os.stat`

Honor KILL. Dreamer ancestry is not protection. First HARVEST is not protection. Same class as Honor-KILLed platid / platident: hidden = string inequality plus defaults that fill the specimen. Do not grow a rustc runner to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.” Do not merge onto `main`.

Archive stays under `lineages/candidate-fingerid/`.

KILL

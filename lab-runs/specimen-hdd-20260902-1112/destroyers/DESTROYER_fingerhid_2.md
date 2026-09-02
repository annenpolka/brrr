# DESTROYER fingerhid 2

Date: 2026-09-02 15:45 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0381
Worker: destroyer-fingerhid-2

Target (archive):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-fingerhid/fingerhid`

sha256 `7aa32068bae559404aef2846c4888e6ef5d960992e77b5012d9d42e5951cbb0e` (3627 bytes, 110 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-fingerhid-fingerhid/fingerhid/fingerhid` is byte-identical (`cmp` rc=0). HEAD `50a760f ground fingerhid from hdd-rustcfinger harvest`, branch `specimen-hdd/candidate-fingerhid-fingerhid`. Parent `main` is `432f954`; `git ls-tree HEAD -- fingerhid` empty. Host Python 3.14.5. unittest 3/3 (`python3 -m unittest discover -s …/tests -v` → `Ran 3 tests in 0.078s` `OK`). `demo.sh` twice to temp logs: byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (605 bytes). `rustc` and `cargo` are on PATH (`/opt/homebrew/bin/rustc`, `/opt/homebrew/bin/cargo`) and **were not executed**. No `os.stat`, no hasher, no subprocess in the CLI. Archive was not edited. Not merged onto `main`.

Origin (`CANDIDATE.md` / harvest `hdd-rustcfinger` / specimen-086): name fingerprint collision vs `-vV` mismatch: `hidden_by_fingerprint` when path and mtime match and verbose-version strings differ. size/birth spectators (not in rustc_fingerprint). Kind: USEFUL_COMPOSITION. Rejected: invented cargo `Cache::load` transcripts. Constraint: owned two rustc identity records; no cargo/rustc required.

First destroyer (`DESTROYER_fingerhid.md`) **KEEP**: tests 3/3; demos identical; owned fc42 vs fc40 harvests at rc=1 with `same_size no` / `same_birth no`; same vv is not hidden, rc=0. Holes named in that KEEP: size/birth never enter the verdict; the join is three equalities on caller-written fields; later destroyer may KILL as THIN_WRAPPER of `path_a==path_b and mtime_a==mtime_b and vv_a!=vv_b`. This is that destroyer. First KEEP is not protection.

Sibling `fingerid` Honor-KILL (`DESTROYER_fingerid.md`): `hidden = path_a==path_b and mtime_a==mtime_b and vv_a!=vv_b` on caller-typed fields. fingerhid is the same join. Size/birth remain spectators (fingerhid prints `-` when either side omits them; fingerid defaulted them to `"-"` and still did not vote). Requiring `vv` (missing key is a parse error) is a legality check, not a fingerprint. Same class as Honor-KILLed platid / platident / fingerid. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-fingerhid/fingerhid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-fingerhid/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-fingerhid-fingerhid/fingerhid/fingerhid
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not run cargo or rustc. Do not grow a rustc_fingerprint hasher / `.rustc_info.json` parser to escape THIN_WRAPPER. Do not mint a third rustc_fingerprint CLI. Do not send cargo theater back to R1.

## What still works

Owned 086: Fedora fc42 vs fc40, same `/usr/bin/rustc`, same clamped mtime `2024-10-17 00:00:00`, `vv` suffixes differ. `same_path yes` / `same_mtime yes` / `vv_mismatch yes` / `same_size no` / `same_birth no` / `hidden_by_fingerprint yes` / rc=1. Same file twice: hidden no, rc=0. Unseen agree (same path+mtime+vv, no size/birth): `same_size -` / `same_birth -` / hidden no, rc=0. Missing path `/no/such/fingerhid`: empty stdout, `fingerhid: [Errno 2] No such file or directory`, rc=1.

```bash
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/086-fc40.rec"; echo rc=$?
```

```text
same_path	yes
same_mtime	yes
vv_mismatch	yes
same_size	no
same_birth	no
hidden_by_fingerprint	yes
vv_a	(Fedora 1.82.0-1.fc42)
vv_b	(Fedora 1.82.0-1.fc40)
rc=1
```

154 bytes. Stderr empty.

```bash
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/086-fc42.rec"; echo rc=$?
# hidden_by_fingerprint	no
# rc=0
```

```bash
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/unseen-agree.rec"; echo rc=$?
# same_size	-
# same_birth	-
# vv_mismatch	no
# hidden_by_fingerprint	no
# rc=0
```

Swapped argv (`086-fc40.rec` then `086-fc42.rec`): same harvest, rc=1. Order of files is not compiler-X-then-Y.

That is the first KEEP. It is also `test` of three strings the caller already typed. Attacks below show size/birth are spectators, requiring `vv` does not add an observation, and a replica of `inspect` is the CLI.

## Implementation

Load-bearing body of `inspect()`:

```python
same_path = a["path"] == b["path"]
same_mtime = a["mtime"] == b["mtime"]
vv_mismatch = a["vv"] != b["vv"]
same_size = a.get("size") == b.get("size") if ("size" in a and "size" in b) else None
same_birth = a.get("birth") == b.get("birth") if ("birth" in a and "birth" in b) else None
hidden = same_path and same_mtime and vv_mismatch
# rc = 1 if hidden else 0
```

`parse_record` requires `path`/`mtime`/`vv`. Empty value or `-` is `not a legal NAME`. Optional `size`/`birth` never enter `hidden`. `inspect.co_names` is `('get',)`. `format_report.co_names` is `('yn', 'join')`. No hash. No stat of `/usr/bin/rustc`. No `Cache::load`. Owned fixtures store only the Fedora suffix, not a `rustc -vV` transcript. `demo.sh` already names the nearest operation: `diff two rustc -vV; compare path+mtime`.

### 1. THIN_WRAPPER of caller-typed path/mtime/vv

Independent reconstruction of `parse_record` + `inspect` + `format_report` (exec of the same predicate, not a package import) is **stdout+stderr+rc identical** to the CLI on **32/32** host cases: owned, same-file, agree, swapped argv, path-diff, mtime-diff, same-size/diff-birth, diff-size/same-birth, omit-size, min-fields, min-min, garbage vv, comments, CRLF, space in filename, last-wins duplicate `vv`, stripped trailing space, huge path, same-vv with size/birth noise, full rustc `-vV` string vs suffix, missing vv, `vv	-`, empty `vv` value, `size	-`, empty path, missing mtime, unknown field, no tabs, JSON, BOM, empty file, and sibling fingerid owned fixtures (`size	-` / `birth	-` refused as NAME).

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

Unix TSV harvests (owned / same / agree / swap / path-diff / mtime-diff / size / birth / omit-size / min / garbage / comments / space / dup / strip / huge / same-vv-noise / full-vv): awk == CLI `hidden_by_fingerprint` and rc **19/19**. CRLF harvests at the CLI (`line.strip()` eats `\r`) and mismatches raw awk (`$1` is `path\r`). That is strip-normalization, not a fourth equality.

Shell of the owned pair:

```bash
test "$path_a" = "$path_b" && test "$mtime_a" = "$mtime_b" && test "$vv_a" != "$vv_b"
# true; CLI hidden yes; CLI rc=1
```

`same_size` / `same_birth` are printed and unused. Constitution: extra TSV rows do not escape THIN_WRAPPER.

### 2. Size and birth are spectators; requiring vv is a parse check

Owned fc42 vs fc40 already disagrees on size (`1` vs `2`) and birth (`x` vs `y`): `same_size no` / `same_birth no` / **hidden yes**, rc=1. Align size, leave birth different: still hidden yes. Align birth, leave size different: still hidden yes. Omit size on B: `same_size -` / still hidden yes. Min fields (`path`+`mtime`+`vv` only, both sides): `same_size -` / `same_birth -` / hidden yes, rc=1.

Same `vv` with size `999` and birth `z`: `vv_mismatch no` / `same_size no` / `same_birth no` / **hidden no**, rc=0. Size/birth never vote.

Missing `vv` key: `fingerhid: … missing vv`, rc=1, empty stdout. Explicit `vv	-`: `not a legal NAME`, rc=1. Empty `vv` value (`vv<TAB>`): `expected key<TAB>value` (`line.strip()` eats the tab). Sibling fingerid owned fixtures (`size	-` / `birth	-`): `not a legal NAME`. fingerid's missing-`vv` default-empty harvest does not exist here. That is stricter parsing of the same three caller-typed fields. It is not a rustc observation.

Path `/usr/local/bin/rustc`: `same_path no` / `vv_mismatch yes` / **hidden no**, rc=0. Mtime `2024-10-18`: same. Fingerprint is path+mtime string equality; `-vV` inequality alone does not harvest.

Garbage `vv	not-even-a-rustc-string` vs owned fc42: hidden yes. Full `rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)` vs owned suffix `(Fedora 1.82.0-1.fc42)`: hidden yes because the strings differ. The Fedora suffix in the owned packet is a caller string, not `rustc -vV`.

NUL inside `vv` (`fc40\x00suffix`) is kept; still hidden against fc42. Not a rustc parse.

### 3. Swapped argv; not a fingerprint

`086-fc40.rec` then `086-fc42.rec`: hidden yes, rc=1. Specimen-086 is X-then-Y on a shared `target/.rustc_info.json`. The swap is commutative string inequality. There is no cache file, no `rustc_fingerprint` u64, no dirty bit.

Symlink / FIFO / process substitution / filename with a space / CRLF / comments: same owned leftover, rc=1. 10000-char path both sides, different `vv`: hidden yes. Missing `/no/such/fingerhid` / directory / empty file / `/dev/null` / no tabs / JSON / `.rustc_info.json` / unknown field `fingerprint` / missing mtime / BOM / invalid UTF-8: `fingerhid: …` rc=1. `-` as a path is refused (`both records must be paths (not a single stdin)`, rc=1). No args / one arg / extra arg: argparse rc=2. `--help` rc=0.

`.rustc_info.json` / a real rustc binary / `cargo metadata` are unknown fields or not TSV. The caller must already have typed path, mtime, and the two `vv` strings.

## Primitive

Parse two TSV tables of caller-written `path`/`mtime`/`vv` (optional `size`/`birth`); hidden iff the two paths match, the two mtimes match, and the two `vv` strings differ; rc=1 iff hidden. Missing size/birth print `same_size`/`same_birth` as `-` and do not vote. Missing `vv` refuses. `-` as a value refuses.

Nearest ordinary workflow (owned packet, also `demo.sh`):

```text
diff two rustc -vV strings; compare path and mtime
test "$path_a" = "$path_b" && test "$mtime_a" = "$mtime_b" && test "$vv_a" != "$vv_b"
```

On specimen-086 that pair is: same `/usr/bin/rustc`, same clamped mtime, Fedora fc42 vs fc40 in the verbose-version string. fingerhid's load-bearing claim is that naming `hidden_by_fingerprint` is a join those three strings do not already contain.

It is not. Size/birth are spectators. Requiring `vv` only refuses a missing key. Swap is the same bit. Stat of the rustc path / hashing `hash_exe` / reading `.rustc_info.json` / running `rustc -vV` is out of scope and refused.

Observable capability lost if fingerhid vanishes: **none**. The caller already wrote both identities. `test` already says the collision. `printf` of the two `vv` lines already is the demo. Defaulting missing size/birth to a printed `-` is not evidence of `st_size` / birthtime. Wrapping `rustc -vV` plus `stat` to capture path/mtime/verbose-version would be a new harvest (live rustc, out of scope, forbidden here). Sibling fingerid already printed `hidden_by_fingerprint` from the same three equalities and was Honor-KILLed. Do not mutate fingerhid into fingerid to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.”

That is why this is KILL, not MUTATE. The *question* (Cache::load reused `.rustc_info.json` because path+mtime matched while `-vV` would have differed) is a real debugging object. This embodiment does not ask it of a cache file or a compiler. It asks whether three strings the caller typed collide. First KEEP is not protection once that harvest is labels on `a == b` / `c != d`.

Hardcoded ceiling:

- `hidden_by_fingerprint` ↔ path equal and mtime equal and vv unequal
- size/birth optional; print `-` when either side omits; different size/birth still harvest
- missing `vv` / `vv	-` / empty `vv` refuse (parse, not harvest)
- `size	-` / `birth	-` refuse (`not a legal NAME`); sibling fingerid fixtures do not load
- swapped argv harvests the same bit; no X-then-Y cache axis
- garbage `vv` harvests; not a rustc parse
- owned leftover stores Fedora suffixes, not `rustc -vV`
- harvest rc=1; agree rc=0
- `.rustc_info.json` / rustc binary / JSON / BOM / empty stdin refuse
- no rustc, no cargo, no hasher, no `os.stat`
- replica leftover+rc **32/32**; awk of three keys **19/19** Unix TSV harvests

Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection. Same class as Honor-KILLed platid / platident / fingerid: hidden = string equality plus string inequality on caller-typed fields. Do not grow a rustc runner to escape THIN_WRAPPER. Do not send cargo theater back to R1. Do not mint a third rustc_fingerprint CLI. Do not merge onto `main`.

Archive stays under `lineages/candidate-fingerhid/`.

KILL

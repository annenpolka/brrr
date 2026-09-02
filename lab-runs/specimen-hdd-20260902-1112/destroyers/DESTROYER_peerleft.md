# DESTROYER peerleft

Date: 2026-09-02 15:03 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-peerleft/peerleft`

sha256 `0a16edd2e154d26a8de230f20415f9f83470e58637534c635e8baebe34a2e53c` (2988 bytes). No `peerleft` worktree under `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-peerleft/`) and was not merged. Host Python 3.14.5. `bun` is on PATH (`/opt/homebrew/bin/bun` → Cellar 1.4.0) and **was not executed**.

Origin claim (`CANDIDATE.md` / harvest `hdd-bunpeer` / specimen-082 leftover packages identity after `bun remove` vs never-installed optional peer): name leftover `packages` identity when `packages_a` is no and `packages_b` is yes. grep hits `optionalPeers` in both. rc=1 on leftover. Kind: USEFUL_COMPOSITION. Owned packet: never-install has no `packages` entry whose prefix is `"no-deps": ["no-deps@`; after add-then-remove the packages identity remains; the name still appears inside `optional-peer-deps` metadata. Rejected: invented bun add/remove transcripts. Constraint: owned two lock excerpts. No bun.

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.078s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0). That is not enough.

This candidate is a **THIN_WRAPPER** of `name in packages_b and name not in packages_a`. `inspect()` never reads a lockfile prefix, never distinguishes `"no-deps": ["no-deps@` from an `optionalPeers` substring, never looks at `mentioned` when it decides leftover. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on owned / unseen / never-never / after-after / swap (`stdout_eq=True`). A python one-liner of packages-row membership matches the `leftover_identity` row and rc on **17/17** host cases. awk of `$1=="packages"` matches the three load-bearing columns on owned / mentioned-only / packages-both / neither / leftover-without-mention. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-peerleft/peerleft
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-peerleft/fixtures
S082=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-082
```

No merge onto `main`. No bun. Do not grow a `bun.lock` parser or a `"no-deps": ["no-deps@` prefix walk to escape THIN_WRAPPER. Do not send bun theater back to R1.

---

## What still works

Owned pair, unseen `widget` pair, and any other two TSV excerpts whose rows are already `packages NAME` vs `peer` / `optionalPeers` / `mentioned NAME`, **when the question is only membership of `--name` in the second `packages` list and not the first**.

```bash
python3 "$CLI" "$FIX/082-never.rec" "$FIX/082-after-remove.rec" --name no-deps
echo rc=$?
```

```text
name	no-deps
packages_a	no
packages_b	yes
mentioned_a	yes
mentioned_b	yes
leftover_identity	yes
rc=1
```

96 bytes. Stderr empty. Unseen `widget`: same six rows with `name	widget`, rc=1, 95 bytes. Never vs never: `packages_a	no` / `packages_b	no` / `leftover_identity	no`, rc=0. After vs after: `packages_a	yes` / `packages_b	yes` / leftover no, rc=0. Swap (after, never): `packages_a	yes` / `packages_b	no` / leftover no, rc=0. Directional membership, not remove-vs-never.

Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF, Unicode name `依存`: same predicate. 10000 other `packages` rows (~169kB) plus leftover `no-deps`: `leftover_identity	yes`, rc=1, stdout still 96 bytes, ~0.029s. Same 10000 plus `no-deps` on both sides: leftover no, rc=0, ~0.029s. Missing path / directory / invalid UTF-8 / BOM / binary NUL / unknown field: `peerleft: …` rc=1. No args / one arg / missing `--name` / extra positional: argparse rc=2.

That is the whole useful surface. It is also what `name in packages_b and name not in packages_a` already does.

---

## Implementation

`inspect()` in full:

```python
def inspect(first: dict, second: dict, name: str) -> dict:
    a_pkg = name in first["packages"]
    b_pkg = name in second["packages"]
    a_ment = name in first["mentioned"] or a_pkg
    b_ment = name in second["mentioned"] or b_pkg
    leftover = (not a_pkg) and b_pkg
    return {
        "name": name,
        "packages_a": a_pkg,
        "packages_b": b_pkg,
        "mentioned_a": a_ment,
        "mentioned_b": b_ment,
        "leftover_identity": leftover,
    }
```

`inspect.co_names` is `()`. `inspect.co_varnames` is `('first', 'second', 'name', 'a_pkg', 'b_pkg', 'a_ment', 'b_ment', 'leftover')`. dis: two `CONTAINS_OP (in)` on `'packages'`, two more on `'mentioned'` OR-ed with the packages bits, then `UNARY_NOT` of `a_pkg` AND `b_pkg`. There is no prefix, no JSON, no lockfile, no optional-peer slot.

`parse_lock` accepts keys `packages` → packages list, and `peer` / `optionalPeers` / `mentioned` → mentioned list. First tab splits key/value; a second tab in the value is dropped (`rest.split("\t", 1)[0]`). Unknown keys raise. `mentioned_*` is inflated by packages membership. leftover never reads mentioned.

When leftover is yes, `mentioned_b` is always yes (`b_ment = mentioned or b_pkg`). Tests never hit mentioned-only, packages-both, name-not-in-either, extra tabs, stdin, empty first, or origin bytes. Three tests: owned leftover, unseen copy of owned, never vs never.

---

## Attacks

### 1. THIN_WRAPPER of `name in packages_b and name not in packages_a`

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout on the five harvest shapes:

| case | cli_rc | replica_rc | stdout_eq | leftover_thin | packages_a | packages_b |
| --- | ---: | ---: | --- | --- | --- | --- |
| owned never → after | 1 | 1 | True | True | False | True |
| unseen widget | 1 | 1 | True | True | False | True |
| never vs never | 0 | 0 | True | False | False | False |
| after vs after | 0 | 0 | True | False | True | True |
| swap after → never | 0 | 0 | True | False | True | False |

Python one-liner, no `inspect` import, packages rows only:

```bash
python3 -c '
import sys
name=sys.argv[3]
def pkgs(path):
    s=[]
    for raw in open(path, encoding="utf-8"):
        line=raw.strip()
        if not line or line.startswith("#") or "\t" not in line: continue
        k,r=line.split("\t",1)
        if k.strip()=="packages":
            s.append(r.split("\t",1)[0].strip())
    return s
a=pkgs(sys.argv[1]); b=pkgs(sys.argv[2])
print("packages_a", name in a)
print("packages_b", name in b)
print("leftover", (name not in a) and (name in b))
' "$FIX/082-never.rec" "$FIX/082-after-remove.rec" no-deps
```

```text
packages_a False
packages_b True
leftover True
```

Same membership function vs the CLI `leftover_identity` row and rc: **17/17 match**, including mentioned-only, packages-both, name-not-in-either, comments-only, leftover-without-mention, reverse, extra-tab, `/dev/null` first, empty first.

awk of the three load-bearing columns, without mentioned:

```awk
BEGIN{FS="\t"}
FNR==1{file++}
/^#/ {next}
$1=="packages" {
  n=$2
  gsub(/^[ \t]+|[ \t]+$/, "", n)
  if(file==1) a[n]=1
  if(file==2) b[n]=1
}
END{
  leftover = (!(name in a)) && (name in b)
  printf "packages_a\t%s\n", (name in a)?"yes":"no"
  printf "packages_b\t%s\n", (name in b)?"yes":"no"
  printf "leftover_identity\t%s\n", leftover?"yes":"no"
}
```

owned / mentioned-only / packages-both / neither / leftover-without-mention: `awk_eq_cli_loadbearing=True` all five. mentioned columns are not in the awk. They do not vote.

Nearest ordinary workflow, host-executed:

```bash
grep -n no-deps "$FIX/082-never.rec"
grep -n no-deps "$FIX/082-after-remove.rec"
grep -n optionalPeers "$FIX/082-never.rec"; echo never_opt_rc=$?
grep -n optionalPeers "$FIX/082-after-remove.rec"; echo after_opt_rc=$?
```

```text
2:# no-deps appears only in optionalPeers metadata.
3:peer	no-deps
1:# Case B after bun remove no-deps: packages identity remains.
2:packages	no-deps
3:peer	no-deps
2:# no-deps appears only in optionalPeers metadata.
never_opt_rc=0
after_opt_rc=1
```

`demo.sh` says “grep no-deps hits optionalPeers in both”. `grep optionalPeers` on after-remove is rc=1. The never hit is a **comment**. The fixtures already rewrote optional-peer metadata as a `peer` row and the leftover as a `packages` row. grep of the name hits both because the caller wrote the name on both sides. leftover is whether they also wrote `packages` on the second side.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`mentioned_a`, `mentioned_b`) to escape classification. Those rows are `name in mentioned or name in packages`. leftover does not read them.

### 2. Mentioned-only both sides

Host-executed, both files `peer	no-deps`, `--name no-deps`:

```text
name	no-deps
packages_a	no
packages_b	no
mentioned_a	yes
mentioned_b	yes
leftover_identity	no
rc=0
```

Same six rows, rc=0, for `optionalPeers	no-deps` on both sides, for `mentioned	no-deps` on both sides, and for `peer` vs `optionalPeers` mixed. replica `stdout_eq=True`. thin leftover False.

This is the harvest sentence “grep hits both, leftover is the packages identity.” The CLI reports leftover no because there is no `packages` row. The caller already omitted that row. `peer` / `optionalPeers` / `mentioned` are one list. Changing the mention key never changes leftover.

Owned never vs never is the same leftover (`no`, rc=0) with the same mentioned yes/yes. Mentioned-only both sides is never vs never.

### 3. Packages both sides

Both files `packages	no-deps` only, `--name no-deps`:

```text
name	no-deps
packages_a	yes
packages_b	yes
mentioned_a	yes
mentioned_b	yes
leftover_identity	no
rc=0
```

No `peer` line exists. `mentioned_*` is still yes because `a_ment = mentioned or a_pkg`. Packages-and-peer on both sides: identical leftover no, rc=0. After vs after (owned after-remove twice): same leftover no. A name that remains as a packages identity on **both** excerpts — harvest Case C, hard dep still holding `no-deps` — is leftover no. leftover is not “still present after remove”. leftover is “absent from the first list the caller typed, present in the second.”

### 4. Name not in either

`peer	other` vs `packages	other`, `--name no-deps`:

```text
name	no-deps
packages_a	no
packages_b	no
mentioned_a	no
mentioned_b	no
leftover_identity	no
rc=0
```

Comments-only both sides: identical leftover no, mentioned no/no, rc=0. Empty `--name` on owned files: `name	` empty field, leftover no, rc=0. `--name No-Deps` on owned (case): leftover no, mentioned no/no, rc=0. `--name no-deps` against `@scope/no-deps` leftover: leftover no. `--name no-deps` against `packages	no-deps@1.0.0`: leftover no (`packages_b	no`). Query the versioned token: leftover yes.

leftover_identity is the same bit as mentioned-only both sides (`no`, rc=0). The mentioned columns differ (yes/yes vs no/no). leftover does not. Name-not-in-either is not a third class. It is packages membership false on both sides.

### 5. Extra tabs

`parse_lock` takes `rest.split("\t", 1)[0].strip()` as the name. Host-executed against `peer	no-deps` vs the after file named below, `--name no-deps`:

| after line | leftover | rc | packages_b |
| --- | --- | ---: | --- |
| `packages	no-deps	extra` | yes | 1 | yes |
| `packages	no-deps	leftover-id	sha` | yes | 1 | yes |
| `packages	no-deps	` (trailing tab) | yes | 1 | yes |
| `packages		no-deps` (empty first field) | no | 0 | no |

Extra columns after the name are dropped. The leftover bit still fires. An extra tab **before** the name makes the packages identity the empty string; `no-deps` sits in the ignored column; leftover no. Same split the thin wrapper uses.

`--name` with an embedded tab on the owned pair:

```text
name	no-deps	extra
packages_a	no
packages_b	no
mentioned_a	no
mentioned_b	no
leftover_identity	no
rc=0
```

The `name` row is three TSV fields. leftover is no because the query string is not `no-deps`. `packages	no-deps extra` (space, not tab) vs `--name no-deps`: leftover no. Spaces instead of a tab: `peerleft: … expected key<TAB>value`, rc=1, no TSV.

Extra tabs are not an attack the name survives. They are the first-field split.

### 6. Stdin

Owned never body on the pipe:

```text
python3 "$CLI" - "$FIX/082-after-remove.rec" --name no-deps
peerleft: [Errno 2] No such file or directory: '-'
rc=1

python3 "$CLI" "$FIX/082-never.rec" - --name no-deps
peerleft: [Errno 2] No such file or directory: '-'
rc=1

python3 "$CLI" - - --name no-deps     # never body on stdin
peerleft: [Errno 2] No such file or directory: '-'
rc=1
```

`-` is not stdin. Argv-less / one-arg / missing `--name`: argparse rc=2, pipe ignored.

`/dev/stdin` as first with never redirected: owned leftover TSV, rc=1 (one file can be stdin). `/dev/stdin` `/dev/stdin` with one never record on the pipe:

```text
name	no-deps
packages_a	no
packages_b	no
mentioned_a	yes
mentioned_b	no
leftover_identity	no
rc=0
```

First open consumes the pipe; second is empty. leftover no. Concatenating never + `---` + after on that same two-`/dev/stdin` invocation: `peerleft: /dev/stdin:4: expected key<TAB>value`, rc=1, no TSV. Process substitution and FIFO work because `Path.read_text` opens those nodes. Fine as a two-file tool; hostile as a pipe component.

### 7. Mention is a spectator; leftover without mention still fires

`packages	other` vs `packages	no-deps`, no peer lines, `--name no-deps`:

```text
name	no-deps
packages_a	no
packages_b	yes
mentioned_a	no
mentioned_b	yes
leftover_identity	yes
rc=1
```

`mentioned_a	no`. leftover still yes. Harvest leftover is “after remove vs metadata-only mention in the never-installed lock.” This pair has no mention on either side. It is “B has a packages row, A does not.”

`/dev/null` as never vs owned after-remove: same leftover yes, `mentioned_a	no`, rc=1. Empty file as never: same. The never-installed excerpt can be empty and leftover still harvests.

leftover yes always prints `mentioned_b	yes`, even with no mention line, because packages implies mentioned. There is no TSV in which leftover is yes and mentioned_b is no. mentioned_b is not evidence that optionalPeers metadata was present.

Reverse (`packages` only on A, `peer` only on B): leftover no, rc=0. Swap of owned: leftover no. The bit is not symmetric and is not “mentioned on both, packages on one.”

### 8. Origin bytes refuse; the prefix is not parsed

Specimen `leftover_lockfile_split.txt` as never: `peerleft: …:1: expected key<TAB>value`, rc=1. A JSON lock shape `{"packages": {"no-deps": ["no-deps@1.0.0"]}}`: same parse error, rc=1. `peerDependencies	no-deps`: `unknown field 'peerDependencies'`, rc=1. `Packages	no-deps`: `unknown field 'Packages'`, rc=1. UTF-8 BOM: `unknown field '\ufeffpeer'`, rc=1. Invalid UTF-8: codec error, no filename, rc=1. Embedded NUL: `unknown field '\x00\x01packages'`, rc=1.

The harvest presence test is the serialized prefix `"no-deps": ["no-deps@`, because a substring match on `no-deps` also hits `optionalPeers`. Host-executed, after file `packages	"no-deps": ["no-deps@1.0.0"` vs `--name no-deps`:

```text
packages_a	no
packages_b	no
mentioned_a	yes
mentioned_b	no
leftover_identity	no
rc=0
```

The prefix bytes are the **name** token. They do not match `no-deps`. leftover no. The caller must already have split `"no-deps": ["no-deps@` into a `packages	no-deps` row. That split is the product. The CLI reprints it.

### 9. Huge dump; still membership

10000 `packages	pkgN` rows on never plus `peer	no-deps`; same 10000 plus `packages	no-deps` and `peer	no-deps` on after: leftover yes, rc=1, stdout **96** bytes, 0.028s. Same 10000 plus `packages	no-deps` on both sides: leftover no, rc=0, 96 bytes, 0.029s. No cap. No names dumped. The useful bit is still `name in packages_b and name not in packages_a`.

Missing path: `No such file or directory`, rc=1. Directory: `Is a directory`, rc=1. Duplicate `packages` lines including `no-deps`: leftover yes (`in` on a list). `peer` then `packages` in the same after file: leftover yes. Tests never hit duplicates, origin, stdin, extra tabs, mentioned-only, packages-both, or name-not-in-either.

---

## Primitive

Reality-stripped operation: parse two TSV files of `packages NAME` and `peer|optionalPeers|mentioned NAME`; leftover iff `--name` is in the second packages list and not the first; print six TSV rows; rc=1 iff that bit. mentioned columns OR packages membership into a spectator boolean.

Nearest ordinary workflow: `grep '^packages'` on two files, or `python3 -c 'print(name not in a and name in b)'` on the packages names the caller already labeled, or `awk '$1=="packages"'` as above. Observable capability lost if peerleft vanishes: **none**. The two excerpts already are the input. The leftover-vs-mention join is still a hand comparison after the caller typed `packages` vs `peer`. grep of the name hits both because the fixtures contain the name on both sides.

That is why this is KILL, not MUTATE. The *question* (after `bun remove`, is `no-deps` still a `packages` identity, or only an `optionalPeers` mention the way the never-installed lock was — grep hits both) is a real debugging object. This embodiment does not ask it of a lockfile. It asks `name in packages_b and name not in packages_a` on caller-labeled tokens. Adding a `"no-deps": ["no-deps@` prefix walk, or ingesting `bun.lock` JSON, would be implementing the bun theater the harvest rejected, and would be a new harvest, not a patch of this 92-line `in`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Hardcoded ceiling:

- leftover iff packages membership gap B\A; mentioned does not vote
- mentioned_* inflated by packages, so leftover yes ⇒ mentioned_b yes
- leftover yes with mentioned_a no (`/dev/null` first, empty first, packages-only after)
- mentioned-only both sides / packages both sides / name not in either: leftover no, same bit
- `peer` / `optionalPeers` / `mentioned` are one list
- extra tab after the name is dropped; extra tab before the name makes the identity `""`
- `--name` with a tab splits the `name` row and is a different query
- `-` is not stdin; two `/dev/stdin` is empty-second leftover no
- origin lock / JSON / `peerDependencies` / `Packages` / BOM / prefix-as-name refuse or miss
- `no-deps@1.0.0` is not `no-deps`; `No-Deps` is not `no-deps`
- 10k-row leftover still 96-byte sticker, ~0.03s
- rc=1 on leftover **or** parse/IO; argparse rc=2 on missing argv
- Dreamer bun add/remove was rejected; this is that leftover, reduced to the harvest sentence as `in`

Honor KILL. Dreamer ancestry is not protection.

Do not grow a bun.lock parser or a packages-prefix matcher to escape THIN_WRAPPER. Do not merge this join onto `main`. No bun.

---

KILL

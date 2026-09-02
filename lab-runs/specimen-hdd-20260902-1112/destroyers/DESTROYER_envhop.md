# DESTROYER envhop

Attacked: 2026-09-02 14:01 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envhop/envhop`

sha256 `5fdecbf6840c209f20308c697742ab357fedc97871350a3857ddbf8390c33858` (2649 bytes). No worktree copy. Parent tree is coordinator-only; this object was not merged onto `main`.

Origin claim (hdd-envdrop / specimen-068): name env keys dropped **because** they are not POSIX identifiers. Classification: USEFUL_COMPOSITION. REALITY.md already names the nearest operation: “diff two env dumps. Delta: dropped_invalid TEST-VAR vs survived_invalid INPUT-FOO.”

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envhop/envhop
FIX=$CLI/../fixtures
```

Host tests: `python3 -m unittest discover -s …/tests -v` → 3/3 OK, rc=0.

This candidate is a **THIN_WRAPPER**. `inspect()` is set-difference of caller-supplied keys plus `re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")`. An awk reconstruction of that join is **byte-identical** to envhop on the owned fixture and on a mixed drop/survive fixture (`cmp` rc=0). Values are parsed and discarded. No process is exec'd. Decision: **KILL**.

---

## What still works

Owned packet (hyphen name present before, absent after) and the unseen “invalid survived” fixture print the rows the tests assert. Missing file → `envhop: [Errno 2] No such file or directory: '/no/such.env'` rc=1. Line without `=` → `envhop: <file>:1: expected NAME=VALUE` rc=1. Empty name `=value` → `envhop: <file>:1: empty name` rc=1.

```bash
python3 "$CLI" "$FIX/068-before.env" "$FIX/068-after.env"
python3 "$CLI" "$FIX/unseen-before.env" "$FIX/unseen-after.env"
```

```text
invalid_posix	TEST-VAR
dropped	TEST-VAR
dropped_invalid	TEST-VAR
survived_invalid	none
kept	PATH	HOME

invalid_posix	INPUT-FOO
dropped	none
dropped_invalid	none
survived_invalid	INPUT-FOO
kept	FOO	INPUT-FOO	_ok
```

That is the whole useful delta. It is also what `diff` plus one identifier regex already does. Attacks below break the “because” claim, or show the primitive cannot grow.

---

## Implementation

`inspect()` in full, with the unused values left visible:

```text
invalid = [k for k in before if not POSIX.match(k)]
dropped = [k for k in before if k not in after]
dropped_invalid = [k for k in dropped if k in set(invalid)]
kept = [k for k in before if k in after]
survived_invalid = [k for k in invalid if k in after]
```

`inspect.__code__.co_names` is `('POSIX', 'match', 'set')`. Two before-maps whose keys match and whose values differ (`A=1` vs `A=999`, `B-X=2` vs `B-X=zzz`) produce **equal** inspect dicts. Empty vs nonempty is presence-only.

### 1. Valid names dropped too (not identifier-caused)

The harvest is “dropped **because** they are not POSIX identifiers.” Intersection is not because. Drop valid `PATH`/`FOO` together with hyphen `TEST-VAR`:

```bash
printf 'PATH=/usr/bin\nHOME=/root\nFOO=1\nTEST-VAR=123\n' > /tmp/envhop-destroyer/validdrop-before.env
printf 'HOME=/root\n' > /tmp/envhop-destroyer/validdrop-after.env
python3 "$CLI" /tmp/envhop-destroyer/validdrop-before.env /tmp/envhop-destroyer/validdrop-after.env
comm -23 <(awk -F= '{print $1}' /tmp/envhop-destroyer/validdrop-before.env | sort) \
         <(awk -F= '{print $1}' /tmp/envhop-destroyer/validdrop-after.env | sort)
```

```text
invalid_posix	TEST-VAR
dropped	PATH	FOO	TEST-VAR
dropped_invalid	TEST-VAR
survived_invalid	none
kept	HOME
```

`comm` lists `FOO`, `PATH`, `TEST-VAR`. envhop still prints `dropped_invalid	TEST-VAR` as if the hyphen caused the hop. `PATH` and `FOO` are valid identifiers. They left for some other reason. The label does not say so.

Mixed hop — valid drop, invalid drop, invalid survive, valid keep, plus an added key:

```text
# before: PATH HOME FOO BAR TEST-VAR INPUT-FOO KEEP-ME
# after:  PATH HOME FOO INPUT-FOO NEW
invalid_posix	TEST-VAR	INPUT-FOO	KEEP-ME
dropped	BAR	TEST-VAR	KEEP-ME
dropped_invalid	TEST-VAR	KEEP-ME
survived_invalid	INPUT-FOO
kept	PATH	HOME	FOO	INPUT-FOO
```

`BAR` (valid) is dropped and is **not** in `dropped_invalid`. `KEEP-ME` (invalid) is. `INPUT-FOO` (invalid) survived. `NEW` is only in after and is invisible. The four rows are four independent filters. Nothing names a cause.

Host dash reproduces the same hole on a **real** POSIX-identifier hop that also unsets a valid name:

```bash
env -i PATH=/usr/bin:/bin HOME=/root FOO=1 'TEST-VAR=123' 'INPUT-FOO=bar' \
  /bin/dash -c 'unset FOO; /usr/bin/printenv' | sort > after
```

```text
invalid_posix	INPUT-FOO	TEST-VAR
dropped	FOO	INPUT-FOO	TEST-VAR
dropped_invalid	INPUT-FOO	TEST-VAR
survived_invalid	none
kept	HOME	PATH
```

`FOO` was `unset`. `TEST-VAR`/`INPUT-FOO` were identifier-dropped by dash. envhop cannot tell them apart beyond “hyphen ∩ missing.” Dash also **added** `PWD=/Users/…/brrr`. envhop has no added-keys row.

### 2. Invalid that survived

Unseen fixture already: `INPUT-FOO` stays, `dropped_invalid none`. Digit-start `0BAD` also survives POSIX-invalid:

```bash
printf 'OK=1\nINPUT-FOO=bar\n0BAD=x\nTEST-VAR=1\n' > surv-before.env
printf 'OK=1\nINPUT-FOO=bar\n0BAD=x\n' > surv-after.env
python3 "$CLI" surv-before.env surv-after.env
```

```text
invalid_posix	INPUT-FOO	0BAD	TEST-VAR
dropped	TEST-VAR
dropped_invalid	TEST-VAR
survived_invalid	INPUT-FOO	0BAD
kept	OK	INPUT-FOO	0BAD
```

Direct `printenv` (execve, no shell) keeps hyphen names. Dash drops them. Observed on this host, no pnpm:

```text
# env -i … printenv          → FOO HOME INPUT-FOO PATH TEST-VAR
# env -i … dash -c printenv  → FOO HOME PATH  (+ PWD)
# env -i … python3 -c 'print(os.environ.get("TEST-VAR","MISSING"))' → 123
# env -i … dash -c 'printenv TEST-VAR'; echo rc → rc=1
```

envhop before vs direct: `dropped none`, `survived_invalid INPUT-FOO TEST-VAR`. before vs dash: `dropped_invalid INPUT-FOO TEST-VAR`. That is the specimen mechanism. The CLI did not hop. The caller dumped two maps and asked for set algebra.

Same file twice (no hop at all) still lists `invalid_posix TEST-VAR` and `survived_invalid TEST-VAR`. Invalidity is a property of the before spelling, not of a hop.

### 3. Empty values

Values are dead after `parse_env`. Empty assignment is presence.

```bash
printf 'PATH=/usr/bin\nEMPTY=\nTEST-VAR=\nFOO=\n' > empty-before.env
printf 'PATH=/usr/bin\nEMPTY=\nFOO=now-nonempty\n' > empty-after.env
python3 "$CLI" empty-before.env empty-after.env
```

```text
invalid_posix	TEST-VAR
dropped	TEST-VAR
dropped_invalid	TEST-VAR
survived_invalid	none
kept	PATH	EMPTY	FOO
```

`EMPTY=` stays empty and is `kept`. `FOO=` → `FOO=now-nonempty` is `kept`. `TEST-VAR=` missing after is a key drop, same as `TEST-VAR=123` missing after. Both-sides `ONLY=` → `kept ONLY`, all other rows `none`. Two empty files → five `none` rows, rc=0.

`line = raw.strip()` also eats trailing value spaces: `TEST-VAR=123  ` parses as `'123'`. Leading spaces on the line are stripped so `  TEST-VAR=123` becomes a valid name. Spaces **around** `=` do the opposite (`TEST-VAR =123` → name `'TEST-VAR '`, invalid_posix, query `TEST-VAR` misses).

Quoted empty `TEST-VAR=""` is a two-character value, not empty. Keys still match; values still unused.

### 4. export PREFIX

dotenv `export NAME=VALUE` is a silent wrong identity, rc=0. After `strip`, the name is `export PATH` / `export TEST-VAR` (space → invalid POSIX).

```bash
printf 'export PATH=/usr/bin\nexport TEST-VAR=123\nHOME=/root\n' > export-before.env
printf 'PATH=/usr/bin\nHOME=/root\n' > export-after.env
python3 "$CLI" export-before.env export-after.env
```

```text
invalid_posix	export PATH	export TEST-VAR
dropped	export PATH	export TEST-VAR
dropped_invalid	export PATH	export TEST-VAR
survived_invalid	none
kept	HOME
```

`PATH` and `TEST-VAR` are not keys. A reader looking for the specimen hyphen drop will see `export TEST-VAR` instead. Both-sides still prefixed: `HOME` (unprefixed) is the only `dropped` row; `export PATH` / `export TEST-VAR` are `survived_invalid`. Parser: `parse_env("export TEST-VAR=123\n") == {'export TEST-VAR': '123'}`.

### 5. Windows names

Windows env is case-insensitive and allows `ProgramFiles(x86)` and empty-name drive vars (`=C:`, `=ExitCode`). envhop is case-sensitive first-`=` partition plus POSIX regex.

```text
# before: Path PATH ProgramFiles(x86) USERNAME USERPROFILE OS INPUT-FOO TEST-VAR PATHEXT NUMBER_OF_PROCESSORS
# after:  PATH USERNAME USERPROFILE OS NUMBER_OF_PROCESSORS
invalid_posix	ProgramFiles(x86)	INPUT-FOO	TEST-VAR
dropped	Path	ProgramFiles(x86)	INPUT-FOO	TEST-VAR	PATHEXT
dropped_invalid	ProgramFiles(x86)	INPUT-FOO	TEST-VAR
survived_invalid	none
kept	PATH	USERNAME	USERPROFILE	OS	NUMBER_OF_PROCESSORS
```

- `Path` vs `PATH`: `Path` is a **valid** POSIX identifier and is `dropped`, not `dropped_invalid`. Case-fold looks like a valid-name drop. Added `PATH` is invisible.
- `ProgramFiles(x86)`: parens → invalid. Real Windows name.
- `PATHEXT`: valid POSIX spelling, dropped for a non-identifier reason.
- Isolated case hop `Path=…` → `PATH=…`: `dropped Path`, `dropped_invalid none`, `kept FOO`.

Windows `=C:=C:\` (empty name, used by `cmd` for drive cwd):

```text
envhop: /tmp/envhop-destroyer/wineq-before.env:2: empty name
rc=1
```

A `cmd /c set` dump cannot be ingested.

### 6. Unicode

ASCII `[A-Za-z_]` only. NFC `CAFÉ`, NFD `CAFÉ` (U+0301), CJK `変数`, `FOO😀`, zero-width `FOO\u200bBAR` are all `invalid_posix` and, when missing after, `dropped_invalid`. `_ok` and `PATH` kept.

UTF-8 BOM glues to the first name. `\ufeffPATH` ≠ `PATH`:

```bash
# bom-before: \ufeffPATH=/usr/bin\nTEST-VAR=123\nHOME=/root
# bom-after:  PATH=/usr/bin\nHOME=/root
invalid_posix	\ufeffPATH	TEST-VAR
dropped	\ufeffPATH	TEST-VAR
dropped_invalid	\ufeffPATH	TEST-VAR
survived_invalid	none
kept	HOME
```

`PATH` is a valid identifier present after. The parser reports it as dropped-invalid. That is a valid name dropped by the tool, not by a hop.

Invalid UTF-8 is a clean one-line error (not a traceback): `envhop: 'utf-8' codec can't decode byte 0xff in position 18: invalid start byte` rc=1. CRLF `splitlines` works on the owned hyphen drop.

### 7. Duplicate keys

Last-wins value, first-seen order, silent, rc=0.

```text
TEST-VAR=first
PATH=/usr/bin
TEST-VAR=second
TEST-VAR=third
```

parses as `{'TEST-VAR': 'third', 'PATH': '/usr/bin'}`. One dropped hyphen. `PATH=a` then `PATH=b` vs `PATH=c`: `kept PATH`, values ignored. `FOO=1` then `FOO=` last-wins empty; empty is still presence. Two `FOO-BAR=` lines vs one: `survived_invalid FOO-BAR`, `dropped none`.

### 8. THIN_WRAPPER of diff plus regex

Nearest ordinary workflow on the owned packet:

```bash
diff -u "$FIX/068-before.env" "$FIX/068-after.env"
# -TEST-VAR=123

comm -23 <(awk -F= '{print $1}' "$FIX/068-before.env" | sort) \
         <(awk -F= '{print $1}' "$FIX/068-after.env" | sort)
# TEST-VAR

awk -F= '$1 !~ /^[A-Za-z_][A-Za-z0-9_]*$/ {print $1}' "$FIX/068-before.env"
# TEST-VAR
```

Full reconstruction (first-seen key order, skip blanks/`#`, POSIX regex, five TSV rows) compared with envhop:

```text
068 cmp_rc=0 (byte-identical)
mix cmp_rc=0 (byte-identical)
```

Owned envhop stdout (repr):

```text
b'invalid_posix\tTEST-VAR\ndropped\tTEST-VAR\ndropped_invalid\tTEST-VAR\nsurvived_invalid\tnone\nkept\tPATH\tHOME\n'
```

awk stdout: same bytes. mix fixture: same bytes as envhop, including `dropped BAR TEST-VAR KEEP-ME` and `survived_invalid INPUT-FOO`.

There is no remainder. `dropped_invalid` is `comm` of `dropped` and `invalid_posix`. `survived_invalid` is invalid keys still in after. `fmt_list` writes `none` when a list is empty.

### Other implementation holes (do not save it)

**`none` sentinel collision.** Dropping a key literally named `none` vs dropping nothing, PATH kept in both:

```text
# none=1 then missing          # PATH only, both sides
invalid_posix	none            invalid_posix	none
dropped	none                dropped	none
dropped_invalid	none            dropped_invalid	none
survived_invalid	none        survived_invalid	none
kept	PATH                    kept	PATH
```

Byte-identical. Tests assert `rows["survived_invalid"] == ["none"]` on the empty case, so they baked the collision in.

**Tab in a name is an unescaped TSV delimiter.** `FOO\tBAR=1` renders as two fields `FOO` and `BAR` on every list row.

**Added keys / value changes.** `FOO=old` → `FOO=new` plus `ADDED=1`: `dropped none`, `kept PATH TEST-VAR FOO`. The value hop and the new key are not rows.

**Huge.** 20 000 `K{i}` keys plus one hyphen drop: 5 output lines, 128 987 bytes, ~0.03s. `kept` is a single tab-separated line of K0…K19999 PATH. No cap.

**Pipes.** No stdin flag. `/dev/stdin` as the before path works (owned hyphen drop). No-args: argparse rc=2. Directory: `Is a directory` rc=1.

---

## Primitive

Reality-stripped operation: parse `NAME=VALUE` lines into two dicts; print key set-difference and a POSIX-identifier regex.

Nearest ordinary workflow: `diff` two env dumps, or `comm` on `cut -d= -f1`, plus `grep -vE '^[A-Za-z_][A-Za-z0-9_]*$'`. On specimen-068 that pair is `TEST-VAR` / `TEST-VAR`. envhop’s load-bearing claim is that naming `dropped_invalid` is a join those two already contain.

It is not. `dropped_invalid` is their intersection. `survived_invalid` is invalid ∩ after. `kept` is before ∩ after. Values never enter. No exec, no shim, no `printenv` of a child, no inode of `command -v node`. The caller already typed both maps.

Observable capability lost if envhop vanishes: none. `diff -u` already shows the hyphen line gone. The regex already says the name is not a POSIX identifier. Wrapping `dash -c` / `python3 -c` to *observe* a hop would be a new harvest (actual before/after of an exec), not a patch of this 80-line file. Constitution: a THIN_WRAPPER does not gain exotic exec features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” This run already killed conventional envdiff (wild-001) and arithmetic-label THIN_WRAPPER (`startimer`). Same extinction class.

Hardcoded ceiling:

- “Because” is correlation. Valid names dropped in the same hop stay in `dropped` and never falsify `dropped_invalid`.
- Invalid that survived is set membership, including “same file twice.”
- Empty values, value edits, and added keys are invisible.
- `export NAME`, BOM, `NAME = v`, Windows `Path`/`=C:` / `ProgramFiles(x86)` are parser identity bugs or hard errors, not hop observations.
- Duplicate keys last-win silently. `none` is both empty and a name. Tabs in names break TSV.
- Demo.sh’s “nearest existing operation” is already `diff two env dumps`. The join in parentheses is the regex.

Do not mutate this into an exec tracer. Do not re-dream pnpm docker. Do not transfer onto envlayers (already FAIL: layers ≠ hop maps). Archive stays under `lineages/candidate-envhop/` for the record.

Honor KILL.

KILL

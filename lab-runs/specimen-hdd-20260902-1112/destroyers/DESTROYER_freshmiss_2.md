# DESTROYER freshmiss 2

Date: 2026-09-02 15:48 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0384
Worker: destroyer-freshmiss-2

Target (archive; mutate-freshmiss-2 already landed FRESH-but-stub):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-freshmiss/freshmiss`

sha256 `8ee31b606f217e053250d2b491b42597a855bd462b75f1e08bfc877f35d62f1c` (7787 bytes, 253 lines).
Worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-freshmiss-freshmiss/freshmiss/freshmiss` is byte-identical (`cmp` rc=0).
HEAD `96379eb mutate freshmiss: FRESH-but-stub for leftover empty extra` on `specimen-hdd/candidate-freshmiss-freshmiss`.
Parent `main` is `432f954`; `git show HEAD:freshmiss` fatal (not in that tree). Host Python 3.14.5.
unittest 14/14 (`Ran 14 tests in 0.279s` `OK`). `demo.sh` still names `out.sbom` as `FRESH-but-missing`. No merge onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-fingerprint` / specimen-011): given two builds, say whether freshness identity omitted a requested extra output (FRESH-but-missing), and name that extra as `omitted_from_identity`. Kind: USEFUL_COMPOSITION. specimen-005 is cargo origin-only. Mutate.md also queued env-omitted (022), flag-omitted (024), and leftover stub (071). Only the stub field landed.

First destroyer (`DESTROYER_freshmiss.md`) **MUTATE**: `omitted_from_identity` is requested-minus-present, not extra-outside-the-key; `none` collides; forgotten `present` is a false miss; `exists()` is completeness; only exact `FRESH` is a hit; `identity-changed` drops the extra; rc=0 on the harvest miss; native log is not an input. Kill condition written there: if the mutation cannot do (1)+(3)+(7), a later destroyer should KILL. First MUTATE is not protection.

Mutate job-0328 (`MUTATE.md` / commit `96379eb`) added `bytes NAME 0` → verdict `FRESH-but-stub`. Env omitted and flag omitted were not implemented (`unknown field 'env'` / `'flag'`, rc=1). (1)+(3)+(7) were not implemented.

This candidate is a **THIN_WRAPPER of two identity hashes plus extra-stub vs produced**. `same_identity` is `first.identity == second.identity` on caller-typed strings. `FRESH-but-missing` is that equality AND `second.status == "FRESH"` AND `requested - present`. `FRESH-but-stub` is extra present AND `sizes.get(name, -1) == 0`. `FRESH-complete` is extra present AND size not 0 (including a directory of size 64 and `/etc/passwd`). Independent reconstruction that does not import freshmiss is **byte-identical** on 63/63 host cases (`stdout_eq=True`, `rc_eq=True`). Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-freshmiss/freshmiss
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-freshmiss/tests/fixtures
```

Host-executed against the archive. Worktree was not edited. Do not grow a cargo fingerprint / uv key / cache hasher / `out.sbom` reader to escape THIN_WRAPPER. Do not send cachetool theater back to R1. Sibling `stubextra` was Honor-KILLed for extra-present vs extra-omitted on caller-labeled stubs; this leftover is that cut plus two hashes.

---

## What still works

The owned fixture pair, and any other two records the caller has already filled with `status`, `identity`, `requested`, and `present` (or `bytes NAME 0`, or a directory `--dir` can `exists()`).

```bash
python3 "$CLI" "$FIX/specimen-011-first.rec" "$FIX/specimen-011-second.rec"
echo rc=$?
```

```text
verdict	FRESH-but-missing
identity	9280cc7e16e9
same_identity	true
first_status	BUILT
second_status	FRESH
requested_extra	out.sbom
missing	out.sbom
stub	none
omitted_from_identity	out.sbom
rc=0
```

`--dir` overrides a lying `present	out.sbom` when the file is absent. `bytes	out.sbom	0` is `FRESH-but-stub`. `bytes	out.sbom	12` is `FRESH-complete`. Tests 14/14. Demo still prints the harvest row (plus `stub	none`).

That is the whole useful delta. It is also two equal identity strings plus `requested - present`, with a size==0 branch for leftover extra.

Nearest ordinary workflow, host-executed on the owned records:

```text
awk -F'\t' '$1=="identity"{print $2}' first.rec   # 9280cc7e16e9
awk -F'\t' '$1=="identity"{print $2}' second.rec  # 9280cc7e16e9
same_hash=true second_status=FRESH
awk_extra out.sbom
awk_missing out.sbom
awk_verdict FRESH-but-missing
awk_omitted out.sbom
```

`demo.sh` already prints `first BUILT extra_exists False key 9280cc7e16e9` / `second FRESH … same_key True` and `ls` of the extra path (`missing_check out.sbom: absent`) before the CLI runs. The CLI will not parse that log.

---

## Implementation

Load-bearing body (`compare`):

```python
extra = [name for name in second.requested if name not in set(first.requested)]
missing = second.missing   # requested not in present
stubs = [
    name
    for name in extra
    if name in set(second.present) and second.sizes.get(name, -1) == 0
]
same = first.identity == second.identity
if not same:
    verdict = "identity-changed"; omitted = []
elif second.status == "FRESH" and missing:
    verdict = "FRESH-but-missing"; omitted = list(missing)
elif second.status == "FRESH" and stubs:
    verdict = "FRESH-but-stub"; omitted = list(stubs)
elif second.status == "FRESH":
    verdict = "FRESH-complete"; omitted = []
else:
    verdict = "rebuilt"; omitted = []
```

`compare.co_names` is `('requested', 'set', 'missing', 'present', 'sizes', 'get', 'identity', 'status', 'list')`. No `hashlib`, no cargo, no uv, no `is_file`. Identity is opaque string equality of two caller hashes. Stub is `sizes.get(name, -1) == 0` on extras that are already in `present`. Missing still wins over stub.

`observe_present` still uses `path.exists()` and, when true, `stat().st_size`. A directory occupying `out.sbom` (size 64, `is_file False`) is `FRESH-complete`. `/dev/null` symlink (size 0, `is_char_device True`) is `FRESH-but-stub`. Absolute `/etc/passwd` under `--dir` is `FRESH-complete`.

---

## 1. THIN_WRAPPER of two hashes

`same_identity` is `first.identity == second.identity`. The CLI does not compute a freshness key. The owned 12-char string `9280cc7e16e9` is already in both `.rec` files (and already printed by `cache_build.py` as `key`).

Same first record. Second identical except the identity string:

| second identity | same_identity | verdict | omitted_from_identity |
| --- | --- | --- | --- |
| `k` (same) | true | FRESH-but-missing | out.sbom |
| `OTHER` | false | identity-changed | none |
| `k` + U+200B | false | identity-changed | none |
| `k\x00x` | false | identity-changed | none |

When the two hashes differ, the extra is still absent and still in `missing`, but `omitted_from_identity` is `none`. The harvest question (which requested extra is outside this identity) is dropped because two strings were unequal. First destroyer already named this. It was not mutated.

Swap of the owned pair (second file first): `rebuilt`, `requested_extra none`, rc=0. Argv order is the time axis. Two hashes still match; status of the second argv is `BUILT`, so the FRESH branch never runs.

Independent reconstruction of parse + `exists()` observe + the `compare` / `format_report` above (no import of the CLI module) is **byte-identical stdout and rc on 63/63** host cases: owned 011, swap, same file twice, FRESH-complete, stub 0, produced 12, missing-wins-over-stub, vanished primary, extra-present-orig-gone, filename `none`, forgotten present, empty `present<TAB>`, identity-changed, rebuilt, `fresh`/`Fresh`/`CACHED`/`HIT`/`UP-TO-DATE`/`SUCCESS`/`FRESH ` / extra tab on status, duplicate status last-win, zwsp, `./out.sbom`, space-split, three extras, unicode extra, unknown `env`/`flag`/`magic`, `--dir` lying present / 0-byte stub / produced / directory / broken symlink / `/dev/null` / not-a-directory, identity-changed+stub, stub-on-primary, bytes 0 but not present, bytes -1 / 1, comment-drops-extra, CRLF, missing status, empty file, native log, two hashes same/differ, first-dir, NUL identity, bytes on unrequested name, rebuilt-with-stub, `fresh`+stub, `CACHED`+stub.

No mismatches.

Unix analog of the owned harvest is two hash prints plus set-difference of `requested` vs `present`. That analog's `awk_verdict FRESH-but-missing` / `awk_omitted out.sbom` is the CLI row.

---

## 2. extra-stub vs produced

The mutate leftover is one integer on a name the caller already listed as present.

Same first record, same two hashes, same `FRESH`, same `requested	out.bin	out.sbom`:

| second extra | bytes | verdict | stub | omitted_from_identity | rc |
| --- | --- | --- | --- | --- | --- |
| present | 0 | **FRESH-but-stub** | out.sbom | out.sbom | 0 |
| present | 12 | **FRESH-complete** | none | none | 0 |
| present | (field omitted; default -1) | FRESH-complete | none | none | 0 |
| present | 1 | FRESH-complete | none | none | 0 |
| present | -1 | FRESH-complete | none | none | 0 |
| absent | (none) | FRESH-but-missing | none | out.sbom | 0 |
| present stub + another extra absent | 0 | **FRESH-but-missing** (missing wins) | out.sbom | out.cdx | 0 |

Independent extra-stub vs produced table (no CLI):

```text
stub0  verdict FRESH-but-stub     stub out.sbom  produced none     missing none
prod12 verdict FRESH-complete     stub none      produced out.sbom missing none
nosize verdict FRESH-complete     stub none      produced none     missing none
miss   verdict FRESH-but-missing  stub none      produced none     missing out.sbom
```

`--dir` observed 0-byte `out.sbom`: `FRESH-but-stub`, rc=0. `--dir` observed 9-byte file: `FRESH-complete`, rc=0. `--dir` directory occupying `out.sbom` (`is_dir True`, `is_file False`, size 64): **FRESH-complete** — a directory is "produced" because size is not 0. `--dir` symlink to `/dev/null` (`is_file False`, `is_char_device True`, size 0): **FRESH-but-stub**. Stub vs produced is `st_size == 0`, not "this extra was written as a hashing side effect."

`CACHED` + `bytes 0`: `rebuilt`, stub still `out.sbom`, omitted `none`, rc=0. Stub without exact `FRESH` is not the harvest. `fresh` lowercase + missing extra: `rebuilt`, omitted `none`. Hit vocabulary is still one token.

TRANSFER_s071_freshmiss.md already recorded the pre-mutation fact: extra present, so `FRESH-but-missing` fails; the miss is leftover empty bytes. The mutate added a `bytes` field so the caller can type `0`. That is extra-stub vs produced on a label. Sibling `stubextra` was Honor-KILLed for `extra_exists` plus `extra_bytes==0`. This leftover is that integer on `requested`/`present` names, gated by two hashes and exact `FRESH`.

---

## 3. First MUTATE leftovers (1)+(3)+(7) still hold

First destroyer required: (1) `omitted_from_identity` = missing ∩ requested_extra; (3) omitting `present` is an error, `present<TAB>` is empty; (7) rc=1 on `FRESH-but-missing`. None of those landed.

Vanished primary, no extra requested:

```text
verdict	FRESH-but-missing
requested_extra	none
missing	out.bin
omitted_from_identity	out.bin
rc=0
```

No extra was requested. The cache key did not omit `out.sbom`. A file that was in the first identity vanished after a hit. Still this verdict.

Extra present, original gone:

```text
verdict	FRESH-but-missing
requested_extra	out.sbom
missing	out.bin
omitted_from_identity	out.bin
```

The extra the tool exists to name is present. `omitted_from_identity` names the original instead.

Forgotten `present` (no dir): every requested name is missing, harvest fires, rc=0. `present<TAB>`: `expected key<TAB>value`, rc=1. Still no legal empty present list except omitting the field, which is the false miss.

`FRESH-but-missing` is still rc=0. Fine as a printer; hostile as a pipe predicate. `test -e out.sbom` is rc=1 on the owned miss.

Filename `none` missing: all three list columns print `none`; only `verdict` differs from the present case. Tests split on tab and compare `["none"]`, so they cannot see it.

MUTATE.md items 1 and 2 (env omitted / flag omitted) refuse as unknown fields:

```text
freshmiss: …/env.rec:5: unknown field 'env'     rc=1
freshmiss: …/flag.rec:5: unknown field 'flag'   rc=1
```

Native fixture log still `expected key<TAB>value`, rc=1. `-` is not stdin. Absolute `/etc/passwd` under `--dir`: `FRESH-complete`, rc=0. Enough `../` to `/etc/passwd`: `FRESH-complete`, rc=0. `--dir` is not a root.

---

## Primitive

Reality-stripped operation: parse two TSV maps; `same_identity` is string equality of two `identity` hashes; if `second.status == "FRESH"` and `requested - present` nonempty, print `FRESH-but-missing` and put that difference in `omitted_from_identity`; else if an extra is present with `bytes==0`, print `FRESH-but-stub`; else if FRESH, `FRESH-complete`; else `rebuilt`; rc=0.

Nearest ordinary workflow: the fixture already prints two keys and `extra_exists False`. `ls` of the extra path shows absence. `test -s` names empty present extra. awk of `identity` equality plus `requested` minus `present` plus `bytes==0` names missing vs stub vs produced. Observable capability lost if freshmiss vanishes: **none**. The harvest question (same freshness identity, FRESH, requested extra absent — treat that as a miss, not a successful hit) is real. This embodiment asks it of two hashes and a set-difference the caller already typed. The 071 leftover asks extra-stub vs produced of a size integer the caller already typed.

That is why this is KILL, not MUTATE. First MUTATE survived because the join was still a debugging object `ls` will not emit, and asked for (1)+(3)+(7). Those did not land. The stub field that did land is extra-stub vs produced. Adding a cargo unit-key reader / uv env-component list / fingerprint reconstruction would be implementing the theater the harvest rejected, and would be a new harvest, not a patch of two-string equality. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Honor KILL if two hashes / extra-stub vs produced.

Hardcoded ceiling:

- `same_identity` ↔ two caller identity strings equal
- `FRESH-but-missing` ↔ that equality AND exact `FRESH` AND `requested - present` (including vanished primaries and forgotten `present`)
- `FRESH-but-stub` ↔ extra present AND `sizes.get(name,-1)==0`; missing still wins
- `FRESH-complete` ↔ extra present AND size not 0, including directories (size 64) and `/etc/passwd` via `exists()`
- `omitted_from_identity` is all missing names, not missing ∩ extra; `none` on identity-changed even when extra is absent
- `none` means both empty and the filename `none`
- only exact `FRESH` is a hit; `CACHED`/`fresh`/`HIT` plus stub are `rebuilt`
- rc=0 on harvest miss / stub / complete / identity-changed
- native `first BUILT extra_exists … key` log is not an input; demo.sh already contains the extra name
- env/flag omitted were never fields
- no hashlib, no cargo, no uv, no `is_file`

Do not grow a cache hasher to escape THIN_WRAPPER. Do not merge this join onto `stubextra` or onto `main`. Honor KILL. Dreamer ancestry is not protection. First MUTATE is not protection.

Archive stays under `lineages/candidate-freshmiss/`.

---

KILL

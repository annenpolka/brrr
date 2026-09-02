# DESTROYER swallowecho 2

Date: 2026-09-02 16:09 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0389 (worker destroyer-swallowecho-2, CLAIMED 15:40, no mutation landed)

Target (archive, bytes unchanged since first destroyer):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-swallowecho/swallowecho`

sha256 `f93554d8a79a5f0018900976b0892da795cd222f03409b32318a9d2b6463a534` (21496 bytes). **IDENTICAL** to `DESTROYER_swallowecho.md`. No `MUTATE.md`. Parent `main` is `432f954`; not merged. Host Python 3.14.5. No Bazel. No Actions runner.

First destroyer **MUTATE**. Required (1) swallow is step-status, not inner boolean rescue; (2) do not `ran 0` unimplemented options; (3) every swallow site is a row. If mutation cannot do (1)+(2)+(3), later destroyer should KILL. Mutation never queued. Bytes unchanged. First MUTATE is not protection. Decision: **KILL**.

CLI:

```text
CLI=lineages/candidate-swallowecho/swallowecho
```

Host-executed against the archive. Do not grow a GitHub Actions runner. Do not send leftover-status theater back to R1.

---

## What still works

`false || echo hid` under a then-body still names swallow yes / swallowed false / hid_by echo hid, rc=0. That is the harvest analogue. `bash -x` plus `$?` already names it.

---

## Honor-KILL leftovers (still fire)

### 1. Inner boolean rescue is still `swallow yes`

```bash
python3 "$CLI" 'if false || true; then echo then; fi'
```

```text
step_status	0
swallow	yes
swallowed	false
hid_by	true
rc=0
```

Mutation 1: this is not the primitive (`swallow no` or a separate `cond` row). Still fires.

### 2. Last-wins still drops the first site

`false || echo a; false || echo b` prints only `hid_by echo b`. Both `||` succeeded. Mutation 3 asked every site as a row.

### 3. Then-body harvest still works, which does not save (1)

`if true; then false || echo hid; fi` is swallow yes. That is the owned analogue. It does not distinguish (1).

---

## Primitive

Reality-stripped operation: tokenize a tiny `||` tree; if step status is 0 and some `||` RHS succeeded, print the last such site.

Nearest ordinary workflow: `bash -x` plus `$?`. Observable capability lost if swallowecho vanishes: **none** beyond that hand join. `--status` remains a caller sticker for anything the model does not implement.

Honor KILL. Do not mutate. Reimpl of this primitive is not a survivor. Archive stays under `lineages/candidate-swallowecho/`.

KILL

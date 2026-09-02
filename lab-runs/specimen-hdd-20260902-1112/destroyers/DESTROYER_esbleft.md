# DESTROYER esbleft

Date: 2026-09-02 16:03 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0422
Worker: destroyer-esbleft

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-esbleft/esbleft`

sha256 `0db312f7bc7af63de3294c23b00c6a6559ae693523f3ece4118cad410f2ede3b` (2776 bytes). Host Python 3.14.5. Tests 4/4. `demo.sh` twice: stdout byte-identical to `demo-1.log` / `demo-2.log`. No esbuild invoked. No merge onto `main`. Archive was not edited. No worktree.

Origin (`CANDIDATE.md` / harvest `hdd-esbmeta` / specimen-093): name leftover uniqueKey-sized `bytesInOutput` after substituted hashed path. Kind: USEFUL_COMPOSITION. Nearest: diff metafile `inputs.bytesInOutput` against `outputs.bytes`. Constraint: owned labeled records; no esbuild. Distinct from Honor-KILLed cssleft (webpack CSS name vs PNG name).

This candidate is a **THIN_WRAPPER of two caller-typed equalities**: `leftover_uniquekey = bool(uniquekey_len) and bytes_in_output == uniquekey_len and substituted_bytes != bytes_in_output`. Echoed numbers do not vote. Independent replica of leftover+rc matches owned fixtures **3/3** and extra well-formed triples **7/7** (empty uniquekey_len field is a parse/rc-1 path, not leftover). `awk` of the three fields already prints the harvest. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-esbleft/esbleft
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-esbleft/fixtures
```

Host-executed against the archive. Do not grow an esbuild runner. Do not send uniqueKey / metafile theater back to R1. First HARVEST is not protection.

---

## What still works

The owned analog leftover 61 vs 94, the long-name 52 vs 196, and any other three caller numbers where `bytes_in_output` equals `uniquekey_len` and differs from `substituted_bytes`.

```bash
python3 "$CLI" "$FIX/093-leftover.rec"
echo rc=$?
```

```text
uniquekey_len	61
bytes_in_output	61
substituted_bytes	94
leftover_uniquekey	yes
```

rc=1.

## What is already named

```bash
python3 "$CLI" "$FIX/093-fresh.rec"; echo rc=$?
```

never-url: uniquekey_len `-`, 22==22, leftover no, rc=0.

## Honor KILL

Replica of `bool(uk) ∧ bio==uk ∧ sub!=bio` matches leftover+rc on the three owned records and eight extra labeled triples. Same class as Honor-KILLed cssleft / pnpbuilt. Do not mutate into a metafile parser.

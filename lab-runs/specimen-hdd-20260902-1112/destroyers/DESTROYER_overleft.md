# DESTROYER overleft

Date: 2026-09-02 16:03 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0423
Worker: destroyer-overleft

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-overleft/overleft`

sha256 `375f67fb60e01c1b29d4759336f1229e630af075d5d90caa8bf298cb4bf47b19` (2927 bytes). Host Python 3.14.5. Tests 4/4. `demo.sh` twice: stdout byte-identical to `demo-1.log` / `demo-2.log`. No npm invoked. No merge onto `main`. Archive was not edited. No worktree.

Origin (`CANDIDATE.md` / harvest `hdd-overleft` / specimen-095): name leftover OverrideSet after the carrying edge is gone versus lock original identity. Kind: USEFUL_COMPOSITION. Nearest: grep nested override vs lock version. Constraint: owned labeled records; no npm. Distinct from specimen-004/033 and Honor-KILLed peerleft.

This candidate is a **THIN_WRAPPER of a caller flag plus string equality**: `leftover_override = override_set in {yes,true,1,present} and original_version and lock_version == original_version`. `package` is a spectator. Independent replica of leftover+rc matches owned fixtures **3/3** and extra well-formed rows **6/6** (empty override_set is a parse/rc-1 path). `awk` of override_set / lock / original already prints the harvest. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-overleft/overleft
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-overleft/fixtures
```

Host-executed against the archive. Do not grow an arborist walker. Do not send npm theater back to R1. First HARVEST is not protection.

---

## What still works

The owned leftover second-install (`lock 6.0.0` + override_set yes), applied 7.0.0, never-overridden, and any other caller-complete lock/original/flag triple.

```bash
python3 "$CLI" "$FIX/095-leftover.rec"
echo rc=$?
```

```text
package	package-json
lock_version	6.0.0
original_version	6.0.0
override_set	yes
leftover_override	yes
```

rc=1.

## Honor KILL

Same shape as Honor-KILLed pnpbuilt / peerleft (leftover = in A not matching B). Do not mutate into a lockfile parser.

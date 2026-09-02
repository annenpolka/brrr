# DESTROYER armtimer

Date: 2026-09-02 16:50 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0444 worker=destroyer-armtimer

Target (archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-armtimer/armtimer`

sha256 `84d650978f0f9b9c4c5a3842444870e9cd9de550a7b59428c9e02d79c95291f0` (3697 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-armtimer-armtimer/armtimer/armtimer` is **byte-identical** (`cmp` rc=0). Worktree HEAD `9ba5ef0 Add armtimer CLI from hdd-s066 harvest (isolated; not for main.)`, branch `specimen-hdd/candidate-armtimer-armtimer`. Parent `main` is `432f954`; `git ls-tree HEAD armtimer` empty. Host Python 3.14.5. `command -v docker` was **not** invoked. unittest `python3 tests/test_armtimer.py` 4/4 OK. `demo-1.log` / `demo-2.log` byte-identical. No `MUTATE.md`. No merge onto `main`. Archive was not edited. No prior `DESTROYER_armtimer.md`.

Origin (`CANDIDATE.md` / harvest `hdd-s066` / specimen-066): name which timer was armed while starting vs the timer after start period. Kind: USEFUL_COMPOSITION. Constraint: no docker. Sibling `startimer` is the same harvest with duration flags instead of a caller TSV.

This candidate is a **THIN_WRAPPER of caller-labeled duration/status arithmetic**. `inspect()` is `remaining = start_period - elapsed`, `starting = status=="starting" and elapsed < start_period`, `armed = start_interval if starting else interval`, `late = starting and armed > remaining and remaining >= 0`, `expected_after_period = interval`. It never reads a container spec, never arms a timer, never talks to a docker daemon. Independent replica (`destroyers/_armtimer_scratch/replica.py`, does not import armtimer) is **byte-identical** to CLI stdout+rc on owned fixtures **2/2** and on a 5×5×5×3×5 grid **1875/1875** (total **1877/1877**, `stdout_eq=True`, `rc_eq=True`). awk of `status==starting && elapsed<period` then `armed=start_interval` else `interval` names owned leftover `armed 30` / `late yes`. `printf` of the six canned owned lines matches the CLI. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-armtimer/armtimer
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-armtimer/fixtures
S066=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-066
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-armtimer-armtimer/armtimer/armtimer
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not merge with `startimer`. Do not grow a docker healthcheck runner to escape THIN_WRAPPER. Do not send dockersim theater back to R1. First HARVEST is not protection.

---

## What still works

Owned 066 starting, elapsed 0, start_interval 30 vs interval 2 after period 2: `armed 30` / `during starting` / `late yes` / `expected_after_period 2`, rc=0. Unseen after period (`status healthy`, elapsed 5): `armed 2` / `late no`. Missing field rc=1. Tests 4/4. Demos identical. That is the harvest analogue. It is also arithmetic on five caller fields.

```bash
python3 "$CLI" "$FIX/066-starting.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-after.rec"; echo rc=$?
```

```text
armed	30
during	starting
period_end	2
remaining	2
expected_after_period	2
late	yes
rc=0

armed	2
during	healthy
period_end	2
remaining	-3
expected_after_period	2
late	no
rc=0
```

---

## Honor KILL

`starting = (status==starting && elapsed<start_period); armed = starting ? start_interval : interval; late = starting && armed>remaining && remaining>=0` already prints the harvest. Same leftover-arithmetic class as Honor-KILLed waitoneshot (timeout 0 + wait-for-creation flag table). `status` / `elapsed` / the three durations are caller-typed. `expected_after_period` is always `interval` (spectator of the post-period formula). Negative `remaining` on unseen-after is `start_period - elapsed`, not a timer.

Sibling `startimer` (DESTROYER_startimer MUTATE leftover, this tick's DESTROYER_startimer_2) is the same four-number join without a TSV. Killing armtimer does not protect startimer; killing startimer does not need a second timer CLI.

KILL

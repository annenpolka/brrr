# DESTROYER startimer 2

Date: 2026-09-02 16:50 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0445 worker=destroyer-startimer-2

Target (archive, bytes unchanged since first destroyer):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-startimer/startimer`

sha256 `dc6f4370906ff427acdd909b8101e6c960d162a79269cfd06cd52fab3f137a84` (4296 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-startimer-startimer/candidate-startimer/startimer` is **byte-identical** (`cmp` rc=0). HEAD `74f1ecf ground startimer from hdd harvest`. Parent `main` is `432f954`; `git ls-tree HEAD startimer` empty. Host Python 3.14.5. docker was **not** invoked. unittest `python3 tests/test_startimer.py` OK. `demo-1.log` / `demo-2.log` byte-identical. **No `MUTATE.md`.** No mutate-startimer job in `jobs.jsonl`. No merge onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-s066` / specimen-066): name the timer armed while starting, remaining at period end, and when the first counted failure fires. Kind: USEFUL_COMPOSITION. Sibling `armtimer` is the same harvest as a TSV arithmetic CLI.

First destroyer (`DESTROYER_startimer.md`) **MUTATE**. Required remaining_at_period_end to match armed−elapsed at period_end only when first_probe is after that instant; negative gap is a lie if the counted probe is the original fire; `reset_at_period_end` is a constant `no`. If mutation cannot do that, a later destroyer should KILL. Mutation never queued. Bytes unchanged. First MUTATE is not protection. Job kill_condition: Honor KILL if THIN_WRAPPER of caller duration flags / mutation never queued.

This candidate is a **THIN_WRAPPER of four caller duration flags**. `inspect()` is `armed = start_interval`, `remaining = max(armed - period_end, 0)`, `reset_at_period_end = False`, `first_probe = armed`, `first_counted = first_probe if first_probe >= period_end else period_end`, `unhealthy_at = first_counted + (retries-1)*interval`, `expected_unhealthy = period_end + interval + (retries-1)*interval`. It never reads a container spec, never arms a timer, never talks to docker. Independent replica (`destroyers/_startimer2_scratch/replica.py`, does not import startimer) is **byte-identical** to CLI stdout+rc on owned 066 **1/1** and on an 8×8×8×4 duration/retries grid **2048/2048** (total **2049/2049**). DESTROYER_1 leftover still fires: `--start-period 30s --start-interval 2s --interval 2s --retries 1` → `remaining_at_period_end 0s`, `first_probe 2s`, `gap -2s`. awk of `remaining=max(start_interval-start_period,0)` already names that 0s. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-startimer/startimer
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-startimer/fixtures
S066=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-066
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-startimer-startimer/candidate-startimer/startimer
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not merge with `armtimer`. Do not grow a docker healthcheck runner to escape THIN_WRAPPER. Do not send dockersim theater back to R1.

---

## What still works

Owned `2s / 30s / 2s / retries 1`: `armed start-interval 30s`, `remaining_at_period_end 28s`, `reset_at_period_end no`, `unhealthy_at 30s`, `expected_unhealthy 4s`, `gap 26s`, rc=0. Unseen retries=2 still prints. Negative duration rc=1. retries 0 rc=1. That is the first destroyer's happy path. It is also arithmetic on four argv flags.

```bash
python3 "$CLI" --start-period 2s --start-interval 30s --interval 2s --retries 1; echo rc=$?
```

```text
armed_at	0s
armed	start-interval	30s
period_end	2s
remaining_at_period_end	28s
reset_at_period_end	no
first_probe	30s
first_counted	30s
unhealthy_at	30s
expected_unhealthy	4s
gap	26s
retries	1
rc=0
```

---

## Honor-KILL leftovers (DESTROYER_startimer mutation; still fire)

### 1. remaining_at_period_end disagrees with first_probe when StartInterval < StartPeriod

```bash
python3 "$CLI" --start-period 30s --start-interval 2s --interval 2s --retries 1
```

```text
armed	start-interval	2s
period_end	30s
remaining_at_period_end	0s
first_probe	2s
first_counted	30s
unhealthy_at	30s
expected_unhealthy	32s
gap	-2s
```

`remaining_at_period_end` is `max(armed - period_end, 0)` so 0s, while `first_probe` is 2s (inside the period). Negative gap is the advertised lie. Bytes unchanged.

### 2. reset_at_period_end is a constant

Always `no` on **2049/2049** replica cells. The CLI replays only the failing getInterval (arm start-interval at t=0, never reset). It cannot name the policy that *would* reset at period end.

### 3. THIN_WRAPPER of caller flags

`demo.sh` already prints `StartPeriod=2s StartInterval=30s Interval=2s Retries=1` and says the four numbers do not name that the timer is not reset. The CLI then prints those four numbers plus `max(si-sp,0)` and `sp+interval`. Same leftover-arithmetic class as Honor-KILLed waitoneshot / this tick's armtimer.

KILL

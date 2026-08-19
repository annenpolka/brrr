# reimpl-08 — scree

## Primitive

Two timestamps or two clock readings on stdin; emit which clock explains the gap (`SLEEP` / `DILATE` / `STEP` / `REST`). A Unix filter. No spawn.

## Why this might not exist

Ancestor `lapse` wrapped a command. Mutation `scarp` flipped the object: consume two cuts, never exec. This reimplementation rebuilds that filter from observed behavior only — README, CANDIDATE transcript, and the ancestor binary as a black box. The test is whether the primitive is real enough to survive a second author.

The Darwin lie is the load-bearing one: `time.monotonic()` is `CLOCK_UPTIME_RAW`, never `CLOCK_MONOTONIC_RAW`. Two unlabeled timestamps are REST. 50 ppm slew is not a step. Largest gap wins.

## How to run

```bash
chmod +x ./scree
./scree selftest
./demo.sh 0
./scree cut | ./scree --explain
{ ./scree cut --json --boot; ./scree cut --json; } | ./scree
{ ./scree cut --json; sleep 0.35; ./scree cut --json; } | ./scree
printf '1000\n1001\n' | ./scree
./scree --require SLEEP < fixtures/slew.txt
```

Python 3.10+, stdlib only. ctypes `sysctlbyname` for `kern.boottime` (no `sysctl(8)`, no `ctypes.util.find_library`). Exit 0 classified, 1 parse / `--require` miss, 2 usage.

## Empirical transcript

### Gold, matched

`./scree selftest` 7/7. Fixtures `sleep/step/dilate/rest/slew` named correctly; explain and porcelain text match the ancestor on those files.

```
$ printf '1000\n1001\n' | ./scree
REST
```

```
$ { ./scree cut --json; sleep 0.35; ./scree cut --json; } | ./scree
DILATE
```

scree did not fork sleep. Two cuts, different pids, proper discarded, world ~0.4s → DILATE.

```
$ ./scree cut | ./scree --explain
SLEEP  explains=machine  kind=host
  wall        22d16h… 
  machine     22d16h…   CLOCK_MONOTONIC_RAW
  awake       21d11h…   CLOCK_UPTIME_RAW
  sleep        1d05h03m
  ntp           -7.48s
reason  host slept 1d05h03m (5% of coordinate)
```

SLEEP, not STEP. `python.monotonic` in the TSV is an alias of awake already filled; it does not split the snapshot (the v0.1 Darwin lie).

```
$ { ./scree cut --json --boot; ./scree cut --json; } | ./scree
SLEEP
```

```
wall <boot> <now>
monotonic 0 <time.monotonic()>
→ SLEEP  explains=awake  kind=host
  machine  —
  ntp      —
```

No machine clock in the input. 29 hours is still not an NTP step.

`fixtures/slew.txt` (`ntp=-7.5s`, one day of sleep) is SLEEP: 50 ppm of 22 days is ~95s, so 7.5s is slew. `--require SLEEP` exits 0; `--require STEP` exits 1.

Busy loop as two JSON cuts from **one** pid (proper 0.280s / awake 0.280s) → **REST**. JSON `python_monotonic` next to `machine` does not clobber RAW → **SLEEP** explains=machine.

### Beat

Repeated `key=value` lines, one clock per pair:

```
wall=0
wall=10
machine=0
machine=10
awake=0
awake=1
```

Ancestor: **REST** (later keys overwrite; only wall survives as an interval). scree: **SLEEP** — each key keeps both timestamps, which is what a human meant. Recorded as a beat, not a gold requirement.

### Divergences (honest)

- JSON `version` is `0.1` (this tool), ancestor `0.2`. Verdicts match.
- Unlabeled three numbers `0 1 2` → scree **STEP**, ancestor **DILATE**. Not a gold case. scree treats `ntp=-1s` as a wall step; ancestor prefers DILATE when proper was never given and wall is 0. Left as-is.
- `hello` / junk: both exit 1, `no clock readings on stdin`. Empty stdin: both exit 2 plus usage.

## Dogfood targets

- This Darwin host since `kern.boottime` (Tue Jul 28 12:43:57 2026): ~22d16h wall/machine, ~21d11h awake, **1d5h3m sleep**, **~−7.48s** adjtime vs `CLOCK_MONOTONIC_RAW`.
- `time.monotonic()` vs `CLOCK_MONOTONIC_RAW` (the timeout author's pair).
- Synthetic duration fixtures: sleep, step, dilate, rest, slew-not-step.
- Two-cut JSONL; two unlabeled timestamps; in-process busy REST.

## Surprises

- Darwin `CLOCK_MONOTONIC` (POSIX name, id 6) **includes sleep** and is adjtime-slewed: it sits ~7.48s behind `CLOCK_MONOTONIC_RAW`. Sampling id 6 as "machine" hides NTP. Only RAW is unslewed. Python never gives you RAW.
- A filter that aliases `python.monotonic` onto `awake` *and then treats the alias as a second timestamp of the same snapshot* invents a ~0s awake interval and reports REST. The wrap-a-command ancestor never saw this. The reimplementation hit it on `cut | scree` until aliases were forbidden from splitting a filled field.
- 50 ppm and 50 ms are different floors. STEP uses `max(50ms, 50ppm × machine)`. SLEEP is a 50 ms positive floor. DILATE competes on `world − proper` only when proper was actually measured and γ > 3; otherwise it is a leftover when STEP/SLEEP did not fire. That split is what keeps JSONL host-sleep as SLEEP instead of DILATE (world 10s, proper discarded).

## Failures

- Host SLEEP still cannot be live-tested as a *lid close during this command* without closing the lid; since-boot plus `kern.sleeptime` is the dogfood. scree does not paint a `Z` band (no sampler).
- Two wall timestamps from `date +%s` cannot distinguish SLEEP from STEP from DILATE. REST is honest, and easy to misread as "nothing happened."
- Linux `CLOCK_BOOTTIME` is selected as machine, not dogfooded tonight.
- `proper` from two different `scree cut` processes is discarded (pids differ). REST of a CPU hog has to come from cuts the work itself wrote.

## Suggested mutations

- Adjacent pairs on a stream of cuts (`scree` as `awk` over a clock log).
- Read rusage of a `--pid` without spawning it (libproc / `/proc`).
- `--check` that a CI interval contains no SLEEP (flaky `time.monotonic` timeouts).
- Name Darwin `CLOCK_MONOTONIC` vs RAW as its own slew object, not NTP.

## Kill / keep

Keep. The primitive survived a second author: the filter, the Darwin monotonic mapping, the 50 ppm floor, and largest-gap vs STEP-first are all load-bearing. The first implementation of this reimplementation *did* split a snapshot on `python.monotonic` and reported REST for a laptop that had slept a day — the same lie the mutation had already documented. That is evidence the trap is real, not that the ancestor was merely well-commented.

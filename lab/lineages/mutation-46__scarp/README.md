# scarp

Which clock explains the gap.

`lapse` wrapped a command and sampled it. **scarp** is the Unix filter of that object: two timestamps or two clock-cuts on stdin, one name on stdout — `SLEEP` / `DILATE` / `STEP` / `REST`. It never execs. The shell (or a log) already had the interval.

```
wall      CLOCK_REALTIME         NTP can step it
machine   CLOCK_MONOTONIC_RAW    runs during lid-close; no NTP
awake     CLOCK_UPTIME_RAW       pauses during lid-close; no NTP
proper    CPU a process aged
```

On Darwin, Python's `time.monotonic()` **is** `CLOCK_UPTIME_RAW`. Lid-close does not tick it. Comparing wall to "monotonic" since boot is a day of **SLEEP**, not a 29-hour NTP **STEP**.

## Install / run

Python 3.10+, stdlib only. No spawn.

```bash
chmod +x ./scarp
./scarp selftest
./scarp cut | ./scarp                 # this machine since boot
./scarp cut --json --boot; ./scarp cut --json | ./scarp
printf '1000\n1001\n' | ./scarp       # two timestamps, one clock → REST
./demo.sh 0
```

## Three examples

### 1. This laptop's lid-close, as a filter

```bash
./scarp cut | ./scarp --explain
```

One snapshot of every clock. The implied other cut is boot. On a Darwin host that has slept: **SLEEP**, `ntp=-7.5s` (slew, not STEP).

### 2. The world moved; nobody aged

```bash
{ ./scarp cut --json; sleep 0.35; ./scarp cut --json; } | ./scarp
```

scarp did not run `sleep`. **DILATE**.

### 3. Named durations (already subtracted)

```bash
./scarp < fixtures/slew.txt     # 7.5s NTP wander over 22 days → SLEEP
./scarp < fixtures/step.txt     # wall jumped 4s → STEP
./scarp < fixtures/dilate.txt   # 2s world, 10ms proper → DILATE
./scarp < fixtures/rest.txt     # proper tracks awake → REST
```

## Verdicts

| name | the clock that explains the gap |
| --- | --- |
| STEP | wall (NTP / adjtime jump, after 50 ppm slew floor) |
| SLEEP | machine ran while awake did not (host suspend) |
| DILATE | awake/machine ran while proper did not |
| REST | they agree, or only one clock was given |

Largest disagreement wins. A 29-hour lid-close beats a 7-second slew.

`--json` / `--porcelain` / `--explain` / `--require SLEEP`. Exit 0 classified (or `--require` matched), 1 parse/`--require` miss, 2 usage.

See `CANDIDATE.md` for the mutation, Darwin dogfood, and the v0.1 lie.

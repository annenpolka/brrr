# mutation-46 — scarp

## Primitive

Two timestamps or two clock readings on stdin; emit which clock explains the gap (`SLEEP` / `DILATE` / `STEP` / `REST`). A Unix filter. No spawn.

## Why this might not exist

Ancestor `lapse` (candidate-36) already named the disagreement between wall, machine, awake, and proper time. Its buried assumption is **we wrap a command**. `lapse -- sleep 1` forks, samples `ps`, waits `wait4`. That is a tracer. You cannot `paste cut0 cut1 | lapse`. You cannot classify a pair of `time.time()` / `time.monotonic()` readings a timeout already stored. You cannot ask "this laptop since boot" without the tool also becoming `uptime(1)`.

The missing verb is the other half of a lapse: **consume two cuts**. The shell sandwiches work. A logger already has the readings. scarp names the clock that owns the leftover.

Discarded (more conventional): add `lapse diff a.json b.json` and keep `Popen`. That leaves spawn in charge.

Not leftover-names, inverse-printf, occupancy, or a wait-for graph. The object is still a clock-cut. The interaction flipped.

## How to run

```bash
chmod +x ./scarp
./scarp selftest
./demo.sh 0
./scarp cut | ./scarp --explain
{ ./scarp cut --json --boot; ./scarp cut --json; } | ./scarp
{ ./scarp cut --json; sleep 0.35; ./scarp cut --json; } | ./scarp
printf '1000\n1001\n' | ./scarp
./scarp --require SLEEP < fixtures/slew.txt
```

Python 3.10+, stdlib only. ctypes `sysctlbyname` for `kern.boottime` (no `sysctl(8)`). Exit 0 classified, 1 parse / `--require` miss, 2 usage.

## Empirical transcript

### v0.1 — working filter, Darwin lie

`./scarp selftest` 5/5. Fixtures `sleep/step/dilate/rest` named correctly. `{cut; sleep 0.35; cut} | scarp` → **DILATE** without scarp forking sleep.

Then the host:

```
$ ./scarp cut | ./scarp --explain
REST  kind=interval
  wall        -1d05h03m
  machine     -1d05h03m
  ntp               +0s
reason  clocks agree
```

29 hours of lid-close, reported as REST with a **negative** day. Cause: `python.monotonic` aliased to `machine` (POSIX folklore), so one snapshot split into two cuts and subtracted `CLOCK_MONOTONIC_RAW − CLOCK_UPTIME_RAW` backwards.

```
$ { ./scarp cut --json --boot; ./scarp cut --json; } | ./scarp --explain
STEP  ntp=+1d05h03m
reason  wall forward-stepped 1d05h03m vs machine
```

Same alias overwrote `machine` with Python's monotonic. Lid-close looked like a 29-hour NTP step.

The question a timeout author actually types — wall vs `time.monotonic()` since boot:

```
wall 1785210237.842 1787166602.856
monotonic 0 1851737.032
→ STEP  ntp=+1d05h03m
```

And the 22-day slew fixture (`ntp=-7.5s`, one day of sleep) was **STEP** because tag order put wall first and the floor was a flat 50ms.

Two unlabeled timestamps `1000 1001` became **DILATE**: missing clocks were filled from wall, proper stayed 0.

### After (v0.2) — origin, Darwin monotonic, largest gap

Driven by that transcript, not by the ancestor's feature list:

1. `time.monotonic()` / `monotonic` → **awake** (pauses on Darwin suspend). Never clobber `CLOCK_MONOTONIC_RAW`.
2. Do not split a snapshot on an alias of a field already filled.
3. Epoch vs since-boot is not NTP. A single live cut with `boottime` is a host interval (proper = awake).
4. 50 ppm slew floor. Largest disagreement wins: 29h sleep beats 7.5s wander.
5. One clock (two timestamps) is REST, not an invented DILATE.

```
$ ./scarp cut | ./scarp --explain
SLEEP  explains=machine  kind=host
  wall        22d15h31m
  machine     22d15h31m   CLOCK_MONOTONIC_RAW
  awake       21d10h27m   CLOCK_UPTIME_RAW
  sleep        1d05h03m
  ntp           -7.466s
reason  host slept 1d05h03m (5% of coordinate)
```

`--require SLEEP` exits 0. `{cut --boot; cut}` is the same SLEEP. `fixtures/slew.txt` is SLEEP, not STEP.

Folklore trap, after:

```
wall 1785210237.842 1787166921.519
monotonic 0 1852055.695
→ SLEEP  explains=awake
  machine  —
  sleep    1d05h03m
  ntp      —
```

No machine clock in the input. scarp still refuses to call 29 hours an NTP step.

Busy loop as two JSON cuts from **one** pid (proper 0.280s / awake 0.280s) → **REST**. Shell `sleep 0.35` between two `scarp cut` processes → **DILATE**. scarp spawned neither.

`./demo.sh 0` exits 0. `selftest 7/7`.

## Dogfood targets

- This Darwin host since `kern.boottime` (Tue Jul 28 12:43:57 2026): 22d15h wall/machine, 21d10h awake, **1d5h3m sleep**, **−7.466s** adjtime vs `CLOCK_MONOTONIC_RAW`. Last lid-close ~11 minutes on Aug 19.
- `time.monotonic()` vs `CLOCK_MONOTONIC_RAW` (the timeout author's pair).
- Synthetic duration fixtures: sleep, step, dilate, rest, slew-not-step.
- Two-cut JSONL; two unlabeled timestamps; in-process busy REST.

## Surprises

- Darwin `CLOCK_MONOTONIC` (the POSIX name) **includes sleep** and is adjtime-slewed: it sits **7.466s behind** `CLOCK_MONOTONIC_RAW`, the same offset as wall−boot−RAW. Using `CLOCK_MONOTONIC` as "machine" hides NTP. Only RAW is unslewed. Python never gives you RAW: `time.monotonic()` is `CLOCK_UPTIME_RAW`.
- A filter that aliases `python.monotonic` onto `machine` will subtract two same-snapshot fields and invent a 29-hour interval with the wrong sign. The wrap-a-command ancestor never saw this: it already subtracted deltas inside one process.
- Largest-gap vs tag-order is the mutation's own primary: ancestor listed STEP before SLEEP, so a laptop since boot was a clock-step.

## Failures

- Host SLEEP still cannot be live-tested as a *lid close during this command* without closing the lid; since-boot plus `kern.sleeptime` is the dogfood. scarp does not paint a `Z` band (no sampler).
- Two wall timestamps from `date +%s` cannot distinguish SLEEP from STEP from DILATE. REST is honest, and easy to misread as "nothing happened."
- Linux `CLOCK_BOOTTIME` is selected, not dogfooded tonight.
- `proper` from two different `scarp cut` processes is discarded (pids differ). REST of a CPU hog has to come from cuts the work itself wrote.

## Suggested mutations

- Adjacent pairs on a stream of cuts (`scarp` as `awk` over a clock log).
- Read rusage of a `--pid` without spawning it (libproc / `/proc`).
- `--check` that a CI interval contains no SLEEP (flaky time.monotonic timeouts).
- Name Darwin `CLOCK_MONOTONIC` vs RAW as its own slew object, not NTP.

## Kill / keep

Keep. The flip is real: lapse is a tracer, scarp is a filter, and the Darwin monotonic lie only shows up once you stop wrapping and start reading the cuts a developer already has. Tomorrow: `scarp cut | scarp` on a laptop, or paste two `time.monotonic()` lines next to wall.

# mutation-60 — yaw

## Primitive

Two clock names or two readings; emit whether the gap is kernel **SLEW** (adjtime), **SLEEP** (RAW vs UPTIME_RAW), **STEP** (true wall jump vs already-slewed POSIX `CLOCK_MONOTONIC`), or **REST**. Darwin POSIX `CLOCK_MONOTONIC` vs RAW is first-class. A Unix filter. No spawn. Not NTP.

## Why this might not exist

Ancestor `scarp` (mutation-46) already names which clock explains a gap (`SLEEP` / `DILATE` / `STEP` / `REST`). Its buried assumption is **wall − machine = NTP**, then a 50 ppm floor decides STEP vs ignore. On Darwin, POSIX `CLOCK_MONOTONIC` includes sleep and is adjtime-slewed: it sits ~7.5s behind `CLOCK_MONOTONIC_RAW`, the same offset as wall−boot−RAW. scarp aliases `CLOCK_MONOTONIC` away (machine = RAW) and prints `ntp=-7.466s`.

The missing verb is not another leftover-namer and not a command wrapper. It is: **name the kernel mechanism between two named clocks**. SLEW is adjtime. STEP is a wall jump vs the already-slewed POSIX clock. SLEEP is RAW vs UPTIME_RAW. Python never exposes RAW (`time.monotonic()` is `CLOCK_UPTIME_RAW`).

Discarded: wrap `scarp` and rewrite the `ntp` field. That leaves scarp's pair in charge.

## How to run

```bash
chmod +x ./yaw
./yaw selftest
./demo.sh 0
./yaw --explain
./yaw CLOCK_MONOTONIC CLOCK_MONOTONIC_RAW
./yaw CLOCK_MONOTONIC_RAW CLOCK_UPTIME_RAW
./yaw CLOCK_REALTIME CLOCK_MONOTONIC
./yaw CLOCK_REALTIME CLOCK_MONOTONIC_RAW
./yaw --all
./yaw clocks
./yaw clocks | ./yaw
./yaw --require SLEW
printf '92.5 100\n' | ./yaw --as CLOCK_MONOTONIC CLOCK_MONOTONIC_RAW
```

Python 3.10+, stdlib only. ctypes `sysctlbyname` for `kern.boottime` (no `sysctl(8)`). Exit 0 classified, 1 parse / `--require` miss, 2 usage.

## Empirical transcript

### v0.1 — working filter, wall−RAW still STEP

`./yaw selftest` 5/5. Fixtures `slew/sleep/step/rest` named correctly. Live object pair:

```
$ ./yaw --explain
SLEW  pair=CLOCK_MONOTONIC − CLOCK_MONOTONIC_RAW  owned=slew
  CLOCK_MONOTONIC         22d15h59m   POSIX; sleep+adjtime
  CLOCK_MONOTONIC_RAW     22d15h59m   unslewed; sleep
  CLOCK_UPTIME_RAW        21d10h55m   unslewed; pauses
  python.monotonic        21d10h55m   Darwin: UPTIME_RAW
  wall − boot             22d15h59m   REALTIME − kern.boottime
  slew                      -7.481s   MONOTONIC − RAW
  sleep                    1d05h03m   RAW − UPTIME_RAW
  step                          +0s   wall−boot − MONOTONIC
reason  adjtime slewed CLOCK_MONOTONIC 7.481s behind CLOCK_MONOTONIC_RAW
```

`--all` on the same snapshot:

```
SLEW   CLOCK_MONOTONIC − CLOCK_MONOTONIC_RAW  Δ=-7.481s
SLEEP  CLOCK_MONOTONIC_RAW − CLOCK_UPTIME_RAW  Δ=+1d05h03m
REST   CLOCK_REALTIME − CLOCK_MONOTONIC  Δ=+0s
STEP   CLOCK_REALTIME − CLOCK_MONOTONIC_RAW  Δ=-7.481s
REST   python.monotonic − CLOCK_UPTIME_RAW  Δ=+0s
SLEEP  python.monotonic − CLOCK_MONOTONIC_RAW  Δ=-1d05h03m
SLEEP  CLOCK_MONOTONIC − python.monotonic  Δ=+1d05h03m
```

Wall vs POSIX `CLOCK_MONOTONIC` is REST (step ~1µs). MONOTONIC vs RAW is SLEW (−7.481s). Wall vs RAW is the same −7.481s, named **STEP**. That is scarp's NTP assumption: any wall vs since-boot gap is a step.

Ancestor scarp, same second:

```
SLEEP  explains=machine  kind=host
  ntp           -7.481s   wall − machine
reason  host slept 1d05h03m
```

Same offset. scarp's field name is `ntp`. yaw's object pair is already SLEW, but the pair scarp actually subtracts (wall−RAW) is still STEP.

### After (v0.2) — POSIX CLOCK_MONOTONIC is the STEP witness

Driven by that `--all` transcript, not by scarp's feature list:

1. STEP is only wall vs already-slewed `CLOCK_MONOTONIC`. Never wall vs RAW.
2. wall−RAW with a MONOTONIC witness and step≈0 is **SLEW**.
3. A scarp-shaped cut (wall + RAW, no POSIX MONOTONIC) is still SLEW, not NTP. Without MONOTONIC a step cannot be named.
4. `monotonic` stays the POSIX name. `time.monotonic` / `python.monotonic` is UPTIME_RAW.

```
$ ./yaw CLOCK_REALTIME CLOCK_MONOTONIC_RAW --explain
SLEW  pair=CLOCK_REALTIME − CLOCK_MONOTONIC_RAW  owned=slew+step
  slew                      -7.485s
  step                          +0s
  slew ppm             -3.82 ppm
reason  adjtime slewed POSIX CLOCK_MONOTONIC 7.485s behind CLOCK_MONOTONIC_RAW; wall−boot tracks CLOCK_MONOTONIC (not a step)
```

`--all` now names wall−RAW **SLEW**, not STEP. Wall vs `python.monotonic` is **SLEEP** (lid-close), not a 29-hour NTP step.

Bakeoff, same host:

```
scarp ntp=-7.485438  (verdict SLEEP, field ntp)
yaw  pair=SLEW slew=-7.485439
```

scarp names NTP. yaw names SLEW. Same number.

`./demo.sh 0` exits 0. `selftest 5/5`. `yaw clocks | yaw` → SLEW.

## Dogfood targets

- This Darwin host since `kern.boottime` (Tue Jul 28 12:43:57 2026): 22d16h wall / POSIX MONOTONIC / RAW, 21d11h UPTIME_RAW, **1d5h3m sleep**, **−7.48s adjtime** vs RAW. Last lid-close ~11 minutes on Aug 19 (14:16→14:27).
- ctypes `clock_gettime` + `sysctlbyname` `kern.boottime` / `sleeptime` / `waketime`. No `sysctl(8)`.
- Ancestor scarp's `ntp=` field vs yaw's slew on the same pair (wall vs RAW).
- Fixtures: slew, sleep, step, rest, scarp-cut-without-MONOTONIC.
- `time.monotonic()` vs RAW (timeout author's pair) → SLEEP.

## Surprises

- POSIX `CLOCK_MONOTONIC` matches wall−boot to **~1µs**. The entire "NTP" offset lives in MONOTONIC vs RAW. Using MONOTONIC as "machine" hides slew; using RAW as machine and calling wall−RAW `ntp` invents NTP.
- The slew is live, not a frozen 7.5s bump. First sample −7.472s; v0.1 demo −7.481s; v0.2 −7.485s. `ntp_adjtime` freq ≈ −17.8 ppm (STA_PLL|STA_FREQHOLD|STA_NANO); 18 ppm × 15 min ≈ 16 ms, which matches the drift. Accumulated slew is only −3.82 ppm over 22 days — freq was not always −18 ppm.
- `adjtime(2)` query returns EPERM on this host. The leftover is not readable; the object has to be the two clocks.
- Python 3.14 here: `time.monotonic()` == `CLOCK_UPTIME_RAW` to tens of nanoseconds. `CLOCK_MONOTONIC_RAW_APPROX` matches RAW. Python has no RAW.
- scarp's largest-gap still wins SLEEP on a host cut. yaw's default pair is the slew object even while the host has a day of sleep. Different question.

## Failures

- Without POSIX `CLOCK_MONOTONIC` in the snapshot, wall vs RAW cannot distinguish a true step from slew. v0.2 names it SLEW (refuses NTP). A `date`-style jump fed as two numbers with `--as wall raw` will be misnamed SLEW. Include CLOCK_MONOTONIC.
- Host SLEEP still cannot be live-tested as a lid-close during this command; since-boot plus `kern.sleeptime` is the dogfood.
- Linux `CLOCK_BOOTTIME` / adjtime-slewed `CLOCK_MONOTONIC` is encoded, not dogfooded tonight.
- `ntp_adjtime` freq is a current rate, not the object. yaw does not print it; doing so would look like wrapping NTP.

## Suggested mutations

- Stream of snapshots: slew as a function of time (ppm path), not one cut.
- Read `mach_absolute_time` / `mach_timebase_info` as a fifth Darwin clock, below RAW.
- `--check` that a CI interval's MONOTONIC vs RAW did not move (flaky adjtime during tests).
- Invert: given SLEW, emit which two clock names produce it on this kernel.

## Kill / keep

Keep. The flip is real: scarp still calls wall−RAW `ntp` (and v0.1 yaw followed it into STEP). After the live `--all`, STEP is wall vs POSIX `CLOCK_MONOTONIC`, and the 7.5s is SLEW. scarp names NTP; yaw names SLEW; same number.

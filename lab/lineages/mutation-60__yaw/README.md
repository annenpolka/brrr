# yaw

Kernel slew between two clocks.

scarp treats `wall − CLOCK_MONOTONIC_RAW` as **NTP** (STEP vs a 50 ppm floor). On Darwin, POSIX `CLOCK_MONOTONIC` **includes sleep and is adjtime-slewed**. It sits the same ~7.5s behind `CLOCK_MONOTONIC_RAW` as wall−boot−RAW. That offset is kernel slew, not an NTP step. Python never exposes RAW: `time.monotonic()` is `CLOCK_UPTIME_RAW`.

**yaw** takes two clock names or two readings and names the gap:

| name | the mechanism |
| --- | --- |
| SLEW | adjtime: `CLOCK_MONOTONIC` vs `CLOCK_MONOTONIC_RAW` |
| SLEEP | host suspend: RAW vs `CLOCK_UPTIME_RAW` |
| STEP | true wall jump vs already-slewed `CLOCK_MONOTONIC` |
| REST | the pair agrees |

It never wraps a command. It never calls the gap NTP.

## Install / run

Python 3.10+, stdlib only. ctypes `sysctlbyname` for `kern.boottime` (no `sysctl(8)`).

```bash
chmod +x ./yaw
./yaw selftest
./demo.sh 0
./yaw                            # this host: POSIX MONOTONIC vs RAW
./yaw CLOCK_MONOTONIC_RAW CLOCK_UPTIME_RAW
./yaw clocks
./yaw --all
printf '92.5 100\n' | ./yaw --as CLOCK_MONOTONIC CLOCK_MONOTONIC_RAW
```

Exit 0 classified (or `--require` matched), 1 parse / `--require` miss, 2 usage.

## Three examples

### 1. The Darwin lie POSIX hid

```bash
./yaw --explain
```

`CLOCK_MONOTONIC` vs `CLOCK_MONOTONIC_RAW` → **SLEW**. `CLOCK_REALTIME` vs RAW is the same offset: scarp prints `ntp=-7.5s`; yaw still says **SLEW** (wall−boot tracks POSIX `CLOCK_MONOTONIC`, so it is not a step).

### 2. Sleep is a different pair

```bash
./yaw CLOCK_MONOTONIC_RAW CLOCK_UPTIME_RAW
```

**SLEEP**. Lid-close. Not adjtime.

### 3. Named readings a timeout already stored

```bash
./yaw --as monotonic raw <<'EOF'
CLOCK_MONOTONIC 1957835.61
CLOCK_MONOTONIC_RAW 1957843.08
EOF
```

`monotonic` is the POSIX name, not `time.monotonic()`. **SLEW**.

## Darwin clocks (first-class)

```
CLOCK_REALTIME         wall; can STEP; adjtime-slewed with MONOTONIC
CLOCK_MONOTONIC        POSIX name; includes sleep; adjtime-slewed
CLOCK_MONOTONIC_RAW    includes sleep; unslewed
CLOCK_UPTIME_RAW       pauses on sleep; unslewed
python.monotonic       Darwin: CLOCK_UPTIME_RAW
kern.boottime          wall origin
```

See `CANDIDATE.md` for the mutation, the v0.1 wall−RAW lie, and the scarp bakeoff.

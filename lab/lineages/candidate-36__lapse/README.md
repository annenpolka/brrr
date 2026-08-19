# lapse

A duration is a disagreement between clocks.

`time(1)` reports one wall, one user, one sys. Those are not the same object as **host sleep**, **NTP step**, or **proper time** (CPU a process actually aged). lapse takes two *clock-cuts* — simultaneous samples of every clock the kernel exposes — and names the disagreement.

```
wall      CLOCK_REALTIME         NTP can step it
machine   CLOCK_MONOTONIC_RAW    runs during lid-close; no NTP
awake     CLOCK_UPTIME_RAW       pauses during lid-close; no NTP
proper    CPU of the process tree (a process ages only on-CPU)
```

On Darwin, Python's `time.monotonic()` **is** `CLOCK_UPTIME_RAW`. Lid-close does not tick it. That is the opposite of POSIX folklore.

Not leftover names. Not inverse-printf. Not occupancy eras. Not a wait-for graph. The object is the **cut**; the verb is to **lapse** two cuts.

## Install / run

Python 3.10+, stdlib only. macOS (Darwin clocks) or Linux (`CLOCK_BOOTTIME`).

```bash
chmod +x ./lapse
./lapse clocks              # one cut of this machine
./lapse machine             # boot → now (host proper time = awake)
./lapse -- sleep 1          # DILATE: world moved, process did not age
./lapse -- make -j4         # BOOST if tree CPU > awake
./demo.sh 0
```

The wrapped command's stdio is passed through. The report is on **stderr**. `--json` / `--porcelain` too.

## Three examples

### 1. A sleep ages almost not at all

```bash
./lapse -- python3 fixtures/block.py 0.35
```

Verdict `DILATE`, γ ≈ 25. The tree's proper time is interpreter startup; the rest is coordinate time the process did not live.

### 2. A CPU hog tracks the awake clock

```bash
./lapse -- python3 fixtures/busy.py 0.30
```

Verdict `REST`, γ ≈ 1.2. Same wall as (1), opposite aging.

### 3. This machine's own worldline since boot

```bash
./lapse machine
```

On a laptop this is usually `SLEEP`: a day of lid-close on a 22-day boot. `time.monotonic()` on Darwin will *not* include that day.

## Verdicts

| tag | meaning |
| --- | --- |
| STEP | wall and machine disagree beyond 50 ppm (clock stepped, not slew) |
| SLEEP | machine advanced while the host was not awake |
| STARVE | runnable, low %cpu, almost no proper-time gain |
| BOOST | tree proper time > awake (parallel age) |
| DILATE | world moved much farther than the tree aged |
| REST | proper time ≈ awake (serial on-CPU) |
| QUIET | clocks agree, or the interval is too small |

Worldlines (when a command is wrapped) are painted on the **machine** axis: `#` on-CPU, `~` blocked, `%` runnable, `Z` host-sleep. Phases collapse that to `run→block`.

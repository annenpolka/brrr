# candidate-36 — lapse

## Primitive

A **lapse** is the disagreement between two simultaneous *clock-cuts* of a machine: wall (NTP), machine (runs during sleep), awake (pauses during sleep), and proper time (CPU a process tree actually aged). `time(1)` is one number. This is four objects and a name for when they stop agreeing.

## Four primitives considered

1. **lapse** — clocks as objects; a duration is their disagreement. **Implemented.**
2. **worldline** — Minkowski diagram of a process tree (proper time vs coordinate time). Absorbed as a view of (1), not a separate product. Discarded as a standalone verb.
3. **aftertime** — mtime vs process happens-before inversions. **Discarded:** needs FS tracing, sits next to `spoor`.
4. **bootcensus** — process *roles* that reincarnate across reboot. **Discarded:** long observation, systemd-adjacent.

Not leftover-names, inverse-printf, occupancy eras, path-conditions, wait-for graphs, generation lots, or env-ABI.

## Why this might not exist

Every developer has watched `time sleep 1` print `real 1.00 user 0.00 sys 0.00` and learned nothing about *which clock that second belonged to*. The same report is printed if:

- the laptop lid closed for that second,
- NTP stepped,
- the process blocked,
- the process was runnable and starved,
- three children burned three cores.

`time` cannot tell them apart. `ps` shows one snapshot. `powermetrics` is a novel. Python's `time.monotonic()` on Darwin is `CLOCK_UPTIME_RAW` (pauses on lid-close) — the opposite of what timeout authors cargo-cult from Linux. There is no Unix verb whose object is **the cut of every clock**, and whose output is a named disagreement.

The recurring question is not "how long did it take?" It is "which time was that?"

## How to run

From this worktree:

```bash
./lapse selftest
./lapse clocks
./lapse machine
./lapse -- python3 fixtures/block.py 0.35
./lapse -- python3 fixtures/busy.py 0.30
./lapse -- python3 fixtures/parallel.py 3 0.28
./lapse -- python3 fixtures/mix.py 0.18 0.25
./demo.sh 0
```

Python 3.10+, stdlib only. Report on stderr; command stdio passed through.

## Empirical transcript

### Before the improvement (v0.1)

`./lapse -- python3 fixtures/busy.py 0.3`

- proper 0.314s from `wait4`, sampled 0s (ps `time` lagged).
- worldline τ=0s, γ=∞.
- verdict **STARVE REST** — a CPU hog classified as scheduler-starve because `state=R` and `last.cpu-first.cpu==0`.
- `./lapse machine` verdict **STEP SLEEP REST**: −7.467s NTP slew over 22 days tagged as a clock step; process-REST leaked onto a host.
- every 0.4s command printed `last-sleep 11m  woke 13h ago` from an unrelated lid-close.

### After (v0.2)

- `busy` → **REST**, γ=1.18, sampled=leader=0.314s. STARVE requires low mean %cpu, not a lagging `ps` counter.
- `%cpu` used for `#` only while `state` is `R` (rolling 1s average otherwise paints sleep as on-CPU).
- `mix` worldline **runq→run→block** (`#` then `~`).
- STEP floor scaled at 50 ppm: 7.5s in 22 days is slew, not STEP. `lapse machine` → **SLEEP**.
- `last-sleep` only if the host sleep interval intersects the lapse.
- single-pid trees take `wait4` as ground truth when `ps` never ticked.

Dogfood: `./lapse -- ./lapse clocks` — inner cut on stdout, outer lapse DILATE γ≈3 (startup vs a 40ms-proper command). JSON round-trips.

## Dogfood targets

- This CLI (`./lapse clocks`, `./lapse machine`, `./lapse -- ./lapse …`)
- Synthetic fixtures: block, busy, parallel, mix
- The host since `kern.boottime` (22d wall, 1d5h sleep on the inventor's laptop)

## Surprises

- Darwin `time.monotonic()` == `CLOCK_UPTIME_RAW`, **not** `CLOCK_MONOTONIC_RAW`. The "monotonic" clock Python programmers use for timeouts does not include lid-close; the kernel's monotonic-raw does. ~29 hours of sleep since boot is invisible to `time.monotonic()` and visible to lapse's machine clock.
- Darwin `wait4` rusage of a parent that `waitpid`'d its children is large enough to cover the kids (0.92s vs 0.54s sampled). `max(sampled, leader)` is the tree proper time; do not also assign it onto the parent worldline.
- `ps %cpu` is a ~1s EWMA. After a 180ms burst it stays "hot" into a sleep. Trust it for on-CPU glyphs only while `state` starts with `R`.

## Failures

- Host SLEEP cannot be live-tested without closing the lid; it is synthetic plus `lapse machine`.
- STARVE has no reliable live fixture without a CPU-hog fight; it is guarded so busy loops cannot false-positive.
- Short-lived grandchildren can miss the sampler; Darwin wait4 still saves the lapse total.

## Suggested mutations

- `lapse diff a.json b.json` — two commands, same clocks, named delta.
- Attach `--pid` for a duration (observe an already-running daemon's proper time).
- Linux `CLOCK_BOOTTIME` path is selected but not dogfooded.
- Paint host-sleep as a `Z` band on the axis when a command actually overlaps suspend.

## Kill / keep

Keep. The object (a clock-cut) is not a wait-for graph, not occupancy of a git predicate, and not `time(1)`. The Darwin monotonic surprise is a thing a developer can use tomorrow: "your timeout did not notice the lid."

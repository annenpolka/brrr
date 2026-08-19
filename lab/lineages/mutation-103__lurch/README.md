# lurch

Name every adjacent clock-cut, with scarp's leftover columns.

`scarp` classifies **`cuts[0], cuts[1]`**. **lurch** is the stream of that object: N cuts on stdin, N−1 named intervals on stdout — `SLEEP` / `DILATE` / `STEP` / `REST` — each row carrying `sleep=` and `ntp=`. It never execs. The log already had the pairs.

```
wall      CLOCK_REALTIME         NTP can step it
machine   CLOCK_MONOTONIC_RAW    runs during lid-close; no NTP
awake     CLOCK_UPTIME_RAW       pauses during lid-close; no NTP
proper    CPU a process aged
```

On Darwin, Python's `time.monotonic()` **is** `CLOCK_UPTIME_RAW`. Lid-close does not tick it.

Unlabeled numbers are timestamps of one clock, not a bag of `{wall, machine, awake, proper}`.

## Install / run

Python 3.10+, stdlib only. No spawn.

```bash
chmod +x ./lurch
./lurch selftest
./demo.sh 0

# ancestor scarp keeps the first pair; lurch names every adjacent pair
./lurch < fixtures/stream-dilate-then-sleep.jsonl
./lurch < fixtures/stream-sleep-then-dilate.jsonl

printf '1000\n1001\n1005\n1010\n' | ./lurch
{ ./lurch cut --json; sleep 0.35; ./lurch cut --json; ./lurch cut --json; } | ./lurch
```

## Three examples

### 1. A log, not the first pair

```bash
./lurch < fixtures/stream-dilate-then-sleep.jsonl
```

Three cuts: 2s world-sleep, then 9s host-sleep. Two names: **DILATE**, **SLEEP**. Each row has `sleep=` and `ntp=`.

`scarp` on the same file prints only **DILATE** (`cuts[0], cuts[1]`; the sleep is gone).

### 2. This laptop, sampled three times

```bash
{ ./lurch cut --json; sleep 0.35; ./lurch cut --json; ./lurch cut --json; } | ./lurch
```

lurch did not run `sleep`. First interval **DILATE**, second **REST**. Pair-delta `sleep=` is 0s; the 29 hours of lid-close since boot live in a singleton `lurch cut | lurch`, not in a 0.35s sandwich.

```bash
./lurch cut | ./lurch --explain
```

One snapshot. Implied origin is boot. On a Darwin host that has slept: **SLEEP**, `ntp=-7.5s` (slew, not STEP).

### 3. One clock, many ticks

```bash
printf '1000\n1001\n' | ./lurch          # two timestamps → REST
./lurch < fixtures/unlabeled.txt         # REST REST REST  (1s, 4s, 5s)
```

Unlabeled numbers are wall ticks. Ancestor scarp called `1000 1001 1005 1010` a **STEP** (duration bag) or kept the first eight fields of a thousand ticks.

## Verdicts

| name | the clock that explains the gap |
| --- | --- |
| STEP | wall (NTP / adjtime jump, after 50 ppm slew floor) |
| SLEEP | machine ran while awake did not (host suspend) |
| DILATE | awake/machine ran while proper did not |
| REST | they agree, or only one clock was given |

Largest disagreement wins. A 29-hour lid-close beats a 7-second slew. Missing rusage is not 22 days of DILATE.

`--json` / `--porcelain` / `--explain` / `--require SLEEP` / `--forbid SLEEP`. Exit 0 classified (or `--require` matched and `--forbid` missed), 1 parse / require / forbid, 2 usage.

See `CANDIDATE.md` for the mutation, Darwin dogfood, and the v0.1 missing-proper lie.

# twixt

Name each interval between consecutive clock-cuts.

`scarp` classifies **one pair**. **twixt** is awk over a clock log: N cuts on stdin, N−1 named intervals on stdout — `SLEEP` / `DILATE` / `STEP` / `REST` — each with timestamps. It never execs. The shell (or a log) already had the stream.

```
wall      CLOCK_REALTIME         NTP can step it
machine   CLOCK_MONOTONIC_RAW    runs during lid-close; no NTP
awake     CLOCK_UPTIME_RAW       pauses during lid-close; no NTP
proper    CPU a process aged
```

On Darwin, Python's `time.monotonic()` **is** `CLOCK_UPTIME_RAW`. Lid-close does not tick it.

## Install / run

Python 3.10+, stdlib only. No spawn.

```bash
chmod +x ./twixt
./twixt selftest
./demo.sh 0

# ancestor scarp keeps the first pair; twixt names every adjacent pair
{ scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json; } | ./twixt
{ scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json; } | scarp

./twixt < fixtures/stream.jsonl
printf '1000\n1001\n1005\n1010\n' | ./twixt
```

## Three examples

### 1. A log, not a pair

```bash
./twixt < fixtures/stream.jsonl
```

Four cuts: boot origin, 22-day host with lid-close, a 0.35s world-sleep, a 0.28s busy loop. Three names: **SLEEP**, **DILATE**, **REST**.

`scarp` on the same file prints only **SLEEP** (cuts[0], cuts[1]).

### 2. This laptop, sampled three times

```bash
{ scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json; } | ./twixt
```

twixt did not run `sleep`. First interval **DILATE**, second **REST** (back-to-back cuts). Each row also carries `host_sleep=` from the cut itself — 29 hours of lid-close since boot, even though the pair delta slept 0s.

```bash
{ scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json; } | ./twixt --origin boot
```

`--origin boot` prepends `kern.boottime` as cut 0: **SLEEP DILATE REST**.

### 3. One clock, many ticks

```bash
printf '1000\n1001\n' | ./twixt          # two timestamps → REST
./twixt < fixtures/unlabeled.txt         # REST REST REST  (1s, 4s, 5s)
```

Unlabeled numbers are wall ticks, not a bag of duration fields. v0.1 (and ancestor scarp) called `1000 1001 1005 1010` a **STEP**. It is three REST intervals.

## Verdicts

| name | the clock that explains the gap |
| --- | --- |
| STEP | wall (NTP / adjtime jump, after 50 ppm slew floor) |
| SLEEP | machine ran while awake did not (host suspend) |
| DILATE | awake/machine ran while proper did not |
| REST | they agree, or only one clock was given |

Largest disagreement wins. A 29-hour lid-close beats a 7-second slew.

`--json` / `--porcelain` / `--explain` / `--require SLEEP` / `--forbid SLEEP`. Exit 0 classified (or `--require` matched and `--forbid` missed), 1 parse / require / forbid, 2 usage.

See `CANDIDATE.md` for the mutation, Darwin dogfood, and the v0.1 unlabeled / invisible-lid-close lie.

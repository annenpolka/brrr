# mutation-59 — twixt

## Primitive

N clock-cuts on stdin; emit one named interval (`SLEEP` / `DILATE` / `STEP` / `REST`) per consecutive pair, with timestamps. A Unix filter over a clock log. No spawn.

## Why this might not exist

Ancestor `scarp` (mutation-46) already names the clock that explains a gap. Its buried assumption is **we classify one pair**. `classify_text` parses every cut, then uses `cuts[0], cuts[1]`. A three-cut JSONL from `{cut; sleep; cut; cut}` is DILATE; the back-to-back REST is dropped. You cannot `awk` a timeout log. You cannot ask "what happened between each sample."

The missing verb is the other half of a scarp: **consume a stream**. The shell sandwiches work more than once. A logger already has many readings. twixt names every adjacent leftover.

Discarded (more conventional): wrap scarp in a loop that peels two lines. That leaves "one pair" in charge and fights TSV multi-line cuts.

Not leftover-names, inverse-printf, occupancy, or a lockset. The object is still a clock-cut. The interaction flipped: pair → stream of adjacent pairs.

## How to run

```bash
chmod +x ./twixt
./twixt selftest
./demo.sh 0
./twixt < fixtures/stream.jsonl
./twixt --explain < fixtures/stream.jsonl
./twixt < fixtures/unlabeled.txt
{ scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json; } | ./twixt
{ scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json; } | ./twixt --origin boot
{ scarp cut --json --boot; scarp cut --json; } | ./twixt
```

Python 3.10+, stdlib only. Exit 0 classified, 1 parse / `--require` miss / `--forbid` hit, 2 usage.

## Empirical transcript

### v0.1 — working stream filter, unlabeled lie (`7ae2b33`)

`./twixt selftest` 6/6. `fixtures/stream.jsonl` (boot → 22d lid-close → 0.35s world-sleep → 0.28s busy) → **SLEEP DILATE REST**. Ancestor scarp on the same file → **SLEEP** only.

Live Darwin, three `scarp cut --json` with a 0.3s sleep between the first two:

```
cut0 wall=1787168623.693 machine=1958393.403 awake=1853757.955 pid=85722
cut1 wall=1787168624.046 machine=1958393.756 awake=1853758.308 pid=85748
cut2 wall=1787168624.083 machine=1958393.792 awake=1853758.345 pid=85752

scarp (whole stream):          DILATE
twixt:                         DILATE REST
scarp on each adjacent pair:   DILATE, REST
```

Pair names agree with piping pairs into ancestor scarp. scarp on the whole stream throws away pair 1. twixt spawned neither sleep nor cut.

`scarp cut | twixt` (one snapshot) → **SLEEP** `1d05h03m`, `ntp=-7.482s`. `{cut --boot; cut} | twixt` is the same SLEEP. Busy loop, three cuts, one pid → **REST REST**.

Then unlabeled timestamps — a clock log a timeout author actually types:

```
$ cat fixtures/unlabeled.txt
1000
1001
1005
1010

$ ./twixt --explain < fixtures/unlabeled.txt
STEP  kind=readings  t0=0.0  t1=1000.0
  wall     16m40.00s
  machine  16m41.00s
  awake    16m45.00s
  proper   16m50.00s
reason  wall backward-stepped 1.000s vs machine
```

Four wall ticks became one duration bag. Ancestor scarp does the same STEP. A stream of one clock is REST, REST, REST (1s, 4s, 5s), not an NTP step.

And the live three-cut stream, whose every cut contains 1d05h03m of lid-close (`machine − awake` ≈ 104635s), printed **DILATE REST** with `sleep=0s`. The host sleep is sitting in each JSON object and never becomes a column, because v0.1 only names the *pair delta*. Singleton `cut | twixt` sees it (`gap_from_one`); a stream of live cuts hides it.

### After (v0.2) — points, not bags; host sleep rides along

Driven by that transcript, not by the ancestor's feature list:

1. Unlabeled numbers are wall timestamps. N ticks → N−1 REST intervals. Never a bag of duration fields.
2. Each live pair carries `host_sleep` / `host_ntp` from the later cut's snapshot (`machine − awake`, `(wall−boot) − machine`). The pair delta stays the verdict; lid-close since boot rides along.
3. `--origin boot` prepends a since-boot origin when the first cut is an absolute snapshot. Opt-in, because inventing a cut would disagree with piping pairs into scarp.

Unlabeled, after:

```
$ ./twixt < fixtures/unlabeled.txt
REST    1000.000000    1001.000000    wall=1.000s
REST    1001.000000    1005.000000    wall=4.000s
REST    1005.000000    1010.000000    wall=5.000s

$ scarp < fixtures/unlabeled.txt
STEP
```

Live Darwin 3-cut stream, after (`host_sleep` was missing on these rows in v0.1):

```
#0 DILATE  t0=1787168846.099  t1=1787168846.485  wall=0.387s
  sleep         -0s
  host_sleep     1d05h03m
  host_ntp        -7.486s
#1 REST    t0=1787168846.485  t1=1787168846.523  wall=0.038s
  host_sleep     1d05h03m
  host_ntp        -7.486s

scarp on each adjacent pair: DILATE, REST   (names still agree)
twixt --origin boot:         SLEEP DILATE REST
```

`fixtures/stream.jsonl` DILATE/REST rows now print `host_sleep=1d00h00m host_ntp=-7.500s` without changing the names. `--require SLEEP` still matches a log that contains a sleep pair; the carried column is not a verdict.

Busy 0.28s+0.12s three cuts, same pid → **REST REST**. `./demo.sh 0` exits 0. `selftest 8/8`.

## Dogfood targets

- This Darwin host since `kern.boottime` Tue Jul 28 12:43:57 2026: 22d16h wall/machine, 21d10h awake, **1d5h3m sleep**, **−7.486s** adjtime vs `CLOCK_MONOTONIC_RAW`.
- `{scarp cut --json; sleep 0.3; scarp cut --json; scarp cut --json}` versus piping each pair into ancestor scarp.
- In-process busy REST (several cuts, same pid).
- Unlabeled timestamps (`fixtures/unlabeled.txt`) vs scarp's duration bag.
- `fixtures/stream.jsonl` (SLEEP then DILATE then REST, host_sleep on the later rows).

## Surprises

- scarp already parsed three JSONL cuts and then threw two of them away. The stream was never a parse problem; it was `len(cuts) >= 2: cuts[0], cuts[1]`.
- Back-to-back `scarp cut` processes are REST only because dt < 50ms. Proper is discarded (pids differ) so γ is ∞; the floor saves it. A 60ms back-to-back would be DILATE.
- Pair-delta SLEEP and snapshot `host_sleep` are different objects. A laptop that slept 29 hours *before the log started* is not a SLEEP interval in the log. v0.1 collapsed that distinction by only having singleton `gap_from_one`. v0.2 keeps the pair names comparable to scarp and still prints the 29 hours.
- Darwin `time.monotonic()` is still awake. A stream tool that aliases it onto machine would hide NTP on every pair, not just one.

## Failures

- Host SLEEP still cannot be live-tested as a *lid close during this command* without closing the lid; since-boot plus `kern.sleeptime` is the dogfood. `--origin boot` is the since-boot stand-in.
- Two wall timestamps from `date +%s` cannot distinguish SLEEP from STEP from DILATE. REST is honest.
- Linux `CLOCK_BOOTTIME` is selected, not dogfooded tonight.
- `proper` from two different `scarp cut` processes is discarded. REST of a CPU hog has to come from cuts the work itself wrote.
- `--origin boot` on a historical log whose first cut is not "now" still prepends this host's boot origin only from that cut's `boottime` field (correct if the cut recorded it; wrong if you paste foreign numbers without boottime).

## Suggested mutations

- Line-buffered JSONL (emit pair i as cut i+1 arrives).
- `--forbid SLEEP` as a CI gate on a timeout log (already wired; not dogfooded as a flake hunter).
- Read rusage of a `--pid` without spawning it (libproc / `/proc`) so a stream of wall ticks can grow a proper column.
- Collapse runs: `DILATE REST REST DILATE` → `DILATE 1, REST 2, DILATE 1` (the gait of a log).
- Name Darwin `CLOCK_MONOTONIC` vs RAW as its own slew object, not NTP (sibling of mutation-60).

## Kill / keep

Keep. The flip is real: scarp is a pair filter, twixt is awk over the same object, and both the unlabeled-timestamp lie and the invisible lid-close only show up once you stop asking for "two numbers" and start asking for a log.

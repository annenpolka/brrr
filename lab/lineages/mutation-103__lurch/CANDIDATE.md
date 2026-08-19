# mutation-103 — lurch

## Primitive

N clock-cuts on stdin; emit one named interval (`SLEEP` / `DILATE` / `STEP` / `REST`) per consecutive pair, each row carrying scarp's leftover columns (`sleep=` / `ntp=`). A Unix filter over a clock log. No spawn.

## Why this might not exist

Ancestor `scarp` (mutation-46) already names the clock that explains a gap. Its buried assumption is **we classify one pair**. `classify_text` parses every cut, then uses `cuts[0], cuts[1]`. A three-cut JSONL that dilates then sleeps is DILATE; the sleep is dropped. Peel `twixt` already streams, but it renamed the leftovers `host_sleep=` / `host_ntp=` and still lets missing rusage invent a 22-day DILATE.

The missing verb is scarp's names on a stream: **every adjacent pair, `sleep=` and `ntp=`**, and a refusal to call 22 days of awake a lid-close.

Discarded: wrap scarp in a loop that peels two lines. That leaves `cuts[0], cuts[1]` in charge. Discarded: twixt's second object (`host_sleep`) as a fifth name. Discarded: leftover-name, inverse-printf, fourth cinch, third ambit.

## How to run

```bash
chmod +x ./lurch
./lurch selftest
./demo.sh 0
./lurch < fixtures/stream-dilate-then-sleep.jsonl
./lurch --explain < fixtures/stream-dilate-then-sleep.jsonl
./lurch < fixtures/unlabeled.txt
./lurch < fixtures/slew-noproper.txt
{ ./lurch cut --json; sleep 0.35; ./lurch cut --json; ./lurch cut --json; } | ./lurch
./lurch cut | ./lurch --explain
```

Python 3.10+, stdlib only. Exit 0 classified, 1 parse / `--require` miss / `--forbid` hit, 2 usage.

## Empirical transcript

### v0.1 (`4fe8d43`) — working stream filter, missing-proper lie

`./lurch selftest` 8/8. `./demo.sh 0` ok. `fixtures/stream-dilate-then-sleep.jsonl` → **DILATE SLEEP**. Ancestor scarp on the same file → **DILATE** only.

```
$ ./lurch < fixtures/stream-dilate-then-sleep.jsonl
DILATE	1000.000000	1002.000000	sleep=0s	ntp=0s
SLEEP	1002.000000	1012.000000	sleep=9.000s	ntp=0s

$ scarp < fixtures/stream-dilate-then-sleep.jsonl
DILATE
```

Same bytes, opposite order (`stream-sleep-then-dilate.jsonl`): lurch **SLEEP DILATE**, scarp **SLEEP**. `/tmp/destroy-scarp/fixtures/huge-1000.jsonl` (1000 cuts, 9s host-sleep on the last pair): lurch 999 names, last **SLEEP**; scarp **REST** (first pair, 1ms). Unlabeled `1000 1001 1005 1010`: lurch **REST REST REST**; scarp **STEP** (duration bag). One thousand unlabeled ticks: 999 REST, not the first eight fields.

twixt on the dilate-then-sleep log already streams, but the leftover columns are not scarp's:

```
$ twixt < fixtures/stream-dilate-then-sleep.jsonl
DILATE	1000.000000	1002.000000	wall=2.000s
SLEEP	1002.000000	1012.000000	sleep=9.000s	host_sleep=9.000s
```

lurch prints `sleep=` and `ntp=` on every pair, including the DILATE row where pair-delta sleep is 0s.

Live Darwin, `{lurch cut --json; sleep 0.35; lurch cut --json; lurch cut --json}`:

```
#0 DILATE  wall=0.431s  sleep=0s  ntp=0s  proper=—
#1 REST    wall=0.038s  sleep=0s
scarp on the whole stream: DILATE
```

Pair names agree with piping pairs into ancestor scarp. The 1d05h03m lid-close sits in every JSON object; pair-delta `sleep=` is 0s. Singleton `lurch cut | lurch` names it: **SLEEP** `sleep=1d05h03m` `ntp=-7.335s`. Folklore `wall + python.monotonic` since boot: **SLEEP**, not STEP. `{cut --boot; cut}`: **SLEEP**. `{cut; sleep 0.35; cut}`: **DILATE**, lurch spawned neither.

Then DESTROYER_SCARP §8 — the 22-day dump with the lid-close still in `sleep=`, proper stripped:

```
$ ./lurch --explain < fixtures/slew-noproper.txt
DILATE  explains=awake  kind=readings
  sleep        1d00h00m
  ntp           -7.500s
  proper              —
  γ                   ∞
reason  world moved ∞× farther than proper (0s / 22d00h00m)
```

Same as scarp. Largest-gap let `awake − 0` (22d) beat `machine − awake` (1d). The 10s sleep fixture without proper stayed SLEEP (`9 > 1`). The laptop-scale dump did not. A 61s zero-origin wait with proper 0.2 was **REST** `kind=host` γ=305: the 60s constant that lets `cut | scarp` stay SLEEP also blessed a timeout author's origin.

### After (v0.2) — missing proper is not the world; zero-origin is not boot

Driven by that transcript, not by twixt's feature list:

1. When rusage is missing, DILATE is not a candidate if SLEEP or STEP already names a gap. `{cut; sleep 0.35; cut}` still DILATEs (no sleep, no step, world moved).
2. `kind=host` only for a live boot→now snapshot (epoch wall / boottime). A 61s duration wait from zero is DILATE.

```
$ ./lurch < fixtures/slew-noproper.txt
SLEEP	0.000000	1900792.500000	sleep=1d00h00m	ntp=-7.500s

$ scarp < fixtures/slew-noproper.txt
DILATE
```

Sitbone-shaped 92s idle with 30s suspend, no proper: **SLEEP** `sleep=30.000s` (v0.1 and scarp: DILATE of 62s awake). Darwin duration dump with POSIX `CLOCK_MONOTONIC` as machine (`/tmp/destroy-scarp/fixtures/posix-monotonic-as-machine.txt`): **SLEEP** (scarp: DILATE). `wait61.txt`: **DILATE** γ=305 (scarp: REST kind=host). Gold paths unchanged: slew-with-proper SLEEP, `{cut; sleep 0.35; cut}` DILATE, live `cut | lurch` SLEEP 1d05h03m, three-cut sandwich DILATE REST.

`./demo.sh 0` exits 0. `selftest 10/10`. lurch 0.2 darwin.

## Dogfood targets

- DESTROYER_SCARP `/tmp/destroy-scarp/fixtures/`: stream-dilate-then-sleep, stream-sleep-then-dilate, huge-1000.jsonl, huge-1000-unlabeled, live-3cut, folklore, posix-monotonic-as-machine.
- Ancestor scarp (`mutation-46`, `subagent-01a01b60-8466-71a3-894a-7bf303f098fd`) on the same bytes: first pair only.
- Peel twixt (`mutation-59`) on the same stream: adjacent names agree; leftover columns do not (`host_sleep=` vs `sleep=`/`ntp=`).
- This Darwin host since `kern.boottime` Tue Jul 28 12:43:57 2026: 22d18h wall/machine, 21d13h awake, **1d5h3m sleep**, **−7.33s** adjtime vs `CLOCK_MONOTONIC_RAW`. Last lid-close still in `kern.sleeptime`/`kern.waketime` (2026-08-19 14:16 → 14:27) and not a column.

## Surprises

- scarp already parsed three JSONL cuts and then threw two of them away. The stream was never a parse problem; it was `len(cuts) >= 2: cuts[0], cuts[1]`.
- twixt's `host_sleep=` is a different object from scarp's `sleep=`. A live 0.35s sandwich has pair-delta sleep 0s and 29h of lid-close inside every cut. Printing scarp names on every pair makes that distinction awkable without a fifth name.
- The 10s sleep fixture without proper was already SLEEP under largest-gap (`9 > 1`). The lie only shows up at laptop scale: 22d of missing rusage beats 1d of lid-close. That is why v0.1's selftest was green.
- `kind=host` at `machine≈0 ∧ end>60s` is how `cut | scarp` stays SLEEP. It is also how a 61s timeout wait becomes REST at γ=305.

## Failures

- Host SLEEP still cannot be live-tested as a *lid close during this command* without closing the lid; since-boot plus `kern.sleeptime` is the dogfood. Pair-delta of live cuts is 0s of sleep.
- Two wall timestamps from `date +%s` cannot distinguish SLEEP from STEP from DILATE. REST is honest.
- ISO-8601 / `date(1)` still scavenge digits via `NUM_RE`. v0.2 names them as a stream of REST ticks, not one invented STEP — still not fail-closed.
- Repeated interleaved `key=value` (`wall=0 / wall=10 / machine=0 / machine=10`) still splits on the second wall; machine never shares a pair. Not a tracer.
- `proper` from two different `lurch cut` processes is discarded. REST of a CPU hog has to come from cuts the work itself wrote.
- Linux `CLOCK_BOOTTIME` is selected, not dogfooded tonight.

## Suggested mutations

- Fail closed on ISO-8601 / `date(1)` (exit 1) instead of scavenging a REST stream.
- Repeated `key=value` keeps both timestamps of that key (sibling of reimpl-08 scree).
- Name Darwin `CLOCK_MONOTONIC` vs RAW as SLEW, not `ntp=` (sibling of yaw).
- Line-buffered JSONL (emit pair i as cut i+1 arrives).
- Collapse runs: `DILATE REST REST DILATE` → gait of a log.
- Do not grow a tracer.

## Kill / keep

Keep. The flip vs scarp is real: three JSONL cuts emit two names, 1000 cuts emit 999, and the leftover columns on each row are still `sleep=` / `ntp=`. The flip vs twixt is the same names plus the 22-day-awake refusal: missing rusage is not DILATE of the world, and a 61s zero-origin wait is not a boot marker. `{cut; sleep; cut; cut} | lurch` is DILATE REST without spawn. `slew-noproper` is SLEEP. That is not `uptime(1)`, not `time(1)`, and not a first-pair filter.

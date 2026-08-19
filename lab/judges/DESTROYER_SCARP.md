# DESTROYER — scarp

Adversarial pass on the clock-cut filter that names which clock explains a gap. No rewrites: the failures are conceptual. The gold path still works; the lies are the object it claims to name (`ntp`), the window it claims to consume (two cuts), and the parser it claims is a Unix filter over a log.

- **scarp** (mutation-46) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b60-8466-71a3-894a-7bf303f098fd`
- Transcript: `/tmp/destroy-scarp/transcript.txt`
- Follow-up: `/tmp/destroy-scarp/followup.txt`
- Fixtures: `/tmp/destroy-scarp/fixtures/`
- Attack driver: `/tmp/destroy-scarp/attack.py`
- Peels read, not re-destroyed as clones: **twixt** (stream), **yaw** (kernel slew), **reimpl-08 scree** (repeated `key=value`)
- `python3 ./scarp selftest` → `7/7 passed  backend=darwin  scarp 0.2` after the attacks. `./demo.sh 0` → `demo 0 ok`. No rewrite of the victim.

Attacks: lid-close vs NTP vs kernel slew, unlabeled ticks, repeated key=value, Darwin `time.monotonic` leftovers, huge clock logs, malformed pairs, `host_sleep` / unused `kern.sleeptime`, two cuts vs stream.

Verdict: **mutate, do not kill.** `{cut; sleep 0.35; cut} | scarp` is still DILATE without spawn. `fixtures/slew.txt` is still SLEEP, not STEP. `wall + python.monotonic` since boot is still SLEEP, not a 29-hour NTP step. The attacks show where `ntp=` is adjtime slew (wall−boot tracks POSIX `CLOCK_MONOTONIC` to ~0.1µs), where a log is `cuts[0], cuts[1]`, where unlabeled numbers are a duration bag or the first eight fields, and where missing proper time lets 22 days of awake beat 1 day of lid-close.

---

## Primitive restated

Two timestamps or two clock-cuts on stdin; emit which clock explains the gap (`SLEEP` / `DILATE` / `STEP` / `REST`). A Unix filter. No spawn. Wall is NTP, machine is `CLOCK_MONOTONIC_RAW`, awake is `CLOCK_UPTIME_RAW`, proper is CPU. Largest disagreement wins. On Darwin, `time.monotonic()` is awake.

---

## 1. Lid-close vs NTP vs kernel slew — `ntp=` is adjtime, not NTP (conceptual, load-bearing)

Live Darwin, same second as `scarp cut | scarp --json`:

```
CLOCK_REALTIME − kern.boottime     1966991.599038s   22d18h23m
CLOCK_MONOTONIC                    1966991.599038s   POSIX; sleep + adjtime
CLOCK_MONOTONIC_RAW                1966998.931727s   unslewed; sleep
CLOCK_UPTIME_RAW                   1862363.483929s   unslewed; pauses
time.monotonic()                   1862363.483929s   Darwin: UPTIME_RAW
MONOTONIC − RAW                    -7.332689s        kernel slew
(wall−boot) − RAW                  -7.332689s        scarp's ntp field
(wall−boot) − MONOTONIC            +1.24e-7s         true step ≈ 0
RAW − UPTIME_RAW                   104635.448s       1d05h03m lid-close
```

```
$ ./scarp cut | ./scarp --explain
SLEEP  explains=machine  kind=host
  sleep        1d05h03m   machine − awake
  ntp           -7.333s   wall − machine
reason  host slept 1d05h03m (5% of coordinate)
```

`ntp=-7.333s` matches `CLOCK_MONOTONIC − CLOCK_MONOTONIC_RAW` to a microsecond. Wall−boot tracks POSIX `CLOCK_MONOTONIC`, not RAW. Peel yaw on the same host: default pair **SLEW**, `CLOCK_REALTIME` vs `CLOCK_MONOTONIC` **REST**, `CLOCK_REALTIME` vs RAW **SLEW**. scarp has no SLEW name. The 50 ppm floor (`step_min ≈ 98s` on this 22-day boot) is why the 7.3s does not flip the verdict to STEP — it is also why the field can keep the name `ntp` while being below the floor that would make a step.

Wall vs RAW since boot, no awake (the pair the field subtracts):

```
$ printf 'wall 0 %s\nclock_monotonic_raw 0 %s\n' "$WALL_BOOT" "$RAW" | ./scarp --explain
REST  explains=agree  kind=host
  ntp           -7.333s   wall − machine
reason  clocks agree (or the interval is too small to split)
```

The leftover scarp prints as NTP, it classifies as agreement. Feed POSIX `CLOCK_MONOTONIC` as machine (Darwin `role_of("clock_monotonic")` → `machine`):

```
ntp when machine=POSIX MONOTONIC:  +0s
sleep:                             1d05h03m   (7.3s short; slew folded into sleep)
primary:                           DILATE     (no proper; see §8)
```

The Darwin lie v0.2 closed is "monotonic → machine, 29h STEP". The leftover lie is "wall − RAW = NTP". Last lid-close on this host is sitting in `kern.sleeptime`/`kern.waketime` (2026-08-19 14:16 → 14:27, 672s) and is not a column.

Not a peel rewrite. yaw already named the object. scarp still ships the field.

---

## 2. Unlabeled ticks — a clock log is a duration bag or the first eight fields (conceptual, load-bearing)

v0.2 claims two unlabeled timestamps are REST, not DILATE. That pair survived:

```
$ printf '1000\n1001\n' | ./scarp
REST
# wall=1.000s, machine=—, sleep=0s
```

A timeout log is not two numbers.

```
$ printf '1000\n1001\n1005\n1010\n' | ./scarp --explain
STEP  explains=wall  kind=readings
  wall        16m40.00s
  machine     16m41.00s
  awake       16m45.00s
  proper      16m50.00s
reason  wall backward-stepped 1.000s vs machine
```

Four wall ticks became one duration record `wall=1000, machine=1001, awake=1005, proper=1010`. Three ticks `0 1 2` → **DILATE** (proper invented as missing, `ntp=-1s`, `sleep=-1s`). Five / six / seven: `rc=1  need 2, 3, 4, or 8 unlabeled numbers`.

Epoch log, the thing `date +%s` actually writes. Four stamps `now, +1, +5, +10` are all `> 1e9`, so `_from_bare` takes them as interleaved wall/machine pairs:

```
wall  now → now+5     = 5s
machine now+1 → now+10 = 9s
→ DILATE  ntp=-4.000s  machine=9.000s  sleep=0s
```

Eight epoch ticks 1s apart → **REST**, `wall=machine=awake=proper=4s`. One thousand unlabeled ticks `1000..1999` is the same REST 4s: `len >= 8` keeps **the first eight numbers as two 4-field cuts** and drops 992 ticks. Porcelain:

```
clock  wall      4.000000
clock  machine   4.000000
clock  proper    4.000000
clock  ntp       0.000000
```

Peel twixt on four unlabeled ticks: `REST REST REST`. Ancestor scarp: `STEP`. Confirmed tonight. A stream of one clock is not an NTP step, and scarp still says it is — or says REST 4s and throws the rest of the log away.

---

## 3. Repeated `key=value` — interleaved pairs overwrite; blank lines are the real parser (conceptual)

reimpl-08 scree already recorded this as a beat against the ancestor. Still REST:

```
wall=0
wall=10
machine=0
machine=10
awake=0
awake=1
```

```
$ ./scarp --explain < repeat-kv.txt
REST  explains=agree  kind=interval
  wall          10.000s
  machine             —
  awake               —
reason  clocks agree
```

Each repeated role with Δ > 50ms `push()`es a new cut. `classify_text` then uses `cuts[0], cuts[1]` only: `Cut(wall=0)` vs `Cut(wall=10, machine=0)`. Machine/awake never share a pair. The 9s sleep the human wrote is gone.

The same numbers as two snapshots, blank line or `---` between them, or even no blank if the second `wall` follows a completed first snapshot, **are SLEEP**. The parser's object is "role seen in this cut", not "each key keeps both timestamps". A logger that emits `wall= t0` / `wall= t1` / `machine= t0` / `machine= t1` — the natural `key=value` stream — is REST.

Alias of the same snapshot within 50ms does not split (`time` next to `wall`). 200ms apart does, and then only the wall delta survives → REST 0.200s. `CLOCK_MONOTONIC` then `CLOCK_MONOTONIC_RAW` are both `role=machine` on Darwin, 7.333s apart → split → **DILATE 7.333s**, 29 hours of lid-close discarded.

---

## 4. Darwin `time.monotonic` — v0.2 mapping holds; alias-split and POSIX MONOTONIC do not (conceptual)

Gold folklore pair still SLEEP:

```
wall <kern.boottime> <time.time()>
monotonic 0 <time.monotonic()>
→ SLEEP  explains=awake  kind=host
  machine  —
  sleep    1d05h03m
  ntp      —
```

JSON `python_monotonic` next to `machine` does not clobber RAW. `python_monotonic_role=awake` on `scarp cut`. That is closed.

Leftover: `python.monotonic` is an awake **alias**. A TSV cut with `python.monotonic` 200ms off `awake` (two samples, not one snapshot) is Δ > 50ms on the same role, so the snapshot splits. `cuts[0], cuts[1]` become (full cut) vs (awake-only):

```
DILATE  explains=awake  kind=interval
  wall         —
  machine      —
  awake        0.200s
  sleep        0s
```

29 hours of `machine − awake` sat in cut 0 and never became a column. Pair-delta is the only object; snapshot host-sleep is not (see §7).

One snapshot that names every Darwin clock (`CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_MONOTONIC_RAW`, `CLOCK_UPTIME_RAW`, `time.monotonic`, `boottime`) is the same split: MONOTONIC and RAW both map to `machine`, 7.333s apart, **DILATE 7.333s**, `sleep=0s`. The filter that exists to name this host's lid-close cannot ingest a full Darwin clock dump.

---

## 5. Huge clock logs / two cuts vs stream — `len(cuts) >= 2: cuts[0], cuts[1]` (conceptual, load-bearing)

scarp already parses three JSONL cuts. It then throws two of them away. Peel twixt exists because of this line. Confirmed on the victim, not on the peel.

```
# SLEEP pair, then DILATE pair
{"wall":1000,"machine":100,"awake":80,"proper":1,"pid":1}
{"wall":1010,"machine":110,"awake":81,"proper":1,"pid":1}
{"wall":1012,"machine":112,"awake":83,"proper":0.01,"pid":1}
→ scarp: SLEEP          (pair 1 dropped)
```

```
# DILATE pair, then SLEEP pair (lid-close later in the log)
… 2s world, proper 0.01 …
… then machine +10s, awake +1s …
→ scarp: DILATE         (the sleep is gone)
→ twixt: DILATE SLEEP   (peel; not a clone)
```

1000-cut JSONL, REST 1ms between the first two rows, 9s host-sleep on the last pair: **REST**, 0.045s. Parse is cheap. The window is two.

Live Darwin, `{scarp cut --json; sleep 0.35; scarp cut --json; scarp cut --json}`:

```
scarp on the whole stream:  DILATE  wall=0.398s  sleep=0s
scarp on pair 0–1:          DILATE  wall=0.398s  sleep=0s
scarp on pair 1–2:          REST    wall=0.041s  sleep=0s
each snapshot:              machine−awake = 104635.448s   (1d05h03m sitting in the JSON)
                            (wall−boot)−machine = −7.333s
```

The laptop's lid-close is in every object and in no verdict. Pair-delta sleep is 0s. That is not a bug in the 0.35s sandwich (that DILATE is the demo). It is the claim "consume two clock-cuts" applied to a log that has three, and to snapshots that already contain since-boot sleep.

60ms intended back-to-back `scarp cut` (different pids; wall dt 0.110s because process startup):

```
DILATE  wall=0.110s  proper=—  γ=∞
pids 55459 55481   proper 0.034s / 0.034s  (discarded: pids differ)
```

Selftest REST is two `cut_now()` calls in **one** process. The advertised filter cannot REST two of its own cuts once spawn is slower than `SLEEP_MIN`/`0.05s`. Proper from two `scarp cut` processes is defined to be discarded. Any `{cut; cut}` over 50ms is therefore DILATE. The 0.35s demo is that case, on purpose; the 110ms case is the same object, not "the world idled."

---

## 6. Malformed pairs — the lexer is a number scavenger (conceptual)

Exit 1 on `hello`, empty `wall=`, `wall NaN`, binary `\x00\xff` is honest. Empty stdin is rc=2 plus usage. That survived.

Paste what a human actually has:

```
$ printf '2026-08-20T07:15:00Z 2026-08-20T07:16:00Z\n' | ./scarp --explain
STEP  explains=wall  kind=host
  wall       -33m31.00s
  machine        8.000s
  awake       34m06.00s
  ntp        -33m39.00s
reason  wall backward-stepped 33m39.00s vs machine
```

`NUM_RE` lifted `2026, -08, -20, 07, 15, 00, …` into eight duration fields. `kind=host` fired because a.awake ≤ 0.01 and b.awake > 60. One minute of ISO-8601 is a 33-minute backward NTP step.

```
$ printf 'Thu Aug 20 07:15:00 JST 2026\nThu Aug 20 07:16:00 JST 2026\n' | ./scarp --explain
STEP  explains=wall  kind=interval
reason  wall forward-stepped 33m13.00s vs machine
```

`date(1)` two lines, same invented step. `wall 1000 1001 1002` does not match `KV_RE` (`\s*$` after two numbers), so the three digits fall through to unlabeled → **DILATE**, `wall=16m40s`. Broken JSON `'{"wall": 1, "machine":'` → `need 2, 3, 4, or 8 unlabeled numbers, got 1`. CSV `10,10,1,1` accidentally **SLEEP** (four unlabeled durations). Same-line `wall: 10, machine: 10, awake: 1, proper: 1` accidentally **SLEEP**. A parser that is a number bag will bless a CSV and curse an ISO stamp, and both look like classification.

JSONL mixed with leftover `wall 2000` lines: JSONL parse returns None the moment a non-`{` line appears after a JSON line; pairs then win; **REST**. Porcelain of a honest REST 1s wall fills missing clocks with `0.000000` (`g.wall or 0`). Feed it back:

```
$ printf '1000\n1001\n' | ./scarp --porcelain | ./scarp --explain
STEP  explains=wall  kind=readings
  ntp           +1.000s
reason  wall forward-stepped 1.000s vs machine
```

A Unix filter whose porcelain is not invertible. JSON keeps `null` and round-trips; porcelain does not. `--json` also emits `backend.wall=0, backend.machine=4, backend.awake=8` (the `CLOCK_*` integers). Harmless tonight because `clock` is merged first; it is still a second clock-id object on a duration payload.

---

## 7. `host_sleep` / `kern.sleeptime` — collected, never classified (conceptual, load-bearing)

`scarp cut --json` emits `sleeptime` and `waketime`. `classify` never reads them. Two JSON cuts with `sleeptime` advanced +60s, `waketime` advanced +60s, and `machine − awake` unchanged:

```
DILATE  wall=1m00.00s  sleep=0s  ntp=+0s
reason  world moved ∞× farther than proper
```

The kernel's own last-nap interval (sleeptime 14:16:36 → waketime 14:27:48) is on the live TSV and absent from porcelain. Porcelain of `scarp cut | scarp` has `clock sleep 104635` (since-boot RAW−UPTIME) and no sleeptime column.

`--require SLEEP` on `scarp cut` exits 0 on this laptop for as long as the host has ever napped since boot. The same flag on `{cut; sleep 0.35; cut}` exits 1 (`DILATE`). The suggested CI mutation "fail if a test interval contains SLEEP" cannot be this `--require`: the default one-cut path is since-boot, not the interval. Sitbone's `drift_timeout` (92s idle → AWAY) as two wall ticks is **REST**. Wall + `monotonic` 92s with a 30s lid-close in RAW is **DILATE** (`sleep=30s` printed, primary DILATE because missing proper; §8). The dogfood trees (kizu, sitbone, tenaoshi, voidtrace) have no clock-cuts. sitbone has timeout *reasons*, not clock-cuts. scarp cannot be pointed at those repos and name a lid-close.

kind=host is not a boot marker. It fires when `a.machine ≤ 0.01` and `b.machine > 60` (or the same on awake). A process that zeros origin and waits:

```
machine 0 / awake 0 / proper 0
---
machine 61 / awake 61 / proper 0.2     → REST  kind=host  γ=305
machine 59 / …                         → DILATE kind=interval
machine 60.01, no proper on cut 0      → REST  kind=host
```

59s of wait is dilation. 61s of wait is "this is a host, clocks agree." The 60s constant is the other half of `SLEEP_MIN=0.05`. DILATE is suppressed for `kind=host` so `scarp cut | scarp` can stay SLEEP. The same suppression turns a 61s timeout author's zero-origin pair into REST.

---

## 8. Largest-gap vs missing proper — 22 days of awake beats 1 day of sleep (conceptual, load-bearing)

`fixtures/slew.txt` is SLEEP because it includes `proper 1814400`. Strip proper:

```
$ printf 'wall 1900792.5\nmachine 1900800\nawake 1814400\n' | ./scarp --explain
DILATE  explains=awake  kind=readings
  sleep        1d00h00m
  ntp           -7.500s
  γ                ∞
reason  world moved ∞× farther than proper (0s / 22d00h00m)
```

DILATE magnitude is `awake − 0 ≈ 22d`. SLEEP magnitude is `1d`. Largest disagreement wins — the rule that saved 29h lid-close from 7.5s slew now names **missing rusage** as the gap. The 10s sleep fixture without proper stays SLEEP (`9 > 1`). The laptop-scale dump without proper does not.

`scarp cut | scarp` survives only because `_looks_absolute` (wall > 1e9) sets `kind=host`, fills `proper = awake`, and skips the DILATE candidate. Duration-style host readings (wall already minus boot) do not look absolute. CLOCK_MONOTONIC-as-machine on this host, duration-style, no proper: **DILATE**, `ntp=+0s`, sleep still printed as 1d05h03m.

Sitbone-shaped 92s idle with RAW showing 30s suspend, no proper: **DILATE**, `sleep=30.000s`. The lid-close is a column and not the name.

Two `date +%s` values (boot, now): **REST** `wall=22d18h23m`, `sleep=0s`. CANDIDATE already said this. Confirmed. One epoch + one small unlabeled: **REST**, `wall=-20684d`, `γ=-1.79e18`. Origin mix is not a parse error.

Negative sleep (`awake > machine`) does not fire SLEEP (`sleep >= 0.05`). `wall 10 / machine 1 / awake 10` → **STEP** 9s (NTP), not "clocks ran backwards."

---

## What survived

- Gold fixtures: sleep/step/dilate/rest/slew named correctly. `slew.txt` SLEEP, `--require STEP` rc=1, `--require SLEEP` rc=0.
- `printf '1000\n1001\n' | scarp` → REST.
- `{cut --json; sleep 0.35; cut --json} | scarp` → DILATE, scarp spawned neither.
- In-process busy 0.28s two cuts, same pid → REST (demo).
- Live Darwin `scarp cut | scarp` → SLEEP 1d05h03m, not STEP. `python.monotonic` does not clobber RAW on a single snapshot.
- Folklore `wall + monotonic` since boot → SLEEP, `ntp=—`.
- `{cut --json --boot; cut --json} | scarp` → SLEEP.
- Blank-separated (or sequential) two snapshots of the sleep fixture → SLEEP.
- No spawn: `subprocess` not imported. `selftest` 7/7. `demo.sh 0` ok. scarp 0.2 darwin.
- JSON of a gap round-trips better than porcelain. Nested `{"clock": {wall, machine, awake, proper}}` still SLEEP.

Nothing in this battery turned the filter into `time(1)` or into lapse-with-Popen. Do not kill because `ntp` is misnamed, because JSONL is a pair, or because ISO stamps scavenge digits.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still "two cuts, which clock owns the leftover." 29 hours of lid-close on `scarp cut | scarp` is SLEEP. 7.5s in 22 days is not STEP. `{cut; sleep; cut}` is DILATE without exec. Two unlabeled timestamps are REST. That is not `uptime(1)`, not `time(1)`, and not lapse. Killing it would throw away a real filter to hide a field name and a two-row window.

Peels already hold the next verbs: yaw names SLEW (POSIX `CLOCK_MONOTONIC` vs RAW); twixt names adjacent pairs; reimpl-08 scree already keeps both timestamps of a repeated key. Those are mutations, not proof the ancestor is dead.

| do not kill because | mutate toward |
| --- | --- |
| Live `cut \| scarp` SLEEP 1d05h03m; slew fixture SLEEP not STEP; folklore wall+`time.monotonic` SLEEP not 29h STEP; `{cut; sleep 0.35; cut}` DILATE no spawn; two timestamps REST | **`ntp` is not NTP.** STEP is wall vs already-slewed POSIX `CLOCK_MONOTONIC`. wall−RAW with step≈0 is SLEW (adjtime). Keep RAW as machine so lid-close stays visible; stop printing the 7.3s as `ntp=`. |
| | **A log is adjacent pairs, not `cuts[0], cuts[1]`.** Three JSONL cuts must emit two names. 1000 unlabeled ticks are 999 REST intervals of one clock, not eight duration fields. Do not become a tracer. |
| | **Unlabeled numbers are timestamps of one clock**, never a bag of `{wall, machine, awake, proper}`. Epoch-sized four-ticks must not become wall+machine pairs because `> 1e9`. |
| | **Repeated `key=value` keeps both timestamps of that key.** Interleaved `wall=0 / wall=10 / machine=0 / machine=10` is the sleep pair, not REST of wall only. |
| | **Snapshot `host_sleep` / `kern.sleeptime` is not pair-delta sleep.** Live JSON already has 1d05h03m in every row; print it as a carried column (twixt v0.2) or refuse to call `scarp cut` an interval of this command. `--require SLEEP` on since-boot is not a CI flake gate. |
| | **Missing proper is not DILATE of the whole world.** Largest-gap must not let `awake − 0` beat lid-close on a 22-day dump. kind=host at `machine≈0 ∧ end>60s` is not a boot marker; a 61s zero-origin wait is still DILATE. |
| | **Porcelain 0 is not a missing clock.** Round-trip REST 1s wall must stay REST. ISO-8601 / `date(1)` are not eight duration fields; fail closed (exit 1) instead of inventing a 33-minute STEP. |
| | **`CLOCK_MONOTONIC` is not `machine` on Darwin.** It is the slew witness. Mapping it onto RAW's role splits a snapshot or hides NTP. Python `time.monotonic` stays awake. |

A one-line `ntp` rename to `slew` would hide the Darwin leftover without touching the two-cut window, the unlabeled bag, or porcelain 0-fill. Not applied.

Do not grow a tracer. The next mutation is *pair-honest logs* plus *slew as a fifth name*, not a prettier `--explain`.

# mutation-33 — lede

## Primitive

Inverse printf as a **filter that binds names only on a prefix of an instance**. Later holes stay unbound. A leftover later fragment is a miss, never stuffing for the last hole.

## Why this might not exist

stump (mutation-23, hardened invert) harvested truncated logs as inverse-printf. DESTROYER_STUMP_PIN showed the kernel was still leftmost `query.find(literal)` plus “if the next literal is missing, the rest of the query is the last hole.” That is not prefix-of-instance.

```
$ rg -n -g '*.swift' awayRecovered fixtures | ./stump --templates - \
    'transition focused → idle awayRecovered=0'
  {from} = focused
  {to} = idle awayRecovered=0          # lie
  truncated:  reason={reason} idle={idle}s …
```

`awayRecovered=0` is a later fragment. A human who copied the start and the end of a log line got a **wrong binding**, not a miss. Terminal wrap did the same to `{reason}`. `--exact` refuses both and also refuses ordinary log prefixes. There was no “prefix-of-instance only” mode.

The conventional patch is `if truncated and not bindings: return None`. DESTROYER already said that hides the no-binding prefix and does not touch middle-drop stuffing. The missing verb is still the stream filter, just one whose truncated match **is** a prefix of some instance.

Discarded: grow a rustc parser; walk the tree; silently complete truncated holes from later literals; one-line no-bindings guard.

## How to run

```bash
chmod +x lede
./lede --selftest
./demo.sh
rg -n --type swift 'awayRecovered' /path | ./lede 'transition focused → idle reason=timeout idle=12s'
rg -n --type swift 'awayRecovered' /path | ./lede 'transition focused → idle awayRecovered=0'
rg -n --type rust 'format!|anyhow!' /path | ./lede '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
./lede --templates src.rs -e '   --> src/git/revert.rs:46:18'
./lede --templates extracted.txt --any < build.log
./lede --templates extracted.txt --any --complete < build.log
```

Exit 0 = every argument matched (stdin / `--any`: any line, and `--any` stops after the first hit; `--any --complete` skips truncated). Exit 1 = miss. Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2; the tool will not walk.

## Empirical transcript

### v0.1 working prototype

Copied stump's stream ingest. Changed the kernel: when the next literal is missing, leftover may be a hole value plus a prefix of that literal — **not** a later static swallowed by the hole. A first-literal prefix with no bindings is not a hit. rustc locators, `--any`, binary stdin, decoy ranking unchanged.

`./lede --selftest` → `selftest: ok`

`./demo.sh` → `passed=61 failed=0` (stump's 59 plus middle-drop and newline-wrap).

```
$ rg -n -g '*.swift' awayRecovered fixtures | ./lede --templates - \
    'transition focused → idle awayRecovered=0'
— no template for: transition focused → idle awayRecovered=0
# rc=1  (stump bound {to}=idle awayRecovered=0)

$ rg -n -g '*.swift' awayRecovered fixtures | ./lede --templates - \
    'transition focused → idle reason=timeout idle=12s'
fixtures/src/log.swift:20:27: score=0.91 holes=7 via=truncated
  {from} = focused
  {to} = idle
  {reason} = timeout
  {idle} = 12
  truncated:  deserted={0} driftRecovered={0} awayRecovered={0}

$ ./lede --templates fixtures/src/user.py 'cannot reach'
— no template for: cannot reach     # no bindings; not a hit

$ ./lede --templates fixtures/src/prefix.rs \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
prefix.rs:7:13: score=0.39 holes=1 via=span
  {cmd} = git ap
  prefix: 2026-08-19T23:50:01Z ERROR
  truncated: `
```

sitbone abridged 7-hole still binds `{oldPhase.rawValue}=focused` … `{idle}=12` with `truncated:`. kizu `--> src/git/revert.rs:46:18` is still a locator.

### Failures that drove the first improvement

v0.1 closed stuffing and then lied in two other places the primitive had just made visible:

1. Header `holes=7 via=truncated` after binding four names. The later holes are unbound — that is the point — but the header still advertised the template's hole count. A reader of the DESTROYER transcript would think seven holes bound.
2. `{ echo 'user 42 not'; echo 'ERROR [worker] user 7 not found'; } | ./lede --any` still stopped on the truncated first line. `--exact` refuses that *and* refuses timestamp span (`2026-08-19T23:50:01Z ERROR failed to spawn \`git apply --reverse\``). DESTROYER asked for a knob that is “first complete instance” without killing span.

### After the improvement (v0.2)

Header is `holes=bound/total` when they differ, plus an `unbound:` line of later names. `--complete` refuses truncated matches and keeps span leftover. `--any --complete` skips truncated lines silently (does not print `— no template for`) and stops on the first complete instance.

`./lede --selftest` → `selftest: ok`

`./demo.sh` → `passed=63 failed=0`

```
$ rg -n -g '*.swift' awayRecovered fixtures | ./lede --templates - \
    'transition focused → idle reason=timeout idle=12s'
fixtures/src/log.swift:20:27: score=0.91 holes=4/7 via=truncated
  {from} = focused
  {to} = idle
  {reason} = timeout
  {idle} = 12
  unbound: {0} {0} {0}
  truncated:  deserted={0} driftRecovered={0} awayRecovered={0}

$ rg -n --type swift 'awayRecovered' ~/src/sitbone | ./lede \
    'transition focused → idle reason=timeout idle=12s'
SitboneCore.swift:554:35: score=0.89 holes=4/7 via=truncated
  {oldPhase.rawValue} = focused
  {newPhase.rawValue} = idle
  {reason.name} = timeout
  {idle} = 12
  unbound: {counters.deserted.value} {counters.driftRecovered.value} {counters.awayRecovered.value}

$ { echo 'user 42 not'; echo 'ERROR [worker] user 7 not found'; } \
    | ./lede --templates fixtures/src/user.py --any --complete
user.py:2:20: score=0.51 via=span
  {uid} = 7
  prefix: ERROR [worker]
# first line not printed; not {uid}=42

$ ./lede --templates fixtures/src/prefix.rs --complete \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
  {cmd} = git apply --reverse
  prefix: 2026-08-19T23:50:01Z ERROR
# --exact still refuses this span
```

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/` | `rg -g`, `--templates` file | middle-drop / wrap / truncated 7-hole / `{uid}` / spawn, rustc locator, prefix.rs decoy, 3000-line `--any`, binary stdin |
| `…/kizu` | `rg 'failed to spawn'`, `format!\|anyhow!` | truncated spawn, timestamp span, rustc locator refuse |
| `…/sitbone` | `rg awayRecovered` | full 7-hole + abridged prefix |
| `…/voidtrace`, `…/tenaoshi` | existing invert dogfood | still pass |

## Surprises

- `transition focused → idle` (no later keys) **is** a prefix and must hit, with `{to}=idle` and later holes unbound. The later-fragment check, not “undelimited middle holes miss”, is what separates that from `… idle awayRecovered=0`.
- `{idle}=12` still works because leftover `12s` ends on a prefix of `s deserted=`. That is alignment, not guesswork. stump already had this; the new kernel keeps it and only refuses when the leftover contains a later static (`awayRecovered=`).
- `cannot reach` (12-char first-literal prefix, no hole entered) is now a miss. `cannot reach db` is still a prefix of an instance and still binds `{host}=db`.

## Failures

- Adjacent concatenation (`"open " + path`) is still not one template (sibling mutation).
- Interpolated tail only (`fatal: not a git repository`) still does not find `git diff single file failed: {1}`. Truncation is a *prefix* of an instance, not a suffix-only hole.
- `--any` without `--complete` still stops on the first truncated hit (the default is still “first prefix”). `--complete` is the complete-instance knob; it does not change decoy-prefix ranking.
- Exact decoy `2026-08-19T23:50:01Z ERROR failed to spawn` still beats a missing holed spawn when the query has no leftover `` `{cmd}` ``.
- Compiler *messages* (`error: {e}`) still bind; only rustc locators are refused.
- `MAX_FILE_BYTES = 2_000_000` still omits a godfile with no warning.
- Dynamic format strings remain invisible.

## Suggested mutations

- Reconstruct a chain of templates from `truncated:` remainder + `prefix:` leftover.
- Stable names on fixture `\(0)` holes (three `{0}` is extract, not alignment).

## Kill / keep

**Keep.** The flipped assumption is visible: middle-drop is a miss; abridged syslog prefixes still bind; later holes stay unbound. Do not grow a rustc parser or a walker. Do not hide §2 with a one-line no-bindings guard and call stuffing fixed.

## What the flipped assumption bought and lost

**Bought**

- Start+end pastes no longer hallucinate a hole value.
- Newline wrap no longer stuffs the rest of the line into `{reason}`.
- A static prefix of a holed template with no bindings is not inverse-printf.
- Real truncated 7-hole / `{uid}` / spawn prefixes still bind names.
- `holes=4/7` + `unbound:` makes the later holes visible. `--any --complete` is first complete instance without killing span.

**Lost**

- Queries that are *not* prefixes (middle-drop, wrap-as-newline) miss. That is the point.
- `cannot reach` no longer scores 0.86 as a 2-hole truncated hit.

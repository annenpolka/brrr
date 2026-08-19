# mutation-23 — stump

## Primitive

Inverse printf as a **filter that binds names**, including when the runtime string is a **prefix of an instance**. Same stream contract as invert (runtime string on argv/stdin, templates on the other channel, no walk). Truncation is reported. rustc locators are refused. `--any` stops. Binary stdin fails closed. A no-hole prefix of the paste cannot beat a holed source template.

## Why this might not exist

invert (mutation-15) harvested unfmt-13's names + span into sluice's stream. Destroyers then showed five places the primitive pretended to be more than it was:

1. An abridged 7-hole paste (`idle=12s` without `deserted=…`) was a miss. Real logs are truncated by syslog, terminal wrap, and humans. Invert inverse-printfs a complete instance only.
2. `--> src/git/revert.rs:46:18` bound `format!("src/{i}.rs")` as `{i}=git/revert`. A compiler locator is a different grammar.
3. `--any` only flipped the exit code. 10 MB of identical log lines printed 98 MB of identical hits.
4. Binary stdin raised `UnicodeDecodeError` instead of failing closed.
5. A documentation decoy `2026-08-19T23:50:01Z ERROR failed to spawn` (no holes, prefix of the paste) outranked `failed to spawn `{cmd}``.

The conventional patch is "lower MIN_SCORE / catch UnicodeDecodeError / add `--prefix`". The missing verb is still the stream filter, just one that treats a truncated instance as a **prefix match with a remainder**, and that will not let a static prefix steal a binding.

Discarded: grow a rustc parser; walk the tree; silently complete truncated holes from later literals.

## How to run

```bash
chmod +x stump
./stump --selftest
./demo.sh
rg -n --type swift 'awayRecovered' /path | ./stump 'transition focused → idle reason=timeout idle=12s'
rg -n --type rust 'format!|anyhow!' /path | ./stump '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
./stump --templates src.rs -e '   --> src/git/revert.rs:46:18'
./stump --templates extracted.txt --any < build.log
```

Exit 0 = every argument matched (stdin / `--any`: any line, and `--any` stops after the first hit). Exit 1 = miss. Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2; the tool will not walk.

## Empirical transcript

### v0.1 working prototype

Copied invert's stream ingest. Changed the kernel: `_align_parts` may stop on a prefix of a later literal or inside a hole; `truncated:` prints the unmatched tail. rustc `-->` / `error[E0308]` are locators. No-hole templates with leftover query text do not hit. `--any` prints one hit. Stdin decodes UTF-8 or exits 2.

`./stump --selftest` → `selftest: ok`

`./demo.sh` → `passed=59 failed=0` after regressions.

```
$ rg -n -g '*.swift' awayRecovered fixtures | ./stump --templates - \
    'transition focused → idle reason=timeout idle=12s'
fixtures/src/log.swift:20:27: score=0.91 holes=7 via=truncated
  tmpl:  transition {from} → {to} reason={reason} idle={idle}s deserted={0} …
  {from} = focused
  {idle} = 12
  truncated:  deserted={0} driftRecovered={0} awayRecovered={0}

$ rg -n -g '*.py' 'f"' fixtures | ./stump --templates - 'user 42 not'
  tmpl:  user {uid} not found
  {uid} = 42
  truncated:  found

$ ./stump --templates fixtures/src/prefix.rs -e '   --> src/git/revert.rs:46:18'
— rustc locator, not a template query: --> src/git/revert.rs:46:18

$ ./stump --templates fixtures/src/prefix.rs \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
prefix.rs:7:13: score=0.48 holes=1 via=span
  tmpl:  failed to spawn `{cmd}`
  {cmd} = git apply --reverse
  prefix: 2026-08-19T23:50:01Z ERROR
# the no-hole decoy on line 3 does not appear
```

### Failures that drove the first improvement

Truncated spawn with a timestamp scored **0.33** (default `--min-score` 0.34) against a `--templates` file, so the fixture regression missed while the grep-hydrated kizu dogfood (hint_line +0.06) passed. Remainder of `failed to spawn `{cmd}`` re-emitted the bound hole: `truncated: {cmd}``. `--any` still slurped every query line before printing one.

### After the improvement (v0.2)

Truncated penalty 0.10 → 0.04 so a timestamp wrapper plus a clipped command still clears 0.34. Remainder starts at the unmatched literal, not the already-bound hole. `--any` reads stdin **line by line** and stops after the first hit — a producer that sleeps 6s after one matching line is inverted in **0.05s**.

```
$ ./stump --templates fixtures/src/prefix.rs \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git ap'
prefix.rs:7:13: score=0.39 holes=1 via=span
  {cmd} = git ap
  prefix: 2026-08-19T23:50:01Z ERROR
  truncated: `
```

sitbone abridged 7-hole binds `{oldPhase.rawValue}=focused` … `{idle}=12` with `truncated:`. kizu `--> src/git/revert.rs:46:18` against `format!|anyhow!` is a locator, not `{i}=git/revert`.

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/` | `rg -g`, `--templates` file | truncated 7-hole / `{uid}` / spawn, rustc locator, prefix.rs decoy, 3000-line `--any`, binary stdin |
| `…/kizu` | `rg 'failed to spawn'`, `format!\|anyhow!` | truncated spawn, timestamp span, rustc locator refuse |
| `…/sitbone` | `rg awayRecovered` | full 7-hole + abridged prefix |
| `…/voidtrace`, `…/tenaoshi` | existing invert dogfood | still pass |

## Surprises

- The 7-hole abridged paste is not "fuzzy match". The next static (`s deserted=`) shares a prefix `s` with the leftover `12s`, so `{idle}=12` is delimited. That is alignment, not guesswork.
- A no-hole decoy with a *short* leftover (` `git ap`, 7 chars) still beat the holed truncated match until leftover meant "any word-like suffix", not `len>=8`.
- Grep hydrate's hint_line bonus hid a min-score miss on the same template opened as `--templates FILE`.
- rustc `error[E0308]: mismatched types` would also have been a suffix-variant (`mismatched types`) if we only filtered after `query_variants`. Refuse the original query.

## Failures

- Adjacent concatenation (`"open " + path`) is still not one template (sibling mutation).
- Interpolated tail only (`fatal: not a git repository`) still does not find `git diff single file failed: {1}`. Truncation is a *prefix* of an instance, not a suffix-only hole.
- `--any` slurped stdin in v0.1 (printed one; read all). v0.2 streams.
- Dynamic format strings remain invisible.
- Relative `git -C` paths still need `--chdir`.

## Suggested mutations

- Reconstruct a chain of templates from `truncated:` remainder + `prefix:` leftover.
- Optional `--complete` that fills truncated holes from a second, longer paste.

## Kill / keep

**Keep.** The flipped assumption is still invert's (stream, names, span). The destroyer misses were load-bearing: truncated instance, locator grammar, `--any` as exists, fail-closed binary, hole-first ranking. Do not grow a rustc parser or a walker.

## What the flipped assumption bought and lost

**Bought**

- Abridged logs are evidence, not misses.
- rustc paste no longer hallucinates `{i}=git/revert`.
- `--any` is a probe, not a printer.
- Inverse-printf ranking prefers a binding over a documentation prefix.

**Lost**

- No-hole templates that are a prefix of a longer paste no longer hit (use the exact string, or a holed template).
- Compiler diagnostics as queries are refused, even if a format string happens to look like `src/{i}.rs`.

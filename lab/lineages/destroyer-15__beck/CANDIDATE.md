# destroyer-15 — beck

## Primitive

Adversarial first-producer: name the earliest pipeline stage that already contains this needle, then try to make that report lie — fd, wrappers, greedy JSON cover, empty cuts, `--run` vs a recorded trace.

## Why this might not exist

beck's pitch is that `tee | grep -n` is the wrong object. A destroyer that only restates the demo is a harvest note. The missing pass is: keep the unpiped-stderr money shot, then check whether mint/carry/wrap, the fd column, and the piece cover still hold on `{ }`, `$()`, binary, overlapping remints, cargo `kizu@0.7.0`, and `--run +`.

## How to run

```bash
chmod +x ./demo.sh ./attack.py
./demo.sh
python3 ./attack.py
```

Victim: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1108ac34ccbe/beck` (v0.2). Do not rewrite it.

## Empirical transcript

See `DESTROYER_BECK.md` and `/tmp/destroy-beck/transcript.txt`.

Gold held: `git -C /tmp status | cat` is `MINT stage 0 stderr`, naive tee 0 bytes. Tiny JSON wrap glue `@`. Trailing `2>&1` keeps stderr. kizu `git log | rg | head` mints git. JSON `--save`/`--trace` MATCH.

Holes: brace groups split (CANDIDATE said they don't). `$()` inner not walked. Mid-command `2>&1` reports stdout. `printf hi | echo hi` later=carry. cargo `kizu@0.7.0` pieces steal `@0.7.0` from `notify-debouncer-full` byte 448982 (facet coincidence). `--min-payload 8` WRAP→MINT. `--run +` strips quotes. Trailing `|` dropped. NUL `--needle` cannot be argv.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `git log`, `cargo metadata --offline`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — `git log | rg hysteresis`
- `git -C /tmp status` — canonical unpiped stderr
- facet on the same cargo dump

## Surprises

- `{` is not nested; `${` is. The documented `{ foo | bar; }` case is three broken bash stages.
- `later_hits` carry is occupancy of `prev.piped`, so echo remint is carry.
- Payload of the cargo wrap is the coincidental `@0.7.0` because `pieces_to_payload` picks the longest fragment.
- `--min-payload` is a classifier, not just a cover knob.

## Failures

- Byte-cover is not field-cover (facet named this; still true).
- Inner pipelines not walked.
- `--needle` cannot contain NUL.
- Trace directory of tee dumps cannot see unpiped stderr; JSON save can.

## Suggested mutations

Field-honest JSON pieces (or hand off to facet). Brace/`$()` descent. later remint as data-flow. `--run +` keep argv. Wrap-without-pieces stays wrap. Trailing `|` fail-closed.

## Kill / keep

**Keep. Mutate.** First-producer of an unpiped byte is still not `tee | grep`. Do not kill because greedy cover crossed a crate.

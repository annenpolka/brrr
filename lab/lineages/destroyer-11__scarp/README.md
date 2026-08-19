# destroyer-11 — scarp

Adversarial pass on **scarp** (mutation-46, clock-cut filter). Isolated worktree. Victim binary was not rewritten.

Report: [`lab/judges/DESTROYER_SCARP.md`](lab/judges/DESTROYER_SCARP.md)

## Victim

- Tool: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b60-8466-71a3-894a-7bf303f098fd/scarp`
- Lineage: `lab/lineages/mutation-46__scarp/`
- After attacks: `selftest 7/7`, `./demo.sh 0` ok, `scarp 0.2 backend=darwin`

Peels (read, not re-destroyed): twixt (stream), yaw (kernel slew), reimpl-08 scree (repeated key=value).

## How it was attacked

Real binary only. Driver: `/tmp/destroy-scarp/attack.py`. Transcripts: `/tmp/destroy-scarp/transcript.txt`, `/tmp/destroy-scarp/followup.txt`. Fixtures under `/tmp/destroy-scarp/fixtures/`.

```bash
SCARP=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b60-8466-71a3-894a-7bf303f098fd/scarp
python3 "$SCARP" selftest
python3 "$SCARP" cut | python3 "$SCARP" --explain
python3 /tmp/destroy-scarp/attack.py
```

Battery (conceptual, not one-line bugs):

1. Live Darwin clocks vs `ntp=` — `CLOCK_MONOTONIC − RAW` equals scarp's NTP field; wall−boot tracks POSIX MONOTONIC to ~0.1µs.
2. Unlabeled ticks — 2 REST, 4 STEP/DILATE bags, ≥8 keeps the first eight fields.
3. Repeated `wall=0 / wall=10 / machine=…` — REST; sleep gone.
4. Darwin `time.monotonic` mapping holds; alias-split and `CLOCK_MONOTONIC` as machine do not.
5. JSONL stream / 1000-cut log — `cuts[0], cuts[1]` only. Live 3-cut stream hides 1d05h03m snapshot sleep.
6. ISO-8601 / `date(1)` number-scavenge → invented STEP. Porcelain 0-fill round-trips REST → STEP.
7. `kern.sleeptime` emitted, never classified. `--require SLEEP` on `scarp cut` is since-boot, not this interval.
8. Missing proper: 22d awake beats 1d sleep (largest-gap). `kind=host` at 60s swallows DILATE.

Dogfood trees (kizu, sitbone, tenaoshi, voidtrace) have no clock-cuts. sitbone `drift_timeout` 92s as two wall ticks is REST; wall+monotonic with 30s lid-close and no proper is DILATE.

## Verdict

**Mutate, do not kill.** Gold path still names lid-close vs step vs idle vs busy for two well-formed cuts. Do not paper over the `ntp` field or the two-row window.

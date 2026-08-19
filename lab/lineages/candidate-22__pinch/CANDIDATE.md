# candidate-22 — pinch

## Primitive

A Unix pipeline is a conversation of blocking; name who waited for whom, including the hidden child a wrapper slept on.

## Why this might not exist

`pv` reports throughput. `time` reports wall/user/sys. `ps` is a snapshot. None of them answer the question you actually have when `cmd | gzip | something` is slow: **was gzip waiting on an empty pipe or sitting on a full one?** The workaround is to insert `pv` by hand and squint. There is no verb for the blocking relationship.

The same hole exists one layer down. `just spec-check` and `bun tools/spec-gen.ts` look like one command. They are not. The wrapper sleeps while `pkl` / `swift-frontend` / `cargo` runs. `time` says "wait-bound"; it will not name the child.

## Four primitives considered

1. **Hunk-felt** — revert each hunk, see which tests fail. Discarded: conventional (coverage + cargo-mutants).
2. **Why-rebuild** — declared vs opened inputs. Discarded: conventional (`ninja -d explain`).
3. **Generation-cohort** — artifacts minted together that later split in time.
4. **Pipeline blocking conversation** — this tool.

## How to run

From the worktree root:

```bash
./pinch --help
./demo.sh
./pinch -- python3 fixtures/fast_producer.py 1048576 + python3 fixtures/slow_consumer.py
./pinch --json --report out.json --sh 'cat file | gzip | wc -c'
./pinch -- cargo test --lib -- --list
```

`--` ends options (so `cargo test -- --list` stays one command). A lone `+` separates stages. `--sh` splits a shell pipeline on `|`.

## Empirical transcript

### Before the improvement

Fixture shapes (still hold):

| pipeline | pinch | relation |
|---|---|---|
| fast_producer \| slow_consumer | stage 1 | blocked-on-write 0.69s |
| slow_producer \| fast_consumer | stage 0 | blocked-on-read 0.22s |
| producer \| cpu \| consumer | stage 1 compute | both neighbors wait on 1 |

Dogfood, first pass:

- **sitbone** `swift build 2>&1 | tee log` (the Makefile `compile` recipe): tee waited 0.39–1.9s on swift (`blocked-on-read`, 98–119 bytes). Correct, but the named stage was `bash -lc swift build 2>&1`. Tree samples already showed `swift-package` / `swift-frontend` and a 8% busy fraction polluted by meter sleepers.
- **kizu** `cargo metadata --format-version 1 | jq '.packages \| length'`: jq waited 2.200s on cargo while cargo downloaded crates; 1.26MB JSON, 290 packages. After cache: jq waited 0.134s, cargo still the pinch. **jq was never the bottleneck.**
- **kizu** `cargo metadata --offline` failed (missing crate). pinch still classified: 0 bytes, jq blocked-on-read, pinch is cargo. Useful on failure.
- **voidtrace** `node tools/spec-check/src/main.ts`: wall 1.124s, 12% busy, classified wait-bound. Samples: `node` 6 run / 18 sleep, **`pkl` 1 run / 17 sleep**. The wait was a hidden inner pipeline. pinch could not name `pkl`.
- **tenaoshi** `bun tools/spec-gen.ts`: wall 0.58s, 4% busy, bun sleeping. `pkl` appeared in one sample and was dropped.
- **voidtrace** `cat generated.ts \| gzip \| wc -c`: 50KB, 93ms, noise. Generated artifacts are too small for gzip to be a real pinch.
- **skills** `find . -name SKILL.md -print0 \| xargs -0 wc -l`: find is the pinch (22ms). Tiny.

CLI failure: `pinch -- cargo test --lib --offline -- --list` split on `--` and tried to exec `--list` (exit 127, BrokenPipe on cargo). `--` cannot be a stage separator.

### After the improvement

1. **Inner tree** — process-group samples minus wrappers (`--meter`/`--wrap`/`bash`/`tee`/macOS `(Python)` placeholders). The child with the most RUN samples is the inner pinch. Phases compress consecutive runner sets.
2. **Stage separator is `+`** — `--` only ends options.

Re-runs:

- **sitbone** `swift build 2>&1 | tee`: tee waited 0.986s on swift; **inner pinch is `swift-build`** (4 run / 13 sleep). Verdict names the compiler, not `bash -lc`.
- **kizu** `cargo metadata | jq`: inner tree `cargo 100% run`, `jq 0% run`, phase `0.05-0.18s cargo RUN  jq SLEEP`. Pipe meters and tree agree.
- **kizu** `cargo test --lib --offline -- --list`: one stage, exit 0, **489 tests listed**, cargo is the pinch.
- **voidtrace spec-check** (warm): 0.29s, node 100% run, pkl no longer visible (cache). First-pass 1.12s with pkl remains the colder evidence.
- Hidden-child fixture: `python3 -c 'subprocess.check_call(["sleep","0.35"])'` → `pinch.inner.comm=sleep`.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — Makefile `swift build 2>&1 | tee`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `cargo metadata | jq`, `cargo test -- --list`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — `node tools/spec-check`, generated-artifact gzip
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `bun tools/spec-gen.ts`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — `find SKILL.md | xargs wc`
- `fixtures/` — slow/fast/cpu stages

## Surprises

- Warm `swift build` still makes `tee` wait almost the whole wall on an empty pipe. `cmd 2>&1 | tee log` is a fake pipeline: tee is a tap, never a pinch.
- `jq` on 1.3MB of `cargo metadata` is free. The download/compute is cargo. People profile the wrong stage.
- macOS `ps` prints `(Python)` when it cannot recover argv, which at first leaked into the inner-pinch name.
- `wait4` rusage on `bash -lc 'swift build 2>&1'` is not the compiler. Labels and inner tree had to descend.

## Failures

- Sub-200ms pipelines (gzip of voidtrace generated TS, skills `find | wc`) are below the stall noise floor; verdicts are not meaningful.
- 20ms sampling misses short-lived `pkl` children on a warm spec-gen.
- Meter processes are themselves Python and add sleep slots; they must be filtered or busy% is a lie.
- No Linux / `pidfd` path yet. macOS `select.poll` + `ps` only.
- Cannot see *which file* a wait-bound inner child is blocked on (would need `dtruss`/root).

## Suggested mutations

- Sample stacks / `wchan` so a wait-bound inner pinch says "poll on socket" vs `nanosleep`.
- Treat `tee`/`pv` as declared taps and drop them from the stage list automatically.
- Record a byte-time series per link (when the pipe was full vs empty), not just totals.
- `--replay` a previous JSON report against a new run (regression: "gzip used to be the pinch").
- Generation-3: combine with generation-cohort — which *artifact writes* happened during which phase.

## Kill / keep

**Keep.** The object (a wait-for graph over pipe meters + process-tree phases) is small, composable (`--json`), and named something developers already say out loud ("where's the pinch?"). First real use immediately found a CLI footgun and a missing inner-child name; both are now fixed.

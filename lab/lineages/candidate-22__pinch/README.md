# pinch

Name who waited for whom in a Unix pipeline.

`pv` tells you throughput. `time` tells you wall clock. `pinch` treats a pipeline as a **conversation of blocking**: each inserted meter times `poll()` waits on an empty pipe (upstream was slow) versus a full pipe (downstream was slow). The pinch point is the stage the others waited for.

A single command is also a pipeline. Process-group samples drop the wrappers (`bash`, `tee`, our meters) and name the **inner pinch** — the child the wrapper slept on (`pkl`, `swift-build`, `cargo`).

## Primitive

A pipeline is not a list of programs. It is a wait-for graph.

```
producer  ──blocked-on-write 1.6s──▶  gzip
wc        ──blocked-on-read  0.4s──▶  gzip
verdict: pinch is gzip (compute)
```

## Install / run

Stdlib Python 3.9+. No dependencies.

```bash
./pinch --help
./demo.sh
```

## Examples

Slow consumer — the producer sits on a full pipe:

```bash
./pinch -- \
  python3 fixtures/fast_producer.py 1048576 + \
  python3 fixtures/slow_consumer.py
```

Slow producer — the consumer sits on an empty pipe:

```bash
./pinch -- \
  python3 fixtures/slow_producer.py + \
  python3 fixtures/fast_consumer.py
```

Compute-bound middle stage — both neighbors wait on it:

```bash
./pinch -- \
  python3 fixtures/fast_producer.py 1048576 + \
  python3 fixtures/cpu_stage.py + \
  python3 fixtures/fast_consumer.py
```

Shell pipeline form, JSON for composition:

```bash
./pinch --json --report pinch.json --sh 'cat data.bin | gzip | wc -c'
```

Single command, including cargo's own `--` (not a stage split):

```bash
./pinch -- cargo test --lib -- --list
```

## Output

Human report on stderr (data still flows on stdout). `--json` writes a machine report (`stages`, `links`, `pinch.wait_for`, `pinch.stage`, `pinch.inner`, `samples.inner.phases`). `--report PATH` redirects the report (`-` = stdout).

`--` ends options. A lone `+` argument separates stages. `--sh` splits a quoted pipeline on `|`.

Exit status is the pipeline's `pipefail` status.

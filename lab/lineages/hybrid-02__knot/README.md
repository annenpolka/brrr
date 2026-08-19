# knot

A command line is both a pipeline and a process tree. `knot` reports the **blocking conversation** across pipes *and* child-wait / sleep / fifo, then names the **wait-source of the whole tree**.

`pv` reports throughput. `time` reports wall. `ps`/`lsof` are snapshots. `pinch` names who waited on a `|`. `hitch` draws a wait-for graph of a process tree. Concatenating them still gives two answers. The missing verb is one walk: jq waited on cargo, cargo waited on rustc — **the knot is rustc**.

## Primitive

The wait-source of a command line: meters (empty vs full pipes) and tree edges (child-wait, fifo, tcp, sleep) are one graph. Walk waiter → blocker until a process is running or sleeping on the kernel. That node is the knot.

```
jq            --pipe-empty  2.2s-->  cargo metadata
cargo metadata --child-wait  1.8s-->  rustc --crate kizu
KNOT  rustc --crate kizu
```

## Install / run

Stdlib Python 3.9+. Needs `ps` and `lsof` (macOS) or `/proc` (Linux). No pip packages.

```bash
chmod +x knot
./knot --help
./demo.sh
./knot selftest
```

## Examples

**1. Slow consumer — producer sits on a full pipe**

```bash
./knot -- \
  python3 fixtures/fast_producer.py 1048576 + \
  python3 fixtures/slow_consumer.py
```

**2. Hidden child — the wrapper is not the knot**

```bash
./knot -- python3 fixtures/hidden_child.py 0.4
# KNOT  sleep   via child-wait
```

**3. Real pipeline, JSON for composition**

```bash
./knot --json --report knot.json --sh 'cargo metadata --format-version 1 | jq ".packages | length"'
```

`--` ends options (so `cargo test -- --list` stays one command). A lone `+` separates stages. `--sh` splits a quoted pipeline on `|`.

Human report on stderr (child stdout still flows). `--json` writes `knot`, `conversation`, `stages`, `links`, `procs`.

# hybrid-02 — knot

## Primitive

A command line is both a pipeline and a process tree: one wait-for conversation spanning pipe meters and child-wait / sleep / fifo, naming the wait-source of the whole tree.

## Why this might not exist

`pinch` answers "who waited on this `|`?" `hitch` answers "what is this process tree blocked on?" Developers type command lines that are both at once: `cargo metadata | jq`, `swift build 2>&1 | tee`, `just spec-check` (a hidden pipeline). Concatenating the two tools still produces two reports. The object is one graph and one walk.

## How to run

From the worktree root:

```bash
./knot --help
./knot selftest
./demo.sh
./knot -- python3 fixtures/hidden_producer.py + python3 fixtures/fast_consumer.py
./knot --json --report out.json --sh 'cargo metadata --format-version 1 | jq ".packages | length"'
```

## Empirical transcript

### Before the improvement

(filled after first demo + dogfood)

### After the improvement

(filled after one improvement)

## Dogfood targets

- fixtures: pipe_block, fifo, hidden_child, hidden_producer | consumer, cpu middle
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `cargo metadata | jq`, `cargo test`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — `node tools/spec-check`, vitest
- python pipelines in fixtures

## Surprises

(filled)

## Failures

(filled)

## Suggested mutations

(filled)

## Kill / keep

(filled)

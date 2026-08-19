# folk

Discover **unwritten calling protocols** and the sites that break them.

A *folk protocol* is a pair of calls a codebase treats as a unit — `lock` then `unlock`, `begin_tx` then `commit_tx`, `session.beginConfiguration` then `session.commitConfiguration` — without ever writing that rule down. `folk` mines those pairs from path-sensitive call sequences and prints the half-pairs as greppable TSV.

This is not dead-code detection, not leftover-name hunting, and not a type checker. It answers: **what handshakes does this repo believe in, and who broke one?**

## Install

Python 3.9+. No third-party dependencies.

```
chmod +x folk
./folk --help
```

## Examples

```
# What protocols does this tree honor?
./folk --pairs src/

# Who performs only one half?
./folk --orphans src/

# CI: exit 1 if a breach exists
./folk --check src/

# One name
./folk --of lock src/

# JSON for jq
./folk --json --all src/ | jq '.pairs[] | select(.score > 0.8)'

# Paths from stdin
find src -name '*.py' | ./folk --pairs -
```

Exit codes: `0` ok, `1` with `--check` when orphans exist, `2` usage error.

TSV columns are stable. Headers on stdout unless `-q`. Progress on stderr.

## How it decides

1. Walk source (py/rs/swift/go/ts/js/java/c/rb). Skip `node_modules`, `target`, `generated`, …
2. Build a cheap CFG per function (if/else, try/finally, loops, return).
3. Discover **inverse-shaped** pairs (`begin*`/`commit*`, `lock`/`unlock`, `set_var`/`remove_var`, `push_back`/`pop_front`).
4. Optionally splice one level of callee *must* protocol-moves into callers (`setup_tx()` hides `begin_tx()`).
5. Report path-sensitive orphans, suppressing fast-fail (`open; if err { return }`) and thin wrappers.

`--stat` also mines collocated-but-not-inverse pairs. It is noisy; leave it off.

## Demo

```
./demo.sh
```

See `CANDIDATE.md` for the primitive, before/after transcripts, and the failure log.

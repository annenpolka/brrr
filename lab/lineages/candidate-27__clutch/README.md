# clutch

A generated file already testifies about its making. `clutch` reads that
testimony, groups files that claim the same parent into a **clutch** (one
generation event / manufacturing lot), and reports when the eggs were not
re-laid together.

Git records commits. Spec-check regenerates and diffs. Neither reconstructs
the lot the artifacts themselves claim they belong to.

Requires Python 3.10+ and `git`. No other dependencies.

## Install / run

```bash
./clutch --help
./demo.sh
```

Copy `clutch` onto your `PATH` if you want. Exit `0` if every clutch is
FRESH (or MUTE). Exit `1` if any clutch is STALE, SPLIT, RAGGED, COLD,
ORPHAN, or FOREIGN. `--ok-cold` treats COLD/RAGGED as green (stable output
that git did not rewrite).

## Examples

**1. Partial regen splits a clutch.** One sibling got the new die, the other
still carries yesterday's stamp.

```bash
./clutch --write-fixture /tmp/clutch-demo
./clutch -C /tmp/clutch-demo -v
```

```
clutch  specs/main.pkl  …  die=sha256:bbbb…  SPLIT
  FRESH     0  out/a.md     stamp=sha256:bbbb…
  STALE     1  out/b.md     stamp=sha256:aaaa…
```

**2. Real tree: VoidTrace generated docs.** Same parent (`specs/main.pkl`),
not the same generation.

```bash
./clutch -C ~/ghq/github.com/annenpolka/voidtrace docs/generated packages/spec-artifacts
```

`docs/generated/AI_UX.md` cites the same parent as `SPEC.md` but its last
commit is 28 parent-moves behind. The file still says it was generated from
`specs/main.pkl`. The lot is ragged; `spec-check` may still be green because
the generator emits identical bytes.

**3. Relico oracles as a clutch.** `docs/SPEC.md` was re-laid with the spec;
`oracles_generated.rs` lagged one parent commit; the TS unit/e2e oracles
lagged four.

```bash
./clutch -C ~/ghq/github.com/annenpolka/relico --tsv \
  | awk -F'\t' '$3 ~ /oracle|SPEC.md/'
```

Pipe `--tsv` / `--json` into `awk`/`jq`. `--summary` is clutch-level only.
`--explain FILE` shows the raw receipt. `--locks` treats `Cargo.lock` as
testimony about `Cargo.toml`.

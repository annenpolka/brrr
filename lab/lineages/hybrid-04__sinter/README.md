# sinter

A generated file both **claims** a parent (the receipt it already carries) and **belongs** to a firing (the generator's output list + import closure). `sinter` fuses those two witnesses into one lot, then reports **RAGGED / STALE / CLEAN** with a typed why: **content**, **clock**, or **dirty-parent**.

kiln reconstructs lots from recipes. clutch reconstructs lots from receipts. Piping them is two reports. The object here is one assay.

Not `ninja -d explain` (that needs a graph you wrote). Not `just spec-check` (that regenerates). Git is silent when four language projections of one spec no longer fired together.

## Install / run

Python 3.10+, stdlib only. `git` for reasons.

```bash
chmod +x ./sinter
./sinter --help
./sinter --selftest
./demo.sh
./sinter -C /path/to/repo
./sinter -C /path/to/repo why tests/unit/oracles_generated.test.ts
./sinter -C /path/to/repo --tsv
./sinter -C /path/to/repo --check    # exit 1 on RAGGED/STALE
```

## Verdicts

| tag | meaning |
| --- | --- |
| CLEAN | one firing; world bytes match fire; parent not dirty |
| RAGGED | siblings of one firing did not stay together, or a regen is in flight |
| STALE | the claim does not hold for anyone in the lot |

| why | meaning |
| --- | --- |
| content | parent, undeclared import, or generator bytes moved since fire |
| clock | mtime would call it fresh; content would rebuild (not a checkout cluster) |
| dirty-parent | parent is dirty in the work tree; artifacts were not rewritten |

`via=recipe` is a member the generator listed that carries no receipt. `via=both` is the join holding.

## Examples

### 1. Relico oracles — one firing, not re-laid together

```bash
./sinter -C ~/ghq/github.com/annenpolka/relico
```

`docs/SPEC.md` and the renderer oracles sit on the current world. Unit/e2e oracles last moved eight days earlier. Git is clean. sinter: **RAGGED why=content**. `why tests/unit/oracles_generated.test.ts` names `specs/notifier.pkl` and undeclared `specs/patterns.pkl`.

### 2. Tenaoshi — recipe members with no colophon

```bash
./sinter -C ~/ghq/github.com/annenpolka/tenaoshi
```

`OraclesGenerated.swift` testifies `specs/tenaoshi.pkl`. `contracts/testcases/*.json` testify nothing. The generator lists them. They join the same firing (`via=recipe`). clutch never sees them; kiln sees them; sinter assays the joined lot.

### 3. Partial regen fixture

```bash
./sinter --write-fixture /tmp/sinter-demo
./sinter -C /tmp/sinter-demo -v
./sinter -C /tmp/sinter-demo why out/b.md
```

`out/a.md` refired; `out/b.md` did not; headerless `extra/EPC-001.json` still belongs. **RAGGED why=content**.

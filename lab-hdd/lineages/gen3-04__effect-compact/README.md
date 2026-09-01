# effect

For a configuration key, emit **one record**: where config declares it, where source assigns it, where the env layer would supply it (or the names those sites defer to), and whether a static **effective** value exists.

```yaml
origin:
  method: hdd
  kind: hybrid
  generation: 3
  mutation: effect-compact
  parent: hybrid-01__effect
```

This is not `stated KEY` followed by `envfrom KEY`. Dotenv is env provenance, not a declaration. `${WAIT}`, `os.getenv("WAIT")`, `os.environ.get("WAIT")`, and `process.env.WAIT` pull **WAIT** into the same record. EFFECTIVE is unknown when the layers are not statically comparable.

```text
effect [--json] KEY [DIR]
```

| exit | meaning |
|------|---------|
| 0 | no declared-literal vs assigned-literal disagreement |
| 1 | usage |
| 2 | declared literal disagrees with assigned literal (env provenance is still printed) |

Python 3 stdlib only.

```bash
python3 effect timeout fixtures/disagree
python3 effect timeout fixtures/compact_json
./demo.sh
python3 -m unittest tests.test_effect
```

Compact `{"timeout": 5}` is a declaration. Missing it used to make EFFECTIVE a false assigned-only 10.

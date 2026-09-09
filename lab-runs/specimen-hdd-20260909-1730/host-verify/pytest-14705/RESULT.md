# Host 実機 pytest#14705 custom TOML `[pytest]` python_files

Not Dreamer-facing. HOLD no View. Related to #14807. Do not apply the PR.

`pytest-benchmark.toml` `[pytest]` vs `pytest-benchmark-tool.toml` `[tool.pytest]`.
`python_files = ["bench_*.py"]`, `python_functions = ["bench_*"]`, `testpaths = ["benchmarks"]`.
Files: `benchmarks/bench_one.py` (`Bench.bench_add`) and `benchmarks/test_normal.py`.

| pytest | `-c` `[pytest]` | `-c` `[tool.pytest]` |
| --- | --- | --- |
| 8.4.1 | rc=0 `test_normal` only | rc=0 `test_normal` only |
| 9.0.1 | rc=0 `test_normal` only | rc=0 `bench_one.py::Bench::bench_add` |
| 9.0.3 | rc=0 `test_normal` only | rc=0 `bench_add` |
| 9.1.0 | rc=0 `test_normal` only | rc=0 `bench_add` |
| 9.1.1 | rc=0 `test_normal` only | rc=0 `bench_add` |

Custom `-c` `[pytest]` ignored 8.4.1–9.1.1 (default `test_*.py`). `[tool.pytest]` unread on 8.4.1; collected from 9.0.1. Same split as #14807.

Custom `-c` `[tool.pytest.ini_options]`: 8.4.1 with `minversion=9.0` rc=4 (table is read); without minversion collects `bench_add`. 9.0.1–9.1.1 collect `bench_add`. Unlike `[tool.pytest]`, ini_options is already honored on 8.4.1 for a custom `-c` file.

Leftover `--collect-only` no `-c`: `test_normal` only on 8.4.1–9.1.1. Leftover `-c` `[pytest]`: `test_normal` only all. Leftover `-c` `[tool.pytest]`: 8.4.1 `test_normal` only; pytest 9 `bench_add` only. Same split as run.

Leftover `--setup-show -c` `[tool.pytest]`: 8.4.1 **1 passed** `test_normal` (table unread); pytest 9 **1 passed** `bench_add`. Leftover `-c` ini_options with minversion=9.0: 8.4.1 rc=4; pytest 9 `bench_add` 1 passed. Same split as collect. No View/export.

Leftover `--lf`/`--ff`/`--nf`/`--sw` `benchmarks/test_normal.py`: **1 passed** on 8.4.1–9.1.1 (no last-failed). No View.

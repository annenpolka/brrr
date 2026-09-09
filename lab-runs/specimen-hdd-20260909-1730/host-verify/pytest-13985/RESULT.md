# Host 実機 pytest#13985

Not Dreamer-facing. HOLD for HDD consumer (no View/export). SchemaStore/even-better-toml not run.

`[tool.pytest] addopts = "-q"` (string):
- pytest 8.4.1: rc=0; table ignored (verbose session, not `-q`)
- pytest 9.0.1 / 9.0.3 / 9.1.0 / 9.1.1: rc=1 TypeError expects list for type args

`[tool.pytest] addopts = ["-q"]` (list): 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 rc=0 (`-q` applies on 9.x)

`[tool.pytest.ini_options] addopts = "-q"`: 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 rc=0

VS Code schema gap is outside pytest. No View staged.

Leftover `--collect-only` per layout: `[tool.pytest] addopts="-q"` string collects 1 on 8.4.1 (table unread) and **TypeError at collect** on pytest 9. List form and `ini_options` string collect 1 on 8.4.1–9.1.1. Collect-only still hits the native-table TypeError.

Leftover `--setup-show` per layout: string native TypeError on pytest 9 (8.4.1 unread 1 pass); list native and `ini_options` **1 passed** on 8.4.1–9.1.1. Same split as collect-only. No View.

Leftover string `--lf`/`--ff`/`--sw`/`--nf`: 8.4.1 **1 passed** (unread); pytest 9 TypeError at configure (not last-failed). Leftover list and `ini_options` `--lf`/`--ff`/`--nf`/`--sw`: **1 passed** on 8.4.1–9.1.1. No View.

Leftover string `--maxfail=1`: 8.4.1 **1 passed**; pytest 9 TypeError at configure (not last-failed). `--maxfail=1` does not skip configure TypeError. No View.

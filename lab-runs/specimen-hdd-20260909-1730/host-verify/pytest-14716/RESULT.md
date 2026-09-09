# Host 実機 pytest#14716 `-c` invalid paths

Not Dreamer-facing. HOLD no View. Related PRs stay 正解 off Dreamer.

Public steps: existing `config.ini` `[pytest] addopts=-q`, existing `config.in` same table, dummy `test_a.py`. `--collect-only`.

| pytest | `-c config.in` (exists, wrong ext) | `-c fake_config.in` (missing, wrong ext) | `-c fake_config.ini` (missing, .ini) | `-c config.ini` |
| --- | --- | --- | --- | --- |
| 8.4.1 | rc=0 `configfile: config.in` 1 collected | rc=0 `configfile: fake_config.in` 1 collected | rc=1 raw `FileNotFoundError` traceback | rc=0 1 collected |
| 9.0.1 | same | same | same | same |
| 9.0.3 | same | same | same | same |
| 9.1.0 | same | same | same | same |
| 9.1.1 | same | same | same | same |

Wrong extension is a silent no-op (configfile still reported, even if missing). Missing `.ini` / `.cfg` / `.toml` are unhandled `FileNotFoundError` tracebacks rc=1, not `UsageError`. Matches the reporter.

Leftover `--setup-show -c config.ini`: **1 passed** on 8.4.1–9.1.1. Leftover `--collect-only -c fake_config.toml` / `fake_config.cfg`: rc=1 raw `FileNotFoundError` on 8.4.1–9.1.1 (same as missing `.ini`).

Leftover `--collect-only -c config.ini`: **1 collected** on 8.4.1–9.1.1. No View/export.

Leftover `--tb=short -c config.ini`: **1 passed** on 8.4.1–9.1.1. Same as run. No View.

# Host 実機 pytest#3062 setup.cfg log_format interpolation

Not Dreamer-facing. HOLD no View.

Public `setup.cfg` `[tool:pytest]`:

```
log_format = %(filename)s:%(lineno)d %(name)s%(levelname)s%(message)s
log_cli = true
```

Stock `configparser.ConfigParser().get("tool:pytest", "log_format")` (default interpolation): `InterpolationMissingOptionError` (`filename` is not a valid option). `ConfigParser(interpolation=None).get(...)` returns the raw `%(filename)s:...` string. `ConfigParser().read()` of sections alone is rc=0 (`ok sections=['tool:pytest']`); the failure is on **get**.

pytest itself reads the same `setup.cfg` on 8.4.1–9.1.1 without interpolating:

| tree | 8.4.1–9.1.1 |
| --- | --- |
| `cfg/` pytest run | rc=0, 1 passed |
| `ini/` pytest.ini same format | rc=0, 1 passed |
| `toml/` `ini_options` quoted format | rc=0, 1 passed |
| `cfg-getini` `config.getini("log_format")` | raw `%(filename)s:%(lineno)d %(name)s%(levelname)s%(message)s`; `log_cli` True |
| `ini-getini` / `toml-getini` | same raw getini string |
| `cfg-log` `--log-cli-level=WARNING` | live log `test_log.py:3 hdd3062WARNINGhello-log` (format applied; no spaces in the template) |

The original pip/setuptools interpolation is default ConfigParser, not a pytest 8/9 split. pytest does not use that interpolation when loading `[tool:pytest]`.

Leftover escaped `%%(filename)s:...` in `setup.cfg`: stock ConfigParser still `InterpolationSyntaxError` (remaining `%(lineno)d` interpolates). `interpolation=None` returns raw `%%(filename)s:...`. pytest getini on 8.4.1–9.1.1 keeps the literal `%%(filename)s` (does not unescape) and 1 passed. Escaping one percent does not make default ConfigParser accept the logging format.

Leftover `pytest.ini` same partial `%%(filename)s:%(lineno)d...`: stock ConfigParser `InterpolationSyntaxError`; `interpolation=None` keeps literal `%%`; pytest getini 8.4.1–9.1.1 keeps `%%` and 1 passed. Same as setup.cfg.

Leftover fully escaped setup.cfg `%%(filename)s:%%(lineno)d %%(name)s%%(levelname)s%%(message)s`: stock ConfigParser **succeeds** and unescapes to `%(filename)s:%(lineno)d %(name)s%(levelname)s%(message)s`. `interpolation=None` keeps the doubled percents. pytest getini 8.4.1–9.1.1 keeps the literal `%%...%%` (does not unescape) and 1 passed. Fully escaping makes ConfigParser accept the logging format; pytest still does not interpolate.

Leftover `tox.ini` `[pytest]` same unescaped `%(filename)s:...`: stock ConfigParser `InterpolationMissingOptionError`; `interpolation=None` keeps raw. pytest getini 8.4.1–9.1.1 keeps the raw format and 1 passed. `tox.ini` `[pytest]` is read (unlike leftover `tox.ini` `[tool:pytest]` ignored).

Leftover pyproject `ini_options` escaped `%%(filename)s:...` and fully escaped `%%...%%`: pytest getini 8.4.1–9.1.1 keeps the literal `%%` and 1 passed. TOML is not ConfigParser; pytest still does not unescape.

Leftover escaped setup.cfg live-log `--log-cli-level=WARNING`: 1 passed; log line is literal `%(filename)s:3 hdd3062WARNINGhello-log` on 8.4.1–9.1.1. getini keeps `%%`; logging then treats `%%` as a literal percent, so the filename conversion never fires (unlike unescaped `test_log.py:3`).

Leftover fully escaped live-log `%%(filename)s:%%(lineno)d %%(name)s%%(levelname)s%%(message)s`: rc=1 ValueError `unsupported format character 'W'` on 8.4.1–9.1.1. Doubling every percent makes logging's `%` pass hit `%W` from `s%%(levelname)`. No View/export.

Leftover `--tb=short` of the parent tree hits leftover nested `toml-getini/`/`tox/` collection errors (duplicate layouts). Isolated setup.cfg getini/live-log results already recorded. No View.

Leftover isolated `cfg-log/` `--tb=short --log-cli-level=INFO`: **1 passed** on 8.4.1–9.1.1. Short traceback does not change pytest applying raw `log_format=%(filename)s`. No View.

Leftover isolated `cfg-getini/` `--tb=short`: **1 passed**, getini still raw `%(filename)s:...` on 8.4.1–9.1.1. No View.

Leftover isolated `ini-getini/` `--tb=short`: **1 passed** on 8.4.1–9.1.1. No View.

Leftover live-log `--log-cli-level=WARNING` getini: pytest.ini and pyproject keep literal `%%(filename)s:...` (same as setup.cfg). tox.ini `[pytest]` unescaped keeps raw `%(filename)s:...`. Fully escaped pyproject getini keeps `%%...%%` and 1 passed (live log did not apply). setup.cfg fully escaped live-log with `-s` still **ValueError** `unsupported format character 'W'`.

Leftover `--log-cli`: rc=4 unrecognized all versions (no such CLI flag). Leftover `-o log_cli=true --log-cli-level=WARNING` without `-s`: 1 passed, no live-log print. Leftover `-s -o log_cli=true --log-cli-level=WARNING` on pytest.ini / pyproject: still 1 passed **without** a live-log line. setup.cfg `[tool:pytest] log_cli=true` **does** print `%(filename)s:3 hdd3062WARNINGhello-log`. pytest.ini `[pytest] log_cli=true` and pyproject `ini_options` do not enable live log the same way.

Leftover `--log-cli-format='CLI:%(filename)s:%(lineno)d %(message)s'` on setup.cfg: live-log **CLI:test_log.py:3 hello-log** (CLI format overrides setup.cfg `log_format`). Same `--log-cli-format` / `--log-format` / `PYTEST_ADDOPTS` log_cli on pytest.ini / pyproject: still **no** live-log line.

Leftover `--log-file --log-file-level=WARNING`: setup.cfg writes `test_log.py:3 hdd3062WARNINGhello-log`; pytest.ini / pyproject log files are **empty** even with `--log-file-level=DEBUG` (same split as live-log). `--log-file-format='FILE:...'` on setup.cfg writes `FILE:test_log.py:3 hello-log`.

Leftover `--log-cli-date-format='%H:%M:%S'` without `asctime` in the format: live-log still `test_log.py:3 hdd3062WARNINGhello-log` (no timestamp). With `--log-cli-format='%(asctime)s %(filename)s:%(lineno)d %(message)s' --log-cli-date-format='%H:%M:%S'`: **HH:MM:SS test_log.py:3 hello-log**.

Leftover `-o log_format='OLOG:...'` and `-o log_cli_format='OCLIFMT:...'` on setup.cfg override live-log the same way as `--log-cli-format`. `-o log_cli_format` on pytest.ini still **no** live-log. `-o log_cli_level=WARNING` prints live-log on setup.cfg only. `-o log_date_format='%H:%M:%S'` with asctime in `-o log_cli_format` prints **HH:MM:SS**.

Leftover-0401 `-o log_cli_date_format='%H:%M:%S'` with `--log-cli-format='%(asctime)s %(message)s'`: live-log **HH:MM:SS hello-log**. Leftover-0404 `--log-file-date-format='%H:%M:%S'` with asctime in `--log-file-format`: file **HH:MM:SS test_log.py:3 hello-log**.

Leftover-0464 `-o log_file_level=WARNING` with `-s` on setup.cfg still prints live-log. Leftover-0467 `-o log_file=` + `log_file_level=WARNING` vs pytest.ini: log file still **empty** (same split as `--log-file`). HOLD no View.

Leftover-0590+ isolated trees with `logging.warning`: pytest.ini/pyproject/tox.ini `log_cli=true` **do** print live-log (leftover-0362 no-live-log was assert-True-only tests). Leftover-0626 `-c /dev/null --log-file-format=FILE:%(message)s` vs pytest.ini writes **FILE:hello-log** (cwd `log_format` displaced) and **no live-log**. env/`--strict-config` `-c /dev/null --log-file --log-file-level=WARNING` writes default **WARNING  hdd3062:test_log.py:3 hello-log**. setup.cfg `cfg-log/` `-c /dev/null --log-file` same default WARNING (displaces compact `test_log.py:3 hdd3062WARNINGhello-log`). Isolated setup.cfg `--log-cli-format=CLI:...` prints **CLI:test_log.py:3 hello-log**.
Leftover-0644 isolated pytest.ini/pyproject `--log-cli-level=ERROR`: **no live-log** (WARNING filtered). `--log-cli-level=INFO` still prints WARNING live-log. Leftover-0647 `--log-file-level=ERROR`: **empty file**; `--log-file-level=INFO` writes cwd format line. Leftover-0629 asctime+`--log-cli-date-format=%H:%M:%S` on pytest.ini/pyproject: **HH:MM:SS test_log.py:3 hello-log**. Leftover-0626 `PYTEST_ADDOPTS` `log_cli_format` with spaces: **rc=4** `%(message)s` file-not-found (env splits on space); no-space format prints **ENV:test_log.py:3:hello-log**. HOLD no View.


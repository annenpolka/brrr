# Host 実機 pytest#14807 / #14705

Not Dreamer-facing. HOLD no View. Do not apply the PR.

`python_files` used as a probe of which TOML table is actually read.

| config | 8.4.1 collected | 9.0.1–9.1.1 collected |
| --- | --- | --- |
| `-c custom.toml` with `[pytest] python_files=["only_custom.py"]` | `test_default.py` (table ignored) | `test_default.py` (still ignored) |
| `-c custom.toml` with `[tool.pytest.ini_options] python_files=["only_tool.py"]` | `only_tool.py` | `only_tool.py` |
| cwd `pytest.toml` with `[pytest] python_files=["only_pytest_toml.py"]` | `test_default.py` (not discovered / unread) | `only_pytest_toml.py` |
| `-c custom.toml` with both `[pytest]` and `[tool.pytest.ini_options]` | `only_tool.py` (ini_options wins; no UsageError) | same |
| cwd `pyproject.toml` with `[pytest]` (not `tool.pytest`) | `test_default.py` (ignored) | `test_default.py` (ignored) |

Custom `-c` TOML still ignores `[pytest]` on 8.4.1–9.1.1. Both tables in one custom file are **not** a UsageError today; ini_options wins. Named `pytest.toml` `[pytest]` works from pytest 9.0.1. `pyproject.toml` `[pytest]` is ignored.

Leftover extras (`python_files` probe, `--collect-only -q`):

| config | 8.4.1 | 9.0.1–9.1.1 |
| --- | --- | --- |
| pyproject `[tool.pytest]` list `["only_native.py"]` | `test_default.py` (unread) | `only_native.py` |
| pyproject `[tool.pytest]` string `"only_native.py"` | `test_default.py` (unread) | rc=1 TypeError list-expected |
| `pytest.toml` `[tool.pytest.ini_options]` | `test_default.py` (ignored) | `test_default.py` (still ignored) |
| `pytest.toml` `[tool.pytest]` native list | `test_default.py` | `test_default.py` (ignored) |
| `pytest.toml` both `[pytest]` + ini_options | `test_default.py` | `only_pytest_toml.py` (`[pytest]` wins; no UsageError) |
| cwd `pytest.ini` `[pytest]` | `only_ini.py` | `only_ini.py` |
| `-c custom.ini` `[pytest]` | `only_cini.py` | `only_cini.py` |
| cwd `pytest.cfg` `[pytest]` | `test_default.py` (filename ignored) | `test_default.py` (ignored) |
| `-c custom.toml` `[tool.pytest]` native list | `test_default.py` | `only_native.py` |
| `tox.ini` `[pytest]` | `only_tox.py` | `only_tox.py` |
| `tox.ini` `[tool:pytest]` | `test_default.py` (ignored) | `test_default.py` (ignored) |
| cwd `pytest.ini` `[tool:pytest]` | `test_default.py` (ignored) | `test_default.py` (ignored) |
| `setup.cfg` `[tool:pytest]` | `only_cfg.py` | `only_cfg.py` |
| pyproject `[tool.pytest]` + `ini_options` | `only_iniopt.py` (native unread) | rc=4 UsageError cannot use both |
| `-c custom.toml` `[tool.pytest]` + `ini_options` | `only_iniopt.py` | rc=4 UsageError cannot use both |

Named `pytest.toml` only reads `[pytest]` from 9.0.1; native `[tool.pytest]` and `ini_options` in that filename are ignored. `-c` INI `[pytest]` is read on every version; `-c` TOML `[pytest]` is not. Combining native `[tool.pytest]` with `ini_options` is a pytest-9 UsageError (8.4.1 silently uses `ini_options`). Combining `[pytest]` with `ini_options` in `-c` TOML is still not a UsageError. cwd `pytest.cfg` is not a recognized config filename (ignored 8.4.1–9.1.1); `pytest.ini` / `tox.ini` / `setup.cfg` are.

Leftover `setup.cfg` `[pytest]` (not `[tool:pytest]`): rc=1 all versions, `Failed: [pytest] section in setup.cfg files is no longer supported, change to [tool:pytest] instead.` Leftover `tox.ini` `[tool:pytest]`: ignored 8.4.1–9.1.1 (`test_default.py`; tox wants `[pytest]`). Leftover `pytest.ini` `[tool:pytest]`: ignored all versions (`pytest.ini` wants `[pytest]`). Leftover pyproject `ini_options` `python_files` **string**: `only_iniopt.py` on 8.4.1–9.1.1 (INI-string form; unlike native `[tool.pytest]` string TypeError). Leftover `pytest.toml` `[pytest]` string: 8.4.1 unread (`test_default.py`); pytest 9 TypeError list-expected.

Leftover `setup.cfg` `[tool:pytest] addopts=-q` collect-only (`scfg-tool/`): rc=0, 1 test on 8.4.1–9.1.1. Quiet collect is `test_a.py::test_a` on 8.4.1/9.0.1/9.1.1 and `test_a.py: 1` on 9.0.3/9.1.0. The `[tool:pytest]` table is read (unlike leftover `[pytest]` Failed).

`-c /dev/null --collect-only`: 8.4.1/9.1.1 rc=0, 1 test collected.

Leftover named `pytest.toml` `[pytest]` + native `[tool.pytest]` (`alt_named_pytest_native/`): 8.4.1 collects `test_default.py` (both unread). Pytest 9 collects `only_pytest_toml.py` (`[pytest]` wins). **No UsageError.** Native `[tool.pytest]` in `pytest.toml` stays ignored (same as leftover `alt_named_native`). Combining `[pytest]` with native in that filename is not the pyproject native+ini_options UsageError.

Leftover cwd `pytest.ini` `[pytest]` + `[tool:pytest]` (`alt_ini_both/`): collects `only_ini.py` on 8.4.1–9.1.1. `[pytest]` wins; `[tool:pytest]` in `pytest.ini` is ignored (same as leftover `pytest.ini` `[tool:pytest]` alone).

Leftover `-c custom.toml` `[pytest]` + native `[tool.pytest]` (`alt_c_pytest_native/`): 8.4.1 collects `test_default.py` (both unread). Pytest 9 collects `only_native.py` (**native wins**; `-c` TOML `[pytest]` stays ignored). **No UsageError.** Opposite of named `pytest.toml`, where `[pytest]` wins and native is ignored.

Leftover `-c custom.ini` `[tool:pytest] python_files = only_cini_tool.py` (`c-ini-tool/`): collects `test_default.py` on 8.4.1–9.1.1. Custom INI `-c` wants `[pytest]`; `[tool:pytest]` is ignored (unlike cwd `setup.cfg` `[tool:pytest]`).

Leftover `tox.ini` `[pytest]` + `[tool:pytest]` (`tox-both/`): collects `only_tox.py` on 8.4.1–9.1.1. `[pytest]` wins; `[tool:pytest]` ignored (same as leftover pytest.ini both).

Leftover `setup.cfg` `[pytest]` + `[tool:pytest]` (`scfg-both/`): collects `only_cfg.py` rc=0 on 8.4.1–9.1.1. `[tool:pytest]` wins; **no** `Failed: [pytest] section ... no longer supported`. Combining tables avoids the leftover `[pytest]`-only Failed.

Leftover cwd `pytest.ini` `[pytest]` + named `pytest.toml` `[pytest]` (`alt_ini_toml/`): 8.4.1 collects `only_ini.py` (pytest.ini; pytest.toml unread). Pytest 9.0.1–9.1.1 collects `only_pytest_toml.py` (**named pytest.toml beats pytest.ini**).

Leftover cwd `tox.ini` `[pytest]` + named `pytest.toml` `[pytest]` (`alt_tox_toml/`): 8.4.1 collects `only_tox.py`. Pytest 9.0.1–9.1.1 collects `only_pytest_toml.py` (same toml-over-ini split).

Leftover cwd `pytest.ini` + pyproject `[tool.pytest]` native (`alt_ini_pynative/`): **only_ini.py** on 8.4.1–9.1.1. pytest.ini beats pyproject native even on pytest 9 (unlike named pytest.toml). Leftover pytest.ini + pyproject `ini_options` (`alt_ini_pyiniopt/`): **only_ini.py** all versions. Leftover pytest.ini + tox.ini (`alt_ini_tox/`): **only_ini.py** all. Leftover pytest.ini + setup.cfg `[tool:pytest]` (`alt_ini_scfg/`): **only_ini.py** all.

Leftover setup.cfg `[tool:pytest]` + named pytest.toml (`alt_scfg_toml/`): 8.4.1 **only_cfg.py**; pytest 9.0.1–9.1.1 **only_pytest_toml.py**. Named pytest.toml beats setup.cfg from 9.0.1 (same as vs pytest.ini/tox.ini). pyproject.toml does **not** beat pytest.ini.

Leftover pytest.ini + pyproject **both** native+ini_options (`alt_ini_pyboth/`): 8.4.1 **only_ini.py**. Pytest 9.0.1–9.1.1 rc=4 UsageError cannot use both `[tool.pytest]` and `ini_options`. pytest.ini does **not** suppress the pyproject dual-table UsageError.

Leftover named pytest.toml + pyproject native (`alt_toml_pynative/`): 8.4.1 `test_default.py` (both unread). Pytest 9 **only_pytest_toml.py** (toml beats native). Leftover pytest.toml + pyproject ini_options (`alt_toml_pyiniopt/`): 8.4.1 **only_iniopt.py** (toml unread); pytest 9 **only_pytest_toml.py**.

Leftover setup.cfg + pyproject native (`alt_scfg_pynative/`): 8.4.1 **only_cfg.py**; pytest 9 **only_native.py** (**native beats setup.cfg**; unlike pytest.ini which beats native). Leftover setup.cfg + pyproject ini_options (`alt_scfg_pyiniopt/`): **only_iniopt.py** all versions (ini_options beats setup.cfg).

Leftover tox.ini + pyproject native (`alt_tox_pynative/`): 8.4.1 **only_tox.py**; pytest 9 **only_native.py** (native beats tox.ini, same as setup.cfg). Leftover tox.ini + pyproject ini_options (`alt_tox_pyiniopt/`): **only_iniopt.py** all (ini_options beats tox.ini). Leftover pytest.toml + tox.ini (`alt_toml_tox/`): 8.4.1 **only_tox.py**; pytest 9 **only_pytest_toml.py**.

Leftover `-c custom.toml` `[pytest]` with cwd pytest.ini (`alt_ini_c_pytest/`): **test_default.py** on 8.4.1–9.1.1. `-c` TOML `[pytest]` is unread **and displaces** cwd pytest.ini. Leftover `-c custom.toml` native with cwd pytest.ini (`alt_ini_c_native/`): 8.4.1 **test_default.py** (native unread, ini displaced); pytest 9 **only_native.py** (`-c` native wins).

Leftover `-c custom.ini` `[pytest]` vs cwd pyproject native (`alt_cini_pynative/`): without `-c`, 8.4.1 `test_default.py` / pytest 9 **only_native.py**. With `-c custom.ini`: **only_cini.py** on 8.4.1–9.1.1 (`-c` INI **displaces pyproject native** on pytest 9). Leftover `-c custom.ini` vs named pytest.toml (`alt_cini_toml/`): without `-c` 8.4.1 default / pytest 9 toml; with `-c` **only_cini.py** all. Leftover `-c custom.ini` vs cwd pytest.ini (`alt_cini_ini/`): without `-c` **only_ini.py** all; with `-c` **only_cini.py** all. Leftover `-c custom.ini` vs setup.cfg (`alt_cini_scfg/`): without `-c` **only_cfg.py** all; with `-c` **only_cini.py** all.

Leftover `-c custom.toml` native vs named pytest.toml (`alt_ctoml_toml/`): without `-c` 8.4.1 default / pytest 9 **only_pytest_toml.py**. With `-c`: 8.4.1 `test_default.py` (native unread, named toml displaced); pytest 9 **only_native.py** (`-c` native displaces named pytest.toml).

Leftover `-c custom.toml` unread `[pytest]` vs cwd pyproject native (`alt_ctoml_pynative/`): without `-c` 8.4.1 default / pytest 9 **only_native.py**. With `-c`: **test_default.py** on 8.4.1–9.1.1 (`-c` unread `[pytest]` **displaces pyproject native** on pytest 9). Leftover vs ini_options (`alt_ctoml_pyiniopt/`): without `-c` **only_iniopt.py** all; with `-c` **test_default.py** all (displaces ini_options). Leftover `-c custom.toml` native vs setup.cfg (`alt_ctoml_scfg/`): without `-c` **only_cfg.py** all (custom.toml is not cwd); with `-c` 8.4.1 default / pytest 9 **only_native.py**.

Leftover `-c custom.ini` vs tox.ini (`alt_cini_tox/`): without `-c` **only_tox.py** all; with `-c` **only_cini.py** all. Leftover `-c custom.ini` vs pyproject ini_options (`alt_cini_pyiniopt/`): without `-c` **only_iniopt.py** all; with `-c` **only_cini.py** all. No View/export.

Leftover `pytest.cfg` `[pytest]` pairings (filename is **not** a cwd config; collect-only):
- vs pyproject native (`alt_cfg_pynative/`): 8.4.1 **test_default.py** (cfg ignored, native unread); pytest 9 **only_native.py**
- vs pytest.ini (`alt_cfg_ini/`): **only_ini.py** all
- vs tox.ini (`alt_cfg_tox/`): **only_tox.py** all
- vs setup.cfg `[tool:pytest]` (`alt_cfg_scfg/`): **only_cfg.py** all
- vs named pytest.toml (`alt_cfg_toml/`): 8.4.1 **test_default.py**; pytest 9 **only_pytest_toml.py**
- vs pyproject ini_options (`alt_cfg_pyiniopt/`): **only_iniopt.py** all
- `-c custom.ini` vs pytest.cfg (`alt_cini_cfg/`): without `-c` **test_default.py** all; with `-c` **only_cini.py** all
- `-c custom.toml` unread `[pytest]` vs pytest.cfg (`alt_ctoml_cfg/`): **test_default.py** all with or without `-c` (unread TOML does not set python_files; cfg ignored)
- tox.ini vs setup.cfg (`alt_tox_scfg/`): **only_tox.py** all (tox.ini beats setup.cfg)

`pytest.cfg` never wins. HOLD no View.

Leftover `setup.cfg` `[pytest]` (unsupported section) pairings:
- vs tox.ini (`alt_scfg_pytest_tox/`): 8.4.1 **only_tox.py** (no Failed); pytest 9 rc=1 Failed `[pytest] section in setup.cfg files is no longer supported`
- vs pytest.ini (`alt_scfg_pytest_ini/`): 8.4.1 **only_ini.py**; pytest 9 Failed
- vs pyproject native (`alt_scfg_pytest_native/`): Failed **all** including 8.4.1
- vs named pytest.toml (`alt_scfg_pytest_toml/`): Failed **all** including 8.4.1

On 8.4.1 a sibling pytest.ini/tox.ini suppresses the setup.cfg `[pytest]` Failed; pytest 9 always Failed. Native/toml do not suppress it.

Leftover pytest.ini `[tool:pytest]` (ignored table) vs pytest.cfg (`alt_ini_tool_cfg/`): **test_default.py** all. Same vs tox.ini (`alt_ini_tool_tox/`): **test_default.py** all — the pytest.ini **filename** still displaces tox.ini even when the section is ignored.

Leftover `-c custom.toml` native vs pytest.cfg (`alt_ctoml_native_cfg/`): without `-c` **test_default.py** all; with `-c` 8.4.1 default / pytest 9 **only_native.py**. Leftover `-c custom.ini` `[tool:pytest]` vs pytest.cfg: **test_default.py** all (INI `[tool:pytest]` ignored even with `-c`). HOLD no View.

Leftover `setup.cfg` `[pytest]` vs `pytest.cfg` (`alt_scfg_pytest_cfg/`): **Failed all versions** (`pytest.cfg` does not suppress). Leftover `-c custom.ini` vs setup.cfg `[pytest]`: without `-c` Failed all; with `-c` **only_cini.py** all (`-c` INI displaces Failed). Leftover `-c` unread TOML vs setup.cfg `[pytest]`: without `-c` Failed all; with `-c` **test_default.py** all. Leftover `-c` native vs setup.cfg `[pytest]`: without `-c` Failed all; with `-c` 8.4.1 default / pytest 9 **only_native.py**.

Leftover pytest.ini `[tool:pytest]` vs pyproject native / ini_options: **test_default.py** all (the pytest.ini **filename** displaces pyproject, including ini_options). Leftover tox.ini `[tool:pytest]` vs pytest.ini: **only_ini.py** all. Leftover setup.cfg `[pytest]` vs pyproject ini_options: 8.4.1 **only_iniopt.py** (ini_options suppresses Failed); pytest 9 Failed.

Leftover `--config-file=/dev/null` vs cwd pytest.ini / native / setup.cfg: **test_default.py** all (`/dev/null` displaces those cwd configs). Leftover tox.ini `[tool:pytest]` alone: **test_default.py** all (ignored table). Leftover pytest.ini `[tool:pytest]` alone: **test_default.py** all.

Leftover `-o python_files=only_native.py` vs cwd pytest.ini / native / setup.cfg: rc=5 no tests (override **replaces** cwd python_files; that file is absent). Same `-o` vs pytest.ini+native and setup.cfg+native: **only_native.py** all (override beats both). HOLD no View.

Leftover `setup.cfg` `[pytest]` vs pytest.cfg (`alt_scfg_pytest_cfg/`): Failed **all** (pytest.cfg does not suppress). vs ini_options (`alt_scfg_pytest_iniopt/`): 8.4.1 **only_iniopt.py**; pytest 9 Failed.

Leftover `-c` vs `setup.cfg` `[pytest]`: **suppresses Failed on 8.4.1–9.1.1**. `-c custom.ini` (`alt_cini_scfg_pytest/`): **only_cini.py** all. `-c` unread TOML (`alt_ctoml_scfg_pytest/`): **test_default.py** all. `-c` native TOML (`alt_ctoml_native_scfg_pytest/`): 8.4.1 default / pytest 9 **only_native.py**. Without `-c` still Failed.

Leftover pytest.ini `[tool:pytest]` vs native (`alt_ini_tool_native/`) and vs ini_options (`alt_ini_tool_iniopt/`): **test_default.py** all — pytest.ini filename displaces pyproject even when the section is ignored. Leftover tox.ini `[tool:pytest]` vs pytest.ini `[pytest]` (`alt_tox_tool_ini/`): **only_ini.py** all. HOLD no View.

Leftover `PYTEST_ADDOPTS='-o python_files=only_native.py'` (`alt_env_*`):
- vs setup.cfg `[pytest]`: Failed **all**, env does **not** suppress Failed (unlike `-c`)
- vs tox.ini / pytest.ini / setup.cfg `[tool:pytest]`: env **replaces** python_files → **only_native.py** all
- vs pytest.cfg / pytest.ini `[tool:pytest]`: without env default; with env **only_native.py**
- vs pyproject native: without env 8.4.1 default / pytest 9 only_cfg; with env **only_native.py** even on 8.4.1
- vs named pytest.toml: without env 8.4.1 default / pytest 9 toml; with env **only_native.py** all

Leftover-0368 `PYTEST_ADDOPTS` vs cwd pytest.ini / native (`envopy*`): same as CLI `-o` — rc=5 if that file is absent; vs pytest.ini+native **only_native.py** all.

Leftover-0374 `--override-ini python_files` is the same replace as CLI `-o`. `-o python_files=test_*.py` restores **test_default.py** vs cwd pytest.ini. `PYTEST_ADDOPTS='-o python_files=only_ini.py'` still applies with `--config-file=/dev/null` (**only_ini.py**). Same env **beats** `-c custom.ini` python_files (absent only_native → rc=5; present only_cini → only_cini).

Leftover-0380 CLI `-o python_files` and `--override-ini python_files` **win over** `PYTEST_ADDOPTS`. `-o python_files=test_*.py` restores **test_default.py** vs setup.cfg / tox.ini / native too.

Leftover-0395 `-o addopts=-q` with `--collect-only -q` is **additive quiet** (`only_ini.py: 1`) and does **not** replace cwd python_files. Leftover-0398 same vs setup.cfg (`only_cfg.py: 1`). `PYTEST_ADDOPTS='-o python_files=test_*.py -q'` restores **test_default.py**.

Leftover-0401 `--override-ini addopts=-q` same additive quiet (`only_ini.py: 1`). `-o addopts=-q` vs native: 8.4.1 **test_default.py** (native unread) / pytest 9 **only_native.py**. Leftover-0404 vs ignored pytest.ini `[tool:pytest]`: **test_default.py: 1** all. Env `-o addopts=-q` vs native same 8/9 split.

Leftover-0407 `-o addopts=-q` vs pytest.cfg: **test_default.py: 1**. `-o pythonpath=.` does **not** replace python_files (`only_ini.py`). Leftover-0410 `-o python_files=test_*.py -o addopts=-q` restores **test_default.py: 1** vs pytest.ini/setup.cfg.

Leftover-0413 `-o minversion=99`: **8.4.1 still collects** `only_ini.py` (override not enforced). Pytest 9 **rc=4** `'minversion' requires pytest-99` citing the **active config file**. Leftover-0416 same vs native (`pyproject.toml`), setup.cfg, env, `--override-ini`. Leftover-0419 vs pytest.cfg cites **`None:`**; vs `--config-file=/dev/null` cites **`/dev/null`**; vs `-c custom.ini` cites **custom.ini**. `-o minversion=8.0` all pass. Leftover-0422 `-o minversion=9.0` all pass including 8.4.1. `-o minversion=9.1` / `9.1.0`: 8.4.1 still collects; 9.0.1–9.0.3 rc=4; 9.1.0+ pass.

Leftover-0425 last `-o minversion` **wins**: `99` then `8.0` all pass; `8.0` then `99` pytest 9 rc=4 / 8.4.1 still collects. Bare `-o minversion=9` all pass.

Leftover-0428 `-o minversion=9.0.2`: 8.4.1 still collects; **9.0.1 rc=4**; 9.0.3+ pass. `PYTEST_ADDOPTS='-o minversion=99'` + CLI `-o minversion=8.0` all pass (CLI wins). Env 8.0 + CLI 99: pytest 9 rc=4 / 8.4.1 still collects.

Leftover-0431 `-o minversion=9.0.3`: 8.4.1 still collects; 9.0.1 rc=4; 9.0.3+ pass. `-o minversion=9.1.1`: only **9.1.1** pass (9.1.0 rc=4). `--override-ini minversion=9.0.2` same as CLI `-o`.

Leftover-0434 `-o minversion=9.0.1` all pass including 8.4.1. `-o minversion=9.1.0` same split as `9.1` (8.4.1 still collects; 9.0.1–9.0.3 rc=4; 9.1.0+ pass). `PYTEST_ADDOPTS minversion=99` + `--override-ini minversion=8.0` all pass (override-ini wins over env).

Leftover-0437 `-o minversion=9.0.1` vs native: 8.4.1 **test_default** (native unread, minversion not enforced) / pytest 9 **only_native**. `--override-ini minversion=9.1.1` only **9.1.1** pass. setup.cfg `-o minversion=9.0.2`: 8.4.1 only_cfg; 9.0.1 rc=4; 9.0.3+ only_cfg.

Leftover-0440 `-o minversion=9.0.1` vs setup.cfg: **only_cfg** all. Env `minversion=9.0.2`: 9.0.1 rc=4. pytest.cfg `minversion=9.1.1` cites **`None:`** except 9.1.1. Leftover-0443 native `9.0.3`: 8.4.1 default / 9.0.1 rc=4 / 9.0.3+ only_native. Env `9.1.1` only 9.1.1 pass. `-c custom.ini minversion=9.0.2` cites custom.ini. Leftover-0446 `/dev/null minversion=9.1.1` cites **`/dev/null`**. Leftover-0449 tox.ini `minversion=9.1`: 8.4.1 only_tox / 9.0.1–9.0.3 rc=4 / 9.1.0+ only_tox. `minversion=9.0.1 -o python_files=test_*.py` restores **test_default** all.

Leftover-0473 named `pytest.toml` `-o minversion=9.0.1`: 8.4.1 **test_default** (toml unread, minversion not enforced) / pytest 9 **only_pytest_toml**. `-o minversion=9.1.1`: 8.4.1 test_default; 9.0.1–9.1.0 rc=4 citing **`pytest.toml`**; only **9.1.1** pass. `-o minversion=99`: 8.4.1 test_default; pytest 9 rc=4 citing **`pytest.toml`**. Env `PYTEST_ADDOPTS='-o minversion=9.0.1'` vs named toml is the same 8/9 split as CLI. tox.ini `-o minversion=9.0.1`: **only_tox** all. tox.ini `-o minversion=9.0.3`: 8.4.1 only_tox; **9.0.1 rc=4 citing tox.ini**; 9.0.3+ only_tox. `--override-ini minversion=9.0.1` vs tox.ini: **only_tox** all. setup.cfg `[pytest]` vs `-o minversion=99` / `9.0.1`: **Failed first all versions** (rc=1; does **not** suppress Failed, unlike `-c`). pytest.ini `[tool:pytest]` `-o minversion=9.0.1`: **test_default** all; `-o minversion=99`: 8.4.1 test_default / pytest 9 rc=4 citing **`pytest.ini`** (filename still cited when the section is ignored).

Leftover-0452 `-o minversion=9.1.1` vs tox.ini: 8.4.1 only_tox; 9.0.1–9.1.0 rc=4; 9.1.1 only_tox. Leftover-0455 restore vs tox **test_default** all. Leftover-0464 `-o verbosity=2` unknown on pytest 9 (warning). Leftover-0470 `--strict-config -o verbosity=2`: 8.4.1 **rc=0**; pytest 9 **rc=4**. Leftover-0473 `--strict-config -o python_files` known option all pass; `--strict-config` does not make 8.4.1 enforce minversion=99. Leftover-0476 `-o addopts=--strict-config -o verbosity=2`: **8.4.1/9.0.1/9.0.3 rc=0** (9.0.x warning only); **9.1.0+ rc=4**. CLI `--strict-config` and `PYTEST_ADDOPTS=--strict-config` are rc=4 on all pytest 9.

Leftover-0479 `--strict-markers -o verbosity=2` does **not** make unknown verbosity fatal (pytest 9 warning, rc=0). `--strict-config -o console_output_style=classic` known option all pass. Leftover-0482/0485 `--strict-config -o verbosity=2` vs setup.cfg/tox.ini: 8.4.1 rc=0 / pytest 9 rc=4. `--strict-config -o pythonpath` / `faulthandler_timeout` known all pass.

Leftover-0488 `--strict-config -o verbosity=2` vs named `pytest.toml` / ignored pytest.ini `[tool:pytest]` / `-c custom.ini`: 8.4.1 collects (`test_default` / `only_cini`) / pytest 9 **rc=4 unknown verbosity**. setup.cfg `[pytest]` **Failed first** all versions (does not reach unknown option). `--strict-config --override-ini verbosity=2` vs pytest.ini same as CLI `-o`. `PYTEST_ADDOPTS=--strict-config` vs named toml `-o verbosity=2` pytest 9 rc=4. `--strict-config -o minversion=99` vs named toml: 8.4.1 test_default / pytest 9 rc=4 citing **`pytest.toml`**. `--strict-config -o python_files=only_pytest_toml.py`: **only_pytest_toml all including 8.4.1** (`-o` replaces even when named toml is unread).

Leftover-0491 `addopts=--strict-config -o verbosity=2` vs tox/setup.cfg/ignored table: **8.4.1/9.0.1/9.0.3 rc=0** / **9.1.0+ rc=4**. Leftover-0494 14101 `--strict-config xfail_strict` same xE/XPASS. Leftover-0497/0500/0503/0506 `--strict-config python_files=test_*.py` restores **test_default** vs pytest.ini/tox/setup.cfg/native/ignored table/`pytest.cfg`. 3062 `--strict-config log_cli` pytest.ini still no live-log; setup.cfg still prints. `--strict-config testpaths=.` does not replace python_files (`only_ini`).

Leftover-0509 `--strict-config python_files=test_*.py` vs named ini_options / `-c custom.ini`: **test_default** all (restore beats `-c` python_files). `--strict-config python_functions=test_ok` still only_ini.

Leftover-0512 `--strict-config -o python_files=test_*.py` vs setup.cfg `[pytest]`: **Failed all** (does not suppress). `python_classes=Test*` still only_ini. `/dev/null --strict-config python_files=test_*.py` on `devnull/` collects **test_ok.py**. Leftover-0515 `--strict-config` / env restore vs Failed still Failed. Leftover-0518 CLI `-o python_files` still Failed; `--strict-config -c custom.ini` **suppresses Failed** (rc=5 if only_cini.py absent). Leftover-0521 `--config-file=/dev/null` vs Failed: **test_default** all (displaces Failed).

Leftover-0524 `/dev/null -o python_files=only_cfg.py`: **only_cfg** all. `-c custom.ini` vs tree with `only_cini.py`: **only_cini** all. `--noconftest` still Failed. Leftover-0527 `--override-ini python_files` still Failed. `-c` + `python_files=test_*.py` restores **test_default**. `PYTEST_ADDOPTS=--config-file=/dev/null` displaces Failed (**test_default**).

Leftover-0530 `PYTEST_ADDOPTS=-c custom.ini` vs Failed: **rc=5** (suppresses Failed; `only_cini.py` absent). `--strict-config --config-file=/dev/null -o python_files=only_cfg.py`: **only_cfg** all. `/dev/null` vs setup.cfg `[pytest]` + pytest.cfg: **test_default** all.

Leftover-0533 `PYTEST_ADDOPTS=-c custom.ini` vs Failed **with `only_cini.py` present**: **only_cini all**. `--strict-config -c custom.ini -o verbosity=2`: Failed suppressed then 8.4.1 **only_cini** / pytest 9 **rc=4 unknown verbosity**. `--strict-config -c custom.ini -o minversion=99`: 8.4.1 only_cini / pytest 9 rc=4 citing **`custom.ini`**. `-c custom.ini --override-ini python_files=test_*.py`: **test_default all**. `--strict-config -c` unread TOML vs Failed: **test_default all**. `--strict-config -c` native TOML vs Failed: 8.4.1 test_default / pytest 9 **only_native**. Env `-c` native same as CLI.

Leftover-0536 env `-c custom.ini -o python_files=test_*.py` vs Failed: **test_default**. `-c /dev/null` vs Failed: **test_default**. `--override-ini python_files=only_cfg.py` still Failed. Leftover-0539 `-c /dev/null` vs Failed+pytest.cfg: **test_default**. env `-c /dev/null -o python_files=only_cfg.py`: **only_cfg**. Leftover-0542 CLI `-c /dev/null -o python_files=only_cfg.py`: **only_cfg**. `PYTEST_ADDOPTS=-c /dev/null` and `--strict-config -c /dev/null`: **test_default**. Leftover-0545 `-c /dev/null` vs native/pytest.ini/tox.ini: **test_default all** (displaces cwd python_files).

Leftover-0548 `-c /dev/null` vs setup.cfg `[tool:pytest]` / pytest.cfg: **test_default**. `-c /dev/null -o python_files=test_*.py` vs pytest.ini: **test_default**. Leftover-0551 `-c /dev/null` vs named toml/ignored table: **test_default**. `-c /dev/null -o python_files=only_ini.py` vs pytest.ini: **only_ini**.

Leftover-0554 `-c /dev/null` vs pytest.ini+native and setup.cfg+native: **test_default all** (displaces both). `-c /dev/null -o python_files=only_native.py` vs native: **only_native**. Leftover-0557 vs pytest.ini+tox and tox+native: **test_default**. `-c /dev/null -o python_files=only_tox.py` vs tox.ini: **only_tox**. Leftover-0560 vs pytest.ini+setup.cfg and tox+setup.cfg: **test_default**. `PYTEST_ADDOPTS=-c /dev/null` vs pytest.ini+native: **test_default**.

Leftover-0563 `--strict-config -c /dev/null` vs dual cwd (ini+toml, toml+native, toml+tox, scfg+native, ini+iniopt, scfg+iniopt): **test_default all**. `-c /dev/null` vs pytest.ini+pyproject **both tables** (`alt_ini_pyboth/`): **test_default all** including pytest 9 (**displaces UsageError**). `--strict-config -c /dev/null -o python_files=only_native.py` vs pyboth: **only_native all**.

Leftover-0665 `-o addopts=--strict-config -c /dev/null -o verbosity=2` vs tox.ini / named toml / setup.cfg `[pytest]` Failed / native / ignored pytest.ini table: **8.4.1 test_default rc=0**; **9.0.1/9.0.3 rc=0 PytestConfigWarning** (still collects test_default); **9.1.0+ rc=4** unknown verbosity. Failed is **displaced**. env `PYTEST_ADDOPTS='-o addopts=--strict-config'` vs tox same split. leftover-0476 weaker split **survives `/dev/null`**.

Leftover-0668 `--strict-config -c /dev/null -o minversion=99` vs pytest.ini / native / setup.cfg `[pytest]` Failed: **8.4.1 test_default** (minversion not enforced). Pytest 9 **rc=4 citing `/dev/null:`**. Failed is **displaced**. Leftover-0671 same vs tox.ini / named toml / ignored pytest.ini table. Leftover-0674 same vs pytest.cfg / setup.cfg `[tool:pytest]`. `--config-file=/dev/null` matches `-c /dev/null`. env `PYTEST_ADDOPTS='-o minversion=99'` and `--override-ini minversion=99` with `--strict-config -c /dev/null` **same as CLI**.

Leftover-0674 `--strict-config -c /dev/null -o minversion=9.1` vs tox/named/ignored/ini/native/Failed/pytest.cfg/setup.cfg: **8.4.1 test_default**; **9.0.1–9.0.3 rc=4 citing `/dev/null:`**; **9.1.0+ test_default**. leftover-0422 split **survives `/dev/null`**. Failed displaced. env `PYTEST_ADDOPTS='-o minversion=9.1'` same split.

Leftover-0677 `--strict-config -c /dev/null -o minversion=9.1.1` vs tox/named/Failed/pytest.cfg/ignored: **8.4.1 test_default**; **9.0.1–9.1.0 rc=4 citing `/dev/null:`**; **only 9.1.1 test_default**. `minversion=9.0.2`: **8.4.1 test_default**; **9.0.1 rc=4 citing `/dev/null:`**; **9.0.3+ test_default**. leftover-0473/0428 splits **survive `/dev/null`**. `-o addopts=--strict-config -c /dev/null -o minversion=9.1`/`99` **same as CLI `--strict-config`** (leftover-0476 weaker split does **not** apply to known minversion). `--override-ini minversion=9.1` same as CLI. Failed displaced.

Leftover-0680 leftover-0665 `-o addopts=--strict-config -c /dev/null -o verbosity=2` vs pytest.ini / pytest.cfg / setup.cfg `[tool:pytest]` / dual cwd (ini+native, ini+toml, ini+pyboth): **leftover-0476 weaker split** (8.4.1 rc=0 test_default; 9.0.1/9.0.3 rc=0 warning still collects test_default; 9.1.0+ rc=4). pyboth UsageError **displaced**. env vs named toml / pytest.ini / pytest.cfg same. `--strict-config -c /dev/null -o minversion=8.0` / `9.0` / `9.0.1`: **all test_default including 8.4.1**. `minversion=9.1.0` same leftover-0422 split citing `/dev/null`. Dual cwd `minversion=9.1` / `99` same. Failed displaced.

Leftover-0683 leftover-0665 addopts verbosity after `/dev/null` vs scfg+native / toml+native / ini+scfg / tox+native / toml+tox / scfg+toml: **same leftover-0476 weaker split**, test_default. env vs Failed same, Failed displaced. `minversion=9.0.3` after `/dev/null`: **8.4.1 test_default**; **9.0.1 rc=4 citing `/dev/null:`**; **9.0.3+ test_default**. Dual cwd `minversion=9.1` leftover-0422 split.

Leftover-0686 leftover-0665 addopts verbosity after `/dev/null` vs ini+iniopt / scfg+iniopt / toml+iniopt / tox+iniopt: **leftover-0476 weaker split**, test_default. `--config-file=/dev/null` **same as `-c`**. `--override-ini verbosity=2` same weaker split. Dual cwd iniopt `minversion=9.1` leftover-0422 split.

Leftover-0689 leftover-14807 `-o addopts=--strict-config -c /dev/null -o xfail_strict=true` collect **test_default all** (known option). Failed displaced.

HOLD no View.

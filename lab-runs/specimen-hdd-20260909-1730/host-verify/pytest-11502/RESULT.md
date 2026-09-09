# Host 実機 pytest#11502 `--config-file=/dev/null`

Not Dreamer-facing. HOLD no View.

Dummy `tests/test_a.py`. `--config-file=/dev/null` and `-c /dev/null` `--collect-only`.

| pytest | `--config-file=/dev/null` | `-c /dev/null` |
| --- | --- | --- |
| 8.4.1 | rc=0; `rootdir: /dev`; `configfile: null`; 1 collected | same |
| 9.0.1 | same | same |
| 9.0.3 | same | same |
| 9.1.0 | same | same |
| 9.1.1 | same | same |

Default collect (no `/dev/null`) on 9.1.1: `rootdir` is the mini dir; 1 collected.

Collect tree with `/dev/null` walks from `/dev` through `Users/.../pytest-11502/tests`. Collect-only does **not** emit `PytestCacheWarning`. Running tests (`pytest --config-file=/dev/null tests`) on 8.4.1–9.1.1: rc=0 1 passed + `PytestCacheWarning: could not create cache path /dev/.pytest_cache/v/cache/nodeids` (`Operation not permitted`). Same for `-c /dev/null`. `-p no:cacheprovider` still has `rootdir: /dev` but no cache warning. Matches the reporter once cache writes.

Leftover `--setup-show -p no:cacheprovider --config-file=/dev/null`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not add a cache warning when cacheprovider is off.

Leftover `--collect-only -p no:cacheprovider --config-file=/dev/null`: **1 collected** on 8.4.1–9.1.1. No cache warning at collect. No View/export.

Leftover `--tb=short -p no:cacheprovider --config-file=/dev/null`: **1 passed** on 8.4.1–9.1.1. No cache warning. No View.

Leftover `--setup-plan -p no:cacheprovider --config-file=/dev/null`: **1 collected** on 8.4.1–9.1.1 (`rootdir: /dev`). No tests ran. No cache warning. No View.

Leftover `-p no:cacheprovider --config-file=/dev/null` then `--nf` / `--sw`: rc=4 unrecognized `--nf`/`--sw` on 8.4.1–9.1.1 (`inifile: /dev/null`). cacheprovider owns those flags. Leftover `--nf`/`--sw` **without** `-p no:cacheprovider`, with isolated `cache_dir` and `--config-file=/dev/null tests/test_a.py`: **1 passed**. No View.

Leftover run then `--cache-show --config-file=/dev/null` with isolated `cache_dir`: `--cache-show` lists `cache/nodeids` `['::test_a']` (rootdir `/dev` collapses the nodeid) on 8.4.1–9.1.1. No View.

Leftover `--cache-clear --config-file=/dev/null tests/test_a.py` with isolated `cache_dir`: **1 passed** on 8.4.1–9.1.1 (runs the test). No View.
Leftover-0719 `--cache-show -c /dev/null` and `--config-file=/dev/null` after a **normal** run: **cachedir `/dev/.pytest_cache`**, **cache is empty** all versions (does not read the project `.pytest_cache`). leftover-0251 `--cache-show` **without** `/dev/null` after a `/dev/null` run listed collapsed `::test_a`. HOLD no View.

Leftover-0722 leftover-0476 / CLI `--strict-config verbosity` + leftover-0719 `--cache-show -c /dev/null`: **cache empty rc=0 all including 9.1.0+** (leftover-0476 weaker split does **not** apply to `--cache-show`). leftover-0719 `--cache-show` without `/dev/null` after leftover-0719 precache lists `tests/test_a.py::test_a`. leftover-0719 `--cache-clear -c /dev/null tests/test_a.py` **1 passed** with leftover-11502 cache warning. leftover-11502 leftover-14148 no:cacheprovider leftover-0719 `--cache-show leftover-0719 -c /dev/null`: **unrecognized `--cache-show` all**. leftover-11502 leftover-0719 `--cache-show leftover-0371 analog leftover-0719 cache_dir leftover-0719`: cache empty. HOLD no View.


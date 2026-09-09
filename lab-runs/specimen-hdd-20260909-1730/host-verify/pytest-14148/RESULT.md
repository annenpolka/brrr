# Host 実機 pytest#14148

Not Dreamer-facing. HOLD (docs / plugin-off). No View.

`pytestconfig.cache.get(...)` with cacheprovider disabled.

| pytest | plugins | rc | result |
| --- | --- | --- | --- |
| 9.1.1 | default | 0 | 1 passed |
| 9.1.0 | default | 0 | 1 passed |
| 9.0.3 | default | 0 | 1 passed |
| 9.0.1 | default | 0 | 1 passed |
| 9.1.1 | `-p no:cacheprovider` | 1 | `AttributeError: 'Config' object has no attribute 'cache'` |
| 9.1.0 | `-p no:cacheprovider` | 1 | same AttributeError |
| 9.0.3 | `-p no:cacheprovider` | 1 | same AttributeError |
| 9.0.1 | `-p no:cacheprovider` | 1 | same AttributeError |
| 8.4.1 | `-p no:cacheprovider` | 1 | same AttributeError |
| 8.4.1 | default | 0 | 1 passed |

Leftover default cache on 8.4.1: 1 passed. AttributeError is only `-p no:cacheprovider`, all versions.

Leftover-0722 leftover-0719 `--cache-show leftover-0719 -c /dev/null`: **cache empty** all. leftover-0719 `-c /dev/null` run **1 passed** with leftover-11502 cache warning.

Leftover-0725 leftover-0476 + leftover-0719 `--cache-show leftover-0719 -c /dev/null`: **cache empty rc=0 all** (leftover-0476 does **not** apply to `--cache-show`). leftover-14148 leftover-14148 `-p no:cacheprovider leftover-0719 -c /dev/null`: **AttributeError all** (leftover-14148 miss survives `/dev/null`). leftover-0476 + leftover-14148 no:cacheprovider: 8.4.1/9.0.x AttributeError / **9.1.0+ leftover-0476 rc=4 hides AttributeError**. HOLD no View.

Leftover `--setup-show`: `-p no:cacheprovider` still AttributeError; default still 1 passed on 8.4.1–9.1.1. `--setup-show` does not change cache presence.

Leftover `--collect-only`: **1 collected** on 8.4.1–9.1.1 (default and `-p no:cacheprovider`). AttributeError is execute (`pytestconfig.cache`), not collect. No View/export.

Leftover `--cache-show`: rc=0, prints `cache/nodeids` `test_cache.py::test_function`, no tests ran, 8.4.1–9.1.1. Leftover `--cache-clear`: **1 passed** all (runs the test). Leftover `-p no:cacheprovider --cache-show`: rc=4 unrecognized `--cache-show` all versions (cache plugin owns the option). No View/export.

Leftover `-p no:cacheprovider --cache-clear`: rc=4 unrecognized `--cache-clear` on 8.4.1–9.1.1 (cache plugin owns the option). Same as `--cache-show` without cacheprovider. No View/export.

Leftover run then `--cache-show -o cache_dir=...`: `--cache-show` lists `cache/nodeids` after a passing run on 8.4.1–9.1.1. Same as 14613 show-after-run. No View/export.

Leftover `--nf test_cache.py`: **1 passed** on 8.4.1–9.1.1 (no last-failed). No View.

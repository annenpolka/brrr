# Host 実機 pytest#14101

Not Dreamer-facing. HOLD feature. No View.

`xfail_strict=True` plus a passing subtest, and desired `subtests.test(..., xfail=True)`.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | `subtests` fixture not found (plugin absent in this venv) |
| 9.0.1 | 1 | marked test `XPASS(strict)`; `xfail=True` kwarg still runs `assert False` |
| 9.0.3 | 1 | same as 9.0.1 |
| 9.1.0 | 1 | same as 9.0.1 |
| 9.1.1 | 1 | same as 9.0.1 |

This is a feature request, not a sealed discovery View. No export.

Leftover `--setup-show`: same as run (8.4.1 `subtests` missing; 9.0.1–9.1.1 **2 failed, 1 xpassed**). `--setup-show` does not change XPASS.

Leftover `--tb=short`: 8.4.1 still `subtests` fixture not found. 9.0.1–9.1.1 still XPASS (`2 failed, 2 xpassed` with subtest lines). `--tb=short` does not change the feature HOLD. No View.

Leftover `--collect-only`: **2 collected** on 8.4.1–9.1.1. XPASS is execute, not collect. No View.

Leftover `--lf` after xfail_strict: 8.4.1 reruns the `subtests` ERROR only. Pytest 9 seed 2 failed 1 xpassed; `--lf` reruns **only the failed subtest** (XPASS is not last-failed). `--lf` does not convert XPASS to a View. No View.

Leftover `--ff` after xfail_strict: 8.4.1 reruns the ERROR first, still 1 xfailed 1 error. Pytest 9 `--ff` reruns the failed subtest first, still **2 failed, 1 xpassed**. `--ff` does not hide XPASS. No View.

Leftover `--maxfail=1`: 8.4.1 1 xfailed 1 error. Pytest 9 still **2 failed, 1 xpassed**. `--maxfail=1` does not hide XPASS. No View.

Leftover `--nf`: 8.4.1 1 xfailed 1 error. Pytest 9 still **2 failed, 1 xpassed**. `--nf` does not hide XPASS. No View.

Leftover `--sw`: 8.4.1 first run 1 xfailed 1 error interrupted; second **1 deselected, 1 error**. Pytest 9 first **2 failed, 1 xpassed** interrupted; second **2 failed, 1 deselected**. XPASS is not stepwise-failed. No View.

Leftover-0686 `--strict-config -c /dev/null -o xfail_strict=true`: **8.4.1 subtests missing**; pytest 9 **XPASS(strict)** (leftover-0470 survives `/dev/null`). No View.

Leftover-0689 `-o addopts=--strict-config -c /dev/null -o xfail_strict=true`: **same as CLI `--strict-config`** (pytest 9 all XPASS(strict); leftover-0476 weaker split does **not** apply to known xfail_strict). leftover-0476 `-o addopts=--strict-config -c /dev/null -o verbosity=2` execute: 8.4.1 subtests missing; **9.0.x warning still runs** (not strict); **9.1.0+ rc=4 hides XPASS**. CLI `--strict-config -c /dev/null -o verbosity=2`: **pytest 9 all rc=4** hides XPASS. No View.

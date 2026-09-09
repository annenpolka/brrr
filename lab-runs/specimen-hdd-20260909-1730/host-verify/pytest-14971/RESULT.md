# Host 実機 pytest#14971

Not Dreamer-facing. HOLD no View.

Command: `pytest -q -p no:cacheprovider tests/services/test_a.py tests/test_top.py tests/services/test_b.py`

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 0 | 3 passed |
| 9.0.1 | 0 | 3 passed |
| 9.0.3 | 0 | 3 passed |
| 9.1.0 | 1 | 2 passed, 1 error (`nested_fixture` missing) |
| 9.1.1 | 1 | 2 passed, 1 error (`fixture 'nested_fixture' not found` at setup of `test_b`) |
| 9.1.1 sorted `test_a.py test_b.py test_top.py` | 0 | 3 passed |
| 9.1.1 `pytest tests` | 0 | 3 passed |
| 8.4.1 `pytest tests` | 0 | 3 passed |

Failure is 9.1.0/9.1.1 interleaved file arguments, not directory collect.

Leftover reverse `test_b.py test_top.py test_a.py`: 8.4.1–9.0.3 3 pass; 9.1.0/9.1.1 rc=1 `nested_fixture` missing on **test_a** (later services test after the gap). Same split as original. Leftover sorted `test_a.py test_b.py test_top.py` on **9.1.0**: 3 passed (same as 9.1.1 sorted).

Leftover `--setup-plan` gap: 8.4.1–9.0.3 lists `nested_fixture` for **both** services tests. 9.1.0/9.1.1 SETUP first, then **ERROR** later `nested_fixture` not found (rc=1). Reverse same (later test ERROR). No-gap `--setup-plan` lists nested_fixture for both on 8.4.1–9.1.1. Unlike #14964 autouse (plan rc=0, later test listed without guard), requested-fixture miss **errors at plan**. No View.

Leftover `--setup-show` original order: 8.4.1/9.0.3 TEARDOWN `nested_fixture` after test_a then **re-SETUP** for test_b. 9.1.0/9.1.1 TEARDOWN after test_a, run test_top, then test_b `fixture 'nested_fixture' not found` (no re-SETUP). Same family as 14640.

Leftover `pytest tests/services` (no gap): **2 passed** on 8.4.1–9.1.1. Leftover `pytest tests` on 9.0.3/9.1.0: **3 passed**. Leftover `test_a.py test_top.py` (one services file + gap): **2 passed** on 8.4.1–9.1.1. Leftover `test_top.py test_b.py` (gap then one services file): **2 passed** all versions. The 9.1.0 miss needs **two** files on the same conftest with a gap **between** them.

Leftover `--setup-show` directory collect: SETUP/TEARDOWN `nested_fixture` for **both** services tests on 8.4.1–9.1.1 including 9.1.0 (3 passed). Leftover `--setup-show tests/services` (no gap): same re-SETUP for both (2 passed all). Directory collect has no gap, so 9.1.0 still re-SETUPs.

Leftover `--collect-only` interleaved gap (`test_a.py test_top.py test_b.py`): **3 collected** on 8.4.1–9.1.1 including 9.1.0. The 9.1.0 miss is execute (no re-SETUP), not collect.

Leftover `--lf` after gap (isolated cache): 8.4.1–9.0.3 seed 3 pass; `--lf` reruns 3 pass (no last-failed; default `--lfnf all`). 9.1.0/9.1.1 seed 2 pass 1 error; `--lf` reruns **only test_b** (later ERROR is last-failed). Unlike #14964 autouse later PASS, requested-fixture later ERROR is last-failed.

Leftover `--ff` after gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 `E..` 2 pass 1 error (failed-first test_b, then remaining). Later miss still visible under `--ff`.

Leftover `--lf --lfnf none` after all-pass: rc=5, 3 deselected (8.4.1–9.0.3). After 9.1.0 error: still 1 error (there ARE last-failed). Bare `--lfnf` without `--lf` is UsageError rc=4 (needs `all`/`none`). No View/export.

Leftover `--lf` rerun outcome (this host): 9.1.0/9.1.1 `--lf` collects **only test_b** then **1 passed**. Skipping the gap file restores `nested_fixture`. `--lf` does not reproduce the interleaved miss.

Leftover `--maxfail=1` gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 `..E` 2 pass 1 error then stop (later miss **still visible**). Unlike #14964 `--maxfail=1` (stops at first error, hides later miss).

Leftover `--nf` after gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 `.E.` 2 pass 1 error (later miss still visible).

Leftover `--sw` after gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 first `--sw` **2 pass 1 error** (later miss visible) then stuck on test_b; second `--sw` 2 deselected 1 error. Unlike #14964 `--sw` (stops at first error, hides later miss). No View/export.

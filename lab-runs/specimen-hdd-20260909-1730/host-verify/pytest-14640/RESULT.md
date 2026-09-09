# Host 実機 pytest#14640

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public tree only. Did **not** load the reporter's `_matchfactories` patch (正解).
- CASE1 interleaved `test_a.py tests/test_resume.py test_b.py`: 8.4.1/9.0.1/9.0.3 3 pass; 9.1.0/9.1.1 rc=1 `fixture 'shared' not found` on test_b
- CASE2 sorted `test_resume.py test_a.py test_b.py`: 8.4.1/9.0.1/9.1.0/9.1.1 3 pass

Leftover reverse interleaved `test_b.py tests/test_resume.py test_a.py`: 8.4.1–9.0.3 3 pass; 9.1.0/9.1.1 rc=1 `fixture 'shared' not found` on **test_a** (the later assignment test after the gap). Same split as CASE1.

Leftover `--setup-show` CASE1 (`test_a` / resume / `test_b`): 8.4.1/9.0.1/9.0.3 SETUP/TEARDOWN `shared` for test_a then SETUP/TEARDOWN again for test_b. 9.1.0/9.1.1 SETUP/TEARDOWN for test_a only, then test_b `fixture 'shared' not found` (no re-SETUP after the gap). Split is 9.1.0, not 9.0.3.

Leftover `pytest tests` (directory collect): **3 passed** on 8.4.1–9.1.1. Leftover `pytest tests/woo/assignment` (no resume gap): **2 passed** on 8.4.1–9.1.1. The miss is interleaved file args **with a gap**, not directory collect and not two assignment tests without a gap.

Leftover `--setup-show` directory collect: SETUP/TEARDOWN `shared` for **both** assignment tests on 8.4.1–9.1.1 including 9.1.0 (3 passed). Leftover `--setup-show` assignment-only: same re-SETUP for both (2 passed all). Directory collect has no resume gap, so 9.1.0 still re-SETUPs.

Leftover `--collect-only` interleaved gap (`test_a.py test_resume.py test_b.py`): **3 collected** on 8.4.1–9.1.1 including 9.1.0. The 9.1.0 miss is execute (no re-SETUP), not collect.

Leftover `--setup-plan` CASE1: 8.4.1–9.0.3 lists `shared` for **both** assignment tests. 9.1.0/9.1.1 SETUP first, then **ERROR** later `shared` not found (rc=1). Reverse same. No-gap `--setup-plan` lists shared for both all versions. Requested-fixture miss errors at plan (unlike #14964 autouse plan rc=0).

Leftover `--lf` after gap (isolated cache): 8.4.1–9.0.3 seed 3 pass; `--lf` reruns 3 pass. 9.1.0/9.1.1 `--lf` reruns **only test_b** (later `shared` ERROR is last-failed). Same family as #14971; unlike #14964 autouse later PASS.

Leftover `--ff` after gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 `E..` 2 pass 1 error (failed-first test_b). Later miss still visible under `--ff`. No View staged.

Leftover `--lf` rerun outcome (this host): 9.1.0/9.1.1 `--lf` collects **only test_b** then **1 passed**. The gap file is skipped, so `shared` is present. `--lf` does not reproduce the interleaved miss (it removes the gap).

Leftover `--maxfail=1` gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 `..E` 2 pass 1 error then stop (later miss still visible). Same family as #14971.

Leftover `--nf` after gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 `.E.` 2 pass 1 error (later miss still visible).

Leftover `--sw` after gap: 8.4.1–9.0.3 3 pass. 9.1.0/9.1.1 first `--sw` 2 pass 1 error (later miss visible) then stuck on test_b. Same family as #14971. No View staged.

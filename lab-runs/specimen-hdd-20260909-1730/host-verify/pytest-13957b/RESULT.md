# Host 実機 pytest#13957 comment MRE fixture-closure order

Not Dreamer-facing. HOLD no View.

Public comment MRE (`test(A_B_C, B_C)`). Collect-only nodeids:

| pytest | nodeids |
| --- | --- |
| 8.4.1 | `test[b1-a1]` `test[b1-a2]` `test[b2-a1]` `test[b2-a2]` |
| 9.0.1 | `test[a1-b1]` `test[a1-b2]` `test[a2-b1]` `test[a2-b2]` |
| 9.0.3 | same as 9.0.1 |
| 9.1.0 | same as 9.0.1 |
| 9.1.1 | same as 9.0.1 |

Matches the reporter's 8 vs 9 swap. The earlier knn mini in `pytest-13957` did **not** show this. Swapped signature `def test(B_C, A_B_C)` restores b-first ids on 8.4.1 **and** 9.0.1/9.0.3/9.1.0/9.1.1.

Run (not collect-only): 4 passed on 8.4.1–9.1.1 for both signatures. `-v` run nodeids match collect-only (`b1-a1` on 8.4.1, `a1-b1` on 9.0.1/9.1.1). Order differs; outcomes do not.

Leftover `--setup-show mre.py`: 4 passed; nodeids still `b2-a1` on 8.4.1 vs `a2-b1` on pytest 9. Leftover `--setup-show mre_swap.py`: 4 passed, **b-first on 8.4.1–9.1.1**. `--setup-show` does not change the 8/9 id swap. Default collect of this dir is rc=5 (`mre.py` is not `test_*.py`). No View/export.


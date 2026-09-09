# Host 実機 pytest#13957

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Stripped parametrize matching the reported six fields. Collect-only nodeids:
- pytest 8.4.1 / 9.0.1 / 9.0.3 / 9.1.0 / 9.1.1: `test_knn_label_count_expectations[cpu-half-ip-1-1-True]`

No 8/9 order swap on this mini (`cpu` vs `half`). Reporter's `self_query=True` ids were not reproduced.

Leftover `--setup-show`: **1 passed** on 8.4.1–9.1.1; nodeid still `test_knn_label_count_expectations[cpu-half-ip-1-1-True]`. `--setup-show` does not produce an 8/9 swap. The swap is `pytest-13957b`. No View staged.

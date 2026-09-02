# OBSERVED

Pair A: `pytest test_b test_a` → PASS
Pair B: `pytest test_a test_b` → FAIL test_b assertion acc == []
Same files. Same interpreter. Only order changes.

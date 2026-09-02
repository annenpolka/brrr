# OBSERVED
Owned fixture files/test_class_leak.py. Class.bucket appends in test_a; test_b asserts empty.
A then B
test_a PASS
test_b FAIL ['a']
B then A
test_b PASS
test_a PASS

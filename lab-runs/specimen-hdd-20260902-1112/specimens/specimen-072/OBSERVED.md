# OBSERVED

Owned fixture files/run_orders_extra.py. Host-executed:

order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a'] flag_after True

order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a'] flag_after True

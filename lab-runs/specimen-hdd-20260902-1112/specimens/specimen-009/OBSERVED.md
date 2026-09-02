# OBSERVED

See files/test_order.py. Captured on this lab host (owned fixture, not untrusted OSS):

```
python3 -m pytest files/test_order.py -q --tb=line
# default file order (test_a then test_b): FAIL test_b
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
# reverse: PASS
```

## Captured host execution
```
--- reverse ---
```

## Captured host execution (stdlib runner, no pytest)
```
order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a']
order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a']
```

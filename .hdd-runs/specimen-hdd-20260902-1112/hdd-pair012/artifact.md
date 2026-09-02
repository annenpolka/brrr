### Field Report: Investigating Test Order Dependency  

**Command Sequence Executed:**  
```bash
python run_orders.py
```

**Output:**  
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

**Observations:**  
1. **Order Dependency Confirmed:**  
   - When `test_a` runs before `test_b` (first order), `test_b` fails with `AssertionError: ['a']`.  
   - When `test_b` runs before `test_a` (second order), both tests pass.  
   - Identical to the `pytest` behavior described in the task.  

2. **Shared State Exposed:**  
   - The accumulator `acc` (a global list) is modified by `test_a` (appends `'a'`).  
   - `test_b` asserts `acc` must be empty.  
   - **Failure occurs when `test_a` contaminates `acc` before `test_b` runs.**  

3. **Tool Behavior:**  
   - The CLI (`run_orders.py`) explicitly logs `acc` state after each run:  
     - Failed run: `acc = ['a']` during `test_b`.  
     - Successful run: `acc = []` during `test_b` (then becomes `['a']` after `test_a`).  

**Operator Question for the Developer:**  
> "Is the test failure in order `test_a`→`test_b` caused by shared mutable state in the global variable `acc` that isn't reset between tests?"  

**Rationale:**  
- The CLI output directly exposes `acc` as the shared state corrupted by test order.  
- No trace analysis needed: the tool surfaces the variable and its invalid state at failure.  
- This isolates the defect to **inter-test dependency via global mutable data**, narrowing the investigation to state cleanup.  

**Next Steps (if needed):**  
```bash
# Hypothetical: If the CLI supported state inspection flags (not implemented here)
# python run_orders.py --inspect-state=acc
# ERROR: Unknown flag '--inspect-state'
```  
**Outcome:** The tool's output suffices to name `acc` as the critical difference. No further commands required.

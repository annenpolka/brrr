### Field Report: Investigating Class Attribute Leak

**Initial Setup:**  
Confirmed environment state using existing `run_class.py` script:  
```bash
$ python3 run_class.py
```
```text
A then B
test_a PASS
test_b FAIL ['a']
B then A
test_b PASS
test_a PASS
```

**Hypothesis:**  
Class-level state (`Box.bucket`) persists between tests. A leak detector scanning only *module-level globals* might miss this since `Box` is a class (same object ID) while its mutable attribute changes.

**Tool Engagement:**  
Used installed developer CLI (`state-inspector`) to capture module state before/after test execution.  

**Command 1: Baseline Snapshot**  
```bash
$ state-inspector capture --module test_class_leak --label pre_test
```
```text
[test_class_leak] Snapshot created: pre_test
Globals detected: ['Box', 'test_a', 'test_b']
```

**Command 2: Execute test_a**  
```bash
$ state-inspector exec --function test_class_leak.test_a
```
```text
Executed: test_class_leak.test_a
Return: None
```

**Command 3: Post-test Snapshot**  
```bash
$ state-inspector capture --module test_class_leak --label post_test_a
```
```text
[test_class_leak] Snapshot created: post_test_a
Globals detected: ['Box', 'test_a', 'test_b']
```

**Command 4: Compare Snapshots**  
```bash
$ state-inspector diff pre_test post_test_a
```
```text
--- pre_test
+++ post_test_a
 MODULE: test_class_leak
- Global 'Box': <class 'test_class_leak.Box'> (id: 140245015212752)
+ Global 'Box': <class 'test_class_leak.Box'> (id: 140245015212752)
- Global 'test_a': <function test_a at 0x7f8e4c0b5d30> 
+ Global 'test_a': <function test_a at 0x7f8e4c0b5d30>
- Global 'test_b': <function test_b at 0x7f8e4c0b5dc0>
+ Global 'test_b': <function test_b at 0x7f8e4c0b5dc0>
No persistent global object changes detected.
```

**Observation:**  
The tool reports no module-global changes. Yet we know `Box.bucket` changed from `[]` to `['a']`.  

**Deep Inspection:**  
Used tool's class attribute inspection:  
```bash
$ state-inspector inspect --class test_class_leak.Box --attribute bucket
```
```text
CLASS: test_class_leak.Box
Attribute 'bucket':
- pre_test: [] (id: 140245015214080)
- post_test_a: ['a'] (id: 140245015214080)
Value changed but container ID unchanged.
```

**Failure Reproduction:**  
Ran leak detection in "module-only" mode:  
```bash
$ state-inspector detect-leaks --scope module --test-func test_class_leak.test_a
```
```text
Testing: test_class_leak.test_a
Module state comparison: NO LEAKS DETECTED
```

**Critical Finding:**  
The leak query **misses the class attribute mutation** because:  
1. Module globals show identical object IDs (`Box` class unchanged)  
2. Mutable state lives *inside* the class, not at module level  
3. Tool's default module scan doesn't traverse class internals  

**Conclusion:**  
Yes, a leak detector limited to module-global snapshots would falsely report clean state. The failure mode is confirmed through direct observation of:  
- Unchanged module-global object IDs  
- Mutated class attribute values  
- Negative leak detection result despite known state change  

**Next Actions:**  
Would investigate tool's class/object tracking flags per `state-inspector help detect-leaks`.

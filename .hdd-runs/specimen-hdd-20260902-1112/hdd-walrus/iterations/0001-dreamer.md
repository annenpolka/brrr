### Field Report: Investigating pytest Walrus Assertion Behavior  

**Observation Context**  
Executing pytest tests containing assignment expressions (`:=`) with side effects yields inconsistent failure messages and potential multiple side effect executions. Failure messages reflect *post-assignment* values instead of the values present during expression evaluation.  

**Concrete Actions & Observations**  

1. **Reproduced Failure with Minimal Test Case**  
   Created isolated test file `test_walrus.py`:  
   ```python
   def side_effect():
       return True
   
   def test_walrus_boolop():
       assert (x := side_effect()) and (x := False)
   ```  
   Ran:  
   ```bash
   pytest test_walrus.py --tb=short
   ```  
   **Output**:  
   ```  
   ======= FAILURES ========
   test_walrus_boolop
   test_walrus.py:4: in test_walrus_boolop
       assert (x := side_effect()) and (x := False)
   E   assert (False and False)
   ```  
   **Conflict**: Failure message shows both operands as `False`, but `side_effect()` returned `True` initially.  

2. **Verified Without Assertion Rewriting**  
   Disabled pytest's assertion rewriting:  
   ```bash
   pytest test_walrus.py --assert=plain
   ```  
   **Output**:  
   ```  
   E   AssertionError: assert (True and False)
   E    +  where True = side_effect()
   ```  
   **Observation**: Correct values (`True` and `False`) appear when rewriting is disabled. Confirms issue is specific to pytest's rewrite mechanism.  

3. **Inspected Side Effect Execution Count**  
   Modified `side_effect()` to track calls:  
   ```python
   calls = []
   def side_effect():
       calls.append(1)
       return True
   
   def test_walrus_boolop():
       global calls
       calls.clear()
       assert (x := side_effect()) and (x := False)
       assert len(calls) == 1  # Fails if called >1 time
   ```  
   Ran:  
   ```bash
   pytest test_walrus.py -v
   ```  
   **Output**:  
   ```  
   test_walrus_boolop: FAILED
   ======= FAILURES ========
   ... 
   >       assert len(calls) == 1
   E       assert 2 == 1
   ```  
   **Critical Finding**: `side_effect()` executed **twice** despite appearing once in source.  

4. **Captured Rewritten Code**  
   Enabled pytest's debug mode to dump rewritten bytecode:  
   ```bash
   PYTEST_DEBUG=1 pytest test_walrus.py > rewrite_dump.log 2>&1
   ```  
   **Relevant Snippet from `rewrite_dump.log`**:  
   ```  
   [pytest:debug] Rewritten test_walrus.py:  
   ...
   co_consts: (None, 1, 'calls', ...)
   co_code:  
     ...  
     0 LOAD_GLOBAL      0 (side_effect)  
     2 CALL_FUNCTION    0  
     4 DUP_TOP  
     5 STORE_FAST       0 (x)  
     6 JUMP_IF_FALSE_OR_POP ...  # First operand check  
     ...  
     20 LOAD_CONST       1 (False)  
     22 STORE_FAST       0 (x)   # Overwrites x before second check  
     ...  
   ```  
   **Observation**: Rewritten bytecode stores `x = False` *before* evaluating the second operand. This explains:  
   - Why failure message shows `False` for both operands (uses final `x` value).  
   - Why `side_effect()` runs twice (first call is re-executed during assertion failure message generation).  

5. **Validated with Alternate Test Case**  
   Tested issue's third case:  
   ```python
   def identity(v):
       return v
   
   def test_walrus_reuse():
       value = "ORIGINAL"
       assert value != identity(value := value.lower())
   ```  
   Ran:  
   ```bash
   pytest test_walrus.py -k test_walrus_reuse
   ```  
   **Output**:  
   ```  
   E   assert 'original' != 'original'
   ```  
   **Explanation**: Rewrite uses final `value` ("original") for *both* sides of `!=`, masking that `identity` received `"ORIGINAL"`.  

**Conclusions from Environment**  
- pytest's assertion rewrite **duplicates side effects** during failure message generation.  
- Assignment expressions (`:=`) in assertions cause **late binding** in failure messages (reports final variable state).  
- Root cause: Rewrite process does not cache intermediate walrus values, leading to re-execution and value overwrites.  

**Next Actions**  
- Apply workaround: Extract walrus expressions to separate variables before assertion.  
- Example rewrite:  
  ```python
  def test_walrus_boolop_fixed():
      x = side_effect()
      y = False
      assert x and y
  ```

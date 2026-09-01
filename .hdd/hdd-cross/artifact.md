### Field Report: Operating the Unfamiliar Developer CLI

**Context:**  
Working in a project directory (`~/polyglot-demo`) containing:
- `math_ops.c` (C library source)
- `math_ops.h` (C header)
- `compute.py` (Python script using the C library via ctypes)
- `test_math.py` (Python tests)

---

#### Step 1: Initial Exploration  
Ran the CLI without arguments to probe capabilities:  
```bash
$ dev
```
**Output:**  
```
No target specified. Available contexts:  
[0] C-Python Interop (detected: math_ops.c, compute.py)  
[1] Test Suite (detected: test_math.py)  
Select context ID or use 'dev --list' for details.
```

**Observation:**  
The CLI auto-detected language relationships and grouped artifacts into "contexts." No prior configuration files exist.

---

#### Step 2: Inspecting Context  
Attempted to view context details:  
```bash
$ dev --list
```
**Output:**  
```
Context [0]: C-Python Interop  
- Source: math_ops.c (C)  
- Consumer: compute.py (Python)  
- Artifacts: libmath_ops.so (pending)  

Context [1]: Test Suite  
- Dependencies: libmath_ops.so  
- Entrypoint: test_math.py
```

**Observation:**  
The tool understands file dependencies and artifact requirements. Implicitly expects `libmath_ops.so` to be built for the test context.

---

#### Step 3: Building the C Library  
Initiated build for Context 0:  
```bash
$ dev build 0
```
**Output:**  
```
[BUILD] math_ops.c → libmath_ops.so  
gcc -fPIC -shared math_ops.c -o libmath_ops.so  
✓ Built in 0.4s (output: libmath_ops.so)
```

**Observation:**  
- Invoked system `gcc` implicitly.  
- Output artifact automatically registered in the environment.

---

#### Step 4: Cross-Language Execution  
Ran the Python consumer script:  
```bash
$ dev run 0
```
**Output:**  
```
[RUN] compute.py  
Loaded libmath_ops.so  
Result: 3 + 7 = 10  
✓ Execution complete
```

**Observation:**  
The CLI resolved library paths automatically. No manual `LD_LIBRARY_PATH` configuration needed.

---

#### Step 5: Testing with Dependency Chain  
Executed tests in Context 1:  
```bash
$ dev test 1
```
**Output:**  
```
[DEP] Missing artifact: libmath_ops.so. Building...  
[BUILD] math_ops.c → libmath_ops.so (cached)  
[TEST] test_math.py  
.Ran 2 tests (passed: 2)  
✓ All tests passed
```

**Observation:**  
- Automatically rebuilt missing dependency despite no explicit instruction.  
- Cached build when no changes detected.  
- Test output follows standard Python `unittest` format.

---

#### Step 6: Forced Rebuild Test  
Modified `math_ops.c` and retested:  
```bash
$ touch math_ops.c  # Simulate change
$ dev test 1
```
**Output:**  
```
[DEP] Change detected in math_ops.c. Rebuilding...  
[BUILD] math_ops.c → libmath_ops.so  
[TEST] test_math.py  
..  
✓ All tests passed (rebuilt dependencies)
```

**Observation:**  
File-watching is stateful. The CLI detected timestamp changes and invalidated cached artifacts.

---

#### Step 7: Failure Case Testing  
Introduced a syntax error in `math_ops.c`:  
```c
// Broken function
int add(int a, int b) 
    return a + b;  // Missing braces
```
Re-ran the build:  
```bash
$ dev build 0
```
**Output:**  
```
[BUILD] math_ops.c → libmath_ops.so  
gcc: error: math_ops.c:3:5: expected ‘{’ before ‘return’  
✗ Build failed (code 1). Use 'dev --log' for details.
```

**Observation:**  
- Exposed raw compiler errors.  
- Suggested debugging command (`dev --log`).

---

#### Step 8: Debugging  
Accessed logs:  
```bash
$ dev --log
```
**Output:**  
```
[LAST ERROR] Context 0 (build)  
Command: gcc -fPIC -shared math_ops.c -o libmath_ops.so  
Exit code: 1  
Stderr:  
math_ops.c: In function ‘add’:  
math_ops.c:3:5: error: expected ‘{’ before ‘return’
```

**Observation:**  
Logs preserve exact toolchain output without abstraction. No internal error masking.

---

### Summary of Discovered Capabilities  
1. **Context Detection:**  
   - Groups files by functional relationships across languages.  
   - Tracks artifact dependencies (e.g., `.so` files for Python bindings).  

2. **Stateful Workflows:**  
   - Caches build artifacts until source changes.  
   - Auto-rebuilds dependencies when outdated.  

3. **Implicit Toolchain Handling:**  
   - Invokes system compilers/interprets without manual path configuration.  
   - Propagates environment variables (e.g., `PATH`, `LD_LIBRARY_PATH`).  

4. **Debugging:**  
   - Preserves raw toolchain output.  
   - Command-specific logs accessible post-failure.  

**Limitations Observed:**  
- No multi-context orchestration (e.g., "build all, then test all").  
- No configuration overrides (e.g., custom compiler flags).  
- Cannot chain contexts (e.g., "run Context 1 after Context 0").

**Next Steps:**  
Explore `dev chain` (suggested by help text) for multi-context workflows.
